from flask import request, session, g
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
        selected_lang = session['language']
        # Store the selected language in g for access in templates
        g.lang_code = selected_lang
        return selected_lang
    
    # Check browser's preferred languages
    best_match = request.accept_languages.best_match(['zh_TW', 'en', 'ja', 'ko'])
    # Store the detected language in g for access in templates
    g.lang_code = best_match or 'zh_TW'
    return g.lang_code

def configure_babel(app):
    """Initialize and configure Flask-Babel for the app."""
    babel.init_app(app, locale_selector=get_locale)
    
    # Configure Babel defaults
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_TW'  # Traditional Chinese default
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Add a context processor to make language available to all templates
    @app.context_processor
    def inject_language():
        return dict(current_language=g.get('lang_code', 'zh_TW'))
