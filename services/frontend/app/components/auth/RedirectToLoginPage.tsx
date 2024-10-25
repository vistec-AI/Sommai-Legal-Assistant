"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Link from "next/link";

const RedirectToLoginPage = () => {
  const router = useRouter();

  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    if (countdown <= 0) {
      router.push(`/auth/login`);
    }
  }, [countdown]);

  useEffect(() => {
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
  }, []);

  return (
    <>
      <div className="flex flex-col gap-2">
        <Link
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
  );
};

export default RedirectToLoginPage;
