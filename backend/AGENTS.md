# Backend Guidance

## Overview

This directory contains the FastAPI backend for the Project Management MVP. The current scaffold serves a temporary static HTML page and exposes a hello-world API endpoint. Later parts of the plan will add JSON persistence, authentication, board APIs, and OpenRouter integration.

## Structure

- `app/main.py` creates the FastAPI application and defines the initial routes.
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

## Conventions

- Use Python with FastAPI and type annotations.
- Manage dependencies with `uv` and keep `uv.lock` up to date.
- Keep HTTP routing separate from persistence, authentication, and provider clients as those features are added.
- Test route behavior and error responses with focused pytest tests.
- Never commit `.env` files, API keys, or generated datastore files.