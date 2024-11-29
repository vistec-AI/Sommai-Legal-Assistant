import { useState, useRef, useEffect } from "react";
import { ResponseError } from "@/app/types";

import api from "@/api";

type ResendEmailProps = {
  email: string;
  handleSetErrorMessage: (msg: string) => void;
  resendClassName?: string;
};

const ResendEmail = ({
  email,
  resendClassName,
  handleSetErrorMessage,
}: ResendEmailProps) => {
  const TIME_LIMIT = 60;

  const [resendCountdown, setResendCountdown] = useState<number>(TIME_LIMIT);
  const [preventClickResend, setPreventClickResend] = useState<boolean>(false);

  const interval = useRef<NodeJS.Timeout | null>(null);

  const countdown = () => {
    interval.current = setInterval(() => {
      setResendCountdown((prevState) => prevState - 1);
    }, 1000);
  };

  const handleResendEmailVerification = async () => {
    try {
      setPreventClickResend(true);
      countdown();
      await api.auth.resendTokenVerifyEmail({ email: email });
    } catch (error) {
      if (error instanceof ResponseError) {
        handleSetErrorMessage("ขณะนี้ระบบมีปัญหา โปรดลองอีกครั้งในภายหลัง");
      }
      setPreventClickResend(false);
    }
  };
  useEffect(() => {
    if (resendCountdown === 0) {
      if (interval.current) clearInterval(interval.current);
      setResendCountdown(TIME_LIMIT);
      setPreventClickResend(false);
      return;
    }
  }, [resendCountdown]);

  return (
    <>
      <button
        type="button"
        aria-label="ส่งอีเมลใหม่อีกครั้ง"
        className={resendClassName}
        onClick={handleResendEmailVerification}
        disabled={resendCountdown !== TIME_LIMIT || preventClickResend}
      >
        ส่งอีเมลใหม่อีกครั้ง
      </button>
      {resendCountdown !== TIME_LIMIT && (
        <span className="font-semibold text-primary-700">
          ใน {resendCountdown} วินาที
        </span>
      )}
    </>
  );
};

export default ResendEmail;
