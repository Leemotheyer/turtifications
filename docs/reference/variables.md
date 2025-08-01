---
layout: default
title: Template Variables
parent: Reference
nav_order: 1
---

# Template Variables Reference
{: .no_toc }

Complete reference for all available template variables and their usage in notification messages.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

Template variables allow you to create dynamic notification messages using data from API responses, webhooks, and system information. Variables are enclosed in curly braces and support nested object access and conditional logic.

---

## Basic Variables

### System Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{time}` | Current timestamp | `2024-01-15 14:30:00` |
| `{date}` | Current date | `2024-01-15` |
| `{timestamp}` | Unix timestamp | `1705330200` |
| `{iso_time}` | ISO 8601 timestamp | `2024-01-15T14:30:00.000Z` |

### Flow Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{flow_name}` | Name of the current flow | `GitHub Monitor` |
| `{trigger_type}` | Type of trigger | `timer`, `on_change`, `webhook` |
| `{execution_count}` | Number of times flow has run | `42` |
| `{last_success}` | Last successful execution time | `2024-01-15 14:25:00` |

### Change Detection Variables

Available only for flows with trigger type "change detection":

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{value}` | Current value of monitored field | `150` |
| `{old_value}` | Previous value of monitored field | `140` |
| `{change}` | Difference between values | `10` |
| `{change_percent}` | Percentage change | `7.14` |

---

## API Data Access

### Basic Field Access

Access fields from API responses using bracket notation:

```yaml
# API Response:
{
  "status": "success",
  "count": 42,
  "message": "All systems operational"
}

# Template Usage:
Status: {result['status']}
Count: {result['count']}
Message: {result['message']}
```

### Nested Object Access

Access nested objects and arrays:

```yaml
# API Response:
{
  "user": {
    "name": "John Doe",
    "email": "john@example.com",
    "settings": {
      "theme": "dark",
      "notifications": true
    }
  },
  "projects": [
    {
      "name": "Project A",
      "status": "active"
    },
    {
      "name": "Project B", 
      "status": "completed"
    }
  ]
}

# Template Usage:
User: {result['user']['name']}
Email: {result['user']['email']}
Theme: {result['user']['settings']['theme']}
First Project: {result['projects']['0']['name']}
Project Status: {result['projects']['0']['status']}
```

### Array Handling

Work with arrays and lists:

```yaml
# Access array elements by index
First item: {result['items']['0']}
Second item: {result['items']['1']}
Last item: {result['items']['-1']}  # Python-style negative indexing

# Get array length (requires conditional logic)
{#if result['items']}
Total items: {result['items']|length}
{#endif}
```

---

## Conditional Logic

### Basic Conditions

Use conditional statements to control message content:

```yaml
# Simple condition
{#if result['status'] == 'success'}
✅ Operation completed successfully!
{#else}
❌ Operation failed!
{#endif}

# Multiple conditions
{#if result['cpu_usage'] > 90}
🔴 Critical CPU usage: {result['cpu_usage']}%
{#elif result['cpu_usage'] > 70}
🟡 High CPU usage: {result['cpu_usage']}%
{#else}
🟢 CPU usage normal: {result['cpu_usage']}%
{#endif}
```

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal to | `{#if result['status'] == 'ok'}` |
| `!=` | Not equal to | `{#if result['error'] != ''}` |
| `>` | Greater than | `{#if result['count'] > 100}` |
| `<` | Less than | `{#if result['cpu'] < 50}` |
| `>=` | Greater than or equal | `{#if result['score'] >= 80}` |
| `<=` | Less than or equal | `{#if result['temp'] <= 30}` |
| `in` | Contains | `{#if 'error' in result['message']}` |

### Logical Operators

Combine conditions with logical operators:

```yaml
# AND operator
{#if result['status'] == 'ok' and result['count'] > 0}
System is healthy with {result['count']} items
{#endif}

# OR operator  
{#if result['status'] == 'error' or result['status'] == 'warning'}
⚠️ System needs attention
{#endif}

# NOT operator
{#if not result['maintenance_mode']}
System is operational
{#endif}
```

### Field Existence Checks

Check if fields exist before using them:

```yaml
# Check if field exists
{#if result['optional_field']}
Optional value: {result['optional_field']}
{#else}
Optional field not provided
{#endif}

# Check for nested fields
{#if result['user'] and result['user']['name']}
Welcome, {result['user']['name']}!
{#endif}

# Check array length
{#if result['items'] and result['items']|length > 0}
Found {result['items']|length} items
{#else}
No items found
{#endif}
```

---

## Advanced Features

### Loops and Iteration

Iterate over arrays and objects:

```yaml
# Loop through array
{#for item in result['items']}
- {item['name']}: {item['status']}
{#endfor}

# Loop with index
{#for item in result['items']}
{loop.index}. {item['name']}
{#endfor}

# Loop through object keys
{#for key, value in result['metadata'].items()}
{key}: {value}
{#endfor}

# Conditional loop
{#for commit in result['commits']}
{#if commit['author'] == 'important-user'}
🔥 Important commit: {commit['message']}
{#endif}
{#endfor}
```

### String Manipulation

Basic string operations:

```yaml
# Uppercase/lowercase
{result['name']|upper}
{result['message']|lower}

# Truncate string
{result['description']|truncate(50)}

# Replace text
{result['path']|replace('/', '\\')}

# Default values
{result['optional_field']|default('Not provided')}
```

### Formatting

Format numbers and dates:

```yaml
# Number formatting
{result['price']|round(2)}
{result['percentage']|round(1)}%

# Date formatting (if timestamp provided)
{result['created_at']|strftime('%Y-%m-%d %H:%M')}

# JSON pretty printing
{result['data']|tojson(indent=2)}
```

---

## Service-Specific Variables

### GitHub API Variables

Common variables when using GitHub API:

```yaml
# Repository info
Repository: {result['full_name']}
Description: {result['description']}
Stars: {result['stargazers_count']}
Forks: {result['forks_count']}
Language: {result['language']}
Last update: {result['updated_at']}

# For webhook data
Author: {result['commits']['0']['author']['name']}
Commit message: {result['commits']['0']['message']}
Branch: {result['ref']}
```

### Docker API Variables

For Docker container monitoring:

```yaml
# Container info
Container: {result['Names']['0']}
Image: {result['Image']}
Status: {result['Status']}
State: {result['State']}
Created: {result['Created']}

# Network info
{#if result['NetworkSettings']}
IP Address: {result['NetworkSettings']['IPAddress']}
{#endif}
```

### System Monitoring Variables

Common system metrics:

```yaml
# CPU and Memory
CPU Usage: {result['cpu_percent']}%
Memory Usage: {result['memory_percent']}%
Available Memory: {result['memory_available']} MB

# Disk Usage
Disk Usage: {result['disk_usage']}%
Free Space: {result['disk_free']} GB

# Network
Bytes Sent: {result['network_sent']} MB
Bytes Received: {result['network_recv']} MB
```

### HTTP Status Monitoring

For website monitoring:

```yaml
# HTTP Response
Status Code: {result['status_code']}
Response Time: {result['response_time']}ms
Content Length: {result['content_length']} bytes

# Headers
Server: {result['headers']['Server']}
Content-Type: {result['headers']['Content-Type']}
```

---

## Webhook-Specific Variables

### Common Webhook Patterns

Variables available in webhook flows depend on the service sending the webhook:

#### Sonarr/Radarr Webhooks

```yaml
# Series info (Sonarr)
Series: {series['title']}
Episode: {episodes['0']['title']}
Season: {episodes['0']['seasonNumber']}
Episode Number: {episodes['0']['episodeNumber']}
Quality: {episodes['0']['quality']['quality']['name']}

# Movie info (Radarr)  
Movie: {movie['title']}
Year: {movie['year']}
Quality: {movie['quality']['quality']['name']}
Size: {movie['movieFile']['size']} bytes
```

#### Jenkins/CI Webhooks

```yaml
# Build info
Build Number: {build['number']}
Result: {build['result']}
Duration: {build['duration']}ms
URL: {build['url']}

# Git info
Branch: {build['scm']['branch']}
Commit: {build['scm']['commit']}
Author: {build['scm']['author']}
```

#### Custom Application Webhooks

```yaml
# Design your own webhook payload structure
Application: {app_name}
Environment: {environment}
Version: {version}
Status: {deployment_status}
User: {deployed_by}
```

---

## Error Handling

### Safe Variable Access

Prevent errors when fields might be missing:

```yaml
# Using default values
Name: {result['name']|default('Unknown')}
Count: {result['count']|default(0)}

# Conditional access
{#if result['user'] and result['user']['email']}
Email: {result['user']['email']}
{#else}
Email: Not provided
{#endif}

# Try-catch pattern (using defaults)
{result['optional']['nested']['field']|default('Field not available')}
```

### Debugging Templates

Debug your templates by showing raw data:

```yaml
# Show entire API response (for debugging)
Raw data: {result|tojson(indent=2)}

# Show specific field types
Field type: {result['field']|string}
Field exists: {result['field'] is defined}
```

---

## Best Practices

### Template Organization

1. **Keep templates readable**
   ```yaml
   # Good: Clear and organized
   📊 **System Status Report**
   
   🖥️ **CPU**: {result['cpu']}%
   💾 **Memory**: {result['memory']}%
   💿 **Disk**: {result['disk']}%
   
   {#if result['cpu'] > 80}
   ⚠️ High CPU usage detected!
   {#endif}
   ```

2. **Use meaningful variable names in webhooks**
   ```yaml
   # Design webhook payloads with clear field names
   {
     "service_name": "web-app",
     "deployment_status": "success", 
     "environment": "production",
     "version": "1.2.3"
   }
   ```

3. **Provide fallbacks for optional data**
   ```yaml
   Author: {result['author']|default('Unknown')}
   Description: {result['description']|default('No description provided')}
   ```

### Performance Considerations

1. **Limit complex logic in templates**
2. **Use simple conditions when possible** 
3. **Avoid deep nesting** in conditional statements
4. **Cache complex calculations** outside the template if possible

### Security Notes

1. **Don't expose sensitive data** in notifications
2. **Sanitize user input** in webhook data
3. **Use allowlists** for acceptable field values when possible

---

## Examples by Use Case

### Monitoring Alerts

```yaml
🚨 **{result['service']} Alert**

**Severity**: {result['severity']|upper}
**Message**: {result['message']}
**Time**: {time}

{#if result['severity'] == 'critical'}
🔴 **IMMEDIATE ACTION REQUIRED**
{#elif result['severity'] == 'warning'}
🟡 **Please investigate when possible**
{#else}
🟢 **Informational only**
{#endif}

**Details**:
- Host: {result['hostname']}
- Service: {result['service']}
- Metric: {result['metric_name']}
- Value: {result['current_value']}
- Threshold: {result['threshold']}
```

### Deployment Notifications

```yaml
🚀 **Deployment Complete**

**Application**: {app_name}
**Environment**: {environment|upper}
**Version**: {version}
**Status**: {#if status == 'success'}✅ Success{#else}❌ Failed{#endif}

**Details**:
- Deployed by: {deployed_by}
- Duration: {duration}s
- Commit: {git_commit[:8]}
- Branch: {git_branch}

{#if status == 'success'}
🔗 [View Application]({app_url})
{#else}
📋 [View Logs]({logs_url})
{#endif}
```

### API Monitoring

```yaml
📡 **API Status Update**

**Endpoint**: {result['endpoint']}
**Status**: {#if result['status'] == 200}🟢 Healthy{#else}🔴 Issue Detected{#endif}
**Response Time**: {result['response_time']}ms

{#if result['status'] != 200}
**Error Details**:
- Status Code: {result['status']}
- Error Message: {result['error_message']|default('No error message')}
{#endif}

**Performance**:
- Average Response Time: {result['avg_response_time']}ms
- Uptime: {result['uptime_percentage']}%
- Last Check: {time}
```

---

For more examples and advanced usage patterns, see the [Notification Flows Guide](../guides/notification-flows) and [Templates Guide](../guides/templates).