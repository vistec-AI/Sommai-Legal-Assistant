import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ยืนยันการลงทะเบียน | สมหมาย",
  description: "ยืนยันการลงทะเบียนอีเมลเพื่อใช้งานสมหมายแชทบอท",
};

export default function VerifyEmailLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
