import Link from "next/link";

import Banner from "@/app/components/auth/Banner";
import RegisterForm from "@/app/components/auth/RegisterForm";

export const metadata = {
  title: "สมัครสมาชิก | สมหมาย",
  description:
    "สมัครสมาชิกกับสมหมายเพื่อถามคำถาม-หาคำตอบทางกฏหมายที่คุณต้องการ",
};

const RegisterPage = () => {
  return (
    <>
      <div className="flex grow items-center justify-between lg:gap-8 gap-6 max-w-[1440px] w-full mx-auto">
        <section className="grow basis-0 flex justify-center relative z-10">
          <div className="flex flex-col gap-4 max-w-[421px] w-full">
            <section className="flex flex-col gap-2">
              {/* header */}
              <div className="text-base text-gray-500">
                สร้างบัญชีเพื่อเริ่มต้นใช้งาน
              </div>
              {/* register section */}
              <RegisterForm />
            </section>
            <div className="text-center text-sm">
              <span className="text-gray-500">
                By register you agree to the
              </span>{" "}
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
        <section className="grow basis-0 md:flex hidden justify-center overflow-visible">
          <Banner />
        </section>
      </div>
    </>
  );
};

export default RegisterPage;
