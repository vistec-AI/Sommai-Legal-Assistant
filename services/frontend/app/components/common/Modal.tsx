"use client";

import React, { ReactNode, useEffect } from "react";
import { Z_INDEX } from "@/app/constants";
import clsx from "clsx";
import Image from "next/image";

import XClose from "@/public/icons/x-close.svg";
import PatternDecorativeImg from "@/public/images/general/pattern-decorative.webp";

type ModalProps = {
  onClose: () => void;
  body: ReactNode;
  className?: string;
  closable?: boolean;
  closeIconClassName?: string;
  showMask?: boolean;
  showCloseButton?: boolean;
  isMaskClosable?: boolean;
  showPatternDecorative?: boolean;
};

const Modal = ({
  onClose,
  className = "",
  body = null,
  closable = true,
  showCloseButton = true,
  closeIconClassName = "top-3.5 right-3.5",
  showMask = true,
  isMaskClosable = true,
  showPatternDecorative = true,
}: ModalProps) => {
  const PATTERN_DECORATIVE_SIZE = "235";

  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (closable && event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleEscapeKey);
    return () => {
      window.removeEventListener("keydown", handleEscapeKey);
    };
  }, []);

  return (
    <>
      <div
        style={{ zIndex: Z_INDEX.MODAL }}
        className={clsx("fixed inset-0 overflow-y-auto")}
      >
        <div
          className={clsx(
            "fixed inset-0 w-full h-full",
            showMask === true && "bg-black opacity-40"
          )}
          onClick={() => {
            if (isMaskClosable) {
              onClose();
            }
          }}
        ></div>
        <div className="flex items-center justify-center h-screen">
          <div
            className={clsx(
              "relative bg-white rounded-xl shadow-xl !max-h-[90vh] !max-w-[90vw] overflow-hidden",
              className
            )}
          >
            {showPatternDecorative && (
              <Image
                src={PatternDecorativeImg}
                alt="Pattern decorative"
                width={PATTERN_DECORATIVE_SIZE}
                height={PATTERN_DECORATIVE_SIZE}
                className="absolute top-0 left-0"
              />
            )}
            {showCloseButton && closable && (
              <button
                type="button"
                aria-label="close modal"
                onClick={onClose}
                className={clsx(
                  "absolute z-20 text-gray-400 hover:text-gray-500 p-2.5",
                  closeIconClassName
                )}
              >
                <XClose className="w-6 h-6 stroke-current shrink-0" />
              </button>
            )}
            {body}
          </div>
        </div>
      </div>
    </>
  );
};

export default Modal;
