import { useState, useRef, useEffect } from "react";
import Modal from "../common/Modal";
import TermsOfUse from "../TermsOfUse";
import PrivacyNotice from "../PrivacyNotice";

type TermsConditionPopupProps = {
  handleAgreeTermsCondition: () => void;
  onClose: () => void;
  isMaskClosable?: boolean;
};

const TermsConditionPopup = ({
  handleAgreeTermsCondition,
  onClose,
  isMaskClosable = true,
}: TermsConditionPopupProps) => {
  const CONDITIONS = {
    TERMS_OF_USE: "Terms of Use",
    PRIVACY_NOTICE: "Privacy Notice",
  };
  const [userScrollToBottom, setUserScrollToBottom] = useState<boolean>(false);
  const [currentSection, setCurrentSection] = useState<string>(
    CONDITIONS.TERMS_OF_USE
  );

  const containerRef = useRef<HTMLDivElement | null>(null);
  const termsOfUseRef = useRef<HTMLDivElement | null>(null);
  const privacyNoticeRef = useRef<HTMLDivElement | null>(null);

  // Detect manual scrolling
  const handleScroll = () => {
    if (containerRef?.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;

      const currentScroll = scrollHeight - scrollTop;
      if (privacyNoticeRef?.current) {
        const privacyNoticeHeight = privacyNoticeRef.current.clientHeight;

        if (currentScroll >= privacyNoticeHeight + 200) {
          setCurrentSection(CONDITIONS.TERMS_OF_USE);
        } else {
          setCurrentSection(CONDITIONS.PRIVACY_NOTICE);
        }
      }

      if (currentScroll <= clientHeight + 400) {
        setUserScrollToBottom(true);
      }
    }
  };

  // Listen to manual scroll
  useEffect(() => {
    const ref = containerRef.current;
    if (ref) {
      ref.addEventListener("scroll", handleScroll);
    }

    // Cleanup event listener on unmount
    return () => {
      if (ref) {
        ref.removeEventListener("scroll", handleScroll);
      }
    };
  }, []);

  return (
    <Modal
      onClose={onClose}
      isMaskClosable={isMaskClosable}
      body={
        <div className="max-h-[calc(85dvh_-_72px)] relative overflow-hidden w-[878px] max-w-[90vw] flex flex-col gap-5 p-6 justify-center">
          <div className="text-lg font-semibold text-gray-900 text-center">
            {currentSection}
          </div>
          <section
            ref={containerRef}
            className="rounded-lg border border-gray-100 overflow-auto grow p-3 flex flex-col gap-4"
          >
            <div ref={termsOfUseRef}>
              <TermsOfUse />
            </div>
            <hr />
            <div ref={privacyNoticeRef}>
              <PrivacyNotice />
            </div>
          </section>
          {/* action */}
          <button
            type="button"
            aria-label="ยอมรับ"
            className="btn-primary mt-3 mx-auto py-2.5 px-4 font-semibold rounded-lg disabled:bg-gray-100 disabled:text-gray-400 sm:w-[250px] w-full"
            disabled={!userScrollToBottom}
            onClick={() => {
              handleAgreeTermsCondition();
              onClose();
            }}
          >
            ยอมรับ
          </button>
        </div>
      }
      showPatternDecorative={false}
      showCloseButton={false}
    />
  );
};

export default TermsConditionPopup;
