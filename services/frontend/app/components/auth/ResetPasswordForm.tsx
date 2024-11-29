"use client";

import { useState } from "react";
import PasswordInput from "../common/PasswordInput";
import { useRouter, useSearchParams } from "next/navigation";
import { ResponseError } from "@/app/types";

import api from "@/api";
import {
  HTTP_401_UNAUTHORIZED,
  HTTP_RESPONSE_CODE,
} from "@/app/constants/httpResponse";

const ResetPasswordForm = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get("email");
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordNotMatch, setPasswordNotMatch] = useState<boolean>(false);
  const [validPassword, setValidPassword] = useState<boolean>(false);
  const [serviceErrorMessage, setServiceErrorMessage] = useState<string>("");

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value);
  };

  const handleConfirmPasswordChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setConfirmPassword(event.target.value);
  };

  // reset password
  const handleResetPassword = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setPasswordNotMatch(false);
    setServiceErrorMessage("");
    setServiceErrorMessage("");

    if (password !== confirmPassword) {
      setPasswordNotMatch(true);
      return;
    }
    if (!email || !token) {
      setServiceErrorMessage("ลิงก์สำหรับตั้งค่ารหัสผ่านใหม่ไม่ถูกต้อง");
      return;
    }
    try {
      const resetPasswordForm = {
        email: email,
        token: token,
        new_password: password,
      };
      await api.auth.resetPassword(resetPasswordForm);

      router.push(`/auth/login?from=reset-password`);
    } catch (error) {
      if (error instanceof ResponseError) {
        if (error.response.status === HTTP_401_UNAUTHORIZED) {
          if (
            error.response.code ===
            HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED]
              .INVALID_RESET_PASSWORD_TOKEN
          ) {
            setServiceErrorMessage(
              "โทเค็นไม่ถูกต้อง โปรดตรวจสอบอีเมลอีกครั้ง หรือส่งคำขอเปลี่ยนรหัสผ่านใหม่"
            );
            return;
          } else if (
            error.response.code ===
            HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED]
              .RESET_PASSWORD_TOKEN_EXPIRED
          ) {
            setServiceErrorMessage(
              "โทเค็นหมดอายุแล้ว โปรดส่งคำขอเปลี่ยนรหัสผ่านใหม่อีกครั้ง"
            );
            return;
          }
        }
        setServiceErrorMessage(`ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง`);
      }
    }
  };

  return (
    <>
      <form
        onSubmit={handleResetPassword}
        className="p-6 flex flex-col gap-4 shadow-xl rounded-xl border border-gray-200"
        noValidate
      >
        <PasswordInput
          id="resetPassword"
          name="password"
          onChange={handlePasswordChange}
          value={password}
          label="รหัสผ่าน"
          placeholder="กรอกรหัสผ่าน"
          autoComplete="password"
          showValidation={true}
          handleSetValidPassword={(isValid) => {
            setValidPassword(isValid);
          }}
        />
        <PasswordInput
          id="confirmResetPassword"
          name="confirmPassword"
          onChange={handleConfirmPasswordChange}
          value={confirmPassword}
          error={passwordNotMatch ? "รหัสผ่านไม่ตรงกัน โปรดลองอีกครั้ง" : ""}
          label="ยืนยันรหัสผ่าน"
          placeholder="กรอกรหัสผ่านใหม่อีกครั้ง"
        />
        <button
          type="submit"
          aria-label="ตั้งค่ารหัสผ่าน"
          className="btn-primary-md"
          disabled={!password || !confirmPassword || !validPassword}
        >
          ตั้งค่ารหัสผ่าน
        </button>
        {serviceErrorMessage && (
          <p className="text-gray-600 whitespace-pre-line text-sm text-center">
            {serviceErrorMessage}
            <br />
            ต้องการความช่วยเหลือ ติดต่อพวกเราได้ที่{" "}
            <a href="mailto:contact@vistec.ac.th" className="font-bold">
              contact@vistec.ac.th
            </a>
          </p>
        )}
      </form>
    </>
  );
};
export default ResetPasswordForm;
