---
layout: default
title: API Reference
parent: API
nav_order: 1
---

# API Reference
{: .no_toc }

Complete reference for the Turtifications REST API with examples and response formats.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Base URL

All API requests should be made to:
```
http://localhost:5000/api
```

Replace `localhost:5000` with your actual server address and port.

---

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing authentication through a reverse proxy or custom middleware.

---

## Common Headers

```http
Content-Type: application/json
User-Agent: YourApp/1.0
```

---

## Status Endpoints

### Get Application Status

Get overall application status and basic statistics.

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "status": "running",
  "timestamp": "2024-01-15T14:30:00.000Z",
  "total_flows": 5,
  "active_flows": 3,
  "version": "1.0.0"
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/status
```

### Health Check

Simple health check endpoint for monitoring.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00.000Z",
  "uptime": 86400
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/health
```

---

## Flow Management

### Get All Flows

Retrieve all notification flows (sensitive data removed).

**Endpoint:** `GET /api/flows`

**Response:**
```json
{
  "flows": [
    {
      "name": "GitHub Monitor",
      "trigger_type": "timer",
      "active": true,
      "url": "https://api.github.com/repos/octocat/Hello-World",
      "check_interval": 3600,
      "message_template": "Repository updated: {result['updated_at']}",
      "embed_config": {
        "enabled": true,
        "title": "GitHub Update",
        "color": "#0066cc"
      }
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/flows
```

### Get Active Flows

Retrieve only currently active flows.

**Endpoint:** `GET /api/flows/active`

**Response:**
```json
{
  "active_flows": [
    {
      "name": "System Monitor",
      "trigger_type": "timer",
      "url": "https://api.example.com/stats",
      "check_interval": 300,
      "last_check": "2024-01-15T14:25:00.000Z",
      "status": "running"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/flows/active
```

### Get Specific Flow

Retrieve details for a specific flow by name.

**Endpoint:** `GET /api/flows/{flow_name}`

**Response:**
```json
{
  "flow": {
    "name": "Website Monitor",
    "trigger_type": "timer",
    "active": true,
    "url": "https://httpstat.us/200",
    "check_interval": 600,
    "timeout": 30,
    "message_template": "Status: {result['status']}",
    "last_execution": "2024-01-15T14:20:00.000Z",
    "execution_count": 42,
    "success_rate": 98.5
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/flows/website-monitor
```

---

## Statistics & Monitoring

### Get Statistics

Retrieve comprehensive application statistics.

**Endpoint:** `GET /api/statistics`

**Response:**
```json
{
  "overview": {
    "total_flows": 5,
    "active_flows": 3,
    "total_executions": 1250,
    "successful_executions": 1232,
    "failed_executions": 18,
    "success_rate": 98.56
  },
  "flow_stats": [
    {
      "name": "GitHub Monitor",
      "executions": 240,
      "successes": 238,
      "failures": 2,
      "success_rate": 99.17,
      "last_execution": "2024-01-15T14:00:00.000Z",
      "avg_response_time": 450
    }
  ],
  "recent_activity": [
    {
      "flow_name": "System Monitor",
      "timestamp": "2024-01-15T14:30:00.000Z",
      "status": "success",
      "execution_time": 0.25
    }
  ],
  "period": {
    "start": "2024-01-01T00:00:00.000Z",
    "end": "2024-01-15T14:30:00.000Z",
    "days": 14
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/statistics
```

### Get Log Statistics

Retrieve log-based statistics and metrics.

**Endpoint:** `GET /api/logs/stats`

**Response:**
```json
{
  "total_logs": 1250,
  "logs_by_level": {
    "info": 1200,
    "warning": 35,
    "error": 15
  },
  "recent_errors": 3,
  "log_file_size": 2048576
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/logs/stats
```

---

## Logging

### Get Application Logs

Retrieve application logs with optional filtering.

**Endpoint:** `GET /api/logs`

**Query Parameters:**
- `limit` (optional): Number of logs to return (default: 100)
- `level` (optional): Filter by log level (info, warning, error)
- `flow` (optional): Filter by flow name

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T14:30:00.000Z",
      "level": "info",
      "message": "Flow 'GitHub Monitor' executed successfully",
      "flow_name": "GitHub Monitor",
      "execution_time": 0.42
    },
    {
      "timestamp": "2024-01-15T14:25:00.000Z",
      "level": "warning",
      "message": "Slow response from API endpoint",
      "flow_name": "System Monitor",
      "response_time": 5.2
    }
  ],
  "count": 2,
  "total_available": 1250
}
```

**Examples:**
```bash
# Get latest 50 logs
curl -X GET "http://localhost:5000/api/logs?limit=50"

# Get only error logs
curl -X GET "http://localhost:5000/api/logs?level=error"

# Get logs for specific flow
curl -X GET "http://localhost:5000/api/logs?flow=GitHub%20Monitor"
```

---

## Testing & Notifications

### Send Test Notification

Send a test notification to verify Discord webhook configuration.

**Endpoint:** `POST /api/test`

**Request Body:**
```json
{
  "message": "Hello from API!",
  "embed": {
    "title": "Test Notification",
    "description": "This is a test message from the API",
    "color": "#00ff00"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test notification sent successfully",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from API!",
    "embed": {
      "title": "API Test",
      "description": "Testing the API",
      "color": "#0066cc"
    }
  }'
```

---

## Webhook Endpoints

### Receive Webhook Data

Endpoint for external services to send webhook notifications.

**Endpoint:** `POST /api/webhook/{flow_name}`

**Request Body:** (Varies by service)
```json
{
  "event": "push",
  "repository": {
    "name": "test-repo",
    "full_name": "user/test-repo"
  },
  "commits": [
    {
      "message": "Update README",
      "author": {
        "name": "John Doe"
      }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "flow_name": "github-updates",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/webhook/github-updates \
  -H "Content-Type: application/json" \
  -d '{
    "action": "opened",
    "pull_request": {
      "title": "Add new feature",
      "user": {
        "login": "developer"
      }
    }
  }'
```

---

## Data Export

### Get Endpoint Information

Retrieve information about monitored endpoints.

**Endpoint:** `GET /api/endpoints`

**Response:**
```json
{
  "endpoints": [
    {
      "url": "https://api.github.com/repos/octocat/Hello-World",
      "flow_name": "GitHub Monitor",
      "last_checked": "2024-01-15T14:30:00.000Z",
      "status": "active",
      "response_time": 0.45,
      "last_status_code": 200
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/endpoints
```

---

## Error Responses

### Standard Error Format

All errors follow this format:

```json
{
  "error": true,
  "message": "Description of the error",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid parameters |
| `404` | Not Found - Resource doesn't exist |
| `500` | Internal Server Error |

### Error Examples

**Flow Not Found (404):**
```json
{
  "error": true,
  "message": "Flow 'nonexistent-flow' not found",
  "code": "FLOW_NOT_FOUND",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

**Invalid Request (400):**
```json
{
  "error": true,
  "message": "Missing required field: message",
  "code": "INVALID_REQUEST",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

---

## Integration Examples

### Python Example

```python
import requests
import json

# Get application status
response = requests.get('http://localhost:5000/api/status')
status = response.json()
print(f"App status: {status['status']}")
print(f"Active flows: {status['active_flows']}")

# Send test notification
test_data = {
    "message": "Hello from Python!",
    "embed": {
        "title": "Python Integration",
        "description": "Testing API integration",
        "color": "#3776ab"
    }
}

response = requests.post(
    'http://localhost:5000/api/test',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(test_data)
)

if response.status_code == 200:
    print("Test notification sent successfully!")
else:
    print(f"Error: {response.status_code}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const baseURL = 'http://localhost:5000/api';

// Get all flows
async function getFlows() {
  try {
    const response = await axios.get(`${baseURL}/flows`);
    console.log(`Found ${response.data.count} flows`);
    return response.data.flows;
  } catch (error) {
    console.error('Error fetching flows:', error.message);
  }
}

// Send webhook data
async function sendWebhookData(flowName, data) {
  try {
    const response = await axios.post(
      `${baseURL}/webhook/${flowName}`,
      data,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('Webhook sent successfully:', response.data);
  } catch (error) {
    console.error('Error sending webhook:', error.message);
  }
}

// Usage
getFlows().then(flows => {
  flows.forEach(flow => {
    console.log(`Flow: ${flow.name}, Active: ${flow.active}`);
  });
});
```

### Bash/cURL Examples

```bash
#!/bin/bash

API_BASE="http://localhost:5000/api"

# Get application statistics
echo "=== Application Statistics ==="
curl -s "$API_BASE/statistics" | jq '.overview'

# Get recent logs
echo -e "\n=== Recent Logs ==="
curl -s "$API_BASE/logs?limit=5" | jq '.logs[]'

# Test webhook
echo -e "\n=== Testing Webhook ==="
curl -X POST "$API_BASE/webhook/test-flow" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "test",
    "message": "Hello from bash script",
    "timestamp": "'$(date -Iseconds)'"
  }' | jq '.'
```

---

## Rate Limiting

Currently, there are no rate limits implemented. For production use, consider implementing rate limiting based on your needs:

- **Recommended limits:**
  - Status endpoints: 60 requests/minute
  - Data endpoints: 30 requests/minute
  - Webhook endpoints: 100 requests/minute

---

## SDK and Libraries

### Community Libraries

- **Python**: `turtifications-py` (community maintained)
- **Node.js**: `turtifications-js` (community maintained)
- **Go**: `go-turtifications` (community maintained)

### Creating Your Own Wrapper

The API is REST-compliant and can be easily wrapped in any language. Key considerations:

1. **Error Handling**: Check HTTP status codes and parse error responses
2. **Retries**: Implement exponential backoff for failed requests
3. **Timeouts**: Set reasonable request timeouts (30-60 seconds)
4. **Logging**: Log API calls for debugging

---

## Next Steps

- Learn about [webhook configuration](../guides/notification-flows#webhook-triggers)
- Explore [flow templates](../guides/templates) for quick setup
- Check out [deployment options](../configuration) for production use