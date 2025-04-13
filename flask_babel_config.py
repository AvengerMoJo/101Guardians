from flask import request, session
from flask_babel import Babel

babel = Babel()

def get_locale():
    """
    Determine which language to use for translations:
    1. Use language from session if available
    2. Use browser's preferred language if supported
    3. Default to Traditional Chinese
    """
    # Check if user has selected a language in this session
    if 'language' in session:
        return session['language']
    
    # Check browser's preferred languages
    return request.accept_languages.best_match(['zh_TW', 'en', 'ja', 'ko'])

def configure_babel(app):
    """Initialize and configure Flask-Babel for the app."""
    babel.init_app(app, locale_selector=get_locale)
    
    # Configure Babel defaults
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_TW'  # Traditional Chinese default
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
