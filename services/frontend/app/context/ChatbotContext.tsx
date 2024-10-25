"use client";

import React, { useState, createContext, useContext, useEffect } from "react";
import { CHAT_MODE } from "../constants";
import { ChatRoomType, ChatType } from "../types";

type ChatbotContextProps = {
  selectedChatbotMode: string;
  handleSetSelectedChatbotMode: (selectedChatbotMode: string) => void;
  currentChatRoom: ChatRoomType | null;
  handleSetCurrentChatRoom: (selectedChatRoom: ChatRoomType) => void;
  streamAbortController: AbortController;
  handleSetStreamAbortController: (abortController: AbortController) => void;
  loadingCurrentChatRoom: boolean;
  handleSetLoadingCurrentChatRoomState: (state: boolean) => void;
  currentChatRoomList: ChatRoomType[];
  handleSetCurrentChatRoomList: (list: ChatRoomType[]) => void;
  handleSetNewChatRoomNameByID: (id: string, newChatRoomName: string) => void;
  stopResponseSSE: () => void;
};

const contextDefaultValues: ChatbotContextProps = {
  selectedChatbotMode: CHAT_MODE.CHATBOT,
  handleSetSelectedChatbotMode: () => {},
  currentChatRoom: null,
  handleSetCurrentChatRoom: () => {},
  streamAbortController: new AbortController(),
  handleSetStreamAbortController: () => {},
  loadingCurrentChatRoom: true,
  handleSetLoadingCurrentChatRoomState: () => {},
  currentChatRoomList: [],
  handleSetCurrentChatRoomList: () => {},
  handleSetNewChatRoomNameByID: () => {},
  stopResponseSSE: () => {},
};

export const ChatbotContext =
  createContext<ChatbotContextProps>(contextDefaultValues);

export function useChatbot() {
  return useContext(ChatbotContext);
}

export const ChatbotProvider = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  const [currentChatRoomList, setCurrentChatRoomList] = useState<
    ChatRoomType[]
  >([]);
  const [selectedChatbotMode, setSelectedChatbotMode] = useState<string>(
    contextDefaultValues.selectedChatbotMode
  );
  const [currentChatRoom, setCurrentChatRoom] = useState<ChatRoomType | null>(
    null
  );
  const [loadingCurrentChatRoom, setLoadingCurrentChatRoom] =
    useState<boolean>(true);

  const [streamAbortController, setStreamAbortController] =
    useState<AbortController>(new AbortController());

  const handleSetSelectedChatbotMode = (mode: string) => {
    setSelectedChatbotMode(mode);
  };

  const handleSetCurrentChatRoom = (chatRoom: ChatRoomType) => {
    setCurrentChatRoom(chatRoom);
  };

  const handleSetStreamAbortController = (
    newAbortController: AbortController
  ) => {
    setStreamAbortController(newAbortController);
  };

  const handleSetLoadingCurrentChatRoomState = (state: boolean) => {
    setLoadingCurrentChatRoom(state);
  };

  const handleSetCurrentChatRoomList = (list: ChatRoomType[]) => {
    setCurrentChatRoomList(list);
  };

  const handleSetNewChatRoomNameByID = (
    id: string,
    newChatRoomName: string
  ) => {
    setCurrentChatRoomList((prevState) => {
      const tempPrevState = [...prevState];
      const chatIndex = prevState.findIndex((p) => p.id === id);
      if (chatIndex !== -1) {
        tempPrevState[chatIndex] = {
          ...prevState[chatIndex],
          name: newChatRoomName,
        };
        return tempPrevState;
      }
      return prevState;
    });
  };

  const stopResponseSSE = () => {
    if (streamAbortController) {
      streamAbortController.abort();
    }
    const newController = new AbortController();
    handleSetStreamAbortController(newController);
  };

  useEffect(() => {
    if (currentChatRoom) {
      const chatRoomElement = document.getElementById(currentChatRoom?.id);

      if (chatRoomElement) {
        chatRoomElement.scrollTop = chatRoomElement.scrollHeight;
      }
    }
  }, [currentChatRoom?.id]);

  const value: ChatbotContextProps = {
    selectedChatbotMode,
    handleSetSelectedChatbotMode,
    currentChatRoom,
    handleSetCurrentChatRoom,
    streamAbortController,
    handleSetStreamAbortController,
    loadingCurrentChatRoom,
    handleSetLoadingCurrentChatRoomState,
    currentChatRoomList,
    handleSetCurrentChatRoomList,
    handleSetNewChatRoomNameByID,
    stopResponseSSE,
  };

  return (
    <ChatbotContext.Provider value={value}>{children}</ChatbotContext.Provider>
  );
};
