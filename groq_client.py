"""Async client for Groq's OpenAI-compatible chat completions API."""

import logging
from typing import Dict, List

import aiohttp


LOGGER = logging.getLogger(__name__)
Message = Dict[str, str]


class GroqAPIError(RuntimeError):
    """Raised when the chat completions API cannot return a usable answer."""


class GroqChatClient:
    """Small wrapper around Groq chat completions."""

    def __init__(
        self,
        api_key: str,
        model: str,
        api_url: str,
        timeout_seconds: int = 30,
    ):
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def complete(self, session: aiohttp.ClientSession, messages: List[Message]) -> str:
        """Return the assistant's next message for a conversation."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 600,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with session.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        ) as response:
            if response.status >= 400:
                body = await response.text()
                LOGGER.warning("Groq API returned %s: %s", response.status, body[:500])
                raise GroqAPIError(f"Groq API returned HTTP {response.status}.")

            data = await response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            LOGGER.warning("Unexpected Groq response shape: %s", data)
            raise GroqAPIError("Groq API returned an unexpected response shape.") from exc

        cleaned_content = content.strip()
        if not cleaned_content:
            raise GroqAPIError("Groq API returned an empty response.")

        return cleaned_content
