"use client";

import React, { useState, useRef, useEffect, ReactNode, useMemo } from "react";
import clsx from "clsx";
import { scrollIntoView } from "seamless-scroll-polyfill";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  InferenceModelType,
  Rating,
  LawReferenceType,
  ResponseError,
} from "@/app/types";
import { EMOJI, Z_INDEX } from "@/app/constants";
import { randomNumber, wait, shuffleArray } from "@/app/utils";
import { useNotification } from "@/app/context/NotificationContext";
import { useChatbot } from "@/app/context/ChatbotContext";

import LoadingThreeDots from "../auth/LoadingThreeDots";
import Notification from "../common/Notification";
import Popover from "../common/Popover";
import CopyButton from "../common/CopyButton";
import LawReferenceSection from "../LawReferenceSection";
import Checkbox from "../common/Checkbox";

import SendIcon from "@/public/icons/send.svg";
import XCloseIcon from "@/public/icons/x-close.svg";
import ClockRefreshIcon from "@/public/icons/clock-refresh.svg";
import ArrowRightIcon from "@/public/icons/arrow-right.svg";
import StopIcon from "@/public/icons/stop.svg";
import api from "@/api";

const CHATBOT_ARENA_MAX_WIDTH = "1024px";
const CHATBOT_ARENA_MAX_HEIGHT = "472px";
export enum ResponseStatus {
  PENDING = "PENDING",
  FAILED = "FAILED",
  DONE = "DONE",
}

type ArenaType = {
  id: string;
  arena_model_responses: ArenaModelResponseType[];
  question: string;
  user_id: string;
  created_at: string;
  updated_at: string;
};

type ArenaModelResponseType = {
  id: string;
  arena_id: string;
  inference_model_id: string;
  alias: string;
  question: string;
  answer: string | null;
  created_at: string;
  updated_at: string;
  user_id: string;
  rating: string | null;
  status: string | null;
  law_references: LawReferenceType[] | null;
};

type DefaultArenaResponseType = {
  [key: string]: {
    name: string;
    response: ArenaModelResponseType | null;
    status: ResponseStatus;
  };
};

type UserAnswerOptionType = {
  shortKey: string;
  name: string;
  selectedModel: string[];
};

const QUESTION_PLACEHOLDER = "กรอกคำถามด้านล่างเพื่อเริ่มใช้แชทบอทอารีน่า";
const ALIAS_MODEL_A = "Model A";
const ALIAS_MODEL_B = "Model B";

const USER_ANSWER_OPTIONS: UserAnswerOptionType[] = [
  { shortKey: "A", name: "A ดีกว่า", selectedModel: [ALIAS_MODEL_A] },
  { shortKey: "B", name: "B ดีกว่า", selectedModel: [ALIAS_MODEL_B] },
  {
    shortKey: "=",
    name: "พอๆ กัน",
    selectedModel: [ALIAS_MODEL_A, ALIAS_MODEL_B],
  },
  { shortKey: "-", name: "ไม่ดีทั้งคู่", selectedModel: [] },
];

const DEFAULT_ARENA_RESPONSE: DefaultArenaResponseType = {
  [ALIAS_MODEL_A]: {
    name: ALIAS_MODEL_A,
    response: null,
    status: ResponseStatus.PENDING,
  },
  [ALIAS_MODEL_B]: {
    name: ALIAS_MODEL_B,
    response: null,
    status: ResponseStatus.PENDING,
  },
};

const ChatbotArenaSection = ({
  inferenceModelList,
  allInferenceModelList,
}: {
  inferenceModelList: InferenceModelType[];
  allInferenceModelList: InferenceModelType[];
}) => {
  const [arenaList, setArenaList] = useState<ArenaType[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<string>("");
  const [loadingState, setLoadingState] = useState<boolean>(false);

  const { notifications, handleAddNotification } = useNotification();

  const questionInputRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // user input text
  const [question, setQuestion] = useState("");
  // model answer
  const [arenaModelResponses, setArenaModelResponses] =
    useState<DefaultArenaResponseType>(DEFAULT_ARENA_RESPONSE);
  // user answer
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  // reveal model name
  const [revealModelName, setRevealModelName] = useState<boolean>(false);
  // emoji
  const [currentEmoji, setCurrentEmoji] = useState<string[]>([]);

  const {
    streamAbortController,
    stopResponseSSE,
    handleSetStreamAbortController,
  } = useChatbot();

  const userAnswerRef = useRef<HTMLDivElement | null>(null);
  const modelRevealRef = useRef<HTMLDivElement | null>(null);
  const bottomResultRef = useRef<HTMLDivElement | null>(null);

  const fetchArenaData = async () => {
    try {
      const res = await api.arena.getArenaList();
      const arena = await res.json();
      setArenaList(arena);
    } catch (err) {
      if (err instanceof ResponseError) {
      }
    }
  };

  useEffect(() => {
    const initialData = async () => {
      await fetchArenaData();
    };
    initialData();
  }, []);

  useEffect(() => {
    if (questionInputRef.current) {
      questionInputRef.current.style.height = "auto";
      questionInputRef.current.style.height = `${questionInputRef.current.scrollHeight}px`;
    }
  }, [question]);

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(event.target.value);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey && !loadingState) {
      event.preventDefault();
      sendQuestion();
    }
  };

  const handleResetQuestion = () => {
    setRevealModelName(false);
    setSelectedAnswer("");
    setLoadingState(false);
    setArenaModelResponses(DEFAULT_ARENA_RESPONSE);
  };

  const handleAskQuestion = async (
    question: string,
    inferenceModelID: string,
    arenaID: string,
    alias: string
  ) => {
    if (inferenceModelID) {
      try {
        const questionForm = {
          question: question,
          inference_model_id: inferenceModelID,
          arena_id: arenaID,
          alias: alias,
        };
        const response =
          await api.arenaModelResponse.askQuestionByInferenceModelID(
            questionForm,
            { signal: streamAbortController.signal }
          );
        const data = await response.json();
        return data;
      } catch (error) {
        console.error(error);
        return null;
      }
    }
    return null;
  };

  const sendQuestion = async () => {
    handleResetQuestion();
    const tempQuestion = question.trim();
    if (tempQuestion && inferenceModelList.length > 0) {
      setLoadingState(true);
      setQuestion("");
      setCurrentQuestion(question);
      // loading
      try {
        // create arena
        const response = await api.arena.createArena(tempQuestion);
        const arenaInfo: ArenaType = await response.json();
        const inferenceModels = shuffleArray(inferenceModelList);
        if (arenaInfo.id) {
          const [modelAResponse, modelBResponse] = await Promise.all([
            handleAskQuestion(
              question,
              inferenceModels?.[0]?.id || "",
              arenaInfo.id,
              ALIAS_MODEL_A
            ),
            handleAskQuestion(
              question,
              inferenceModels?.[1]?.id || "",
              arenaInfo.id,
              ALIAS_MODEL_B
            ),
          ]);

          if (!modelAResponse || !modelBResponse) {
            setArenaModelResponses((prevState) => {
              const tempPrevState = JSON.parse(JSON.stringify(prevState));
              tempPrevState[ALIAS_MODEL_A].status = ResponseStatus.DONE;
              tempPrevState[ALIAS_MODEL_A].response = "";
              tempPrevState[ALIAS_MODEL_B].status = ResponseStatus.DONE;
              tempPrevState[ALIAS_MODEL_B].response = "";
              return tempPrevState;
            });
          } else {
            setArenaModelResponses((prevState) => {
              const tempPrevState = JSON.parse(JSON.stringify(prevState));
              tempPrevState[ALIAS_MODEL_A].status = ResponseStatus.DONE;
              tempPrevState[ALIAS_MODEL_A].response = modelAResponse;
              tempPrevState[ALIAS_MODEL_B].status = ResponseStatus.DONE;
              tempPrevState[ALIAS_MODEL_B].response = modelBResponse;
              return tempPrevState;
            });
          }
        } else {
          handleAddNotification({
            status: "error",
            content: `Chatbot arena unavailable.`,
          });
        }
        setLoadingState(false);
        if (modelRevealRef?.current) {
          await wait(100);
          scrollIntoView(modelRevealRef.current, {
            behavior: "smooth",
            block: "end",
            inline: "nearest",
          });
        }
        await fetchArenaData();
      } catch (error) {
        setLoadingState(false);
        if (error instanceof ResponseError) {
          handleAddNotification({
            status: "error",
            content: `Chatbot arena unavailable due to: ${error.response.status} Error`,
          });
        }
      }

      setLoadingState(false);
    }
  };

  useEffect(() => {
    setCurrentEmoji(EMOJI[randomNumber(EMOJI.length - 1)]);
  }, []);

  const modelAName: string = useMemo(() => {
    const inferenceModelID =
      arenaModelResponses?.[ALIAS_MODEL_A]?.response?.inference_model_id;
    if (inferenceModelID) {
      const inferenceModel = inferenceModelList.find(
        (model) => model.id === inferenceModelID
      );
      return inferenceModel?.name || "";
    }
    return "";
  }, [arenaModelResponses?.[ALIAS_MODEL_A]?.response, inferenceModelList]);
  const modelBName: string = useMemo(() => {
    const inferenceModelID =
      arenaModelResponses?.[ALIAS_MODEL_B]?.response?.inference_model_id;
    if (inferenceModelID) {
      const inferenceModel = inferenceModelList.find(
        (model) => model.id === inferenceModelID
      );
      return inferenceModel?.name || "";
    }
    return "";
  }, [arenaModelResponses?.[ALIAS_MODEL_B]?.response, inferenceModelList]);

  const scrollToBottom = () => {
    if (containerRef?.current !== null) {
      containerRef.current.scrollTop = containerRef.current?.scrollHeight;
    }
  };

  const handleSetSelectedAnswer = async (
    selectedOption: UserAnswerOptionType
  ) => {
    setSelectedAnswer(selectedOption.name);
    if (userAnswerRef.current) {
      await wait(100);
      scrollIntoView(userAnswerRef.current, {
        behavior: "smooth",
        block: "start",
        inline: "nearest",
      });
    }
    try {
      for (const modelKey of Object.keys(arenaModelResponses)) {
        const modelResponse = arenaModelResponses?.[modelKey]?.response;
        if (selectedOption.selectedModel.includes(modelKey)) {
          // update like
          if (modelResponse) {
            await api.arenaModelResponse.likeArenaModelResponse(
              modelResponse.id
            );
          }
        } else {
          // update dislike
          if (modelResponse) {
            await api.arenaModelResponse.dislikeArenaModelResponse(
              modelResponse.id
            );
          }
        }
      }
      await fetchArenaData();
    } catch (error) {
      console.error(error);
      if (error instanceof ResponseError) {
        handleAddNotification({
          status: "error",
          content: `Cannot send feedback due to: ${error.response.status} Error`,
        });
      }
    }
  };

  useEffect(() => {
    return () => {
      stopResponseSSE();
    };
  }, []);

  return (
    <>
      <section className="relative grow pb-2 flex flex-col justify-between overflow-hidden">
        <Notification
          notificationList={notifications}
          style={{ maxWidth: CHATBOT_ARENA_MAX_WIDTH }}
          containerClassName={`bottom-28 w-full mx-auto`}
        />
        {/* result */}
        <div
          ref={containerRef}
          className="flex flex-col items-center grow overflow-auto md:px-8 px-6"
        >
          <div
            style={{ maxWidth: CHATBOT_ARENA_MAX_WIDTH }}
            className="flex flex-col gap-2 text-center pt-8 relative w-full px-12 mb-6"
          >
            {arenaList && arenaList.length > 0 && (
              <div className="absolute right-0">
                <HistoryPopup
                  arenaHistory={arenaList}
                  inferenceModelList={allInferenceModelList}
                />
              </div>
            )}
            <p className="text-gray-600 text-sm">
              หาคำตอบที่โดนใจคุณด้วยการเปรียบเทียบคำตอบระหว่าง 2 โมเดล
            </p>
            <div className="bg-clip-text text-transparent bg-gradient-primary mx-auto font-semibold text-3xl leading-[38px]">
              แชทบอทอารีน่า
            </div>
          </div>
          {/* body */}
          <section
            className="flex flex-col gap-8 w-full"
            style={{ maxWidth: CHATBOT_ARENA_MAX_WIDTH }}
          >
            {/* question */}
            <div className="flex items-start justify-between gap-3 border border-primary-300 w-full p-4 rounded-xl text-base bg-primary-50 text-primary-700">
              <p>{currentQuestion || QUESTION_PLACEHOLDER}</p>
              {currentQuestion && !loadingState && (
                <button
                  type="button"
                  aria-label="Clear question"
                  className="bg-white hover:bg-gray-50 text-gray-400 hover:text-gray-500 border border-gray-300 rounded-md p-1"
                  onClick={() => {
                    setCurrentQuestion("");
                    handleResetQuestion();
                  }}
                >
                  <XCloseIcon className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            {/* arena */}
            <div className={clsx("flex flex-col gap-4")}>
              <div className="flex items-start lg:gap-8 sm:gap-4 gap-2">
                {Object.values(arenaModelResponses).map((modelAlias, index) => {
                  return (
                    <ModelAnswerCard
                      key={`${modelAlias.name}-${index}`}
                      modelNameElement={
                        <div className="!font-inter flex items-center justify-center gap-1 rounded-2xl py-0.5 px-2 bg-blue-50 border border-blue-200 text-xs leading-[18px] font-medium text-blue-700">
                          {currentEmoji?.[index]} {modelAlias.name}
                        </div>
                      }
                      answer={
                        modelAlias?.response
                          ? modelAlias.response.answer || ""
                          : ""
                      }
                      lawReferences={modelAlias?.response?.law_references}
                      status={modelAlias.status}
                      loadingState={loadingState}
                    />
                  );
                })}
              </div>
              {/* options */}
              <div
                ref={userAnswerRef}
                className="grid md:grid-cols-4 grid-cols-2 border border-gray-300 rounded-lg overflow-hidden"
              >
                {USER_ANSWER_OPTIONS.map((option, index) => {
                  return (
                    <button
                      key={index}
                      type="button"
                      aria-label={option.name}
                      className={clsx(
                        "group flex items-center gap-2 justify-center py-2 px-4 hover:bg-gray-50 disabled:cursor-default last:md:border-r-0 md:border-r odd:border-r border-gray-300",
                        selectedAnswer === option.name
                          ? "bg-gray-50"
                          : "bg-white disabled:hover:bg-white",
                        index < USER_ANSWER_OPTIONS.length - 2 &&
                          "md:border-b-0 border-b"
                      )}
                      onClick={() => handleSetSelectedAnswer(option)}
                      disabled={
                        selectedAnswer !== "" ||
                        !currentQuestion ||
                        loadingState
                      }
                    >
                      <div
                        className={clsx(
                          "border border-gray-300 rounded-md h-6 flex items-center justify-center px-2 text-xs leading-[18px] text-gray-700 font-medium",
                          selectedAnswer === "" &&
                            "group-disabled:text-gray-400"
                        )}
                      >
                        {option.shortKey}
                      </div>
                      <span
                        className={clsx(
                          "text-gray-800 text-sm font-semibold",
                          selectedAnswer === "" &&
                            "group-disabled:text-gray-400"
                        )}
                      >
                        {option.name}
                      </span>
                    </button>
                  );
                })}
              </div>
              <div
                ref={modelRevealRef}
                className="flex flex-col items-center gap-4"
              >
                {currentQuestion &&
                !loadingState &&
                modelAName &&
                modelBName ? (
                  <>
                    <button
                      type="button"
                      className="btn-secondary-sm"
                      onClick={async () => {
                        setRevealModelName(!revealModelName);
                        await wait(200);
                        scrollToBottom();
                      }}
                    >
                      ดูเฉลยโมเดล
                    </button>
                    <div
                      ref={bottomResultRef}
                      className={clsx(
                        "font-bold transition-all",
                        revealModelName
                          ? "opacity-100 h-6 duration-500"
                          : "opacity-0 h-0 duration-200"
                      )}
                    >
                      <div className="animate-text-fill mix-blend-multiply bg-clip-text text-transparent bg-gradient-primary">
                        A = {modelAName} | B = {modelBName}
                      </div>
                    </div>
                  </>
                ) : (
                  <></>
                )}
              </div>
            </div>
          </section>
        </div>
        {selectedAnswer && (
          <div
            style={{ maxWidth: CHATBOT_ARENA_MAX_WIDTH }}
            className="mx-auto py-8 w-full text-success-600 text-xs relative"
          >
            <div className="text-center px-1 bg-white absolute left-1/2 -translate-y-1/2 top-1/2 -translate-x-1/2 ">
              ส่งคำตอบของคุณเรียบร้อย!
            </div>
            <div className="h-px bg-gray-300 w-full"></div>
          </div>
        )}
        {/* chat input */}
        <section
          style={{ maxWidth: CHATBOT_ARENA_MAX_WIDTH }}
          className="flex flex-col gap-1 lg:px-0 md:px-8 px-6 mx-auto w-full relative"
        >
          {/* stop button */}
          {/* {loadingState && (
            <button
              style={{ zIndex: Z_INDEX.STOP_BUTTON }}
              className="absolute right-0 bottom-20 bg-primary-100 p-2 rounded-full opacity-60 hover:opacity-80"
              onClick={stopResponseSSE}
            >
              <StopIcon className="w-4 h-4 fill-primary-700" />
            </button>
          )} */}
          {/* typing chat */}
          <div className="relative flex h-fit grow ml-[-1px] text-gray-900 rounded-lg overflow-hidden">
            {/* question input */}
            <textarea
              ref={questionInputRef}
              value={question}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder="พิมพ์ข้อความที่นี่..."
              className="box-border flex text-md min-h-11 text-gray-900 rounded-l-lg border border-gray-300 shadow-xs outline-none rounded-r-lg w-full py-2.5 pl-3.5 pr-12"
              style={{ height: "44px" }}
              disabled={loadingState}
            />
            <button
              disabled={!question || loadingState}
              type="button"
              aria-label="ส่งคำถาม"
              className="absolute h-full w-11 shrink-0 rounded-r-lg right-0 top-0 btn-primary flex items-center justify-center"
              onClick={sendQuestion}
            >
              <SendIcon className="w-5 h-5" />
            </button>
          </div>
          <p className="!font-inter text-center text-gray-400 sm:text-xs text-[9px] sm:leading-[18px]">
            Single-turn Chatbot | Powered by: VISTEC and VISAI.ai
          </p>
          <p className="text-center text-gray-400 text-[9px] sm:text-xs leading-[10px]">
            ข้อจำกัดความรับผิดชอบ: แชทบอทนี้ให้ข้อมูลกฎหมายเบื้องต้นเท่านั้น
            ไม่สามารถทดแทนคำปรึกษาจากผู้เชี่ยวชาญด้านกฎหมายได้
            ควรปรึกษาผู้เชี่ยวชาญด้านกฎหมาย เพื่อคำแนะนำที่เหมาะสมกับกรณีของท่าน
          </p>
        </section>
      </section>
    </>
  );
};

const ModelAnswerCard = ({
  modelNameElement,
  answer,
  status,
  lawReferences,
  loadingState,
}: {
  modelNameElement: ReactNode;
  answer: string;
  status: ResponseStatus;
  lawReferences?: LawReferenceType[] | null;
  loadingState: boolean;
}) => {
  const heightScoreLawReference: LawReferenceType | null = useMemo(() => {
    return lawReferences && Array.isArray(lawReferences)
      ? lawReferences.reduce((maxLawReferences, lawReference) =>
          maxLawReferences.score > lawReference.score
            ? maxLawReferences
            : lawReference
        )
      : null;
  }, [lawReferences]);

  return (
    <div className="h-full grow basis-0 shrink-0 flex flex-col items-start gap-1 relative pt-2 pb-10 bg-white border border-gray-200 rounded-xl">
      {/* model name */}
      <div className="px-4">{modelNameElement}</div>
      <div className="overflow-auto flex px-4 min-h-56 2xl:h-80 xl:h-54 h-52">
        {loadingState ? (
          <div className="pt-5">
            <LoadingThreeDots />
          </div>
        ) : (
          <>
            {status === ResponseStatus.FAILED ? (
              <p className="text-error-400 text-base">Failed</p>
            ) : (
              <>
                {status === ResponseStatus.DONE ? (
                  <>
                    <Markdown
                      remarkPlugins={[remarkGfm]}
                      className={clsx(
                        "text-base whitespace-pre-line answer-section",
                        answer ? "text-gray-600" : "text-gray-400"
                      )}
                    >
                      {answer || "No result."}
                    </Markdown>
                  </>
                ) : (
                  <></>
                )}
              </>
            )}
          </>
        )}
      </div>
      {heightScoreLawReference && !loadingState && (
        <div className="px-4 w-full flex flex-col gap-1">
          <hr className="w-full border-gray-200" />
          <LawReferenceSection
            lawName={heightScoreLawReference.law_name}
            lawRefs={[heightScoreLawReference]}
          />
        </div>
      )}
      {!loadingState ? (
        <>
          <div className={clsx("absolute left-4 bottom-2")}>
            <CopyButton text={answer} />
          </div>
        </>
      ) : (
        <></>
      )}
    </div>
  );
};

type HistoryModelResponseType = {
  modelName: string;
} & ArenaModelResponseType;

const HistoryPopup = ({
  arenaHistory,
  inferenceModelList,
}: {
  arenaHistory: ArenaType[];
  inferenceModelList: InferenceModelType[];
}) => {
  const TITLE_HEIGHT = 58;
  const HISTORY_ITEM_HEIGHT = 52;
  const HEIGHT_DISPLAYED_CHAT_ARENA_HISTORY = "458px";

  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [selectedPreviewHistory, setSelectedPreviewHistory] =
    useState<ArenaType | null>(null);

  const arenaResponseRef = useRef<HTMLDivElement | null>(null);

  const handleShowHistoryPopup = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
    event.stopPropagation();
    setShowHistory(!showHistory);
  };

  useEffect(() => {
    if (!showHistory) {
      setSelectedPreviewHistory(null);
    }
  }, [showHistory]);

  const userSelectedChoice = useMemo(() => {
    if (selectedPreviewHistory) {
      const likedModels = selectedPreviewHistory.arena_model_responses.filter(
        (modelResponse) => modelResponse.rating === Rating.LIKE
      );
      const dislikedModels =
        selectedPreviewHistory.arena_model_responses.filter(
          (modelResponse) => modelResponse.rating === Rating.DISLIKE
        );
      if (likedModels.length === 0 && dislikedModels.length === 0) {
        return "";
      }
      if (
        likedModels.length ===
        selectedPreviewHistory.arena_model_responses.length
      ) {
        return `พอๆ กัน`;
      }
      if (
        dislikedModels.length ===
        selectedPreviewHistory.arena_model_responses.length
      ) {
        return `ไม่ดีทั้งคู่`;
      }
      if (likedModels.length > 0) {
        const liked = likedModels
          .map((m) => m?.alias?.replaceAll("Model ", ""))
          .join(", ");

        return `${liked} ดีกว่า`;
      }
      return "";
    }
  }, [selectedPreviewHistory?.arena_model_responses]);

  const sortedArenaResponses: ArenaModelResponseType[] = useMemo(() => {
    const arenaModelResponses = selectedPreviewHistory?.arena_model_responses;
    if (arenaModelResponses) {
      return [...arenaModelResponses].sort((a, b) =>
        b.alias > a.alias ? -1 : 1
      );
    }
    return [];
  }, [selectedPreviewHistory?.arena_model_responses]);

  return (
    <>
      <Popover
        isOpen={showHistory}
        handleSetIsOpen={(state) => setShowHistory(state)}
        className="flex justify-center"
        position="bottom-right"
        contentClassName="mt-1.5"
        content={
          <div
            style={{
              width: CHATBOT_ARENA_MAX_WIDTH,
              height:
                arenaHistory.length >= 4
                  ? selectedPreviewHistory
                    ? HEIGHT_DISPLAYED_CHAT_ARENA_HISTORY
                    : CHATBOT_ARENA_MAX_HEIGHT
                  : selectedPreviewHistory
                  ? HEIGHT_DISPLAYED_CHAT_ARENA_HISTORY
                  : `${
                      TITLE_HEIGHT + HISTORY_ITEM_HEIGHT * arenaHistory.length
                    }px`,
            }}
            className="md:max-w-[70dvw] max-w-[calc(100dvw_-_40px)] max-h-[calc(100dvh_-_300px)] transition-all overflow-hidden text-left py-3 flex flex-col gap-2 text-base bg-white border border-gray-200 rounded-lg shadow-lg"
          >
            {selectedPreviewHistory ? (
              <div className="flex flex-col gap-1 overflow-hidden px-3 grow">
                <button
                  type="button"
                  aria-label="กลับ"
                  className="w-fit flex items-center shrink-0 gap-1.5 text-sm text-primary-700 hover:text-primary-800"
                  onClick={() => setSelectedPreviewHistory(null)}
                >
                  <ArrowRightIcon className="w-5 h-5 rotate-180" />
                  <span className="font-semibold">กลับ</span>
                </button>
                <header className="text-base text-gray-700 font-semibold">
                  {selectedPreviewHistory?.question}
                </header>
                <div className="py-4 flex flex-col gap-2 grow overflow-auto">
                  {/* user selected answer */}
                  <div className="flex flex-wrap gap-1 items-center">
                    {USER_ANSWER_OPTIONS.map((option, index) => {
                      return (
                        <div
                          key={index}
                          className={clsx(
                            "py-[3px] px-2 flex items-center gap-1.5 rounded-md border border-gray-300"
                          )}
                        >
                          <Checkbox
                            isSelected={option.name === userSelectedChoice}
                            disabled={true}
                            sm={true}
                          />

                          <span className="text-xs text-gray-700">
                            {option.name}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  {/* answer from model */}
                  <div
                    ref={arenaResponseRef}
                    className="grid grid-cols-2 items-start gap-2 overflow-hidden grow"
                  >
                    {sortedArenaResponses?.map(
                      (
                        modelResponse: ArenaModelResponseType,
                        index: number
                      ) => {
                        const model = inferenceModelList.find(
                          (model) =>
                            model.id === modelResponse.inference_model_id
                        );
                        return (
                          <HistoryCard
                            key={index}
                            alias={modelResponse.alias}
                            answer={modelResponse.answer || ""}
                            modelName={model?.name || ""}
                          />
                        );
                      }
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <>
                <header className="text-base text-gray-700 font-semibold px-3">
                  ประวัติการใช้งาน
                </header>
                {arenaHistory.length > 0 ? (
                  <>
                    <div className="flex flex-col gap-1 grow overflow-auto px-3">
                      {arenaHistory.map((history: ArenaType, index: number) => {
                        return (
                          <div
                            key={index}
                            className="py-4 flex items-start justify-between gap-2 last:border-0 border-b border-gray-200"
                          >
                            <div className="grow truncate text-gray-700 text-sm font-semibold">
                              {history.question}
                            </div>
                            <button
                              type="button"
                              aria-label="ดูข้อมูลเพิ่มเติม"
                              className="flex items-center shrink-0 gap-1.5 text-sm text-primary-700 hover:text-primary-800"
                              onClick={(
                                event: React.MouseEvent<HTMLButtonElement>
                              ) => {
                                event.preventDefault();
                                event.stopPropagation();
                                setSelectedPreviewHistory(history);
                              }}
                            >
                              <span className="font-semibold">
                                ดูข้อมูลเพิ่มเติม
                              </span>
                              <ArrowRightIcon className="w-5 h-5" />
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </>
                ) : (
                  <p className="text-center text-sm text-gray-600 py-7 px-6">
                    ยังไม่มีประวัติการใช้งานแชทบอทอารีน่า
                  </p>
                )}
              </>
            )}
          </div>
        }
      >
        <button
          type="button"
          aria-label="History"
          className="btn-secondary rounded-lg p-2 transition-all animate-fade-in"
          onClick={handleShowHistoryPopup}
        >
          <ClockRefreshIcon className="w-5 h-5" />
        </button>
      </Popover>
    </>
  );
};

const HistoryCard = ({
  alias,
  answer,
  modelName,
}: {
  alias: string;
  answer: string;
  modelName: string;
}) => {
  const [showModelName, setShowModelName] = useState(false);
  return (
    <div className="grow basis-0 h-full items-start overflow-hidden border border-gray-200 flex flex-col rounded-lg pt-2">
      <button
        type="button"
        aria-label={alias}
        className="!font-inter break-words p-2 mx-2 flex items-center justify-center gap-1 rounded-2xl py-0.5 bg-blue-50 hover:bg-blue-100 disabled:hover:bg-blue-50 border border-blue-200 text-xs leading-[18px] font-medium text-blue-700"
        onClick={() => setShowModelName(!showModelName)}
        disabled={modelName === ""}
      >
        {showModelName && modelName !== "" ? modelName : alias}
      </button>
      <div className="grow overflow-auto custom-word-break break-words px-2 pt-1 pb-2">
        {answer ? (
          <Markdown
            remarkPlugins={[remarkGfm]}
            className="text-gray-600 answer-section whitespace-pre-line"
          >
            {answer}
          </Markdown>
        ) : (
          <p className="text-gray-400">No result.</p>
        )}
      </div>
    </div>
  );
};

export default ChatbotArenaSection;
