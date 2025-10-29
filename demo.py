"""
Demonstration script showing how the bot works without Discord connection.
This helps verify the core logic works correctly.
"""

from database import UserDatabase
from ai_client import MockAIClient
from ai_extractor import MockAIExtractor
import tempfile
import os


def simulate_conversation():
    """Simulate a conversation with the bot."""
    print("=" * 60)
    print("Discord Bot Conversation Simulation")
    print("(Using AI-based extraction)")
    print("=" * 60)
    print()
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        # Initialize components
        db = UserDatabase(db_path)
        ai_client = MockAIClient()
        ai_extractor = MockAIExtractor()
        
        # Simulate user
        user_id = "123456789"
        username = "TestUser#1234"
        
        print("User: @Bot Hello!")
        print("Bot: That's interesting! Tell me more.")
        print()
        
        # First message with name
        message1 = "My name is Alice"
        info = ai_extractor.extract_user_info(message1)
        if info:
            db.store_user_info(user_id, username, info)
            print(f"[AI Extraction] Stored: {info}")
        
        user_context = db.get_user_info(user_id)
        response = ai_client.get_response(message1, user_context)
        print(f"User: @Bot {message1}")
        print(f"Bot: {response}")
        print()
        
        # Second message with age
        message2 = "I'm 25 years old"
        info = ai_extractor.extract_user_info(message2)
        if info:
            db.store_user_info(user_id, username, info)
            print(f"[AI Extraction] Stored: {info}")
        
        user_context = db.get_user_info(user_id)
        response = ai_client.get_response(message2, user_context)
        print(f"User: @Bot {message2}")
        print(f"Bot: {response}")
        print()
        
        # Third message with location
        message3 = "I live in New York"
        info = ai_extractor.extract_user_info(message3)
        if info:
            db.store_user_info(user_id, username, info)
            print(f"[AI Extraction] Stored: {info}")
        
        user_context = db.get_user_info(user_id)
        response = ai_client.get_response(message3, user_context)
        print(f"User: @Bot {message3}")
        print(f"Bot: {response}")
        print()
        
        # Fourth message with occupation
        message4 = "I work as a software engineer"
        info = ai_extractor.extract_user_info(message4)
        if info:
            db.store_user_info(user_id, username, info)
            print(f"[AI Extraction] Stored: {info}")
        
        user_context = db.get_user_info(user_id)
        response = ai_client.get_response(message4, user_context)
        print(f"User: @Bot {message4}")
        print(f"Bot: {response}")
        print()
        
        # Fifth message asking about name
        message5 = "What's my name?"
        user_context = db.get_user_info(user_id)
        response = ai_client.get_response(message5, user_context)
        print(f"User: @Bot {message5}")
        print(f"Bot: {response}")
        print()
        
        # Show stored data
        print("=" * 60)
        print("Stored User Information")
        print("=" * 60)
        user_data = db.get_user_info(user_id)
        if user_data:
            print(f"Username: {user_data['username']}")
            print(f"Data: {user_data['data']}")
            print(f"Last Updated: {user_data['last_updated']}")
        print()
        
        print("=" * 60)
        print("Simulation Complete!")
        print("=" * 60)
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    simulate_conversation()
