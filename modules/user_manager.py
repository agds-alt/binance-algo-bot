"""
User Management System
Handles user registration, authentication, and profile management
"""

import sqlite3
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import os
from pathlib import Path


class UserManager:
    """Manage user accounts and authentication"""

    def __init__(self, db_path: str = "data/users.db"):
        """Initialize user manager with database"""
        self.db_path = db_path

        # Create data directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create users table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                tier TEXT DEFAULT 'free',
                license_key TEXT,
                api_key_encrypted TEXT,
                api_secret_encrypted TEXT
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()

    def register_user(self, email: str, username: str, password: str,
                     full_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Register a new user

        Returns:
            (success, message)
        """
        # Validate input
        if not email or not username or not password:
            return False, "All fields are required"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not self._is_valid_email(email):
            return False, "Invalid email format"

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (email, username, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            """, (email.lower(), username, password_hash, full_name))

            conn.commit()
            conn.close()

            return True, "Registration successful! Please login."

        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                return False, "Email already registered"
            elif "username" in str(e):
                return False, "Username already taken"
            else:
                return False, "Registration failed"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def authenticate(self, username_or_email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Authenticate user

        Returns:
            (success, user_data, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check if input is email or username
            if '@' in username_or_email:
                cursor.execute("""
                    SELECT * FROM users
                    WHERE email = ? AND is_active = 1
                """, (username_or_email.lower(),))
            else:
                cursor.execute("""
                    SELECT * FROM users
                    WHERE username = ? AND is_active = 1
                """, (username_or_email,))

            user = cursor.fetchone()

            if not user:
                conn.close()
                return False, None, "Invalid credentials"

            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (user['id'],))
                conn.commit()

                # Convert to dict
                user_data = {
                    'id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'tier': user['tier'],
                    'license_key': user['license_key'],
                    'created_at': user['created_at']
                }

                conn.close()
                return True, user_data, "Login successful"
            else:
                conn.close()
                return False, None, "Invalid credentials"

        except Exception as e:
            return False, None, f"Error: {str(e)}"

    def create_session(self, user_id: int, ip_address: str = None,
                      user_agent: str = None) -> str:
        """Create a new session for user"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)  # 7 days session

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_token, expires_at, ip_address, user_agent))

        conn.commit()
        conn.close()

        return session_token

    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate session and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT u.*, s.expires_at
                FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_token,))

            user = cursor.fetchone()
            conn.close()

            if user:
                return True, {
                    'id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'tier': user['tier'],
                    'license_key': user['license_key']
                }
            else:
                return False, None

        except Exception:
            return False, None

    def delete_session(self, session_token: str):
        """Delete/logout session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))

        conn.commit()
        conn.close()

    def update_user_tier(self, user_id: int, tier: str, license_key: str = None):
        """Update user's tier and license"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET tier = ?, license_key = ?
            WHERE id = ?
        """, (tier, license_key, user_id))

        conn.commit()
        conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user data by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user data by email"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def get_total_users(self) -> int:
        """Get total registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        conn.close()
        return count


# Singleton instance
_user_manager = None

def get_user_manager() -> UserManager:
    """Get singleton UserManager instance"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
