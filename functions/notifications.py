import requests
import json
import time
from datetime import datetime
from functions.config import get_config, save_config
from functions.utils import log_notification, format_message_template, evaluate_condition, log_notification_sent
from functions.embed_utils import create_discord_embed

def extract_field_value(data, field_path):
    """Extract field value using bracket notation (e.g., result['0']['web_title'])"""
    try:
        # Convert bracket notation to dot notation for nested access
        # e.g., result['0']['web_title'] -> result.0.web_title
        path = field_path.replace("['", ".").replace("']", "")
        
        # Split the path and traverse the data
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                # Handle array access
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return str(current) if current is not None else None
        
    except Exception as e:
        log_notification(f"Field extraction error for '{field_path}': {str(e)}")
        return None

def send_discord_notification(message, flow=None, data=None):
    """Send a notification to Discord webhook"""
    config = get_config()
    webhook_url = flow.get('webhook_url', '') if flow else config.get('discord_webhook', '')
    
    if not webhook_url:
        return False
    
    # Check conditions if enabled
    if flow and flow.get('condition_enabled', False):
        condition = flow.get('condition', '')
        if condition:
            # Use provided data, or get from flow's last_data
            if data is not None:
                condition_data = data
            elif flow and flow.get('last_data'):
                if isinstance(flow['last_data'], str):
                    try:
                        condition_data = json.loads(flow['last_data'])
                    except json.JSONDecodeError:
                        log_notification(f"Failed to parse last_data JSON for condition: {flow['last_data']}")
                        condition_data = {}
                else:
                    condition_data = flow['last_data']
            else:
                condition_data = {}
            
            # Evaluate the condition
            if not evaluate_condition(condition, condition_data):
                log_notification(f"⏭️ Condition not met for flow '{flow.get('name', 'unnamed')}': {condition}")
                return True  # Return True to indicate "handled" but not sent
    
    try:
        # Handle message formatting with data
        if isinstance(message, str):
            try:
                # Use provided data, or get from flow's last_data
                if data is not None:
                    message_data = data
                elif flow and flow.get('last_data'):
                    if isinstance(flow['last_data'], str):
                        try:
                            message_data = json.loads(flow['last_data'])
                        except json.JSONDecodeError:
                            log_notification(f"Failed to parse last_data JSON: {flow['last_data']}")
                            message_data = {}
                    else:
                        message_data = flow['last_data']
                else:
                    message_data = {}
                
                # Use the new template formatter
                user_variables = config.get('user_variables', {})
                message = format_message_template(message, message_data, user_variables)
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                log_notification(f"Data formatting error: {str(e)}")
                message = format_message_template(message, {})
        
        # Check if embed is enabled and configured
        embed = None
        if flow and flow.get('embed_config', {}).get('enabled', False):
            embed = create_discord_embed(flow['embed_config'], message_data, user_variables)
        
        # Get webhook name and avatar, using defaults if empty
        config = get_config()
        user_variables = config.get('user_variables', {})
        webhook_name = flow.get('webhook_name', '') if flow else ''
        webhook_avatar = flow.get('webhook_avatar', '') if flow else ''
        
        # Use defaults if flow-specific values are empty
        if not webhook_name:
            webhook_name = config.get('default_webhook_name', 'Notification Bot')
        if not webhook_avatar:
            webhook_avatar = config.get('default_webhook_avatar', '')
        
        payload = {
            "username": webhook_name,
        }
        
        # Always add content if message template has content (even with embeds)
        if message and message.strip():
            payload["content"] = message
        
        # Add embed if available
        if embed:
            payload["embeds"] = [embed]
        
        if webhook_avatar:
            payload["avatar_url"] = webhook_avatar
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        success = response.status_code == 204
        
        if success:
            # Log what was actually sent
            notification_details = []
            if message and message.strip():
                notification_details.append(f"Message: {message}")
            if embed:
                embed_title = embed.get('title', 'No title')
                embed_description = embed.get('description', 'No description')[:100] + '...' if len(embed.get('description', '')) > 100 else embed.get('description', 'No description')
                notification_details.append(f"Embed: {embed_title} - {embed_description}")
            
            notification_summary = " | ".join(notification_details) if notification_details else "Empty notification"
            log_notification(f"✅ Notification sent successfully to Discord webhook: {notification_summary}")
            
            # Only log to notification-specific log if there's actual content
            if message and message.strip() or embed:
                flow_name = flow.get('name', 'Test') if flow else 'Test'
                embed_info = None
                if embed:
                    embed_info = {
                        'title': embed.get('title', ''),
                        'description': embed.get('description', '')[:200] if embed.get('description') else '',
                        'color': embed.get('color', ''),
                        'url': embed.get('url', '')
                    }
                log_notification_sent(flow_name, message, embed_info, webhook_name)
        else:
            log_notification(f"❌ Failed to send notification to Discord (Status: {response.status_code})")
        
        return success
        
    except Exception as e:
        log_notification(f"❌ Discord send error: {str(e)}")
        return False

def make_api_request(endpoint, headers=None, request_body=None):
    """Make an API request with optional headers and request body (POST if body, else GET)"""
    try:
        req_headers = {h['key']: h['value'] for h in headers} if headers else {}
        
        if request_body:
            # POST request
            # Check if Content-Type is application/json
            content_type = req_headers.get('Content-Type', '').lower()
            
            if 'application/json' in content_type:
                # Try to parse as JSON first
                try:
                    json_body = json.loads(request_body)
                    response = requests.post(endpoint, headers=req_headers, json=json_body, timeout=5)
                except json.JSONDecodeError:
                    # If it's not valid JSON, check if it looks like a GraphQL query
                    if request_body.strip().startswith('{') and 'query' not in request_body:
                        # This looks like a GraphQL query without the wrapper
                        json_body = {"query": request_body}
                        response = requests.post(endpoint, headers=req_headers, json=json_body, timeout=5)
                    else:
                        # Send as raw string
                        response = requests.post(endpoint, headers=req_headers, data=request_body, timeout=5)
            else:
                # Non-JSON content type, send as raw data
                response = requests.post(endpoint, headers=req_headers, data=request_body, timeout=5)
        else:
            # GET request
            response = requests.get(endpoint, headers=req_headers, timeout=5)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_notification(f"API request error: {str(e)}")
        return None

def check_endpoints():
    """Monitor endpoints and send notifications based on triggers"""
    while True:
        config = get_config()
        check_interval = config.get('check_interval', 5)  # Default to 5 seconds
        config_changed = False  # Track if we need to save
        
        for flow in config.get('notification_flows', []):
            if not flow.get('active', False):
                continue 
            try:
                # Skip webhook-triggered flows
                if flow['trigger_type'] == 'on_incoming':
                    continue
                
                # Get API data if endpoint is configured
                api_data = None
                current_value = None
                if flow.get('endpoint'):
                    try:
                        api_data = make_api_request(
                            flow['endpoint'],
                            flow.get('api_headers'),
                            flow.get('api_request_body')
                        )
                        # Extract field value using the same logic as template formatter
                        if flow.get('field'):
                            current_value = extract_field_value(api_data, flow['field'])
                        else:
                            current_value = None
                    except Exception as api_error:
                        log_notification(f"API error in {flow['name']}: {str(api_error)}")
                        continue
                
                # Handle timer-based flows
                if flow['trigger_type'] == 'timer':
                    now = time.time()
                    last_run = flow.get('last_run', 0)
                    interval = flow.get('interval', 5) * 60
                    
                    if now - last_run >= interval:
                        log_notification(f"⏰ Timer trigger: Sending notification for flow '{flow['name']}'")
                        # Create data object for condition evaluation
                        timer_data = api_data.copy() if api_data else {}
                        timer_data.update({
                            'value': current_value,
                            'api_data': api_data
                        })
                        if send_discord_notification(flow['message_template'], flow, timer_data):
                            flow['last_run'] = now
                            config_changed = True
                
                # Handle change detection flows
                elif flow['trigger_type'] == 'on_change':
                    if not flow.get('endpoint') or not flow.get('field'):
                        continue
                        
                    if 'last_value' not in flow:
                        flow['last_value'] = current_value
                        config_changed = True
                        continue
                    
                    if current_value != flow['last_value']:
                        log_notification(f"🔄 Change detected: Field '{flow['field']}' changed from '{flow['last_value']}' to '{current_value}' in flow '{flow['name']}'")
                        # Create a data object that includes both API data and change information
                        change_data = api_data.copy() if api_data else {}
                        change_data.update({
                            'value': current_value,
                            'old_value': flow['last_value'],
                            'api_data': api_data  # Keep original API data as well
                        })
                        if send_discord_notification(flow['message_template'], flow, change_data):
                            flow['last_value'] = current_value
                            config_changed = True
                            
            except Exception as e:
                log_notification(f"Error in flow {flow.get('name', 'unnamed')}: {str(e)}")
        
        # Only save if something changed
        if config_changed:
            save_config(config)
        
        time.sleep(check_interval)  # Use configurable check interval 