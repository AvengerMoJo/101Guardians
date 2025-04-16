import duckdb
from flask import g
import os

class DBCore:
    def __init__(self, db_path='app.db'):
        """Initialize the DuckDB database connection."""
        self.db_path = db_path
        
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
        except Exception as e:
            print(f"Error creating users table: {e}")
        # Add user roles and status fields to users table
        try:
            conn.execute("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'")
        except: # Column might already exist
            pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN status VARCHAR DEFAULT 'active'")
        except: # Column might already exist
            pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN reputation INTEGER DEFAULT 0")
        except: # Column might already exist
            pass
        try:
            # Create sequence for report IDs if it doesn't exist
            conn.execute("CREATE SEQUENCE IF NOT EXISTS report_id_seq")
            # Reports table for abuse monitoring
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY DEFAULT(nextval('report_id_seq')),
                    reported_prayer_id INTEGER,
                    reported_by VARCHAR,
                    reason VARCHAR,
                    status VARCHAR DEFAULT 'pending',
                    created_at TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    reviewer_id VARCHAR,
                    FOREIGN KEY (reported_prayer_id) REFERENCES user_data(id),
                    FOREIGN KEY (reported_by) REFERENCES users(id),
                    FOREIGN KEY (reviewer_id) REFERENCES users(id)
                )
            """)
        except Exception as e:
            print(f"Error setting up moderation tables: {e}")
        try:
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
        except Exception as e:
            print(f"Error creating sessions table: {e}")
        try:
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
        except Exception as e:
            print(f"Error creating user_data table: {e}")
        try:    
            conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS prayer_interactions_id_seq;
                
                CREATE TABLE IF NOT EXISTS prayer_interactions (
                    id INTEGER PRIMARY KEY DEFAULT(nextval('prayer_interactions_id_seq')),
                    prayer_id INTEGER,
                    user_id VARCHAR,
                    interaction_type VARCHAR,  -- 'pray', 'praise', etc.
                    created_at TIMESTAMP,
                    FOREIGN KEY (prayer_id) REFERENCES user_data(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        except Exception as e:
            print(f"Error creating prayer_interactions table: {e}")
        try:
            # Create sequence for fellowship IDs if it doesn't exist
            conn.execute("CREATE SEQUENCE IF NOT EXISTS fellowship_id_seq")
            # Fellowship groups table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fellowships (
                    id INTEGER PRIMARY KEY DEFAULT(nextval('fellowship_id_seq')),
                    name VARCHAR NOT NULL,
                    description VARCHAR,
                    image_url VARCHAR,
                    is_private BOOLEAN DEFAULT TRUE,
                    join_code VARCHAR,
                    created_by VARCHAR,
                    created_at TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            # Fellowship memberships table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fellowship_members (
                    fellowship_id INTEGER,
                    user_id VARCHAR,
                    role VARCHAR DEFAULT 'member',
                    joined_at TIMESTAMP,
                    PRIMARY KEY (fellowship_id, user_id),
                    FOREIGN KEY (fellowship_id) REFERENCES fellowships(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            # Prayer to fellowship relationship
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fellowship_prayers (
                    prayer_id INTEGER,
                    fellowship_id INTEGER,
                    shared_at TIMESTAMP,
                    PRIMARY KEY (prayer_id, fellowship_id),
                    FOREIGN KEY (prayer_id) REFERENCES user_data(id),
                    FOREIGN KEY (fellowship_id) REFERENCES fellowships(id)
                )
            """)
        except Exception as e:
            print(f"Error creating fellowships tables: {e}")
        finally:
            conn.close()
    
    def close(self):
        """Close the database connection."""
        if hasattr(g, 'db_conn'):
            g.db_conn.close()