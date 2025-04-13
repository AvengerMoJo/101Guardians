from models.db_core import DBCore
from models.user_db import UserDB
from models.prayer_db import PrayerDB
from models.interaction_db import InteractionDB

class Database(DBCore, UserDB, PrayerDB, InteractionDB):
    def __init__(self, db_path='app.db'):
        """Initialize the DuckDB database connection."""
        super().__init__(db_path)
        self.setup_tables()

# Create a singleton instance
db = Database()