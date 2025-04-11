from flask import url_for, session, redirect, request, current_app
import requests
import json
from models.database import db
from datetime import datetime, timedelta
import secrets

def setup_line_auth(app):
    """Setup and configure Line Login."""
    
    @app.route('/login/line')
    def line_login():
        redirect_uri = url_for('line_authorize', _external=True)
        line_auth_url = "https://access.line.me/oauth2/v2.1/authorize"
        
        params = {
            'response_type': 'code',
            'client_id': app.config['LINE_CLIENT_ID'],
            'redirect_uri': redirect_uri,
            'state': secrets.token_hex(8),
            'scope': 'profile openid email',
        }
        
        # Build the query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        authorization_url = f"{line_auth_url}?{query_string}"
        
        return redirect(authorization_url)
    
    @app.route('/login/line/callback')
    def line_authorize():
        code = request.args.get('code')
        
        if not code:
            return redirect('/login')
        
        # Exchange code for token
        token_url = "https://api.line.me/oauth2/v2.1/token"
        redirect_uri = url_for('line_authorize', _external=True)
        
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': app.config['LINE_CLIENT_ID'],
            'client_secret': app.config['LINE_CLIENT_SECRET'],
        }
        
        token_response = requests.post(token_url, data=payload)
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            return redirect('/login')
        
        # Get user profile
        profile_url = "https://api.line.me/v2/profile"
        headers = {
            'Authorization': f"Bearer {token_data['access_token']}"
        }
        
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()
        
        # Extract user information
        user_id = f"line_{profile_data.get('userId')}"
        name = profile_data.get('displayName', '')
        profile_pic = profile_data.get('pictureUrl', '')
        
        # For email, we need to verify the ID token
        email = ''
        if 'id_token' in token_data:
            # This is a simplification - in production you should verify the token
            id_token = token_data['id_token']
            try:
                id_token_parts = id_token.split('.')
                if len(id_token_parts) >= 2:
                    import base64
                    # Fix padding
                    padded = id_token_parts[1] + '=' * (4 - len(id_token_parts[1]) % 4)
                    token_payload = json.loads(base64.b64decode(padded))
                    email = token_payload.get('email', '')
            except Exception as e:
                app.logger.error(f"Error decoding Line ID token: {e}")
        
        # Save or update user in database
        db.add_user(user_id, email, name, profile_pic, 'line')
        
        # Create a session
        session_id = secrets.token_hex(16)
        expires_at = datetime.now() + timedelta(days=7)
        db.create_session(session_id, user_id, expires_at)
        
        # Set session cookie
        session['session_id'] = session_id
        session['user_id'] = user_id
        
        return redirect('/dashboard')
