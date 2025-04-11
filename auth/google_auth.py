from authlib.integrations.flask_client import OAuth
from flask import url_for, session, redirect, current_app
import json
from models.database import db
from datetime import datetime, timedelta
import secrets

def setup_google_auth(app):
    """Setup and configure Google OAuth."""
    oauth = OAuth(app)
    
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
    )
    
    @app.route('/login/google')
    def google_login():
        redirect_uri = url_for('google_authorize', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    
    @app.route('/login/google/callback')
    def google_authorize():
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token, None)
        
        # Extract user information
        user_id = f"google_{user_info['sub']}"
        email = user_info.get('email', '')
        name = user_info.get('name', '')
        profile_pic = user_info.get('picture', '')
        
        # Save or update user in the database
        db.add_user(user_id, email, name, profile_pic, 'google')
        
        # Create a session
        session_id = secrets.token_hex(16)
        expires_at = datetime.now() + timedelta(days=7)
        db.create_session(session_id, user_id, expires_at)
        
        # Set session cookie
        session['session_id'] = session_id
        session['user_id'] = user_id
        
        return redirect('/dashboard')

    return oauth

