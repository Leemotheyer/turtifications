import json
import os
from datetime import datetime

# Configuration files
CONFIG_FILE = 'data/config.json'
LOG_FILE = 'data/notification_logs.json'

def initialize_files():
    """Initialize config and log files if they don't exist"""
    # Initialize default config if file doesn't exist
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "discord_webhook": "",
                "check_interval": 5,
                "log_retention": 1000,
                "notification_log_retention": 100,
                "user_variables": {}
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
    """Save configuration to file with proper serialization"""
    # Create a copy of config to avoid modifying the original
    config_copy = config.copy()
    
    # Convert any last_data that might be complex objects to JSON strings
    for flow in config_copy.get('notification_flows', []):
        if 'last_data' in flow and not isinstance(flow['last_data'], str):
            flow['last_data'] = json.dumps(flow['last_data'])
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_copy, f, indent=4)

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