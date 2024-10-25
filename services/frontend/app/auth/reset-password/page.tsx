import { Suspense } from "react";
import ResetPasswordForm from "@/app/components/auth/ResetPasswordForm";

export const metadata = {
  title: "ตั้งค่ารหัสผ่านใหม่ | สมหมาย",
  description: "ตั้งค่ารหัสผ่านใหม่",
};

const ResetPasswordPage = () => {
  return (
    <section className="transition-all relative flex flex-col gap-8 justify-start items-center grow">
      {/* header */}
      <h1 className="text-center mx-auto w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
        ตั้งค่ารหัสผ่านใหม่
      </h1>
      <section className="flex flex-col gap-1 w-full max-w-[421px]">
        <p className="text-gray-600 text-lg text-center">กรอกรหัสผ่านใหม่</p>
        {/* reset password form */}
        <Suspense>
          <ResetPasswordForm />
        </Suspense>
      </section>
    </section>
  );
};

export default ResetPasswordPage;
