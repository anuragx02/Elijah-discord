"""
Simple tests for the Discord bot components.
Run with: python test_bot.py
"""

import os
import sys
import tempfile
from database import UserDatabase
from ai_client import MockAIClient


def test_database():
    """Test database functionality."""
    print("Testing database...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db = UserDatabase(db_path)
        
        # Test storing user info
        db.store_user_info("123", "TestUser", {"name": "Alice", "age": "25"})
        print("✓ User info stored successfully")
        
        # Test retrieving user info
        user_data = db.get_user_info("123")
        assert user_data is not None, "User data should exist"
        assert user_data["username"] == "TestUser", "Username should match"
        assert user_data["data"]["name"] == "Alice", "Name should match"
        assert user_data["data"]["age"] == "25", "Age should match"
        print("✓ User info retrieved successfully")
        
        # Test updating user info
        db.store_user_info("123", "TestUser", {"location": "New York"})
        user_data = db.get_user_info("123")
        assert user_data["data"]["name"] == "Alice", "Name should still exist"
        assert user_data["data"]["location"] == "New York", "Location should be added"
        print("✓ User info updated successfully")
        
        # Test non-existent user
        no_data = db.get_user_info("999")
        assert no_data is None, "Non-existent user should return None"
        print("✓ Non-existent user handled correctly")
        
        print("✅ Database tests passed!\n")
        return True
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_ai_client():
    """Test AI client functionality."""
    print("Testing AI client...")
    
    client = MockAIClient()
    
    # Test basic response
    response = client.get_response("Hello")
    assert response, "Response should not be empty"
    assert isinstance(response, str), "Response should be a string"
    print(f"✓ Basic response: {response}")
    
    # Test with context
    context = {
        "username": "TestUser",
        "data": {"name": "Alice"}
    }
    response = client.get_response("What's my name?", context)
    assert "Alice" in response, "Response should contain the user's name"
    print(f"✓ Context-aware response: {response}")
    
    # Test information storage response
    response = client.get_response("My name is Bob")
    assert response, "Response should not be empty"
    print(f"✓ Information storage response: {response}")
    
    print("✅ AI client tests passed!\n")
    return True


def test_user_info_extraction():
    """Test user information extraction from bot.py."""
    print("Testing user info extraction...")
    
    # Import the extract_user_info function
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from bot import extract_user_info
    except ImportError as e:
        print(f"⚠️  Skipping test (discord.py not installed): {e}")
        print("   Install dependencies with: pip install -r requirements.txt")
        return True
    
    # Test name extraction
    info = extract_user_info("My name is John")
    assert info.get("name") == "John", "Should extract name"
    print(f"✓ Name extraction: {info}")
    
    info = extract_user_info("I'm Alice")
    assert info.get("name") == "Alice", "Should extract name from 'I'm'"
    print(f"✓ Name extraction (I'm): {info}")
    
    # Test age extraction
    info = extract_user_info("I'm 25 years old")
    assert info.get("age") == "25", "Should extract age"
    print(f"✓ Age extraction: {info}")
    
    # Test location extraction
    info = extract_user_info("I live in New York")
    assert info.get("location") == "New York", "Should extract location"
    print(f"✓ Location extraction: {info}")
    
    # Test multiple info extraction
    info = extract_user_info("My name is Bob and I'm 30 years old")
    assert info.get("name") == "Bob", "Should extract name"
    assert info.get("age") == "30", "Should extract age"
    print(f"✓ Multiple info extraction: {info}")
    
    print("✅ User info extraction tests passed!\n")
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Running Discord Bot Tests")
    print("=" * 50 + "\n")
    
    tests = [
        test_database,
        test_ai_client,
        test_user_info_extraction,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}\n")
            failed += 1
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
