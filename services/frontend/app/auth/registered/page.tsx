import Image from "next/image";
import IllustrationSuccess from "@/public/images/general/illustration-success.webp";
import BGPattern from "@/public/images/general/bg-pattern.webp";
import RedirectToLoginPage from "@/app/components/auth/RedirectToLoginPage";

export const metadata = {
  title: "สมัครสมาชิกสำเร็จ | สมหมาย",
  description: "สมัครสมาชิกสำเร็จ",
};

const RegisteredPage = () => {
  return (
    <section className="pt-8 transition-all relative flex flex-col justify-start items-center grow">
      <Image
        src={BGPattern}
        alt="banner background"
        className="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] w-auto h-[calc(100dvh_-_200px)] max-h-[900px] z-[0]"
      />
      <div className="flex flex-col gap-16 relative">
        {/* header */}
        <header className="relative flex flex-col gap-2 text-center mx-auto">
          <h1 className="text-center w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
            สร้างบัญชีสำเร็จ
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
        {/* redirect to log in */}
        <RedirectToLoginPage />
      </div>
    </section>
  );
};

export default RegisteredPage;
