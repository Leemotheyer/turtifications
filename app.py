from flask import Flask
import secrets
import os
from threading import Thread
from config import initialize_files
from routes import init_routes
from api import init_api_routes
from notifications import check_endpoints

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
    # Only start the thread in the main process
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        monitor_thread = Thread(target=check_endpoints)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    app.run(debug=True)