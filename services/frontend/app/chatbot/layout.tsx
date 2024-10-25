import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chatbot | สมหมาย",
  description: "ถามคำถาม-หาคำตอบทางกฏหมายที่คุณต้องการได้ที่โหมดแชทบอท",
};

export default function ChatbotLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
