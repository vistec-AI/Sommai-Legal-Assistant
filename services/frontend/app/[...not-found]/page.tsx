import Link from "next/link";

const NotFoundPage = () => {
  return (
    <section className="transition-all relative flex flex-col md:gap-12 gap-8 justify-start items-center grow md:px-8 px-6 py-12">
      {/* header */}
      <h1 className="text-center mx-auto w-fit bg-clip-text text-transparent bg-gradient-primary font-semibold">
        ไม่พบหน้าที่คุณต้องการ
      </h1>
      <section className="flex flex-col items-center w-full gap-8 max-w-[421px]">
        <p className="text-gray-600 text-lg text-center">
          ขออภัย, ไม่พบหน้าที่คุณพยายามเข้าถึงในเว็บไซต์ของเรา กรุณาตรวจสอบ URL
          อีกครั้ง
          <br />
          คุณสามารถกลับไปที่
          <span className="inline-block">หน้าแชทบอท</span> หรือลงชื่อเข้าใช้ใหม่
        </p>
        <div className="flex items-center gap-3">
          <Link href={"/auth/login"} className="btn-secondary-lg !px-[18px]">
            เข้าสู่ระบบ
          </Link>
          <Link href={"/chatbot"} className="btn-primary-lg !px-[18px]">
            แชทบอท
          </Link>
        </div>
      </section>
      <p className="text-center text-gray-500">
        หากยังคงพบปัญหา สามารถติดต่อเราเพื่อขอความช่วยเหลือ
        <br />
        ที่อีเมล{" "}
        <a
          href="mailto:contact@vistec.ac.th"
          className="font-bold text-gray-900"
        >
          contact@vistec.ac.th
        </a>
        <br />
      </p>
    </section>
  );
};

export default NotFoundPage;
