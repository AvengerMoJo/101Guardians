from flask import render_template, redirect, session, current_app as app
from models.database import db
import os
from datetime import datetime

def init_debug_routes(app):
    @app.route('/debug')
    def debug_page():
        """Debug page to help diagnose authentication issues"""
        
        user = None
        session_data = None
        
        # Get user data if authenticated
        if 'user_id' in session:
            user_id = session.get('user_id')
            user = db.get_user(user_id)
            
            # Get session data
            if 'session_id' in session:
                session_id = session.get('session_id')
                session_data = db.get_session(session_id)
        
        return render_template(
            'debug.html',
            env=os.environ,
            config=app.config,
            user=user,
            session_data=session_data,
            now=datetime.now()
        )

    @app.route('/debug/clear-session')
    def debug_clear_session():
        """Clear the current session for debugging purposes"""
        session.clear()
        return redirect('/debug')