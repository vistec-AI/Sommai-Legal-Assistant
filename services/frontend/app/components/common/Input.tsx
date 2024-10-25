import clsx from "clsx";
import { InputSize } from "@/app/types";
import React, { InputHTMLAttributes } from "react";

type InputProps = {
  type: string;
  value?: string | number | undefined;
  label?: string;
  id?: string;
  placeholder?: string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  disabled?: boolean;
  error?: string;
  inputRef?: React.RefObject<HTMLInputElement> | null;
  className?: string;
  containerClassName?: string;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  onClick?: (event: React.MouseEvent<HTMLInputElement>) => void;
  size?: InputSize;
  name?: string;
  autoComplete?: string;
  autoFocus?: boolean;
};

const Input = ({
  type,
  value,
  label,
  prefix,
  suffix,
  error,
  id,
  name,
  autoComplete,
  autoFocus,
  disabled = false,
  placeholder = "",
  inputRef = null,
  className = "",
  containerClassName = "",
  size = InputSize.SM,
  onKeyDown = () => {},
  onBlur = () => {},
  onFocus = () => {},
  onChange = () => {},
  onClick = () => {},
  ...rest
}: InputProps) => {
  return (
    <div
      className={clsx("flex flex-col gap-1.5 text-left", containerClassName)}
    >
      {label && (
        <label className="text-sm font-medium text-gray-700">{label}</label>
      )}
      <div
        className={clsx(
          "flex rounded-lg border shadow-xs focus-within:border-primary-300 focus-within:ring-4 ring-primary-shadow border-gray-300",
          className
        )}
      >
        {prefix && <>{prefix}</>}
        <input
          id={id}
          value={value}
          ref={inputRef}
          name={name}
          type={type}
          className={clsx(
            "w-full focus:outline-none rounded-lg text-base placeholder:text-gray-500 disabled:bg-gray-50 disabled:text-gray-500",
            size === InputSize.XS && "py-1 px-2.5",
            size === InputSize.SM && "py-2 px-3",
            size === InputSize.MD && "py-2.5 px-3.5",
            prefix && "!pl-2",
            suffix && "!pr-2",
            className
          )}
          placeholder={placeholder}
          disabled={disabled}
          onBlur={onBlur}
          onFocus={onFocus}
          onChange={onChange}
          onKeyDown={onKeyDown}
          onClick={onClick}
          autoComplete={autoComplete}
          autoFocus={autoFocus}
          {...rest}
        />
        {suffix && <>{suffix}</>}
      </div>
      {error && (
        <span className="text-left text-error-600 text-sm">{error}</span>
      )}
    </div>
  );
};

export default Input;
