"use client";

import React, { useState, createContext, useContext, useEffect } from "react";
import { NotificationProps } from "../types";

type NotificationContextProps = {
  notifications: NotificationProps[];
  handleAddNotification: (
    notification: NotificationProps,
    time?: number
  ) => void;
};

const contextDefaultValues: NotificationContextProps = {
  notifications: [],
  handleAddNotification: () => {},
};

export const NotificationContext =
  createContext<NotificationContextProps>(contextDefaultValues);

export function useNotification() {
  return useContext(NotificationContext);
}

export const NotificationProvider = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  const [notifications, setNotifications] = useState<NotificationProps[]>([]);

  const handleAddNotification = (
    notification: NotificationProps,
    time = 3000
  ) => {
    setNotifications((prevState) => {
      return [...prevState, notification];
    });
    let count = 0;
    let notifyTimeInterval = setTimeout(() => {
      count++;
      setNotifications((prevState) =>
        prevState.filter((n) => n !== notification)
      );
      clearTimeout(notifyTimeInterval);
    }, time);
  };

  useEffect(() => {
    return () => {
      setNotifications([]);
    };
  }, []);

  const value: NotificationContextProps = {
    notifications,
    handleAddNotification,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
