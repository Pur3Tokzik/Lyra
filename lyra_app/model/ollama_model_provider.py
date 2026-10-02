"""Ollama backend using only the standard library.

Uses ``urllib.request`` (no ``requests``) and the ``/api/chat`` endpoint, which
takes a proper message list. Timeout is configurable and a failure is raised as
:class:`ModelUnavailable` so the brain can fall back to reduced mode instead of
crashing.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from lyra_app.model.entities import ModelResponse
from lyra_app.model.model_interface import ModelInterface, ModelUnavailable


class OllamaModelProvider(ModelInterface):
    """Talks to a local Ollama server over HTTP."""

    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._available: Optional[bool] = None

    @property
    def name(self) -> str:  # type: ignore[override]
        return self.model_name

    def _request(self, path: str, payload: Optional[dict] = None, timeout: float | None = None):
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        with urllib.request.urlopen(request, timeout=timeout or self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def is_available(self) -> bool:
        try:
            self._request("/api/tags", timeout=3.0)
            self._available = True
        except (urllib.error.URLError, OSError, ValueError):
            self._available = False
        return bool(self._available)

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        timeout: float = 60.0,
    ) -> ModelResponse:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for turn in history or []:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        payload = {"model": self.model_name, "messages": messages, "stream": False}
        try:
            result = self._request("/api/chat", payload=payload, timeout=timeout)
        except (urllib.error.URLError, OSError, ValueError) as error:
            self._available = False
            raise ModelUnavailable(str(error)) from error

        content = ""
        message = result.get("message")
        if isinstance(message, dict):
            content = message.get("content", "")
        elif isinstance(result.get("response"), str):
            content = result["response"]

        return ModelResponse(
            content=content,
            metadata={
                "model": self.model_name,
                "status": "success",
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
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
            "backend": "ollama",
            "available": self.is_available(),
            "base_url": self.base_url,
        }
