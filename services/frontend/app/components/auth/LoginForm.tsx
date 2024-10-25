"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Input from "@/app/components/common/Input";
import { UserFormProps, ResponseError } from "@/app/types";
import { validateEmail } from "@/app/utils/validator";
import { setUserTokens, TokenType } from "@/app/utils/auth";
import LoadingThreeDots from "./LoadingThreeDots";
import { useLoading } from "@/app/context/LoadingFullScreenContext";
import api from "@/api";

import PasswordInput from "../common/PasswordInput";
import TermsConditionPopup from "./TermsConditionPopup";
import LoadingFullScreen from "../animation/LoadingFullScreen";

import {
  HTTP_401_UNAUTHORIZED,
  HTTP_RESPONSE_CODE,
} from "@/app/constants/httpResponse";

import GoogleIcon from "@/public/icons/google.svg";
import ArrowRightIcon from "@/public/icons/arrow-right.svg";

const LoginForm = () => {
  const router = useRouter();
  const searchParams = useSearchParams();

  const authError = searchParams.get("authError");
  const { loadingFullScreen, handleSetLoadingFullScreen } = useLoading();

  const [userForm, setUserForm] = useState<UserFormProps>({
    email: "",
    password: "",
  });
  const [emailError, setEmailError] = useState<boolean>(false);
  const [loadingState, setLoadingState] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [serviceErrorMessage, setServiceErrorMessage] = useState<string>("");
  const [currentTokens, setCurrentTokens] = useState<TokenType | null>(null);
  // Terms of use and privacy notice
  const [isAcceptedTermsCondition, setIsAcceptedTermsCondition] =
    useState<boolean>(false);
  const [showTermsConditionPopup, setShowTermsConditionPopup] =
    useState<boolean>(false);

  const { email, password }: UserFormProps = userForm;

  const resetState = () => {
    setLoadingState(false);
    setErrorMessage("");
    setServiceErrorMessage("");
  };

  useEffect(() => {
    resetState();
  }, []);

  useEffect(() => {
    if (authError) {
      setLoadingState(false);
      setServiceErrorMessage(
        "เกิดข้อผิดพลาดเกี่ยวกับข้อมูลผู้ใช้งาน โปรดลองอีกครั้งในภายหลัง"
      );
      window.history.replaceState(null, "", "/auth/login");
    }
  }, [authError]);

  const handleUserFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserForm({
      ...userForm,
      [event.target.name]: event.target.value,
    });
    if (emailError) {
      setEmailError(false);
    }
    if (errorMessage) {
      setErrorMessage("");
    }
    if (serviceErrorMessage) {
      setServiceErrorMessage("");
    }
  };

  const redirectToChatbot = () => {
    router.push("/chatbot");
    router.refresh();
  };

  // login
  const handleSubmitLoginForm = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    resetState();
    const customEmail = email?.trim();
    const isValidEmail = validateEmail(customEmail);
    if (!isValidEmail) {
      setEmailError(true);
      return;
    }
    try {
      setLoadingState(true);
      const response = await api.auth.login({ email: customEmail, password });

      const tokens = await response.json();
      setCurrentTokens(tokens);
      try {
        const hasAcceptedTermsStateRes = await api.auth.isUserAcceptedTerms(
          email
        );
        const hasAcceptedTermsState = await hasAcceptedTermsStateRes.json();

        if (hasAcceptedTermsState.has_accepted_terms) {
          await setUserTokens(tokens);
          redirectToChatbot();
        } else {
          setShowTermsConditionPopup(true);
          setLoadingState(false);
        }
        return;
      } catch (_) {
        await setUserTokens(tokens);
        redirectToChatbot();
      }

      // setLoadingState(false);
    } catch (error) {
      if (error instanceof ResponseError) {
        if (error.response.status === HTTP_401_UNAUTHORIZED) {
          if (
            error.response.code ===
              HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].EMAIL_NOT_EXISTS ||
            error.response.code ===
              HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED]
                .INVALID_USERNAME_OR_PASSWORD ||
            error.response.code ===
              HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].KEYCLOAK_USER_NOT_FOUND
          ) {
            setErrorMessage("อีเมลหรือรหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง");
            setLoadingState(false);
            return;
          } else if (
            error.response.code ===
            HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].DISABLED_ACCOUNT
          ) {
            setErrorMessage("บัญชีของคุณถูกระงับ โปรดติดต่อฝ่ายสนับสนุน");
            setLoadingState(false);
            return;
          }
        }
      }
      setServiceErrorMessage(`ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง`);
      setLoadingState(false);
    }
  };

  const handleCloseTermsConditionPopup = async () => {
    setShowTermsConditionPopup(false);
    setLoadingState(false);
  };

  const handleAgreeTermsCondition = async () => {
    handleSetLoadingFullScreen(true);
    try {
      await api.auth.acceptTerms(email);
    } catch (_) {}
    if (currentTokens) await setUserTokens(currentTokens);
    redirectToChatbot();
    handleCloseTermsConditionPopup();
  };

  useEffect(() => {
    return () => {
      setLoadingState(false);
      handleSetLoadingFullScreen(false);
    };
  }, []);

  return (
    <>
      {loadingFullScreen && <LoadingFullScreen />}
      {showTermsConditionPopup && (
        <TermsConditionPopup
          handleAgreeTermsCondition={handleAgreeTermsCondition}
          onClose={handleCloseTermsConditionPopup}
          isMaskClosable={false}
        />
      )}
      <section className="p-6 flex flex-col gap-4 shadow-xl rounded-xl border border-gray-200 bg-white">
        {/* log in with google */}
        {/* <button
          type="button"
          aria-label="Continue with Google"
          className="btn-secondary rounded-lg py-2.5 px-4 font-semibold text-base flex items-center justify-center gap-3"
        >
          <GoogleIcon className="w-6 h-6 no-inherit" />
          <span>Continue with Google</span>
        </button> */}
        {/* divider */}
        {/* <div className="flex items-center gap-3">
          <hr className="grow border-gray-300" />
          <span className="text-gray-400">หรือ</span>
          <hr className="grow border-gray-300" />
        </div> */}
        {/* log in with e-mail */}
        <form
          onSubmit={handleSubmitLoginForm}
          className="flex flex-col gap-4"
          noValidate
        >
          <Input
            id="email"
            name="email"
            onChange={handleUserFormChange}
            value={email}
            error={emailError ? "รูปแบบอีเมลไม่ถูกต้อง โปรดลองอีกครั้ง" : ""}
            type="email"
            label="อีเมล"
            placeholder="กรอกอีเมล"
            autoComplete="email"
            autoFocus
          />
          <PasswordInput
            id="password"
            name="password"
            onChange={handleUserFormChange}
            value={password}
            label="รหัสผ่าน"
            placeholder="กรอกรหัสผ่าน"
            autoComplete="password"
            error={errorMessage}
          />

          <Link
            href={`/auth/forgot-password`}
            className="text-sm text-primary-700 hover:text-primary-800 font-semibold ml-auto"
          >
            ลืมรหัสผ่าน
          </Link>
          <button
            type="submit"
            aria-label="เข้าสู่ระบบ"
            className="btn-primary-md h-[42px]"
            disabled={!email || !password || loadingState}
          >
            {loadingState ? <LoadingThreeDots /> : "เข้าสู่ระบบ"}
          </button>
          {serviceErrorMessage && (
            <div className="text-error-600 whitespace-pre-line text-sm text-center">
              {serviceErrorMessage}
              <div className="text-center text-gray-500 text-xs">
                หากยังคงพบปัญหา สามารถติดต่อเราเพื่อขอความช่วยเหลือ
                <br />
                ที่อีเมล{" "}
                <a
                  href="mailto:contact@vistec.ac.th"
                  className="font-bold text-gray-500"
                >
                  contact@vistec.ac.th
                </a>
                <br />
              </div>
            </div>
          )}
          <div className="text-sm text-center flex items-center justify-center gap-2">
            <span className="text-gray-600 text-sm">ยังไม่มีบัญชีใช้งาน?</span>{" "}
            <Link
              href={`/auth/register`}
              className="text-primary-700 hover:text-primary-800 font-semibold flex items-center gap-1.5 group"
            >
              <span>สร้างบัญชีใช้งาน</span>
              <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-all duration-500" />
            </Link>
          </div>
        </form>
      </section>
    </>
  );
};

export default LoginForm;
