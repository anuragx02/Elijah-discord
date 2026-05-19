"""Postgres storage for persistent conversation memory."""

import json
import logging
from typing import List, Optional

from memory import Message


LOGGER = logging.getLogger(__name__)


class PostgresConversationStore:
    """Persists scoped conversation history in Supabase Postgres."""

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("database_url is required.")

        try:
            import psycopg
            from psycopg.rows import dict_row
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Postgres memory requires psycopg. Run `pip install -r requirements.txt`."
            ) from exc

        self.database_url = database_url
        self._psycopg = psycopg
        self._row_factory = dict_row
        self.init_schema()

    def init_schema(self) -> None:
        """Create the memory table if it does not exist."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_memories (
                    scope_id TEXT PRIMARY KEY,
                    messages JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

    def load(self, scope_id: str) -> Optional[List[Message]]:
        """Load a scope's stored messages."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT messages FROM conversation_memories WHERE scope_id = %s",
                (scope_id,),
            ).fetchone()

        if not row:
            return None

        messages = row["messages"]
        if isinstance(messages, str):
            messages = json.loads(messages)

        if not isinstance(messages, list):
            LOGGER.warning("Ignoring malformed stored memory for scope %s.", scope_id)
            return None

        return [
            {"role": str(message["role"]), "content": str(message["content"])}
            for message in messages
            if isinstance(message, dict) and "role" in message and "content" in message
        ]

    def save(self, scope_id: str, messages: List[Message]) -> None:
        """Upsert a scope's complete bounded message history."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_memories (scope_id, messages, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (scope_id)
                DO UPDATE SET messages = EXCLUDED.messages, updated_at = NOW()
                """,
                (scope_id, json.dumps(messages)),
            )

    def reset(self, scope_id: str, messages: List[Message]) -> None:
        """Replace a scope's memory with a fresh history."""
        self.save(scope_id, messages)

    def _connect(self):
        return self._psycopg.connect(
            self.database_url,
            row_factory=self._row_factory,
            autocommit=True,
        )
