from authlib.integrations.flask_client import OAuth
from flask import url_for, session, redirect, current_app, request
import json
from models.database import db
from google_auth_oauthlib.flow import Flow
from datetime import datetime, timedelta
import secrets
import os

SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email']

# Update the REDIRECT_URI to handle both development and production environments
def get_redirect_uri():
    """
    Dynamically determine the redirect URI based on the environment.
    In development, use localhost. In production, use the configured domain.
    """
    # Check if running in development mode
    if os.getenv('FLASK_ENV', 'development') == 'development':
        return 'http://localhost:5001/login/google/callback'
    else:
        # In production, use the configured domain
        # Ensure to set this in your environment variables or configuration
        # For example, you can set it in your .env file or server configuration
        # Example: REDIRECT_URI=https://your-production-domain.com/login/google/callback
        redirect_uri = os.getenv('REDIRECT_URI')
        if redirect_uri:
            return redirect_uri
        else:
            raise ValueError("REDIRECT_URI is not set for production environment.")
    
    # Use the production redirect URI
    return 'https://pray.avengergear.com/login/google/callback'

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
        redirect_uri = get_redirect_uri()
        
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
        flow.redirect_uri = redirect_uri
        authorization_url, state = flow.authorization_url(access_type='offline')
        session['state'] = state
        return redirect(authorization_url)

    @app.route('/login/google/callback')
    def google_authorize():
        # Dynamically get the redirect URI
        redirect_uri = get_redirect_uri()
        
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
        flow.fetch_token(authorization_response=request.url)
        session['credentials'] = flow.credentials.to_json()
        return redirect(url_for('index'))
    
    return oauth
