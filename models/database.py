from models.db_core import DBCore
from models.user_db import UserDB
from models.prayer_db import PrayerDB
from models.interaction_db import InteractionDB
from models.fellowship_db import FellowshipDB
from models.moderation_db import ModerationDB

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
        self.fellowship = FellowshipDB(self.core)
        self.moderation = ModerationDB(self.core)
        
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
    
    # Fellowship methods
    def create_fellowship(self, name, description, created_by, is_private=True, image_url=None):
        return self.fellowship.create_fellowship(name, description, created_by, is_private, image_url)
    
    def update_fellowship(self, fellowship_id, name=None, description=None, image_url=None, is_private=None):
        return self.fellowship.update_fellowship(fellowship_id, name, description, image_url, is_private)
    
    def delete_fellowship(self, fellowship_id):
        return self.fellowship.delete_fellowship(fellowship_id)
    
    def get_fellowship(self, fellowship_id):
        return self.fellowship.get_fellowship(fellowship_id)
    
    def get_public_fellowships(self):
        return self.fellowship.get_public_fellowships()
    
    def get_user_fellowships(self, user_id):
        return self.fellowship.get_user_fellowships(user_id)
    
    def add_fellowship_member(self, fellowship_id, user_id, role='member'):
        return self.fellowship.add_fellowship_member(fellowship_id, user_id, role)
    
    def remove_fellowship_member(self, fellowship_id, user_id):
        return self.fellowship.remove_fellowship_member(fellowship_id, user_id)
    
    def get_fellowship_members(self, fellowship_id):
        return self.fellowship.get_fellowship_members(fellowship_id)
    
    def is_fellowship_member(self, fellowship_id, user_id):
        return self.fellowship.is_fellowship_member(fellowship_id, user_id)
    
    def join_fellowship_with_code(self, join_code, user_id):
        return self.fellowship.join_fellowship_with_code(join_code, user_id)
    
    def share_prayer_with_fellowship(self, prayer_id, fellowship_id):
        return self.fellowship.share_prayer_with_fellowship(prayer_id, fellowship_id)
    
    def unshare_prayer_from_fellowship(self, prayer_id, fellowship_id):
        return self.fellowship.unshare_prayer_from_fellowship(prayer_id, fellowship_id)
    
    def get_fellowship_prayers(self, fellowship_id):
        return self.fellowship.get_fellowship_prayers(fellowship_id)
    
    def get_prayer_fellowships(self, prayer_id):
        return self.fellowship.get_prayer_fellowships(prayer_id)
    
    def regenerate_join_code(self, fellowship_id):
        return self.fellowship.regenerate_join_code(fellowship_id)
    
    # Moderation methods
    def report_prayer(self, prayer_id, reported_by, reason):
        return self.moderation.report_prayer(prayer_id, reported_by, reason)
    
    def get_pending_reports(self):
        return self.moderation.get_pending_reports()
    
    def handle_report(self, report_id, reviewer_id, action, notes=None):
        return self.moderation.handle_report(report_id, reviewer_id, action, notes)
    
    def update_user_role(self, user_id, new_role):
        return self.moderation.update_user_role(user_id, new_role)
    
    def update_user_status(self, user_id, new_status):
        return self.moderation.update_user_status(user_id, new_status)
    
    def adjust_user_reputation(self, user_id, delta):
        return self.moderation.adjust_user_reputation(user_id, delta)
    
    def get_user_role(self, user_id):
        return self.moderation.get_user_role(user_id)
    
    def is_admin_or_moderator(self, user_id):
        return self.moderation.is_admin_or_moderator(user_id)
    
    def get_abuse_report_count(self, prayer_id):
        return self.moderation.get_abuse_report_count(prayer_id)
    
    def check_user_status(self, user_id):
        return self.moderation.check_user_status(user_id)
    
    def get_user_activity_metrics(self, user_id):
        return self.moderation.get_user_activity_metrics(user_id)
    
    def close(self):
        """Close the database connection."""
        self.core.close()

# Create a singleton instance				      <
db = Database()