import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chatbot Arena | สมหมาย",
  description: "หาคำตอบที่โดนใจคุณด้วยการเปรียบเทียบคำตอบระหว่าง 2 โมเดล",
};

export default function ChatbotArenaLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
