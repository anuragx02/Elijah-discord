# Elijah Discord Bot

A smart Discord chatbot that can have conversations with users and remember information about them.

## Features

- **Selective Response**: Only responds when mentioned (@bot) or when someone replies to its messages
- **Channel-Specific**: Can be configured to only respond in a specific channel
- **AI-Powered Extraction**: Uses AI to intelligently extract and store user information (name, age, location, occupation, hobbies, etc.) from conversations
- **Information Recall**: Can recall stored information about users when needed
- **AI Integration**: Uses the requests library to communicate with AI models for intelligent responses
- **Database Persistence**: Stores user data in SQLite for persistence across restarts
- **Fallback Logic**: Works with or without a real AI API - includes mock AI for testing

## Requirements

- Python 3.8 or higher
- Discord bot token (from Discord Developer Portal)
- Optional: AI API endpoint for advanced responses

## Installation

1. Clone the repository:
```bash
git clone https://github.com/anuragx02/Elijah-discord.git
cd Elijah-discord
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Configure your `.env` file with your credentials:
```env
DISCORD_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_channel_id_here  # Optional: leave empty to respond in all channels
AI_API_URL=https://api.example.com/chat  # Optional: use your AI API endpoint
AI_API_KEY=your_api_key_here  # Optional: if your AI API requires authentication
```

## Getting a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Under the TOKEN section, click "Copy" to copy your bot token
6. Enable the following Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
7. Go to OAuth2 > URL Generator
8. Select scopes: `bot`
9. Select bot permissions: `Send Messages`, `Read Messages/View Channels`, `Read Message History`
10. Use the generated URL to invite the bot to your server

## Getting Channel ID

1. Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)
2. Right-click on the channel you want the bot to respond in
3. Click "Copy ID"
4. Paste this ID in your `.env` file as `CHANNEL_ID`

## Usage

Run the bot:
```bash
python bot.py
```

### Interacting with the Bot

The bot will only respond when:
1. You mention it: `@Elijah hello!`
2. You reply to one of its messages

### Commands

- `!userinfo` - Display stored information about yourself
- `!userinfo @user` - Display stored information about another user

### How Information Storage Works

The bot uses **AI-powered extraction** to intelligently identify and store user information from conversations. It can extract:

- **Name**: "My name is John" or "Call me Alice"
- **Age**: "I'm 25 years old" or "My age is 30"
- **Location**: "I live in New York" or "I'm from London"
- **Occupation**: "I work as a software engineer"
- **Hobbies**: "I love playing guitar" or "I like reading"
- **And more**: The AI can identify various types of personal information

**Examples:**

**Examples:**
- "My name is John" → Stores name: John
- "I'm 25 years old" → Stores age: 25
- "I live in New York" → Stores location: New York
- "I work as a software engineer" → Stores occupation: Software Engineer
- "I love playing guitar" → Stores hobby: Playing Guitar

The bot can recall this information in future conversations.

**Note**: When a real AI API is configured, it uses the API for extraction. Otherwise, it falls back to enhanced pattern-matching logic.

## Project Structure

```
Elijah-discord/
├── bot.py              # Main bot file with Discord event handlers
├── database.py         # Database module for user data storage
├── ai_client.py        # AI client for API communication
├── ai_extractor.py     # AI-powered information extraction
├── demo.py             # Demonstration script
├── test_bot.py         # Test suite
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Architecture

- **bot.py**: Main Discord bot logic using discord.py library
  - Handles message events
  - Checks for mentions and replies
  - Coordinates between AI extractor, database, and AI client

- **ai_extractor.py**: AI-powered information extraction
  - Uses AI API to intelligently extract user information
  - Falls back to pattern matching when AI API is unavailable
  - Extracts name, age, location, occupation, hobbies, and more

- **database.py**: SQLite database management
  - Stores user information with JSON data field
  - Provides methods to store and retrieve user data
  - Maintains user history with timestamps

- **ai_client.py**: AI API communication
  - Uses requests library for HTTP communication
  - Includes mock client for testing without real API
  - Handles API errors gracefully

- **demo.py**: Demonstration script
  - Shows how the bot works without Discord connection
  - Tests extraction and storage functionality

- **test_bot.py**: Test suite
  - Unit tests for database, AI client, and AI extractor
  - Ensures all components work correctly

## AI Integration

The bot supports integration with any AI API that accepts JSON POST requests. If no AI API is configured, it uses a built-in mock client for basic responses.

### AI API Expected Format

Request:
```json
{
  "message": "user message",
  "context": {
    "username": "User#1234",
    "data": {
      "name": "John",
      "age": "25"
    }
  }
}
```

Response (any of these formats):
```json
{
  "response": "AI response text"
}
```
or
```json
{
  "message": "AI response text"
}
```
or
```json
{
  "text": "AI response text"
}
```

## Development

### Testing Without AI API

The bot includes a mock AI client that works without any external API. Simply leave `AI_API_URL` unset or set to the example URL, and the bot will use mock responses for testing.

### Database Schema

Users table:
- `user_id` (TEXT, PRIMARY KEY): Discord user ID
- `username` (TEXT): Discord username
- `data` (TEXT): JSON field containing user information
- `last_updated` (TIMESTAMP): Last update timestamp

## Troubleshooting

**Bot doesn't respond:**
- Ensure the bot has "Message Content Intent" enabled in Discord Developer Portal
- Check that you're mentioning the bot or replying to its messages
- If using CHANNEL_ID, verify the bot is in that specific channel

**Database errors:**
- Ensure the bot has write permissions in its directory
- Delete `users.db` to reset the database if corrupted

**AI API errors:**
- Check your API URL and key are correct
- Verify your API endpoint is accessible
- Check API request/response format matches expectations

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
