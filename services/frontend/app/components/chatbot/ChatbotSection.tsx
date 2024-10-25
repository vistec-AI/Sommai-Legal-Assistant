"use client";

import React, {
  useMemo,
  memo,
  useState,
  useRef,
  useEffect,
  useId,
} from "react";
import Image from "next/image";

import { fetchEventSource } from "@microsoft/fetch-event-source";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import clsx from "clsx";
import sanitizeHtml from "sanitize-html";
import { v4 as uuidv4 } from "uuid";
import EventSource from "eventsource";
import JSON5 from "json5";

import { wait } from "@/app/utils";
import api from "@/api";

import { useNotification } from "@/app/context/NotificationContext";
import { useChatbot } from "@/app/context/ChatbotContext";
import LoadingThreeDots from "../auth/LoadingThreeDots";

import {
  LawReferenceType,
  ChatType,
  ChatRoomType,
  ResponseError,
  Rating,
  InferenceModelType,
  MappedLawReferenceByNameType,
} from "@/app/types";
import { scrollIntoView } from "seamless-scroll-polyfill";
import {
  getAccessToken,
  getRefreshToken,
  setUserTokens,
} from "@/app/utils/auth";
import { HTTP_200_OK } from "@/app/constants/httpResponse";

import LawReferenceSection from "../LawReferenceSection";
import Popover from "../common/Popover";
import CopyButton from "../common/CopyButton";
import Notification from "../common/Notification";
import Modal from "../common/Modal";
import Checkbox from "../common/Checkbox";

import ChevronDownIcon from "@/public/icons/chevron-down.svg";
import SendIcon from "@/public/icons/send.svg";
import UserIcon from "@/public/icons/user.svg";
import CheckIcon from "@/public/icons/check.svg";
import StopIcon from "@/public/icons/stop.svg";
import ThumbUpIcon from "@/public/icons/thumbs-up.svg";
import ThumbDownGradientIcon from "../ThumbDownGradientIcon";

import SommaiiIcon from "@/public/images/logo/sommaii-icon.webp";

type ChatbotSectionProps = {
  chatRoom: ChatRoomType;
  inferenceModelList: InferenceModelType[];
  chats: ChatType[];
  updateChatByChatRoomID?: (chatRoomID: string, newChats: ChatType[]) => void;
  className?: string;
};

const CHAT_STATUS = {
  QUEUE: "QUEUE",
  PROCESSING: "PROCESSING",
  FAILED: "FAILED",
  DONE: "DONE",
  TYPING: "TYPING",
  DONE_STREAMING: "DONE_STREAMING",
};

const Z_INDEX_STOP_BUTTON = 100;

class RetriableError extends Error {}
class FatalError extends Error {}

// chatbot
const ChatbotSection = ({
  chatRoom,
  inferenceModelList,
  chats = [],
  updateChatByChatRoomID,
  className,
}: ChatbotSectionProps) => {
  const sanitizeConfig = {
    allowedTags: ["b", "i", "a", "p"],
    allowedAttributes: { a: ["href"] },
  };
  const BACKEND_URL = process.env["NEXT_PUBLIC_BACKEND_API"];

  const { notifications, handleAddNotification } = useNotification();
  const {
    stopResponseSSE,
    streamAbortController,
    handleSetNewChatRoomNameByID,
  } = useChatbot();

  const [chatHistories, setChatHistories] = useState<ChatType[]>(chats);

  const [loadingChat, setLoadingChat] = useState<boolean>(false);
  const [selectedInferenceModel, setSelectedInferenceModel] =
    useState<InferenceModelType | null>(null);

  const newChatIDRef = useRef<string>("");
  const newCustomChatIDRef = useRef<string>("");
  const currentCustomChatIDRef = useRef<string>("");

  useEffect(() => {
    setChatHistories(chats);
  }, [chats]);

  useEffect(() => {
    if (inferenceModelList.length > 0) {
      const defaultInferenceModel = inferenceModelList.find(
        (model) => model.llm_name === "Typhoon-1.5"
      );
      setSelectedInferenceModel(defaultInferenceModel || inferenceModelList[0]);
    }
  }, [inferenceModelList]);

  useEffect(() => {
    // updateChatByChatRoomID(chatRoom.id, chatHistories);
  }, [chatHistories]);

  const resetChatID = () => {
    if (newCustomChatIDRef.current) {
      newCustomChatIDRef.current = "";
    }
    if (newChatIDRef.current) {
      newChatIDRef.current = "";
    }
  };

  const handleGetLawRefInDoneState = async (
    customID: string,
    chatID: string,
    question: string
  ) => {
    let lawReferencesData = null;
    if (chatID && selectedInferenceModel) {
      try {
        const response = await api.chats.retrieveLawRef(
          question,
          chatID,
          selectedInferenceModel?.id
        );
        const lawRefs = await response.json();
        if (lawRefs?.law_references) {
          lawReferencesData = lawRefs.law_references;
        }
      } catch (error) {
        if (error instanceof ResponseError) {
        }
      }
    }
    setChatHistories((prevState) => {
      const tempPrevState = [...prevState];
      const chatIndex = prevState.findIndex((p) => p.customID === customID);
      if (chatIndex !== -1) {
        tempPrevState[chatIndex] = {
          ...prevState[chatIndex],
          status: CHAT_STATUS.DONE_STREAMING,
          law_references: lawReferencesData,
          loadingRef: false,
        };
        return tempPrevState;
      }
      return prevState;
    });
  };

  const handleAskQuestion = async (question: string) => {
    resetChatID();

    if (selectedInferenceModel) {
      const customID = uuidv4();
      newCustomChatIDRef.current = customID;

      const now = new Date();

      const setFailedEmptyChat = () => {
        setChatHistories((prevState) => {
          const tempPrevState = [...prevState];
          const chatIndex = prevState.findIndex((p) => p.customID === customID);
          if (chatIndex !== -1) {
            tempPrevState[chatIndex] = {
              ...prevState[chatIndex],
              status: CHAT_STATUS.FAILED,
              loadingState: false,
            };
            return tempPrevState;
          }
          return prevState;
        });
      };
      const setTypingEmptyChat = () => {
        setChatHistories((prevState) => {
          const tempPrevState = [...prevState];
          const chatIndex = prevState.findIndex((p) => p.customID === customID);
          if (chatIndex !== -1) {
            tempPrevState[chatIndex] = {
              ...prevState[chatIndex],
              status: CHAT_STATUS.TYPING,
              loadingState: false,
            };
            return tempPrevState;
          }
          return prevState;
        });
      };

      try {
        const changeChatRoomNameState: boolean = chatHistories.length <= 0;
        setChatHistories((prevState) => {
          const defaultChat = {
            id: "",
            customID: customID,
            question: question,
            answer: "",
            status: CHAT_STATUS.QUEUE,
            created_at: now.toISOString(),
            updated_at: now.toISOString(),
            rating: "",
            user_id: "",
            inference_id: selectedInferenceModel?.id,
            chat_room_id: chatRoom.id,
            loadingState: true,
          };

          return [...prevState, defaultChat];
        });
        await wait(100);

        let accessToken = getAccessToken();
        let chatID: string = "";
        let index: number = 0;
        let status: number | null = null;
        let eventError: boolean = false;
        let retry: number = 0;
        let completedAnswer: string = "";
        // Refresh
        try {
          const refreshToken = getRefreshToken();
          const refreshResponse = await api.auth.refresh({
            refresh_token: refreshToken,
          });
          const refreshData = await refreshResponse?.json();
          accessToken = refreshData["access_token"];
          await setUserTokens(refreshData);
        } catch (error) {}

        // Event source stream
        await fetchEventSource(`${BACKEND_URL}/chats/question`, {
          signal: streamAbortController.signal,
          method: "POST",
          body: JSON.stringify({
            chat_room_id: chatRoom.id,
            inference_model_id: selectedInferenceModel?.id,
            question: question,
          }),
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          openWhenHidden: true,
          async onopen(response) {
            status = response.status;
            retry++;
            if (changeChatRoomNameState) {
              try {
                const response = await api.chatRooms.renameChatRoom(
                  chatRoom.id,
                  question
                );
                const newChatroom = await response?.json();
                handleSetNewChatRoomNameByID(newChatroom.id, newChatroom.name);
              } catch (error) {
                if (error instanceof ResponseError) {
                }
              }
            }
            if (response.ok) {
              return;
            } else if (
              response.status >= 400 &&
              response.status < 500 &&
              response.status !== 429
            ) {
              console.error("Client error, not retrying", response.status);
              setFailedEmptyChat();
              resetChatID();
              stopResponseSSE();
              return;
            } else {
              console.error("Server error, retrying", response.status);
              setFailedEmptyChat();
              resetChatID();
              stopResponseSSE();
            }
          },
          onmessage(msg) {
            const data = msg?.data;
            if (msg?.event === "error") {
              eventError = true;

              setFailedEmptyChat();
              resetChatID();
              stopResponseSSE();
              return;
            }
            if (data) {
              try {
                const dataJson = JSON5.parse(data);
                chatID = dataJson?.chat_id;
                newChatIDRef.current = chatID;
                const answer = dataJson?.text;
                if (index === 0 && !answer) {
                  handleSetStatusChatHistories(
                    customID,
                    dataJson?.chat_id || "",
                    answer || "",
                    CHAT_STATUS.TYPING,
                    true
                  );
                }
                handleSetStatusChatHistories(
                  customID,
                  dataJson?.chat_id || "",
                  answer || "",
                  CHAT_STATUS.TYPING,
                  false
                );
                if (answer) {
                  completedAnswer = completedAnswer + answer;
                }
              } catch (e) {
                console.error("Error parsing message data:", e);
                setTypingEmptyChat();
              }
            }

            if (msg.event === "FatalError") {
              setFailedEmptyChat();
              resetChatID();
              stopResponseSSE();
              return;
            }
          },
          async onclose() {
            stopResponseSSE();
            return;
            // throw new Error();
          },
          onerror(err) {
            console.error("Event source stream error: ", err);
            resetChatID();
            setFailedEmptyChat();
            stopResponseSSE();
            throw err;
          },
        });
        if (status === HTTP_200_OK && !eventError) {
          const noResultState = completedAnswer.includes("ไม่สามารถตอบคำถาม");
          setChatHistories((prevState) => {
            const tempPrevState = [...prevState];
            const chatIndex = prevState.findIndex(
              (p) => p.customID === customID
            );
            if (chatIndex !== -1) {
              tempPrevState[chatIndex] = {
                ...prevState[chatIndex],
                status: CHAT_STATUS.DONE,
                loadingState: false,
                loadingRef: !noResultState,
              };
              return tempPrevState;
            }
            return prevState;
          });

          if (!noResultState) {
            await handleGetLawRefInDoneState(customID, chatID, question);
          } else {
            setChatHistories((prevState) => {
              const tempPrevState = [...prevState];
              const chatIndex = prevState.findIndex(
                (p) => p.customID === customID
              );
              if (chatIndex !== -1) {
                tempPrevState[chatIndex] = {
                  ...prevState[chatIndex],
                  status: CHAT_STATUS.DONE_STREAMING,
                };
                return tempPrevState;
              }
              return prevState;
            });
          }
        }
        currentCustomChatIDRef.current = customID;

        resetChatID();
        stopResponseSSE();
      } catch (error) {
        setFailedEmptyChat();
        resetChatID();

        if (error instanceof ResponseError) {
          handleAddNotification({
            status: "error",
            content: `Cannot ask question due to: ${error.response.status} Error`,
          });
        }
        stopResponseSSE();
      }
    } else {
      handleAddNotification({
        status: "error",
        content: `Cannot ask question due to: No inference model available`,
      });
    }
  };

  const handleSetStatusChatHistories = (
    customID: string,
    id: string,
    answer: string,
    status: string,
    loadingState: boolean
  ) => {
    setChatHistories((prevState) => {
      const tempPrevState = [...prevState];
      const chatIndex = prevState.findIndex((p) => p.customID === customID);

      if (chatIndex !== -1) {
        tempPrevState[chatIndex] = {
          ...prevState[chatIndex],
          loadingState: loadingState,
          answer: prevState[chatIndex].answer + answer,
          status: status,
          id: id,
        };
        return tempPrevState;
      }
      return prevState;
    });
  };

  const handleSetSelectedInferenceModel = (
    inferenceModel: InferenceModelType
  ) => {
    setSelectedInferenceModel(inferenceModel);
  };

  useEffect(() => {
    return () => {
      stopResponseSSE();
    };
  }, []);

  return (
    <>
      <section
        className={clsx(
          "relative flex flex-col justify-between pb-2 grow overflow-hidden",
          className
        )}
      >
        <Notification
          notificationList={notifications || []}
          containerClassName="bottom-28 w-full mx-auto w-full md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem]"
        />
        {/* chat history */}
        <ChatHistorySection
          loadingChat={loadingChat}
          chatRoomID={chatRoom?.id}
          chatHistories={chatHistories}
          handleAskQuestion={handleAskQuestion}
          newCustomChatID={newCustomChatIDRef.current}
        />
        {/* question typing */}
        <UserQuestionInputSection
          selectedInferenceModel={selectedInferenceModel}
          inferenceModelList={inferenceModelList}
          handleAskQuestion={handleAskQuestion}
          handleSetSelectedInferenceModel={handleSetSelectedInferenceModel}
          showStopChat={newCustomChatIDRef.current !== ""}
          handleStopChat={stopResponseSSE}
        />
      </section>
    </>
  );
};

type ChatHistorySectionProps = {
  loadingChat: boolean;
  chatHistories: ChatType[];
  chatRoomID: string;
  handleAskQuestion: (question: string) => void;
  newCustomChatID: string;
};

type DefaultLawQuestion = {
  question: string;
  lawType: string;
};

const ChatHistorySection = ({
  loadingChat,
  chatHistories,
  chatRoomID,
  handleAskQuestion,
  newCustomChatID,
}: ChatHistorySectionProps) => {
  const DEFAULT_LAW_QUESTIONS: DefaultLawQuestion[] = [
    {
      question: "การจัดซื้อจัดจ้างพัสดุของภาครัฐทำวิธีไหนได้บ้าง",
      lawType: "กฎหมายการจัดซื้อจัดจ้างและการบริหารพัสดุภาครัฐ",
    },
    {
      question: "ใครไม่ต้องเสียภาษีธุรกิจเฉพาะ",
      lawType: "กฎหมายภาษี",
    },
    {
      question: "คนต่างด้าวประเภทใดห้ามประกอบธุรกิจในไทย",
      lawType: "กฎหมายการประกอบธุรกิจของคนต่างด้าว",
    },
    {
      question: "ขอวิธีจดทะเบียนพาณิชย์",
      lawType: "กฎหมายทะเบียนพาณิชย์",
    },
    {
      question: "การดำเนินการใดที่ต้องแจ้งธนาคารแห่งประเทศไทย",
      lawType: "กฎหมายธุรกิจสถาบันการเงิน",
    },
    {
      question: "ความผิดของพนักงานในหน่วยงานรัฐมีอะไรบ้าง",
      lawType: "กฎหมายว่าด้วยความผิดของพนักงานในองค์การหรือหน่วยงานของรัฐ",
    },
  ];
  const [loadingElement, setLoadingElement] = useState<boolean>(true);
  const [isUserScrolling, setIsUserScrolling] = useState<boolean>(false);

  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (containerRef?.current !== null && !isUserScrolling) {
      containerRef.current.scrollTop = containerRef.current?.scrollHeight;
    }
  };

  // Scroll to bottom in new question state
  useEffect(() => {
    if (newCustomChatID) {
      if (containerRef?.current !== null) {
        containerRef.current.scrollTop = containerRef.current?.scrollHeight;
      }
    }
  }, [newCustomChatID]);

  // Detect manual scrolling
  const handleScroll = () => {
    if (containerRef?.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;

      if (scrollHeight - scrollTop <= clientHeight + 10) {
        setIsUserScrolling(false);
      } else {
        setIsUserScrolling(true);
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

  useEffect(() => {
    const delayScroll = async () => {
      if (!loadingChat) {
        scrollToBottom();
        await wait(50);
        setLoadingElement(false);
      }
    };

    delayScroll();
  }, []);

  if (loadingChat) {
    return (
      <section className="relative grow overflow-auto pt-8 flex flex-col gap-4 items-center"></section>
    );
  }
  if (chatHistories.length <= 0) {
    // empty state
    return (
      <section className="relative grow overflow-auto lg:px-0 md:px-8 px-6 pt-8 pb-4 flex flex-col gap-4 items-center">
        <div className="flex flex-col gap-2 text-center">
          <p className="text-gray-600 text-sm">
            ถามคำถาม-หาคำตอบทางกฏหมายที่คุณต้องการได้ที่โหมดแชทบอท
          </p>
          <div className="bg-clip-text text-transparent bg-gradient-primary mx-auto font-semibold text-3xl leading-[38px]">
            คุณมีอะไรให้เราช่วยเหลือ?
          </div>
        </div>
        {/* default questions */}
        <div className="flex flex-wrap items-center justify-center">
          {/* civil law */}
          <div className="grid sm:grid-cols-2 grid-cols-1 gap-y-2 lg:gap-x-8 gap-x-4">
            {DEFAULT_LAW_QUESTIONS.map((defaultLaw, index) => {
              return (
                <DefaultQuestionCard
                  key={index}
                  lawType={defaultLaw.lawType}
                  question={defaultLaw.question}
                  onClick={() => handleAskQuestion(defaultLaw.question)}
                />
              );
            })}
          </div>
        </div>
      </section>
    );
  }
  return (
    <>
      <section
        id={chatRoomID}
        ref={containerRef}
        className={clsx(
          "grow overflow-auto md:px-8 px-6 md:pb-8 pb-6 transition-opacity duration-150",
          loadingElement ? "opacity-0" : "opacity-100"
        )}
      >
        {chatHistories.map((chat, index) => {
          return (
            <ConversationSection
              key={`${chatRoomID}-${chat.id}-${index}`}
              chat={chat}
              scrollToBottom={scrollToBottom}
              newChatAnswering={newCustomChatID === chat?.customID}
              isLastIndex={index === chatHistories.length - 1}
            />
          );
        })}
        <div ref={chatEndRef}></div>
      </section>
    </>
  );
};

type ConversationSection = {
  scrollToBottom: () => void;
  chat: ChatType;
  newChatAnswering: boolean;
  isLastIndex: boolean;
};

const ConversationSection = memo(
  ({
    chat,
    scrollToBottom,
    newChatAnswering,
    isLastIndex,
  }: ConversationSection) => {
    const [showDislikeResponseModal, setShowDislikeResponseModal] =
      useState<boolean>(false);
    const [lawReferences, setLawReferences] = useState<
      LawReferenceType[] | null
    >(chat?.law_references || null);
    const [feedback, setFeedback] = useState<string>(chat?.feedback || "");
    const [rating, setRating] = useState<string>(chat?.rating || "");

    const answerEndRef = useRef<HTMLDivElement | null>(null);
    const answerRef = useRef<HTMLDivElement | null>(null);

    const { id, question, answer, status } = chat;
    const { handleAddNotification } = useNotification();

    const onCloseDislikeResponseModal = async (feedback: string) => {
      // await handleDislikeResponse(feedback);
      setShowDislikeResponseModal(false);
    };
    const handleShowDislikeResponseModal = () => {
      setShowDislikeResponseModal(true);
    };

    useEffect(() => {
      if (chat.law_references) {
        setLawReferences(chat.law_references);
      }
    }, [chat.law_references]);

    const handleLikeResponse = async () => {
      setFeedback("");
      setRating(Rating.LIKE);
      try {
        await api.chats.likeChat(id);

        if (!rating) {
          handleAddNotification({
            status: "success",
            content: `ขอบคุณสำหรับความคิดเห็น เราจะพัฒนาให้ดียิ่งขึ้น`,
          });
        }
      } catch (error) {
        if (error instanceof ResponseError) {
          handleAddNotification({
            status: "error",
            content: `Cannot like the answer due to: ${error.response.status} error`,
          });
        }
      }
    };

    const handleDislikeResponse = async (feedback: string = "") => {
      setFeedback(feedback);
      setRating(Rating.DISLIKE);
      try {
        await api.chats.dislikeChat(id, feedback);

        if (!rating) {
          handleAddNotification({
            status: "success",
            content: `ขอบคุณสำหรับความคิดเห็น เราจะพัฒนาให้ดียิ่งขึ้น`,
          });
        }
      } catch (error) {
        if (error instanceof ResponseError) {
          handleAddNotification({
            status: "error",
            content: `Cannot dislike the answer due to: ${error.response.status} error`,
          });
        }
      } finally {
        setShowDislikeResponseModal(false);
      }
    };

    useEffect(() => {
      if (newChatAnswering) {
        scrollToBottom();
      }
    }, [chat?.answer, newChatAnswering]);

    useEffect(() => {
      const scrollToLawRef = async () => {
        await wait(300);
        scrollToBottom();
      };
      if (status === CHAT_STATUS.DONE_STREAMING && isLastIndex) {
        scrollToLawRef();
      }
    }, [chat.law_references, status, isLastIndex]);

    const mappedLawReferences: MappedLawReferenceByNameType | null =
      useMemo(() => {
        if (lawReferences) {
          const reducedLawReferencesByLawName = lawReferences.reduce<
            Record<string, LawReferenceType[]>
          >((acc, value) => {
            if (!acc[value.law_name]) {
              acc[value.law_name] = [];
            }
            acc[value.law_name].push(value);
            return acc;
          }, {});
          return reducedLawReferencesByLawName;
        }
        return null;
      }, [lawReferences]);

    const responseAction = (
      <>
        <div className="flex items-center">
          <CopyButton text={answer || ""} />
          {/* Like */}
          <button
            type="button"
            aria-label="Like response"
            className={clsx("p-2 rounded-lg group text-gray-600")}
            onClick={handleLikeResponse}
          >
            {rating === Rating.LIKE ? (
              <>
                <ThumbDownGradientIcon
                  className={clsx("rotate-180 transition-all no-inherit")}
                />
              </>
            ) : (
              <ThumbUpIcon
                className={clsx(
                  "w-5 h-5 transition-all",
                  rating
                    ? "!text-gray-400"
                    : "group-hover:text-primary-300 group-hover:fill-primary-50"
                )}
              />
            )}
          </button>
          {/* Dislike */}
          <button
            type="button"
            aria-label="Dislike response"
            className="p-2 rounded-lg group text-gray-600"
            onClick={handleShowDislikeResponseModal}
          >
            {rating === Rating.DISLIKE ? (
              <ThumbDownGradientIcon
                className={clsx("transition-all no-inherit")}
              />
            ) : (
              <ThumbUpIcon
                className={clsx(
                  "w-5 h-5 rotate-180 transition-all",
                  rating
                    ? "!text-gray-400"
                    : "group-hover:text-primary-300 group-hover:fill-primary-50"
                )}
              />
            )}
          </button>
        </div>
      </>
    );

    return (
      <>
        {showDislikeResponseModal && (
          <DislikeResponseModal
            feedback={feedback}
            onClose={onCloseDislikeResponseModal}
            handleDislikeResponse={handleDislikeResponse}
          />
        )}
        <div
          id={id}
          className="flex flex-col md:gap-8 gap-6 pt-8 w-full md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto"
        >
          {/* user's question */}
          <div className="flex flex-col items-end gap-3">
            {/* header */}
            <div className="flex items-center gap-2.5">
              <div className="flex justify-center items-center rounded-full w-8 h-8 border border-gray-300 bg-gray-100">
                <UserIcon className="text-gray-600 w-5 h-5" />
              </div>
              <span className="text-gray-700 font-semibold text-sm">คุณ</span>
            </div>
            {/* question */}
            <div className="text-primary-700 md:max-w-[90%] break-words overflow-hidden text-md py-2 px-4 rounded-b-xl rounded-tl-xl border border-primary-300 bg-primary-50">
              {question}
            </div>
          </div>
          {/* sommaii's answer */}
          <div className="flex flex-col items-start gap-3">
            {/* header */}
            <div className="flex items-center gap-2.5">
              <Image
                src={SommaiiIcon}
                alt="Sommaii logo"
                className="h-8 w-8 object-contain rounded-full"
              />
              <span className="text-gray-700 font-semibold text-sm">
                สมหมาย
              </span>
            </div>
            {/* answer */}
            <div
              ref={answerRef}
              className="py-2 px-4 border border-gray-300 bg-gray-50 rounded-b-xl rounded-tr-xl md:max-w-[90%] overflow-hidden"
            >
              {chat?.loadingState && <LoadingThreeDots />}
              <div
                id={`${id}-answer`}
                className={clsx(
                  "flex-col gap-4 overflow-hidden",
                  chat?.loadingState ? "hidden" : "flex"
                )}
              >
                <>
                  {(chat.status === CHAT_STATUS.DONE ||
                    chat.status === CHAT_STATUS.DONE_STREAMING) &&
                  !answer?.trim() ? (
                    <p className="whitespace-pre-line text-gray-400 pr-2">
                      No result.
                    </p>
                  ) : chat.status === CHAT_STATUS.FAILED ? (
                    <p className="whitespace-pre-line text-error-300 pr-2">
                      Failed
                    </p>
                  ) : chat.status === CHAT_STATUS.PROCESSING &&
                    !newChatAnswering ? (
                    <p className="whitespace-pre-line text-gray-400 break-words">
                      Queuing up...
                    </p>
                  ) : (
                    <Markdown
                      remarkPlugins={[remarkGfm]}
                      className="whitespace-pre-line text-gray-600 break-words answer-section"
                    >
                      {answer}
                    </Markdown>
                  )}

                  {answer &&
                  (chat.status === CHAT_STATUS.DONE ||
                    chat.status === CHAT_STATUS.DONE_STREAMING) ? (
                    <>
                      <section className="flex flex-col gap-4">
                        {/* ref */}
                        <div className="font-semibold text-md">
                          กฏหมายที่เกี่ยวข้องมีดังนี้
                        </div>
                        {chat.loadingRef ? (
                          <div className="pl-1">
                            <LoadingThreeDots />
                          </div>
                        ) : (
                          <>
                            {mappedLawReferences &&
                            lawReferences &&
                            lawReferences.length > 0 ? (
                              <section className="flex flex-col gap-4">
                                {Object.keys(mappedLawReferences).map(
                                  (lawName, lawRefIndex) => {
                                    return (
                                      <LawReferenceSection
                                        key={lawRefIndex}
                                        lawName={lawName}
                                        lawRefs={mappedLawReferences[lawName]}
                                      />
                                    );
                                  }
                                )}
                              </section>
                            ) : (
                              <p className="text-gray-600 text-sm">
                                ไม่มีกฏหมายที่เกี่ยวข้อง
                              </p>
                            )}
                          </>
                        )}
                      </section>
                      {responseAction}
                    </>
                  ) : (
                    <></>
                  )}
                </>
              </div>
            </div>
          </div>
          {/* divider */}
          <div className="relative" ref={answerEndRef}>
            <hr
              className={clsx(
                !chat?.loadingState && !newChatAnswering
                  ? "border-gray-300"
                  : "border-transparent"
              )}
            />
            <div
              className={clsx(
                "text-gray-500 text-xs",
                !chat?.loadingState && !newChatAnswering
                  ? "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-1"
                  : "hidden"
              )}
            >
              จบการสนทนา
            </div>
          </div>
        </div>
      </>
    );
  }
);

type DefaultQuestionCardProps = {
  lawType: string;
  question: string;
  onClick: () => void;
};

const DefaultQuestionCard = ({
  lawType,
  question,
  onClick,
}: DefaultQuestionCardProps) => {
  return (
    <button
      type="button"
      aria-label={question}
      className="sm:max-w-[240px] sm:min-h-28 text-left relative rounded-b-xl rounded-tr-xl border-2 group border-transparent overflow-hidden p-0.5"
      onClick={onClick}
    >
      {/* border gradient */}
      <div className="absolute top-0 left-0 w-full h-full group-hover:bg-gradient-primary z-0"></div>
      {/* question */}
      <div className="h-full rounded-b-xl rounded-tr-xl group-hover:rounded-b-lg group-hover:rounded-tr-lg relative flex flex-col gap-1 bg-white border border-gray-300 group-hover:border-transparent p-2">
        <div className="text-gray-500 text-xs leading-[18px] bg-white">
          {lawType}
        </div>
        <p className="whitespace-pre-line text-md text-gray-600">{question}</p>
      </div>
    </button>
  );
};

type UserQuestionInputSectionProps = {
  handleAskQuestion: (question: string) => void;
  handleSetSelectedInferenceModel: (inferenceModel: InferenceModelType) => void;
  handleStopChat: () => void;
  showStopChat: boolean;
  selectedInferenceModel: InferenceModelType | null;
  inferenceModelList: InferenceModelType[];
};

const UserQuestionInputSection = memo(
  ({
    handleAskQuestion,
    handleSetSelectedInferenceModel,
    handleStopChat,
    showStopChat,
    selectedInferenceModel,
    inferenceModelList,
  }: UserQuestionInputSectionProps) => {
    // inference model selection
    const [showInferenceModelOptions, setShowInferenceModelOptions] =
      useState<boolean>(false);
    // user input text
    const [text, setText] = useState<string>("");
    const [clickedStopChat, setClickedStopChat] = useState<boolean>(false);

    const questionInputRef = useRef<HTMLTextAreaElement>(null);
    const { handleAddNotification } = useNotification();

    const handleShowInferenceModelOptions = (
      event: React.MouseEvent<HTMLButtonElement>
    ) => {
      event.preventDefault();
      event.stopPropagation();
      setShowInferenceModelOptions(!showInferenceModelOptions);
    };

    useEffect(() => {
      if (questionInputRef.current) {
        questionInputRef.current.style.height = "auto";
        questionInputRef.current.style.height = `${questionInputRef.current.scrollHeight}px`;
      }
    }, [text]);

    useEffect(() => {
      if (showStopChat) {
        setClickedStopChat(false);
      }
    }, [showStopChat]);

    const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
      setText(event.target.value);
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendText();
      }
    };

    const sendText = () => {
      if (text.trim() && !showStopChat) {
        handleAskQuestion(text);
        setText("");
      }
    };

    const handleClickStopChat = () => {
      handleStopChat();
      setClickedStopChat(true);
    };

    const inferenceModelOptions = useMemo(() => {
      return inferenceModelList.filter(
        (inferenceModel) => inferenceModel.id !== selectedInferenceModel?.id
      );
    }, [inferenceModelList, selectedInferenceModel]);

    return (
      <>
        <section className="relative flex flex-col gap-1 lg:px-0 md:px-8 px-6 mx-auto w-full md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem]">
          {showStopChat && (
            <>
              <button
                style={{ zIndex: Z_INDEX_STOP_BUTTON }}
                className="absolute lg:right-0 right-8 bottom-28 bg-primary-100 p-2 rounded-full opacity-60 hover:opacity-80"
                onClick={handleClickStopChat}
                disabled={clickedStopChat}
              >
                <StopIcon className="w-4 h-4 fill-primary-700" />
                {clickedStopChat && (
                  <span className="animate-ping absolute bottom-1 right-1 inline-flex h-6 w-6 rounded-full bg-gradient-primary opacity-75"></span>
                )}
              </button>
            </>
          )}

          {/* typing chat */}
          <div className="flex rounded-lg bg-white">
            {/* model selection */}
            {inferenceModelOptions.length > 0 ? (
              <Popover
                isOpen={showInferenceModelOptions}
                handleSetIsOpen={(state) => setShowInferenceModelOptions(state)}
                position="top-left"
                contentClassName="mb-1.5 sm:w-60 w-48"
                content={
                  <ul className="!font-inter flex flex-col gap-2 bg-white border border-gray-200 shadow-lg rounded-xl sm:p-3 p-1.5 w-80 max-w-[calc(100dvw_-_200px)]">
                    {inferenceModelList.map((inferenceModel, index) => {
                      return (
                        <li
                          className="w-full"
                          key={index}
                          title={inferenceModel.name}
                        >
                          <button
                            type="button"
                            aria-label={`${inferenceModel.name}`}
                            className="sm:py-3 py-2 pr-3 pl-5 text-left w-full rounded-lg bg-white hover:bg-gray-50 flex items-center gap-4 relative"
                            onClick={() => {
                              handleSetSelectedInferenceModel(inferenceModel);
                              if (questionInputRef.current) {
                                questionInputRef.current.focus();
                              }
                              setShowInferenceModelOptions(false);
                            }}
                          >
                            {inferenceModel.id ===
                              selectedInferenceModel?.id && (
                              <CheckIcon className="w-4 h-4 text-primary-500 absolute left-0.5 top-1/2 -translate-y-1/2" />
                            )}

                            <span className="text-[15px] font-semibold text-gray-600 sm:truncate pl-0.5">
                              {inferenceModel.name}
                            </span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                }
              >
                <button
                  type="button"
                  aria-label="Option"
                  title={selectedInferenceModel?.name}
                  className="rounded-l-lg sm:w-44 shadow-xs h-11 py-2.5 px-3.5 flex items-center gap-1 text-gray-700 font-semibold bg-white hover:bg-gray-50 border border-gray-300 disabled:border-gray-200 disabled:text-gray-400"
                  onClick={handleShowInferenceModelOptions}
                >
                  <span className="truncate text-left grow sm:block hidden">
                    {selectedInferenceModel?.name}
                  </span>
                  <ChevronDownIcon
                    className={clsx(
                      "w-5 h-5 transition-all shrink-0",
                      showInferenceModelOptions ? "rotate-180" : ""
                    )}
                  />
                </button>
              </Popover>
            ) : (
              <div className="rounded-l-lg shadow-xs h-11 py-2.5 px-3.5 flex items-center gap-1 text-gray-700 font-semibold bg-white border border-gray-300 disabled:border-gray-200 disabled:text-gray-400">
                <span>{selectedInferenceModel?.name}</span>
              </div>
            )}
            {/* question input */}
            <div className="relative flex h-fit grow ml-[-1px] text-gray-900 rounded-r-lg overflow-hidden">
              <textarea
                ref={questionInputRef}
                value={text}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="พิมพ์ข้อความที่นี่..."
                className="box-border flex text-md min-h-11 text-gray-900 border border-gray-300 shadow-xs outline-none rounded-r-lg w-full py-2.5 pl-3.5 pr-12"
                style={{ height: "44px" }}
              />
              <button
                disabled={!text || showStopChat}
                type="button"
                aria-label="ส่งคำถาม"
                className="absolute h-full w-11 shrink-0 rounded-r-lg right-0 top-0 btn-primary flex items-center justify-center"
                onClick={sendText}
              >
                <SendIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
          <p className="!font-inter text-center text-gray-400 sm:text-xs text-[9px] sm:leading-[18px]">
            Single-turn Chatbot | Model: {selectedInferenceModel?.name} |
            Powered by: VISTEC and VISAI.ai
          </p>
          <p className="text-center text-gray-400 text-[9px] sm:text-xs leading-[10px]">
            ข้อจำกัดความรับผิดชอบ: แชทบอทนี้ให้ข้อมูลกฎหมายเบื้องต้นเท่านั้น
            ไม่สามารถทดแทนคำปรึกษาจากผู้เชี่ยวชาญด้านกฎหมายได้
            ควรปรึกษาผู้เชี่ยวชาญด้านกฎหมาย เพื่อคำแนะนำที่เหมาะสมกับกรณีของท่าน
          </p>
        </section>
      </>
    );
  }
);

const DislikeResponseModal = ({
  feedback,
  onClose,
  handleDislikeResponse,
}: {
  feedback: string;
  onClose: (feedback: string) => void;
  handleDislikeResponse: (feedback: string) => void;
}) => {
  const responseInputID = useId();

  const dislikeOptions = [
    "ข้อความตอบกลับไม่รู้เรื่อง, ใช้ภาษาที่ผิด/แปลก",
    "อ้างอิงข้อมูลผิด",
    "ข้อมูลไม่ครบถ้วน",
    "ข้อมูลอ้างอิงถูก แต่โมเดลไม่ได้ใช้ข้อมูลนั้น",
    "แชทบอทอ้างอิงกฎหมายเก่า",
  ];

  const [selectedDislikeOptions, setSelectedDislikeOptions] = useState<
    string[]
  >([]);
  const [responseInput, setResponseInput] = useState<string>("");

  useEffect(() => {
    if (feedback?.trim()) {
      const lastParenIndex = feedback.lastIndexOf("(");
      const firstPart = feedback.substring(0, lastParenIndex).trim();
      const secondPart = feedback.substring(lastParenIndex).trim();
      setResponseInput(firstPart);
      const values = secondPart
        .replace(/[()]/g, "")
        .split(",")
        .map((v) => v?.trim());

      let containedOptions: string[] = [];

      values.forEach((value) => {
        const includedOption = dislikeOptions.find((option) =>
          option.includes(value)
        );
        if (includedOption) {
          containedOptions.push(includedOption);
        }
      });

      const selectedOptions = containedOptions.filter(function (
        value,
        index,
        array
      ) {
        return array.indexOf(value) === index;
      });

      setSelectedDislikeOptions(selectedOptions);
    }
  }, [feedback]);

  const onChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setResponseInput(event.target.value);
  };

  const handleSendFeedbackResponse = () => {
    const feedbackResponse: string = getFeedbackResponse();
    handleDislikeResponse(feedbackResponse);
  };

  const getFeedbackResponse = () => {
    const responseText: string = responseInput?.trim();
    let feedbackResponse: string = responseText;
    if (selectedDislikeOptions.length > 0) {
      const responseOption: string = selectedDislikeOptions.join(", ");
      feedbackResponse =
        responseText !== ""
          ? `${responseText} (${responseOption})`
          : responseOption;
    }
    return feedbackResponse;
  };

  const onEnterPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendFeedbackResponse();
    }
  };

  const handleAddSelectedDislikeOptions = (option: string) => {
    setSelectedDislikeOptions((prevState) => {
      if (prevState.includes(option)) {
        return prevState.filter((p) => p !== option);
      }
      return [...prevState, option];
    });
  };

  const onModalClose = () => {
    onClose(feedback);
  };

  return (
    <>
      <Modal
        onClose={onModalClose}
        body={
          <div className="p-6 max-h-[90vh] relative overflow-hidden w-[544px] max-w-[90vw] flex flex-col gap-8 justify-center text-left">
            <div>
              <header className="pr-6 text-lg font-semibold text-gray-900">
                ให้เหตุผลที่คุณไม่ชอบคำตอบนี้ได้ไหมครับ?
              </header>
              {/* response body */}
              <section className="flex flex-col gap-4 py-4">
                <div className="flex flex-wrap gap-2">
                  {dislikeOptions.map((option, index) => {
                    const isSelected = selectedDislikeOptions.includes(option);

                    return (
                      <button
                        type="button"
                        key={index}
                        aria-label={option}
                        className="group py-1 px-2.5 bg-white rounded-md flex items-center gap-1.5 border border-gray-300"
                        onClick={() => handleAddSelectedDislikeOptions(option)}
                      >
                        <Checkbox
                          isSelected={selectedDislikeOptions.includes(option)}
                        />
                        <span className="text-sm text-gray-700 font-medium">
                          {option}
                        </span>
                      </button>
                    );
                  })}
                </div>
                <div className="flex flex-col gap-1.5">
                  <label
                    htmlFor={responseInputID}
                    className="text-gray-700 text-sm font-medium"
                  >
                    บอกเราเพิ่มเติม
                  </label>
                  <textarea
                    id={responseInputID}
                    value={responseInput}
                    onChange={onChange}
                    onKeyDown={onEnterPress}
                    className="py-3 px-3.5 min-h-24 shadow-xs border border-gray-300 rounded-lg outline-none focus:border-primary-300 focus:ring-4 ring-primary-shadow"
                  />
                </div>
              </section>
            </div>
            {/* action */}
            <footer className="flex items-center gap-3">
              <button
                type="button"
                aria-label="ยกเลิก"
                className="btn-secondary-lg grow basis-0"
                onClick={onModalClose}
              >
                ยกเลิก
              </button>
              <button
                type="button"
                aria-label="ส่ง"
                className="btn-primary-lg grow basis-0"
                onClick={handleSendFeedbackResponse}
              >
                ส่ง
              </button>
            </footer>
          </div>
        }
      />
    </>
  );
};

export default ChatbotSection;
