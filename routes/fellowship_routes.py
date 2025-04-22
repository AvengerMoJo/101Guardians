from flask import request, jsonify, session, current_app as app
from auth.auth_middleware import login_required
from models.database import db

def init_fellowship_routes(app):
    @app.route('/api/fellowships', methods=['GET'])
    @login_required
    def get_fellowships():
        """Get fellowships for the current user and public fellowships"""
        user_id = session.get('user_id')
        
        # Get user's fellowships
        user_fellowships = db.get_user_fellowships(user_id)
        
        # Get public fellowships (that the user is not a member of)
        public_fellowships = db.get_public_fellowships()
        
        # Filter out fellowships that the user is already a member of
        user_fellowship_ids = [f[0] for f in user_fellowships]
        filtered_public = [f for f in public_fellowships if f[0] not in user_fellowship_ids]
        
        # Convert to dictionaries for JSON response
        user_fellowships_data = []
        for f in user_fellowships:
            user_fellowships_data.append({
                'id': f[0],
                'name': f[1],
                'description': f[2],
                'image_url': f[3],
                'is_private': f[4],
                'join_code': f[5] if f[8] == 'admin' else None,  # Only show join code to admins
                'created_by': f[6],
                'created_at': f[7].isoformat() if f[7] else None,
                'user_role': f[8],
                'creator_name': f[9],
                'creator_pic': f[10],
                'member_count': f[11]
            })
        
        public_fellowships_data = []
        for f in filtered_public:
            public_fellowships_data.append({
                'id': f[0],
                'name': f[1],
                'description': f[2],
                'image_url': f[3],
                'is_private': f[4],  # Always false for public fellowships
                'created_by': f[6],
                'created_at': f[7].isoformat() if f[7] else None,
                'creator_name': f[8],
                'creator_pic': f[9],
                'member_count': f[10]
            })
        
        return jsonify({
            'user_fellowships': user_fellowships_data,
            'public_fellowships': public_fellowships_data
        })

    @app.route('/api/fellowships', methods=['POST'])
    @login_required
    def create_fellowship():
        """Create a new fellowship"""
        user_id = session.get('user_id')
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Validate required fields
            if 'name' not in data or not data['name'].strip():
                return jsonify({'error': 'Fellowship name is required'}), 400
            
            # Extract and sanitize inputs
            name = data['name'].strip()
            description = data.get('description', '').strip()
            is_private = data.get('is_private', True)
            image_url = data.get('image_url', None)
            
            # Create the fellowship
            fellowship_id = db.create_fellowship(
                name=name,
                description=description,
                created_by=user_id,
                is_private=is_private,
                image_url=image_url
            )
            
            if not fellowship_id:
                return jsonify({'error': 'Failed to create fellowship'}), 500
            
            # Get the created fellowship details
            fellowship = db.get_fellowship(fellowship_id)
            
            if not fellowship:
                return jsonify({'error': 'Fellowship created but failed to retrieve details'}), 500
            
            return jsonify({
                'success': True,
                'fellowship': {
                    'id': fellowship[0],
                    'name': fellowship[1],
                    'description': fellowship[2],
                    'image_url': fellowship[3],
                    'is_private': fellowship[4],
                    'join_code': fellowship[5],  # Include join code in response for private fellowships
                    'created_by': fellowship[6],
                    'created_at': fellowship[7].isoformat() if fellowship[7] else None,
                    'user_role': 'admin',  # Creator is always admin
                    'creator_name': fellowship[8],
                    'creator_pic': fellowship[9],
                    'member_count': fellowship[10]
                }
            })
        except Exception as e:
            app.logger.error(f"Error creating fellowship: {str(e)}")
            return jsonify({'error': 'An error occurred while creating the fellowship'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>', methods=['GET'])
    @login_required
    def get_fellowship(fellowship_id):
        """Get details of a specific fellowship"""
        user_id = session.get('user_id')
        
        # Get the fellowship
        fellowship = db.get_fellowship(fellowship_id)
        
        if not fellowship:
            return jsonify({'error': 'Fellowship not found'}), 404
        
        # Check if user is a member or if it's a public fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role and fellowship[4]:  # Not a member and it's private
            return jsonify({'error': 'You do not have access to this fellowship'}), 403
        
        # Get members (if user is a member)
        members = []
        if user_role:
            members_data = db.get_fellowship_members(fellowship_id)
            for member in members_data:
                members.append({
                    'user_id': member[1],
                    'role': member[2],
                    'joined_at': member[3].isoformat() if member[3] else None,
                    'name': member[4],
                    'email': member[5],
                    'profile_pic': member[6]
                })
        
        # Get prayers shared in this fellowship (if user is a member)
        prayers = []
        if user_role:
            prayers_data = db.get_fellowship_prayers(fellowship_id)
            for prayer in prayers_data:
                prayers.append({
                    'id': prayer[0],
                    'user_id': prayer[1],
                    'title': prayer[2],
                    'content': prayer[3],
                    'is_public': prayer[4],
                    'is_answered': prayer[5],
                    'answer': prayer[6],
                    'answered_at': prayer[7].isoformat() if prayer[7] else None,
                    'created_at': prayer[8].isoformat() if prayer[8] else None,
                    'user_name': prayer[9],
                    'user_pic': prayer[10],
                    'shared_at': prayer[11].isoformat() if prayer[11] else None
                })
        
        # Return fellowship details
        return jsonify({
            'id': fellowship[0],
            'name': fellowship[1],
            'description': fellowship[2],
            'image_url': fellowship[3],
            'is_private': fellowship[4],
            'join_code': fellowship[5] if user_role == 'admin' else None,  # Only show join code to admins
            'created_by': fellowship[6],
            'created_at': fellowship[7].isoformat() if fellowship[7] else None,
            'creator_name': fellowship[8],
            'creator_pic': fellowship[9],
            'member_count': fellowship[10],
            'user_role': user_role,
            'members': members,
            'prayers': prayers
        })

    @app.route('/api/fellowships/<int:fellowship_id>', methods=['PUT'])
    @login_required
    def update_fellowship(fellowship_id):
        """Update a fellowship (admin only)"""
        user_id = session.get('user_id')
        
        # Check if user is an admin of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        if user_role != 'admin':
            return jsonify({'error': 'Only fellowship admins can update fellowship details'}), 403
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Extract and sanitize inputs
            name = data.get('name')
            if name:
                name = name.strip()
            
            description = data.get('description')
            if description:
                description = description.strip()
            
            is_private = data.get('is_private')
            image_url = data.get('image_url')
            
            # Update the fellowship
            success = db.update_fellowship(
                fellowship_id=fellowship_id,
                name=name,
                description=description,
                is_private=is_private,
                image_url=image_url
            )
            
            if not success:
                return jsonify({'error': 'Failed to update fellowship'}), 500
            
            # Get the updated fellowship
            fellowship = db.get_fellowship(fellowship_id)
            
            return jsonify({
                'success': True,
                'fellowship': {
                    'id': fellowship[0],
                    'name': fellowship[1],
                    'description': fellowship[2],
                    'image_url': fellowship[3],
                    'is_private': fellowship[4],
                    'join_code': fellowship[5],
                    'created_by': fellowship[6],
                    'created_at': fellowship[7].isoformat() if fellowship[7] else None
                }
            })
        except Exception as e:
            app.logger.error(f"Error updating fellowship: {str(e)}")
            return jsonify({'error': 'An error occurred while updating the fellowship'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>', methods=['DELETE'])
    @login_required
    def delete_fellowship(fellowship_id):
        """Delete a fellowship (admin only)"""
        user_id = session.get('user_id')
        
        # Check if user is an admin of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        if user_role != 'admin':
            return jsonify({'error': 'Only fellowship admins can delete fellowships'}), 403
        
        try:
            # Delete the fellowship
            success = db.delete_fellowship(fellowship_id)
            
            if not success:
                return jsonify({'error': 'Failed to delete fellowship'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error deleting fellowship: {str(e)}")
            return jsonify({'error': 'An error occurred while deleting the fellowship'}), 500

    @app.route('/api/fellowships/join', methods=['POST'])
    @login_required
    def join_fellowship():
        """Join a fellowship using a join code"""
        user_id = session.get('user_id')
        
        try:
            data = request.get_json()
            if not data or 'join_code' not in data:
                return jsonify({'error': 'Join code is required'}), 400
            
            join_code = data['join_code'].strip()
            
            # Try to join the fellowship
            success, result = db.join_fellowship_with_code(join_code, user_id)
            
            if not success:
                return jsonify({'error': result}), 400
            
            # Get the fellowship details
            fellowship_id = result
            fellowship = db.get_fellowship(fellowship_id)
            
            return jsonify({
                'success': True,
                'fellowship': {
                    'id': fellowship[0],
                    'name': fellowship[1],
                    'description': fellowship[2],
                    'image_url': fellowship[3],
                    'is_private': fellowship[4],
                    'created_by': fellowship[6],
                    'created_at': fellowship[7].isoformat() if fellowship[7] else None,
                    'creator_name': fellowship[8],
                    'creator_pic': fellowship[9],
                    'member_count': fellowship[10],
                    'user_role': 'member'
                }
            })
        except Exception as e:
            app.logger.error(f"Error joining fellowship: {str(e)}")
            return jsonify({'error': 'An error occurred while joining the fellowship'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>/members', methods=['GET'])
    @login_required
    def get_fellowship_members(fellowship_id):
        """Get members of a fellowship"""
        user_id = session.get('user_id')
        
        # Check if user is a member of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        try:
            # Get the members
            members_data = db.get_fellowship_members(fellowship_id)
            
            members = []
            for member in members_data:
                members.append({
                    'user_id': member[1],
                    'role': member[2],
                    'joined_at': member[3].isoformat() if member[3] else None,
                    'name': member[4],
                    'email': member[5],
                    'profile_pic': member[6]
                })
            
            return jsonify({'members': members})
        except Exception as e:
            app.logger.error(f"Error getting fellowship members: {str(e)}")
            return jsonify({'error': 'An error occurred while getting fellowship members'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>/members/<path:member_id>', methods=['PUT'])
    @login_required
    def update_member_role(fellowship_id, member_id):
        """Update a member's role (admin only)"""
        user_id = session.get('user_id')
        
        # Check if user is an admin of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        if user_role != 'admin':
            return jsonify({'error': 'Only fellowship admins can update member roles'}), 403
        
        try:
            data = request.get_json()
            if not data or 'role' not in data:
                return jsonify({'error': 'Role is required'}), 400
            
            new_role = data['role']
            if new_role not in ('admin', 'moderator', 'member'):
                return jsonify({'error': 'Invalid role'}), 400
            
            # Update the member's role
            success = db.add_fellowship_member(fellowship_id, member_id, new_role)
            
            if not success:
                return jsonify({'error': 'Failed to update member role'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error updating member role: {str(e)}")
            return jsonify({'error': 'An error occurred while updating member role'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>/members/<path:member_id>', methods=['DELETE'])
    @login_required
    def remove_member(fellowship_id, member_id):
        """Remove a member from a fellowship (admin or self)"""
        user_id = session.get('user_id')
        
        # Check if user is an admin of this fellowship or removing themselves
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        if user_id != member_id and user_role != 'admin':
            return jsonify({'error': 'Only fellowship admins can remove other members'}), 403
        
        try:
            # Cannot remove the last admin
            if member_id == user_id and user_role == 'admin':
                # Check if this is the last admin
                members = db.get_fellowship_members(fellowship_id)
                admin_count = sum(1 for m in members if m[2] == 'admin')
                
                if admin_count <= 1:
                    return jsonify({'error': 'Cannot remove the last admin. Transfer admin role to another member first'}), 400
            
            # Remove the member
            success = db.remove_fellowship_member(fellowship_id, member_id)
            
            if not success:
                return jsonify({'error': 'Failed to remove member'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error removing member: {str(e)}")
            return jsonify({'error': 'An error occurred while removing member'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>/regenerate-code', methods=['POST'])
    @login_required
    def regenerate_join_code(fellowship_id):
        """Regenerate join code for a fellowship (admin only)"""
        user_id = session.get('user_id')
        
        # Check if user is an admin of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        if user_role != 'admin':
            return jsonify({'error': 'Only fellowship admins can regenerate join codes'}), 403
        
        try:
            # Get the fellowship to verify it's private
            fellowship = db.get_fellowship(fellowship_id)
            
            if not fellowship[4]:  # Not private
                return jsonify({'error': 'Cannot generate join code for public fellowships'}), 400
            
            # Regenerate the join code
            new_code = db.regenerate_join_code(fellowship_id)
            
            if not new_code:
                return jsonify({'error': 'Failed to regenerate join code'}), 500
            
            return jsonify({
                'success': True,
                'join_code': new_code
            })
        except Exception as e:
            app.logger.error(f"Error regenerating join code: {str(e)}")
            return jsonify({'error': 'An error occurred while regenerating join code'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>/prayers', methods=['POST'])
    @login_required
    def share_prayer_with_fellowship(fellowship_id):
        """Share a prayer with a fellowship"""
        user_id = session.get('user_id')
        
        # Check if user is a member of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        try:
            data = request.get_json()
            if not data or 'prayer_id' not in data:
                return jsonify({'error': 'Prayer ID is required'}), 400
            
            prayer_id = data['prayer_id']
            
            # Verify the prayer exists and belongs to the user
            prayer = db.get_prayer(prayer_id)
            
            if not prayer:
                return jsonify({'error': 'Prayer not found'}), 404
            
            if prayer[1] != user_id:
                return jsonify({'error': 'You can only share your own prayers'}), 403
            
            # Share the prayer
            success = db.share_prayer_with_fellowship(prayer_id, fellowship_id)
            
            if not success:
                return jsonify({'error': 'Failed to share prayer'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error sharing prayer: {str(e)}")
            return jsonify({'error': 'An error occurred while sharing prayer'}), 500

    @app.route('/api/fellowships/<int:fellowship_id>/prayers/<int:prayer_id>', methods=['DELETE'])
    @login_required
    def unshare_prayer_from_fellowship(fellowship_id, prayer_id):
        """Unshare a prayer from a fellowship"""
        user_id = session.get('user_id')
        
        # Check if user is a member of this fellowship
        user_role = db.is_fellowship_member(fellowship_id, user_id)
        
        if not user_role:
            return jsonify({'error': 'You are not a member of this fellowship'}), 403
        
        try:
            # Verify the prayer exists
            prayer = db.get_prayer(prayer_id)
            
            if not prayer:
                return jsonify({'error': 'Prayer not found'}), 404
            
            # Only allow the prayer owner, fellowship admin, or moderator to unshare
            if prayer[1] != user_id and user_role not in ('admin', 'moderator'):
                return jsonify({'error': 'You can only unshare your own prayers or as an admin/moderator'}), 403
            
            # Unshare the prayer
            success = db.unshare_prayer_from_fellowship(prayer_id, fellowship_id)
            
            if not success:
                return jsonify({'error': 'Failed to unshare prayer'}), 500
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error unsharing prayer: {str(e)}")
            return jsonify({'error': 'An error occurred while unsharing prayer'}), 500
