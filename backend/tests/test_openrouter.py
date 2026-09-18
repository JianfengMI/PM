import os
from collections.abc import Callable

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app, get_openrouter_client
from backend.app.openrouter import (
    MissingOpenRouterKey,
    OpenRouterClient,
    OpenRouterError,
)


client = TestClient(app)


def auth() -> tuple[str, str]:
    return ("user", "password")


def mock_transport(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def test_client_builds_openrouter_request() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = request.read()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "4"}}]},
        )

    result = OpenRouterClient(
        api_key="test-key",
        model="openai/gpt-oss-120b",
        transport=mock_transport(handler),
    ).complete("What is 2+2? Answer with only the number.")

    assert result == "4"
    assert captured["method"] == "POST"
    assert captured["url"] == OpenRouterClient.endpoint
    assert captured["authorization"] == "Bearer test-key"
    assert b'"model":"openai/gpt-oss-120b"' in captured["payload"]  # type: ignore[operator]
    assert b'"role":"user"' in captured["payload"]  # type: ignore[operator]


def test_client_adds_structured_response_format() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = request.read()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"response":"4","actions":[]}'}}]},
        )

    result = OpenRouterClient(api_key="test-key", transport=mock_transport(handler)).complete_json(
        [{"role": "user", "content": "Return JSON."}],
        {"type": "object", "properties": {"response": {"type": "string"}}},
    )

    assert result == {"response": "4", "actions": []}
    assert b'"response_format"' in captured["payload"]  # type: ignore[operator]
    assert b'"json_schema"' in captured["payload"]  # type: ignore[operator]


def test_missing_api_key_is_reported() -> None:
    with pytest.raises(MissingOpenRouterKey, match="OPENROUTER_API_KEY"):
        OpenRouterClient(api_key="").complete("2+2")


def test_provider_error_is_reported() -> None:
    transport = mock_transport(lambda request: httpx.Response(500, text="provider error"))

    with pytest.raises(OpenRouterError, match="request failed"):
        OpenRouterClient(api_key="test-key", transport=transport).complete("2+2")


def test_invalid_provider_response_is_reported() -> None:
    transport = mock_transport(lambda request: httpx.Response(200, json={"choices": []}))

    with pytest.raises(OpenRouterError, match="invalid response"):
        OpenRouterClient(api_key="test-key", transport=transport).complete("2+2")


def test_timeout_is_reported() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    with pytest.raises(OpenRouterError, match="timed out"):
        OpenRouterClient(
            api_key="test-key", transport=mock_transport(handler)
        ).complete("2+2")


def test_ai_connectivity_endpoint_requires_authentication() -> None:
    response = client.post("/api/ai/test")

    assert response.status_code == 401


def test_ai_connectivity_endpoint_returns_provider_answer(monkeypatch) -> None:
    class FakeClient:
        def complete(self, prompt: str) -> str:
            assert "2+2" in prompt
            return "4"

    app.dependency_overrides[get_openrouter_client] = lambda: FakeClient()
    try:
        response = client.post("/api/ai/test", auth=auth())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"answer": "4"}


def test_ai_connectivity_endpoint_maps_missing_key(monkeypatch) -> None:
    app.dependency_overrides[
        get_openrouter_client
    ] = lambda: OpenRouterClient(api_key="")
    try:
        response = client.post("/api/ai/test", auth=auth())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


@pytest.mark.live
def test_live_openrouter_connectivity() -> None:
    if os.getenv("RUN_LIVE_AI_TESTS") != "1":
        pytest.skip("set RUN_LIVE_AI_TESTS=1 to call OpenRouter")

    answer = OpenRouterClient().complete("What is 2+2? Answer with only the number.")

    assert "4" in answer
