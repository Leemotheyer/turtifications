import json
import os
import sys
from datetime import datetime



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
    """Save configuration to file with proper serialization."""
    
    # Prepare a serializable copy first (convert any complex last_data to string)
    config_copy = config.copy()
    for flow in config_copy.get('notification_flows', []):
        if 'last_data' in flow and not isinstance(flow['last_data'], str):
            try:
                flow['last_data'] = json.dumps(flow['last_data'])
            except Exception:
                # If it cannot be serialized, drop it rather than breaking saves
                flow['last_data'] = ""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    # Simple atomic write using temporary file
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

def increment_notification_counter():
    """Simple function to increment total_notifications_sent by 1"""
    print("Incrementing notification counter")
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        current_total = config.get('total_notifications_sent', 0)
        config['total_notifications_sent'] = current_total + 1
        
        # Use atomic write like save_config
        tmp_path = CONFIG_FILE + '.tmp'
        with open(tmp_path, 'w') as tf:
            json.dump(config, tf, indent=4)
        os.replace(tmp_path, CONFIG_FILE)

        print(f"Notification counter incremented to {config['total_notifications_sent']}")
            
    except Exception as e:
        # If something goes wrong, just log it and continue
        print(f"Failed to increment notification counter: {e}")