import Link from "next/link";
import LoginForm from "@/app/components/auth/LoginForm";
import Banner from "@/app/components/auth/Banner";
import clsx from "clsx";

export const metadata = {
  title: "เข้าสู่ระบบ | สมหมาย",
  description: "เข้าสู่ระบบสมหมายเพื่อถามคำถาม-หาคำตอบทางกฏหมายที่คุณต้องการ",
};

const LogInPage = ({ searchParams }: any) => {
  const fromResetPasswordState = searchParams?.from === "reset-password";
  return (
    <div
      className={clsx(
        "flex grow justify-between lg:gap-8 gap-6 max-w-[1440px] w-full mx-auto",
        fromResetPasswordState ? "items-start" : "items-center"
      )}
    >
      <section className="grow basis-0 flex justify-center relative z-10">
        <div
          className={clsx(
            "flex flex-col gap-4 w-full",
            fromResetPasswordState ? "max-w-[430px]" : "max-w-[421px]"
          )}
        >
          <section className="flex flex-col gap-2">
            {/* header */}
            {fromResetPasswordState && (
              <h1 className="text-left mx-auto w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
                แชทบอทกฏหมาย
              </h1>
            )}
            <div className="text-base text-gray-500">
              {fromResetPasswordState
                ? `ตั้งค่ารหัสผ่านใหม่แล้ว เข้าสู่ระบบเพื่อใช้งาน`
                : `เข้าสู่ระบบเพื่อใช้งาน`}
            </div>
            {/* login section */}
            <LoginForm />
          </section>
          <div className="text-center text-sm">
            <span className="text-gray-500">By login you agree to the</span>{" "}
            <Link
              href={`/terms-of-use`}
              target="_blank"
              className="text-primary-700 hover:text-primary-800 font-semibold"
            >
              Terms of Use
            </Link>
            <span className="text-gray-500"> and </span>
            <Link
              href={`/privacy-notice`}
              target="_blank"
              className="text-primary-700 hover:text-primary-800 font-semibold"
            >
              Privacy Notice
            </Link>
          </div>
        </div>
      </section>
      <section
        className={clsx(
          "grow basis-0 justify-center overflow-visible",
          fromResetPasswordState ? "hidden" : "md:flex hidden"
        )}
      >
        <Banner />
      </section>
    </div>
  );
};

export default LogInPage;
