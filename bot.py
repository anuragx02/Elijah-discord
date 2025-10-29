"""
Discord chatbot that responds to mentions and stores user information.
Uses AI for intelligent extraction of user information from conversations.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import UserDatabase
from ai_client import AIClient, MockAIClient
from ai_extractor import AIExtractor, MockAIExtractor

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
AI_API_URL = os.getenv("AI_API_URL")
AI_API_KEY = os.getenv("AI_API_KEY")

# Initialize database
db = UserDatabase()

# Initialize AI client
if AI_API_URL and AI_API_URL != "https://api.example.com/chat":
    ai_client = AIClient(AI_API_URL, AI_API_KEY)
    ai_extractor = AIExtractor(AI_API_URL, AI_API_KEY)
    print("Using real AI client and extractor.")
else:
    print("Using mock AI client and extractor. Set AI_API_URL in .env to use a real AI service.")
    ai_client = MockAIClient()
    ai_extractor = MockAIExtractor()

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Event handler when bot is ready."""
    print(f"{bot.user} has connected to Discord!")
    print(f"Bot is in {len(bot.guilds)} guilds")
    if CHANNEL_ID:
        print(f"Configured to respond in channel ID: {CHANNEL_ID}")
    else:
        print("No specific channel configured. Will respond in any channel when mentioned.")


@bot.event
async def on_message(message):
    """
    Event handler for incoming messages.
    Only responds when mentioned or replied to in the configured channel.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if message is in the configured channel (if specified)
    if CHANNEL_ID and str(message.channel.id) != CHANNEL_ID:
        return
    
    # Check if bot was mentioned or if message is a reply to the bot
    bot_mentioned = bot.user in message.mentions
    is_reply_to_bot = False
    
    if message.reference:
        # Check if this is a reply to the bot
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            is_reply_to_bot = replied_message.author == bot.user
        except (discord.NotFound, discord.HTTPException):
            pass
    
    # Only respond if mentioned or replied to
    if not (bot_mentioned or is_reply_to_bot):
        return
    
    # Remove bot mention from message content
    content = message.content
    for mention in message.mentions:
        content = content.replace(f"<@{mention.id}>", "").strip()
        content = content.replace(f"<@!{mention.id}>", "").strip()
    
    if not content:
        await message.channel.send("Yes? How can I help you?")
        return
    
    # Extract and store user information using AI
    user_info = ai_extractor.extract_user_info(content)
    if user_info:
        db.store_user_info(
            str(message.author.id),
            str(message.author),
            user_info
        )
    
    # Get user context from database
    user_context = db.get_user_info(str(message.author.id))
    
    # Get AI response
    response = ai_client.get_response(content, user_context)
    
    # Send response
    await message.channel.send(response)
    
    # Process commands (if any)
    await bot.process_commands(message)


@bot.command(name="userinfo")
async def user_info_command(ctx, member: discord.Member = None):
    """
    Display stored information about a user.
    Usage: !userinfo @user or !userinfo (for yourself)
    """
    target = member or ctx.author
    user_data = db.get_user_info(str(target.id))
    
    if user_data:
        embed = discord.Embed(
            title=f"Information about {target.display_name}",
            color=discord.Color.blue()
        )
        
        data = user_data.get("data", {})
        if data:
            for key, value in data.items():
                embed.add_field(name=key.capitalize(), value=value, inline=True)
        else:
            embed.description = "No information stored yet."
        
        embed.set_footer(text=f"Last updated: {user_data.get('last_updated', 'Unknown')}")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No information stored about {target.display_name} yet.")


def main():
    """Main entry point for the bot."""
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        print("Please create a .env file with your Discord bot token.")
        print("See .env.example for the required format.")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("Error: Invalid Discord token. Please check your .env file.")
    except Exception as e:
        print(f"Error starting bot: {e}")


if __name__ == "__main__":
    main()
