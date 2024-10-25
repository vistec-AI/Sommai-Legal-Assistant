"use client";

import { useEffect, useMemo, useState } from "react";
import clsx from "clsx";
import {
  ChatRoomType,
  ChatType,
  InferenceModelType,
  ResponseError,
} from "@/app/types";

import api from "@/api";

import { useChatbot } from "@/app/context/ChatbotContext";
import { useNotification } from "@/app/context/NotificationContext";
import ChatbotSidebar from "./ChatbotSidebar";
import ChatbotSection from "./ChatbotSection";

import PlusIcon from "@/public/icons/plus.svg";

const ChatLayout = ({
  inferenceModelList = [],
}: {
  inferenceModelList: InferenceModelType[];
}) => {
  const [chatsByChatRoomID, setChatByChatRoomID] = useState<
    Record<string, ChatType[]>
  >({});
  const [loadingChats, setLoadingChats] = useState<boolean>(false);

  const [chatRoomList, setChatRoomList] = useState<ChatRoomType[]>([]);
  const [loadingState, setLoadingState] = useState<boolean>(true);

  const { currentChatRoom, loadingCurrentChatRoom } = useChatbot();
  const { handleAddNotification } = useNotification();

  useEffect(() => {
    const initialData = async () => {
      await fetchChatroomData();
      setLoadingState(false);
    };
    initialData();
  }, []);

  const fetchChatroomData = async () => {
    try {
      const res = await api.chatRooms.getAllChatRooms();
      const chatRooms = await res.json();
      setChatRoomList(chatRooms);
    } catch (err) {
      if (err instanceof ResponseError) {
      }
    }
  };

  useEffect(() => {
    setLoadingChats(true);
    const reducedChatsByChatRoomID = chatRoomList.reduce<
      Record<string, ChatType[]>
    >((acc, value) => {
      if (!acc[value.id]) {
        acc[value.id] = [];
      }
      acc[value.id] = value.chats;
      return acc;
    }, {});
    setChatByChatRoomID(reducedChatsByChatRoomID);
    setLoadingChats(false);
  }, [chatRoomList]);

  const updateChatByChatRoomID = (chatRoomID: string, newChats: ChatType[]) => {
    setChatByChatRoomID((prevState) => {
      const tempPrevState = JSON.parse(JSON.stringify(prevState));

      if (tempPrevState[chatRoomID]) {
        tempPrevState[chatRoomID] = newChats;
        return tempPrevState;
      }

      return tempPrevState;
    });
  };

  // create chat room
  const handleCreateNewChat = async () => {
    try {
      const response = await api.chatRooms.createChatRoom("การสนทนาใหม่");
      // revalidate
      await fetchChatroomData();

      const newChatRoom = await response.json();
      return newChatRoom;
    } catch (error) {
      if (error instanceof ResponseError) {
        handleAddNotification({
          status: "error",
          content: `Cannot create new chat room due to: ${error.response.status} error`,
        });
      }
    }
  };

  return (
    <>
      <ChatbotSidebar
        loadingState={loadingState}
        chatRoomList={chatRoomList}
        fetchChatroomData={fetchChatroomData}
      />
      <section className={clsx("overflow-hidden flex grow")}>
        {loadingCurrentChatRoom || loadingChats || loadingState ? (
          <>
            <div className="animate-pulse flex flex-col pt-8 md:gap-8 gap-6 md:px-8 px-6 md:pb-8 pb-6 w-full md:max-w-3xl lg:max-w-[40rem] xl:max-w-[48rem] mx-auto">
              {/* user's question */}
              <div className="flex flex-col items-end gap-3">
                {/* header */}
                <div className="flex items-center gap-2.5">
                  <div className="flex justify-center items-center rounded-full w-8 h-8 border border-gray-100 bg-gray-100"></div>
                  <span className="text-gray-100 font-semibold rounded text-sm bg-gray-100">
                    คุณ
                  </span>
                </div>
                {/* question */}
                <div className="h-10 w-[50%] shrink-0 md:max-w-[90%] break-words overflow-hidden text-md py-2 px-4 rounded-b-xl rounded-tl-xl border border-primary-50 bg-primary-50"></div>
              </div>
              <div className="flex flex-col items-start gap-3">
                {/* header */}
                <div className="flex items-center gap-2.5">
                  <div className="h-8 w-8 rounded-full bg-gray-100"></div>
                  <span className="text-gray-100 font-semibold text-sm bg-gray-100 rounded">
                    สมหมาย
                  </span>
                </div>
                {/* answer */}
                <div className="shrink-0 w-[50%] h-20 border border-gray-100 bg-gray-100 rounded-b-xl rounded-tr-xl md:max-w-[90%] overflow-hidden"></div>
              </div>
            </div>
          </>
        ) : (
          <>
            {chatRoomList.length <= 0 ? (
              <>
                <section className="relative grow overflow-auto lg:px-0 md:px-8 px-6 pt-8 pb-4 flex flex-col gap-8 items-center">
                  <div className="flex flex-col gap-2 text-center">
                    <p className="text-gray-600 text-sm">
                      ถามคำถาม-หาคำตอบทางกฏหมายที่คุณต้องการได้ที่โหมดแชทบอท
                    </p>
                    <div className="bg-clip-text text-transparent bg-gradient-primary mx-auto font-semibold md:text-3xl md:leading-[38px] text-2xl">
                      สร้างห้องแชทใหม่เพื่อเริ่มต้นใช้งาน
                    </div>
                  </div>
                  <button
                    type="button"
                    aria-label="New Chat"
                    className="!font-inter btn-primary text-base font-semibold py-2.5 px-3.5 rounded-lg flex justify-center items-center gap-1.5"
                    onClick={handleCreateNewChat}
                  >
                    <PlusIcon className="w-5 h-5" />
                    New Chat
                  </button>
                </section>
              </>
            ) : (
              <>
                {currentChatRoom ? (
                  <>
                    {chatRoomList.map((chatRoom) => {
                      const chats =
                        chatsByChatRoomID[chatRoom.id] || chatRoom.chats || [];
                      chats.sort(
                        (a, b) =>
                          new Date(a.created_at).getTime() -
                          new Date(b.created_at).getTime()
                      );

                      return (
                        <ChatbotSection
                          key={chatRoom.id}
                          chatRoom={chatRoom}
                          inferenceModelList={inferenceModelList}
                          chats={chats}
                          updateChatByChatRoomID={updateChatByChatRoomID}
                          className={clsx(
                            chatRoom.id === currentChatRoom.id ? "" : "hidden"
                          )}
                        />
                      );
                    })}
                  </>
                ) : (
                  <></>
                )}
              </>
            )}

            {/* {currentChatRoom && currentChatRoom?.id && (
              <ChatbotSection
                key={currentChatRoom.id}
                chatRoom={currentChatRoom}
                inferenceModelList={inferenceModelList}
                chats={
                  chatsByChatRoomID[currentChatRoom.id] ||
                  currentChatRoom.chats ||
                  []
                }
                updateChatByChatRoomID={updateChatByChatRoomID}
              />
            )} */}
          </>
        )}
      </section>
    </>
  );
};

export default ChatLayout;
