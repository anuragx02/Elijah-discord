"""
AI-based user information extraction module.
Uses AI to intelligently extract user information from conversations.
"""

import requests
import json
from typing import Dict, Any, Optional


class AIExtractor:
    """Uses AI to extract user information from messages."""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the AI extractor.
        
        Args:
            api_url: URL endpoint for the AI API
            api_key: Optional API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
        self.use_ai = api_url and api_url != "https://api.example.com/chat"
    
    def extract_user_info(self, message: str) -> Dict[str, Any]:
        """
        Extract user information from a message using AI.
        
        Args:
            message: The message text to analyze
            
        Returns:
            Dictionary containing extracted user information
        """
        if self.use_ai:
            return self._extract_with_ai(message)
        else:
            return self._extract_with_simple_logic(message)
    
    def _extract_with_ai(self, message: str) -> Dict[str, Any]:
        """
        Use AI API to extract user information.
        
        Args:
            message: The message text
            
        Returns:
            Dictionary of extracted information
        """
        try:
            # Prepare extraction prompt
            extraction_prompt = f"""Analyze the following message and extract any personal information mentioned by the user.
Return ONLY a valid JSON object with the extracted information.

Possible fields to extract (only include if explicitly mentioned):
- name: User's name
- age: User's age (as string)
- location: User's location/city/country
- occupation: User's job or occupation
- hobby: User's hobbies or interests
- email: User's email address
- phone: User's phone number

Message: "{message}"

If no personal information is found, return an empty JSON object: {{}}

JSON Response:"""

            payload = {
                "message": extraction_prompt,
                "max_tokens": 200,
                "temperature": 0.1
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=15
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Try to parse the response as JSON
            response_text = ""
            if "response" in data:
                response_text = data["response"]
            elif "message" in data:
                response_text = data["message"]
            elif "text" in data:
                response_text = data["text"]
            elif isinstance(data, str):
                response_text = data
            
            # Try to extract JSON from the response
            if response_text:
                # Find JSON object in response
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    json_str = response_text[start:end+1]
                    extracted_info = json.loads(json_str)
                    return extracted_info
            
            return {}
            
        except Exception as e:
            print(f"AI extraction failed, falling back to simple logic: {e}")
            return self._extract_with_simple_logic(message)
    
    def _extract_with_simple_logic(self, message: str) -> Dict[str, Any]:
        """
        Fallback: Use simple pattern matching for extraction.
        
        Args:
            message: The message text
            
        Returns:
            Dictionary of extracted information
        """
        import re
        
        info = {}
        message_lower = message.lower()
        
        # Extract age first
        age_patterns = [
            r"i'm (\d+) years old",
            r"i am (\d+) years old",
            r"my age is (\d+)",
            r"i'm (\d+)\b",
            r"i am (\d+)\b"
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info["age"] = match.group(1)
                break
        
        # Extract name patterns (avoid matching age)
        name_patterns = [
            r"my name is ([a-zA-Z]+)",
            r"call me ([a-zA-Z]+)",
            r"i'm ([a-zA-Z]+)(?!\s*years|\s*\d)",
            r"i am ([a-zA-Z]+)(?!\s*years|\s*\d)",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1)
                # Avoid common words
                if name not in ['happy', 'sad', 'good', 'fine', 'okay', 'ok']:
                    info["name"] = name.capitalize()
                    break
        
        # Extract location
        location_patterns = [
            r"i live in ([a-zA-Z\s]+?)(?:\.|$|,|\s+and\s+)",
            r"i'm from ([a-zA-Z\s]+?)(?:\.|$|,|\s+and\s+)",
            r"i am from ([a-zA-Z\s]+?)(?:\.|$|,|\s+and\s+)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info["location"] = match.group(1).strip().title()
                break
        
        # Extract occupation
        occupation_patterns = [
            r"i work as (?:a |an )?([a-zA-Z\s]+?)(?:\.|$|,|\s+at\s+)",
            r"i'm (?:a |an )?([a-zA-Z\s]+) by profession",
            r"i am (?:a |an )?([a-zA-Z\s]+) by profession",
            r"my job is ([a-zA-Z\s]+?)(?:\.|$|,)",
        ]
        
        for pattern in occupation_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info["occupation"] = match.group(1).strip().title()
                break
        
        # Extract hobby
        hobby_patterns = [
            r"i like ([a-zA-Z\s]+?)(?:\.|$|,|\s+and\s+)",
            r"i love ([a-zA-Z\s]+?)(?:\.|$|,|\s+and\s+)",
            r"my hobby is ([a-zA-Z\s]+?)(?:\.|$|,)",
        ]
        
        for pattern in hobby_patterns:
            match = re.search(pattern, message_lower)
            if match:
                hobby = match.group(1).strip()
                if hobby not in ['to', 'that', 'it']:
                    info["hobby"] = hobby.title()
                    break
        
        return info


class MockAIExtractor(AIExtractor):
    """Mock AI extractor that simulates AI-based extraction for testing."""
    
    def __init__(self):
        """Initialize mock extractor."""
        super().__init__(None, None)
    
    def extract_user_info(self, message: str) -> Dict[str, Any]:
        """
        Simulate AI extraction with enhanced logic.
        
        Args:
            message: The message text
            
        Returns:
            Dictionary of extracted information
        """
        # Use the simple logic as our mock AI
        return self._extract_with_simple_logic(message)
