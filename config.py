import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    LINE_CLIENT_ID = os.getenv('LINE_CLIENT_ID')
    LINE_CLIENT_SECRET = os.getenv('LINE_CLIENT_SECRET')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'app.db')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # In production, you should use a more secure secret key
    SECRET_KEY = os.getenv('SECRET_KEY')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Return the appropriate configuration object based on the environment."""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])
