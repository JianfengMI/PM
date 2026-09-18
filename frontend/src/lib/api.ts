import type { BoardData } from "@/lib/kanban";

type ApiCredentials = {
  username: string;
  password: string;
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
