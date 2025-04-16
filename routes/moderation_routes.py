from flask import request, jsonify, session, current_app as app
from auth.auth_middleware import login_required
from models.database import db
from functools import wraps

# Middleware to check if user is admin or moderator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        # Check if user is admin or moderator
        if not db.is_admin_or_moderator(user_id):
            return jsonify({'error': 'Admin privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def init_moderation_routes(app):
    @app.route('/api/reports', methods=['POST'])
    @login_required
    def report_prayer():
        """Report a prayer for abuse"""
        user_id = session.get('user_id')
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if 'prayer_id' not in data:
                return jsonify({'error': 'Prayer ID is required'}), 400
            
            if 'reason' not in data or not data['reason'].strip():
                return jsonify({'error': 'Reason is required'}), 400
            
            prayer_id = data['prayer_id']
            reason = data['reason'].strip()
            
            # Verify the prayer exists
            prayer = db.get_prayer(prayer_id)
            
            if not prayer:
                return jsonify({'error': 'Prayer not found'}), 404
            
            # Submit the report
            success = db.report_prayer(prayer_id, user_id, reason)
            
            if not success:
                return jsonify({'error': 'Failed to submit report'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error reporting prayer: {str(e)}")
            return jsonify({'error': 'An error occurred while submitting report'}), 500

    @app.route('/api/reports', methods=['GET'])
    @login_required
    @admin_required
    def get_reports():
        """Get pending reports (admin/moderator only)"""
        try:
            # Get pending reports
            reports = db.get_pending_reports()
            
            # Format for JSON response
            reports_data = []
            for report in reports:
                reports_data.append({
                    'id': report[0],
                    'prayer_id': report[1],
                    'reported_by': report[2],
                    'reason': report[3],
                    'status': report[4],
                    'created_at': report[5].isoformat() if report[5] else None,
                    'prayer_title': report['prayer_title'],
                    'prayer_content': report['prayer_content'],
                    'reporter_name': report['reporter_name'],
                    'prayer_author_name': report['prayer_author_name']
                })
            
            return jsonify({'reports': reports_data})
        except Exception as e:
            app.logger.error(f"Error getting reports: {str(e)}")
            return jsonify({'error': 'An error occurred while getting reports'}), 500

    @app.route('/api/reports/<int:report_id>', methods=['PUT'])
    @login_required
    @admin_required
    def handle_report(report_id):
        """Handle a report (admin/moderator only)"""
        user_id = session.get('user_id')
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if 'action' not in data or not data['action'].strip():
                return jsonify({'error': 'Action is required'}), 400
            
            action = data['action'].strip()
            notes = data.get('notes', '').strip()
            
            if action not in ('reviewed', 'actioned', 'dismissed'):
                return jsonify({'error': 'Invalid action'}), 400
            
            # Handle the report
            success = db.handle_report(report_id, user_id, action, notes)
            
            if not success:
                return jsonify({'error': 'Failed to handle report'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error handling report: {str(e)}")
            return jsonify({'error': 'An error occurred while handling report'}), 500

    @app.route('/api/users/<path:user_id>/role', methods=['PUT'])
    @login_required
    @admin_required
    def update_user_role(user_id):
        """Update a user's role (admin only)"""
        admin_id = session.get('user_id')
        
        # Only true admins can change roles
        admin_role = db.get_user_role(admin_id)
        if admin_role != 'admin':
            return jsonify({'error': 'Only administrators can change user roles'}), 403
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if 'role' not in data or not data['role'].strip():
                return jsonify({'error': 'Role is required'}), 400
            
            new_role = data['role'].strip()
            
            if new_role not in ('admin', 'moderator', 'user'):
                return jsonify({'error': 'Invalid role'}), 400
            
            # Update the user's role
            success = db.update_user_role(user_id, new_role)
            
            if not success:
                return jsonify({'error': 'Failed to update user role'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error updating user role: {str(e)}")
            return jsonify({'error': 'An error occurred while updating user role'}), 500

    @app.route('/api/users/<path:user_id>/status', methods=['PUT'])
    @login_required
    @admin_required
    def update_user_status(user_id):
        """Update a user's status (admin/moderator only)"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if 'status' not in data or not data['status'].strip():
                return jsonify({'error': 'Status is required'}), 400
            
            new_status = data['status'].strip()
            
            if new_status not in ('active', 'suspended', 'banned'):
                return jsonify({'error': 'Invalid status'}), 400
            
            # Update the user's status
            success = db.update_user_status(user_id, new_status)
            
            if not success:
                return jsonify({'error': 'Failed to update user status'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error updating user status: {str(e)}")
            return jsonify({'error': 'An error occurred while updating user status'}), 500

    @app.route('/api/users/<path:user_id>/reputation', methods=['PUT'])
    @login_required
    @admin_required
    def adjust_user_reputation(user_id):
        """Adjust a user's reputation (admin/moderator only)"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if 'delta' not in data:
                return jsonify({'error': 'Reputation delta is required'}), 400
            
            try:
                delta = int(data['delta'])
            except ValueError:
                return jsonify({'error': 'Reputation delta must be an integer'}), 400
            
            # Adjust the user's reputation
            success = db.adjust_user_reputation(user_id, delta)
            
            if not success:
                return jsonify({'error': 'Failed to adjust user reputation'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error adjusting user reputation: {str(e)}")
            return jsonify({'error': 'An error occurred while adjusting user reputation'}), 500

    @app.route('/api/moderation/stats', methods=['GET'])
    @login_required
    @admin_required
    def get_moderation_stats():
        """Get moderation dashboard statistics (admin/moderator only)"""
        try:
            # Get count of pending reports
            pending_reports = db.get_pending_reports()
            pending_count = len(pending_reports)
            
            # Get user metrics
            user_id = session.get('user_id')
            current_user_role = db.get_user_role(user_id)
            
            return jsonify({
                'pending_reports': pending_count,
                'user_role': current_user_role
            })
        except Exception as e:
            app.logger.error(f"Error getting moderation stats: {str(e)}")
            return jsonify({'error': 'An error occurred while getting moderation statistics'}), 500

    # Middleware to verify user account status before processing requests
    @app.before_request
    def check_user_account_status():
        """Check if user account is active, suspended, or banned"""
        # Skip for login/logout routes
        if request.endpoint in ('login', 'logout', 'index', 'line_login', 'google_login',
                               'line_authorize', 'google_authorize', 'static'):
            return None
        
        # Skip if not authenticated
        if 'user_id' not in session:
            return None
        
        user_id = session.get('user_id')
        status = db.check_user_status(user_id)
        
        if status == 'suspended':
            # Allow access to profile page only
            if request.endpoint != 'profile':
                return jsonify({
                    'error': 'Your account has been temporarily suspended. Please check your profile for details.'
                }), 403
        
        elif status == 'banned':
            # Clear session and redirect to login
            session.clear()
            return jsonify({
                'error': 'Your account has been banned for violating community guidelines.',
                'redirect': '/login'
            }), 403
        
        return None