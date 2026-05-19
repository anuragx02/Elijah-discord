"""Channel-scoped conversation memory."""

import logging
from typing import Dict, List, Optional, Protocol


Message = Dict[str, str]
LOGGER = logging.getLogger(__name__)


class ConversationStore(Protocol):
    """Persistence contract for conversation history stores."""

    def load(self, scope_id: str) -> Optional[List[Message]]:
        """Load messages for a scope, or None if no memory exists."""

    def save(self, scope_id: str, messages: List[Message]) -> None:
        """Persist the complete bounded message history for a scope."""

    def reset(self, scope_id: str, messages: List[Message]) -> None:
        """Replace a scope's memory with a fresh history."""


class ConversationMemory:
    """Keeps a bounded chat history per channel or DM."""

    def __init__(
        self,
        system_prompt: str,
        max_messages: int = 12,
        store: Optional[ConversationStore] = None,
    ):
        if max_messages < 2:
            raise ValueError("max_messages must be at least 2.")

        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.store = store
        self._histories: Dict[str, List[Message]] = {}

    def get_history(self, scope_id: str) -> List[Message]:
        """Return a defensive copy of a scope's message history."""
        history = self._ensure_history(scope_id)
        return [message.copy() for message in history]

    def add_user_message(self, scope_id: str, content: str) -> List[Message]:
        """Append a user message and return the updated history."""
        return self._append(scope_id, "user", content)

    def add_assistant_message(self, scope_id: str, content: str) -> List[Message]:
        """Append an assistant message and return the updated history."""
        return self._append(scope_id, "assistant", content)

    def reset(self, scope_id: str) -> None:
        """Clear the chat history for a single channel or DM."""
        history = self._new_history()
        self._histories[scope_id] = history
        self._persist(scope_id, history)

    def count_messages(self, scope_id: str) -> int:
        """Return the number of messages stored for a scope."""
        return len(self._ensure_history(scope_id))

    def _new_history(self) -> List[Message]:
        return [{"role": "system", "content": self.system_prompt}]

    def _append(self, scope_id: str, role: str, content: str) -> List[Message]:
        cleaned_content = content.strip()
        if not cleaned_content:
            return self.get_history(scope_id)

        history = self._ensure_history(scope_id)
        history.append({"role": role, "content": cleaned_content})
        self._prune(history)
        self._persist(scope_id, history)
        return self.get_history(scope_id)

    def _prune(self, history: List[Message]) -> None:
        system_message = history[0]
        recent_messages = history[1:][-self.max_messages + 1 :]
        history[:] = [system_message] + recent_messages

    def _ensure_history(self, scope_id: str) -> List[Message]:
        if scope_id in self._histories:
            return self._histories[scope_id]

        stored_history = self._load(scope_id)
        if stored_history:
            self._histories[scope_id] = self._normalize(stored_history)
        else:
            self._histories[scope_id] = self._new_history()

        return self._histories[scope_id]

    def _load(self, scope_id: str) -> Optional[List[Message]]:
        if not self.store:
            return None

        try:
            return self.store.load(scope_id)
        except Exception:
            LOGGER.exception("Failed to load memory for scope %s.", scope_id)
            return None

    def _persist(self, scope_id: str, history: List[Message]) -> None:
        if not self.store:
            return

        try:
            self.store.save(scope_id, [message.copy() for message in history])
        except Exception:
            LOGGER.exception("Failed to persist memory for scope %s.", scope_id)

    def _normalize(self, history: List[Message]) -> List[Message]:
        normalized = [
            {"role": message["role"], "content": message["content"]}
            for message in history
            if message.get("role") in {"system", "user", "assistant"}
            and isinstance(message.get("content"), str)
            and message.get("content", "").strip()
        ]

        if not normalized or normalized[0]["role"] != "system":
            normalized.insert(0, {"role": "system", "content": self.system_prompt})
        else:
            normalized[0] = {"role": "system", "content": self.system_prompt}

        self._prune(normalized)
        return normalized
