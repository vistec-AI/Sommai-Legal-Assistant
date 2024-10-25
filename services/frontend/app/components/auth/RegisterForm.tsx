"use client";

import { useState } from "react";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { UserFormProps, ResponseError } from "@/app/types";
import { validateEmail } from "@/app/utils/validator";

import {
  HTTP_401_UNAUTHORIZED,
  HTTP_RESPONSE_CODE,
} from "@/app/constants/httpResponse";
import api from "@/api";

import Input from "../common/Input";
import PasswordInput from "../common/PasswordInput";
import LoadingThreeDots from "./LoadingThreeDots";

import GoogleIcon from "@/public/icons/google.svg";
import ArrowRightIcon from "@/public/icons/arrow-right.svg";

import AcceptTermsCondition from "../AcceptTermsCondition";

const RegisterForm = () => {
  const router = useRouter();

  const [userForm, setUserForm] = useState<UserFormProps>({
    email: "",
    password: "",
  });
  const [emailError, setEmailError] = useState<boolean>(false);
  const [loadingState, setLoadingState] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [serviceErrorMessage, setServiceErrorMessage] = useState<string>("");
  const [validPassword, setValidPassword] = useState<boolean>(false);
  // Terms of use and privacy notice
  const [isAcceptedTermsCondition, setIsAcceptedTermsCondition] =
    useState<boolean>(false);

  const { email, password } = userForm;

  const handleUserFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserForm({
      ...userForm,
      [event.target.name]: event.target.value,
    });
    if (emailError) {
      setEmailError(false);
    }
  };

  // register
  const handleSubmitLoginForm = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setEmailError(false);
    setErrorMessage("");
    setServiceErrorMessage("");
    const customEmail = email?.trim();
    const isValidEmail = validateEmail(customEmail);

    if (!isValidEmail) {
      setEmailError(true);
      return;
    }
    try {
      setLoadingState(true);
      await api.auth.register({ email: customEmail, password });

      router.push("/auth/registered");
      setLoadingState(false);
    } catch (error) {
      if (error instanceof ResponseError) {
        if (error.response.status === HTTP_401_UNAUTHORIZED) {
          if (
            error.response.code ===
            HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].EMAIL_ALREADY_EXISTS
          ) {
            setErrorMessage("อีเมลถูกใช้งานแล้ว");
          }
        } else {
          setServiceErrorMessage(`ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง`);
        }
      } else {
        setServiceErrorMessage(`ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง`);
      }
      setLoadingState(false);
    }
  };

  return (
    <>
      <form
        onSubmit={handleSubmitLoginForm}
        className="p-6 flex flex-col gap-4 shadow-xl rounded-xl border border-gray-200 bg-white"
        noValidate
      >
        {/* register with e-mail */}
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
          showValidation={true}
          handleSetValidPassword={(isValid) => {
            setValidPassword(isValid);
          }}
          error={errorMessage}
        />
        <AcceptTermsCondition
          isAcceptedTermsCondition={isAcceptedTermsCondition}
          handleIsAcceptedTermsCondition={(state: boolean) =>
            setIsAcceptedTermsCondition(state)
          }
        />
        <button
          type="submit"
          aria-label="สมัครสมาชิก"
          className="btn-primary-md h-[42px]"
          disabled={
            !email ||
            !password ||
            !validPassword ||
            loadingState ||
            !isAcceptedTermsCondition
          }
        >
          {loadingState ? <LoadingThreeDots /> : "สมัครสมาชิก"}
        </button>
        {serviceErrorMessage && (
          <p className="text-error-600 whitespace-pre-line text-sm text-center">
            {serviceErrorMessage}
          </p>
        )}
        {/* divider */}
        {/* <div
          className={clsx("items-center gap-3", password ? "hidden" : "flex")}
        >
          <hr className="grow border-gray-300" />
          <span className="text-gray-400">หรือ</span>
          <hr className="grow border-gray-300" />
        </div> */}
        {/* register with google */}
        {/* <button
          type="button"
          aria-label="Continue with Google"
          className={clsx(
            "btn-secondary rounded-lg py-2.5 px-4 font-semibold text-base items-center justify-center gap-3",
            password ? "hidden" : "flex"
          )}
        >
          <GoogleIcon className="w-6 h-6 no-inherit" />
          <span>Continue with Google</span>
        </button> */}
        <div className="text-sm text-center flex items-center justify-center gap-2">
          <span className="text-gray-600 text-sm">มีบัญชีใช้งานอยู่แล้ว?</span>{" "}
          <Link
            href={`/auth/login`}
            className="text-primary-700 hover:text-primary-800 font-semibold flex items-center gap-1.5 group"
          >
            <span>เข้าสู่ระบบ</span>
            <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-all duration-500" />
          </Link>
        </div>
      </form>
    </>
  );
};

export default RegisterForm;
