# 🚀 turtifications

A powerful Discord notification system built with Flask that monitors APIs, detects changes, and sends rich notifications with embeds.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)

## ✨ Features

- **Multiple Triggers**: Timer-based, change detection, and webhook triggers
- **Rich Discord Notifications**: Message templates with variable substitution and Discord embeds
- **Local Image Upload**: Automatically upload images from local services as Discord attachments
- **Flow Templates**: Pre-built templates for Sonarr, Radarr, Kapowarr, and more
- **Real-time Preview**: Preview notifications with real API data
- **Statistics & Monitoring**: Track usage, success rates, and activity history
- **REST API**: Full API for external integrations
- **Import/Export**: Backup and restore flow configurations

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Discord webhook URL

### Installation

```bash
git clone https://github.com/yourusername/notification-organizer.git
cd notification-organizer
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` and configure your Discord webhook in the "Configure" page.

## 🖼️ Local Image Upload

The system automatically detects when embed images point to local services (localhost, private IPs, internal hostnames) and uploads them as Discord attachments instead of broken links. This works transparently with:

- Main embed images (`image_url`)
- Thumbnails (`thumbnail_url`) 
- Footer icons (`footer_icon`)
- Author icons (`author_icon`)

No configuration required - just use your local image URLs in embed configurations and they'll be automatically uploaded!

See the [Local Images Guide](docs/guides/local-images.md) for detailed documentation.

## 📖 Usage

### Creating a Flow

1. Go to "Builder" or use a template from "Templates"
2. Configure trigger type (Timer/Change Detection/Webhook)
3. Set up message template with variables
4. Optionally enable Discord embeds
5. Test and save

### Template Variables

```javascript
{time}                    // Current timestamp
{value}                   // Current field value
{old_value}              // Previous value (change detection)
{result['downloaded_issues']}  // API data access
{result['0']['web_title']}     // Array access
```

### Flow Templates

- **Sonarr/Radarr**: Download notifications
- **Kapowarr**: Comic download notifications
- **System Monitor**: Resource monitoring
- **Website Monitor**: Availability checks
- **Daily Summary**: Periodic reports

## 🔌 API

The app provides a REST API for external integrations:

```bash
# Get app status
curl http://localhost:5000/api/status

# Get statistics
curl http://localhost:5000/api/statistics

# Send test notification
curl -X POST http://localhost:5000/api/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from API!"}'
```

Visit `http://localhost:5000/api/docs` for complete API documentation.

## 🚀 Deployment

### Production
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```bash
# Build and run with Docker
docker build -t turtifications .
docker run -p 5000:5000 -v $(pwd)/data:/app/data turtifications
```