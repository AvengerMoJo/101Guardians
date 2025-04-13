from app_config import create_app
from auth.google_auth import setup_google_auth
from auth.line_auth import setup_line_auth
from routes.main_routes import init_routes
from routes.api_routes import init_api_routes
from routes.debug_routes import init_debug_routes
import datetime

# Create Flask app
app = create_app()

# Setup authentication
setup_google_auth(app)
setup_line_auth(app)


# Setup routes
init_routes(app)
init_api_routes(app)
init_debug_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=app.config['FLASK_RUN_PORT'], ssl_context='adhoc')
