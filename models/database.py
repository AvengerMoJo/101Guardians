import duckdb
from flask import g
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='app.db'):
        """Initialize the DuckDB database connection."""
        self.db_path = db_path
        self.setup_tables()

    def get_connection(self):
        """Get or create a database connection for the DuckDB database."""
        if 'db_conn' not in g:
            g.db_conn = duckdb.connect(self.db_path)
        return g.db_conn
    
    def setup_tables(self):
        """Set up the necessary tables if they don't exist."""
        conn = duckdb.connect(self.db_path)  # Temporary connection for setup
        try:
            # Users table
            conn.execute("""
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR PRIMARY KEY,
                    user_id VARCHAR,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # User prayers table - Enhanced with new fields
            conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS user_data_id_seq;
                
                CREATE TABLE IF NOT EXISTS user_data (
                    id INTEGER PRIMARY KEY DEFAULT(nextval('user_data_id_seq')),
                    user_id VARCHAR,
                    title VARCHAR,
                    content VARCHAR,
                    is_public BOOLEAN DEFAULT FALSE,
                    is_answered BOOLEAN DEFAULT FALSE,
                    answer_text VARCHAR,
                    answered_at TIMESTAMP,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Prayer interactions table (for tracking prays, praise, etc.)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prayer_interactions (
                    id INTEGER PRIMARY KEY,
                    prayer_id INTEGER,
                    user_id VARCHAR,
                    interaction_type VARCHAR,  -- 'pray', 'praise', etc.
                    created_at TIMESTAMP,
                    FOREIGN KEY (prayer_id) REFERENCES user_data(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        finally:
            conn.close()
    
    def add_user(self, user_id, email, name, profile_pic, auth_provider):
        """Add a new user to the database."""
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO users (id, email, name, profile_pic, auth_provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                email=excluded.email,
                name=excluded.name,
                profile_pic=excluded.profile_pic
        """, (user_id, email, name, profile_pic, auth_provider, datetime.now()))
        
    def get_user(self, user_id):
        """Get a user by ID."""
        conn = self.get_connection()
        result = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return result
    
    def create_session(self, session_id, user_id, expires_at):
        """Create a new session."""
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (session_id) DO UPDATE SET
                user_id=excluded.user_id,
                created_at=excluded.created_at,
                expires_at=excluded.expires_at
        """, (session_id, user_id, datetime.now(), expires_at))
    
    def get_session(self, session_id):
        """Get a session by ID."""
        conn = self.get_connection()
        result = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ? AND expires_at > ?", 
            (session_id, datetime.now())
        ).fetchone()
        return result
    
    def add_prayer(self, user_id, title, content, is_public=False):
        """Add a prayer for a user."""
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO user_data (user_id, title, content, is_public, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, content, is_public, datetime.now()))
    
    def get_user_prayers(self, user_id):
        """Get all prayers for a user."""
        conn = self.get_connection()
        result = conn.execute(
            "SELECT * FROM user_data WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        ).fetchall()
        return result
    
    def get_global_prayers(self):
        """Get all public prayers that haven't been answered yet."""
        conn = self.get_connection()
        query = """
            SELECT ud.*, u.name as user_name, u.profile_pic as user_pic
            FROM user_data ud
            JOIN users u ON ud.user_id = u.id
            WHERE ud.is_public = TRUE AND ud.is_answered = FALSE
            ORDER BY ud.created_at DESC
        """
        result = conn.execute(query).fetchall()
        return result
    
    def get_answered_prayers(self):
        """Get all public prayers that have been answered."""
        conn = self.get_connection()
        query = """
            SELECT ud.*, u.name as user_name, u.profile_pic as user_pic
            FROM user_data ud
            JOIN users u ON ud.user_id = u.id
            WHERE ud.is_public = TRUE AND ud.is_answered = TRUE
            ORDER BY ud.answered_at DESC
        """
        result = conn.execute(query).fetchall()
        return result
    
    def mark_prayer_as_answered(self, prayer_id, answer_text):
        """Mark a prayer as answered with the given answer text."""
        conn = self.get_connection()
        conn.execute("""
            UPDATE user_data
            SET is_answered = TRUE, answer_text = ?, answered_at = ?
            WHERE id = ?
        """, (answer_text, datetime.now(), prayer_id))
    
    def add_prayer_interaction(self, prayer_id, user_id, interaction_type):
        """Add an interaction (pray, praise) to a prayer."""
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO prayer_interactions (prayer_id, user_id, interaction_type, created_at)
            VALUES (?, ?, ?, ?)
        """, (prayer_id, user_id, interaction_type, datetime.now()))
    
    def get_prayer_interaction_count(self, prayer_id, interaction_type):
        """Get the count of a specific interaction type for a prayer."""
        conn = self.get_connection()
        result = conn.execute("""
            SELECT COUNT(*) FROM prayer_interactions
            WHERE prayer_id = ? AND interaction_type = ?
        """, (prayer_id, interaction_type)).fetchone()
        return result[0] if result else 0

    def close(self):
        """Close the database connection."""
        self.conn.close()

# Create a singleton instance
db = Database()
