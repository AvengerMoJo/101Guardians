from flask import render_template, redirect, session, current_app as app
from auth.auth_middleware import login_required
from models.database import db
from functools import wraps

# Middleware to check if user is admin or moderator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        # Check if user is admin or moderator
        if not db.is_admin_or_moderator(user_id):
            app.logger.warning(f"Unauthorized access attempt to admin area by user {user_id}")
            return redirect('/dashboard')
            
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect('/dashboard')
        return render_template('index.html', db=db)

    @app.route('/login')
    def login():
        if 'user_id' in session:
            return redirect('/dashboard')
        return render_template('index.html', db=db)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_id = session.get('user_id')
        app.logger.debug(f"Loading dashboard for user {user_id}")
        
        user = db.get_user(user_id)
        if not user:
            app.logger.error(f"User {user_id} not found in database")
            session.clear()
            return redirect('/login')
        
        # Get user's prayers
        user_prayers = db.get_user_prayers(user_id)
        
        # Get global prayers (waiting to be fulfilled)
        global_prayers = db.get_global_prayers()
        
        # Get answered prayers
        answered_prayers = db.get_answered_prayers()
        
        # Format prayers for template rendering
        formatted_global_prayers = []
        for prayer in global_prayers:
            formatted_global_prayers.append({
                'id': prayer[0],
                'user_id': prayer[1],
                'title': prayer[2],
                'content': prayer[3],
                'created_at': prayer[8].strftime('%Y-%m-%d %H:%M') if prayer[8] else '',
                'user_name': prayer[9],
                'user_pic': prayer[10]
            })
        
        formatted_answered_prayers = []
        for prayer in answered_prayers:
            formatted_answered_prayers.append({
                'id': prayer[0],
                'user_id': prayer[1],
                'title': prayer[2],
                'content': prayer[3],
                'answer': prayer[6],
                'created_at': prayer[8].strftime('%Y-%m-%d %H:%M') if prayer[8] else '',
                'answered_at': prayer[7].strftime('%Y-%m-%d %H:%M') if prayer[7] else '',
                'user_name': prayer[9],
                'user_pic': prayer[10]
            })
        
        return render_template('dashboard.html', 
                            user=user,
                            data=user_prayers,
                            global_prayers=formatted_global_prayers,
                            answered_prayers=formatted_answered_prayers,
                            db=db)

    @app.route('/profile')
    @login_required
    def profile():
        user_id = session.get('user_id')
        user = db.get_user(user_id)
        
        if not user:
            app.logger.error(f"User {user_id} not found in database")
            session.clear()
            return redirect('/login')
        
        return render_template('profile.html', user=user, db=db)
    
    @app.route('/fellowships')
    @login_required
    def fellowships():
        """Fellowship management page"""
        user_id = session.get('user_id')
        user = db.get_user(user_id)
        
        if not user:
            app.logger.error(f"User {user_id} not found in database")
            session.clear()
            return redirect('/login')
        
        return render_template('fellowships.html', user=user, db=db)
    
    @app.route('/moderation')
    @login_required
    @admin_required
    def moderation():
        """Moderation dashboard for admins and moderators"""
        user_id = session.get('user_id')
        user = db.get_user(user_id)
        
        if not user:
            app.logger.error(f"User {user_id} not found in database")
            session.clear()
            return redirect('/login')
        
        # Get user role
        user_role = db.get_user_role(user_id)
        
        return render_template('moderation.html', user=user, user_role=user_role, db=db)
