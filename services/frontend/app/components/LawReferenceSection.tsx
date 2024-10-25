"use client";

import { useState, useRef, useEffect } from "react";
import { LawReferenceType } from "@/app/types";
import clsx from "clsx";

import LinkExternalIcon from "@/public/icons/link-external.svg";
import ChevronDownIcon from "@/public/icons/chevron-down.svg";
import { scrollIntoView } from "seamless-scroll-polyfill";

const LawReferenceSection = ({
  lawName,
  lawRefs,
}: {
  lawName: string;
  lawRefs: LawReferenceType[];
}) => {
  const [showRefDetail, setShowRefDetail] = useState(false);
  const firstRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (showRefDetail) {
      if (firstRef.current) {
        scrollIntoView(firstRef.current, {
          behavior: "smooth",
          block: "center",
          inline: "nearest",
        });
      }
    }
  }, [showRefDetail]);

  return (
    <section className="flex flex-col items-start">
      {/* header */}
      <button
        type="button"
        aria-label="Show/hide law reference"
        className="flex items-start gap-1 group w-full"
        onClick={() => {
          setShowRefDetail(!showRefDetail);
        }}
      >
        <div className="text-gray-900 text-lg text-left grow">{lawName}</div>
        <ChevronDownIcon
          className={clsx(
            "shrink-0 w-6 h-6 text-gray-400 group-hover:text-gray-500 transition-transform duration-300",
            showRefDetail && "rotate-180"
          )}
        />
      </button>
      <div
        className={clsx(
          "flex flex-col gap-4 transition-all",
          showRefDetail
            ? "scale-y-100 origin-top opacity-100 ease-out duration-[400ms] mt-2"
            : "scale-y-0 h-0 origin-top invisible opacity-0 ease-in duration-100"
        )}
      >
        {lawRefs.map((lawRef: LawReferenceType, index: number) => {
          return (
            <div
              ref={index === 0 ? firstRef : null}
              key={index}
              className="flex flex-col gap-2"
            >
              <p
                className={clsx(
                  "text-gray-600 text-base",
                  showRefDetail ? "opacity-100 ease-out" : "opacity-0 ease-in"
                )}
              >
                {lawRef.text}
              </p>
              <a
                href={lawRef.url}
                target="_blank"
                className={clsx(
                  "flex items-center gap-1.5 text-primary-700 hover:text-primary-800 font-semibold text-sm",
                  showRefDetail ? "opacity-100 ease-out" : "opacity-0 ease-in"
                )}
              >
                <span>ดูข้อมูลเพิ่มเติม</span>
                <LinkExternalIcon className="w-5 h-5" />
              </a>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default LawReferenceSection;
