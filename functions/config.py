import json
import os
import sys
from datetime import datetime

# Cross-platform file locking
if sys.platform == 'win32':
    import msvcrt
    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    def lock_file(f):
        fcntl.flock(f, fcntl.LOCK_EX)
    def unlock_file(f):
        fcntl.flock(f, fcntl.LOCK_UN)

# Configuration files
CONFIG_FILE = 'data/config.json'
LOG_FILE = 'data/notification_logs.json'

def initialize_files():
    """Initialize config and log files if they don't exist"""
    # Ensure data directory exists
    data_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Initialize default config if file doesn't exist
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "discord_webhook": "",
                "check_interval": 5,
                "log_retention": 1000,
                "notification_log_retention": 500,
                "user_variables": {},
                "total_notifications_sent": 0
            }, f)

    # Initialize log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)

def get_config():
    """Get configuration from file"""
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if 'user_variables' not in config:
        config['user_variables'] = {}
    return config

def save_config(config):
    """Save configuration to file with proper serialization.
    
    Guarantees that 'total_notifications_sent' is monotonic and resilient to
    concurrent saves by performing a locked read-modify-write. Also sanitizes
    non-numeric values to avoid TypeError during comparisons.
    """
    
    def to_non_negative_int(value, default=0):
        try:
            if isinstance(value, bool):
                # Avoid True -> 1 surprises
                return default
            if isinstance(value, int):
                return max(0, value)
            if isinstance(value, float):
                return max(0, int(value))
            if isinstance(value, str):
                v = value.strip()
                # Try int directly; fallback to float then int
                try:
                    return max(0, int(v))
                except Exception:
                    try:
                        return max(0, int(float(v)))
                    except Exception:
                        return default
            return default
        except Exception:
            return default
    
    # Prepare a serializable copy first (convert any complex last_data to string)
    config_copy = config.copy()
    for flow in config_copy.get('notification_flows', []):
        if 'last_data' in flow and not isinstance(flow['last_data'], str):
            try:
                flow['last_data'] = json.dumps(flow['last_data'])
            except Exception:
                # If it cannot be serialized, drop it rather than breaking saves
                flow['last_data'] = ""
    
    # Normalize incoming counter value
    incoming_total = to_non_negative_int(config_copy.get('total_notifications_sent', 0), 0)
    
    # Also bound by current sent notifications log length
    try:
        with open('data/sent_notifications.json', 'r') as f:
            sent_logs = json.load(f)
            current_log_total = to_non_negative_int(len(sent_logs) if isinstance(sent_logs, list) else 0, 0)
    except (FileNotFoundError, json.JSONDecodeError):
        current_log_total = 0
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    # Locked read-modify-write to avoid TOCTOU
    fd = os.open(CONFIG_FILE, os.O_RDWR | os.O_CREAT)
    try:
        with os.fdopen(fd, 'r+') as f:
            lock_file(f)
            try:
                try:
                    f.seek(0)
                    existing_cfg = json.load(f)
                    if not isinstance(existing_cfg, dict):
                        existing_cfg = {}
                except Exception:
                    existing_cfg = {}
                
                existing_total = to_non_negative_int(existing_cfg.get('total_notifications_sent', 0), 0)
                final_total = max(existing_total, incoming_total, current_log_total)
                config_copy['total_notifications_sent'] = final_total
                
                # Write back atomically under the same lock
                f.seek(0)
                json.dump(config_copy, f, indent=4)
                f.truncate()
            finally:
                unlock_file(f)
    except Exception:
        # If something goes wrong with locked write, fall back to a best-effort write
        # using atomic replace to avoid partial writes.
        config_copy['total_notifications_sent'] = max(incoming_total, current_log_total)
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
    
    # Filter by category if specified
    if category:
        logs = [log for log in logs if log.get('category', 'General') == category]
    
    # Get category breakdown
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