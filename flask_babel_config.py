from flask import request, session, g, current_app
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
        current_app.logger.debug(f"Using session language: {selected_lang}")
        # Store the selected language in g for access in templates
        g.lang_code = selected_lang
        return selected_lang
    
    # Check browser's preferred languages
    supported_languages = list(current_app.config['LANGUAGES'].keys())
    best_match = request.accept_languages.best_match(supported_languages)
    current_app.logger.debug(f"Browser languages: {request.accept_languages}")
    current_app.logger.debug(f"Best language match: {best_match}")
    
    # Default to zh_TW if no match
    selected_lang = best_match or 'zh_TW'
    # Store the detected language in g for access in templates
    g.lang_code = selected_lang
    current_app.logger.debug(f"Final language selected: {g.lang_code}")
    return selected_lang

def configure_babel(app):
    """Initialize and configure Flask-Babel for the app."""
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_TW'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Initialize Babel
    babel.init_app(app, locale_selector=get_locale)
    
    # IMPORTANT: Override _ with our direct translation function
    app.jinja_env.globals['_'] = direct_translate
    
    # Also keep the original gettext available for debugging
    from flask_babel import gettext as flask_babel_gettext
    app.jinja_env.globals['babel_gettext'] = flask_babel_gettext
    
    # Context processor for language info
    @app.context_processor
    def inject_language():
        return dict(current_language=g.get('lang_code', 'zh_TW'))
    
    # Before request handler
    @app.before_request
    def before_request():
        # Set g.lang_code based on session or browser
        if 'language' in session:
            g.lang_code = session['language']
        else:
            supported_languages = list(app.config['LANGUAGES'].keys())
            best_match = request.accept_languages.best_match(supported_languages)
            g.lang_code = best_match or 'zh_TW'
        
        app.logger.debug(f"Request locale: {g.lang_code}, Session language: {session.get('language')}")

def direct_translate(text):
    """
    Direct translation function that works for all configured languages
    """
    import gettext
    import os
    from flask import g, session, request, current_app
    
    # Determine the current locale
    locale = None
    
    # First check session
    if 'language' in session:
        locale = session['language']
    
    # If not in session, check g.lang_code
    if not locale and hasattr(g, 'lang_code'):
        locale = g.lang_code
    
    # Fallback to browser's accept-languages
    if not locale and request:
        supported = current_app.config.get('LANGUAGES', {}).keys()
        locale = request.accept_languages.best_match(supported)
    
    # Final fallback
    if not locale:
        locale = 'zh_TW'  # Default to Chinese
    
    translations_dir = os.path.abspath('translations')
    
    try:
        # Try to load the translation for the current locale
        translation = gettext.translation('messages', translations_dir, languages=[locale])
        return translation.gettext(text)
    except FileNotFoundError:
        # If translation file not found, fall back to the original text
        return text
    except Exception as e:
        # Log error but don't crash
        if current_app:
            current_app.logger.error(f"Translation error: {str(e)}")
        return text