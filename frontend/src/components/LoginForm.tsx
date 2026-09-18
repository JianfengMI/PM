"use client";

import { useState, type FormEvent } from "react";
import { isValidCredentials, registerAccount } from "@/lib/auth";

type LoginFormProps = {
  hasAccount: boolean;
  onLogin: () => void;
};

export const LoginForm = ({ hasAccount, onLogin }: LoginFormProps) => {
  const [isCreatingAccount, setIsCreatingAccount] = useState(!hasAccount);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!isCreatingAccount) {
      if (!isValidCredentials(username, password)) {
        setError("Enter the correct username and password.");
        return;
      }
      setError("");
      onLogin();
      return;
    }

    if (password !== confirmation) {
      setError("Passwords do not match.");
      return;
    }
    if (!registerAccount(username.trim(), password)) {
      setError("An account is already registered in this browser.");
      return;
    }
    setError("");
    setUsername("");
    setPassword("");
    setConfirmation("");
    setIsCreatingAccount(false);
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="w-full max-w-md rounded-[32px] border border-[var(--stroke)] bg-white/85 p-8 shadow-[var(--shadow)] backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          Single Board Kanban
        </p>
        <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
          Kanban Studio
        </h1>
        <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
          {!isCreatingAccount
            ? "Sign in to keep your project moving."
            : "Create an account to start your project board."}
        </p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <label className="block text-sm font-semibold text-[var(--navy-dark)]">
            Username
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-3 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              autoComplete="username"
              required
            />
          </label>
          <label className="block text-sm font-semibold text-[var(--navy-dark)]">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-3 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              autoComplete="current-password"
              required
            />
          </label>
          {isCreatingAccount ? (
            <label className="block text-sm font-semibold text-[var(--navy-dark)]">
              Confirm password
              <input
                type="password"
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-3 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                autoComplete="new-password"
                required
              />
            </label>
          ) : null}
          {error ? (
            <p role="alert" className="text-sm font-semibold text-[var(--secondary-purple)]">
              {error}
            </p>
          ) : null}
          <button
            type="submit"
            className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110"
          >
            {isCreatingAccount ? "Create account" : "Sign in"}
          </button>
          {hasAccount ? (
            <button
              type="button"
              onClick={() => {
                setError("");
                setIsCreatingAccount((previous) => !previous);
              }}
              className="w-full rounded-full border border-[var(--stroke)] px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:border-[var(--primary-blue)] hover:text-[var(--navy-dark)]"
            >
              {isCreatingAccount ? "Back to sign in" : "Create an account instead"}
            </button>
          ) : null}
        </form>
      </section>
    </main>
  );
};
