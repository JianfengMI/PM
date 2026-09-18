export const AUTH_STORAGE_KEY = "kanban-studio-authenticated";
export const ACCOUNT_STORAGE_KEY = "kanban-studio-account";

const listeners = new Set<() => void>();
let isSessionActive = false;

export type Account = {
  username: string;
  password: string;
};

export const getStoredAccount = (): Account | null => {
  if (typeof window === "undefined") {
    return null;
  }

  const storedAccount = window.localStorage.getItem(ACCOUNT_STORAGE_KEY);
  return storedAccount ? (JSON.parse(storedAccount) as Account) : null;
};

export const hasRegisteredAccount = () => getStoredAccount() !== null;

export const isValidCredentials = (username: string, password: string) => {
  const account = getStoredAccount();
  return account?.username === username && account.password === password;
};

export const registerAccount = (username: string, password: string) => {
  if (hasRegisteredAccount()) {
    return false;
  }
  window.localStorage.setItem(
    ACCOUNT_STORAGE_KEY,
    JSON.stringify({ username, password })
  );
  listeners.forEach((listener) => listener());
  return true;
};

export const hasStoredSession = () => isSessionActive;

export const storeSession = () => {
  isSessionActive = true;
  listeners.forEach((listener) => listener());
};

export const clearSession = () => {
  isSessionActive = false;
  listeners.forEach((listener) => listener());
};

export const subscribeToSession = (listener: () => void) => {
  listeners.add(listener);
  return () => listeners.delete(listener);
};

export const getSessionSnapshot = () => hasStoredSession();

export const getServerSessionSnapshot = () => false;

export const subscribeToAccount = (listener: () => void) => {
  listeners.add(listener);
  return () => listeners.delete(listener);
};

export const getAccountSnapshot = () =>
  typeof window !== "undefined"
    ? window.localStorage.getItem(ACCOUNT_STORAGE_KEY) ?? ""
    : "";

export const getServerAccountSnapshot = () => "";
