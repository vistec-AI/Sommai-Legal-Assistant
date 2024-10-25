"use client";

import { useState, memo } from "react";

import InfoCircleIcon from "@/public/icons/info-circle.svg";
import CheckIcon from "@/public/icons/check.svg";
import { NotificationProps } from "@/app/types";
import clsx from "clsx";
import { Z_INDEX } from "@/app/constants";

const MAX_WIDTH_BADGE = "693px";

type NotificationContainerProps = {
  notificationList: NotificationProps[];
  containerClassName?: string;
  style?: Record<string, any>;
};

const Notification = memo(
  ({
    notificationList,
    containerClassName,
    style = {},
  }: NotificationContainerProps) => {
    return (
      <section
        style={{ zIndex: Z_INDEX.NOTIFICATION, ...style }}
        className={clsx(
          "absolute overflow-hidden transition-all lg:px-0 md:px-8 px-6 duration-[400ms] flex flex-col gap-2 w-full left-1/2 translate-x-[-50%]",
          containerClassName
        )}
      >
        {notificationList.map((notification, index) => {
          return (
            <Badge
              key={index}
              status={notification.status}
              content={notification.content}
            />
          );
        })}
      </section>
    );
  }
);

const Badge = ({ status, content }: NotificationProps) => {
  let borderColor = "border-gray-600/30";
  let outlineColor = "outline-gray-600/10";
  let textColor = "text-gray-600";

  if (status === "success") {
    borderColor = "border-success-600/30";
    outlineColor = "outline-success-600/10";
    textColor = "text-success-600";
  } else if (status === "error") {
    borderColor = "border-error-600/30";
    outlineColor = "outline-error-600/10";
    textColor = "text-error-600";
  } else if (status === "warning") {
    borderColor = "border-warning-600/30";
    outlineColor = "outline-warning-600/10";
    textColor = "text-warning-600";
  }

  const successIcon = <CheckIcon className={clsx("w-5 h-5", textColor)} />;
  const infoIcon = <InfoCircleIcon className={clsx("w-5 h-5", textColor)} />;

  return (
    <>
      <div
        className={clsx(
          "relative animate-slide-from-bottom transition-all w-full overflow-hidden border border-gray-300 shadow-xs bg-white/50 backdrop-blur-sm rounded-xl py-4 pr-4 pl-12 flex items-center gap-4"
        )}
      >
        {/* icon */}
        <div
          className={clsx(
            "absolute left-2 top-2.5 shrink-0 rounded-full flex justify-center items-center p-0.5 border-2 outline outline-2 outline-offset-2",
            borderColor,
            outlineColor
          )}
        >
          {status === "success" ? <>{successIcon}</> : <>{infoIcon}</>}
        </div>
        {/* content */}
        <div className="flex overflow-hidden text-sm">
          <p className="text-gray-700 font-semibold">{content}</p>
        </div>
      </div>
    </>
  );
};

export default Notification;
