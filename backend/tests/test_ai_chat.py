from pathlib import Path
import os

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app, get_openrouter_client
from backend.app.datastore import default_board


client = TestClient(app)


def auth() -> tuple[str, str]:
    return ("user", "password")


def board_payload() -> dict:
    return default_board().model_dump(mode="json")


def test_chat_sends_board_question_and_history_to_ai(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))
    captured: dict[str, object] = {}
    current_board = board_payload()
    current_board["columns"][0]["title"] = "My custom backlog"

    class FakeClient:
        def complete_json(self, messages, response_schema):
            captured["messages"] = messages
            captured["schema"] = response_schema
            return {"response": "Your board is ready.", "actions": []}

    app.dependency_overrides[get_openrouter_client] = lambda: FakeClient()
    try:
        response = client.post(
            "/api/ai/chat",
            auth=auth(),
            json={
                "question": "What should I do next?",
                "board": current_board,
                "history": [{"role": "user", "content": "Hello"}],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["board_updated"] is False
    assert response.json()["board"]["columns"][0]["title"] == "My custom backlog"
    messages = captured["messages"]
    assert "Current board JSON:" in messages[1]["content"]
    assert "What should I do next?" in messages[1]["content"]
    assert "Hello" in messages[1]["content"]
    assert "actions" in captured["schema"]["properties"]


def test_chat_does_not_require_authentication(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))

    class FakeClient:
        def complete_json(self, messages, response_schema):
            return {"response": "No login needed.", "actions": []}

    app.dependency_overrides[get_openrouter_client] = lambda: FakeClient()
    try:
        response = client.post(
            "/api/ai/chat", json={"question": "Hello", "board": board_payload()}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["response"] == "No login needed."


def test_chat_applies_multiple_actions_atomically(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))

    class FakeClient:
        def complete_json(self, messages, response_schema):
            return {
                "response": "I created and moved the follow-up.",
                "actions": [
                    {
                        "action": "create_card",
                        "column_id": "col-backlog",
                        "title": "Follow up",
                        "details": "Created by the assistant.",
                    },
                    {
                        "action": "rename_column",
                        "column_id": "col-backlog",
                        "title": "Next up",
                    },
                    {
                        "action": "move_card",
                        "card_id": "card-1",
                        "column_id": "col-review",
                    },
                ],
            }

    app.dependency_overrides[get_openrouter_client] = lambda: FakeClient()
    try:
        response = client.post(
            "/api/ai/chat",
            auth=auth(),
            json={
                "question": "Create a follow-up and move card 1 to review.",
                "board": board_payload(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["board_updated"] is True
    assert payload["board"]["columns"][0]["title"] == "Next up"
    assert "card-1" not in payload["board"]["columns"][0]["cardIds"]
    assert payload["board"]["columns"][3]["cardIds"][-1] == "card-1"
    assert "ai-card-1" in payload["board"]["cards"]


def test_rejected_action_does_not_mutate_the_datastore(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "kanban.json"
    monkeypatch.setenv("KANBAN_DATA_PATH", str(path))
    original = client.get("/api/board", auth=auth()).json()

    class FakeClient:
        def complete_json(self, messages, response_schema):
            return {
                "response": "I will move that card.",
                "actions": [
                    {
                        "action": "move_card",
                        "card_id": "missing-card",
                        "column_id": "col-review",
                    }
                ],
            }

    app.dependency_overrides[get_openrouter_client] = lambda: FakeClient()
    try:
        response = client.post(
            "/api/ai/chat",
            auth=auth(),
            json={"question": "Move the missing card.", "board": board_payload()},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert client.get("/api/board", auth=auth()).json() == original


def test_history_limit_is_enforced(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KANBAN_DATA_PATH", str(tmp_path / "kanban.json"))
    history = [{"role": "user", "content": "hello"}] * 21

    response = client.post(
        "/api/ai/chat",
        auth=auth(),
        json={"question": "Hello", "board": board_payload(), "history": history},
    )

    assert response.status_code == 422


@pytest.mark.live
def test_live_structured_chat() -> None:
    if os.getenv("RUN_LIVE_AI_TESTS") != "1":
        pytest.skip("set RUN_LIVE_AI_TESTS=1 to call OpenRouter")

    response = client.post(
        "/api/ai/chat",
        auth=auth(),
        json={
            "question": "Answer 2+2 briefly and do not change the board.",
            "board": board_payload(),
        },
    )

    assert response.status_code == 200
    assert response.json()["response"]
