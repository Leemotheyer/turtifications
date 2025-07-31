"""
API endpoints for the notification organizer app
"""

from flask import jsonify, request
from datetime import datetime, timedelta
from functions.config import get_config, get_logs, get_log_stats
from functions.flow_stats import get_flow_statistics, get_recent_flow_activity
from functions.notifications import send_discord_notification
from functions.utils import get_notification_logs
import json

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
            'version': '1.0.0'
        })
    
    @app.route('/api/flows')
    def api_flows():
        """Get all notification flows"""
        config = get_config()
        flows = config.get('notification_flows', [])
        
        # Clean up sensitive data
        safe_flows = []
        for flow in flows:
            safe_flow = flow.copy()
            # Remove webhook URLs for security
            safe_flow.pop('webhook_url', None)
            safe_flow.pop('webhook_secret', None)
            safe_flows.append(safe_flow)
        
        return jsonify({
            'flows': safe_flows,
            'count': len(safe_flows)
        })
    
    @app.route('/api/flows/active')
    def api_active_flows():
        """Get only active notification flows"""
        config = get_config()
        flows = config.get('notification_flows', [])
        active_flows = [flow for flow in flows if flow.get('active', False)]
        
        # Clean up sensitive data
        safe_flows = []
        for flow in active_flows:
            safe_flow = flow.copy()
            safe_flow.pop('webhook_url', None)
            safe_flow.pop('webhook_secret', None)
            safe_flows.append(safe_flow)
        
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
        
        # Clean up sensitive data
        safe_flow = flow.copy()
        safe_flow.pop('webhook_url', None)
        safe_flow.pop('webhook_secret', None)
        
        return jsonify(safe_flow)
    
    @app.route('/api/statistics')
    def api_statistics():
        """Get comprehensive app statistics"""
        config = get_config()
        flows = config.get('notification_flows', [])
        logs = get_logs()
        
        # Basic flow statistics
        active_flows = [flow for flow in flows if flow.get('active', False)]
        timer_flows = [flow for flow in flows if flow.get('trigger_type') == 'timer']
        change_flows = [flow for flow in flows if flow.get('trigger_type') == 'on_change']
        webhook_flows = [flow for flow in flows if flow.get('trigger_type') == 'on_incoming']
        
        # Get detailed flow statistics
        flow_stats = get_flow_statistics()
        
        # Recent activity (last 24 hours)
        recent_activity = get_recent_flow_activity(24)
        
        # Log statistics
        total_logs = len(logs)
        recent_logs = len([log for log in logs if 
                          datetime.now() - datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S') < timedelta(hours=24)])
        
        # Notification statistics
        notification_logs = get_notification_logs()
        total_notifications_in_log = len(notification_logs)
        total_notifications_sent = config.get('total_notifications_sent', 0)
        
        # Calculate notifications in last 24 hours
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
                    'timer': len(timer_flows),
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
        limit = min(limit, 1000)  # Cap at 1000 logs
        
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
        
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'config_loaded': bool(config),
                'discord_webhook_configured': bool(config.get('discord_webhook')),
                'flows_accessible': 'notification_flows' in config
            }
        }
        
        # Check if any critical issues
        if not config.get('discord_webhook'):
            health_status['status'] = 'warning'
            health_status['message'] = 'Discord webhook not configured'
        
        return jsonify(health_status)
    
    @app.route('/api/test', methods=['POST'])
    def api_test_notification():
        """Send a test notification via API"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            message = data.get('message', 'Test notification from API')
            webhook_url = data.get('webhook_url')
            
            if not webhook_url:
                # Use default webhook from config
                config = get_config()
                webhook_url = config.get('discord_webhook')
                if not webhook_url:
                    return jsonify({'error': 'No webhook URL provided and no default configured'}), 400
            
            # Create a simple test flow
            test_flow = {
                'webhook_url': webhook_url,
                'webhook_name': data.get('webhook_name', ''),
                'webhook_avatar': data.get('webhook_avatar', ''),
                'message_template': message
            }
            
            # Send notification
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
                'GET /api/flows/active': 'Get only active flows',
                'GET /api/flows/<name>': 'Get specific flow details',
                'GET /api/statistics': 'Get comprehensive statistics',
                'GET /api/logs': 'Get recent logs (optional: ?limit=50)',
                'GET /api/logs/stats': 'Get log statistics',
                'GET /api/health': 'Health check endpoint',
                'POST /api/test': 'Send test notification',
                'POST /api/webhook/<flow_name>': 'Webhook endpoint for flows'
            },
            'timestamp': datetime.now().isoformat()
        }) 