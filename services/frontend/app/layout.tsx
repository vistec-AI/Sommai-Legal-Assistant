import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Noto_Sans_Thai } from "next/font/google";
import localFont from "next/font/local";
import { Provider } from "./context";
import { GoogleAnalytics } from "@next/third-parties/google";
import HotjarScript from "./components/HotjarScript";
import { headers } from "next/headers";

import "./globals.css";

import Navbar from "./components/Navbar";
import clsx from "clsx";
import TabSelection from "./components/TabSelection";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const notoSansThai = Noto_Sans_Thai({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-noto",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://sommai.wangchan.ai"),
  title: "Chatbot | สมหมาย",
  description: "ถามคำถาม-หาคำตอบทางกฏหมายที่คุณต้องการได้ที่โหมดแชทบอท",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        {process.env.NEXT_PUBLIC_HOTJAR_ID &&
          process.env.NODE_ENV === "production" && (
            <HotjarScript hjid={process.env.NEXT_PUBLIC_HOTJAR_ID} />
          )}
      </head>
      <body suppressHydrationWarning={true}>
        <Provider>
          <main
            className={clsx(
              "flex flex-col justify-between font-noto h-[100dvh] overflow-hidden",
              notoSansThai.variable,
              inter.variable
            )}
          >
            <section className="grow overflow-auto flex flex-col relative">
              <Navbar />
              <TabSelection />
              {children}
            </section>
            {/* Footer */}
          </main>
        </Provider>
      </body>
      {process.env.NEXT_PUBLIC_GOOGLE_ANALYTICS &&
        process.env.NODE_ENV === "production" && (
          <GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GOOGLE_ANALYTICS} />
        )}
    </html>
  );
}
