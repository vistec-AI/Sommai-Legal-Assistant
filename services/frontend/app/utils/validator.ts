import DOMPurify from "isomorphic-dompurify";

export const validateEmail = (email: string) => {
  return /^[\w-\.]+@([\w-]+\.)+[\w-]{2,}$/.test(email);
};

export const validateContainLowerCase = (str: string) => {
  return /^(?=.*[a-z])[^]+/.test(str);
};

export const validateContainUpperCase = (str: string) => {
  return /^(?=.*[A-Z])[^]+/.test(str);
};

export const validateContainNumber = (str: string) => {
  return /^(?=.*\d)[^]+/.test(str);
};

export const sanitizedInput = (input: string) => {
  return DOMPurify.sanitize(input);
};
