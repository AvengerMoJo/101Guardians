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
        return 'http://localhost:5001/login/google/callback'
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
        print("Redirect URI:", redirect_uri)
        flow.redirect_uri = redirect_uri
        authorization_url, state = flow.authorization_url(access_type='offline')
        session['state'] = state
        print("Authorization URL:", authorization_url)
        return redirect(authorization_url)

    @app.route('/login/google/callback')
    def google_authorize():
        if 'state' not in session or session['state'] != request.args.get('state'):
            flash('Invalid state parameter', 'error')
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
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials 

        try:
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(),
                app.config['GOOGLE_CLIENT_ID']
            )
            
            # Store user info in session
            session['user_id'] = id_info['sub']
            session['user_email'] = id_info['email']
            session['user_name'] = id_info.get('name', 'Google User')
            session['session_id'] = secrets.token_hex(16)

            # Save user to database (if needed)
            db.add_user(
                id_info['sub'],
                id_info['email'],
                id_info.get('name', 'Google User'),
                'google'
            )
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        except Exception as e:
            flash('Failed to authenticate with Google', 'error')
            return redirect(url_for('login'))
    return oauth
