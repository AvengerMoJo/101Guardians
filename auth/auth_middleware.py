from flask import session, redirect, g
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        user_id = session.get('user_id')
        
        # Get the current app context
        from flask import current_app as app
        app.logger.debug(f"Checking authentication: session_id={session_id is not None}, user_id={user_id}")
        
        if not session_id or not user_id:
            app.logger.debug("No session_id or user_id in session, redirecting to login")
            return redirect('/login')
        
        # Verify session
        session_data = db.get_session(session_id)
        if not session_data or session_data[1] != user_id:
            # Invalid session, clear and redirect to login
            app.logger.warning(f"Invalid session for user {user_id}, clearing and redirecting")
            session.clear()
            return redirect('/login')
            
        return f(*args, **kwargs)
    return decorated_function
