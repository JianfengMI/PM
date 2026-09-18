import os

import httpx
from dotenv import load_dotenv


load_dotenv()


class OpenRouterError(RuntimeError):
    pass


class MissingOpenRouterKey(OpenRouterError):
    pass


class OpenRouterClient:
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        self.timeout = timeout or float(os.getenv("OPENROUTER_TIMEOUT", "30"))
        self.transport = transport

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise MissingOpenRouterKey("OPENROUTER_API_KEY is not configured")
        if not prompt.strip():
            raise OpenRouterError("prompt must not be empty")

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Project Management MVP",
        }

        try:
            with httpx.Client(transport=self.transport, timeout=self.timeout) as client:
                response = client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as error:
            raise OpenRouterError("OpenRouter request timed out") from error
        except httpx.HTTPError as error:
            raise OpenRouterError("OpenRouter request failed") from error

        try:
            response_payload = response.json()
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise OpenRouterError("OpenRouter returned an invalid response") from error

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError("OpenRouter returned an empty response")
        return content
