"use client";

import Image from "next/image";

import BGPattern from "@/public/images/general/bg-pattern.webp";
import SommaiiLogo from "@/public/images/logo/sommaii.webp";
import ChatBanner from "@/public/images/general/chat-banner.webp";

const Banner = () => {
  const LAWS = [
    {
      text: "กฏหมายทั่วไป",
    },
    {
      text: "กฏหมายบริษัทจดทะเบียน",
    },
    {
      text: "กฏหมายรัฐวิสากิจ",
    },
  ];

  return (
    <div className="relative grow">
      <Image
        src={BGPattern}
        alt="banner background"
        className="fixed top-1/2 -translate-y-1/2 left-2/3 -translate-x-1/2 w-auto h-[825px] object-contain z-[0]"
      />
      <div className="relative flex flex-col items-center gap-4">
        <div className="flex flex-col items-center w-full">
          <div className="text-2xl text-gray-600 leading-[30px] text-left w-1/2">
            ไม่ว่าจะ
          </div>
          <div className="py-2 block text-center leading-[5rem] font-semibold [&_li]:block bg-clip-text text-transparent bg-gradient-primary">
            <div className="overflow-hidden h-[70px] flex xl:text-6xl lg:text-5xl text-4xl">
              <ul className="flip3 pt-2">
                {LAWS.map((laws, index) => {
                  return (
                    <li
                      key={index}
                      className="mb-[65px] h-[65px] block whitespace-nowrap"
                    >
                      {laws.text}
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1 justify-center flex-wrap font-medium text-3xl text-gray-600">
          <div className="flex items-center gap-1">
            <span>ให้</span>
            <Image
              src={SommaiiLogo}
              alt="Sommaii logo"
              className="h-[49px] w-auto object-contain"
            />
          </div>
          <span>หาคำตอบให้คุณ</span>
        </div>
        <Image
          src={ChatBanner}
          alt="Chat with Sommaii"
          className="h-[288px] xl:h-[400px] w-auto object-contain"
        />
      </div>
    </div>
  );
};

export default Banner;
