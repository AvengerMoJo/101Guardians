from datetime import datetime

class ModerationDB:
    def __init__(self, db_core):
        """Initialize with the core DB connection handler."""
        self.db_core = db_core
    
    def report_prayer(self, prayer_id, reported_by, reason):
        """Submit a report for a prayer."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                INSERT INTO reports (reported_prayer_id, reported_by, reason, created_at)
                VALUES (?, ?, ?, ?)
            """, (prayer_id, reported_by, reason, datetime.now()))
            return True
        except Exception as e:
            print(f"Error reporting prayer: {e}")
            return False

    def get_pending_reports(self):
        """Get all pending reports."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT r.*, 
                       ud.title as prayer_title, ud.content as prayer_content, 
                       u1.name as reporter_name, u2.name as prayer_author_name
                FROM reports r
                JOIN user_data ud ON r.reported_prayer_id = ud.id
                JOIN users u1 ON r.reported_by = u1.id
                JOIN users u2 ON ud.user_id = u2.id
                WHERE r.status = 'pending'
                ORDER BY r.created_at DESC
            """).fetchall()
            return result
        except Exception as e:
            print(f"Error getting pending reports: {e}")
            return []

    def handle_report(self, report_id, reviewer_id, action, notes=None):
        """Handle a report - mark as reviewed, actioned, or dismissed."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                UPDATE reports
                SET status = ?, reviewer_id = ?, reviewed_at = ?
                WHERE id = ?
            """, (action, reviewer_id, datetime.now(), report_id))
            return True
        except Exception as e:
            print(f"Error handling report: {e}")
            return False

    def update_user_role(self, user_id, new_role):
        """Update a user's role (user, moderator, admin)."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                UPDATE users
                SET role = ?
                WHERE id = ?
            """, (new_role, user_id))
            return True
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False

    def update_user_status(self, user_id, new_status):
        """Update a user's status (active, suspended, banned)."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                UPDATE users
                SET status = ?
                WHERE id = ?
            """, (new_status, user_id))
            return True
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False

    def adjust_user_reputation(self, user_id, delta):
        """Adjust a user's reputation score."""
        conn = self.db_core.get_connection()
        
        try:
            conn.execute("""
                UPDATE users
                SET reputation = reputation + ?
                WHERE id = ?
            """, (delta, user_id))
            return True
        except Exception as e:
            print(f"Error adjusting user reputation: {e}")
            return False

    def get_user_role(self, user_id):
        """Get a user's role."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT role FROM users WHERE id = ?
            """, (user_id,)).fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user role: {e}")
            return None

    def is_admin_or_moderator(self, user_id):
        """Check if a user is an admin or moderator."""
        role = self.get_user_role(user_id)
        return role in ('admin', 'moderator')
    
    def get_abuse_report_count(self, prayer_id):
        """Get the number of reports for a specific prayer."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT COUNT(*) FROM reports 
                WHERE reported_prayer_id = ?
            """, (prayer_id,)).fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting abuse report count: {e}")
            return 0

    def check_user_status(self, user_id):
        """Check if a user is active, suspended, or banned."""
        conn = self.db_core.get_connection()
        
        try:
            result = conn.execute("""
                SELECT status FROM users WHERE id = ?
            """, (user_id,)).fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error checking user status: {e}")
            return None

    def get_user_activity_metrics(self, user_id):
        """Get activity metrics for a user."""
        conn = self.db_core.get_connection()
        
        try:
            # Get prayer count
            prayer_count = conn.execute("""
                SELECT COUNT(*) FROM user_data WHERE user_id = ?
            """, (user_id,)).fetchone()[0]
            
            # Get reports submitted count
            reports_submitted = conn.execute("""
                SELECT COUNT(*) FROM reports WHERE reported_by = ?
            """, (user_id,)).fetchone()[0]
            
            # Get reports received count
            reports_received = conn.execute("""
                SELECT COUNT(*) FROM reports 
                JOIN user_data ON reports.reported_prayer_id = user_data.id
                WHERE user_data.user_id = ?
            """, (user_id,)).fetchone()[0]
            
            # Get reputation
            reputation = conn.execute("""
                SELECT reputation FROM users WHERE id = ?
            """, (user_id,)).fetchone()[0]
            
            return {
                'prayer_count': prayer_count,
                'reports_submitted': reports_submitted,
                'reports_received': reports_received,
                'reputation': reputation
            }
        except Exception as e:
            print(f"Error getting user activity metrics: {e}")
            return {}
