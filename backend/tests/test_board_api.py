import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def auth() -> tuple[str, str]:
    return ("user", "password")


def test_board_requires_authentication(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))

    response = client.get("/api/board")

    assert response.status_code == 401
    assert "www-authenticate" not in response.headers


def test_board_is_initialized_and_read_for_authenticated_user(
    monkeypatch, tmp_path: Path
) -> None:
    path = tmp_path / "nested" / "kanban.json"
    monkeypatch.setenv("KANBAN_DATA_PATH", str(path))

    response = client.get("/api/board", auth=auth())

    assert response.status_code == 200
    assert response.json()["columns"][0]["title"] == "Backlog"
    assert path.exists()


def test_board_update_persists_and_can_be_loaded_again(
    monkeypatch, tmp_path: Path
) -> None:
    path = tmp_path / "kanban.json"
    monkeypatch.setenv("KANBAN_DATA_PATH", str(path))
    board = client.get("/api/board", auth=auth()).json()
    board["columns"][0]["title"] = "Queued"

    update_response = client.put("/api/board", json=board, auth=auth())
    read_response = client.get("/api/users/user-1/board", auth=auth())

    assert update_response.status_code == 200
    assert read_response.status_code == 200
    assert read_response.json()["columns"][0]["title"] == "Queued"
    assert json.loads(path.read_text(encoding="utf-8"))["users"][0]["board"]["columns"][0]["title"] == "Queued"


def test_board_update_supports_card_and_column_mutations(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))
    board = client.get("/api/board", auth=auth()).json()
    board["columns"][0]["title"] = "Ready"
    board["cards"]["card-1"]["title"] = "Updated roadmap"
    board["cards"]["card-new"] = {
        "id": "card-new",
        "title": "New card",
        "details": "Created through the API.",
    }
    board["columns"][0]["cardIds"].remove("card-1")
    board["columns"][1]["cardIds"].append("card-1")
    board["columns"][0]["cardIds"].append("card-new")

    response = client.put("/api/board", json=board, auth=auth())
    saved_board = client.get("/api/board", auth=auth()).json()

    assert response.status_code == 200
    assert saved_board["columns"][0]["title"] == "Ready"
    assert saved_board["cards"]["card-1"]["title"] == "Updated roadmap"
    assert saved_board["columns"][1]["cardIds"][-1] == "card-1"
    assert saved_board["columns"][0]["cardIds"][-1] == "card-new"


def test_invalid_board_is_rejected_without_mutating_saved_board(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))
    original = client.get("/api/board", auth=auth()).json()
    invalid = original.copy()
    invalid["columns"] = [
        {"id": "col-a", "title": "A", "cardIds": ["card-1", "card-1"]}
    ]
    invalid["cards"] = {"card-1": original["cards"]["card-1"]}

    response = client.put("/api/board", json=invalid, auth=auth())

    assert response.status_code == 422
    assert client.get("/api/board", auth=auth()).json() == original


def test_user_cannot_access_another_users_board(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))

    response = client.get("/api/users/user-2/board", auth=auth())

    assert response.status_code == 403


def test_invalid_credentials_are_rejected(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))

    response = client.get("/api/board", auth=("user", "wrong"))

    assert response.status_code == 401
