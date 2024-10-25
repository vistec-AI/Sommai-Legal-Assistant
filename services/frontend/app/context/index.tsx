"use client";

import { ChatbotProvider } from "./ChatbotContext";
import { LoadingProvider } from "./LoadingFullScreenContext";
import { NotificationProvider } from "./NotificationContext";

const providers = [ChatbotProvider, LoadingProvider, NotificationProvider];

const combineComponents = (...components: any[]) => {
  return components.reduce(
    (AccumulatedComponents, CurrentComponent) => {
      return ({ children }: any) => {
        return (
          <AccumulatedComponents>
            <CurrentComponent>{children}</CurrentComponent>
          </AccumulatedComponents>
        );
      };
    },
    ({ children }: any) => <>{children}</>
  );
};

export const Provider = combineComponents(...providers);
