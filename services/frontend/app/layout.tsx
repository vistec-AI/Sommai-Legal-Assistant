import type { Metadata } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";
import { Provider } from "./context";
import { GoogleAnalytics } from "@next/third-parties/google";
import HotjarScript from "./components/HotjarScript";

import "./globals.css";

import Navbar from "./components/Navbar";
import clsx from "clsx";
import TabSelection from "./components/TabSelection";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const sukhumvit = localFont({
  src: [
    {
      path: "../public/fonts/Sukhumvit/SukhumvitSet-Thin.ttf",
      weight: "200",
      style: "normal",
    },
    {
      path: "../public/fonts/Sukhumvit/SukhumvitSet-Light.ttf",
      weight: "300",
      style: "normal",
    },
    {
      path: "../public/fonts/Sukhumvit/SukhumvitSet-Medium.ttf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../public/fonts/Sukhumvit/SukhumvitSet-SemiBold.ttf",
      weight: "500",
      style: "normal",
    },
    {
      path: "../public/fonts/Sukhumvit/SukhumvitSet-Bold.ttf",
      weight: "600",
      style: "normal",
    },
  ],
  variable: "--font-sukhumvit",
  display: "swap",
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
              "flex flex-col justify-between font-sukhumvit h-[100dvh] overflow-hidden",
              sukhumvit.variable,
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
