import json
import os
import sys
import fcntl
from contextlib import contextmanager
from datetime import datetime

# Configuration paths (override with env vars)
DATA_DIR = os.environ.get('DATA_DIR', 'data')
CONFIG_FILE = os.environ.get('CONFIG_FILE', os.path.join(DATA_DIR, 'config.json'))
LOG_FILE = os.environ.get('LOG_FILE', os.path.join(DATA_DIR, 'notification_logs.json'))
LOCK_FILE = CONFIG_FILE + '.lock'


@contextmanager
def _config_lock(shared=False):
    """File-based lock for config read/write operations."""
    os.makedirs(os.path.dirname(CONFIG_FILE) or '.', exist_ok=True)
    with open(LOCK_FILE, 'w') as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def initialize_files():
    """Initialize config and log files if they don't exist"""
    data_dir = os.path.dirname(CONFIG_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        with _config_lock():
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    "discord_webhook": "",
                    "check_interval": 5,
                    "log_retention": 1000,
                    "notification_log_retention": 500,
                    "user_variables": {},
                    "total_notifications_sent": 0
                }, f)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)


def get_config():
    """Get configuration from file"""
    with _config_lock(shared=True):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    if 'user_variables' not in config:
        config['user_variables'] = {}
    return config


def save_config(config):
    """Save configuration to file with proper serialization."""

    config_copy = json.loads(json.dumps(config))

    for flow in config_copy.get('notification_flows', []):
        if 'last_data' in flow and not isinstance(flow['last_data'], str):
            try:
                flow['last_data'] = json.dumps(flow['last_data'])
            except Exception:
                flow['last_data'] = ""

    os.makedirs(os.path.dirname(CONFIG_FILE) or '.', exist_ok=True)

    with _config_lock():
        tmp_path = CONFIG_FILE + '.tmp'
        with open(tmp_path, 'w') as tf:
            json.dump(config_copy, tf, indent=4)
        os.replace(tmp_path, CONFIG_FILE)


def get_logs():
    """Get logs from the separate log file"""
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_logs(logs):
    """Save logs to the separate log file"""
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)


def clear_logs():
    """Clear all logs"""
    save_logs([])


def get_log_stats(category=None):
    """Get log statistics, optionally filtered by category"""
    logs = get_logs()

    if category:
        logs = [log for log in logs if log.get('category', 'General') == category]

    all_logs = get_logs()
    category_counts = {}
    for log in all_logs:
        cat = log.get('category', 'General')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        'total_logs': len(logs),
        'oldest_log': logs[0]['timestamp'] if logs else None,
        'newest_log': logs[-1]['timestamp'] if logs else None,
        'category_counts': category_counts,
        'filtered_category': category
    }


def increment_notification_counter():
    """Increment total_notifications_sent by 1 using locked read-modify-write."""
    try:
        with _config_lock():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            config['total_notifications_sent'] = config.get('total_notifications_sent', 0) + 1
            tmp_path = CONFIG_FILE + '.tmp'
            with open(tmp_path, 'w') as tf:
                json.dump(config, tf, indent=4)
            os.replace(tmp_path, CONFIG_FILE)
    except Exception as e:
        print(f"Failed to increment notification counter: {e}", file=sys.stderr)
