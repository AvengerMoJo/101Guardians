from flask import Flask, render_template, redirect, session, request, jsonify, g
from models.database import db
from auth.google_auth import setup_google_auth
from auth.line_auth import setup_line_auth
from dotenv import load_dotenv
import os
import logging
from functools import wraps

# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
            
# Set application name
app.config['APP_NAME'] = '101Guardians'
app.config['APP_FULL_NAME'] = 'Covenant Guardians: Journal of Blessings'

# Configuration
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
    'FLASK_RUN_PORT': os.getenv('FLASK_RUN_PORT', 5000),
    'REDIRECT_URI': os.getenv('REDIRECT_URI'),
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'LINE_CLIENT_ID': os.getenv('LINE_CLIENT_ID'),
    'LINE_CLIENT_SECRET': os.getenv('LINE_CLIENT_SECRET'),
})

# Log configuration at startup (excluding secrets)
app.logger.info(f"Starting {app.config['APP_NAME']}")
app.logger.info(f"Running on port: {app.config['FLASK_RUN_PORT']}")
app.logger.info(f"Google Client ID configured: {'Yes' if app.config['GOOGLE_CLIENT_ID'] else 'No'}")
app.logger.info(f"Line Client ID configured: {'Yes' if app.config['LINE_CLIENT_ID'] else 'No'}")

# Setup authentication
setup_google_auth(app)
setup_line_auth(app)

# Close database connection at the end of each request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db_conn'):
        g.db_conn.close()

# Authentication middleware
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        user_id = session.get('user_id')
        
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

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

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
                          db=db)  # Pass the database to the template

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    user = db.get_user(user_id)
    
    if not user:
        app.logger.error(f"User {user_id} not found in database")
        session.clear()
        return redirect('/login')
    
    return render_template('profile.html', user=user)

# API Endpoints
@app.route('/api/prayers', methods=['GET'])
@login_required
def get_prayers():
    user_id = session.get('user_id')
    user_prayers = db.get_user_prayers(user_id)
    
    # Convert to a list of dictionaries
    result = []
    for prayer in user_prayers:
        result.append({
            'id': prayer[0],
            'title': prayer[2],
            'content': prayer[3],
            'is_public': prayer[4],
            'is_answered': prayer[5],
            'answer': prayer[6],
            'created_at': prayer[8].isoformat() if prayer[8] else None
        })
    
    return jsonify(result)

@app.route('/api/prayers', methods=['POST'])
@login_required
def add_prayer():
    user_id = session.get('user_id')
    
    # Better error handling for the request body
    try:
        data = request.get_json()
        if not data:
            app.logger.warning("Failed to parse JSON data from request")
            return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        app.logger.error(f"Error parsing JSON: {str(e)}")
        return jsonify({'error': 'Could not parse request data'}), 400
    
    # Validate required fields
    if 'title' not in data or not data['title'].strip():
        app.logger.warning("Missing title in request")
        return jsonify({'error': 'Title is required'}), 400
        
    if 'content' not in data or not data['content'].strip():
        app.logger.warning("Missing content in request")
        return jsonify({'error': 'Content is required'}), 400
    
    # Get public status
    is_public = data.get('is_public', False)
    
    # Sanitize inputs (basic example)
    title = data['title'].strip()
    content = data['content'].strip()
    
    # Log the attempted prayer addition
    app.logger.info(f"Adding prayer for user {user_id}: title='{title}', public={is_public}")
    
    try:
        # Save to database
        db.add_prayer(user_id, title, content, is_public)
        app.logger.info(f"Successfully added prayer for user {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Database error adding prayer for user {user_id}: {str(e)}")
        return jsonify({'error': 'Failed to save prayer due to a server error'}), 500

@app.route('/api/prayers/<int:prayer_id>/answer', methods=['POST'])
@login_required
def answer_prayer(prayer_id):
    user_id = session.get('user_id')
    
    try:
        data = request.get_json()
        if not data or 'answer' not in data:
            return jsonify({'error': 'Answer text is required'}), 400
        
        answer_text = data['answer'].strip()
        if not answer_text:
            return jsonify({'error': 'Answer cannot be empty'}), 400
        
        # Mark the prayer as answered
        db.mark_prayer_as_answered(prayer_id, answer_text)
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error marking prayer {prayer_id} as answered: {str(e)}")
        return jsonify({'error': 'Failed to update prayer'}), 500

@app.route('/api/prayers/<int:prayer_id>/interact', methods=['POST'])
@login_required
def interact_with_prayer(prayer_id):
    user_id = session.get('user_id')
    
    try:
        data = request.get_json()
        if not data or 'type' not in data:
            return jsonify({'error': 'Interaction type is required'}), 400
        
        interaction_type = data['type']
        if interaction_type not in ['pray', 'praise']:
            return jsonify({'error': 'Invalid interaction type'}), 400
        
        # Add the interaction
        db.add_prayer_interaction(prayer_id, user_id, interaction_type)
        
        # Get updated count
        count = db.get_prayer_interaction_count(prayer_id, interaction_type)
        
        return jsonify({
            'success': True, 
            'count': count
        })
    except Exception as e:
        app.logger.error(f"Error adding interaction to prayer {prayer_id}: {str(e)}")
        return jsonify({'error': 'Failed to record interaction'}), 500

# Add a route to check authentication status
@app.route('/api/auth/status')
def auth_status():
    """Check current authentication status and return debug info"""
    if 'user_id' not in session or 'session_id' not in session:
        return jsonify({
            'authenticated': False,
            'message': 'No user session found'
        })
    
    session_id = session.get('session_id')
    user_id = session.get('user_id')
    
    # Check session validity
    session_data = db.get_session(session_id)
    if not session_data or session_data[1] != user_id:
        return jsonify({
            'authenticated': False,
            'message': 'Invalid or expired session',
            'session_exists': session_data is not None
        })
    
    # Get user info
    user = db.get_user(user_id)
    if not user:
        return jsonify({
            'authenticated': False,
            'message': 'User not found in database',
            'user_id': user_id
        })
    
    return jsonify({
        'authenticated': True,
        'user_id': user_id,
        'user_email': user[1],
        'user_name': user[2],
        'auth_provider': user[4]
    })

# Debug routes
@app.route('/debug')
def debug_page():
    """Debug page to help diagnose authentication issues"""
    from datetime import datetime
    
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

if __name__ == '__main__':
    app.run(debug=True, port=app.config['FLASK_RUN_PORT'], ssl_context='adhoc')
