import Link from "next/link";

import ForgotPasswordForm from "@/app/components/auth/ForgotPasswordForm";
import ArrowRightIcon from "@/public/icons/arrow-right.svg";

export const metadata = {
  title: "รีเซ็ตรหัสผ่าน | สมหมาย",
  description: "วิธีการรีเซ็ตรหัสผ่านของสมหมาย",
};

const ForgotPasswordPage = ({ searchParams }: any) => {
  return (
    <section className="transition-all max-w-[1440px] mx-auto relative flex flex-col gap-16 justify-start items-center grow">
      <div className="flex flex-col gap-4 relative w-full">
        {/* header */}
        <h1 className="text-center mx-auto w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
          รีเซ็ตรหัสผ่าน
        </h1>
        {/* detail for resetting password */}
        <section className="flex flex-col gap-4 text-left w-full">
          <p className="text-gray-700 sm:text-lg leading-[26px]">
            หากคุณต้องการเปลี่ยนรหัสผ่านสำหรับบัญชีของคุณ
            <br />
            กรุณาส่งอีเมลมาที่{" "}
            <a
              href="mailto:contact@vistec.ac.th"
              className="font-bold text-gray-900"
            >
              contact@vistec.ac.th
            </a>
            <br />
          </p>
          <p className="text-gray-700 sm:text-lg">โดยมีรายละเอียดดังนี้:</p>
          <ol className="font-medium list-decimal text-gray-600 flex flex-col gap-3 sm:text-lg">
            <li>
              ใช้หัวข้ออีเมล (Subject):{" "}
              <span className="font-bold">แจ้งความต้องการรีเซ็ตรหัสผ่าน</span>
            </li>
            <li>ระบุอีเมลที่ใช้สมัครบัญชีของคุณในเนื้อหาอีเมล</li>
          </ol>
        </section>
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
