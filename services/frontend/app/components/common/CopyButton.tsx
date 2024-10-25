"use client";

import { useNotification } from "@/app/context/NotificationContext";

import CopyIcon from "@/public/icons/copy.svg";
import clsx from "clsx";

const CopyButton = ({
  text,
  buttonText = "",
  className = "",
}: {
  text: string;
  buttonText?: string;
  className?: string;
}) => {
  const { handleAddNotification } = useNotification();

  const handleCopyToClipboard = () => {
    if (!text) return;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
    } else {
      const input = document.createElement("input");
      input.setAttribute("value", text);
      document.body.appendChild(input);
      input.select();
      document.body.removeChild(input);
    }

    handleAddNotification(
      {
        status: "info",
        content: `Copied to Clipboard`,
      },
      3000
    );
  };

  return (
    <>
      <button
        type="button"
        aria-label="Copy to clipboard"
        className={clsx(
          "p-2 rounded-lg disabled:text-gray-400 disabled:hover:text-gray-400 text-gray-600 hover:text-gray-700 flex items-center justify-center gap-1",
          className
        )}
        onClick={handleCopyToClipboard}
        disabled={!text}
      >
        {buttonText && <>{buttonText}</>}
        <CopyIcon className="w-5 h-5" />
      </button>
    </>
  );
};

export default CopyButton;
