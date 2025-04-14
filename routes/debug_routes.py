from flask import g, render_template, redirect, session, current_app as app
from flask import jsonify, request
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

    @app.route('/debug/i18n')
    def debug_i18n():
        from flask_babel import gettext
        from flask import current_app
        import os
        
        # Check which translation domains are loaded
        babel = current_app.extensions.get('babel', None)
        domain_info = "No babel extension found" if not babel else str(babel)

        # Check if translation files exist
        zh_mo_path = os.path.join('translations', 'zh_TW', 'LC_MESSAGES', 'messages.mo')
        zh_po_path = os.path.join('translations', 'zh_TW', 'LC_MESSAGES', 'messages.po')
        zh_mo_exists = os.path.exists(zh_mo_path)
        zh_po_exists = os.path.exists(zh_po_path)
        
        test_translations = {
            'original': 'Welcome to 101Guardians',
            'translated': gettext('Welcome to 101Guardians'),
            'session_lang': session.get('language', 'Not set'),
            'g_lang': g.get('lang_code', 'Not set'),
            'accept_languages': str(request.accept_languages),
            'babel_info': domain_info,
            'zh_mo_exists': zh_mo_exists,
            'zh_po_exists': zh_po_exists,
            'translations_dir': os.path.abspath('translations'),
            'current_dir': os.getcwd()
        }
        return jsonify(test_translations)

    @app.route('/debug/direct-gettext')
    def debug_direct_gettext():
        import gettext
        import os
        
        translations_dir = '/Users/alex/Development/Personal/101Guardians/translations'
        locale = 'zh_TW'
        
        # Try setting up gettext directly
        try:
            translation = gettext.translation('messages', translations_dir, languages=[locale])
            translation.install()
            # Use _ from the translation
            _ = translation.gettext
            direct_translated = _('Welcome to 101Guardians')
        except Exception as e:
            direct_translated = f"Error: {str(e)}"
        
        return jsonify({
            'direct_translated': direct_translated,
        'locale': locale
        })

    @app.route('/debug/babel-details')
    def debug_babel_details():
        from flask_babel import get_locale
        from flask import current_app
        import inspect
        
        # Get the actual Babel instance
        babel = current_app.extensions.get('babel')
        
        # Get the actual gettext function
        from flask_babel import gettext
        gettext_source = inspect.getsource(gettext)
        
        return jsonify({
            'current_locale': str(get_locale()),
            'babel_domain': babel.domain,
            'babel_translation_directories': current_app.config['BABEL_TRANSLATION_DIRECTORIES'],
            'gettext_source': gettext_source
        })