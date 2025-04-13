from datetime import datetime
from models.db_core import DBCore

class UserDB(DBCore):
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