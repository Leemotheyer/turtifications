---
layout: default
title: API Usage Guide
parent: Guides
nav_order: 3
---

# API Usage Guide
{: .no_toc }

Learn how to integrate with Turtifications using the REST API for automation and external integrations.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Introduction

The Turtifications API provides programmatic access to:
- Monitor application status and health
- Retrieve flow information and statistics
- Send test notifications
- Manage webhook endpoints
- Access logs and analytics

This guide provides practical examples for common integration scenarios.

---

## Quick Start

### Basic Status Check

```bash
# Check if Turtifications is running
curl http://localhost:5000/api/status

# Expected response:
{
  "status": "running",
  "timestamp": "2024-01-15T14:30:00.000Z", 
  "total_flows": 5,
  "active_flows": 3,
  "version": "1.0.0"
}
```

### Send a Test Notification

```bash
curl -X POST http://localhost:5000/api/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from API!",
    "embed": {
      "title": "Test Notification",
      "description": "This is a test from the API",
      "color": "#00ff00"
    }
  }'
```

---

## Common Integration Patterns

### 1. Monitoring Dashboard Integration

Create a monitoring dashboard that displays Turtifications metrics:

```python
import requests
import json
from datetime import datetime

class TurtificationsMonitor:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def get_status(self):
        """Get application status"""
        response = requests.get(f"{self.base_url}/api/status")
        return response.json()
    
    def get_statistics(self):
        """Get detailed statistics"""
        response = requests.get(f"{self.base_url}/api/statistics")
        return response.json()
    
    def get_active_flows(self):
        """Get currently active flows"""
        response = requests.get(f"{self.base_url}/api/flows/active")
        return response.json()
    
    def check_health(self):
        """Perform health check"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False

# Usage example
monitor = TurtificationsMonitor()

# Get current status
status = monitor.get_status()
print(f"Status: {status['status']}")
print(f"Active flows: {status['active_flows']}/{status['total_flows']}")

# Check health
if monitor.check_health():
    print("✅ Application is healthy")
else:
    print("❌ Application health check failed")

# Get statistics
stats = monitor.get_statistics()
print(f"Total notifications sent: {stats['notifications']['total_sent']}")
```

### 2. External Service Integration

Trigger notifications from external applications:

```python
import requests
import json

def send_deployment_notification(app_name, version, status, environment):
    """Send deployment notification via Turtifications"""
    
    webhook_url = "http://localhost:5000/api/webhook/deployments"
    
    payload = {
        "app_name": app_name,
        "version": version,
        "status": status,
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat(),
        "deployed_by": "CI/CD Pipeline"
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Deployment notification sent for {app_name} v{version}")
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")

# Usage in deployment script
send_deployment_notification(
    app_name="my-web-app",
    version="1.2.3",
    status="success",
    environment="production"
)
```

### 3. Log Analysis and Alerting

Monitor logs and send alerts based on patterns:

```python
import requests
import re
from collections import Counter

def analyze_logs_and_alert():
    """Analyze recent logs and send alerts if needed"""
    
    # Get recent logs
    response = requests.get("http://localhost:5000/api/logs?limit=1000")
    logs = response.json()
    
    # Analyze error patterns
    error_logs = [log for log in logs['logs'] if log['level'] == 'error']
    warning_logs = [log for log in logs['logs'] if log['level'] == 'warning']
    
    # Count errors by flow
    error_by_flow = Counter()
    for log in error_logs:
        if 'flow_name' in log:
            error_by_flow[log['flow_name']] += 1
    
    # Send alert if too many errors
    if len(error_logs) > 10:  # More than 10 errors
        alert_data = {
            "message": f"🚨 High error rate detected: {len(error_logs)} errors in recent logs",
            "embed": {
                "title": "Error Rate Alert",
                "description": f"Found {len(error_logs)} errors and {len(warning_logs)} warnings",
                "color": "#ff0000",
                "fields": [
                    {
                        "name": "Top Error Sources",
                        "value": "\n".join([f"{flow}: {count}" for flow, count in error_by_flow.most_common(5)]),
                        "inline": False
                    }
                ]
            }
        }
        
        # Send alert
        requests.post(
            "http://localhost:5000/api/test",
            headers={"Content-Type": "application/json"},
            json=alert_data
        )

# Run analysis
analyze_logs_and_alert()
```

### 4. Flow Management Automation

Automatically manage flows based on external conditions:

```python
import requests
import json

class FlowManager:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_flows(self):
        """Get all flows"""
        response = requests.get(f"{self.base_url}/api/flows")
        return response.json()['flows']
    
    def get_flow_statistics(self):
        """Get flow performance statistics"""
        response = requests.get(f"{self.base_url}/api/statistics")
        return response.json()
    
    def disable_failing_flows(self, failure_threshold=80):
        """Disable flows with high failure rates"""
        stats = self.get_flow_statistics()
        
        for flow_stat in stats.get('statistics', []):
            success_rate = flow_stat.get('success_rate', 100)
            flow_name = flow_stat.get('name')
            
            if success_rate < failure_threshold:
                print(f"⚠️ Flow '{flow_name}' has {success_rate:.1f}% success rate")
                # In a real implementation, you would call an API to disable the flow
                # This would require additional API endpoints for flow management
    
    def generate_health_report(self):
        """Generate a comprehensive health report"""
        flows = self.get_flows()
        stats = self.get_flow_statistics()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_flows": len(flows),
            "active_flows": len([f for f in flows if f.get('active', False)]),
            "overall_health": "healthy"
        }
        
        # Calculate overall health
        if stats.get('flows', {}).get('active', 0) == 0:
            report["overall_health"] = "no_active_flows"
        elif len([f for f in flows if f.get('active')]) < len(flows) * 0.5:
            report["overall_health"] = "degraded"
            
        return report

# Usage
manager = FlowManager()
report = manager.generate_health_report()
print(f"System health: {report['overall_health']}")
print(f"Active flows: {report['active_flows']}/{report['total_flows']}")
```

---

## Integration Examples

### GitHub Actions Integration

Use Turtifications in GitHub Actions workflows:

```yaml
# .github/workflows/deploy.yml
name: Deploy and Notify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Application
        run: |
          # Your deployment steps here
          echo "Deploying..."
          
      - name: Notify via Turtifications
        if: always()
        run: |
          curl -X POST ${{ secrets.TURTIFICATIONS_WEBHOOK_URL }} \
            -H "Content-Type: application/json" \
            -d '{
              "repository": "${{ github.repository }}",
              "commit": "${{ github.sha }}",
              "branch": "${{ github.ref_name }}",
              "status": "${{ job.status }}",
              "actor": "${{ github.actor }}",
              "workflow": "${{ github.workflow }}"
            }'
```

### Docker Health Check Integration

Monitor Docker containers and send notifications:

```python
import docker
import requests
import json

def check_docker_containers():
    """Check Docker container status and notify if issues"""
    client = docker.from_env()
    
    containers = client.containers.list(all=True)
    unhealthy_containers = []
    
    for container in containers:
        if container.status != 'running':
            unhealthy_containers.append({
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown"
            })
    
    if unhealthy_containers:
        notification = {
            "message": f"🐳 Docker containers need attention: {len(unhealthy_containers)} containers not running",
            "embed": {
                "title": "Docker Container Alert",
                "color": "#ff6600",
                "fields": [
                    {
                        "name": container["name"],
                        "value": f"Status: {container['status']}\nImage: {container['image']}",
                        "inline": True
                    }
                    for container in unhealthy_containers[:10]  # Limit to 10
                ]
            }
        }
        
        # Send to webhook
        requests.post(
            "http://localhost:5000/api/webhook/docker-monitor",
            headers={"Content-Type": "application/json"},
            json=notification
        )

# Run check
check_docker_containers()
```

### Prometheus Metrics Integration

Export Turtifications metrics to Prometheus:

```python
import requests
import time
from prometheus_client import Gauge, Counter, start_http_server

# Define metrics
turtifications_flows_total = Gauge('turtifications_flows_total', 'Total number of flows')
turtifications_flows_active = Gauge('turtifications_flows_active', 'Number of active flows')
turtifications_notifications_sent_total = Counter('turtifications_notifications_sent_total', 'Total notifications sent')
turtifications_flow_success_rate = Gauge('turtifications_flow_success_rate', 'Flow success rate', ['flow_name'])

def collect_metrics():
    """Collect metrics from Turtifications API"""
    try:
        # Get status
        status_response = requests.get("http://localhost:5000/api/status")
        status = status_response.json()
        
        turtifications_flows_total.set(status['total_flows'])
        turtifications_flows_active.set(status['active_flows'])
        
        # Get statistics
        stats_response = requests.get("http://localhost:5000/api/statistics")
        stats = stats_response.json()
        
        # Update flow-specific metrics
        for flow_stat in stats.get('statistics', []):
            flow_name = flow_stat.get('name', 'unknown')
            success_rate = flow_stat.get('success_rate', 0)
            turtifications_flow_success_rate.labels(flow_name=flow_name).set(success_rate)
            
        print(f"✅ Metrics updated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error collecting metrics: {e}")

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)
    print("📊 Prometheus metrics server started on port 8000")
    
    # Collect metrics every 30 seconds
    while True:
        collect_metrics()
        time.sleep(30)
```

---

## Advanced API Usage

### Batch Operations

Perform multiple operations efficiently:

```python
import asyncio
import aiohttp
import json

async def batch_webhook_test():
    """Test multiple webhook endpoints concurrently"""
    
    webhook_endpoints = [
        "github-webhook",
        "docker-monitor", 
        "deployment-alerts",
        "system-monitor"
    ]
    
    test_payload = {
        "test": True,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Batch test from API"
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for endpoint in webhook_endpoints:
            url = f"http://localhost:5000/api/webhook/{endpoint}"
            task = send_webhook_async(session, url, test_payload)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            endpoint = webhook_endpoints[i]
            if isinstance(result, Exception):
                print(f"❌ {endpoint}: {result}")
            else:
                print(f"✅ {endpoint}: {result.status}")

async def send_webhook_async(session, url, payload):
    """Send webhook request asynchronously"""
    async with session.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    ) as response:
        return response

# Run batch test
asyncio.run(batch_webhook_test())
```

### API Response Caching

Cache API responses to reduce load:

```python
import requests
import time
import json
from functools import wraps

def cache_response(ttl_seconds=300):
    """Decorator to cache API responses"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
            
        return wrapper
    return decorator

class CachedTurtificationsAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    @cache_response(ttl_seconds=60)  # Cache for 1 minute
    def get_status(self):
        response = requests.get(f"{self.base_url}/api/status")
        return response.json()
    
    @cache_response(ttl_seconds=300)  # Cache for 5 minutes
    def get_statistics(self):
        response = requests.get(f"{self.base_url}/api/statistics")
        return response.json()
    
    @cache_response(ttl_seconds=30)  # Cache for 30 seconds
    def get_flows(self):
        response = requests.get(f"{self.base_url}/api/flows")
        return response.json()

# Usage
api = CachedTurtificationsAPI()

# First call hits the API
status1 = api.get_status()

# Second call uses cache
status2 = api.get_status()
```

---

## Error Handling and Retries

### Robust API Client

Create a production-ready API client with proper error handling:

```python
import requests
import time
import logging
from typing import Optional, Dict, Any

class TurtificationsAPIClient:
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retries and error handling"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt == self.max_retries:
                    raise
                    
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Connection error on attempt {attempt + 1} for {url}")
                if attempt == self.max_retries:
                    raise
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500:
                    # Retry on server errors
                    self.logger.warning(f"Server error {e.response.status_code} on attempt {attempt + 1}")
                    if attempt == self.max_retries:
                        raise
                else:
                    # Don't retry on client errors
                    raise
            
            # Exponential backoff
            if attempt < self.max_retries:
                time.sleep(2 ** attempt)
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status"""
        response = self._make_request('GET', '/api/status')
        return response.json()
    
    def send_test_notification(self, message: str, embed: Optional[Dict] = None) -> bool:
        """Send test notification"""
        payload = {"message": message}
        if embed:
            payload["embed"] = embed
            
        try:
            self._make_request(
                'POST', '/api/test',
                headers={'Content-Type': 'application/json'},
                json=payload
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to send test notification: {e}")
            return False
    
    def send_webhook(self, flow_name: str, data: Dict[str, Any]) -> bool:
        """Send data to webhook endpoint"""
        try:
            self._make_request(
                'POST', f'/api/webhook/{flow_name}',
                headers={'Content-Type': 'application/json'},
                json=data
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to send webhook to {flow_name}: {e}")
            return False

# Usage
client = TurtificationsAPIClient("http://localhost:5000")

# These calls will automatically retry on failure
status = client.get_status()
success = client.send_test_notification("Hello from robust client!")
```

---

## Security Considerations

### API Key Authentication

If implementing API key authentication:

```python
class SecureTurtificationsClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'User-Agent': 'TurtificationsClient/1.0'
        })
    
    def make_authenticated_request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

# Usage
client = SecureTurtificationsClient(
    "https://your-domain.com",
    api_key="your-secret-api-key"
)
```

### Webhook Signature Validation

Validate webhook signatures for security:

```python
import hmac
import hashlib

def validate_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Validate webhook signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected_signature}")

# Usage in webhook handler
def handle_webhook(request):
    signature = request.headers.get('X-Hub-Signature-256')
    if not validate_webhook_signature(request.body, signature, WEBHOOK_SECRET):
        return {"error": "Invalid signature"}, 401
        
    # Process webhook data
    data = request.json()
    # ... handle webhook
```

---

## Next Steps

- Explore the complete [API Reference](../api/reference) for all available endpoints
- Learn about [Configuration](../configuration) for production API deployments  
- Check out [Troubleshooting](../troubleshooting) for API-related issues
- Review [notification flow examples](notification-flows) for webhook integration patterns