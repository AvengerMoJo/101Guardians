from models.db_core import DBCore
from models.user_db import UserDB
from models.prayer_db import PrayerDB
from models.interaction_db import InteractionDB

class Database:
    """
    Main database class that combines all functionality from different database modules.
    """
    def __init__(self, db_path='app.db'):
        """Initialize the Database with all components."""
        # Create a single DBCore instance that will be shared
        self.core = DBCore(db_path)
        
        # Initialize DB component instances with the shared core
        self.user = UserDB(self.core)
        self.prayer = PrayerDB(self.core)
        self.interaction = InteractionDB(self.core)
        
        # Set up tables
        self.core.setup_tables()
    
    # User methods
    def add_user(self, user_id, email, name, profile_pic, auth_provider):
        return self.user.add_user(user_id, email, name, profile_pic, auth_provider)
    
    def get_user(self, user_id):
        return self.user.get_user(user_id)
    
    def create_session(self, session_id, user_id, expires_at):
        return self.user.create_session(session_id, user_id, expires_at)
    
    def get_session(self, session_id):
        return self.user.get_session(session_id)
    
    # Prayer methods
    def add_prayer(self, user_id, title, content, is_public=False):
        return self.prayer.add_prayer(user_id, title, content, is_public)

    def get_prayer(self, prayer_id):
        return self.prayer.get_prayer(prayer_id)

    def update_prayer(self, prayer_id, title, content, is_public=None):
        return self.prayer.update_prayer(prayer_id, title, content, is_public)

    def delete_prayer(self, prayer_id):
        return self.prayer.delete_prayer(prayer_id)
        
    def get_user_prayers(self, user_id):
        return self.prayer.get_user_prayers(user_id)
    
    def get_global_prayers(self):
        return self.prayer.get_global_prayers()
    
    def get_answered_prayers(self):
        return self.prayer.get_answered_prayers()
    
    def mark_prayer_as_answered(self, prayer_id, answer_text):
        return self.prayer.mark_prayer_as_answered(prayer_id, answer_text)
    
    # Interaction methods
    def add_prayer_interaction(self, prayer_id, user_id, interaction_type):
        return self.interaction.add_prayer_interaction(prayer_id, user_id, interaction_type)
    
    def get_prayer_interaction_count(self, prayer_id, interaction_type):
        return self.interaction.get_prayer_interaction_count(prayer_id, interaction_type)
    
    def close(self):
        """Close the database connection."""
        self.core.close()

# Create a singleton instance
db = Database()