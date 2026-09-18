import type { BoardData } from "@/lib/kanban";

type ApiCredentials = {
  username: string;
  password: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatResponse = {
  response: string;
  board: BoardData;
  board_updated: boolean;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");

const request = async <Response>(
  path: string,
  credentials: ApiCredentials,
  options?: RequestInit
): Promise<Response> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`,
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<Response>;
};

export const fetchBoard = (credentials: ApiCredentials) =>
  request<BoardData>("/api/board", credentials);

export const updateBoard = (board: BoardData, credentials: ApiCredentials) =>
  request<BoardData>("/api/board", credentials, {
    method: "PUT",
    body: JSON.stringify(board),
  });

export const sendChat = (
  question: string,
  history: ChatMessage[],
  board: BoardData
) =>
  fetch(`${API_BASE_URL}/api/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history, board }),
  }).then(async (response) => {
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    return (await response.json()) as ChatResponse;
  });
