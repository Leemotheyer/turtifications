---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started with Turtifications
{: .no_toc }

This guide will help you install, configure, and start using Turtifications to create powerful Discord notification flows.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Prerequisites

Before installing Turtifications, ensure you have:

- **Python 3.7+** installed on your system
- **Discord webhook URL** for sending notifications
- Basic familiarity with command line/terminal

### Getting a Discord Webhook URL

1. Open Discord and navigate to your server
2. Go to **Server Settings** → **Integrations** → **Webhooks**
3. Click **Create Webhook**
4. Set a name and channel for your webhook
5. Copy the **Webhook URL** - you'll need this for configuration

---

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/turtifications.git
cd turtifications

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Method 2: Download Release

1. Download the latest release from the [GitHub releases page](https://github.com/yourusername/turtifications/releases)
2. Extract the archive
3. Navigate to the extracted directory
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`

### Method 3: Docker

```bash
# Build and run with Docker
docker build -t turtifications .
docker run -p 5000:5000 -v $(pwd)/data:/app/data turtifications
```

---

## First Time Setup

### 1. Start the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 2. Configure Discord Webhook

1. Open your browser and navigate to `http://localhost:5000`
2. Click on **Configure** in the navigation menu
3. Enter your Discord webhook URL
4. Click **Save Configuration**

### 3. Test Your Setup

1. Go to the **Configure** page
2. Click **Send Test Message**
3. Check your Discord channel for the test notification

If you see the test message, congratulations! Your setup is working correctly.

---

## Creating Your First Flow

Let's create a simple notification flow to get you started:

### 1. Use a Template

1. Navigate to **Templates** in the main menu
2. Choose a template that matches your use case (e.g., "System Monitor")
3. Click **Use Template**
4. The flow builder will open with pre-configured settings

### 2. Customize the Flow

1. **Name**: Give your flow a descriptive name
2. **Trigger**: Choose when the notification should be sent
3. **Message**: Customize the notification message
4. **Test**: Click **Test Flow** to preview the notification

### 3. Save and Activate

1. Click **Save Flow**
2. Toggle the **Active** switch to start monitoring

---

## Environment Configuration

### Environment Variables

You can configure Turtifications using environment variables:

```bash
# Set debug mode
export FLASK_DEBUG=true

# Set custom port
export FLASK_PORT=8080

# Set data directory
export DATA_DIR=/path/to/data
```

### Configuration File

The application creates a `config.json` file in the data directory. You can manually edit this file:

```json
{
  "discord_webhook": "https://discord.com/api/webhooks/...",
  "notification_flows": [],
  "settings": {
    "check_interval": 60,
    "max_retries": 3,
    "timeout": 30
  }
}
```

---

## Production Deployment

### Using Gunicorn

For production deployment, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using systemd (Linux)

Create a systemd service file:

```ini
# /etc/systemd/system/turtifications.service
[Unit]
Description=Turtifications Discord Notification System
After=network.target

[Service]
Type=notify
User=turtifications
Group=turtifications
WorkingDirectory=/opt/turtifications
Environment=PATH=/opt/turtifications/venv/bin
ExecStart=/opt/turtifications/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable turtifications
sudo systemctl start turtifications
```

### Reverse Proxy with Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Next Steps

Now that you have Turtifications running:

1. **Explore Templates**: Check out the [Templates Guide](guides/templates) for pre-built flows
2. **Create Custom Flows**: Learn to build your own flows in the [Notification Flows Guide](guides/notification-flows)
3. **Use the API**: Integrate with external tools using the [API Guide](guides/api)
4. **Configure Advanced Features**: Set up webhooks, conditions, and monitoring

---

## Troubleshooting

### Common Issues

**Application won't start**
: Check that Python 3.7+ is installed and all dependencies are available

**Discord notifications not working**
: Verify your webhook URL is correct and the webhook hasn't been deleted

**Flows not triggering**
: Check that flows are marked as "Active" and URLs are accessible

For more help, see the [Troubleshooting Guide](troubleshooting) or [open an issue](https://github.com/yourusername/turtifications/issues) on GitHub.