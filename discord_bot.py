"""Discord event handling for Elijah."""

import logging
from typing import Iterable, List

import aiohttp
import discord

from config import BotConfig
from groq_client import GroqAPIError, GroqChatClient
from memory import ConversationMemory
from postgres_store import PostgresConversationStore


LOGGER = logging.getLogger(__name__)
DISCORD_MESSAGE_LIMIT = 1900


def split_discord_message(content: str, limit: int = DISCORD_MESSAGE_LIMIT) -> List[str]:
    """Split long model output into Discord-safe chunks."""
    if len(content) <= limit:
        return [content]

    chunks = []
    remaining = content
    while remaining:
        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at == -1:
            split_at = limit

        chunk = remaining[:split_at].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_at:].strip()

    return chunks


class ElijahDiscordClient(discord.Client):
    """Discord client with scoped memory and AI-backed responses."""

    def __init__(
        self,
        config: BotConfig,
        chat_client: GroqChatClient,
        memory: ConversationMemory,
    ):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True

        super().__init__(intents=intents)
        self.config = config
        self.chat_client = chat_client
        self.memory = memory
        self.http_session: aiohttp.ClientSession = None

    async def setup_hook(self) -> None:
        self.http_session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
        await super().close()

    async def on_ready(self) -> None:
        guild_count = len(self.guilds)
        user_label = str(self.user) if self.user else "unknown user"
        LOGGER.info("Logged in as %s across %s guild(s).", user_label, guild_count)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not await self._should_respond(message):
            return

        scope_id = self._scope_id(message)
        content = self._clean_trigger_text(message.content, message.mentions)

        if await self._handle_command(message, scope_id, content):
            return

        if not content:
            await message.channel.send("Say a little more and I can work with it.")
            return

        user_label = getattr(message.author, "display_name", str(message.author))
        prompt = f"{user_label}: {content}"
        messages = self.memory.add_user_message(scope_id, prompt)

        async with message.channel.typing():
            try:
                reply = await self.chat_client.complete(self.http_session, messages)
            except GroqAPIError as exc:
                LOGGER.warning("AI request failed: %s", exc)
                await message.channel.send("I could not reach the AI service right now. Try again in a moment.")
                return
            except aiohttp.ClientError as exc:
                LOGGER.warning("Network request failed: %s", exc)
                await message.channel.send("The AI service connection failed. Try again in a moment.")
                return

        self.memory.add_assistant_message(scope_id, reply)
        for chunk in split_discord_message(reply):
            await message.channel.send(chunk)

    async def _should_respond(self, message: discord.Message) -> bool:
        if self.config.channel_id and message.channel.id != self.config.channel_id:
            return False

        if isinstance(message.channel, discord.DMChannel):
            return True

        if message.content.strip().lower().startswith(self.config.command_prefix.lower()):
            return True

        if self.config.respond_to_all:
            return True

        if self.user and self.user in message.mentions:
            return True

        return await self._is_reply_to_bot(message)

    async def _is_reply_to_bot(self, message: discord.Message) -> bool:
        if not message.reference or not message.reference.message_id or not self.user:
            return False

        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False

        return replied_message.author == self.user

    def _clean_trigger_text(self, content: str, mentions: Iterable[discord.User]) -> str:
        cleaned = content.strip()
        prefix = self.config.command_prefix

        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix) :].strip()

        for mention in mentions:
            cleaned = cleaned.replace(f"<@{mention.id}>", "")
            cleaned = cleaned.replace(f"<@!{mention.id}>", "")

        return cleaned.strip()

    def _scope_id(self, message: discord.Message) -> str:
        if isinstance(message.channel, discord.DMChannel):
            return f"dm:{message.author.id}"
        return f"channel:{message.channel.id}"

    async def _handle_command(self, message: discord.Message, scope_id: str, content: str) -> bool:
        command = content.strip().lower()

        if command in {"reset", "forget"}:
            self.memory.reset(scope_id)
            await message.channel.send("Memory cleared for this chat.")
            return True

        if command == "status":
            stored_messages = self.memory.count_messages(scope_id)
            await message.channel.send(
                f"Model: `{self.config.groq_model}` | Stored messages here: `{stored_messages}`"
            )
            return True

        if command in {"help", "commands"}:
            await message.channel.send(
                "Use `!elijah reset` to clear this chat's memory or `!elijah status` to inspect it."
            )
            return True

        return False


def build_client(config: BotConfig) -> ElijahDiscordClient:
    """Assemble the Discord client and its dependencies."""
    chat_client = GroqChatClient(
        api_key=config.groq_api_key,
        model=config.groq_model,
        api_url=config.groq_api_url,
        timeout_seconds=config.request_timeout_seconds,
    )
    store = None
    if config.database_url:
        store = PostgresConversationStore(config.database_url)
        LOGGER.info("Using Supabase/Postgres-backed conversation memory.")
    else:
        LOGGER.info("Using in-memory conversation memory.")

    memory = ConversationMemory(
        system_prompt=config.system_prompt,
        max_messages=config.max_history_messages,
        store=store,
    )
    return ElijahDiscordClient(config=config, chat_client=chat_client, memory=memory)


def run() -> None:
    """Load config and start the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    try:
        config = BotConfig.from_env()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    client = build_client(config)
    client.run(config.discord_token, log_handler=None)
