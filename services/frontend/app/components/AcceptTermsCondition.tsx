import { useState, useEffect } from "react";
import TermsConditionPopup from "./auth/TermsConditionPopup";

import Checkbox from "./common/Checkbox";

type AcceptTermsConditionProps = {
  isAcceptedTermsCondition: boolean;
  handleIsAcceptedTermsCondition: (state: boolean) => void;
};

const AcceptTermsCondition = ({
  isAcceptedTermsCondition,
  handleIsAcceptedTermsCondition,
}: AcceptTermsConditionProps) => {
  // Terms of use and privacy notice
  const [alreadyAcceptTermsCondition, setAlreadyAcceptTermsCondition] =
    useState<boolean>(true);
  const [showTermsConditionPopup, setShowTermsConditionPopup] =
    useState<boolean>(false);
  const [alreadyShowTermsConditionPopup, setAlreadyShowTermsConditionPopup] =
    useState<boolean>(false);

  // useEffect(() => {
  //   const termsHistory = getAcceptTermsHistory();
  //   setAlreadyAcceptTermsCondition(termsHistory);
  //   handleIsAcceptedTermsCondition(termsHistory);
  // }, []);

  const handleShowTermsConditionPopup = () => {
    setShowTermsConditionPopup(true);
  };

  const handleCloseTermsConditionPopup = () => {
    setShowTermsConditionPopup(false);
  };

  return (
    <>
      {showTermsConditionPopup && (
        <TermsConditionPopup
          handleAgreeTermsCondition={() => {
            handleIsAcceptedTermsCondition(true);
            setAlreadyShowTermsConditionPopup(true);
          }}
          onClose={handleCloseTermsConditionPopup}
        />
      )}

      <button
        type="button"
        aria-label="ฉันยอมรับเงื่อนไขการใช้งานและนโยบายความเป็นส่วนตัว"
        className="flex items-start group gap-2"
        onClick={() => {
          if (!isAcceptedTermsCondition && !alreadyShowTermsConditionPopup) {
            handleShowTermsConditionPopup();
            return;
          }
          handleIsAcceptedTermsCondition(!isAcceptedTermsCondition);
        }}
      >
        <Checkbox
          isSelected={isAcceptedTermsCondition}
          sm={true}
          className="mt-0.5"
        />
        <span className="text-sm text-gray-700 font-medium text-left">
          ฉันยอมรับเงื่อนไขการใช้งานและนโยบายความเป็นส่วนตัว
        </span>
      </button>
    </>
  );
};

export default AcceptTermsCondition;
