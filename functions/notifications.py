import requests
import json
import time
from datetime import datetime
from functions.config import get_config, save_config
from functions.utils import log_notification, format_message_template, evaluate_condition, log_notification_sent
from functions.embed_utils import create_discord_embed
from functions.image_utils import download_image_to_temp, cleanup_temp_files, get_image_filename_from_url, get_mime_type_from_extension

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
        
        if current is not None:
            # If the result is a dictionary or list, convert to JSON string for consistent comparison
            if isinstance(current, (dict, list)):
                return json.dumps(current, sort_keys=True)
            else:
                return str(current)
        return None
        
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
        # Handle message formatting with data and extract images
        image_attachments = []
        temp_files = []
        
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
        
        if isinstance(message, str):
            try:
                # Use the new template formatter with image extraction
                user_variables = config.get('user_variables', {})
                message, image_urls = format_message_template(message, message_data, user_variables, extract_images=True)
                
                # Log image extraction for debugging
                if image_urls:
                    log_notification(f"🖼️ Extracted {len(image_urls)} image URL(s) from message template")
                
                # Download images from URLs and prepare for attachment
                for image_url in image_urls:
                    temp_file_path = download_image_to_temp(image_url)
                    if temp_file_path:
                        temp_files.append(temp_file_path)
                        filename = get_image_filename_from_url(image_url)
                        image_attachments.append({
                            'file_path': temp_file_path,
                            'filename': filename
                        })
                        log_notification(f"🖼️ Downloaded image: {filename} from {image_url}")
                    else:
                        log_notification(f"❌ Failed to download image from: {image_url}")
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                log_notification(f"Data formatting error: {str(e)}")
                message, image_urls = format_message_template(message, {}, extract_images=True)
                # Still try to download images even if data formatting failed
                for image_url in image_urls:
                    temp_file_path = download_image_to_temp(image_url)
                    if temp_file_path:
                        temp_files.append(temp_file_path)
                        filename = get_image_filename_from_url(image_url)
                        image_attachments.append({
                            'file_path': temp_file_path,
                            'filename': filename
                        })
        
        # Check if embed is enabled and configured
        embed = None
        if flow and flow.get('embed_config', {}).get('enabled', False):
            embed = create_discord_embed(flow['embed_config'], message_data, user_variables)

            # If embed has image/thumbnail URLs, download them and attach as files
            # This makes embeds work even when URLs are not publicly accessible to Discord
            try:
                # Handle main image
                if embed and isinstance(embed, dict):
                    if 'image' in embed and isinstance(embed['image'], dict):
                        image_url_value = embed['image'].get('url')
                        if isinstance(image_url_value, str) and image_url_value.startswith(('http://', 'https://')):
                            log_notification(f"🖼️ Processing embed image: {image_url_value}")
                            temp_file_path = download_image_to_temp(image_url_value)
                            if temp_file_path:
                                temp_files.append(temp_file_path)
                                filename = get_image_filename_from_url(image_url_value)
                                image_attachments.append({
                                    'file_path': temp_file_path,
                                    'filename': filename
                                })
                                # Reference the attached file in the embed
                                embed['image']['url'] = f"attachment://{filename}"
                                log_notification(f"🖼️ Embed image attached: {filename}")
                            else:
                                log_notification(f"❌ Failed to download embed image: {image_url_value}")

                    # Handle thumbnail
                    if 'thumbnail' in embed and isinstance(embed['thumbnail'], dict):
                        thumb_url_value = embed['thumbnail'].get('url')
                        if isinstance(thumb_url_value, str) and thumb_url_value.startswith(('http://', 'https://')):
                            log_notification(f"🖼️ Processing embed thumbnail: {thumb_url_value}")
                            temp_file_path = download_image_to_temp(thumb_url_value)
                            if temp_file_path:
                                temp_files.append(temp_file_path)
                                filename = get_image_filename_from_url(thumb_url_value)
                                image_attachments.append({
                                    'file_path': temp_file_path,
                                    'filename': filename
                                })
                                # Reference the attached file in the embed
                                embed['thumbnail']['url'] = f"attachment://{filename}"
                                log_notification(f"🖼️ Embed thumbnail attached: {filename}")
                            else:
                                log_notification(f"❌ Failed to download embed thumbnail: {thumb_url_value}")
            except Exception as embed_img_err:
                log_notification(f"Embed image processing error: {str(embed_img_err)}")
        
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
        
        # Send request with or without file attachments
        try:
            if image_attachments:
                # Prepare multipart form data for file uploads
                files = {}
                for i, attachment in enumerate(image_attachments):
                    file_key = f'file{i}'
                    mime_type = get_mime_type_from_extension(attachment['file_path'])
                    with open(attachment['file_path'], 'rb') as f:
                        files[file_key] = (attachment['filename'], f.read(), mime_type)
                
                # For multipart requests, payload needs to be sent as 'payload_json'
                multipart_data = {
                    'payload_json': json.dumps(payload)
                }
                
                response = requests.post(webhook_url, data=multipart_data, files=files, timeout=30)
            else:
                # Standard JSON request without attachments
                response = requests.post(webhook_url, json=payload, timeout=10)
            
            success = response.status_code in [200, 204]
        finally:
            # Always cleanup temporary files
            cleanup_temp_files(temp_files)
        
        if success:
            # Log what was actually sent
            notification_details = []
            if message and message.strip():
                notification_details.append(f"Message: {message}")
            if embed:
                embed_title = embed.get('title', 'No title')
                embed_description = embed.get('description', 'No description')[:100] + '...' if len(embed.get('description', '')) > 100 else embed.get('description', 'No description')
                notification_details.append(f"Embed: {embed_title} - {embed_description}")
            if image_attachments:
                notification_details.append(f"Images: {len(image_attachments)} attachment(s)")
            
            notification_summary = " | ".join(notification_details) if notification_details else "Empty notification"
            log_notification(f"✅ Notification sent successfully to Discord webhook: {notification_summary}")
            log_notification(f"✅ Discord API returned status {response.status_code} - notification sent successfully")
            
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
            if response.text:
                log_notification(f"❌ Discord error response: {response.text[:500]}")
        
        return success
        
    except Exception as e:
        log_notification(f"❌ Discord send error: {str(e)}")
        # Cleanup temporary files on error
        if 'temp_files' in locals():
            cleanup_temp_files(temp_files)
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
    max_consecutive_errors = 5
    consecutive_errors = 0
    base_retry_delay = 1  # Start with 1 second delay
    
    while True:
        try:
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
                                log_notification(f"🔍 Field extraction for '{flow['name']}': field='{flow['field']}' -> value='{current_value}'")
                            else:
                                current_value = None
                        except Exception as api_error:
                            log_notification(f"API error in {flow['name']}: {str(api_error)}")
                            continue
                    
                    # Handle scheduled monitoring (timer-based flows)
                    if flow['trigger_type'] == 'timer':
                        now = time.time()
                        last_run = flow.get('last_run', 0)
                        interval = flow.get('interval', 5) * 60
                        
                        if now - last_run >= interval:
                            log_notification(f"⏰ Scheduled monitoring: Running check for flow '{flow['name']}'")
                            # Create data object for condition evaluation
                            timer_data = api_data.copy() if api_data else {}
                            timer_data.update({
                                'value': current_value,
                                'old_value': flow.get('last_value'),  # Include old_value for template support
                                'api_data': api_data
                            })
                            notification_sent = send_discord_notification(flow['message_template'], flow, timer_data)
                            if notification_sent:
                                flow['last_run'] = now
                                # Store current value as last_value for next run
                                flow['last_value'] = current_value
                                config_changed = True
                                log_notification(f"✅ Updated last_value for timer flow '{flow['name']}' to '{current_value}'")
                            else:
                                log_notification(f"❌ Failed to send notification for timer flow '{flow['name']}', last_value not updated")
                    
                    # Handle change detection flows (immediate on change)
                    elif flow['trigger_type'] == 'on_change':
                        if not flow.get('endpoint') or not flow.get('field'):
                            continue
                            
                        # Initialize last_value if not present
                        if 'last_value' not in flow:
                            flow['last_value'] = current_value
                            config_changed = True
                            log_notification(f"🔍 Change detection: Initialized baseline for flow '{flow['name']}' with value '{current_value}'")
                            continue
                        
                        # Only proceed if value actually changed
                        if current_value != flow['last_value']:
                            log_notification(f"🔄 Change detected: Field '{flow['field']}' changed from '{flow['last_value']}' to '{current_value}' in flow '{flow['name']}'")
                            # Create a data object that includes both API data and change information
                            change_data = api_data.copy() if api_data else {}
                            change_data.update({
                                'value': current_value,
                                'old_value': flow['last_value'],
                                'api_data': api_data  # Keep original API data as well
                            })
                            notification_sent = send_discord_notification(flow['message_template'], flow, change_data)
                            if notification_sent:
                                flow['last_value'] = current_value
                                config_changed = True
                                log_notification(f"✅ Updated last_value for flow '{flow['name']}' to '{current_value}'")
                            else:
                                log_notification(f"❌ Failed to send notification for flow '{flow['name']}', last_value not updated")
                        else:
                            log_notification(f"🔄 No change detected: Field '{flow['field']}' value '{current_value}' unchanged in flow '{flow['name']}'")
                                
                except Exception as e:
                    log_notification(f"Error in flow {flow.get('name', 'unnamed')}: {str(e)}")
            
            # Only save if something changed
            if config_changed:
                try:
                    save_config(config)
                except Exception as save_error:
                    log_notification(f"Failed to save config: {str(save_error)}")
            
            # Reset error counter on successful iteration
            consecutive_errors = 0
            
            time.sleep(check_interval)  # Use configurable check interval
            
        except KeyboardInterrupt:
            # Handle graceful shutdown
            log_notification("Monitoring thread received shutdown signal")
            break
            
        except Exception as main_error:
            # Handle any unexpected errors in the main loop
            consecutive_errors += 1
            retry_delay = min(base_retry_delay * (2 ** (consecutive_errors - 1)), 60)  # Exponential backoff, max 60s
            
            log_notification(f"Monitoring thread error #{consecutive_errors}: {str(main_error)}")
            
            if consecutive_errors >= max_consecutive_errors:
                log_notification(f"Too many consecutive errors ({consecutive_errors}). Monitoring thread will restart with {retry_delay}s delay.")
                consecutive_errors = 0  # Reset counter
            
            # Wait before retrying, but don't let the delay get too long
            time.sleep(retry_delay)
    
    log_notification("Monitoring thread stopped") 