from flask import request, session, redirect, url_for, current_app

def init_language_routes(app):
    @app.route('/language/<language_code>')
    def set_language(language_code):
        """Set the language for the current session."""
        # Verify the language is supported
        if language_code in app.config['LANGUAGES']:
            session['language'] = language_code
            app.logger.debug(f"Setting language to {language_code}")
        else:
            app.logger.warning(f"Unsupported language requested: {language_code}")
        
        # Redirect back to referring page or home
        return redirect(request.referrer or url_for('index'))
