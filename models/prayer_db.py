from datetime import datetime

class PrayerDB:
    def __init__(self, db_core):
        """Initialize with the core DB connection handler."""
        self.db_core = db_core
    
    def add_prayer(self, user_id, title, content, is_public=False):
        """Add a prayer for a user."""
        conn = self.db_core.get_connection()
        conn.execute("""
            INSERT INTO user_data (user_id, title, content, is_public, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, content, is_public, datetime.now()))
    
    def get_user_prayers(self, user_id):
        """Get all prayers for a user."""
        conn = self.db_core.get_connection()
        result = conn.execute(
            "SELECT * FROM user_data WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        ).fetchall()
        return result
    
    def get_global_prayers(self):
        """Get all public prayers that haven't been answered yet."""
        conn = self.db_core.get_connection()
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
        conn = self.db_core.get_connection()
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
        conn = self.db_core.get_connection()
        conn.execute("""
            UPDATE user_data
            SET is_answered = TRUE, answer_text = ?, answered_at = ?
            WHERE id = ?
        """, (answer_text, datetime.now(), prayer_id))