"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { validateEmail } from "@/app/utils/validator";
import Input from "../common/Input";

const ForgotPasswordForm = () => {
  const router = useRouter();

  const [email, setEmail] = useState<string>("");
  const [emailError, setEmailError] = useState<boolean>(false);

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setEmail(value);
    if (emailError) {
      setEmailError(false);
    }
  };

  // send reset password link to email
  const handleSubmitSendEmail = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const isValidEmail = validateEmail(email);
    if (!isValidEmail) {
      setEmailError(true);
      return;
    }
    // TODO: integrate reset password api

    router.push(`/auth/forgot-password?email=${email}`);
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
      <button
        type="submit"
        aria-label="ดำเนินการต่อ"
        className="btn-primary-md mx-auto min-w-[158px]"
        disabled={!email}
      >
        ดำเนินการต่อ
      </button>
    </form>
  );
};

export default ForgotPasswordForm;
