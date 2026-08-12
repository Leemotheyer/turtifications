import hashlib
import requests
import json
import time
from datetime import datetime
from functions.config import get_config, save_config, increment_notification_counter
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
            log_notification(f"✅ Notification sent successfully to Discord webhook (Status: {response.status_code}): {notification_summary}")
            
            # Increment total_notifications_sent
            increment_notification_counter()
            
            # Always log to notification-specific log when notification is sent successfully
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

def _is_webhook_flow(flow):
    """Return True for incoming-webhook flows that should not be polled."""
    return flow.get('trigger_type') in ('webhook', 'on_incoming')


def _api_request_cache_key(flow):
    """Build a stable cache key for deduplicating identical API requests."""
    endpoint = flow.get('endpoint')
    if not endpoint:
        return None

    headers = flow.get('api_headers') or []
    normalized_headers = sorted(
        (header.get('key', ''), header.get('value', ''))
        for header in headers
        if header.get('key')
    )
    body = flow.get('api_request_body') or ''
    payload = json.dumps(
        {'endpoint': endpoint, 'headers': normalized_headers, 'body': body},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _flow_check_interval_seconds(flow, default_interval):
    """Return how long to wait before checking this flow again."""
    if flow.get('trigger_type') == 'timer':
        return max(60, int(flow.get('interval', 5) or 5) * 60)
    return max(1, int(flow.get('poll_interval', default_interval) or default_interval))


def _fetch_api_data_for_flow(flow, api_cache):
    """Fetch API data once per unique endpoint/headers/body per monitor cycle."""
    if not flow.get('endpoint'):
        return None, None

    cache_key = _api_request_cache_key(flow)
    if cache_key in api_cache:
        api_data = api_cache[cache_key]
    else:
        api_data = make_api_request(
            flow['endpoint'],
            flow.get('api_headers'),
            flow.get('api_request_body'),
        )
        if cache_key:
            api_cache[cache_key] = api_data

    current_value = None
    if api_data is not None and flow.get('field'):
        current_value = extract_field_value(api_data, flow['field'])
        log_notification(
            f"🔍 Field extraction for '{flow['name']}': field='{flow['field']}' -> value='{current_value}'"
        )

    return api_data, current_value


def _process_timer_flow(flow, api_data, current_value, now):
    """Run a timer flow when its interval has elapsed. Returns True if config changed."""
    last_run = flow.get('last_run', 0)
    interval = max(60, int(flow.get('interval', 5) or 5) * 60)

    if now - last_run < interval:
        return False

    log_notification(f"⏰ Scheduled monitoring: Running check for flow '{flow['name']}'")
    timer_data = api_data.copy() if isinstance(api_data, dict) else {}
    timer_data.update({
        'value': current_value,
        'old_value': flow.get('last_value'),
        'api_data': api_data,
    })

    if send_discord_notification(flow['message_template'], flow, timer_data):
        flow['last_run'] = now
        flow['last_value'] = current_value
        log_notification(f"✅ Updated last_value for timer flow '{flow['name']}' to '{current_value}'")
        return True

    log_notification(f"❌ Failed to send notification for timer flow '{flow['name']}', last_value not updated")
    return False


def _process_change_flow(flow, api_data, current_value, last_no_change_log):
    """Run a change-detection flow. Returns True if config changed."""
    if not flow.get('endpoint') or not flow.get('field'):
        return False

    if 'last_value' not in flow:
        flow['last_value'] = current_value
        log_notification(
            f"🔍 Change detection: Initialized baseline for flow '{flow['name']}' with value '{current_value}'"
        )
        return True

    if current_value == flow['last_value']:
        flow_name = flow['name']
        now = time.time()
        if now - last_no_change_log.get(flow_name, 0) >= 3600:
            last_no_change_log[flow_name] = now
            log_notification(
                f"🔄 No change detected: Field '{flow['field']}' value '{current_value}' unchanged in flow '{flow_name}'"
            )
        return False

    log_notification(
        f"🔄 Change detected: Field '{flow['field']}' changed from '{flow['last_value']}' to '{current_value}' in flow '{flow['name']}'"
    )
    change_data = api_data.copy() if isinstance(api_data, dict) else {}
    change_data.update({
        'value': current_value,
        'old_value': flow['last_value'],
        'api_data': api_data,
    })

    if send_discord_notification(flow['message_template'], flow, change_data):
        flow['last_value'] = current_value
        log_notification(f"✅ Updated last_value for flow '{flow['name']}' to '{current_value}'")
        return True

    log_notification(f"❌ Failed to send notification for flow '{flow['name']}', last_value not updated")
    return False


def check_endpoints():
    """Monitor endpoints and send notifications based on triggers."""
    max_consecutive_errors = 5
    consecutive_errors = 0
    base_retry_delay = 1
    next_check_at = {}
    last_no_change_log = {}

    while True:
        try:
            config = get_config()
            default_interval = max(1, int(config.get('check_interval', 5) or 5))
            config_changed = False
            now = time.time()
            api_cache = {}

            due_flows = []
            for flow in config.get('notification_flows', []):
                if not flow.get('active', False) or _is_webhook_flow(flow):
                    continue

                flow_name = flow.get('name') or 'unnamed'
                if flow_name not in next_check_at:
                    next_check_at[flow_name] = 0

                if now >= next_check_at[flow_name]:
                    due_flows.append(flow)

            for flow in due_flows:
                flow_name = flow.get('name') or 'unnamed'
                interval = _flow_check_interval_seconds(flow, default_interval)

                try:
                    api_data = None
                    current_value = None
                    if flow.get('endpoint'):
                        api_data, current_value = _fetch_api_data_for_flow(flow, api_cache)
                        if flow.get('field') and api_data is None:
                            next_check_at[flow_name] = now + interval
                            continue

                    if flow.get('trigger_type') == 'timer':
                        if _process_timer_flow(flow, api_data, current_value, now):
                            config_changed = True
                    elif flow.get('trigger_type') == 'on_change':
                        if _process_change_flow(flow, api_data, current_value, last_no_change_log):
                            config_changed = True
                except Exception as e:
                    log_notification(f"Error in flow {flow_name}: {str(e)}")
                finally:
                    next_check_at[flow_name] = now + interval

            if config_changed:
                try:
                    save_config(config)
                except Exception as save_error:
                    log_notification(f"Failed to save config: {str(save_error)}")

            consecutive_errors = 0

            active_names = {
                flow.get('name')
                for flow in config.get('notification_flows', [])
                if flow.get('active') and not _is_webhook_flow(flow)
            }
            for name in list(next_check_at.keys()):
                if name not in active_names:
                    del next_check_at[name]

            if next_check_at:
                sleep_for = max(1, min(next_check_at.values()) - time.time())
            else:
                sleep_for = default_interval
            time.sleep(max(1, sleep_for))

        except KeyboardInterrupt:
            log_notification("Monitoring thread received shutdown signal")
            break

        except Exception as main_error:
            consecutive_errors += 1
            retry_delay = min(base_retry_delay * (2 ** (consecutive_errors - 1)), 60)
            log_notification(f"Monitoring thread error #{consecutive_errors}: {str(main_error)}")

            if consecutive_errors >= max_consecutive_errors:
                log_notification(
                    f"Too many consecutive errors ({consecutive_errors}). Monitoring thread will restart with {retry_delay}s delay."
                )
                consecutive_errors = 0

            time.sleep(retry_delay)

    log_notification("Monitoring thread stopped") 