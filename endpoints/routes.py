from flask import render_template, request, redirect, url_for, jsonify, flash, abort, send_file
import secrets
import requests
import json
import io
from datetime import datetime
from functions.config import get_config, save_config, get_logs, clear_logs, get_log_stats
from functions.utils import log_notification, get_notification_logs, format_message_template
from functions.notifications import send_discord_notification, make_api_request
from functions.embed_utils import validate_embed_config, create_discord_embed
from functions.flow_templates import FLOW_TEMPLATES, get_template_categories, get_templates_by_category, get_template
from functions.flow_stats import get_flow_statistics, get_flow_success_rate, get_recent_flow_activity, export_flow_config, import_flow_config, duplicate_flow

def init_routes(app):
    """Initialize all Flask routes"""
    
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).strftime(format)
        elif isinstance(value, str):
            return value
        return ''

    @app.route('/', methods=['GET', 'POST'])
    def index():
        config = get_config()
        test_result = None
        
        if request.method == 'POST':
            # Handle test notification
            test_message = request.form.get('test_message', '').strip()
            if test_message:
                # Create a simple test flow for sending
                test_flow = {
                    'webhook_url': config.get('discord_webhook', ''),
                    'webhook_name': '',  # Use default
                    'webhook_avatar': '',  # Use default
                    'message_template': test_message
                }
                
                if test_flow['webhook_url']:
                    test_result = send_discord_notification(test_message, test_flow)
                    if test_result:
                        log_notification(f"🧪 Homepage test notification sent: {test_message}")
                        flash('Test notification sent successfully!', 'success')
                    else:
                        log_notification(f"❌ Homepage test notification failed: {test_message}")
                        flash('Failed to send test notification. Check your webhook configuration.', 'error')
                else:
                    flash('Discord webhook not configured. Please configure it in the Configure page.', 'error')
                
                # Redirect to prevent form resubmission
                return redirect(url_for('index'))
        
        active_flows = [flow for flow in config.get('notification_flows', []) 
                      if flow.get('active', False)]
        
        # Convert last_run timestamp to readable format if it exists
        for flow in active_flows:
            if 'last_run' in flow and isinstance(flow['last_run'], (int, float)):
                flow['last_run'] = datetime.fromtimestamp(flow['last_run']).strftime('%Y-%m-%d %H:%M:%S')

        # Get last 10 notification logs (most recent first)
        notification_logs = list(reversed(get_notification_logs()))[:10]
        
        return render_template('index.html', 
                             active_flows=active_flows,
                             notification_logs=notification_logs)

    @app.route('/configure', methods=['GET', 'POST'])
    def configure():
        config = get_config()
        user_variables = config.get('user_variables', {})
        if request.method == 'POST':
            try:
                # Discord webhook settings
                webhook_url = request.form.get('webhook_url', '').strip()
                default_webhook_name = request.form.get('default_webhook_name', 'Notification Bot').strip()
                default_webhook_avatar = request.form.get('default_webhook_avatar', '').strip()
                # System settings
                check_interval = int(request.form.get('check_interval', 5))
                log_retention = int(request.form.get('log_retention', 1000))
                notification_log_retention = int(request.form.get('notification_log_retention', 100))
                # User variables
                var_keys = request.form.getlist('var_key[]')
                var_vals = request.form.getlist('var_value[]')
                user_variables = {}
                for k, v in zip(var_keys, var_vals):
                    k = k.strip()
                    if k:
                        user_variables[k] = v
                # Validate inputs
                if not webhook_url:
                    flash('Discord webhook URL is required', 'error')
                    return redirect(url_for('configure'))
                if check_interval < 1 or check_interval > 3600:
                    flash('Check interval must be between 1 and 3600 seconds', 'error')
                    return redirect(url_for('configure'))
                if log_retention < 100 or log_retention > 10000:
                    flash('Log retention must be between 100 and 10000 entries', 'error')
                    return redirect(url_for('configure'))
                if notification_log_retention < 10 or notification_log_retention > 1000:
                    flash('Notification log retention must be between 10 and 1000 entries', 'error')
                    return redirect(url_for('configure'))
                # Update configuration
                config['discord_webhook'] = webhook_url
                config['default_webhook_name'] = default_webhook_name
                config['default_webhook_avatar'] = default_webhook_avatar
                config['check_interval'] = check_interval
                config['log_retention'] = log_retention
                config['notification_log_retention'] = notification_log_retention
                config['user_variables'] = user_variables
                save_config(config)
                log_notification("System configuration updated")
                flash('Configuration saved successfully!', 'success')
                return redirect(url_for('configure'))
            except ValueError as e:
                flash('Invalid input values. Please check your settings.', 'error')
                return redirect(url_for('configure'))
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                return redirect(url_for('configure'))
        return render_template('configure.html', config=config, user_variables=user_variables)

    @app.route('/logs')
    def show_logs():
        category = request.args.get('category', '')
        logs = get_logs()
        
        # Filter by category if specified
        if category:
            logs = [log for log in logs if log.get('category', 'General') == category]
        
        # Get unique categories for filter dropdown
        all_logs = get_logs()
        categories = list(set(log.get('category', 'General') for log in all_logs))
        categories.sort()
        
        return render_template('logs.html', 
                             logs=reversed(logs), 
                             categories=categories,
                             selected_category=category)

    @app.route('/logs/clear', methods=['POST'])
    def clear_notification_logs():
        clear_logs()
        log_notification("Notification logs cleared")
        return redirect(url_for('show_logs'))

    @app.route('/logs/stats')
    def get_log_stats_endpoint():
        category = request.args.get('category', '')
        stats = get_log_stats(category=category)
        return jsonify(stats)

    @app.route('/builder', methods=['GET', 'POST'])
    def notification_builder():
        config = get_config()
        edit_index = request.args.get('edit', type=int)
        editing_flow = None
        
        if edit_index is not None and 0 <= edit_index < len(config.get('notification_flows', [])):
            editing_flow = config['notification_flows'][edit_index]
        
        if request.method == 'POST':
            try:
                # Validate required fields
                webhook_url = request.form.get('webhook_url', '').strip()
                if not webhook_url:
                    flash('Webhook URL is required', 'error')
                    return redirect(url_for('notification_builder'))
                    
                if not request.form.get('flow_name'):
                    flash('Flow name is required', 'error')
                    return redirect(url_for('notification_builder'))
                
                # Check if embed is enabled
                embed_enabled = request.form.get('embed_enabled') == 'true'
                
                # Allow empty message template if embed is enabled
                if not request.form.get('message_template') and not embed_enabled:
                    flash('Message template is required (or enable Discord embed)', 'error')
                    return redirect(url_for('notification_builder'))
                
                trigger_type = request.form.get('trigger_type', 'on_change')
                accept_webhooks = request.form.get('accept_webhooks', 'false') == 'true'
                require_webhook_secret = request.form.get('require_webhook_secret', 'false') == 'true'
                
                # Validate trigger-specific requirements
                if trigger_type == 'on_change':
                    if not request.form.get('endpoint'):
                        flash('API Endpoint is required for change detection', 'error')
                        return redirect(url_for('notification_builder'))
                    if not request.form.get('field'):
                        flash('Field is required for change detection', 'error')
                        return redirect(url_for('notification_builder'))
                elif trigger_type == 'timer' and not request.form.get('interval'):
                    flash('Interval is required for timer triggers', 'error')
                    return redirect(url_for('notification_builder'))

                # Parse embed configuration
                embed_config = {}
                if request.form.get('embed_enabled') == 'true':
                    embed_config = {
                        'enabled': True,
                        'title': request.form.get('embed_title', ''),
                        'description': request.form.get('embed_description', ''),
                        'url': request.form.get('embed_url', ''),
                        'color': request.form.get('embed_color', ''),
                        'timestamp': request.form.get('embed_timestamp', 'true') == 'true',
                        'footer_text': request.form.get('embed_footer_text', ''),
                        'footer_icon': request.form.get('embed_footer_icon', ''),
                        'author_name': request.form.get('embed_author_name', ''),
                        'author_icon': request.form.get('embed_author_icon', ''),
                        'author_url': request.form.get('embed_author_url', ''),
                        'thumbnail_url': request.form.get('embed_thumbnail_url', ''),
                        'image_url': request.form.get('embed_image_url', ''),
                        'fields': [],
                        'dynamic_fields': []
                    }
                    

                
                # Parse advanced API settings
                api_headers = []
                header_keys = request.form.getlist('header_key[]')
                header_values = request.form.getlist('header_value[]')
                for k, v in zip(header_keys, header_values):
                    if k:
                        api_headers.append({'key': k, 'value': v})
                api_request_body = request.form.get('api_request_body', '')

                updated_flow = {
                    'name': request.form['flow_name'],
                    'trigger_type': trigger_type,
                    'webhook_url': webhook_url,
                    'webhook_name': request.form.get('webhook_name', '').strip(),  # Allow empty
                    'webhook_avatar': request.form.get('webhook_avatar', '').strip(),  # Allow empty
                    'message_template': request.form.get('message_template', ''),
                    'active': request.form.get('active', 'false') == 'true',
                    'endpoint': request.form.get('endpoint', ''),
                    'field': request.form.get('field', ''),
                    'interval': int(request.form.get('interval', 5)) if trigger_type == 'timer' else None,
                    'accept_webhooks': accept_webhooks,
                    'embed_config': embed_config,
                    'category': request.form.get('category', 'General'),
                    'condition_enabled': request.form.get('condition_enabled', 'false') == 'true',
                    'condition': request.form.get('condition', ''),
                    'api_headers': api_headers,
                    'api_request_body': api_request_body,
                }
                
                # Handle webhook_secret logic
                if accept_webhooks and require_webhook_secret:
                    if editing_flow and editing_flow.get('webhook_secret'):
                        updated_flow['webhook_secret'] = editing_flow['webhook_secret']
                    else:
                        updated_flow['webhook_secret'] = secrets.token_urlsafe(16)
                # If not required, remove any existing secret
                elif 'webhook_secret' in updated_flow:
                    del updated_flow['webhook_secret']
                
                # Preserve existing tracking data if editing
                if editing_flow:
                    if 'last_value' in editing_flow:
                        updated_flow['last_value'] = editing_flow['last_value']
                    if 'last_run' in editing_flow:
                        updated_flow['last_run'] = editing_flow['last_run']
                    if 'last_data' in editing_flow:
                        updated_flow['last_data'] = editing_flow['last_data']
                
                # Initialize flows list if it doesn't exist
                if 'notification_flows' not in config:
                    config['notification_flows'] = []
                
                if editing_flow is not None:
                    # Update existing flow
                    config['notification_flows'][edit_index] = updated_flow
                    flash('Notification flow updated successfully!', 'success')
                else:
                    # Add new flow
                    config['notification_flows'].append(updated_flow)
                    flash('Notification flow saved successfully!', 'success')
                    
                save_config(config)
                
            except Exception as e:
                app.logger.error(f"Error saving flow: {str(e)}")
                flash('An error occurred while saving the flow', 'error')
                
            return redirect(url_for('notification_builder'))
        
        # Check if we're using a template
        template_name = request.args.get('template')
        template_data = None
        if template_name:
            template_data = get_template(template_name)
        
        return render_template('builder.html', 
                             webhook_url=config.get('discord_webhook', ''),
                             flows=config.get('notification_flows', []),
                             editing_flow=editing_flow,
                             edit_index=edit_index,
                             config=config,
                             template_data=template_data,
                             template_categories=get_template_categories())

    @app.route('/toggle_flow', methods=['POST'])
    def toggle_flow():
        try:
            data = request.get_json()
            config = get_config()
            
            for flow in config['notification_flows']:
                if flow['name'] == data['flow_name']:
                    flow['active'] = data['active']
                    save_config(config)
                    return jsonify({'success': True})
            
            return jsonify({'success': False, 'error': 'Flow not found'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/delete_flow/<int:index>')
    def delete_flow(index):
        config = get_config()
        if 0 <= index < len(config.get('notification_flows', [])):
            config['notification_flows'].pop(index)
            save_config(config)
            flash('Notification flow deleted', 'success')
        # Redirect to the referring page, or statistics if not available
        return redirect(request.referrer)

    @app.route('/test_flow', methods=['POST'])
    def test_flow():
        try:
            # Parse embed configuration for test
            embed_config = {}
            if request.form.get('embed_enabled') == 'true':
                embed_config = {
                    'enabled': True,
                    'title': request.form.get('embed_title', ''),
                    'description': request.form.get('embed_description', ''),
                    'url': request.form.get('embed_url', ''),
                    'color': request.form.get('embed_color', ''),
                    'timestamp': request.form.get('embed_timestamp', 'true') == 'true',
                    'footer_text': request.form.get('embed_footer_text', ''),
                    'footer_icon': request.form.get('embed_footer_icon', ''),
                    'author_name': request.form.get('embed_author_name', ''),
                    'author_icon': request.form.get('embed_author_icon', ''),
                    'author_url': request.form.get('embed_author_url', ''),
                    'thumbnail_url': request.form.get('embed_thumbnail_url', ''),
                    'image_url': request.form.get('embed_image_url', ''),
                    'fields': [],
                    'dynamic_fields': []
                }
                
                
            
            # Parse advanced API settings
            api_headers = []
            header_keys = request.form.getlist('header_key[]')
            header_values = request.form.getlist('header_value[]')
            for k, v in zip(header_keys, header_values):
                if k:
                    api_headers.append({'key': k, 'value': v})
            api_request_body = request.form.get('api_request_body', '')

            # Create a temporary flow from form data
            test_flow = {
                'name': request.form.get('flow_name', 'test_flow'),
                'trigger_type': request.form.get('trigger_type', 'on_change'),
                'webhook_url': request.form.get('webhook_url', '').strip(),
                'message_template': request.form.get('message_template', ''),
                'active': False,  # Always false for tests
                'endpoint': request.form.get('endpoint', ''),
                'field': request.form.get('field', ''),
                'interval': int(request.form.get('interval', 5)) if request.form.get('trigger_type') == 'timer' else None,
                'accept_webhooks': request.form.get('accept_webhooks', 'false') == 'true',
                'embed_config': embed_config,
                'condition_enabled': request.form.get('condition_enabled', 'false') == 'true',
                'condition': request.form.get('condition', ''),
                'api_headers': api_headers,
                'api_request_body': api_request_body,
            }
            webhook_name = request.form.get('webhook_name', '').strip()
            if webhook_name:
                test_flow['webhook_name'] = webhook_name
            webhook_avatar = request.form.get('webhook_avatar', '').strip()
            if webhook_avatar:
                test_flow['webhook_avatar'] = webhook_avatar

            # Validate required fields
            if not test_flow['webhook_url']:
                return jsonify({'success': False, 'error': 'Webhook URL is required'})
            
            # Allow empty message template if embed is enabled
            if not test_flow['message_template'] and not test_flow.get('embed_config', {}).get('enabled', False):
                return jsonify({'success': False, 'error': 'Message template is required (or enable Discord embed)'})
            
            # Try to get real data from API endpoint if provided
            sample_data = {}
            api_data = None
            
            if test_flow.get('endpoint'):
                try:
                    api_data = make_api_request(
                        test_flow['endpoint'],
                        test_flow.get('api_headers'),
                        test_flow.get('api_request_body')
                    )
                    sample_data = api_data
                    log_notification(f"Test: Successfully fetched data from {test_flow['endpoint']}")
                except Exception as api_error:
                    log_notification(f"Test: Failed to fetch from API endpoint: {str(api_error)}")
                    sample_data = None
            
            else:
                # Fallback to sample data if no API endpoint or API call failed
                if test_flow['trigger_type'] == 'on_change':
                    sample_data = {
                        'value': 'test_value',
                        'old_value': 'old_test_value',
                        'field': test_flow.get('field', 'test_field'),
                        'api_data': {'status': 'active', 'count': 42}
                    }
                elif test_flow['trigger_type'] == 'timer':
                    sample_data = {
                        'value': 'test_value',
                        'api_data': {'status': 'active', 'count': 42}
                    }
                else:  # on_incoming webhook
                    # Use the sample Kapowarr data structure as fallback
                    sample_data = {
                        'error': None,
                        'result': {
                            'downloaded_issues': 299,
                            'files': 299,
                            'issues': 469,
                            'monitored': 29,
                            'total_file_size': 45108577065,
                            'unmonitored': 44,
                            'volumes': 73
                        }
                    }
            
            # Send notification
            log_notification(f"🧪 Test notification: Sending test for flow '{test_flow['name']}'")
            if send_discord_notification(test_flow['message_template'], test_flow, sample_data):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Failed to send Discord notification'})
                
        except Exception as e:
            log_notification(f"Test flow error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/webhook/<flow_name>', methods=['POST'])
    def handle_webhook(flow_name):
        config = get_config()
        
        # Find the flow
        flow = next((f for f in config.get('notification_flows', []) 
                   if f['name'] == flow_name and f['active'] and 
                   (f.get('accept_webhooks') or f['trigger_type'] == 'on_incoming')), None)
        
        if not flow:
            abort(404, description="Flow not found, inactive, or not accepting webhooks")
        
        # Verify secret if present
        if flow.get('webhook_secret'):
            if request.headers.get('X-Secret') != flow['webhook_secret']:
                abort(403, description="Invalid webhook secret")
        
        try:
            data = request.get_json()
            
            # Store the data in the flow for use in message formatting
            flow['last_data'] = data
            
            # Send notification
            log_notification(f"🌐 Webhook received: Processing webhook for flow '{flow_name}'")
            if send_discord_notification(flow['message_template'], flow, data):
                save_config(config)  # Save the updated flow with last_data
                return jsonify({"status": "success"})
            else:
                abort(500, description="Failed to send notification")
                
        except Exception as e:
            log_notification(f"Webhook error for {flow_name}: {str(e)}")
            abort(400, description=str(e))

    # ===== NEW FEATURES ROUTES =====
    
    @app.route('/templates')
    def show_templates():
        """Show available flow templates"""
        category = request.args.get('category')
        templates = get_templates_by_category(category) if category else FLOW_TEMPLATES
        categories = get_template_categories()
        return render_template('templates.html', 
                             templates=templates, 
                             categories=categories,
                             selected_category=category)

    @app.route('/templates/<template_name>')
    def use_template(template_name):
        """Use a template to create a new flow"""
        template = get_template(template_name)
        if not template:
            flash('Template not found', 'error')
            return redirect(url_for('show_templates'))
        
        # Pre-fill the builder form with template data
        return redirect(url_for('notification_builder', template=template_name))

    @app.route('/duplicate_flow/<flow_name>')
    def duplicate_flow_route(flow_name):
        """Duplicate an existing flow"""
        try:
            new_flow_name = duplicate_flow(flow_name)
            if new_flow_name:
                flash(f'Flow "{flow_name}" duplicated as "{new_flow_name}"', 'success')
            else:
                flash('Flow not found', 'error')
        except Exception as e:
            flash(f'Error duplicating flow: {str(e)}', 'error')
        return redirect(url_for('notification_builder'))

    @app.route('/flow_stats')
    def show_flow_stats():
        """Show flow statistics"""
        stats = get_flow_statistics()
        recent_activity = get_recent_flow_activity(24)  # Last 24 hours
        return render_template('flow_stats.html', 
                             stats=stats, 
                             recent_activity=recent_activity)

    @app.route('/export_flows')
    def export_flows():
        """Export all flows to JSON file"""
        try:
            export_data = export_flow_config()
            if not export_data:
                flash('No flows to export', 'error')
                return redirect(url_for('notification_builder'))
            
            # Create file-like object
            file_obj = io.BytesIO()
            file_obj.write(json.dumps(export_data, indent=2).encode('utf-8'))
            file_obj.seek(0)
            
            return send_file(
                file_obj,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'notification_flows_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        except Exception as e:
            flash(f'Error exporting flows: {str(e)}', 'error')
            return redirect(url_for('notification_builder'))

    @app.route('/export_flow/<flow_name>')
    def export_single_flow(flow_name):
        """Export a single flow to JSON file"""
        try:
            export_data = export_flow_config(flow_name)
            if not export_data:
                flash('Flow not found', 'error')
                return redirect(url_for('notification_builder'))
            
            file_obj = io.BytesIO()
            file_obj.write(json.dumps(export_data, indent=2).encode('utf-8'))
            file_obj.seek(0)
            
            return send_file(
                file_obj,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'{flow_name}_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        except Exception as e:
            flash(f'Error exporting flow: {str(e)}', 'error')
            return redirect(url_for('notification_builder'))

    @app.route('/import_flows', methods=['POST'])
    def import_flows():
        """Import flows from JSON file"""
        try:
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(url_for('notification_builder'))
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('notification_builder'))
            
            if not file.filename or not file.filename.endswith('.json'):
                flash('Please select a JSON file', 'error')
                return redirect(url_for('notification_builder'))
            
            # Read and parse the file
            import_data = json.loads(file.read().decode('utf-8'))
            
            # Import the flows
            imported_names = import_flow_config(import_data)
            
            if imported_names:
                if isinstance(imported_names, list):
                    flash(f'Successfully imported {len(imported_names)} flows', 'success')
                else:
                    flash(f'Successfully imported flow: {imported_names}', 'success')
            else:
                flash('No flows were imported', 'error')
                
        except json.JSONDecodeError:
            flash('Invalid JSON file', 'error')
        except Exception as e:
            flash(f'Error importing flows: {str(e)}', 'error')
        
        return redirect(url_for('notification_builder'))

    @app.route('/preview_notification', methods=['POST'])
    def preview_notification():
        """Preview how a notification will look"""
        try:
            # Get form data
            message_template = request.form.get('message_template', '')
            embed_enabled = request.form.get('embed_enabled') == 'true'
            trigger_type = request.form.get('trigger_type', 'on_change')
            endpoint = request.form.get('endpoint', '')
            field = request.form.get('field', '')
            
            # Try to get real data from API endpoint if provided
            sample_data = {}
            api_data = None
            
            if endpoint:
                try:
                    api_headers = []
                    header_keys = request.form.getlist('header_key[]')
                    header_values = request.form.getlist('header_value[]')
                    for k, v in zip(header_keys, header_values):
                        if k:
                            api_headers.append({'key': k, 'value': v})
                    api_request_body = request.form.get('api_request_body', '')
                    api_data = make_api_request(
                        endpoint,
                        api_headers,
                        api_request_body
                    )
                    sample_data = api_data
                    log_notification(f"Preview: Successfully fetched data from {endpoint}")
                except Exception as api_error:
                    log_notification(f"Preview: Failed to fetch from API endpoint: {str(api_error)}")
                    sample_data = None
            
            # Fallback to sample data if no API endpoint or API call failed
            if not sample_data:
                if trigger_type == 'on_change':
                    sample_data = {
                        'value': 'preview_value',
                        'old_value': 'old_preview_value',
                        'field': field or 'test_field',
                        'api_data': {'status': 'active', 'count': 42}
                    }
                elif trigger_type == 'timer':
                    sample_data = {
                        'value': 'preview_value',
                        'api_data': {'status': 'active', 'count': 42}
                    }
                else:  # on_incoming webhook
                    sample_data = {
                        'error': None,
                        'result': {
                            'downloaded_issues': 299,
                            'files': 299,
                            'issues': 469,
                            'monitored': 29,
                            'total_file_size': 45108577065,
                            'unmonitored': 44,
                            'volumes': 73
                        }
                    }
            
            # Parse advanced API settings
            api_headers = []
            header_keys = request.form.getlist('header_key[]')
            header_values = request.form.getlist('header_value[]')
            for k, v in zip(header_keys, header_values):
                if k:
                    api_headers.append({'key': k, 'value': v})
            api_request_body = request.form.get('api_request_body', '')

            # Format the message
            formatted_message = format_message_template(message_template, sample_data)
            
            # Create embed preview if enabled
            embed_preview = None
            if embed_enabled:
                embed_config = {
                    'enabled': True,
                    'title': request.form.get('embed_title', ''),
                    'description': request.form.get('embed_description', ''),
                    'url': request.form.get('embed_url', ''),
                    'color': request.form.get('embed_color', '#3498db'),
                    'timestamp': request.form.get('embed_timestamp', 'true') == 'true',
                    'footer_text': request.form.get('embed_footer_text', ''),
                    'footer_icon': request.form.get('embed_footer_icon', ''),
                    'author_name': request.form.get('embed_author_name', ''),
                    'author_icon': request.form.get('embed_author_icon', ''),
                    'author_url': request.form.get('embed_author_url', ''),
                    'thumbnail_url': request.form.get('embed_thumbnail_url', ''),
                    'image_url': request.form.get('embed_image_url', ''),
                    'fields': [],
                    'dynamic_fields': []
                }
                
                embed_preview = create_discord_embed(embed_config, sample_data)
            
            return jsonify({
                'success': True,
                'message': formatted_message,
                'embed': embed_preview,
                'sample_data': sample_data
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generating preview: {str(e)}'
            })

    @app.route('/search_flows')
    def search_flows():
        """Search flows by name, type, or category"""
        query = request.args.get('q', '').lower()
        category = request.args.get('category', '')
        trigger_type = request.args.get('trigger_type', '')
        
        config = get_config()
        flows = config.get('notification_flows', [])
        
        # Filter flows
        filtered_flows = []
        for flow in flows:
            # Search by name
            if query and query not in flow['name'].lower():
                continue
            
            # Filter by category
            if category and flow.get('category', 'General') != category:
                continue
            
            # Filter by trigger type
            if trigger_type and flow['trigger_type'] != trigger_type:
                continue
            
            filtered_flows.append(flow)
        
        return jsonify({
            'flows': filtered_flows,
            'count': len(filtered_flows)
        })

    @app.route('/api/docs')
    def api_documentation():
        """Show API documentation page"""
        return render_template('api_docs.html')