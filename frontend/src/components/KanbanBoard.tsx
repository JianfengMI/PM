"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { ChatSidebar } from "@/components/ChatSidebar";
import {
  createId,
  loadAccountBoard,
  moveCard,
  saveAccountBoard,
  type BoardData,
} from "@/lib/kanban";
import { fetchBoard, updateBoard } from "@/lib/api";
import type { Account } from "@/lib/auth";

type KanbanBoardProps = {
  account?: Account;
  onLogout?: () => void;
};

export const KanbanBoard = ({ account, onLogout = () => {} }: KanbanBoardProps) => {
  const [board, setBoard] = useState<BoardData>(() =>
    account ? loadAccountBoard(account.username) : loadAccountBoard("default")
  );
  const [isLoading, setIsLoading] = useState(Boolean(account));
  const [error, setError] = useState("");
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);

  useEffect(() => {
    if (!account) {
      return;
    }

    let isCurrent = true;
    const credentials = {
      username: account.username,
      password: account.password,
    };
    fetchBoard(credentials)
      .then((nextBoard) => {
        if (isCurrent) {
          setBoard(nextBoard);
          saveAccountBoard(account.username, nextBoard);
          setError("");
        }
      })
      .catch(() => {
        if (isCurrent) {
          setBoard(loadAccountBoard(account.username));
          setError("Unable to load your board. Check that the backend is running.");
        }
      })
      .finally(() => {
        if (isCurrent) {
          setIsLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [account]);

  const applyBoard = (nextBoard: BoardData) => {
    setBoard(nextBoard);
    if (account) {
      saveAccountBoard(account.username, nextBoard);
    }
    if (account) {
      updateBoard(nextBoard, account).catch(() => {
        setError("Unable to save your latest board change.");
      });
    }
  };

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  const cardsById = useMemo(() => board.cards, [board.cards]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    if (!over || active.id === over.id) {
      return;
    }

    const nextBoard = {
      ...board,
      columns: moveCard(board.columns, active.id as string, over.id as string),
    };
    applyBoard(nextBoard);
  };

  const handleRenameColumn = (columnId: string, title: string) => {
    applyBoard({
      ...board,
      columns: board.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    });
  };

  const handleAddCard = (columnId: string, title: string, details: string) => {
    const id = createId("card");
    applyBoard({
      ...board,
      cards: {
        ...board.cards,
        [id]: { id, title, details: details || "No details yet." },
      },
      columns: board.columns.map((column) =>
        column.id === columnId
          ? { ...column, cardIds: [...column.cardIds, id] }
          : column
      ),
    });
  };

  const handleDeleteCard = (columnId: string, cardId: string) => {
    applyBoard({
      ...board,
      cards: Object.fromEntries(
        Object.entries(board.cards).filter(([id]) => id !== cardId)
      ),
      columns: board.columns.map((column) =>
        column.id === columnId
          ? {
              ...column,
              cardIds: column.cardIds.filter((id) => id !== cardId),
            }
          : column
      ),
    });
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  const handleLogout = async () => {
    if (account) {
      try {
        await updateBoard(board, account);
        saveAccountBoard(account.username, board);
      } catch {
        saveAccountBoard(account.username, board);
        setError("Unable to save your latest board change.");
      }
    }
    onLogout();
  };

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                  Focus
                </p>
                <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                  One board. Five columns. Zero clutter.
                </p>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:border-[var(--primary-blue)] hover:text-[var(--navy-dark)]"
              >
                Log out
              </button>
              {account ? (
                <button
                  type="button"
                  onClick={() => setIsChatOpen((open) => !open)}
                  className="rounded-full bg-[var(--primary-blue)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110"
                  aria-expanded={isChatOpen}
                >
                  {isChatOpen ? "Hide assistant" : "Open assistant"}
                </button>
              ) : null}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
          {isLoading ? (
            <p className="text-sm font-semibold text-[var(--gray-text)]">Loading board...</p>
          ) : null}
          {error ? (
            <p role="alert" className="text-sm font-semibold text-[var(--secondary-purple)]">
              {error}
            </p>
          ) : null}
        </header>

        <div className={isChatOpen && account ? "grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]" : ""}>
          <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <section className="grid gap-6 lg:grid-cols-5">
              {board.columns.map((column) => (
                <KanbanColumn
                  key={column.id}
                  column={column}
                  cards={column.cardIds.map((cardId) => board.cards[cardId])}
                  onRename={handleRenameColumn}
                  onAddCard={handleAddCard}
                  onDeleteCard={handleDeleteCard}
                />
              ))}
            </section>
            <DragOverlay>
              {activeCard ? (
                <div className="w-[260px]">
                  <KanbanCardPreview card={activeCard} />
                </div>
              ) : null}
            </DragOverlay>
          </DndContext>
          {isChatOpen && account ? (
            <ChatSidebar
              board={board}
              onBoardUpdated={(nextBoard) => {
                setBoard(nextBoard);
                setError("");
              }}
              onClose={() => setIsChatOpen(false)}
            />
          ) : null}
        </div>
      </main>
    </div>
  );
};
