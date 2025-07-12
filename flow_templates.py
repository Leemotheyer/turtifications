"""
Flow templates for common services and use cases
"""

FLOW_TEMPLATES = {
    "sonarr_download": {
        "name": "Sonarr Download Notification",
        "description": "Notify when Sonarr downloads a new episode",
        "category": "Media",
        "trigger_type": "on_incoming",
        "webhook_name": "Sonarr",
        "webhook_avatar": "https://raw.githubusercontent.com/Sonarr/Sonarr/develop/Logo/400.png",
        "message_template": "🎬 **{series['title']}** - {episode['title']}\n\n📺 Episode: {episode['episodeNumber']}x{episode['seasonNumber']:02d}\n📁 Quality: {episode['quality']}\n💾 Size: {episode['size']}MB\n⏰ Downloaded: {time}",
        "embed_config": {
            "enabled": True,
            "title": "New Episode Downloaded",
            "description": "**{series['title']}** - {episode['title']}\n\n📺 Episode: {episode['episodeNumber']}x{episode['seasonNumber']:02d}\n📁 Quality: {episode['quality']}\n💾 Size: {episode['size']}MB",
            "color": "#00ff00",
            "timestamp": True,
            "thumbnail_url": "{series['images']['0']['remoteUrl']}"
        },
        "accept_webhooks": True
    },
    
    "radarr_download": {
        "name": "Radarr Download Notification",
        "description": "Notify when Radarr downloads a new movie",
        "category": "Media",
        "trigger_type": "on_incoming",
        "webhook_name": "Radarr",
        "webhook_avatar": "https://raw.githubusercontent.com/Radarr/Radarr/develop/Logo/400.png",
        "message_template": "🎬 **{movie['title']}** ({movie['year']})\n\n📁 Quality: {movie['quality']}\n💾 Size: {movie['size']}MB\n⏰ Downloaded: {time}",
        "embed_config": {
            "enabled": True,
            "title": "New Movie Downloaded",
            "description": "**{movie['title']}** ({movie['year']})\n\n📁 Quality: {movie['quality']}\n💾 Size: {movie['size']}MB",
            "color": "#00ff00",
            "timestamp": True,
            "thumbnail_url": "{movie['images']['0']['remoteUrl']}"
        },
        "accept_webhooks": True
    },
    
    "kapowarr_download": {
        "name": "Kapowarr Download Notification",
        "description": "Notify when Kapowarr downloads a new comic",
        "category": "Media",
        "trigger_type": "on_incoming",
        "webhook_name": "Kapowarr",
        "webhook_avatar": "https://img.freepik.com/free-vector/angry-man-yelling-cartoon-illustration_1308-163237.jpg",
        "message_template": "📚 **{result['0']['web_title']}**\n\n📖 From: {result['0']['web_link']}\n📥 Source: {result['0']['source']}\n⏰ Downloaded: {result['0']['downloaded_at']}",
        "embed_config": {
            "enabled": True,
            "title": "New Comic Downloaded",
            "description": "**{result['0']['web_title']}**\n\n📖 From: {result['0']['web_link']}\n📥 Source: {result['0']['source']}",
            "color": "#00ff00",
            "timestamp": True
        },
        "accept_webhooks": True
    },
    
    "system_monitor": {
        "name": "System Monitor",
        "description": "Monitor system resources and notify on changes",
        "category": "System",
        "trigger_type": "on_change",
        "webhook_name": "System Monitor",
        "message_template": "🖥️ **System Status Update**\n\n💾 Memory Usage: {data['memory_usage']}%\n💿 Disk Usage: {data['disk_usage']}%\n🔥 CPU Usage: {data['cpu_usage']}%\n⏰ Time: {time}",
        "embed_config": {
            "enabled": True,
            "title": "System Status",
            "description": "💾 Memory: {data['memory_usage']}%\n💿 Disk: {data['disk_usage']}%\n🔥 CPU: {data['cpu_usage']}%",
            "color": "#ff9900",
            "timestamp": True
        },
        "endpoint": "http://localhost:8080/api/system/stats",
        "field": "data['cpu_usage']"
    },
    
    "website_monitor": {
        "name": "Website Status Monitor",
        "description": "Monitor website availability and response time",
        "category": "Monitoring",
        "trigger_type": "on_change",
        "webhook_name": "Website Monitor",
        "message_template": "🌐 **Website Status: {data['status']}**\n\n🔗 URL: {data['url']}\n⏱️ Response Time: {data['response_time']}ms\n📊 Status Code: {data['status_code']}\n⏰ Time: {time}",
        "embed_config": {
            "enabled": True,
            "title": "Website Status",
            "description": "🔗 {data['url']}\n⏱️ {data['response_time']}ms\n📊 {data['status_code']}",
            "color": "#00ff00",
            "timestamp": True
        },
        "endpoint": "https://httpbin.org/status/200",
        "field": "data['status']"
    },
    
    "daily_summary": {
        "name": "Daily Summary",
        "description": "Send a daily summary of activities",
        "category": "Reports",
        "trigger_type": "timer",
        "webhook_name": "Daily Summary",
        "message_template": "📊 **Daily Summary Report**\n\n📈 Total Downloads: {data['total_downloads']}\n🎬 Movies: {data['movie_count']}\n📺 Episodes: {data['episode_count']}\n📚 Comics: {data['comic_count']}\n⏰ Date: {time}",
        "embed_config": {
            "enabled": True,
            "title": "Daily Summary",
            "description": "📈 Total Downloads: {data['total_downloads']}\n🎬 Movies: {data['movie_count']}\n📺 Episodes: {data['episode_count']}\n📚 Comics: {data['comic_count']}",
            "color": "#6366f1",
            "timestamp": True
        },
        "interval": 1440  # 24 hours
    },
    
    "error_alert": {
        "name": "Error Alert",
        "description": "Alert when errors occur in monitored services",
        "category": "Alerts",
        "trigger_type": "on_change",
        "webhook_name": "Error Alert",
        "message_template": "🚨 **Error Alert**\n\n❌ Service: {data['service_name']}\n🔍 Error: {data['error_message']}\n⏰ Time: {time}",
        "embed_config": {
            "enabled": True,
            "title": "Error Alert",
            "description": "❌ {data['service_name']}\n🔍 {data['error_message']}",
            "color": "#ff0000",
            "timestamp": True
        },
        "endpoint": "http://localhost:8080/api/errors",
        "field": "data['error_count']"
    }
}

def get_template_categories():
    """Get list of available template categories"""
    categories = set()
    for template in FLOW_TEMPLATES.values():
        categories.add(template.get('category', 'General'))
    return sorted(list(categories))

def get_templates_by_category(category=None):
    """Get templates filtered by category"""
    if category:
        return {name: template for name, template in FLOW_TEMPLATES.items() 
                if template.get('category') == category}
    return FLOW_TEMPLATES

def get_template(template_name):
    """Get a specific template by name"""
    return FLOW_TEMPLATES.get(template_name) 