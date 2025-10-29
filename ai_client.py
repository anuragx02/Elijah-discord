"""
AI client module for communicating with the AI model API.
Uses the requests library as specified in requirements.
"""

import requests
import json
from typing import Dict, Any, Optional


class AIClient:
    """Handles communication with the AI model API."""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize the AI client.
        
        Args:
            api_url: URL endpoint for the AI API
            api_key: Optional API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
    
    def get_response(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a response from the AI model.
        
        Args:
            message: User message to send to the AI
            user_context: Optional user context/history to include
            
        Returns:
            AI response as a string
        """
        try:
            # Prepare the request payload
            payload = {
                "message": message,
                "context": user_context or {}
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Make the request
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Try different common response formats
            if "response" in data:
                return data["response"]
            elif "message" in data:
                return data["message"]
            elif "text" in data:
                return data["text"]
            elif isinstance(data, str):
                return data
            else:
                return str(data)
                
        except requests.exceptions.RequestException as e:
            # Return a fallback response if the API fails
            return f"I'm having trouble connecting to my AI service right now. Error: {str(e)}"
        except json.JSONDecodeError:
            return "I received an unexpected response from my AI service."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"


class MockAIClient(AIClient):
    """Mock AI client for testing purposes when no real API is available."""
    
    def __init__(self):
        """Initialize mock AI client."""
        super().__init__("mock://localhost", None)
    
    def get_response(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a mock response.
        
        Args:
            message: User message
            user_context: Optional user context
            
        Returns:
            Mock AI response
        """
        message_lower = message.lower()
        
        # Check if asking about stored information
        if "my name" in message_lower or "who am i" in message_lower:
            if user_context and "data" in user_context and "name" in user_context["data"]:
                return f"Your name is {user_context['data']['name']}!"
            return "I don't think you've told me your name yet."
        
        if "remember" in message_lower or "my name is" in message_lower:
            return "Got it! I'll remember that."
        
        # Default responses
        responses = [
            "That's interesting! Tell me more.",
            "I understand. How can I help you today?",
            "Thanks for sharing that with me!",
            "I'm here to chat. What else would you like to talk about?",
        ]
        
        # Use message length to deterministically pick a response
        return responses[len(message) % len(responses)]
