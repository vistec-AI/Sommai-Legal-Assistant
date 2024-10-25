import { ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// waiting for (ms) milliseconds
export const wait = (ms: number) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

export const randomNumber = (max: number) => {
  return Math.floor(Math.random() * max);
}

export const shuffleArray = (array: any[]) => {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
};

export const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(inputs));
}