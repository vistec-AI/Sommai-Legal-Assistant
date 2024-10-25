"use client";

import React from "react";
import clsx from "clsx";

import LoadingThreeDots from "../auth/LoadingThreeDots";
import { useLoading } from "@/app/context/LoadingFullScreenContext";

const LoadingFullScreen = ({
  backgroundClassName,
}: {
  backgroundClassName?: string;
}) => {
  const { loadingText } = useLoading();

  return (
    <div className={clsx("fixed inset-0 overflow-y-auto z-[3000]")}>
      <div
        className={clsx(
          "fixed inset-0 w-full h-full bg-white opacity-60",
          backgroundClassName
        )}
      ></div>
      <div className="flex items-center flex-col gap-2 justify-center h-screen relative">
        {loadingText && (
          <span className="text-gray-500 font-medium text-center">
            {loadingText}
          </span>
        )}
        <LoadingThreeDots />
      </div>
    </div>
  );
};

export default LoadingFullScreen;
