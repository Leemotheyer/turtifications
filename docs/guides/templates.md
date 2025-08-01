---
layout: default
title: Using Templates
parent: Guides
nav_order: 2
---

# Using Templates
{: .no_toc }

Learn how to use pre-built flow templates to quickly set up notification flows for popular services and use cases.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## What are Flow Templates?

Flow templates are pre-configured notification setups for popular services and common use cases. They include:

- **Pre-configured triggers** optimized for specific services
- **Message templates** with proper formatting and variables
- **Discord embeds** designed for the service's data structure
- **Best practice settings** for intervals and conditions

Templates save you time and provide proven configurations that work well with various services.

---

## Available Templates

### Media Management

#### Sonarr Download Notifications

Monitor your Sonarr instance for completed downloads.

**Features:**
- Webhook trigger for instant notifications
- Rich embeds with episode artwork
- Series and episode information
- Quality and file size details

**Setup:**
1. In Sonarr: Settings → Connect → Add Webhook
2. URL: `http://your-server:5000/api/webhook/sonarr`
3. Triggers: "On Download" and "On Upgrade"

**Example Notification:**
```
🎬 Breaking Bad - Pilot

📺 Episode: S01E01
📁 Quality: WEBDL-1080p
💾 Size: 1.2GB
⏰ Downloaded: 2024-01-15 14:30:00
```

#### Radarr Download Notifications

Get notified when movies are downloaded via Radarr.

**Features:**
- Movie poster thumbnails
- Quality and release information
- IMDb ratings and year
- File size and format details

**Setup:**
1. In Radarr: Settings → Connect → Add Webhook
2. URL: `http://your-server:5000/api/webhook/radarr`
3. Triggers: "On Download" and "On Upgrade"

**Example Notification:**
```
🎬 The Dark Knight (2008)

📁 Quality: BluRay-1080p
💾 Size: 8.5GB
⭐ Rating: 9.0/10
⏰ Downloaded: 2024-01-15 14:30:00
```

#### Kapowarr Comic Downloads

Monitor comic downloads from Kapowarr.

**Features:**
- Comic series tracking
- Issue information
- Download source details
- Custom comic artwork

**Setup:**
1. In Kapowarr: Settings → Webhooks
2. URL: `http://your-server:5000/api/webhook/kapowarr`
3. Event: "Download Complete"

---

### System Monitoring

#### Server Health Monitor

Monitor server resources and health metrics.

**Features:**
- CPU, memory, and disk usage
- Uptime tracking
- Alert thresholds
- Service status monitoring

**Configuration:**
```yaml
Name: Server Health Monitor
Trigger: Timer (every 5 minutes)
URL: https://your-server.com/api/health
Condition: result['cpu_usage'] > 80 or result['memory_usage'] > 90
```

**Example Alert:**
```
🚨 High Resource Usage Alert

🖥️ CPU Usage: 85%
💾 Memory Usage: 92%
💿 Disk Usage: 67%
⏱️ Uptime: 15 days

⚠️ Immediate attention required!
```

#### Website Uptime Monitor

Monitor website availability and response times.

**Features:**
- HTTP status code monitoring
- Response time tracking
- Downtime alerts
- Performance metrics

**Configuration:**
```yaml
Name: Website Monitor
Trigger: Timer (every 2 minutes)
URL: https://httpstat.us/200
Condition: result['status'] != '200'
```

**Example Alert:**
```
🚨 Website Down Alert

🌐 URL: https://example.com
📊 Status: 503 Service Unavailable
⏰ Time: 2024-01-15 14:30:00
🔄 Response Time: Timeout

❌ Website appears to be offline!
```

---

### Development & CI/CD

#### GitHub Repository Monitor

Track repository activity, releases, and issues.

**Features:**
- Star and fork tracking
- Release notifications
- Issue and PR monitoring
- Commit activity alerts

**Configuration:**
```yaml
Name: GitHub Activity
Trigger: Change Detection (hourly)
URL: https://api.github.com/repos/owner/repo
Field: result['updated_at']
```

#### CI/CD Pipeline Notifications

Monitor build and deployment status.

**Features:**
- Build status alerts
- Deployment notifications
- Test result summaries
- Performance metrics

**Webhook Setup:**
Configure your CI/CD tool to send webhook notifications:
```
POST http://your-server:5000/api/webhook/ci-cd
Content-Type: application/json

{
  "build_id": "123",
  "status": "success",
  "branch": "main",
  "commit": "abc123",
  "duration": 180
}
```

---

### API and Service Monitoring

#### API Response Monitor

Monitor API endpoints for changes or issues.

**Features:**
- Response time tracking
- Status code monitoring
- Data change detection
- Error rate alerts

**Configuration:**
```yaml
Name: API Monitor
Trigger: Timer (every 10 minutes)
URL: https://api.example.com/status
Condition: result['response_time'] > 5000 or result['error_rate'] > 0.1
```

#### Database Health Monitor

Monitor database performance and health.

**Features:**
- Connection pool status
- Query performance metrics
- Storage usage alerts
- Replication lag monitoring

---

## Using Templates

### Method 1: From the Templates Page

1. Navigate to **Templates** in the main menu
2. Browse available templates by category
3. Click **Preview** to see example output
4. Click **Use Template** to create a flow
5. Customize settings as needed
6. Save and activate the flow

### Method 2: From the Flow Builder

1. Go to **Builder** in the main menu
2. Click **Load Template** button
3. Select a template from the dropdown
4. The builder will populate with template settings
5. Modify as needed for your use case

---

## Customizing Templates

### Modifying Message Templates

Templates come with pre-built messages, but you can customize them:

**Original Sonarr Template:**
```
🎬 **{series['title']}** - {episode['title']}

📺 Episode: S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}
```

**Customized Version:**
```
🆕 NEW EPISODE DOWNLOADED!

📺 **{series['title']}**
🎬 {episode['title']} (S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d})
📁 Quality: {episode['quality']}
⭐ Rating: {episode['overview']}

🔗 [View in Sonarr]({series['url']})
```

### Adjusting Embed Settings

Customize embed colors, fields, and layout:

```yaml
Embed Settings:
  Title: "🎬 New Movie Available"
  Description: "{movie['title']} ({movie['year']})"
  Color: "#ff6b6b"  # Custom red color
  Fields:
    - Name: "Genre"
      Value: "{movie['genres'][0]}"
      Inline: true
    - Name: "Runtime"
      Value: "{movie['runtime']} minutes"
      Inline: true
  Thumbnail: "{movie['poster_url']}"
  Footer: "Downloaded via Radarr"
```

### Adding Conditions

Add custom conditions to control when notifications are sent:

**Example: Only notify for high-rated content**
```yaml
Condition: result['vote_average'] >= 7.0
```

**Example: Only notify during specific hours**
```yaml
Condition: 9 <= datetime.now().hour <= 17
```

**Example: Skip certain qualities**
```yaml
Condition: result['quality']['quality']['name'] != 'SDTV'
```

---

## Creating Custom Templates

### Template Structure

Create your own templates by following this structure:

```yaml
template_name:
  name: "Template Display Name"
  description: "Brief description of what this template does"
  category: "Category (Media, System, Development, etc.)"
  trigger_type: "timer|on_change|webhook"
  
  # Timer/Change Detection settings
  url: "https://api.example.com/endpoint"
  check_interval: 300
  timeout: 30
  
  # Webhook settings (if applicable)
  webhook_name: "service-name"
  webhook_avatar: "https://example.com/avatar.png"
  
  # Message template
  message_template: |
    🔔 **Alert Title**
    
    📊 **Status**: {result['status']}
    ⏰ **Time**: {time}
  
  # Embed configuration
  embed_config:
    enabled: true
    title: "Embed Title"
    description: "Embed description with {variables}"
    color: "#00ff00"
    thumbnail_url: "{result['image_url']}"
    fields:
      - name: "Field Name"
        value: "{result['field_value']}"
        inline: true
```

### Adding Custom Templates

1. Create your template YAML file
2. Test the configuration manually in the flow builder
3. Save successful configurations as templates
4. Share with the community via GitHub

---

## Template Examples by Service

### Plex Media Server

Monitor Plex server activity and new content.

```yaml
Name: "Plex Activity Monitor"
Trigger: Webhook
Message: |
  🎬 **Plex Activity**
  
  👤 **User**: {user['title']}
  📺 **Content**: {Metadata['title']}
  🎭 **Type**: {Metadata['type']}
  ▶️ **Action**: {event}
  
  ⏰ **Time**: {time}

Webhook Setup:
URL: http://your-server:5000/api/webhook/plex
```

### Docker Container Monitoring

Monitor Docker container status and health.

```yaml
Name: "Docker Health Check"
Trigger: Timer (every 5 minutes)
URL: "http://localhost:2375/containers/json"
Condition: any(container['State'] != 'running' for container in result)
Message: |
  🐳 **Docker Container Alert**
  
  {#for container in result}
  {#if container['State'] != 'running'}
  ❌ **{container['Names'][0]}**: {container['State']}
  {#endif}
  {#endfor}
```

### Home Assistant Integration

Monitor Home Assistant entities and automation.

```yaml
Name: "Home Assistant Alerts"
Trigger: Webhook
Message: |
  🏠 **Home Assistant Alert**
  
  🏷️ **Entity**: {entity_id}
  📊 **State**: {new_state['state']}
  📅 **Changed**: {time}
  
  {#if attributes}
  📋 **Attributes**: {attributes}
  {#endif}
```

### Weather Monitoring

Track weather conditions and alerts.

```yaml
Name: "Weather Alerts"
Trigger: Timer (every hour)
URL: "https://api.openweathermap.org/data/2.5/weather?q=YourCity&appid=YOUR_API_KEY"
Condition: result['weather'][0]['main'] in ['Thunderstorm', 'Snow', 'Rain']
Message: |
  🌦️ **Weather Alert**
  
  📍 **Location**: {result['name']}
  🌡️ **Temperature**: {result['main']['temp']}°C
  ☁️ **Conditions**: {result['weather'][0]['description']}
  💧 **Humidity**: {result['main']['humidity']}%
  
  {#if result['weather'][0]['main'] == 'Rain'}
  ☔ Don't forget your umbrella!
  {#endif}
```

---

## Best Practices

### Template Design

1. **Use clear, descriptive names** for easy identification
2. **Include relevant emojis** for visual appeal
3. **Test with real data** before sharing
4. **Document required setup steps** clearly
5. **Provide example outputs** in descriptions

### Performance Optimization

1. **Set appropriate check intervals** (avoid over-polling APIs)
2. **Use conditions to reduce noise** (only notify when necessary)
3. **Optimize embed complexity** (balance detail with performance)
4. **Consider rate limits** of target APIs

### Security Considerations

1. **Don't hardcode API keys** in templates
2. **Use environment variables** for sensitive data
3. **Validate webhook sources** when possible
4. **Document security requirements** clearly

---

## Template Troubleshooting

### Common Issues

**Template variables showing as empty**
: Check that the API response structure matches the template expectations

**Webhook not triggering**
: Verify the webhook URL is correct and accessible from the service

**Embed not displaying correctly**
: Validate embed JSON structure and field types

**Condition not working**
: Test conditions with actual data using the preview feature

### Debugging Tips

1. **Use the Preview feature** to test with real API data
2. **Check application logs** for error details
3. **Test API endpoints manually** with curl or Postman
4. **Validate JSON structure** of webhook payloads

---

## Contributing Templates

### Sharing Your Templates

1. **Test thoroughly** with your actual services
2. **Document setup requirements** clearly
3. **Provide example configurations** and outputs
4. **Submit via GitHub** pull request
5. **Include screenshots** of notifications

### Template Guidelines

- Follow the standard template structure
- Include comprehensive documentation
- Test with multiple data scenarios
- Ensure compatibility with service APIs
- Provide fallback handling for missing data

---

## Next Steps

- Learn about [Creating Custom Notification Flows](notification-flows) for advanced setups
- Explore the [API Reference](../api/reference) for programmatic template management
- Check out [Configuration Options](../configuration) for production deployment