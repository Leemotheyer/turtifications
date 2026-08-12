"""
API endpoints for the notification organizer app
"""

from flask import jsonify, request
from datetime import datetime, timedelta
from functions.config import get_config, save_config, get_logs, get_log_stats
from functions.flow_stats import get_flow_statistics, get_recent_flow_activity
from functions.notifications import send_discord_notification
from functions.utils import get_notification_logs
from functions.version import get_version, get_version_info
from functions.auth import require_api_key
from functions.form_parsers import build_flow_from_json
from functions.embed_utils import validate_embed_config
import json


def _sanitize_flow(flow):
    """Return a copy of a flow without sensitive fields."""
    safe_flow = flow.copy()
    safe_flow.pop('webhook_url', None)
    safe_flow.pop('webhook_secret', None)
    return safe_flow


def _find_flow_index(flows, flow_name):
    for index, flow in enumerate(flows):
        if flow.get('name') == flow_name:
            return index
    return None


def init_api_routes(app):
    """Initialize API routes"""
    
    @app.route('/api/status')
    def api_status():
        """Get overall app status"""
        config = get_config()
        flows = config.get('notification_flows', [])
        active_flows = [flow for flow in flows if flow.get('active', False)]
        
        return jsonify({
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'total_flows': len(flows),
            'active_flows': len(active_flows),
            'version': get_version()
        })
    
    @app.route('/api/flows')
    def api_flows():
        """Get all notification flows"""
        config = get_config()
        flows = config.get('notification_flows', [])
        safe_flows = [_sanitize_flow(flow) for flow in flows]
        
        return jsonify({
            'flows': safe_flows,
            'count': len(safe_flows)
        })
    
    @app.route('/api/flows', methods=['POST'])
    @require_api_key
    def api_create_flow():
        """Create a new notification flow"""
        try:
            data = request.get_json(force=True, silent=False)
            if not data:
                return jsonify({'error': 'JSON body required'}), 400

            flow = build_flow_from_json(data)
            embed_config = flow.get('embed_config', {})
            if embed_config.get('enabled'):
                errors = validate_embed_config(embed_config)
                if errors:
                    return jsonify({'error': '; '.join(errors)}), 400

            config = get_config()
            flows = config.setdefault('notification_flows', [])

            if _find_flow_index(flows, flow['name']) is not None:
                return jsonify({'error': 'Flow already exists'}), 409

            flows.append(flow)
            save_config(config)
            return jsonify({'success': True, 'flow': _sanitize_flow(flow)}), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/flows/<flow_name>', methods=['PUT'])
    @require_api_key
    def api_update_flow(flow_name):
        """Update an existing notification flow"""
        try:
            data = request.get_json(force=True, silent=False)
            if not data:
                return jsonify({'error': 'JSON body required'}), 400

            config = get_config()
            flows = config.get('notification_flows', [])
            index = _find_flow_index(flows, flow_name)
            if index is None:
                return jsonify({'error': 'Flow not found'}), 404

            if data.get('name') and data['name'] != flow_name:
                if _find_flow_index(flows, data['name']) is not None:
                    return jsonify({'error': 'Target flow name already exists'}), 409

            flow = build_flow_from_json(data, existing_flow=flows[index])
            embed_config = flow.get('embed_config', {})
            if embed_config.get('enabled'):
                errors = validate_embed_config(embed_config)
                if errors:
                    return jsonify({'error': '; '.join(errors)}), 400

            flows[index] = flow
            save_config(config)
            return jsonify({'success': True, 'flow': _sanitize_flow(flow)})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/flows/<flow_name>', methods=['DELETE'])
    @require_api_key
    def api_delete_flow(flow_name):
        """Delete a notification flow"""
        config = get_config()
        flows = config.get('notification_flows', [])
        index = _find_flow_index(flows, flow_name)
        if index is None:
            return jsonify({'error': 'Flow not found'}), 404

        removed = flows.pop(index)
        save_config(config)
        return jsonify({'success': True, 'deleted': _sanitize_flow(removed)})

    @app.route('/api/flows/<flow_name>/toggle', methods=['POST'])
    @require_api_key
    def api_toggle_flow(flow_name):
        """Enable or disable a notification flow"""
        data = request.get_json(silent=True) or {}
        active = data.get('active')
        if active is None:
            return jsonify({'error': 'active (boolean) is required'}), 400

        config = get_config()
        flows = config.get('notification_flows', [])
        index = _find_flow_index(flows, flow_name)
        if index is None:
            return jsonify({'error': 'Flow not found'}), 404

        flows[index]['active'] = bool(active)
        save_config(config)
        return jsonify({'success': True, 'flow': _sanitize_flow(flows[index])})
    
    @app.route('/api/flows/active')
    def api_active_flows():
        """Get only active notification flows"""
        config = get_config()
        flows = config.get('notification_flows', [])
        active_flows = [flow for flow in flows if flow.get('active', False)]
        safe_flows = [_sanitize_flow(flow) for flow in active_flows]
        
        return jsonify({
            'flows': safe_flows,
            'count': len(safe_flows)
        })
    
    @app.route('/api/flows/<flow_name>')
    def api_flow_details(flow_name):
        """Get details for a specific flow"""
        config = get_config()
        flows = config.get('notification_flows', [])
        
        flow = next((f for f in flows if f['name'] == flow_name), None)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        return jsonify(_sanitize_flow(flow))
    
    @app.route('/api/statistics')
    def api_statistics():
        """Get comprehensive app statistics"""
        config = get_config()
        flows = config.get('notification_flows', [])
        logs = get_logs()
        
        active_flows = [flow for flow in flows if flow.get('active', False)]
        timer_flows = [flow for flow in flows if flow.get('trigger_type') == 'timer']
        change_flows = [flow for flow in flows if flow.get('trigger_type') == 'on_change']
        webhook_flows = [flow for flow in flows if flow.get('trigger_type') in ('webhook', 'on_incoming')]
        
        flow_stats = get_flow_statistics()
        recent_activity = get_recent_flow_activity(24)
        
        total_logs = len(logs)
        recent_logs = len([log for log in logs if 
                          datetime.now() - datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S') < timedelta(hours=24)])
        
        notification_logs = get_notification_logs()
        total_notifications_in_log = len(notification_logs)
        total_notifications_sent = config.get('total_notifications_sent', 0)
        
        now = datetime.now()
        notifications_24h = 0
        for notification in notification_logs:
            try:
                notification_time = datetime.strptime(notification['timestamp'], '%Y-%m-%d %H:%M:%S')
                if now - notification_time < timedelta(hours=24):
                    notifications_24h += 1
            except (ValueError, KeyError):
                continue
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'flows': {
                'total': len(flows),
                'active': len(active_flows),
                'inactive': len(flows) - len(active_flows),
                'by_type': {
                    'scheduled': len(timer_flows),
                    'change_detection': len(change_flows),
                    'webhook': len(webhook_flows)
                }
            },
            'statistics': flow_stats,
            'recent_activity': recent_activity,
            'logs': {
                'total': total_logs,
                'last_24h': recent_logs
            },
            'notifications': {
                'total_sent': total_notifications_sent,
                'total_in_current_log': total_notifications_in_log,
                'last_24h': notifications_24h
            }
        })
    
    @app.route('/api/logs')
    def api_logs():
        """Get recent logs"""
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 1000)
        
        logs = get_logs()
        recent_logs = list(reversed(logs))[:limit]
        
        return jsonify({
            'logs': recent_logs,
            'count': len(recent_logs),
            'total_logs': len(logs)
        })
    
    @app.route('/api/logs/stats')
    def api_log_stats():
        """Get log statistics"""
        stats = get_log_stats()
        return jsonify(stats)
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        config = get_config()
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'config_loaded': bool(config),
                'discord_webhook_configured': bool(config.get('discord_webhook')),
                'flows_accessible': 'notification_flows' in config
            }
        }
        
        if not config.get('discord_webhook'):
            health_status['status'] = 'warning'
            health_status['message'] = 'Discord webhook not configured'
        
        return jsonify(health_status)
    
    @app.route('/api/test', methods=['POST'])
    @require_api_key
    def api_test_notification():
        """Send a test notification via API"""
        try:
            data = request.get_json(force=True, silent=False, cache=False)
            
            if not data:
                return jsonify({'error': 'No JSON data provided or invalid JSON format'}), 400
            
            import sys
            data_size = sys.getsizeof(str(data))
            max_size = 1024 * 512
            if data_size > max_size:
                return jsonify({'error': f'Request data too large ({data_size} bytes, max {max_size})'}), 413
            
            message = data.get('message', 'Test notification from API')
            if not isinstance(message, str):
                return jsonify({'error': 'Message must be a string'}), 400
            
            if len(message) > 2000:
                return jsonify({'error': 'Message too long (max 2000 characters)'}), 400
            
            webhook_url = data.get('webhook_url')
            
            if not webhook_url:
                config = get_config()
                webhook_url = config.get('discord_webhook')
                if not webhook_url:
                    return jsonify({'error': 'No webhook URL provided and no default configured'}), 400
            
            if not isinstance(webhook_url, str) or not webhook_url.startswith('https://'):
                return jsonify({'error': 'Invalid webhook URL format'}), 400
            
            test_flow = {
                'webhook_url': webhook_url,
                'webhook_name': data.get('webhook_name', ''),
                'webhook_avatar': data.get('webhook_avatar', ''),
                'message_template': message,
                'embed_config': data.get('embed_config', {}),
            }
            
            if send_discord_notification(message, test_flow):
                return jsonify({
                    'success': True,
                    'message': 'Test notification sent successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send notification'
                }), 500
                
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON format'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error sending test notification: {str(e)}'
            }), 500
    
    @app.route('/api/endpoints')
    def api_endpoints():
        """List all available API endpoints"""
        return jsonify({
            'endpoints': {
                'GET /api/status': 'Get overall app status',
                'GET /api/flows': 'Get all notification flows',
                'POST /api/flows': 'Create a notification flow (API key if configured)',
                'PUT /api/flows/<name>': 'Update a notification flow (API key if configured)',
                'DELETE /api/flows/<name>': 'Delete a notification flow (API key if configured)',
                'POST /api/flows/<name>/toggle': 'Enable/disable a flow (API key if configured)',
                'GET /api/flows/active': 'Get only active flows',
                'GET /api/flows/<name>': 'Get specific flow details',
                'GET /api/statistics': 'Get comprehensive statistics',
                'GET /api/logs': 'Get recent logs (optional: ?limit=50)',
                'GET /api/logs/stats': 'Get log statistics',
                'GET /api/health': 'Health check endpoint',
                'POST /api/test': 'Send test notification (API key if configured)',
                'POST /api/webhook/<flow_name>': 'Webhook endpoint for flows'
            },
            'auth': 'Set API_KEY environment variable to require X-API-Key header on mutating endpoints',
            'timestamp': datetime.now().isoformat()
        })
