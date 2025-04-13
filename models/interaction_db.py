from datetime import datetime
from models.db_core import DBCore

class InteractionDB(DBCore):
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