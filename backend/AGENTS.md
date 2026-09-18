# Backend Guidance

## Overview

This directory contains the FastAPI backend for the Project Management MVP. The current scaffold serves a temporary static HTML page and exposes a hello-world API endpoint. Later parts of the plan will add JSON persistence, authentication, board APIs, and OpenRouter integration.

## Structure

- `app/main.py` creates the FastAPI application and defines the initial routes.
- `app/datastore.py` defines the validated JSON document models, default board, and atomic file datastore.
- `app/auth.py` provides the MVP HTTP Basic authentication dependency.
- `static/index.html` is the temporary static page served at `/` until the frontend export is integrated.
- `tests/test_main.py` contains backend tests using FastAPI's test client.

## Commands

Run these commands from the repository root:

```bash
uv sync
uv run pytest
uv run uvicorn backend.app.main:app --reload
```

The local backend listens on port `8000`. The Docker scripts publish it on host port `3000`.

The protected board routes are `GET /api/board` and `PUT /api/board`. They use HTTP Basic credentials from `KANBAN_USERNAME` and `KANBAN_PASSWORD`, defaulting to `user` and `password`. Explicit user routes are also available at `/api/users/{user_id}/board` and reject access to another user.

The API allows local development calls from the frontend at ports `3000` on `127.0.0.1` and `localhost`. Production uses same-origin requests.

The protected `POST /api/ai/test` endpoint performs the Part 8 `2+2` connectivity check through OpenRouter. Configure `OPENROUTER_API_KEY`, optionally `OPENROUTER_MODEL`, and optionally `OPENROUTER_TIMEOUT` through `.env` or the process environment.

## Conventions

- Use Python with FastAPI and type annotations.
- Manage dependencies with `uv` and keep `uv.lock` up to date.
- Keep HTTP routing separate from persistence, authentication, and provider clients as those features are added.
- Use `JsonDataStore` for JSON persistence and configure its location with `KANBAN_DATA_PATH` when needed.
- Test route behavior and error responses with focused pytest tests.
- Never commit `.env` files, API keys, or generated datastore files.