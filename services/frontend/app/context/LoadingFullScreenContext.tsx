"use client";

import React, { useState, createContext, useContext, useEffect } from "react";

type LoadingContextProps = {
  loadingFullScreen: boolean;
  loadingText: string;
  handleSetLoadingFullScreen: (state: boolean) => void;
  handleSetLoadingText: (text: string) => void;
};

const contextDefaultValues: LoadingContextProps = {
  loadingFullScreen: false,
  handleSetLoadingFullScreen: () => {},
  loadingText: "",
  handleSetLoadingText: () => {},
};

export const LoadingContext =
  createContext<LoadingContextProps>(contextDefaultValues);

export function useLoading() {
  return useContext(LoadingContext);
}

export const LoadingProvider = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  const [loadingFullScreen, setLoadingFullScreen] = useState<boolean>(false);
  const [loadingText, setLoadingText] = useState<string>("");

  const handleSetLoadingFullScreen = (state: boolean) => {
    setLoadingFullScreen(state);
  };
  const handleSetLoadingText = (text: string) => {
    setLoadingText(text);
  };

  const value: LoadingContextProps = {
    loadingFullScreen,
    handleSetLoadingFullScreen,
    loadingText,
    handleSetLoadingText,
  };

  return (
    <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>
  );
};
