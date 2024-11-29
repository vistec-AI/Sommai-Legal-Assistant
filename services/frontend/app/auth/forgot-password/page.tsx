import Link from "next/link";

import ForgotPasswordForm from "@/app/components/auth/ForgotPasswordForm";
import ArrowRightIcon from "@/public/icons/arrow-right.svg";

export const metadata = {
  title: "ตั้งค่ารหัสผ่านใหม่ | สมหมาย",
  description: "ตั้งค่ารหัสผ่านของแชทบอทสมหมายใหม่",
};

const ForgotPasswordPage = ({ searchParams }: any) => {
  return (
    <section className="transition-all max-w-[1440px] mx-auto relative flex flex-col gap-16 justify-start items-center grow">
      <div className="flex flex-col gap-4 relative w-full items-center">
        {/* header */}
        <h1 className="text-center mx-auto w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
          ตั้งค่ารหัสผ่านใหม่
        </h1>
        {/* detail for resetting password */}
        {searchParams.email ? (
          <>
            <p className="text-gray-600 sm:text-lg leading-[26px] text-center">
              เราได้ส่งลิงก์รีเซ็ตรหัสผ่านไปที่{" "}
              <span className="font-medium">{searchParams.email}</span>
              <br />
              โปรดตรวจสอบกล่องจดหมายของคุณและคลิกที่ลิงก์ที่ได้รับเพื่อ
              <br />
              รีเซ็ตรหัสผ่าน
            </p>
          </>
        ) : (
          <section className="flex flex-col gap-4 text-left w-full max-w-[373px]">
            <p className="text-gray-600 sm:text-lg leading-[26px] text-center">
              โปรดใส่อีเมลที่ลงทะเบียนไว้ด้านล่างและเราจะส่งลิงก์ให้คุณเพื่อรีเซ็ตรหัสผ่านของคุณ
            </p>
            <ForgotPasswordForm />
          </section>
        )}
      </div>
      {!searchParams?.email && (
        <section className="flex items-center gap-2">
          <span className="text-gray-600 text-sm">ยังไม่มีบัญชีใช้งาน?</span>{" "}
          <Link
            href={`/auth/register`}
            className="flex items-center gap-1.5 font-semibold text-sm text-primary-700 hover:text-primary-800 group"
          >
            <span>สร้างบัญชีใช้งาน</span>
            <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-all duration-500" />
          </Link>
        </section>
      )}
    </section>
  );
};

export default ForgotPasswordPage;
