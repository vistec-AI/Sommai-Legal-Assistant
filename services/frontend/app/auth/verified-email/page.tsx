"use client";
import { useEffect, useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import { useSearchParams } from "next/navigation";

import Link from "next/link";
import { sanitizedInput } from "@/app/utils/validator";
import { ResponseError } from "@/app/types";
import {
  HTTP_401_UNAUTHORIZED,
  HTTP_RESPONSE_CODE,
  HTTP_400_BAD_REQUEST,
} from "@/app/constants/httpResponse";
import LoadingThreeDots from "@/app/components/auth/LoadingThreeDots";

import Image from "next/image";
import IllustrationSuccess from "@/public/images/general/illustration-success.webp";
import BGPattern from "@/public/images/general/bg-pattern.webp";
import api from "@/api";
import ResendEmail from "@/app/components/auth/ResendEmail";

const VerifiedEmailPage = () => {
  return (
    <section className="md:pt-8 transition-all relative flex flex-col justify-start items-center grow">
      <Image
        src={BGPattern}
        alt="banner background"
        className="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] w-auto h-[calc(100dvh_-_200px)] max-h-[900px] z-[0]"
      />
      <Suspense>
        <VerifiedEmailContent />
      </Suspense>
    </section>
  );
};

const VerifiedEmailContent = () => {
  const TIME_LIMIT = 5;
  const LOGIN_MAX_WEIGHT = "358px";

  const router = useRouter();
  const searchParams = useSearchParams();

  const tokenParam = searchParams.get("token");
  const emailParam = searchParams.get("email");

  const [startCountdown, setStartCountdown] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [countdown, setCountdown] = useState(TIME_LIMIT);
  const [emailTokenExpired, setEmailTokenExpired] = useState<boolean>(false);
  const [errorParams, setErrorParams] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const [alreadyVerifyEmail, setAlreadyVerifyEmail] = useState(false);

  const resetErrorState = () => {
    setErrorParams(false);
    setErrorMessage("");
    setEmailTokenExpired(false);
  };

  useEffect(() => {
    setLoading(true);
    const verifyEmailByToken = async () => {
      resetErrorState();

      if (tokenParam && emailParam) {
        const token = sanitizedInput(tokenParam);
        const email = sanitizedInput(emailParam);

        try {
          const response = await api.auth.isEmailEnabled(email);
          const data = await response.json();
          if (data?.enabled) {
            // already enabled email
            setAlreadyVerifyEmail(true);
            setLoading(false);
            setStartCountdown(true);
            return;
          } else {
            if (!alreadyVerifyEmail) {
              await api.auth.verifyEmail({ email, token });
              setStartCountdown(true);
            }
          }
          setAlreadyVerifyEmail(true);
          setLoading(false);
        } catch (error) {
          setLoading(false);
          console.error(error);
          if (error instanceof ResponseError) {
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
                  .INVALID_VERIFY_EMAIL_TOKEN ||
              error.response.status === HTTP_400_BAD_REQUEST
            ) {
              setErrorParams(true);
              return;
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
  }, [searchParams, alreadyVerifyEmail]);

  useEffect(() => {
    if (countdown <= 0) {
      router.push(`/auth/login`);
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
    <div className="flex flex-col gap-16 relative">
      {loading ? (
        <div>
          <LoadingThreeDots />
        </div>
      ) : (
        <>
          {/* redirect to log in */}

          {errorParams || emailTokenExpired || errorMessage ? (
            <div className="flex flex-col items-center">
              {errorParams && (
                <div className="flex flex-col gap-5 mx-auto">
                  <div className="flex flex-col gap-1 text-center">
                    <p className="text-error-600 text-lg font-medium whitespace-pre-line">
                      ลิงก์สำหรับยืนยันอีเมลไม่ถูกต้อง
                    </p>
                    <p className="text-gray-500">
                      โปรดตรวจสอบลิงก์จากอีเมล
                      <br />
                      {emailParam && (
                        <>
                          หรือส่งอีเมลยืนยันตัวตนอีกครั้งไปที่{" "}
                          <span className="font-semibold">{emailParam}</span>{" "}
                        </>
                      )}
                    </p>
                  </div>
                  {emailParam && (
                    <div className="flex flex-col mx-auto text-center gap-2 text-sm">
                      <ResendEmail
                        handleSetErrorMessage={(msg) => setErrorMessage(msg)}
                        email={emailParam}
                        resendClassName="btn-secondary-md mx-auto"
                      />
                    </div>
                  )}
                </div>
              )}
              {emailTokenExpired && (
                <div className="flex flex-col gap-6">
                  <p className="text-error-600 text-lg font-medium">
                    ลิงก์ยืนยันอีเมลหมดอายุแล้ว กรุณาเข้าสู่ระบบอีกครั้ง
                  </p>
                  <Link
                    style={{ maxWidth: LOGIN_MAX_WEIGHT }}
                    href={`/auth/login`}
                    className="btn-secondary-md"
                    aria-label="เข้าสู่ระบบ"
                  >
                    เข้าสู่ระบบ
                  </Link>
                </div>
              )}
              {errorMessage && (
                <p className="text-error-600 whitespace-pre-line text-sm text-center">
                  {errorMessage}
                </p>
              )}
              <br />
              <div className="text-gray-500 text-center">
                ต้องการความช่วยเหลือ ติดต่อพวกเราได้ที่
                <br />
                <a href="mailto:contact@vistec.ac.th" className="font-bold">
                  contact@vistec.ac.th
                </a>
              </div>
            </div>
          ) : (
            <>
              <header className="relative flex flex-col gap-2 text-center mx-auto">
                <h1 className="text-center w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
                  ลงทะเบียนเสร็จสมบูรณ์
                </h1>
                <p className="text-gray-500 text-xl leading-[26px]">
                  คุณสามารถเข้าใช้งานด้วยอีเมลและรหัสผ่านของคุณ
                </p>
              </header>
              {/* illustration */}
              <figure className="mx-auto relative">
                <Image
                  src={IllustrationSuccess}
                  alt="illustration success"
                  className="h-[122px] w-[122px] object-contain"
                />
              </figure>
              <div className="flex flex-col gap-2 mx-auto">
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
    </div>
  );
};

export default VerifiedEmailPage;
