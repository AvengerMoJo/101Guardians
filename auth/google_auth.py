from authlib.integrations.flask_client import OAuth
from flask import url_for, session, redirect, current_app, request, flash
import json
from models.database import db
from google_auth_oauthlib.flow import Flow
from datetime import datetime, timedelta

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import secrets
import os

SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid']

# Update the REDIRECT_URI to handle both development and production environments
def get_redirect_uri(app):
    """
    Dynamically determine the redirect URI based on the environment.
    In development, use localhost. In production, use the configured domain.
    """
    # Check if running in development mode
    if os.getenv('FLASK_ENV', 'development') == 'development':
        port = app.config.get('FLASK_RUN_PORT', 5000)
        return f'http://localhost:{port}/login/google/callback'
    else:
        redirect_uri = os.getenv('REDIRECT_URI')
        if redirect_uri:
            return redirect_uri
        else:
            raise ValueError("REDIRECT_URI is not set for production environment.")

def setup_google_auth(app):
    """Setup and configure Google OAuth."""
    # Ensure HTTPS in production
    if os.getenv('FLASK_ENV', 'development') != 'development':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
    else:
        # Allow insecure transport only in development
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    )
    
    @app.route('/login/google')
    def google_login():
        # Dynamically get the redirect URI
        redirect_uri = get_redirect_uri(app)
        
        flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES)
        app.logger.debug(f"Redirect URI: {redirect_uri}")
        flow.redirect_uri = redirect_uri
        authorization_url, state = flow.authorization_url(access_type='offline')
        session['state'] = state
        app.logger.debug(f"Authorization URL: {authorization_url}")
        return redirect(authorization_url)

    @app.route('/login/google/callback')
    def google_authorize():
        if 'state' not in session or session['state'] != request.args.get('state'):
            flash('Invalid state parameter', 'error')
            return redirect(url_for('login'))
        # Check for error in the callback
        if 'error' in request.args:
            error = request.args.get('error')
            app.logger.error(f'OAuth error: {error}')
            flash(f'Authentication error: {error}', 'error')
            return redirect(url_for('login'))
        # Dynamically get the redirect URI
        redirect_uri = get_redirect_uri(app)
        flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES,
        state=session['state'])
        flow.redirect_uri = redirect_uri

        # Get the full URL with query parameters
        authorization_response = request.url
        # Ensure we're using https if in production
        if os.getenv('FLASK_ENV', 'development') != 'development':
            Aauthorization_response = authorization_response.replace('http://', 'https://')
        
        app.logger.debug(f"Authorization response: {authorization_response}")
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials 

        try:
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(),
                app.config['GOOGLE_CLIENT_ID']
            )
            # Extract user information from id_token
            user_id = f"google_{id_info['sub']}"  # Add prefix to distinguish provider
            user_email = id_info['email']
            user_name = id_info.get('name', 'Google User')
            profile_pic = id_info.get('picture', '')  # Get profile picture URL
            app.logger.debug(f"Authenticated user: {user_name} ({user_email})") 

            # Generate a session ID
            session_id = secrets.token_hex(16)
            
            # Store session info
            session['session_id'] = session_id
            session['user_id'] = user_id

            # Save user to database with all required fields
            db.add_user(
                user_id=user_id,
                email=user_email,
                name=user_name,
                profile_pic=profile_pic,
                auth_provider='google'
            )
            # Create a session record
            expires_at = datetime.now() + timedelta(days=7)  # Session valid for 7 days
            db.create_session(
                session_id=session_id,
                user_id=user_id,
                expires_at=expires_at)
            app.logger.info(f"User {user_name} logged in successfully")
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        except Exception as e:
            flash('Failed to authenticate with Google', 'error')
            return redirect(url_for('login'))
    return oauth
