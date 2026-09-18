"use client";

import { useSyncExternalStore } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import {
  clearSession,
  getAccountSnapshot,
  getServerAccountSnapshot,
  getServerSessionSnapshot,
  getSessionSnapshot,
  storeSession,
  subscribeToAccount,
  subscribeToSession,
} from "@/lib/auth";

export default function Home() {
  const isAuthenticated = useSyncExternalStore(
    subscribeToSession,
    getSessionSnapshot,
    getServerSessionSnapshot
  );
  const accountSnapshot = useSyncExternalStore(
    subscribeToAccount,
    getAccountSnapshot,
    getServerAccountSnapshot
  );

  if (!isAuthenticated) {
    return (
      <LoginForm
        hasAccount={Boolean(accountSnapshot)}
        onLogin={() => {
          storeSession();
        }}
      />
    );
  }

  return (
    <KanbanBoard
      onLogout={() => {
        clearSession();
      }}
    />
  );
}
