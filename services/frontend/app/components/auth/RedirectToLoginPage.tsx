"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSearchParams } from "next/navigation";

import Link from "next/link";
import { sanitizedInput } from "@/app/utils/validator";
import { ResponseError } from "@/app/types";
import {
  HTTP_401_UNAUTHORIZED,
  HTTP_RESPONSE_CODE,
} from "@/app/constants/httpResponse";

import LoadingThreeDots from "./LoadingThreeDots";

const RedirectToLoginPage = () => {
  const TIME_LIMIT = 5;
  const LOGIN_MAX_WEIGHT = "358px";

  const router = useRouter();
  const searchParams = useSearchParams();

  const [startCountdown, setStartCountdown] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [countdown, setCountdown] = useState(TIME_LIMIT);
  const [emailTokenExpired, setEmailTokenExpired] = useState<boolean>(false);
  const [errorParams, setErrorParams] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    const tokenParam = searchParams.get("token");
    const emailParam = searchParams.get("email");

    const verifyEmailByToken = async () => {
      if (tokenParam && emailParam) {
        const token = sanitizedInput(tokenParam);
        const email = sanitizedInput(emailParam);

        try {
          setLoading(false);
        } catch (error) {
          setLoading(false);
          console.error(error);
          if (error instanceof ResponseError) {
            if (error.response.status === HTTP_401_UNAUTHORIZED) {
              if (
                error.response.code ===
                HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED]
                  .EMAIL_VERIFY_TOKEN_EXPIRED
              ) {
                setEmailTokenExpired(true);
              } else if (
                error.response.code ===
                  HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].EMAIL_NOT_EXISTS ||
                error.response.code ===
                  HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED]
                    .INVALID_VERIFY_EMAIL_TOKEN
              ) {
                setErrorParams(true);
                return;
              }
            }
            setErrorMessage("ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง");
          }
        }
      } else {
        setErrorParams(true);
        setLoading(false);
      }
    };

    verifyEmailByToken();
  }, [searchParams]);

  useEffect(() => {
    if (countdown <= 0) {
      // router.push(`/auth/login`);
    }
  }, [countdown]);

  useEffect(() => {
    if (startCountdown) {
      const interval = setInterval(() => {
        setCountdown((currentTime) => {
          if (currentTime > 0) {
            return currentTime - 1;
          } else {
            clearInterval(interval);
            return currentTime;
          }
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [startCountdown]);

  return (
    <>
      {loading ? (
        <div className="mx-auto">
          <LoadingThreeDots />
        </div>
      ) : (
        <>
          {errorParams ? (
            <div className="flex flex-col">
              <p className="text-error-600 whitespace-pre-line text-sm text-center">
                ลิงก์สำหรับตั้งค่ารหัสผ่านใหม่ไม่ถูกต้อง
                <br />
                ต้องการความช่วยเหลือ ติดต่อพวกเราได้ที่{" "}
                <a href="mailto:contact@vistec.ac.th" className="font-bold">
                  contact@vistec.ac.th
                </a>
              </p>
            </div>
          ) : (
            <>
              <div className="flex flex-col gap-2 mx-auto">
                {!emailTokenExpired && (
                  <p className="text-error-600 font-medium">
                    ลิงก์ยืนยันอีเมลหมดอายุแล้ว กรุณาเข้าสู่ระบบอีกครั้ง
                  </p>
                )}
                <Link
                  style={{ maxWidth: LOGIN_MAX_WEIGHT }}
                  href={`/auth/login`}
                  className="btn-secondary-md"
                  aria-label="เข้าสู่ระบบ"
                >
                  เข้าสู่ระบบ
                </Link>
                <p className="text-gray-500 text-base leading-7 text-center">
                  เรากำลังพาคุณไปยังหน้าเข้าสู่ระบบใน {countdown} วินาที
                </p>
              </div>
            </>
          )}
        </>
      )}
    </>
  );
};

export default RedirectToLoginPage;
