"""
Database module for storing and retrieving user information.
Uses SQLite for data persistence.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any


class UserDatabase:
    """Manages user data storage and retrieval."""
    
    def __init__(self, db_path: str = "users.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the users table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    data TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def store_user_info(self, user_id: str, username: str, info: Dict[str, Any]):
        """
        Store or update user information in the database.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            info: Dictionary containing user information to store
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT data FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                # Merge existing data with new info
                existing_data = json.loads(result[0])
                existing_data.update(info)
                data_json = json.dumps(existing_data)
                
                cursor.execute("""
                    UPDATE users 
                    SET username = ?, data = ?, last_updated = ?
                    WHERE user_id = ?
                """, (username, data_json, datetime.now(), user_id))
            else:
                # Insert new user
                data_json = json.dumps(info)
                cursor.execute("""
                    INSERT INTO users (user_id, username, data, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, data_json, datetime.now()))
            
            conn.commit()
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information from the database.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Dictionary containing user information or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, data, last_updated 
                FROM users 
                WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            
            if result:
                username, data_json, last_updated = result
                data = json.loads(data_json)
                return {
                    "username": username,
                    "data": data,
                    "last_updated": last_updated
                }
            return None
    
    def get_all_users(self) -> list:
        """
        Retrieve all users from the database.
        
        Returns:
            List of tuples containing (user_id, username, data, last_updated)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, data, last_updated FROM users")
            return cursor.fetchall()
