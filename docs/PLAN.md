# Project Plan

## Decisions and constraints

- Preserve the existing frontend behavior and visual design while integrating new capabilities.
- Use Next.js for the frontend and FastAPI for the backend.
- Package the application into one Docker container, with FastAPI serving the statically built Next.js site at `/`.
- Use `uv` for Python dependency management.
- Use a JSON file-based datastore. Create the datastore automatically when it does not exist.
- Require first-use account registration in the frontend demo, then sign in with the registered credentials; keep the data model ready for multiple users.
- Support one Kanban board per signed-in user.
- Require authentication for the AI chat and all board API operations.
- Use OpenRouter with model `openai/gpt-oss-120b` for AI features.
- Keep the app runnable locally through start and stop scripts for Windows, macOS, and Linux.
- Use the existing project color scheme and avoid unrelated frontend redesign.
- Do not add features beyond the steps below without user approval.

## Approval gate

- [ ] User reviews and approves this plan before implementation begins.
- [ ] Resolve any requested changes to scope, API shape, persistence format, ports, or test coverage.

## Part 1: Planning and frontend documentation

### Checklist

- [x] Record the agreed architecture, persistence choice, authentication scope, and AI model in this document.
- [x] Inspect the existing frontend components, state flow, scripts, and tests.
- [x] Create `frontend/AGENTS.md` describing the existing frontend structure, commands, conventions, and test setup.
- [x] Confirm the frontend documentation matches the code without changing frontend behavior.

### Tests and checks

- Verify the documented commands run from the expected directories.
- Run the existing frontend lint, unit test, and build commands where available.

### Success criteria

- The user has approved this plan.
- `frontend/AGENTS.md` accurately describes the current frontend.
- Existing frontend checks pass before infrastructure changes begin.

## Part 2: Docker and backend scaffolding

### Checklist

- [x] Add the Dockerfile and required Docker configuration.
- [x] Add the FastAPI application under `backend/` with a health or example endpoint.
- [x] Configure FastAPI to serve a minimal static example when the frontend build is not yet integrated.
- [x] Add Windows, macOS, and Linux start scripts under `scripts/`.
- [x] Define one documented local port and pass configuration through environment variables where appropriate.
- [x] Add backend dependency and test configuration using `uv`.
- [x] Keep secrets out of source control and load `OPENROUTER_API_KEY` from the project-root `.env` when AI work begins.

### Tests and checks

- [x] Backend unit test for the example endpoint.
- [ ] Build the Docker image successfully. Blocked locally because the Docker daemon is not running.
- [x] Start the backend locally and verify the example HTML at `/`.
- [x] Verify the example API call returns the documented response.
- [ ] Verify each platform script has the expected start/stop behavior; Windows scripts are present but Docker daemon availability blocked execution.

### Success criteria

- [ ] A clean checkout can build and run the container locally once Docker is available.
- [x] `/` serves the example page and the example API endpoint responds successfully.
- [x] Stopping the locally started application does not leave an unmanaged process.

## Part 3: Serve the existing frontend

### Checklist

- [x] Configure Next.js for a static export compatible with FastAPI static serving.
- [x] Build the existing frontend as a production export for the backend image.
- [x] Serve the exported frontend at `/` and preserve its existing routes and assets.
- [x] Keep the current Kanban interactions and styling unchanged.
- [x] Retain integration coverage for the built site's main board workflow.

### Tests and checks

- [x] Run frontend lint, unit tests, and production build.
- [x] Run backend/static-serving tests.
- [x] Use browser integration tests to load `/`, view the board, create a card, and move a card.
- [ ] Verify static assets load from the container rather than the Next.js development server; Docker daemon is unavailable locally.

### Success criteria

- [ ] The container serves the existing Kanban demo at `/` once the Docker image is built.
- [x] Existing frontend behavior remains intact.
- [x] Production build and frontend integration tests pass.

## Part 4: Fake sign-in and sign-out

### Checklist

- [x] Add a registration-first view and sign-in using the newly registered credentials.
- [x] Protect the Kanban view until authentication succeeds.
- [x] Add a logout action that clears the local authentication state.
- [x] Define the MVP session mechanism and keep it compatible with the backend API.
- [x] Show useful validation for invalid credentials without exposing secrets.

### Tests and checks

- [x] Unit-test valid and invalid credential handling through the login behavior.
- [x] Browser-test gating before login, successful login, logout, and failed login.
- [x] Verify a new browser session cannot view protected content without signing in.

### Success criteria

- [x] Unauthenticated users see the login experience.
- [x] Only the registered account credentials grant access.
- [x] Logout reliably returns the user to the login experience.

## Part 5: JSON datastore modeling

### Checklist

- [x] Propose the JSON schema for users, boards, columns, cards, ordering, and metadata needed by the UI.
- [x] Define stable identifiers and validation rules for each entity.
- [x] Define the datastore file location and initialization behavior.
- [x] Define how writes are persisted and how malformed or missing data is handled.
- [x] Document the schema and persistence approach in `docs/DATASTORE.md`.
- [x] Get user sign-off on the schema before implementing board persistence.

### Tests and checks

- [x] Validate representative empty, default, and populated board documents.
- [x] Test initialization when the file does not exist.
- [x] Test persistence and reload of representative board changes.
- [x] Test rejection of invalid schema data without corrupting the datastore.

### Success criteria

- [x] The schema is documented and approved before Part 6.
- [x] The JSON file can represent the MVP board and multiple future users.
- [x] Initialization, read, write, and validation behavior are specified by tests.

## Part 6: Backend board API

### Checklist

- [ ] Implement authenticated read access for the current user's board.
- [ ] Implement authenticated create/update operations needed by the board UI.
- [ ] Enforce the one-board-per-user constraint.
- [ ] Validate cards, columns, ordering, and renamed column values at the API boundary.
- [ ] Ensure the JSON datastore is created on first use.
- [ ] Prevent one user from reading or changing another user's board.
- [ ] Return clear HTTP status codes and error payloads.

### Tests and checks

- Unit-test datastore operations and API handlers.
- Test first-run datastore creation.
- Test board reads, card creation/editing/moving, column renaming, and persistence.
- Test unauthenticated requests, invalid payloads, missing boards, and cross-user access.
- Run the backend test suite with coverage appropriate to the API surface.

### Success criteria

- Authenticated API calls can fully support the existing Kanban interactions.
- Changes survive a backend restart.
- Unauthorized and invalid operations are rejected consistently.

## Part 7: Connect the frontend to the backend

### Checklist

- [ ] Replace frontend-only board state with API-backed loading and updates.
- [ ] Preserve existing board layout and interactions.
- [ ] Add loading, saving, and error states without disrupting normal use.
- [ ] Refresh or reconcile board state after successful mutations.
- [ ] Ensure authentication state is sent with protected API requests.
- [ ] Keep the UI usable when the backend is temporarily unavailable.

### Tests and checks

- Frontend unit-test API client and board state transitions.
- Integration-test login, initial board load, card operations, column renaming, reload, and persistence.
- Test API failures and recovery.
- Run frontend lint, unit tests, production build, backend tests, and container integration tests.

### Success criteria

- The board is persistent across browser reloads and application restarts.
- The existing UI can perform all supported board operations through the backend.
- Error and loading states are covered by tests.

## Part 8: OpenRouter connectivity

### Checklist

- [ ] Add a small backend AI client isolated from HTTP handlers and board mutation logic.
- [ ] Load `OPENROUTER_API_KEY` from environment configuration.
- [ ] Configure the agreed model and OpenRouter request format.
- [ ] Add a development/test connectivity operation for the simple `2+2` prompt.
- [ ] Keep external AI tests opt-in so the normal test suite does not require a live key.
- [ ] Define timeout and error behavior for unavailable or invalid AI responses.

### Tests and checks

- Unit-test request construction with a mocked OpenRouter response.
- Test missing-key and provider-error handling.
- Run the live `2+2` connectivity check when a valid key is available.

### Success criteria

- The backend can make a verified OpenRouter request using the configured model.
- Failures are reported clearly and do not crash unrelated board operations.

## Part 9: Structured AI board operations

### Checklist

- [ ] Define the structured response schema for assistant text and an optional board update.
- [ ] Send the current user's board JSON, question, and conversation history on every AI request.
- [ ] Define allowed board operations and validation rules for AI-proposed changes.
- [ ] Validate structured output before applying any update.
- [ ] Apply accepted changes atomically through the same persistence rules as normal API updates.
- [ ] Return the assistant response and the resulting board state or update indicator.
- [ ] Define behavior for malformed, ambiguous, or rejected AI updates.

### Tests and checks

- Unit-test prompt/request construction, structured parsing, and schema validation.
- Test responses with no board update, one update, and multiple updates.
- Test invalid card IDs, columns, ordering, and unauthorized user references.
- Test conversation history ordering and size limits.
- Test that rejected AI output cannot partially mutate the datastore.
- Use mocked provider responses for the standard suite and a live check only when explicitly enabled.

### Success criteria

- Every AI request includes the required board, question, and history context.
- Only validated structured changes can modify the current user's board.
- A failed AI request leaves the board unchanged.

## Part 10: AI chat sidebar

### Checklist

- [ ] Add the sidebar chat widget while preserving the existing board design.
- [ ] Support composing, submitting, and displaying a conversation history.
- [ ] Require authentication before chat requests are sent.
- [ ] Show loading, provider error, validation error, and empty states.
- [ ] Apply accepted AI board updates and refresh the board automatically.
- [ ] Prevent duplicate submissions while a request is in progress.
- [ ] Add accessible labels, keyboard interaction, and responsive behavior.

### Tests and checks

- Component-test chat rendering, submission, loading, errors, and structured responses.
- Browser-test authenticated chat, an assistant-only response, and a response that updates the board.
- Verify the board visibly refreshes after an AI update.
- Verify unauthenticated users cannot use the chat endpoint or UI.
- Run the complete frontend, backend, and container test suites.

### Success criteria

- Signed-in users can chat with the AI from the sidebar.
- AI-created, edited, or moved cards appear in the board without a manual reload.
- Authentication, validation, error handling, and responsive behavior are tested.

## Final verification

- [ ] Run all documented lint, unit, integration, build, and container checks.
- [ ] Verify the clean-start workflow from the documented scripts.
- [ ] Verify no secrets, generated databases, or build artifacts are committed.
- [ ] Update the README and relevant docs with setup, test, configuration, and troubleshooting instructions.
- [ ] Report any remaining limitations or externally dependent checks.