from flask import request, jsonify, session, current_app as app
from auth.auth_middleware import login_required
from models.database import db

def init_api_routes(app):
    @app.route('/api/prayers', methods=['GET'])
    @login_required
    def get_prayers():
        user_id = session.get('user_id')
        user_prayers = db.get_user_prayers(user_id)
        
        # Convert to a list of dictionaries
        result = []
        for prayer in user_prayers:
            result.append({
                'id': prayer[0],
                'title': prayer[2],
                'content': prayer[3],
                'is_public': prayer[4],
                'is_answered': prayer[5],
                'answer': prayer[6],
                'created_at': prayer[8].isoformat() if prayer[8] else None
            })
        
        return jsonify(result)

    @app.route('/api/prayers', methods=['POST'])
    @login_required
    def add_prayer():
        user_id = session.get('user_id')
        
        # Better error handling for the request body
        try:
            data = request.get_json()
            if not data:
                app.logger.warning("Failed to parse JSON data from request")
                return jsonify({'error': 'Invalid JSON data'}), 400
        except Exception as e:
            app.logger.error(f"Error parsing JSON: {str(e)}")
            return jsonify({'error': 'Could not parse request data'}), 400
        
        # Validate required fields
        if 'title' not in data or not data['title'].strip():
            app.logger.warning("Missing title in request")
            return jsonify({'error': 'Title is required'}), 400
            
        if 'content' not in data or not data['content'].strip():
            app.logger.warning("Missing content in request")
            return jsonify({'error': 'Content is required'}), 400
        
        # Get public status
        is_public = data.get('is_public', False)
        
        # Sanitize inputs (basic example)
        title = data['title'].strip()
        content = data['content'].strip()
        
        # Log the attempted prayer addition
        app.logger.info(f"Adding prayer for user {user_id}: title='{title}', public={is_public}")
        
        try:
            # Save to database
            db.add_prayer(user_id, title, content, is_public)
            app.logger.info(f"Successfully added prayer for user {user_id}")
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Database error adding prayer for user {user_id}: {str(e)}")
            return jsonify({'error': 'Failed to save prayer due to a server error'}), 500

    @app.route('/api/prayers/<int:prayer_id>', methods=['PUT'])
    @login_required
    def update_prayer(prayer_id):
        user_id = session.get('user_id')
        try:
            # Verify the prayer belongs to the user
            prayer = db.get_prayer(prayer_id)
            if not prayer or prayer[1] != user_id:
                return jsonify({'error': 'Prayer not found or you do not have permission to edit it'}), 403
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400

            # Validate required fields
            if 'title' not in data or not data['title'].strip():
                return jsonify({'error': 'Title is required'}), 400
            if 'content' not in data or not data['content'].strip():
                return jsonify({'error': 'Content is required'}), 400
            # Get public status
            is_public = data.get('is_public', prayer[4])
            # Sanitize inputs
            title = data['title'].strip()
            content = data['content'].strip()
            # Update the prayer
            db.update_prayer(prayer_id, title, content, is_public)
            app.logger.info(f"Successfully updated prayer {prayer_id} for user {user_id}")
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error updating prayer {prayer_id}: {str(e)}")
            return jsonify({'error': 'Failed to update prayer'}), 500

    @app.route('/api/prayers/<int:prayer_id>', methods=['DELETE'])
    @login_required
    def delete_prayer(prayer_id):
        user_id = session.get('user_id')
        try:
            # Verify the prayer belongs to the user
            prayer = db.get_prayer(prayer_id)
            if not prayer or prayer[1] != user_id:
                return jsonify({'error': 'Prayer not found or you do not have permission to delete it'}), 403
            # Delete the prayer
            db.delete_prayer(prayer_id)
            app.logger.info(f"Successfully deleted prayer {prayer_id} for user {user_id}")
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error deleting prayer {prayer_id}: {str(e)}")
            return jsonify({'error': 'Failed to delete prayer'}), 500
        
    @app.route('/api/prayers/<int:prayer_id>/answer', methods=['POST'])
    @login_required
    def answer_prayer(prayer_id):
        user_id = session.get('user_id')
        
        try:
            data = request.get_json()
            if not data or 'answer' not in data:
                return jsonify({'error': 'Answer text is required'}), 400
            
            answer_text = data['answer'].strip()
            if not answer_text:
                return jsonify({'error': 'Answer cannot be empty'}), 400
            
            # Mark the prayer as answered
            db.mark_prayer_as_answered(prayer_id, answer_text)
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error marking prayer {prayer_id} as answered: {str(e)}")
            return jsonify({'error': 'Failed to update prayer'}), 500

    @app.route('/api/prayers/<int:prayer_id>/interact', methods=['POST'])
    @login_required
    def interact_with_prayer(prayer_id):
        user_id = session.get('user_id')
        
        try:
            data = request.get_json()
            if not data or 'type' not in data:
                return jsonify({'error': 'Interaction type is required'}), 400
            
            interaction_type = data['type']
            if interaction_type not in ['pray', 'praise']:
                return jsonify({'error': 'Invalid interaction type'}), 400
            
            # Add the interaction
            db.add_prayer_interaction(prayer_id, user_id, interaction_type)
            
            # Get updated count
            count = db.get_prayer_interaction_count(prayer_id, interaction_type)
            
            return jsonify({
                'success': True, 
                'count': count
            })
        except Exception as e:
            app.logger.error(f"Error adding interaction to prayer {prayer_id}: {str(e)}")
            return jsonify({'error': 'Failed to record interaction'}), 500

    @app.route('/api/auth/status')
    def auth_status():
        """Check current authentication status and return debug info"""
        if 'user_id' not in session or 'session_id' not in session:
            return jsonify({
                'authenticated': False,
                'message': 'No user session found'
            })
        
        session_id = session.get('session_id')
        user_id = session.get('user_id')
        
        # Check session validity
        session_data = db.get_session(session_id)
        if not session_data or session_data[1] != user_id:
            return jsonify({
                'authenticated': False,
                'message': 'Invalid or expired session',
                'session_exists': session_data is not None
            })
        
        # Get user info
        user = db.get_user(user_id)
        if not user:
            return jsonify({
                'authenticated': False,
                'message': 'User not found in database',
                'user_id': user_id
            })
        
        return jsonify({
            'authenticated': True,
            'user_id': user_id,
            'user_email': user[1],
            'user_name': user[2],
            'auth_provider': user[4]
        })