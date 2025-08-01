"""
Test data for comprehensive testing of the notification organizer app.
Contains realistic sample data for various services and scenarios.
"""

import json
from datetime import datetime, timedelta

# Sample configuration data
SAMPLE_CONFIG = {
    "discord_webhook": "https://discord.com/api/webhooks/123456789/test-webhook-url",
    "check_interval": 5,
    "log_retention": 1000,
    "notification_log_retention": 500,
    "user_variables": {
        "server_name": "Production Server",
        "admin_email": "admin@example.com",
        "environment": "prod"
    },
    "total_notifications_sent": 42,
    "notification_flows": [
        {
            "name": "Sonarr Downloads",
            "active": True,
            "trigger_type": "webhook",
            "category": "Media",
            "webhook_url": "https://discord.com/api/webhooks/123/sonarr",
            "webhook_name": "Sonarr",
            "message_template": "🎬 **{series['title']}** - {episode['title']}\n📺 Episode: S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}",
            "last_run": "2024-01-15 14:30:00",
            "last_value": "Breaking Bad - Pilot",
            "embed_config": {
                "enabled": True,
                "title": "New Episode Downloaded",
                "description": "**{series['title']}** - {episode['title']}",
                "color": "#00ff00",
                "timestamp": True
            },
            "condition_enabled": True,
            "condition": "episode['quality'] != 'SDTV'"
        },
        {
            "name": "Server Monitoring",
            "active": True,
            "trigger_type": "timer",
            "category": "System",
            "url": "https://api.example.com/server/status",
            "interval": 300,
            "message_template": "🖥️ Server Status: {status}\n💾 Memory: {memory_usage}%\n💽 Disk: {disk_usage}%",
            "last_run": "2024-01-15 14:25:00",
            "last_value": "Online",
            "change_detection": True
        },
        {
            "name": "GitHub Releases",
            "active": False,
            "trigger_type": "api",
            "category": "Development",
            "url": "https://api.github.com/repos/user/repo/releases/latest",
            "message_template": "🚀 New release: {name}\n📝 {body}",
            "last_run": None,
            "last_value": None
        }
    ]
}

# Sample Sonarr webhook data
SONARR_WEBHOOK_DATA = {
    "eventType": "Download",
    "series": {
        "id": 1,
        "title": "Breaking Bad",
        "path": "/tv/Breaking Bad",
        "tvdbId": 81189,
        "type": "standard",
        "images": [
            {
                "coverType": "poster",
                "remoteUrl": "https://artworks.thetvdb.com/banners/posters/81189-1.jpg"
            }
        ]
    },
    "episode": {
        "id": 123,
        "episodeNumber": 1,
        "seasonNumber": 1,
        "title": "Pilot",
        "airDate": "2008-01-20",
        "quality": "HDTV-720p",
        "size": 1024
    },
    "isUpgrade": False,
    "downloadClient": "SABnzbd",
    "downloadId": "SABnzbd_nzo_abc123"
}

# Sample Radarr webhook data
RADARR_WEBHOOK_DATA = {
    "eventType": "Download",
    "movie": {
        "id": 1,
        "title": "The Matrix",
        "year": 1999,
        "path": "/movies/The Matrix (1999)",
        "tmdbId": 603,
        "quality": "Bluray-1080p",
        "size": 8192,
        "images": [
            {
                "coverType": "poster",
                "remoteUrl": "https://image.tmdb.org/t/p/original/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
            }
        ]
    },
    "isUpgrade": False,
    "downloadClient": "qBittorrent"
}

# Sample Kapowarr webhook data
KAPOWARR_WEBHOOK_DATA = {
    "result": [
        {
            "web_title": "Amazing Spider-Man #1",
            "web_link": "https://comicsite.com/spider-man-1",
            "source": "Marvel Comics",
            "downloaded_at": "2024-01-15T14:30:00Z",
            "file_size": "25.6 MB",
            "quality": "HD"
        }
    ]
}

# Sample server monitoring API response
SERVER_STATUS_DATA = {
    "status": "online",
    "uptime": 86400,
    "memory_usage": 68.5,
    "disk_usage": 45.2,
    "cpu_usage": 23.1,
    "services": {
        "nginx": "running",
        "database": "running",
        "redis": "running"
    },
    "last_backup": "2024-01-15T02:00:00Z"
}

# Sample GitHub API response
GITHUB_RELEASE_DATA = {
    "url": "https://api.github.com/repos/user/repo/releases/123",
    "id": 123,
    "tag_name": "v2.1.0",
    "name": "Version 2.1.0 - Bug Fixes and Improvements",
    "body": "## Changes\n- Fixed memory leak in data processing\n- Improved error handling\n- Added new configuration options",
    "created_at": "2024-01-15T12:00:00Z",
    "published_at": "2024-01-15T12:30:00Z",
    "author": {
        "login": "developer",
        "avatar_url": "https://github.com/developer.png"
    }
}

# Sample notification logs
SAMPLE_NOTIFICATION_LOGS = [
    {
        "timestamp": "2024-01-15 14:30:00",
        "flow_name": "Sonarr Downloads",
        "message_content": "🎬 **Breaking Bad** - Pilot\n📺 Episode: S01E01",
        "embed_info": {
            "title": "New Episode Downloaded",
            "description": "**Breaking Bad** - Pilot",
            "color": 65280
        },
        "webhook_name": "Sonarr",
        "type": "sent",
        "category": "Notifications"
    },
    {
        "timestamp": "2024-01-15 14:25:00",
        "flow_name": "Server Monitoring",
        "message_content": "🖥️ Server Status: online\n💾 Memory: 68.5%\n💽 Disk: 45.2%",
        "embed_info": None,
        "webhook_name": "",
        "type": "sent",
        "category": "Notifications"
    }
]

# Sample general logs
SAMPLE_LOGS = [
    {
        "timestamp": "2024-01-15 14:30:15",
        "message": "✅ Notification sent for flow 'Sonarr Downloads'",
        "category": "Notifications"
    },
    {
        "timestamp": "2024-01-15 14:25:30",
        "message": "🔄 Change detected for 'Server Monitoring': status changed from 'maintenance' to 'online'",
        "category": "Change Detection"
    },
    {
        "timestamp": "2024-01-15 14:20:00",
        "message": "⏰ Timer triggered for flow 'Server Monitoring'",
        "category": "Timers"
    },
    {
        "timestamp": "2024-01-15 14:15:45",
        "message": "🌐 Incoming webhook for flow 'Sonarr Downloads'",
        "category": "Webhooks"
    },
    {
        "timestamp": "2024-01-15 14:10:00",
        "message": "❌ Failed to send notification: Webhook URL not configured",
        "category": "Errors"
    },
    {
        "timestamp": "2024-01-15 14:05:00",
        "message": "🧪 Test notification sent for flow 'GitHub Releases'",
        "category": "Testing"
    }
]

# Sample embed configurations
SAMPLE_EMBED_CONFIGS = {
    "basic": {
        "enabled": True,
        "title": "Basic Notification",
        "description": "This is a basic notification",
        "color": "#3498db",
        "timestamp": True
    },
    "advanced": {
        "enabled": True,
        "title": "{title} - {status}",
        "description": "Server: {server_name}\nStatus: {status}\nUptime: {uptime} seconds",
        "color": "#00ff00",
        "timestamp": True,
        "footer_text": "Automated Notification",
        "footer_icon": "https://example.com/icon.png",
        "author_name": "System Monitor",
        "author_icon": "https://example.com/system.png",
        "thumbnail_url": "https://example.com/thumb.png",
        "fields": [
            {
                "name": "Memory Usage",
                "value": "{memory_usage}%",
                "inline": True
            },
            {
                "name": "Disk Usage",
                "value": "{disk_usage}%",
                "inline": True
            }
        ]
    },
    "media": {
        "enabled": True,
        "title": "New {type} Downloaded",
        "description": "**{title}** ({year})\n\nQuality: {quality}\nSize: {size}MB",
        "color": "#e74c3c",
        "timestamp": True,
        "thumbnail_url": "{poster_url}",
        "fields": [
            {
                "name": "Download Client",
                "value": "{download_client}",
                "inline": True
            },
            {
                "name": "Category",
                "value": "{category}",
                "inline": True
            }
        ]
    }
}

# Sample condition test data
CONDITION_TEST_DATA = [
    {
        "condition": "status == 'online'",
        "data": {"status": "online", "uptime": 3600},
        "expected": True
    },
    {
        "condition": "memory_usage > 80",
        "data": {"memory_usage": 85.5, "status": "warning"},
        "expected": True
    },
    {
        "condition": "episode['quality'] != 'SDTV'",
        "data": {"episode": {"quality": "HDTV-720p", "title": "Pilot"}},
        "expected": True
    },
    {
        "condition": "len(services) >= 3",
        "data": {"services": ["nginx", "mysql", "redis", "app"]},
        "expected": True
    },
    {
        "condition": "disk_usage < 90 and memory_usage < 85",
        "data": {"disk_usage": 75.2, "memory_usage": 80.1},
        "expected": True
    }
]

# Sample template test data
TEMPLATE_TEST_DATA = [
    {
        "template": "Hello {name}!",
        "data": {"name": "World"},
        "user_vars": {},
        "expected": "Hello World!"
    },
    {
        "template": "Server {$server_name} is {status}",
        "data": {"status": "online"},
        "user_vars": {"server_name": "Production"},
        "expected": "Server Production is online"
    },
    {
        "template": "Memory usage: {memory_usage:.1f}%",
        "data": {"memory_usage": 68.567},
        "user_vars": {},
        "expected": "Memory usage: 68.6%"
    },
    {
        "template": "Episode: S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}",
        "data": {"episode": {"seasonNumber": 1, "episodeNumber": 5}},
        "user_vars": {},
        "expected": "Episode: S01E05"
    },
    {
        "template": "Calculation: {calc:memory_usage + disk_usage}%",
        "data": {"memory_usage": 50, "disk_usage": 30},
        "user_vars": {},
        "expected": "Calculation: 80%"
    }
]

# Sample API response for testing
SAMPLE_API_RESPONSES = {
    "status": {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "total_flows": 3,
        "active_flows": 2,
        "version": "1.0.0"
    },
    "health": {
        "status": "healthy",
        "uptime": 86400,
        "memory_usage": 68.5,
        "last_check": datetime.now().isoformat()
    },
    "flows": {
        "flows": SAMPLE_CONFIG["notification_flows"],
        "count": len(SAMPLE_CONFIG["notification_flows"])
    }
}

# Sample error scenarios for testing
ERROR_SCENARIOS = {
    "invalid_webhook_url": {
        "flow": {
            "name": "Invalid Webhook Test",
            "webhook_url": "not-a-valid-url",
            "message_template": "Test message"
        },
        "expected_error": "Invalid webhook URL"
    },
    "malformed_json": {
        "data": '{"invalid": json}',
        "expected_error": "JSON decode error"
    },
    "missing_template_var": {
        "template": "Hello {missing_var}!",
        "data": {"other_var": "value"},
        "expected_error": "Template variable not found"
    }
}

# Performance test data
PERFORMANCE_TEST_DATA = {
    "large_dataset": {
        "data": {f"item_{i}": f"value_{i}" for i in range(1000)},
        "template": "Processing {item_count} items",
        "user_vars": {"item_count": 1000}
    },
    "complex_nested": {
        "data": {
            "level1": {
                "level2": {
                    "level3": {
                        "items": [{"id": i, "name": f"item_{i}"} for i in range(100)]
                    }
                }
            }
        },
        "template": "Found {level1['level2']['level3']['items'][0]['name']}"
    }
}