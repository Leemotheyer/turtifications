from flask import Flask
import secrets
import os
from threading import Thread
from functions.config import initialize_files
from endpoints.routes import init_routes
from endpoints.api import init_api_routes
from functions.notifications import check_endpoints

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Initialize configuration files
initialize_files()

# Initialize routes
init_routes(app)

# Initialize API routes
init_api_routes(app)

if __name__ == '__main__':
    # Use environment variable for debug mode, default to False for production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Only start the thread in the main process (after reloader in debug mode)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not debug_mode:
        monitor_thread = Thread(target=check_endpoints)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    app.run(debug=debug_mode, host='0.0.0.0')