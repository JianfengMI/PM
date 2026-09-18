# JSON Datastore Proposal

## Scope

The MVP uses one JSON file for application data. The file is created on first use and supports multiple users and one Kanban board per user. The frontend currently collects the first account locally; backend registration and persistence will use the stable user ID `user-1` for that account.

The datastore path is configured by `KANBAN_DATA_PATH` and defaults to `data/kanban.json` relative to the application working directory.

## Document shape

```json
{
  "version": 1,
  "users": [
    {
      "id": "user-1",
      "username": "user",
      "board": {
        "columns": [
          {
            "id": "col-backlog",
            "title": "Backlog",
            "cardIds": ["card-1"]
          }
        ],
        "cards": {
          "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics."
          }
        }
      }
    }
  ]
}
```

## Rules

- `version` is a required positive integer used for future migrations.
- Each user has a unique stable `id` and unique `username`.
- Each user has exactly one `board`.
- A board has ordered `columns`; column order is the display order.
- Column IDs and card IDs are unique within the document.
- Every ID in `column.cardIds` must exist in that user's `cards` map.
- Each card appears in at most one column and must have matching `id`, `title`, and `details` values.
- Column titles, card titles, and card details are strings. Empty titles are rejected; details may be empty.
- The API validates the complete board before writing it.
- The datastore layer writes a temporary file in the same directory, flushes it, and replaces the original file so a failed write does not partially update the active document.
- Missing parent directories and the initial datastore file are created automatically.
- Malformed JSON or invalid schema data is reported as a server error and does not get silently replaced.

## Persistence behavior

Reads load and validate the complete document. Writes validate the proposed complete document, serialize it as UTF-8 JSON, and atomically replace the existing file. The backend owns all writes; the frontend never accesses the file directly.

The initial board is copied from the current frontend demo data when a user's board is first created. Future users receive their own board and cannot access another user's board through the API.

## Approval gate

Implementation of the datastore and board API should begin only after approval of this document. Please confirm the document shape and persistence rules, or specify changes before Part 6 begins.
