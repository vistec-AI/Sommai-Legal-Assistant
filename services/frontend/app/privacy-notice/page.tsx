import PrivacyNotice from "../components/PrivacyNotice";

export const metadata = {
  title: "คำประกาศเกี่ยวกับความเป็นส่วนตัว (Privacy Notice) | สมหมาย",
  description: "คำประกาศเกี่ยวกับความเป็นส่วนตัว (Privacy Notice)",
};

const PrivacyNoticePage = () => {
  return (
    <main className="max-w-[940px] mx-auto py-8 md:px-8 px-6 flex flex-col gap-6">
      <PrivacyNotice />
    </main>
  );
};

export default PrivacyNoticePage;
