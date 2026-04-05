import { User } from "../types";

const USER_STORAGE_KEY = "user";
const TOKEN_STORAGE_KEY = "auth_tokens";

export interface StoredTokens {
  accessToken: string;
  refreshToken: string;
}

function canUseStorage() {
  return typeof window !== "undefined" && !!window.localStorage;
}

function emitAuthLogout() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("auth:logout"));
  }
}

export function getStoredUser(): User | null {
  if (!canUseStorage()) return null;
  const raw = window.localStorage.getItem(USER_STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setStoredUser(user: User | null) {
  if (!canUseStorage()) return;
  if (user) {
    window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    return;
  }
  window.localStorage.removeItem(USER_STORAGE_KEY);
}

export function getStoredTokens(): StoredTokens | null {
  if (!canUseStorage()) return null;
  const raw = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setStoredTokens(tokens: StoredTokens | null) {
  if (!canUseStorage()) return;
  if (tokens) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
    return;
  }
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function clearAuthSession() {
  if (!canUseStorage()) return;
  window.localStorage.removeItem(USER_STORAGE_KEY);
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  emitAuthLogout();
}
