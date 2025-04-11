from flask import Flask, render_template, redirect, session, request, jsonify
from models.database import db
from auth.google_auth import setup_google_auth
from auth.line_auth import setup_line_auth
from dotenv import load_dotenv
import os
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
            
# Set application name
app.config['APP_NAME'] = '101Guardians'
app.config['APP_FULL_NAME'] = 'Covenant Guardians: Journal of Blessings'

# Configuration
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'LINE_CLIENT_ID': os.getenv('LINE_CLIENT_ID'),
    'LINE_CLIENT_SECRET': os.getenv('LINE_CLIENT_SECRET'),
})

# Setup authentication
setup_google_auth(app)
setup_line_auth(app)

# Authentication middleware
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        user_id = session.get('user_id')
        
        if not session_id or not user_id:
            return redirect('/login')
        
        # Verify session
        session_data = db.get_session(session_id)
        if not session_data or session_data[1] != user_id:
            # Invalid session, clear and redirect to login
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
    user = db.get_user(user_id)
    user_data = db.get_user_data(user_id)
    
    return render_template('dashboard.html', 
                          user=user,
                          data=user_data)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    user = db.get_user(user_id)
    
    return render_template('profile.html', user=user)

# API Endpoints
@app.route('/api/data', methods=['GET'])
@login_required
def get_data():
    user_id = session.get('user_id')
    user_data = db.get_user_data(user_id)
    
    # Convert to a list of dictionaries
    result = []
    for item in user_data:
        result.append({
            'id': item[0],
            'title': item[2],
            'content': item[3],
            'created_at': item[4].isoformat() if item[4] else None
        })
    
    return jsonify(result)

@app.route('/api/data', methods=['POST'])
@login_required
def add_data():
    user_id = session.get('user_id')
    data = request.json
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    db.add_user_data(user_id, data['title'], data['content'])
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
