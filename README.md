# Elijah Discord Bot

Elijah is a Discord AI chatbot powered by Groq's OpenAI-compatible chat completions API. It keeps channel-scoped conversation memory, can persist that memory in Supabase Postgres, responds in DMs, mentions, replies, or an opt-in "respond to all" mode, and is configured entirely through environment variables.

This repo is structured as a deployable Python bot project: modular package code, no hardcoded secrets, and environment-based configuration for hosting platforms like Wispbyte.

## Highlights

- Async Discord bot built on `discord.py` and `aiohttp`
- Groq chat completions integration with configurable model and endpoint
- Per-channel and per-DM memory window with optional Supabase Postgres persistence
- Mention, reply, DM, command-prefix, or configured channel response modes
- Safe environment-based configuration through `.env`
- Local commands for memory reset and status checks
- Simple `python main.py` startup command for hosting

## Demo Commands

After inviting the bot to a server:

```text
@Elijah help me brainstorm a project idea
!elijah status
!elijah reset
```

By default, Elijah responds to DMs, direct mentions, replies to the bot, and `!elijah` commands. Set `RESPOND_TO_ALL=true` only in a private or dedicated bot channel.

## Project Structure

```text
Elijah-discord/
|-- main.py           # Wispbyte-friendly startup file
|-- config.py         # Environment configuration and validation
|-- discord_bot.py    # Discord event handling and bot commands
|-- groq_client.py    # Async Groq chat completions client
|-- memory.py         # Channel-scoped conversation memory
|-- postgres_store.py # Supabase/Postgres-backed memory store
|-- Procfile          # Worker process command for compatible hosts
|-- runtime.txt       # Python runtime hint for compatible hosts
|-- .env.example
`-- requirements.txt
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your environment file:

```bash
copy .env.example .env
```

4. Fill in the required values:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

5. Optional: add Supabase-backed memory:

```env
SUPABASE_DB_URL=postgresql://postgres.your-ref:password@aws-0-region.pooler.supabase.com:6543/postgres?sslmode=require
```

6. Run the bot:

```bash
python main.py
```

## Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `DISCORD_TOKEN` | Yes | - | Discord bot token from the Developer Portal |
| `GROQ_API_KEY` | Yes | - | Groq API key |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` | Chat model name |
| `GROQ_API_URL` | No | Groq chat completions URL | OpenAI-compatible chat endpoint |
| `CHANNEL_ID` | No | empty | Restrict bot responses to one Discord channel |
| `RESPOND_TO_ALL` | No | `false` | Respond to every message in the allowed channel |
| `MAX_HISTORY_MESSAGES` | No | `12` | Max messages retained per chat, including system prompt |
| `REQUEST_TIMEOUT_SECONDS` | No | `30` | HTTP timeout for AI requests |
| `COMMAND_PREFIX` | No | `!elijah` | Prefix for local bot commands |
| `SYSTEM_PROMPT` | No | concise Elijah persona | Bot behavior instruction |
| `SUPABASE_DB_URL` | No | empty | Supabase/Postgres connection string for persistent memory |

`DATABASE_URL` also works as an alias for `SUPABASE_DB_URL`.

## Supabase Memory

Without `SUPABASE_DB_URL`, Elijah uses in-memory chat history. That is fine for local testing, but the memory disappears when the bot restarts.

With `SUPABASE_DB_URL`, Elijah stores each channel or DM's bounded message history in Supabase Postgres. On startup, the app creates this table automatically:

```sql
CREATE TABLE IF NOT EXISTS conversation_memories (
    scope_id TEXT PRIMARY KEY,
    messages JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

To get the connection string in Supabase:

1. Open your Supabase project.
2. Go to Project Settings > Database.
3. Copy the pooled connection string.
4. Add your database password.
5. Keep `sslmode=require` in the URL.

The bot stores only the recent bounded context configured by `MAX_HISTORY_MESSAGES`, not an unlimited transcript.

## Discord Setup

1. Open the Discord Developer Portal.
2. Create an application and add a bot user.
3. Enable the Message Content Intent.
4. Use OAuth2 URL Generator with the `bot` scope.
5. Give it `View Channels`, `Send Messages`, and `Read Message History`.
6. Invite the bot to your server.

## Wispbyte Hosting

Use this startup command:

```bash
python main.py
```

If Wispbyte reads a `Procfile`, it can use:

```text
worker: python main.py
```

Configure secrets in Wispbyte's environment variable panel instead of committing a real `.env` file.

## Security Notes

- Never commit `.env` or real tokens.
- If a token was ever committed or shared, rotate it in the Discord Developer Portal or Groq dashboard.
- Treat your Supabase database password like a secret too.
- Keep `RESPOND_TO_ALL=false` unless the bot is in a private or dedicated bot channel.
