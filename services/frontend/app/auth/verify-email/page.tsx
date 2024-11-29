"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { sanitizedInput } from "@/app/utils/validator";
import { ResponseError } from "@/app/types";
import {
  HTTP_401_UNAUTHORIZED,
  HTTP_400_BAD_REQUEST,
  HTTP_500_INTERNAL_SERVER_ERROR,
} from "@/app/constants/httpResponse";
import api from "@/api";
import LoadingThreeDots from "@/app/components/auth/LoadingThreeDots";

import ResendEmail from "@/app/components/auth/ResendEmail";

const VerifyEmailPage = ({ searchParams }: any) => {
  const registerEmail = useMemo(() => {
    return sanitizedInput(searchParams.email || "");
  }, [searchParams?.email]);

  const [loading, setLoading] = useState(true);

  const [errorMessage, setErrorMessage] = useState<string>("");
  const [serviceErrorMessage, setServiceErrorMessage] = useState<string>("");

  // const interval = useRef<NodeJS.Timeout | null>(null);
  const router = useRouter();

  useEffect(() => {
    const initialUserStatus = async () => {
      try {
        const response = await api.auth.isEmailEnabled(registerEmail);
        const data = await response.json();
        if (data?.enabled) {
          // already enabled email
          router.replace("/auth/login");
        }
        setLoading(false);
      } catch (error) {
        console.error(error);
        setLoading(false);
        if (error instanceof ResponseError) {
          if (error.response.status === HTTP_400_BAD_REQUEST) {
            setErrorMessage("อีเมลไม่ถูกต้อง โปรดเข้าสู่ระบบใหม่อีกครั้ง");
            return;
          }
          setServiceErrorMessage("ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง");
        }
      }
    };

    if (registerEmail) {
      initialUserStatus();
    }
  }, [searchParams?.email]);

  return (
    <>
      <section className="transition-all text-center max-w-[1440px] mx-auto relative flex flex-col md:pt-8 gap-16 justify-start items-center grow">
        <div className="flex flex-col gap-4 relative w-full">
          {/* header */}
          <h1 className="text-center mx-auto w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
            โปรดยืนยันอีเมล
          </h1>
          <p className="text-lg text-gray-500">
            ขอบคุณที่ลงทะเบียนใช้งานกับ สมหมาย!
            <br />
            เราได้ส่งลิงก์ยืนยันตัวตนไปที่อีเมล {registerEmail}
            <br />
            <br />
            โปรดยืนยันตัวตนภายใน 24 ชั่วโมง เพื่อให้การลงทะเบียนเสร็จสมบูรณ์
          </p>
        </div>
        {loading ? (
          <>
            <LoadingThreeDots />
          </>
        ) : (
          <div className="flex flex-col gap-8">
            {!errorMessage && (
              <div className="text-base">
                <span className="font-medium text-gray-500">
                  ไม่ได้รับอีเมลยืนยันตัวตน?
                </span>{" "}
                <ResendEmail
                  email={registerEmail}
                  handleSetErrorMessage={(msg) => setErrorMessage(msg)}
                  resendClassName={
                    "font-semibold disabled:hover:no-underline hover:underline text-primary-700"
                  }
                />
              </div>
            )}
            {errorMessage && (
              <p className="text-sm text-error-600">{errorMessage}</p>
            )}
            {serviceErrorMessage && (
              <p className="text-sm text-error-600">{serviceErrorMessage}</p>
            )}
          </div>
        )}
      </section>
    </>
  );
};

export default VerifyEmailPage;
