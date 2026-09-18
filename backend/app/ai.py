import copy
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.datastore import Board, Card, Column


MAX_HISTORY_MESSAGES = 20
MAX_MESSAGE_LENGTH = 4000


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)


class AIAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["create_card", "update_card", "move_card", "delete_card", "rename_column"]
    card_id: str | None = None
    column_id: str | None = None
    title: str | None = None
    details: str | None = None
    index: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_action_fields(self) -> "AIAction":
        required_by_action = {
            "create_card": ("column_id", "title"),
            "update_card": ("card_id",),
            "move_card": ("card_id", "column_id"),
            "delete_card": ("card_id",),
            "rename_column": ("column_id", "title"),
        }
        missing = [
            field
            for field in required_by_action[self.action]
            if getattr(self, field) is None
        ]
        if missing:
            raise ValueError(f"missing fields for {self.action}: {', '.join(missing)}")
        if self.title is not None and not self.title.strip():
            raise ValueError("title must not be empty")
        return self


class AIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    actions: list[AIAction] = Field(default_factory=list, max_length=20)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    board: Board
    history: list[ChatMessage] = Field(default_factory=list, max_length=MAX_HISTORY_MESSAGES)

    @model_validator(mode="after")
    def validate_question(self) -> "ChatRequest":
        if not self.question.strip():
            raise ValueError("question must not be empty")
        return self


class ChatResponse(BaseModel):
    response: str
    board: Board
    board_updated: bool


def build_chat_messages(board: Board, request: ChatRequest) -> list[dict[str, str]]:
    board_json = json.dumps(board.model_dump(mode="json"), separators=(",", ":"))
    history_json = json.dumps(
        [message.model_dump(mode="json") for message in request.history],
        separators=(",", ":"),
    )
    return [
        {
            "role": "system",
            "content": (
                "You are a project management assistant. Return only the requested JSON schema. "
                "Use actions only when the user asks to change the board. "
                "Valid actions are create_card, update_card, move_card, delete_card, and rename_column."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Current board JSON: {board_json}\n"
                f"Conversation history JSON: {history_json}\n"
                f"User question: {request.question}"
            ),
        },
    ]


def apply_actions(board: Board, actions: list[AIAction]) -> Board:
    next_board = Board.model_validate(copy.deepcopy(board.model_dump(mode="json")))
    columns_by_id = {column.id: column for column in next_board.columns}

    for action in actions:
        if action.action == "create_card":
            assert action.column_id is not None
            assert action.title is not None
            column = columns_by_id.get(action.column_id)
            if column is None:
                raise ValueError(f"column not found: {action.column_id}")
            card_id = _new_card_id(next_board)
            next_board.cards[card_id] = Card(
                id=card_id,
                title=action.title,
                details=action.details or "No details yet.",
            )
            _insert_card(column, card_id, action.index)
        elif action.action == "update_card":
            assert action.card_id is not None
            card = next_board.cards.get(action.card_id)
            if card is None:
                raise ValueError(f"card not found: {action.card_id}")
            if action.title is not None:
                card.title = action.title
            if action.details is not None:
                card.details = action.details
        elif action.action == "move_card":
            assert action.card_id is not None
            assert action.column_id is not None
            if action.card_id not in next_board.cards:
                raise ValueError(f"card not found: {action.card_id}")
            target = columns_by_id.get(action.column_id)
            if target is None:
                raise ValueError(f"column not found: {action.column_id}")
            for column in next_board.columns:
                if action.card_id in column.cardIds:
                    column.cardIds.remove(action.card_id)
            _insert_card(target, action.card_id, action.index)
        elif action.action == "delete_card":
            assert action.card_id is not None
            if action.card_id not in next_board.cards:
                raise ValueError(f"card not found: {action.card_id}")
            del next_board.cards[action.card_id]
            for column in next_board.columns:
                if action.card_id in column.cardIds:
                    column.cardIds.remove(action.card_id)
        elif action.action == "rename_column":
            assert action.column_id is not None
            assert action.title is not None
            column = columns_by_id.get(action.column_id)
            if column is None:
                raise ValueError(f"column not found: {action.column_id}")
            column.title = action.title

    return Board.validate_consistency(next_board)


def _insert_card(column: Column, card_id: str, index: int | None) -> None:
    if index is None or index >= len(column.cardIds):
        column.cardIds.append(card_id)
    else:
        column.cardIds.insert(index, card_id)


def _new_card_id(board: Board) -> str:
    index = 1
    while f"ai-card-{index}" in board.cards:
        index += 1
    return f"ai-card-{index}"
