"""Environment-driven configuration for the Discord bot."""

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


DEFAULT_SYSTEM_PROMPT = (
    "You are Elijah, a concise, witty, respectful Discord assistant. "
    "Keep replies short, useful, and natural."
)


def _read_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _read_int(name: str, default: int, minimum: int = 1) -> int:
    raw_value = os.getenv(name)
    if not raw_value:
        return default

    try:
        parsed_value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc

    if parsed_value < minimum:
        raise RuntimeError(f"{name} must be at least {minimum}.")

    return parsed_value


def _read_optional_int(name: str) -> Optional[int]:
    raw_value = os.getenv(name)
    if not raw_value:
        return None

    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a numeric Discord channel ID.") from exc


@dataclass(frozen=True)
class BotConfig:
    """Runtime settings loaded from environment variables."""

    discord_token: str
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    max_history_messages: int = 12
    channel_id: Optional[int] = None
    respond_to_all: bool = False
    command_prefix: str = "!elijah"
    request_timeout_seconds: int = 30
    database_url: Optional[str] = None

    @classmethod
    def from_env(cls, load_env_file: bool = True) -> "BotConfig":
        """Build config from .env and process environment variables."""
        if load_env_file:
            if load_dotenv is None:
                raise RuntimeError(
                    "python-dotenv is not installed. Run `pip install -r requirements.txt`."
                )
            load_dotenv()

        discord_token = os.getenv("DISCORD_TOKEN", "").strip()
        groq_api_key = (
            os.getenv("GROQ_API_KEY")
            or os.getenv("AI_API_KEY")
            or ""
        ).strip()

        missing = []
        if not discord_token:
            missing.append("DISCORD_TOKEN")
        if not groq_api_key:
            missing.append("GROQ_API_KEY")

        if missing:
            joined_names = ", ".join(missing)
            raise RuntimeError(
                f"Missing required environment variable(s): {joined_names}. "
                "Create a .env file from .env.example and add your credentials."
            )

        return cls(
            discord_token=discord_token,
            groq_api_key=groq_api_key,
            groq_model=os.getenv("GROQ_MODEL", cls.groq_model).strip(),
            groq_api_url=os.getenv("GROQ_API_URL", cls.groq_api_url).strip(),
            system_prompt=os.getenv("SYSTEM_PROMPT", cls.system_prompt).strip(),
            max_history_messages=_read_int("MAX_HISTORY_MESSAGES", cls.max_history_messages, minimum=2),
            channel_id=_read_optional_int("CHANNEL_ID"),
            respond_to_all=_read_bool("RESPOND_TO_ALL", cls.respond_to_all),
            command_prefix=os.getenv("COMMAND_PREFIX", cls.command_prefix).strip(),
            request_timeout_seconds=_read_int(
                "REQUEST_TIMEOUT_SECONDS",
                cls.request_timeout_seconds,
                minimum=1,
            ),
            database_url=(
                os.getenv("SUPABASE_DB_URL")
                or os.getenv("DATABASE_URL")
                or ""
            ).strip() or None,
        )
