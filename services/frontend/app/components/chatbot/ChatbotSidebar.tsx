"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import clsx from "clsx";
import { getRefreshToken, getUser, logout } from "@/app/utils/auth";
import { useChatbot } from "@/app/context/ChatbotContext";
import { useNotification } from "@/app/context/NotificationContext";
import { ChatRoomType, ResponseError, InputSize } from "@/app/types";
import { Z_INDEX } from "@/app/constants";
import api from "@/api";
import { useLoading } from "@/app/context/LoadingFullScreenContext";

import LoadingFullScreen from "../animation/LoadingFullScreen";

import Input from "../common/Input";
import Popover from "../common/Popover";
import Modal from "../common/Modal";
import Toggle from "../common/Toggle";

import UserIcon from "@/public/icons/user.svg";
import SearchIcon from "@/public/icons/search.svg";
import PlusIcon from "@/public/icons/plus.svg";
import TrashIcon from "@/public/icons/trash.svg";
import EditIcon from "@/public/icons/edit.svg";
import DotVerticalIcon from "@/public/icons/dots-vertical.svg";
import CheckIcon from "@/public/icons/check.svg";
import XCloseIcon from "@/public/icons/x-close.svg";
import SettingIcon from "@/public/icons/settings.svg";
import LogoutIcon from "@/public/icons/log-out.svg";
import MenuIcon from "@/public/icons/menu.svg";
// modal
import AlertTriangleIcon from "@/public/icons/alert-triangle.svg";
import { sanitizedInput } from "@/app/utils/validator";

const CHAT_ACTION_WIDTH = "255px";
const SIDEBAR_CONTAINER_ID = "sidebarContainer";

const ChatbotSidebar = ({
  loadingState,
  chatRoomList = [],
  fetchChatroomData,
}: {
  loadingState: boolean;
  chatRoomList: ChatRoomType[];
  fetchChatroomData: () => Promise<any>;
}) => {
  const [showSidebar, setShowSidebar] = useState(false);

  const sidebarContainer = useRef<HTMLDivElement>(null);

  const onSidebarClose = () => {
    setShowSidebar(false);
  };

  useEffect(() => {
    if (showSidebar) {
      onSidebarFocus();
    }
  }, [chatRoomList, showSidebar]);

  const onSidebarFocus = () => {
    if (sidebarContainer.current) {
      sidebarContainer.current.focus();
    }
  };

  return (
    <>
      <div className={clsx("relative")}>
        <button
          type="button"
          aria-label="Show sidebar"
          style={{ zIndex: Z_INDEX.SIDEBAR_BUTTON }}
          className={clsx(
            "fixed top-16 left-6 md:hidden text-gray-700 hover:text-gray-800 tablet:hidden flex items-center justify-center w-7 rounded-lg"
          )}
          onClick={() => setShowSidebar(true)}
        >
          <MenuIcon
            className={clsx(
              "transition-all",
              !showSidebar ? "w-6 h-6" : "w-0 h-0"
            )}
          />
        </button>
        {showSidebar && (
          <div
            id={"backdropSidebar"}
            style={{ zIndex: Z_INDEX.SIDEBAR_BACKDROP }}
            className="md:hidden absolute w-[100dvw] h-[100dvh] bg-black/30"
          ></div>
        )}
        <div
          style={{ zIndex: Z_INDEX.SIDEBAR }}
          className={clsx(
            "md:relative h-full absolute grow md:w-auto",
            showSidebar
              ? "w-[100dvw] flex animate-slide-from-left"
              : "md:flex hidden"
          )}
        >
          <div
            ref={sidebarContainer}
            tabIndex={0}
            onBlur={(event: React.FocusEvent<HTMLDivElement>) => {
              if (!event.currentTarget.contains(event.relatedTarget)) {
                setShowSidebar(false);
              }
            }}
            className={clsx("flex outline-none", showSidebar ? "w-[80%]" : "")}
          >
            <button
              type="button"
              aria-label="Hide sidebar"
              style={{ zIndex: Z_INDEX.SIDEBAR_BUTTON }}
              className={clsx(
                "left-[70%] top-2 absolute md:hidden text-gray-700 hover:text-gray-800 tablet:hidden flex items-center justify-center w-7 rounded-lg"
              )}
              onClick={() => setShowSidebar(false)}
            >
              <XCloseIcon className={clsx("transition-all w-6 h-6")} />
            </button>
            <ChatbotSidebarBody
              loadingState={loadingState}
              chatRoomList={chatRoomList}
              showSidebar={showSidebar}
              onSidebarClose={onSidebarClose}
              fetchChatroomData={fetchChatroomData}
              onSidebarFocus={onSidebarFocus}
            />
          </div>
        </div>
      </div>
    </>
  );
};

const ChatbotSidebarBody = ({
  loadingState,
  chatRoomList = [],
  showSidebar,
  onSidebarClose,
  fetchChatroomData,
  onSidebarFocus,
}: {
  loadingState: boolean;
  chatRoomList: ChatRoomType[];
  showSidebar: boolean;
  onSidebarClose: () => void;
  fetchChatroomData: () => Promise<any>;
  onSidebarFocus: () => void;
}) => {
  const router = useRouter();

  const [userEmail, setUserEmail] = useState<string>("");
  const [searchChatInput, setSearchChatInput] = useState<string>("");
  const [deleteChatRoom, setDeleteChatRoom] = useState<ChatRoomType | null>(
    null
  );
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showSettingsModal, setShowSettingsModal] = useState<boolean>(false);

  const sidebarRef = useRef<HTMLDivElement | null>(null);
  const { handleAddNotification } = useNotification();
  const {
    currentChatRoom,
    handleSetCurrentChatRoom,
    handleSetLoadingCurrentChatRoomState,
    currentChatRoomList,
    handleSetCurrentChatRoomList,
  } = useChatbot();
  const { loadingFullScreen } = useLoading();

  const currentRoomID = currentChatRoom?.id || "";

  useEffect(() => {
    if (showSidebar && sidebarRef.current) {
      sidebarRef.current.focus();
    }
  }, [showSidebar]);

  useEffect(() => {
    handleSetCurrentChatRoomList(chatRoomList);
  }, [chatRoomList]);

  useEffect(() => {
    const user = getUser();
    if (user?.email) {
      setUserEmail(user.email);
    }
  }, []);

  useEffect(() => {
    if (chatRoomList.length > 0) {
      handleSetCurrentChatRoom(chatRoomList[0]);
    }
    handleSetLoadingCurrentChatRoomState(false);
  }, [chatRoomList]);

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

  const handleSetDeleteChatRoom = (chatRoom: ChatRoomType) => {
    setDeleteChatRoom(chatRoom);
  };

  const handleShowSettings = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();

    setShowSettings(!showSettings);
  };

  const handleShowSettingsModal = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
    event.stopPropagation();

    setShowSettingsModal(!showSettingsModal);
  };

  const handleSetChatRoom = (chatRoom: ChatRoomType) => {
    handleSetCurrentChatRoom(chatRoom);
  };

  const handleLogout = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();

    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await api.auth.logout({ refresh_token: refreshToken });
      } catch (error) {
        if (error instanceof ResponseError) {
          console.error(error);
        }
      }
    }
    logout();
    router.replace("/auth/login");
  };

  useEffect(() => {
    if (!deleteChatRoom || !showSettingsModal) {
      onSidebarFocus();
    }
  }, [deleteChatRoom, showSettingsModal]);

  return (
    <>
      {loadingFullScreen && <LoadingFullScreen />}
      {deleteChatRoom && (
        <DeleteChatRoomModal
          chatRoom={deleteChatRoom}
          chatRoomList={chatRoomList}
          handleCreateNewChat={handleCreateNewChat}
          onClose={() => {
            setDeleteChatRoom(null);
          }}
          fetchChatroomData={fetchChatroomData}
        />
      )}
      {showSettingsModal && (
        <SettingsModal onClose={() => setShowSettingsModal(false)} />
      )}
      <aside
        id={SIDEBAR_CONTAINER_ID}
        ref={sidebarRef}
        className={clsx(
          "bg-white md:pt-6 pt-8 w-full md:w-[320px] border-r border-gray-200 flex flex-col justify-between overflow-hidden shrink-0"
        )}
      >
        <div className="grow flex flex-col overflow-auto">
          {/* header */}
          <div className="pr-4 md:pl-8 pl-4 flex flex-col gap-6 pt-2">
            <SearchInput
              searchInputText={searchChatInput}
              handleSetSearchInputText={(input: string) =>
                setSearchChatInput(input)
              }
            />
            <button
              type="button"
              aria-label="New chat"
              className="btn-secondary !font-inter text-base rounded-lg py-2.5 px-4 flex justify-center items-center font-semibold gap-1.5"
              onClick={handleCreateNewChat}
            >
              <PlusIcon className="w-5 h-5" />
              <span>New Chat</span>
            </button>
          </div>
          {/* list of chats */}
          <ul className="grow overflow-auto flex flex-col gap-2 py-6 pr-4 md:pl-8 pl-4">
            {loadingState ? (
              <>
                {[...Array(3)].map((_, index) => {
                  return (
                    <li
                      key={`${index}`}
                      className="h-[58px] shrink-0 w-full rounded-xl overflow-auto bg-gray-100 animate-pulse duration-300"
                    >
                      <div className="text-gray-700 font-semibold text-base truncate opacity-0 w-[100dvw]"></div>
                    </li>
                  );
                })}
              </>
            ) : (
              <>
                {currentChatRoomList
                  .filter((chatRoom) =>
                    chatRoom.name
                      ?.toLowerCase()
                      ?.trim()
                      .includes(searchChatInput?.toLowerCase()?.trim())
                  )
                  .map((chatRoom, index) => {
                    return (
                      <li key={`${chatRoom.id}-${index}`}>
                        <ChatLink
                          chatRoom={chatRoom}
                          currentRoomID={currentRoomID}
                          handleSetDeleteChatRoom={handleSetDeleteChatRoom}
                          handleSetChatRoom={handleSetChatRoom}
                          onSidebarClose={onSidebarClose}
                          onSidebarFocus={onSidebarFocus}
                        />
                      </li>
                    );
                  })}
              </>
            )}
          </ul>
        </div>
        {/* footer */}
        <footer className="md:pb-8 pb-6 pt-4 md:mx-8 mx-6 border-t border-gray-200 flex gap-3 items-start justify-between">
          <div className="flex items-center gap-3 overflow-hidden">
            {/* user image */}
            <div className="flex justify-center items-center shrink-0 rounded-full w-10 h-10 border border-gray-300 bg-gray-100">
              <UserIcon className="text-gray-600 w-6 h-6" />
            </div>
            {/* user info */}
            <div className="flex flex-col text-sm overflow-hidden">
              <div className="text-gray-700 font-semibold truncate">
                ผู้ใช้งาน
              </div>
              {/* user email */}
              <div className="text-gray-600 truncate">{userEmail}</div>
            </div>
          </div>
          <Popover
            isOpen={showSettings}
            handleSetIsOpen={(state) => setShowSettings(state)}
            className="flex justify-center"
            position="top-right"
            contentClassName="mr-2"
            content={
              <div
                style={{ width: CHAT_ACTION_WIDTH }}
                className="w-full p-3 text-base bg-white border border-gray-200 rounded-xl shadow-lg flex flex-col gap-2"
              >
                {/* <button
                  type="button"
                  aria-label="ตั้งค่า"
                  className="rounded-lg p-3 flex gap-4 items-center bg-white hover:bg-gray-50 text-gray-600 hover:text-gray-800 font-semibold"
                  onClick={handleShowSettingsModal}
                >
                  <SettingIcon className="stroke-current w-6 h-6" />
                  <span>ตั้งค่า</span>
                </button> */}
                <button
                  type="button"
                  aria-label="ออกจากระบบ"
                  className="rounded-lg p-3 flex gap-4 items-center bg-white hover:bg-gray-50 text-gray-600 hover:text-gray-800 font-semibold"
                  onClick={handleLogout}
                >
                  <LogoutIcon className="stroke-current w-6 h-6" />
                  <span>ออกจากระบบ</span>
                </button>
              </div>
            }
          >
            <button
              type="button"
              aria-label="Option"
              className="text-gray-400 hover:text-gray-500"
              onClick={handleShowSettings}
            >
              <DotVerticalIcon className="w-5 h-5" />
            </button>
          </Popover>
        </footer>
      </aside>
    </>
  );
};

const DeleteChatRoomModal = ({
  chatRoom,
  chatRoomList,
  handleCreateNewChat,
  onClose,
  fetchChatroomData,
}: {
  chatRoom: ChatRoomType;
  chatRoomList: ChatRoomType[];
  handleCreateNewChat: () => Promise<any>;
  onClose: () => void;
  fetchChatroomData: () => Promise<any>;
}) => {
  const { handleAddNotification } = useNotification();
  const { handleSetCurrentChatRoom, handleSetLoadingCurrentChatRoomState } =
    useChatbot();
  const { handleSetLoadingFullScreen } = useLoading();

  const initialNewChatRoom = async () => {
    const newChatRoom = await handleCreateNewChat();
    handleSetCurrentChatRoom(newChatRoom);
    handleSetLoadingCurrentChatRoomState(false);
  };

  const handleCancelDelete = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    onClose();
  };

  const handleDeleteChatRoom = async (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
    event.stopPropagation();

    handleSetLoadingFullScreen(true);
    const deleteChatRoomName = chatRoom?.name || "";
    try {
      await api.chatRooms.deleteChatRoom(chatRoom?.id);
      if (chatRoomList.length <= 1) {
        await initialNewChatRoom();
      }

      await fetchChatroomData();
      handleAddNotification({
        status: "success",
        content: `ลบประวัติการสนทนา ${deleteChatRoomName}`,
      });
    } catch (error) {
      if (error instanceof ResponseError) {
        handleAddNotification({
          status: "error",
          content: `Cannot create new chat due to: ${error.response.status} error`,
        });
      }
    } finally {
      handleSetLoadingFullScreen(false);
      onClose();
    }
  };

  return (
    <Modal
      onClose={onClose}
      body={
        <div className="p-6 max-h-[90vh] relative overflow-hidden w-[400px] max-w-[90vw] flex flex-col gap-8 justify-center text-left">
          <header className="flex flex-col gap-4">
            <div className="mr-auto rounded-full bg-warning-100 w-14 h-14 flex justify-center items-center border-8 border-warning-50">
              <AlertTriangleIcon className="text-warning-600 inherit-stroke-w stroke-[1.5] h-6 w-6" />
            </div>
            {/* header */}
            <section className="flex flex-col gap-1">
              <h5 className="text-lg text-gray-900 font-semibold">
                ยืนยันการลบประวัติสนทนานี้
              </h5>
              <p className="text-gray-600 text-sm">
                คุณแน่ใจหรือไม่ว่าต้องการลบประวัติสนทนานี้?
                <br />
                การลบจะไม่สามารถย้อนกลับได้
              </p>
            </section>
          </header>
          {/* action */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              aria-label="ยกเลิก"
              className="btn-secondary-md grow basis-0"
              onClick={handleCancelDelete}
            >
              ยกเลิก
            </button>
            <button
              type="button"
              aria-label="ลบประวัติการสนทนา"
              className="btn-error-md grow basis-0 whitespace-nowrap"
              onClick={handleDeleteChatRoom}
            >
              ลบประวัติการสนทนา
            </button>
          </div>
        </div>
      }
    />
  );
};

const SettingsModal = ({ onClose }: { onClose: () => void }) => {
  const [enableSaveChat, setEnableSaveChat] = useState<boolean>(true);

  const { handleAddNotification } = useNotification();

  const handleEnableSaveChatHistory = async () => {
    try {
      handleAddNotification({
        status: "success",
        content: enableSaveChat
          ? "เก็บประวัติการใช้งาน"
          : "ยกเลิกการเก็บประวัติการใช้งาน",
      });
    } catch (error) {
      if (error instanceof ResponseError) {
        handleAddNotification({
          status: "error",
          content: `Cannot enable due to: ${error.response.status} error`,
        });
      }
    } finally {
      onClose();
    }
  };

  return (
    <Modal
      onClose={onClose}
      body={
        <div className="p-6 max-h-[90vh] relative overflow-hidden w-[400px] max-w-[90vw] flex flex-col gap-8 justify-center text-left">
          <header className="flex flex-col gap-5">
            {/* header */}
            <h5 className="text-lg text-gray-900 font-semibold">Setting</h5>
            {/* enable chat history saving toggle */}
            <div className="flex items-center text-gray-700 text-sm gap-2">
              <Toggle
                isSelected={enableSaveChat}
                handleToggle={() => setEnableSaveChat(!enableSaveChat)}
              />
              <p>เก็บประวัติการใช้งาน</p>
            </div>
          </header>
          {/* action */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              aria-label="ยกเลิก"
              className="btn-secondary-lg grow basis-0"
              onClick={onClose}
            >
              ยกเลิก
            </button>
            <button
              type="button"
              aria-label="บันทึก"
              className="btn-primary-lg grow basis-0"
              onClick={handleEnableSaveChatHistory}
            >
              บันทึก
            </button>
          </div>
        </div>
      }
    />
  );
};

const ChatLink = ({
  chatRoom,
  handleSetDeleteChatRoom,
  currentRoomID,
  handleSetChatRoom,
  onSidebarClose,
  onSidebarFocus,
}: {
  chatRoom: ChatRoomType;
  handleSetDeleteChatRoom: (chatRoom: ChatRoomType) => void;
  currentRoomID: string;
  handleSetChatRoom: (chatRoom: ChatRoomType) => void;
  onSidebarClose: () => void;
  onSidebarFocus: () => void;
}) => {
  const [showChatAction, setShowChatAction] = useState<boolean>(false);
  // rename
  const [renameState, setRenameState] = useState<boolean>(false);
  const [newChatRoomName, setNewChatRoomName] = useState<string>(
    chatRoom?.name || ""
  );

  const renameRef = useRef<HTMLInputElement | null>(null);

  const { handleAddNotification } = useNotification();
  const { handleSetNewChatRoomNameByID, stopResponseSSE } = useChatbot();

  const handleShowChatAction = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();

    setShowChatAction(!showChatAction);
  };

  const handleShowRenameState = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
    event.stopPropagation();

    setRenameState(true);
    setShowChatAction(false);
  };

  useEffect(() => {
    setNewChatRoomName(chatRoom?.name || "");
  }, [chatRoom.name]);

  const handleCloseRenameState = (
    event:
      | React.MouseEvent<HTMLButtonElement>
      | React.KeyboardEvent<HTMLInputElement>
  ) => {
    event.preventDefault();
    event.stopPropagation();

    setRenameState(false);
    setNewChatRoomName(chatRoom?.name || "");
  };

  const handleNewNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNewChatRoomName(event.target.value);
  };

  const handleRenameChatRoom = async (
    event:
      | React.MouseEvent<HTMLButtonElement>
      | React.KeyboardEvent<HTMLInputElement>
  ) => {
    event.preventDefault();
    event.stopPropagation();

    const originalChatRoom = chatRoom?.name || "";
    const sanitizedNewChatRoomName = sanitizedInput(newChatRoomName);
    try {
      await api.chatRooms.renameChatRoom(
        chatRoom?.id,
        sanitizedNewChatRoomName
      );
      handleSetNewChatRoomNameByID(chatRoom.id, sanitizedNewChatRoomName);
      handleAddNotification({
        status: "success",
        content: `เปลี่ยนชื่อจาก ‘${originalChatRoom}’ เป็น ‘${sanitizedNewChatRoomName}’`,
      });
    } catch (error) {
      if (error instanceof ResponseError) {
        handleAddNotification({
          status: "error",
          content: `Cannot create new chat due to: ${error.response.status} error`,
        });
      }
    } finally {
      setRenameState(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleRenameChatRoom(event);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      handleCloseRenameState(event);
    }
  };

  useEffect(() => {
    if (renameState && renameRef.current) {
      renameRef.current?.focus();
      return;
    }
  }, [renameState]);

  return (
    <div
      className={clsx(
        "border border-gray-300 flex items-center justify-between rounded-xl p-4 w-full hover:bg-gray-50 cursor-pointer",
        currentRoomID === chatRoom?.id
          ? "bg-gray-50 ring-4 ring-gray-400/[14%]"
          : "",
        renameState ? "gap-0" : "gap-2"
      )}
      onClick={() => {
        stopResponseSSE();
        onSidebarClose();
        handleSetChatRoom(chatRoom);
      }}
    >
      {renameState ? (
        <div
          tabIndex={0}
          onBlur={(event: React.FocusEvent<HTMLDivElement>) => {
            if (!event.currentTarget.contains(event.relatedTarget)) {
              setNewChatRoomName(chatRoom?.name || "");
              setRenameState(false);
            }
          }}
          className="flex items-center gap-2"
        >
          <Input
            inputRef={renameRef}
            type={"text"}
            containerClassName="rounded-md outline-none w-[90%]"
            value={newChatRoomName}
            onChange={handleNewNameChange}
            onKeyDown={handleKeyDown}
            size={InputSize.XS}
            onClick={(event: React.MouseEvent<HTMLInputElement>) => {
              event.preventDefault();
              event.stopPropagation();
            }}
          />
          <button
            type="button"
            aria-label="ยืนยันการเปลี่ยนชื่อ"
            className="text-gray-600 hover:text-gray-700 flex items-center justify-center rounded-lg"
            onClick={handleRenameChatRoom}
          >
            <CheckIcon className="w-5 h-5" />
          </button>
          <button
            type="button"
            aria-label="ยกเลิกการเปลี่ยนชื่อ"
            className="text-gray-600 hover:text-gray-700 flex items-center justify-center rounded-lg"
            onClick={handleCloseRenameState}
          >
            <XCloseIcon className="w-5 h-5" />
          </button>
        </div>
      ) : (
        <span className="text-gray-700 font-semibold text-base truncate">
          {chatRoom.name}
        </span>
      )}
      <Popover
        isOpen={showChatAction}
        handleSetIsOpen={(state) => setShowChatAction(state)}
        className="flex justify-center"
        position="bottom-right"
        contentClassName="mr-2"
        content={
          <div
            style={{ width: CHAT_ACTION_WIDTH }}
            className="w-full p-3 text-base bg-white border border-gray-200 rounded-xl shadow-lg flex flex-col gap-2"
          >
            <button
              type="button"
              aria-label="แก้ไขชื่อ"
              className="rounded-lg p-3 flex gap-4 items-center bg-white hover:bg-gray-50 text-gray-600 hover:text-gray-800 font-semibold"
              onClick={handleShowRenameState}
            >
              <EditIcon className="stroke-current w-6 h-6" />
              <span>แก้ไขชื่อ</span>
            </button>
            <button
              type="button"
              aria-label="ลบ"
              className="rounded-lg p-3 flex gap-4 items-center bg-white hover:bg-error-50 text-error-600 hover:text-error-700 font-semibold"
              onClick={() => handleSetDeleteChatRoom(chatRoom)}
            >
              <TrashIcon className="stroke-current w-6 h-6" />
              <span>ลบ</span>
            </button>
          </div>
        }
      >
        <button
          type="button"
          aria-label="Option"
          className="text-gray-400 hover:text-gray-500"
          onClick={handleShowChatAction}
        >
          <DotVerticalIcon className="w-5 h-5" />
        </button>
      </Popover>
    </div>
  );
};

type SearchInputProps = {
  searchInputText: string;
  handleSetSearchInputText: (input: string) => void;
};

const SearchInput = ({
  searchInputText,
  handleSetSearchInputText,
}: SearchInputProps) => {
  const inputPrefix = (
    <div className="flex items-center justify-center text-gray-500 shrink-0 pl-2.5">
      <SearchIcon className="stroke-current w-5 h-5" />
    </div>
  );
  return (
    <Input
      type="text"
      placeholder="Search"
      value={searchInputText}
      prefix={inputPrefix}
      onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
        handleSetSearchInputText(event.target.value)
      }
      size={InputSize.MD}
      containerClassName="!font-inter"
    />
  );
};

export default ChatbotSidebar;
