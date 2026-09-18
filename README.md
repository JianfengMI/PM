# Project Management MVP

A local Kanban project management app with account sign-up, persistent board editing, and an AI assistant sidebar.

## Run With Docker

Start Docker Desktop, then run from the repository root.

Windows PowerShell:

```powershell
.\scripts\start.ps1
```

Windows Command Prompt:

```bat
scripts\start.bat
```

macOS or Linux:

```bash
./scripts/start.sh
```

Open http://127.0.0.1:3000. Stop the app with the matching `stop` script.

The first visit shows account creation. After signing in, the Kanban board and AI assistant are available. The AI sidebar does not require a separate login.

## Configuration

Create a root `.env` file for AI features:

```env
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openai/gpt-oss-120b
```

The JSON datastore defaults to `data/kanban.json`. Override it with `KANBAN_DATA_PATH` when needed.

## Development

Backend commands run from the repository root:

```bash
uv sync
uv run uvicorn backend.app.main:app --reload
uv run pytest
```

Frontend commands run from `frontend/`:

```bash
npm install
npm run dev
npm run lint
npm run test:unit
npm run test:e2e
npm run build
```

For local frontend/backend development, the frontend uses FastAPI at `http://127.0.0.1:8000` and the frontend development server uses port `3000`.

## Tests

The standard backend suite uses mocked AI responses and does not require a live provider call. Run the optional live checks with a configured key:

```bash
RUN_LIVE_AI_TESTS=1 uv run pytest -m live
```

On PowerShell:

```powershell
$env:RUN_LIVE_AI_TESTS = "1"; uv run pytest -m live
```
