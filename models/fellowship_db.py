from datetime import datetime
import secrets

class FellowshipDB:
    def __init__(self, db_core):
        """Initialize with the core DB connection handler."""
        self.db_core = db_core
    
    def setup_tables(self):
        """Set up fellowship-related tables if they don't exist."""
        conn = self.db_core.get_connection()
        
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
            print(f"Error setting up fellowship tables: {e}")

    def create_fellowship(self, name, description, created_by, is_private=True, image_url=None):
        """Create a new fellowship group."""
        conn = self.db_core.get_connection()
        
        # Generate a unique join code for private fellowships
        join_code = secrets.token_hex(4) if is_private else None
        
        try:
            conn.execute("""
                INSERT INTO fellowships (name, description, image_url, is_private, join_code, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, description, image_url, is_private, join_code, created_by, datetime.now()))
            
            # Get the ID of the newly created fellowship
            result = conn.execute("SELECT MAX(id) FROM fellowships").fetchone()
            fellowship_id = result[0] if result else None
            
            if fellowship_id:
                # Add the creator as an admin member
                self.add_fellowship_member(fellowship_id, created_by, 'admin')
                return fellowship_id
            return None
        except Exception as e:
            print(f"Error creating fellowship: {e}")
            return None

    def update_fellowship(self, fellowship_id, name=None, description=None, image_url=None, is_private=None):
        """Update fellowship details."""
        conn = self.db_core.get_connection()
        
        # Build the update query dynamically based on provided parameters
        update_parts = []
        params = []
        
        if name is not None:
            update_parts.append("name = ?")
            params.append(name)
        
        if description is not None:
            update_parts.append("description = ?")
            params.append(description)
        
        if image_url is not None:
            update_parts.append("image_url = ?")
            params.append(image_url)
        
        if is_private is not None:
            update_parts.append("is_private = ?")
            params.append(is_private)
            
            # If changing from private to public, remove the join code
            if not is_private:
                update_parts.append("join_code = NULL")
            # If changing from public to private, generate a new join code
            elif is_private:
                join_code = secrets.token_hex(4)
                update_parts.append("join_code = ?")
                params.append(join_code)
        
        if not update_parts:
            return False  # No updates to make
        
        # Build and execute the final query
        query = f"UPDATE fellowships SET {', '.join(update_parts)} WHERE id = ?"
        params.append(fellowship_id)
        
        try:
            conn.execute(query, params)
            return True
        except Exception as e:
            print(f"Error updating fellowship: {e}")
            return False

    def delete_fellowship(self, fellowship_id):
        """Delete a fellowship and all its associations."""
        conn = self.db_core.get_connection()
        
        try:
            # Delete all prayer associations
            conn.execute("DELETE FROM fellowship_prayers WHERE fellowship_id = ?", (fellowship_id,))
            
            # Delete all member associations
            conn.execute("DELETE FROM fellowship_members WHERE fellowship_id = ?", (fellowship_id,))
            
            # Delete the fellowship
            conn.execute("DELETE FROM fellowships WHERE id = ?", (fellowship_id,))
            return True
        except Exception as e:
            print(f"Error deleting fellowship: {e}")
            return False

    def get_fellowship(self, fellowship_id):
        """Get fellowship details by ID."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT f.*, u.name as creator_name, u.profile_pic as creator_pic,
                       (SELECT COUNT(*) FROM fellowship_members WHERE fellowship_id = f.id) as member_count
                FROM fellowships f
                LEFT JOIN users u ON f.created_by = u.id
                WHERE f.id = ?
            """, (fellowship_id,)).fetchone()
            return result
        except Exception as e:
            print(f"Error getting fellowship: {e}")
            return None

    def get_public_fellowships(self):
        """Get all public fellowships."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT f.*, u.name as creator_name, u.profile_pic as creator_pic,
                       (SELECT COUNT(*) FROM fellowship_members WHERE fellowship_id = f.id) as member_count
                FROM fellowships f
                LEFT JOIN users u ON f.created_by = u.id
                WHERE f.is_private = FALSE
                ORDER BY f.created_at DESC
            """).fetchall()
            return result
        except Exception as e:
            print(f"Error getting public fellowships: {e}")
            return []

    def get_user_fellowships(self, user_id):
        """Get all fellowships that a user is a member of."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT f.*, fm.role as user_role, u.name as creator_name, u.profile_pic as creator_pic,
                       (SELECT COUNT(*) FROM fellowship_members WHERE fellowship_id = f.id) as member_count
                FROM fellowships f
                JOIN fellowship_members fm ON f.id = fm.fellowship_id
                LEFT JOIN users u ON f.created_by = u.id
                WHERE fm.user_id = ?
                ORDER BY f.created_at DESC
            """, (user_id,)).fetchall()
            return result
        except Exception as e:
            print(f"Error getting user fellowships: {e}")
            return []

    def add_fellowship_member(self, fellowship_id, user_id, role='member'):
        """Add a user to a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            # Check if user is already a member
            existing = conn.execute("""
                SELECT * FROM fellowship_members 
                WHERE fellowship_id = ? AND user_id = ?
            """, (fellowship_id, user_id)).fetchone()
            
            if existing:
                # Update role if different
                if existing[2] != role:
                    conn.execute("""
                        UPDATE fellowship_members 
                        SET role = ? 
                        WHERE fellowship_id = ? AND user_id = ?
                    """, (role, fellowship_id, user_id))
                return True
            
            # Add new member
            conn.execute("""
                INSERT INTO fellowship_members (fellowship_id, user_id, role, joined_at)
                VALUES (?, ?, ?, ?)
            """, (fellowship_id, user_id, role, datetime.now()))
            return True
        except Exception as e:
            print(f"Error adding fellowship member: {e}")
            return False

    def remove_fellowship_member(self, fellowship_id, user_id):
        """Remove a user from a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                DELETE FROM fellowship_members 
                WHERE fellowship_id = ? AND user_id = ?
            """, (fellowship_id, user_id))
            return True
        except Exception as e:
            print(f"Error removing fellowship member: {e}")
            return False

    def get_fellowship_members(self, fellowship_id):
        """Get all members of a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT fm.*, u.name, u.email, u.profile_pic
                FROM fellowship_members fm
                JOIN users u ON fm.user_id = u.id
                WHERE fm.fellowship_id = ?
                ORDER BY fm.role, fm.joined_at
            """, (fellowship_id,)).fetchall()
            return result
        except Exception as e:
            print(f"Error getting fellowship members: {e}")
            return []

    def is_fellowship_member(self, fellowship_id, user_id):
        """Check if a user is a member of a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT role FROM fellowship_members 
                WHERE fellowship_id = ? AND user_id = ?
            """, (fellowship_id, user_id)).fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error checking fellowship membership: {e}")
            return None

    def join_fellowship_with_code(self, join_code, user_id):
        """Join a fellowship using a join code."""
        conn = self.db_core.get_connection()
        
        try:
            # Find the fellowship with this join code
            fellowship = conn.execute("""
                SELECT id FROM fellowships 
                WHERE join_code = ?
            """, (join_code,)).fetchone()
            
            if not fellowship:
                return False, "Invalid join code"
            
            fellowship_id = fellowship[0]
            
            # Check if user is already a member
            if self.is_fellowship_member(fellowship_id, user_id):
                return False, "Already a member"
            
            # Add the user as a member
            self.add_fellowship_member(fellowship_id, user_id)
            return True, fellowship_id
        except Exception as e:
            print(f"Error joining fellowship with code: {e}")
            return False, str(e)

    def share_prayer_with_fellowship(self, prayer_id, fellowship_id):
        """Share a prayer with a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            # Check if already shared
            existing = conn.execute("""
                SELECT * FROM fellowship_prayers 
                WHERE prayer_id = ? AND fellowship_id = ?
            """, (prayer_id, fellowship_id)).fetchone()
            
            if existing:
                return True  # Already shared
            
            # Share the prayer
            conn.execute("""
                INSERT INTO fellowship_prayers (prayer_id, fellowship_id, shared_at)
                VALUES (?, ?, ?)
            """, (prayer_id, fellowship_id, datetime.now()))
            return True
        except Exception as e:
            print(f"Error sharing prayer with fellowship: {e}")
            return False

    def unshare_prayer_from_fellowship(self, prayer_id, fellowship_id):
        """Remove a prayer from a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                DELETE FROM fellowship_prayers 
                WHERE prayer_id = ? AND fellowship_id = ?
            """, (prayer_id, fellowship_id))
            return True
        except Exception as e:
            print(f"Error unsharing prayer from fellowship: {e}")
            return False

    def get_fellowship_prayers(self, fellowship_id):
        """Get all prayers shared with a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT ud.*, u.name as user_name, u.profile_pic as user_pic, fp.shared_at
                FROM user_data ud
                JOIN fellowship_prayers fp ON ud.id = fp.prayer_id
                JOIN users u ON ud.user_id = u.id
                WHERE fp.fellowship_id = ?
                ORDER BY fp.shared_at DESC
            """, (fellowship_id,)).fetchall()
            return result
        except Exception as e:
            print(f"Error getting fellowship prayers: {e}")
            return []

    def get_prayer_fellowships(self, prayer_id):
        """Get all fellowships a prayer is shared with."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT f.*, fp.shared_at
                FROM fellowships f
                JOIN fellowship_prayers fp ON f.id = fp.fellowship_id
                WHERE fp.prayer_id = ?
                ORDER BY fp.shared_at DESC
            """, (prayer_id,)).fetchall()
            return result
        except Exception as e:
            print(f"Error getting prayer fellowships: {e}")
            return []

    def regenerate_join_code(self, fellowship_id):
        """Generate a new join code for a fellowship."""
        conn = self.db_core.get_connection()
        
        try:
            # Generate new code
            new_code = secrets.token_hex(4)
            
            # Update the fellowship
            conn.execute("""
                UPDATE fellowships SET join_code = ? WHERE id = ?
            """, (new_code, fellowship_id))
            
            return new_code
        except Exception as e:
            print(f"Error regenerating join code: {e}")
            return None
