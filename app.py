from flask import Flask
import os
import secrets
import threading
from threading import Thread
from functions.config import initialize_files, CONFIG_FILE
from functions.version import initialize_version
from endpoints.routes import init_routes
from endpoints.api import init_api_routes
from functions.notifications import check_endpoints

# Initialize Flask app
app = Flask(__name__)

# Stable secret key for sessions (env override or persisted file)
_secret_key = os.environ.get('SECRET_KEY', '').strip()
if not _secret_key:
    secret_file = os.path.join(os.path.dirname(CONFIG_FILE), '.secret_key')
    if os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            _secret_key = f.read().strip()
    else:
        _secret_key = secrets.token_hex(32)
        os.makedirs(os.path.dirname(secret_file) or '.', exist_ok=True)
        with open(secret_file, 'w') as f:
            f.write(_secret_key)
app.secret_key = _secret_key

# Initialize configuration files
initialize_files()

# Initialize version system
initialize_version()

# Initialize routes
init_routes(app)

# Initialize API routes
init_api_routes(app)

_monitor_thread = None
_monitor_lock = threading.Lock()


def start_monitor_thread():
    """Start background endpoint monitoring once per process."""
    global _monitor_thread

    if os.environ.get('DISABLE_MONITOR', '').lower() in ('1', 'true', 'yes'):
        return

    # Avoid double-start under Flask debug reloader parent process
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    if debug_mode and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    with _monitor_lock:
        if _monitor_thread and _monitor_thread.is_alive():
            return
        _monitor_thread = Thread(target=check_endpoints, daemon=True, name='endpoint-monitor')
        _monitor_thread.start()


start_monitor_thread()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0')
