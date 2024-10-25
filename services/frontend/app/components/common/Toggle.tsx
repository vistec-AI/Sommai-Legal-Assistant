import React from "react";
import clsx from "clsx";

type ToggleProps = {
  isSelected: boolean;
  handleToggle: () => void;
  disabled?: boolean;
};

const Toggle = ({
  isSelected,
  handleToggle = () => {},
  disabled = false,
}: ToggleProps) => {
  return (
    <div
      tabIndex={1}
      className={clsx(
        "relative shrink-0 h-5 w-9 rounded-xl p-0.5 flex transition ease-in-out duration-300",
        isSelected
          ? "bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:ring-[#9E77ED3D]"
          : "bg-gray-200",
        disabled ? "cursor-default" : "cursor-pointer"
      )}
      onClick={(event) => {
        event.stopPropagation();
        event.preventDefault();
        if (!disabled) {
          handleToggle();
        }
      }}
    >
      <div
        className={clsx(
          "rounded-full w-4 h-4 bg-white transition shadow-sm ease-in-out duration-300 absolute",
          isSelected ? "translate-x-full" : ""
        )}
      ></div>
    </div>
  );
};

export default Toggle;
