"""OpenAI-compatible cloud backend, using only the standard library.

Many providers speak the OpenAI chat-completions shape (OpenAI, Groq,
OpenRouter, Together, Mistral, DeepSeek, and local gateways like LM Studio or
vLLM). One backend covers them all by changing the base URL.

Used for weak machines that cannot run a useful local model. The model is still
only a function: the brain decides when to call it, and the guideline still
checks the output. The API key is read from the environment and never stored in
the instance folder.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from lyra_app.model.entities import ModelResponse
from lyra_app.model.model_interface import ModelInterface, ModelUnavailable

DEFAULT_BASE_URL = "https://api.openai.com/v1"


class OpenAICompatibleProvider(ModelInterface):
    """Talks to any OpenAI-compatible chat-completions endpoint."""

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ):
        self.model_name = model_name
        self.api_key = api_key or ""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._available: Optional[bool] = None

    @property
    def name(self) -> str:  # type: ignore[override]
        return self.model_name

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def is_available(self) -> bool:
        # A cloud call costs time and money; "available" only means configured.
        self._available = bool(self.api_key and self.model_name)
        return self._available

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        timeout: float = 60.0,
    ) -> ModelResponse:
        if not self.is_available():
            raise ModelUnavailable("cloud model is not configured (missing API key)")

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for turn in history or []:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout or self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:300]
            raise ModelUnavailable(f"HTTP {error.code}: {detail}") from error
        except (urllib.error.URLError, OSError, ValueError) as error:
            raise ModelUnavailable(str(error)) from error

        content = ""
        choices = result.get("choices") or []
        if choices:
            content = (choices[0].get("message") or {}).get("content", "") or ""
        usage = result.get("usage") or {}
        return ModelResponse(
            content=content,
            metadata={
                "model": self.model_name,
                "backend": "cloud",
                "status": "success",
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
            },
        )

    def configure(self, model_name: str) -> bool:
        if not model_name:
            return False
        self.model_name = model_name
        self._available = None
        return True

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "backend": "cloud",
            "base_url": self.base_url,
            "available": self.is_available(),
            "key_env": "LYRA_CLOUD_API_KEY",
        }


def api_key_from_env() -> str:
    """Read the cloud API key from the environment (never from disk)."""
    return (
        os.environ.get("LYRA_CLOUD_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("GROQ_API_KEY")
        or ""
    )
