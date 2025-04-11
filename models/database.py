import duckdb
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='app.ddb'):
        """Initialize the DuckDB database connection."""
        self.conn = duckdb.connect(db_path)
        self.setup_tables()
    
    def setup_tables(self):
        """Set up the necessary tables if they don't exist."""
        # Users table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR PRIMARY KEY,
                email VARCHAR,
                name VARCHAR,
                profile_pic VARCHAR,
                auth_provider VARCHAR,
                created_at TIMESTAMP
            )
        """)
        
        # User sessions table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Example data table - modify based on your app needs
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY,
                user_id VARCHAR,
                title VARCHAR,
                content VARCHAR,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    
    def add_user(self, user_id, email, name, profile_pic, auth_provider):
        """Add a new user to the database."""
        self.conn.execute("""
            INSERT INTO users (id, email, name, profile_pic, auth_provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                email=excluded.email,
                name=excluded.name,
                profile_pic=excluded.profile_pic
        """, (user_id, email, name, profile_pic, auth_provider, datetime.now()))
        
    def get_user(self, user_id):
        """Get a user by ID."""
        result = self.conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return result
    
    def create_session(self, session_id, user_id, expires_at):
        """Create a new session."""
        self.conn.execute("""
            INSERT INTO sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (session_id) DO UPDATE SET
                user_id=excluded.user_id,
                created_at=excluded.created_at,
                expires_at=excluded.expires_at
        """, (session_id, user_id, datetime.now(), expires_at))
    
    def get_session(self, session_id):
        """Get a session by ID."""
        result = self.conn.execute(
            "SELECT * FROM sessions WHERE session_id = ? AND expires_at > ?", 
            (session_id, datetime.now())
        ).fetchone()
        return result
    
    def add_user_data(self, user_id, title, content):
        """Add data for a user."""
        self.conn.execute("""
            INSERT INTO user_data (user_id, title, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, title, content, datetime.now()))
    
    def get_user_data(self, user_id):
        """Get all data for a user."""
        result = self.conn.execute(
            "SELECT * FROM user_data WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        ).fetchall()
        return result
    
    def close(self):
        """Close the database connection."""
        self.conn.close()


# Create a singleton instance
db = Database()
