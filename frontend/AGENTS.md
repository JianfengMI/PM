# Frontend Guidance

## Overview

This directory contains the Next.js frontend for the Project Management MVP. The current app is a client-side Kanban demo. It will later be statically exported and served by the FastAPI backend.

## Structure

- `src/app/` contains the Next.js app entry points, global styles, and page layout.
- `src/components/` contains the Kanban UI components.
  - `KanbanBoard.tsx` owns the board state and drag-and-drop interactions.
  - `KanbanColumn.tsx` renders a column, its cards, rename field, and add-card form.
  - `KanbanCard.tsx` renders a sortable card and its remove action.
  - `KanbanCardPreview.tsx` renders the drag overlay preview.
  - `NewCardForm.tsx` handles local new-card form state.
- `src/lib/kanban.ts` defines `Card`, `Column`, and `BoardData`, provides the demo data, and contains card movement and ID helpers.
- `src/lib/api.ts` contains the authenticated board API client used by the signed-in page.
- `src/**/*.test.{ts,tsx}` contains Vitest unit and component tests.
- `tests/` contains Playwright browser tests.
- `public/` contains static frontend assets.

## Commands

Run these commands from `frontend/`:

```bash
npm install
npm run dev
npm run build
npm run lint
npm run test:unit
npm run test:e2e
npm run test:all
```

The development server and Playwright tests use port `3000`.

In development, board API requests target FastAPI at `http://127.0.0.1:8000`. Set `NEXT_PUBLIC_API_BASE_URL` to override this. Production static exports use same-origin `/api` requests because FastAPI serves the frontend and API together.

## Conventions

- Use TypeScript and existing React/Next.js patterns.
- Use the `@/` alias for imports from `src/`.
- Preserve the existing visual language and CSS variables in `src/app/globals.css`.
- Keep board state transitions in the owning board or shared `src/lib/kanban.ts` helpers rather than duplicating movement logic in presentational components.
- Preserve accessible labels and the existing `data-testid` selectors when changing board behavior.
- Keep components focused and avoid adding state management libraries unless the project requirements justify them.
- Add focused unit tests for state and helper changes and Playwright coverage for user-visible workflows.

## Testing Notes

Vitest runs in `jsdom` with `src/test/setup.ts` and includes tests under `src/`. Playwright starts the Next.js development server automatically using `playwright.config.ts`. The current demo tests cover rendering five columns, renaming a column, adding and removing a card, and moving a card between columns.

The API client tests mock `fetch`. Browser tests should use the documented local backend/container so board reads and writes exercise the real API.
