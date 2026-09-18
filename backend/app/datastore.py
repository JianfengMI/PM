import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Card(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    details: str

    @field_validator("id", "title")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be empty")
        return value


class Column(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    cardIds: list[str] = Field(default_factory=list)

    @field_validator("id", "title")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be empty")
        return value


class Board(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[Column]
    cards: dict[str, Card]

    @classmethod
    def validate_consistency(cls, board: "Board") -> "Board":
        column_ids = [column.id for column in board.columns]
        if len(column_ids) != len(set(column_ids)):
            raise ValueError("column IDs must be unique")

        card_ids = list(board.cards)
        if len(card_ids) != len(set(card_ids)):
            raise ValueError("card IDs must be unique")
        if any(card_id != card.id for card_id, card in board.cards.items()):
            raise ValueError("card map keys must match card IDs")

        referenced_card_ids = [
            card_id for column in board.columns for card_id in column.cardIds
        ]
        if len(referenced_card_ids) != len(set(referenced_card_ids)):
            raise ValueError("a card may appear in only one column")
        if not set(referenced_card_ids).issubset(board.cards):
            raise ValueError("columns may reference only existing cards")
        return board


class UserRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    username: str
    board: Board

    @field_validator("id", "username")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be empty")
        return value


class DataDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(gt=0)
    users: list[UserRecord]

    @classmethod
    def validate_consistency(cls, document: "DataDocument") -> "DataDocument":
        user_ids = [user.id for user in document.users]
        usernames = [user.username for user in document.users]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("user IDs must be unique")
        if len(usernames) != len(set(usernames)):
            raise ValueError("usernames must be unique")
        for user in document.users:
            Board.validate_consistency(user.board)
        return document


def default_board() -> Board:
    return Board(
        columns=[
            Column(id="col-backlog", title="Backlog", cardIds=["card-1", "card-2"]),
            Column(id="col-discovery", title="Discovery", cardIds=["card-3"]),
            Column(
                id="col-progress",
                title="In Progress",
                cardIds=["card-4", "card-5"],
            ),
            Column(id="col-review", title="Review", cardIds=["card-6"]),
            Column(id="col-done", title="Done", cardIds=["card-7", "card-8"]),
        ],
        cards={
            "card-1": Card(
                id="card-1",
                title="Align roadmap themes",
                details="Draft quarterly themes with impact statements and metrics.",
            ),
            "card-2": Card(
                id="card-2",
                title="Gather customer signals",
                details="Review support tags, sales notes, and churn feedback.",
            ),
            "card-3": Card(
                id="card-3",
                title="Prototype analytics view",
                details="Sketch initial dashboard layout and key drill-downs.",
            ),
            "card-4": Card(
                id="card-4",
                title="Refine status language",
                details="Standardize column labels and tone across the board.",
            ),
            "card-5": Card(
                id="card-5",
                title="Design card layout",
                details="Add hierarchy and spacing for scanning dense lists.",
            ),
            "card-6": Card(
                id="card-6",
                title="QA micro-interactions",
                details="Verify hover, focus, and loading states.",
            ),
            "card-7": Card(
                id="card-7",
                title="Ship marketing page",
                details="Final copy approved and asset pack delivered.",
            ),
            "card-8": Card(
                id="card-8",
                title="Close onboarding sprint",
                details="Document release notes and share internally.",
            ),
        },
    )


def default_document() -> DataDocument:
    return DataDocument(
        version=1,
        users=[UserRecord(id="user-1", username="user", board=default_board())],
    )


class JsonDataStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(
            os.environ.get("KANBAN_DATA_PATH", "data/kanban.json")
        )

    def read(self) -> DataDocument:
        self._ensure_initialized()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            document = DataDocument.model_validate(payload)
            return DataDocument.validate_consistency(document)
        except (json.JSONDecodeError, OSError, ValueError) as error:
            raise ValueError(f"invalid datastore: {self.path}") from error

    def write(self, document: DataDocument) -> None:
        validated_document = DataDocument.validate_consistency(
            DataDocument.model_validate(document)
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(
                    validated_document.model_dump(mode="json"),
                    temporary_file,
                    indent=2,
                )
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink()

    def _ensure_initialized(self) -> None:
        if not self.path.exists():
            self.write(default_document())
