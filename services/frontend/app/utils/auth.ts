import Cookie from "js-cookie";
import { actionSetCookie } from "../actions";

// expires in 14 days
const EXPIRES_DAY = 14;

// token key
export const TOKEN = "legal_chatbot_token";
// user key
export const USER = "legal_chatbot_user";
// terms
export const HAS_ACCEPTED_TERMS = "legal_chatbot_has_accepted_terms"

export type UserType = {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export type TokenType = {
  access_token: string;
  refresh_token: string;
}

export const SECURE_OPTION = process.env.NODE_ENV === "production" ? { secure: true } : {}
const tokenOption = { expires: EXPIRES_DAY, path: "/", ...SECURE_OPTION };

export const isBrowser = () => typeof window !== "undefined";

export const getUser = () => {
  const storedUser = Cookie.get(USER);
  if (storedUser) {
    const user = JSON.parse(storedUser);
    return user && Object.keys(user).length > 0 ? user : null;
  } else {
    return null;
  }
};


export const setUser = (user: UserType) => {
  Cookie.set(USER, JSON.stringify(user), tokenOption);
};

export const setUserTokens = async (token: TokenType) => {
  const data = JSON.stringify(token);
  Cookie.set(TOKEN, data, tokenOption);
};

export const getTokens = () => {
  const token = Cookie.get(TOKEN);
  return token ? JSON.parse(token) : null;
};

export const getAccessToken = () => {
  const token = Cookie.get(TOKEN);
  return token ? JSON.parse(token)?.["access_token"] : null;
};

export const getRefreshToken = () => {
  const token = Cookie.get(TOKEN);
  return token ? JSON.parse(token)?.["refresh_token"] : null;
};
export const isLoggedIn = !!getAccessToken();

export const logout = () => {
  Cookie.remove(USER, { path: "/" });
  Cookie.remove(TOKEN, { path: "/" });
};

export const getAcceptTermsHistory = () => {
  return isBrowser() && window.localStorage.getItem(HAS_ACCEPTED_TERMS)
    ? JSON.parse(window.localStorage.getItem(HAS_ACCEPTED_TERMS) || "")
    : false;
};

export const updateUserAcceptTerms = (
  state: boolean
) => {
  localStorage.setItem(HAS_ACCEPTED_TERMS, String(state));
  window.dispatchEvent(new Event("storage"));
};

