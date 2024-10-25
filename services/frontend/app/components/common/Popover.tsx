"use client";

import { useEffect, useRef } from "react";
import clsx from "clsx";
import React from "react";
import { Z_INDEX } from "@/app/constants";

type PopoverProps = {
  isOpen: boolean;
  handleSetIsOpen: (state: boolean) => void;
  content: React.ReactNode;
  children: React.ReactNode;
  position: "bottom-left" | "bottom-right" | "top-left" | "top-right";
  delay?: string;
  className?: string;
  contentClassName?: string;
};

const Popover = ({
  isOpen,
  handleSetIsOpen,
  content,
  children,
  position = "bottom-left",
  delay = "75",
  className = "",
  contentClassName = "",
}: PopoverProps) => {
  const popoverRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (popoverRef.current && isOpen) {
      popoverRef.current.focus();
    }
  }, [content, isOpen]);

  return (
    <div
      ref={popoverRef}
      tabIndex={0}
      onBlur={(event: React.FocusEvent<HTMLDivElement>) => {
        if (!event.currentTarget.contains(event.relatedTarget)) {
          handleSetIsOpen(false);
        }
      }}
      onClick={(event: React.MouseEvent<HTMLDivElement>) => {
        event.preventDefault();
        event.stopPropagation();
      }}
      className={clsx("relative outline-none", className)}
    >
      {children}
      <div
        style={{ zIndex: Z_INDEX.POPOVER }}
        className={clsx(
          isOpen
            ? "visible scale-y-100 origin-top opacity-100"
            : "invisible opacity-0 h-0 w-0 overflow-hidden hidden",
          position === "top-left" && "bottom-full left-0",
          position === "bottom-left" && "top-full left-0",
          position === "top-right" && "bottom-full right-0",
          position === "bottom-right" && "top-full right-0",
          contentClassName,
          `delay-[${delay}]`,
          "absolute w-auto transition-alls duration-100 outline-none"
        )}
      >
        {content}
      </div>
    </div>
  );
};

export default Popover;
