import json
from pathlib import Path

import pytest

from backend.app.datastore import (
    DataDocument,
    JsonDataStore,
    UserRecord,
    default_document,
)


def test_missing_file_is_initialized_with_default_document(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "kanban.json"
    store = JsonDataStore(path)

    document = store.read()

    assert path.exists()
    assert document == default_document()
    assert document.users[0].board.columns[0].title == "Backlog"


def test_write_and_read_round_trip(tmp_path: Path) -> None:
    store = JsonDataStore(tmp_path / "kanban.json")
    document = store.read()
    document.users[0].board.columns[0].title = "Queued"

    store.write(document)

    assert store.read().users[0].board.columns[0].title == "Queued"


def test_malformed_json_is_rejected_without_replacement(tmp_path: Path) -> None:
    path = tmp_path / "kanban.json"
    path.write_text("{not valid json", encoding="utf-8")
    store = JsonDataStore(path)

    with pytest.raises(ValueError, match="invalid datastore"):
        store.read()

    assert path.read_text(encoding="utf-8") == "{not valid json"


def test_invalid_board_references_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "kanban.json"
    payload = default_document().model_dump(mode="json")
    payload["users"][0]["board"]["columns"][0]["cardIds"].append("missing-card")
    path.write_text(json.dumps(payload), encoding="utf-8")
    store = JsonDataStore(path)

    with pytest.raises(ValueError, match="invalid datastore"):
        store.read()


def test_duplicate_user_ids_and_usernames_are_rejected() -> None:
    document = default_document()
    duplicate_user = UserRecord(
        id=document.users[0].id,
        username="another-user",
        board=document.users[0].board,
    )
    document.users.append(duplicate_user)

    with pytest.raises(ValueError, match="user IDs must be unique"):
        DataDocument.validate_consistency(document)

    duplicate_user.id = "user-2"
    duplicate_user.username = document.users[0].username
    with pytest.raises(ValueError, match="usernames must be unique"):
        DataDocument.validate_consistency(document)


def test_write_replaces_previous_document_atomically(tmp_path: Path) -> None:
    path = tmp_path / "kanban.json"
    store = JsonDataStore(path)
    store.write(default_document())
    document = store.read()
    document.version = 2

    store.write(document)

    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 2
    assert list(tmp_path.glob("*.tmp")) == []
