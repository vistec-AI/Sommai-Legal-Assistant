"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { validateEmail, sanitizedInput } from "@/app/utils/validator";
import { ResponseError } from "@/app/types";
import {
  HTTP_400_BAD_REQUEST,
  HTTP_401_UNAUTHORIZED,
  HTTP_500_INTERNAL_SERVER_ERROR,
} from "@/app/constants/httpResponse";
import Input from "../common/Input";
import api from "@/api";
import LoadingThreeDots from "./LoadingThreeDots";

const ForgotPasswordForm = () => {
  const router = useRouter();

  const [email, setEmail] = useState<string>("");
  const [emailError, setEmailError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setEmail(value);
    if (emailError) {
      setEmailError(false);
    }
  };

  // send reset password link to email
  const handleSubmitSendEmail = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setLoading(true);
    setErrorMessage("");

    const isValidEmail = validateEmail(email);
    if (!isValidEmail) {
      setEmailError(true);
      return;
    }
    const sanitizedEmail = sanitizedInput(email);
    try {
      await api.auth.requestResetPassword({ email: sanitizedEmail });
      router.push(`/auth/forgot-password?email=${sanitizedEmail}`);
    } catch (error) {
      console.error(error);
      setLoading(false);
      if (error instanceof ResponseError) {
        if (
          error.response.status === HTTP_400_BAD_REQUEST ||
          error.response.status === HTTP_401_UNAUTHORIZED
        ) {
          setErrorMessage("อีเมลไม่ถูกต้อง โปรดตรวจสอบใหม่อีกครั้ง");
          return;
        }

        setErrorMessage("ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง");
      }
    }
  };

  return (
    <form
      onSubmit={handleSubmitSendEmail}
      className="flex flex-col gap-4"
      noValidate={true}
    >
      <Input
        id="emailForgetPassword"
        name="email"
        onChange={handleEmailChange}
        value={email}
        error={emailError ? "รูปแบบอีเมลไม่ถูกต้อง" : ""}
        type="email"
        label="อีเมล"
        placeholder="กรอกอีเมล"
        autoComplete="email"
        autoFocus
      />
      {loading ? (
        <div className="m-auto min-h-[42px] flex items-center">
          <LoadingThreeDots />
        </div>
      ) : (
        <button
          type="submit"
          aria-label="ดำเนินการต่อ"
          className="btn-primary-md mx-auto min-w-[158px]"
          disabled={!email || loading}
        >
          ดำเนินการต่อ
        </button>
      )}
      {errorMessage && (
        <p className="text-center text-sm text-error-600">{errorMessage}</p>
      )}
    </form>
  );
};

export default ForgotPasswordForm;
