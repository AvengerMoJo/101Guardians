from authlib.integrations.flask_client import OAuth
from flask import url_for, session, redirect, current_app, request
import json
from models.database import db
from google_auth_oauthlib.flow import Flow
from datetime import datetime, timedelta
import secrets

SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email']

REDIRECT_URI = 'https://pray.avengergear.com/login/google/callback'

def setup_google_auth(app):
    """Setup and configure Google OAuth."""
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    )
    
    @app.route('/login/google')
    def google_login():
        flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        authorization_url, state = flow.authorization_url(access_type='offline')
        session['state'] = state
        return redirect(authorization_url)

    @app.route('/login/google/callback')
    def google_authorize():
        flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        state=session['state'])
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(authorization_response=request.url)
        session['credentials'] = flow.credentials.to_json()
        return redirect(url_for('index'))
    return oauth

