"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useChatbot } from "@/app/context/ChatbotContext";
import { CHAT_MODE, APP_PATH } from "@/app/constants";
import clsx from "clsx";

const TabSelection = () => {
  const pathname = usePathname();
  const isAppPath = APP_PATH.includes(pathname);

  const { stopResponseSSE } = useChatbot();

  return (
    <>
      {isAppPath && (
        <ul className="flex gap-2 items-end md:justify-start justify-center md:mx-8 mx-6 border-b border-gray-200">
          {Object.values(CHAT_MODE).map((mode, index) => {
            const modePathname = mode?.toLowerCase().replaceAll(" ", "-");
            return (
              <li key={index}>
                <Link
                  onClick={async () => {
                    stopResponseSSE();
                  }}
                  href={`/${modePathname}`}
                  className={clsx(
                    "!font-inter text-sm md:p-3 p-2 border-b-2 font-semibold transition-colors block",
                    pathname === `/${modePathname}`
                      ? "border-primary-600 bg-primary-50 text-primary-700"
                      : "border-transparent bg-white text-gray-500 hover:border-primary-600 hover:bg-primary-50 hover:text-primary-700"
                  )}
                >
                  {mode}
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
};

export default TabSelection;
