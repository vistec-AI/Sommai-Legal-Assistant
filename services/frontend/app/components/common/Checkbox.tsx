import clsx from "clsx";

import CheckIcon from "@/public/icons/check.svg";

const Checkbox = ({
  className,
  isSelected = false,
  sm = false,
  disabled = false,
}: {
  className?: string;
  isSelected: boolean;
  sm?: boolean;
  disabled?: boolean;
}) => {
  return (
    <div
      className={clsx(
        "flex-shrink-0 rounded flex justify-center items-center border border-gray-300",

        className,
        sm ? "w-4 h-4" : "w-[18px] h-[18px]",
        disabled
          ? "bg-gray-50"
          : isSelected
          ? "bg-primary-600 border-primary-600"
          : "bg-white group-hover:bg-primary-50 group-hover:border-primary-700 group-focus:ring-4 group-focus:ring-primary-shadow"
      )}
    >
      {isSelected && (
        <CheckIcon
          className={clsx(
            sm ? "w-2.5 h-2.5" : "w-3.5 h-3.5",
            disabled ? "text-gray-300" : "text-white"
          )}
        />
      )}
    </div>
  );
};

export default Checkbox;
