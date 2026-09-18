"use client";

import { useState, type FormEvent } from "react";
import { sendChat, type ChatMessage } from "@/lib/api";
import type { BoardData } from "@/lib/kanban";

type ChatSidebarProps = {
  board: BoardData;
  onBoardUpdated: (board: BoardData) => void;
  onClose: () => void;
};

export const ChatSidebar = ({
  board,
  onBoardUpdated,
  onClose,
}: ChatSidebarProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || isSending) {
      return;
    }

    const userMessage: ChatMessage = { role: "user", content: trimmedQuestion };
    const previousMessages = messages;
    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setError("");
    setIsSending(true);
    try {
      const result = await sendChat(trimmedQuestion, previousMessages, board);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.response },
      ]);
      onBoardUpdated(result.board);
    } catch {
      setError("The assistant could not respond. Try again.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <aside className="flex min-h-[520px] flex-col rounded-3xl border border-[var(--stroke)] bg-white/90 p-5 shadow-[var(--shadow)] backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
            Workspace assistant
          </p>
          <h2 className="mt-2 font-display text-2xl font-semibold text-[var(--navy-dark)]">
            Ask about your board
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-full border border-[var(--stroke)] px-3 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:border-[var(--primary-blue)] hover:text-[var(--navy-dark)]"
          aria-label="Close assistant"
        >
          Close
        </button>
      </div>

      <div className="mt-5 flex-1 space-y-3 overflow-y-auto" aria-live="polite">
        {messages.length === 0 ? (
          <p className="rounded-2xl bg-[var(--surface)] px-4 py-4 text-sm leading-6 text-[var(--gray-text)]">
            Ask for a summary or request a board change.
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={
                message.role === "user"
                  ? "ml-6 rounded-2xl bg-[var(--primary-blue)] px-4 py-3 text-sm leading-6 text-white"
                  : "mr-6 rounded-2xl bg-[var(--surface)] px-4 py-3 text-sm leading-6 text-[var(--navy-dark)]"
              }
            >
              {message.content}
            </div>
          ))
        )}
      </div>

      {error ? (
        <p role="alert" className="mt-4 text-sm font-semibold text-[var(--secondary-purple)]">
          {error}
        </p>
      ) : null}
      <form onSubmit={handleSubmit} className="mt-5 space-y-3">
        <label className="sr-only" htmlFor="assistant-question">
          Your question
        </label>
        <textarea
          id="assistant-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Ask or update your board..."
          rows={3}
          disabled={isSending}
          className="w-full resize-none rounded-2xl border border-[var(--stroke)] bg-white px-3 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={isSending || !question.trim()}
          className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSending ? "Thinking..." : "Send to assistant"}
        </button>
      </form>
    </aside>
  );
};