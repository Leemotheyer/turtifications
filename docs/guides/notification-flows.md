---
layout: default
title: Creating Notification Flows
parent: Guides
nav_order: 1
---

# Creating Notification Flows
{: .no_toc }

Learn how to create powerful notification flows that monitor APIs, detect changes, and send rich Discord notifications.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## What are Notification Flows?

Notification flows are automated monitoring systems that:
- Watch APIs or webhooks for changes
- Process and format data
- Send notifications to Discord with rich formatting
- Can include conditions, embeds, and custom scheduling

---

## Types of Triggers

### Timer-Based Triggers

Monitor an API endpoint at regular intervals.

**Example: System Status Monitor**

```yaml
Name: Server Health Check
Trigger Type: Timer
Interval: 300 seconds (5 minutes)
URL: https://api.example.com/health
Message: "🟢 Server Status: {result['status']} | CPU: {result['cpu']}% | Memory: {result['memory']}%"
```

### Change Detection Triggers

Only notify when specific values change.

**Example: User Count Monitor**

```yaml
Name: User Growth Tracker
Trigger Type: Change Detection
URL: https://api.example.com/stats
Field to Monitor: result['total_users']
Message: "📈 User count changed from {old_value} to {value}!"
```

### Webhook Triggers

Receive notifications from external services.

**Example: CI/CD Pipeline**

```yaml
Name: Build Notifications
Trigger Type: Webhook
Webhook URL: https://yourserver.com/api/webhook/build-notify
Message: "🚀 Build {result['build_id']} completed with status: {result['status']}"
```

---

## Creating Your First Flow

### Step 1: Access the Flow Builder

1. Navigate to your Turtifications dashboard
2. Click **Builder** in the main menu
3. The flow builder interface will open

### Step 2: Basic Configuration

**Flow Name**
: Give your flow a descriptive name (e.g., "Website Uptime Monitor")

**Trigger Type**
: Choose from Timer, Change Detection, or Webhook

**Active Status**
: Toggle to enable/disable the flow

### Step 3: Configure the Trigger

#### For Timer-Based Flows:

```
URL: https://httpstat.us/200
Check Interval: 300 (seconds)
Timeout: 30 (seconds)
```

#### For Change Detection Flows:

```
URL: https://api.github.com/repos/octocat/Hello-World
Field to Monitor: result['stargazers_count']
Check Interval: 3600 (1 hour)
```

#### For Webhook Flows:

```
Webhook Name: github-releases
(The webhook URL will be automatically generated)
```

### Step 4: Design Your Message

Use template variables to create dynamic messages:

```
🔔 **Alert: Website Status**

🌐 **URL**: https://example.com
📊 **Status**: {result['status']}
⏰ **Checked**: {time}
🔄 **Response Time**: {result['response_time']}ms

{#if result['status'] == '200'}
✅ Everything is working perfectly!
{#else}
❌ There might be an issue - please check manually.
{#endif}
```

---

## Advanced Features

### Conditional Logic

Add conditions to control when notifications are sent:

**Example: Only notify on errors**

```yaml
Condition: result['status_code'] != 200
Message: "🚨 ALERT: Website is down! Status: {result['status_code']}"
```

**Example: Only notify during business hours**

```yaml
Condition: time.hour >= 9 and time.hour <= 17
Message: "📊 Business hours update: {result['summary']}"
```

### Discord Embeds

Create rich, formatted notifications:

```yaml
Embed Enabled: true
Title: "🚀 New Release Available"
Description: "**{result['name']}** ({result['tag_name']})"
Color: "#00ff00"
Fields:
  - Name: "Release Notes"
    Value: "{result['body']}"
  - Name: "Published"
    Value: "{result['published_at']}"
    Inline: true
Thumbnail: "{result['author']['avatar_url']}"
```

### Custom Headers & Authentication

For APIs requiring authentication:

```yaml
Headers:
  Authorization: "Bearer YOUR_API_TOKEN"
  User-Agent: "Turtifications/1.0"
  Content-Type: "application/json"
```

---

## Real-World Examples

### Example 1: Sonarr Download Notifications

Monitor your Sonarr instance for new downloads:

```yaml
Name: "Sonarr Downloads"
Trigger Type: Webhook
Message: |
  🎬 **{series['title']}** - {episode['title']}
  
  📺 **Episode**: S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}
  📁 **Quality**: {episode['quality']}
  💾 **Size**: {episode['size']}MB
  ⏰ **Downloaded**: {time}

Embed:
  Title: "New Episode Downloaded"
  Color: "#00ff00"
  Thumbnail: "{series['images']['0']['url']}"
```

### Example 2: Website Change Monitor

Monitor a website for content changes:

```yaml
Name: "News Website Monitor"
Trigger Type: Change Detection
URL: "https://news-site.com/api/latest"
Field: "result['articles']['0']['title']"
Message: |
  📰 **Breaking News Update**
  
  🔖 **New Article**: {result['articles']['0']['title']}
  ✍️ **Author**: {result['articles']['0']['author']}
  🔗 **Link**: {result['articles']['0']['url']}
  
  📝 **Summary**: {result['articles']['0']['summary']}
```

### Example 3: Server Resource Monitor

Monitor server resources with thresholds:

```yaml
Name: "Server Resources"
Trigger Type: Timer
Interval: 300
URL: "https://your-server.com/api/stats"
Condition: result['cpu_usage'] > 80 or result['memory_usage'] > 90
Message: |
  🚨 **High Resource Usage Alert**
  
  🖥️ **CPU Usage**: {result['cpu_usage']}%
  💾 **Memory Usage**: {result['memory_usage']}%
  💿 **Disk Usage**: {result['disk_usage']}%
  
  ⚠️ Immediate attention may be required!

Embed:
  Title: "Server Alert"
  Color: "#ff0000"
```

### Example 4: GitHub Repository Monitor

Track GitHub repository activity:

```yaml
Name: "GitHub Activity"
Trigger Type: Change Detection
URL: "https://api.github.com/repos/owner/repo"
Field: "result['updated_at']"
Message: |
  🔄 **Repository Updated**
  
  📁 **Repository**: {result['full_name']}
  ⭐ **Stars**: {result['stargazers_count']}
  🍴 **Forks**: {result['forks_count']}
  📝 **Description**: {result['description']}
  
  🔗 [View Repository]({result['html_url']})
```

---

## Template Variables Reference

### Basic Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{time}` | Current timestamp | `2024-01-15 14:30:00` |
| `{value}` | Current monitored value | `150` |
| `{old_value}` | Previous value (change detection) | `140` |

### API Data Access

| Format | Description | Example |
|--------|-------------|---------|
| `{result['key']}` | Direct field access | `{result['status']}` |
| `{result['nested']['key']}` | Nested object access | `{result['user']['name']}` |
| `{result['array']['0']['key']}` | Array element access | `{result['items']['0']['title']}` |

### Conditional Logic

```yaml
# Simple condition
{#if result['status'] == 'success'}
✅ Operation successful!
{#else}
❌ Operation failed!
{#endif}

# Multiple conditions
{#if result['cpu'] > 80}
🔴 High CPU usage!
{#elif result['cpu'] > 60}
🟡 Moderate CPU usage
{#else}
🟢 CPU usage normal
{#endif}
```

---

## Testing and Debugging

### Using the Preview Feature

1. Configure your flow settings
2. Click **Preview Notification**
3. Review the formatted output
4. Adjust your template as needed

### Testing Flows

1. Click **Test Flow** in the builder
2. Check your Discord channel for the test notification
3. Verify all variables are displaying correctly

### Common Issues

**Variables showing as empty**
: Check that the field path is correct using the preview feature

**Notifications not sending**
: Verify your Discord webhook URL and that the flow is marked as "Active"

**Webhook not receiving data**
: Check that external services are configured with the correct webhook URL

---

## Best Practices

### Message Design

1. **Use clear, descriptive titles**
2. **Include relevant emojis for visual appeal**
3. **Keep messages concise but informative**
4. **Use embeds for complex data**

### Performance

1. **Set reasonable check intervals** (avoid checking every few seconds)
2. **Use conditions to reduce noise**
3. **Monitor only essential data points**

### Security

1. **Use environment variables for sensitive data**
2. **Avoid exposing API keys in message templates**
3. **Regularly rotate webhook URLs if needed**

---

## Next Steps

- Learn about [Using Templates](templates) for quick setup
- Explore the [API Reference](../api/reference) for programmatic access
- Check out [Advanced Configuration](../configuration) for production deployments