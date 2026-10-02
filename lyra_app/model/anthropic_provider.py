"""Anthropic (Claude) cloud backend, using only the standard library.

Same contract as every other backend: the brain decides when to call it, and
the guideline still checks the output. The API key is read from the environment.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from lyra_app.model.entities import ModelResponse
from lyra_app.model.model_interface import ModelInterface, ModelUnavailable

DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(ModelInterface):
    """Talks to the Anthropic Messages API."""

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

    @property
    def name(self) -> str:  # type: ignore[override]
        return self.model_name

    def is_available(self) -> bool:
        return bool(self.api_key and self.model_name)

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
        for turn in history or []:
            role = turn.get("role", "user")
            if role == "system":
                continue
            content = turn.get("content", "")
            if content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        request = urllib.request.Request(
            f"{self.base_url}/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": ANTHROPIC_VERSION,
            },
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
        for block in result.get("content") or []:
            if block.get("type") == "text":
                content += block.get("text", "")
        usage = result.get("usage") or {}
        return ModelResponse(
            content=content,
            metadata={
                "model": self.model_name,
                "backend": "cloud",
                "status": "success",
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
            },
        )

    def configure(self, model_name: str) -> bool:
        if not model_name:
            return False
        self.model_name = model_name
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
    return os.environ.get("LYRA_CLOUD_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or ""
