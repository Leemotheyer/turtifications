"""
Flow statistics and management features
"""

import json
import time
from datetime import datetime, timedelta
from functions.config import get_logs

def get_flow_statistics():
    """Get statistics for all flows (including those that have never run)"""
    logs = get_logs()
    log_stats = get_flow_usage_from_logs(logs)

    from functions.config import get_config
    config = get_config()
    all_flows = {flow['name']: flow for flow in config.get('notification_flows', [])}

    # Build a complete stats dict for all flows
    all_stats = {}
    for flow_name, flow_config in all_flows.items():
        # Start with log stats if present, else zero/defaults
        stats = log_stats.get(flow_name, {
            'total_runs': 0,
            'timer_runs': 0,
            'change_runs': 0,
            'webhook_runs': 0,
            'test_runs': 0,
            'first_run': None,
            'last_run': None,
            'successful_runs': 0,
            'failed_runs': 0
        })
        # Always update with config info
        stats.update({
            'active': flow_config.get('active', False),
            'trigger_type': flow_config.get('trigger_type', 'unknown'),
            'category': flow_config.get('category', 'General'),
            'last_run': flow_config.get('last_run', stats.get('last_run')),
            'last_value': flow_config.get('last_value')
        })
        all_stats[flow_name] = stats
    return all_stats

def get_flow_usage_from_logs(logs):
    """Extract flow usage statistics from logs"""
    flow_stats = {}
    
    for log in logs:
        message = log.get('message', '')
        timestamp = log.get('timestamp', '')
        
        # Parse different types of log messages
        if 'Timer trigger: Sending notification for flow' in message:
            flow_name = extract_flow_name_from_message(message)
            if flow_name:
                update_flow_stats(flow_stats, flow_name, 'timer', timestamp)
                
        elif 'Change detected: Field' in message and 'in flow' in message:
            flow_name = extract_flow_name_from_message(message)
            if flow_name:
                update_flow_stats(flow_stats, flow_name, 'change', timestamp)
                
        elif 'Webhook received: Processing webhook for flow' in message:
            flow_name = extract_flow_name_from_message(message)
            if flow_name:
                update_flow_stats(flow_stats, flow_name, 'webhook', timestamp)
                
        elif 'Test notification sent for' in message:
            flow_name = extract_flow_name_from_message(message)
            if flow_name:
                update_flow_stats(flow_stats, flow_name, 'test', timestamp)
    
    return flow_stats

def extract_flow_name_from_message(message):
    """Extract flow name from log message"""
    import re
    
    # Different patterns for extracting flow names
    patterns = [
        r"flow '([^']+)'",
        r"for flow '([^']+)'",
        r"flow ([^\s]+)",
        r"sent for ([^\s]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    
    return None

def update_flow_stats(flow_stats, flow_name, trigger_type, timestamp):
    """Update statistics for a flow"""
    if flow_name not in flow_stats:
        flow_stats[flow_name] = {
            'total_runs': 0,
            'timer_runs': 0,
            'change_runs': 0,
            'webhook_runs': 0,
            'test_runs': 0,
            'first_run': timestamp,
            'last_run': timestamp,
            'successful_runs': 0,
            'failed_runs': 0
        }
    
    stats = flow_stats[flow_name]
    stats['total_runs'] += 1
    stats['last_run'] = timestamp
    
    if trigger_type == 'timer':
        stats['timer_runs'] += 1
    elif trigger_type == 'change':
        stats['change_runs'] += 1
    elif trigger_type == 'webhook':
        stats['webhook_runs'] += 1
    elif trigger_type == 'test':
        stats['test_runs'] += 1

def get_flow_success_rate(flow_name):
    """Get success rate for a specific flow"""
    logs = get_logs()
    successful = 0
    failed = 0
    
    for log in logs:
        message = log.get('message', '')
        if flow_name in message:
            if '✅ Notification sent successfully' in message:
                successful += 1
            elif '❌ Failed to send notification' in message or '❌ Discord send error' in message:
                failed += 1
    
    total = successful + failed
    if total == 0:
        return 0
    
    return (successful / total) * 100

def get_recent_flow_activity(hours=24):
    """Get flow activity in the last N hours"""
    logs = get_logs()
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    recent_activity = {}
    
    for log in logs:
        try:
            log_time = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
            if log_time >= cutoff_time:
                message = log['message']
                
                # Extract flow name and activity type
                if 'flow' in message:
                    flow_name = extract_flow_name_from_message(message)
                    if flow_name:
                        if flow_name not in recent_activity:
                            recent_activity[flow_name] = []
                        
                        activity_type = 'unknown'
                        if 'Timer trigger' in message:
                            activity_type = 'timer'
                        elif 'Change detected' in message:
                            activity_type = 'change'
                        elif 'Webhook received' in message:
                            activity_type = 'webhook'
                        elif 'Test notification' in message:
                            activity_type = 'test'
                        
                        recent_activity[flow_name].append({
                            'type': activity_type,
                            'timestamp': log['timestamp'],
                            'message': message
                        })
        except (ValueError, KeyError):
            continue
    
    return recent_activity

def export_flow_config(flow_name=None):
    """Export flow configuration(s) to JSON"""
    from functions.config import get_config
    config = get_config()
    
    if flow_name:
        # Export specific flow
        for flow in config.get('notification_flows', []):
            if flow['name'] == flow_name:
                return {
                    'export_date': datetime.now().isoformat(),
                    'flow': flow
                }
        return None
    else:
        # Export all flows
        return {
            'export_date': datetime.now().isoformat(),
            'flows': config.get('notification_flows', []),
            'settings': {
                'discord_webhook': config.get('discord_webhook'),
                'default_webhook_name': config.get('default_webhook_name'),
                'default_webhook_avatar': config.get('default_webhook_avatar'),
                'check_interval': config.get('check_interval'),
                'log_retention': config.get('log_retention')
            }
        }

def import_flow_config(import_data):
    """Import flow configuration from JSON"""
    from functions.config import get_config, save_config
    config = get_config()
    
    if 'flow' in import_data:
        # Import single flow
        new_flow = import_data['flow']
        new_flow['name'] = f"{new_flow['name']}_imported_{int(time.time())}"
        
        if 'notification_flows' not in config:
            config['notification_flows'] = []
        
        config['notification_flows'].append(new_flow)
        save_config(config)
        return new_flow['name']
        
    elif 'flows' in import_data:
        # Import multiple flows
        imported_flows = []
        
        for flow in import_data['flows']:
            new_flow = flow.copy()
            new_flow['name'] = f"{new_flow['name']}_imported_{int(time.time())}"
            imported_flows.append(new_flow)
        
        if 'notification_flows' not in config:
            config['notification_flows'] = []
        
        config['notification_flows'].extend(imported_flows)
        
        # Import settings if provided
        if 'settings' in import_data:
            settings = import_data['settings']
            for key, value in settings.items():
                if value is not None:
                    config[key] = value
        
        save_config(config)
        return [flow['name'] for flow in imported_flows]
    
    return None

def duplicate_flow(flow_name):
    """Duplicate an existing flow"""
    from functions.config import get_config, save_config
    config = get_config()
    
    for flow in config.get('notification_flows', []):
        if flow['name'] == flow_name:
            new_flow = flow.copy()
            new_flow['name'] = f"{flow['name']}_copy_{int(time.time())}"
            new_flow['active'] = False  # Start as inactive
            
            # Remove tracking data from copy
            new_flow.pop('last_value', None)
            new_flow.pop('last_run', None)
            new_flow.pop('last_data', None)
            
            config['notification_flows'].append(new_flow)
            save_config(config)
            return new_flow['name']
    
    return None 