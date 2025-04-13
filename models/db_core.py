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
        finally:
            conn.close()
    
    def close(self):
        """Close the database connection."""
        if hasattr(g, 'db_conn'):
            g.db_conn.close()