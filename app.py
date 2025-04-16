from app_config import create_app
from auth.google_auth import setup_google_auth
from auth.line_auth import setup_line_auth
from routes.main_routes import init_routes
from routes.api_routes import init_api_routes
from routes.debug_routes import init_debug_routes
from routes.language_routes import init_language_routes
from routes.fellowship_routes import init_fellowship_routes
from routes.moderation_routes import init_moderation_routes
import models.database as db

# Create Flask app
app = create_app()

# Setup authentication
setup_google_auth(app)
setup_line_auth(app)

# Setup routes
init_routes(app)
init_api_routes(app)
init_debug_routes(app)
init_language_routes(app)
init_fellowship_routes(app)  # Add fellowship routes
init_moderation_routes(app)  # Add moderation routes

# Add context processor to make db available to all templates
@app.context_processor
def inject_db():
    return dict(db=db)

if __name__ == '__main__':
    app.run(debug=True, port=app.config['FLASK_RUN_PORT'], ssl_context='adhoc')
