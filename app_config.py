from flask import Flask
from dotenv import load_dotenv
import os
import logging
import datetime
import models
from flask_babel_config import configure_babel


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

def create_app():
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
        'LANGUAGES': {
            'zh_TW': '繁體中文',  # Traditional Chinese
            'en': 'English',
#            'ja': '日本語',        # Japanese
#            'ko': '한국어'         # Korean
        }
    })
    # Initialize Flask-Babel
    configure_babel(app)

    # Log configuration at startup (excluding secrets)
    app.logger.info(f"Starting {app.config['APP_NAME']}")
    app.logger.info(f"Running on port: {app.config['FLASK_RUN_PORT']}")
    app.logger.info(f"Google Client ID configured: {'Yes' if app.config['GOOGLE_CLIENT_ID'] else 'No'}")
    app.logger.info(f"Line Client ID configured: {'Yes' if app.config['LINE_CLIENT_ID'] else 'No'}")
    app.logger.info(f"Default locale: {app.config['BABEL_DEFAULT_LOCALE']}")

    # Register teardown function to close DB connection
    # app.teardown_appcontext(close_db)
    return app
