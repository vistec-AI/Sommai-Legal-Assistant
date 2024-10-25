"use client";

import { useState, useMemo, useEffect } from "react";
import { MIN_PASSWORD_CHARACTERS } from "@/app/constants";
import { InputProps } from "@/app/types";

import clsx from "clsx";
import {
  validateContainLowerCase,
  validateContainNumber,
  validateContainUpperCase,
} from "@/app/utils/validator";

import Input from "./Input";
import EyeIcon from "@/public/icons/eye.svg";
import EyeOffIcon from "@/public/icons/eye-off.svg";
import CheckCircleIcon from "@/public/icons/check-circle.svg";

type PasswordInput = {
  showValidation?: boolean;
  handleSetValidPassword?: (isValid: boolean) => void;
} & InputProps;

const PasswordInput = ({
  showValidation = false,
  handleSetValidPassword,
  ...rest
}: PasswordInput) => {
  const [isVisibleText, setIsVisibleText] = useState(false);

  const { value: password }: any = { ...rest };

  const isPasswordContainLowerCase = useMemo(
    () => validateContainLowerCase(password),
    [password]
  );
  const isPasswordContainUpperCase = useMemo(
    () => validateContainUpperCase(password),
    [password]
  );
  const isPasswordContainNumber = useMemo(
    () => validateContainNumber(password),
    [password]
  );
  const isPasswordPassMinimumCharacter = useMemo(
    () => password.length >= MIN_PASSWORD_CHARACTERS,
    [password]
  );

  useEffect(() => {
    if (showValidation && handleSetValidPassword) {
      handleSetValidPassword(
        isPasswordContainLowerCase &&
          isPasswordContainUpperCase &&
          isPasswordContainNumber &&
          isPasswordPassMinimumCharacter
      );
    }
  }, [showValidation, password]);

  return (
    <>
      {/* @ts-ignore */}
      <Input
        type={isVisibleText ? "text" : "password"}
        suffix={
          <>
            <button
              onClick={() => setIsVisibleText(!isVisibleText)}
              type="button"
              aria-label="Toggle password"
              className="pr-3.5"
            >
              {isVisibleText ? (
                <EyeOffIcon className="self-center cursor-pointer text-gray-400 w-4 h-4" />
              ) : (
                <EyeIcon className="self-center cursor-pointer text-gray-400 w-4 h-4" />
              )}
            </button>
          </>
        }
        {...rest}
      />
      {showValidation && (
        <div
          className={clsx("flex flex-col gap-1", password ? "flex" : "hidden")}
        >
          <ValidateCondition
            passCondition={isPasswordContainLowerCase}
            condition={`At least 1 lowercase character`}
          />
          <ValidateCondition
            passCondition={isPasswordContainUpperCase}
            condition={`At least 1 uppercase character`}
          />
          <ValidateCondition
            passCondition={isPasswordContainNumber}
            condition={`At least 1 number`}
          />
          <ValidateCondition
            passCondition={isPasswordPassMinimumCharacter}
            condition={`${MIN_PASSWORD_CHARACTERS} characters long`}
          />
        </div>
      )}
    </>
  );
};

type ValidateConditionProps = {
  passCondition: boolean;
  condition: string;
};

const ValidateCondition = ({
  passCondition,
  condition,
}: ValidateConditionProps) => {
  return (
    <div className="flex items-center gap-2 text-base text-gray-600">
      <CheckCircleIcon
        className={clsx(
          "w-6 h-6",
          passCondition ? "text-success-600" : "text-gray-600"
        )}
      />
      <span>{condition}</span>
    </div>
  );
};

export default PasswordInput;
