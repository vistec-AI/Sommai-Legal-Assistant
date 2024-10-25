import TermsOfUse from "../components/TermsOfUse";

export const metadata = {
  title: "ข้อกำหนดและเงื่อนไขการใช้งาน (Terms of Use) | สมหมาย",
  description: "ข้อกำหนดและเงื่อนไขการใช้งาน (Terms of Use)",
};

const TermsOfUsePage = () => {
  return (
    <main className="max-w-[940px] mx-auto py-8 md:px-8 px-6 flex flex-col gap-6">
      <TermsOfUse />
    </main>
  );
};

export default TermsOfUsePage;
