---
layout: default
title: Configuration
nav_order: 3
---

# Configuration & Deployment
{: .no_toc }

Complete guide for configuring and deploying Turtifications in production environments.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Configuration Overview

Turtifications can be configured through multiple methods:

1. **Web Interface** - Basic configuration through the `/configure` page
2. **Configuration File** - Advanced settings via `config.json`
3. **Environment Variables** - System-level configuration
4. **Command Line Arguments** - Runtime configuration

---

## Environment Variables

### Basic Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `FLASK_DEBUG` | Enable debug mode | `False` | `true` |
| `FLASK_HOST` | Host to bind to | `0.0.0.0` | `127.0.0.1` |
| `FLASK_PORT` | Port to listen on | `5000` | `8080` |
| `DATA_DIR` | Data directory path | `./data` | `/app/data` |

### Advanced Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CONFIG_FILE` | Config file path | `data/config.json` | `/etc/turtifications/config.json` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `LOG_FILE` | Log file path | `data/app.log` | `/var/log/turtifications.log` |
| `SECRET_KEY` | Flask secret key | Auto-generated | `your-secret-key` |

### Security Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ALLOWED_HOSTS` | Allowed host headers | `*` | `localhost,yourdomain.com` |
| `WEBHOOK_SECRET` | Global webhook secret | None | `webhook-secret-key` |
| `API_RATE_LIMIT` | API rate limit | None | `100/hour` |

### Example Environment Setup

```bash
# .env file
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DATA_DIR=/app/data
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=localhost,yourdomain.com
```

---

## Configuration File

The main configuration is stored in `config.json` (by default in the `data` directory).

### Configuration Structure

```json
{
  "discord_webhook": "https://discord.com/api/webhooks/...",
  "notification_flows": [
    {
      "name": "Example Flow",
      "trigger_type": "timer",
      "active": true,
      "url": "https://api.example.com/status",
      "check_interval": 300,
      "timeout": 30,
      "message_template": "Status: {result['status']}",
      "embed_config": {
        "enabled": true,
        "title": "Status Update",
        "color": "#00ff00"
      },
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}",
        "User-Agent": "Turtifications/1.0"
      },
      "condition_enabled": false,
      "condition": "",
      "last_check": "2024-01-15T14:30:00.000Z",
      "last_value": null,
      "execution_count": 0,
      "success_count": 0,
      "failure_count": 0
    }
  ],
  "settings": {
    "check_interval": 60,
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Turtifications/1.0",
    "webhook_timeout": 10,
    "max_webhook_payload_size": 1048576,
    "enable_logging": true,
    "log_retention_days": 30
  },
  "ui_settings": {
    "theme": "dark",
    "timezone": "UTC",
    "date_format": "YYYY-MM-DD HH:mm:ss",
    "items_per_page": 20
  },
  "total_notifications_sent": 0,
  "app_version": "1.0.0"
}
```

### Configuration Sections

#### Discord Settings

```json
{
  "discord_webhook": "https://discord.com/api/webhooks/123456789/abcdef...",
  "discord_settings": {
    "default_username": "Turtifications",
    "default_avatar": "https://example.com/avatar.png",
    "embed_color": "#0066cc",
    "timeout": 10,
    "retry_attempts": 3
  }
}
```

#### Flow Settings

```json
{
  "settings": {
    "check_interval": 60,
    "max_retries": 3,
    "timeout": 30,
    "concurrent_checks": 5,
    "rate_limit_per_minute": 60,
    "enable_change_detection": true,
    "change_detection_precision": 0.001
  }
}
```

#### Security Settings

```json
{
  "security": {
    "webhook_secret": "your-webhook-secret",
    "allowed_origins": ["https://yourdomain.com"],
    "csrf_protection": true,
    "secure_headers": true,
    "api_key_required": false
  }
}
```

---

## Production Deployment

### Using Gunicorn (Recommended)

Gunicorn is a production-grade WSGI server perfect for running Turtifications.

#### Installation

```bash
pip install gunicorn
```

#### Basic Configuration

```bash
# Basic command
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With configuration file
gunicorn -c gunicorn.conf.py app:app
```

#### Gunicorn Configuration File

Create `gunicorn.conf.py`:

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "turtifications"

# Logging
accesslog = "/var/log/turtifications/access.log"
errorlog = "/var/log/turtifications/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process
daemon = False
pidfile = "/var/run/turtifications.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
```

### Systemd Service

Create a systemd service for automatic startup and management.

#### Service File

Create `/etc/systemd/system/turtifications.service`:

```ini
[Unit]
Description=Turtifications Discord Notification System
After=network.target
Wants=network.target

[Service]
Type=notify
User=turtifications
Group=turtifications
WorkingDirectory=/opt/turtifications
Environment=PATH=/opt/turtifications/venv/bin
Environment=FLASK_DEBUG=false
Environment=DATA_DIR=/opt/turtifications/data
EnvironmentFile=-/etc/turtifications/environment
ExecStart=/opt/turtifications/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Environment File

Create `/etc/turtifications/environment`:

```bash
# Turtifications Environment Configuration
SECRET_KEY=your-super-secret-key-here
DISCORD_WEBHOOK=https://discord.com/api/webhooks/your/webhook
LOG_LEVEL=INFO
```

#### Service Management

```bash
# Create user and directories
sudo useradd -r -s /bin/false turtifications
sudo mkdir -p /opt/turtifications/data
sudo chown -R turtifications:turtifications /opt/turtifications

# Enable and start service
sudo systemctl enable turtifications
sudo systemctl start turtifications
sudo systemctl status turtifications

# View logs
sudo journalctl -u turtifications -f
```

---

## Reverse Proxy Configuration

### Nginx

Nginx provides SSL termination, load balancing, and static file serving.

#### Basic Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Proxy to Turtifications
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API Webhook endpoints
    location /api/webhook/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increased limits for webhook payloads
        client_max_body_size 10M;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files (if serving from nginx)
    location /static/ {
        alias /opt/turtifications/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/turtifications_access.log;
    error_log /var/log/nginx/turtifications_error.log;
}
```

#### Load Balancing

For high availability, configure multiple Turtifications instances:

```nginx
upstream turtifications {
    server 127.0.0.1:5000 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:5001 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:5002 weight=1 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    location / {
        proxy_pass http://turtifications;
        # ... other proxy settings
    }
}
```

### Apache

Alternative reverse proxy configuration using Apache.

```apache
<VirtualHost *:443>
    ServerName yourdomain.com
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/yourdomain.com.crt
    SSLCertificateKeyFile /etc/ssl/private/yourdomain.com.key
    
    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # Headers
    ProxyPassReverse / http://127.0.0.1:5000/
    ProxySetHeader X-Forwarded-Proto https
    ProxySetHeader X-Forwarded-For %{REMOTE_ADDR}s
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/turtifications_error.log
    CustomLog ${APACHE_LOG_DIR}/turtifications_access.log combined
</VirtualHost>
```

---

## Docker Deployment

### Basic Docker Setup

#### Dockerfile

The project includes a Dockerfile. Build and run:

```bash
# Build image
docker build -t turtifications .

# Run container
docker run -d \
  --name turtifications \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e FLASK_DEBUG=false \
  turtifications
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  turtifications:
    build: .
    container_name: turtifications
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_DEBUG=false
      - DATA_DIR=/app/data
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
    networks:
      - turtifications_network

  nginx:
    image: nginx:alpine
    container_name: turtifications_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
    depends_on:
      - turtifications
    networks:
      - turtifications_network

networks:
  turtifications_network:
    driver: bridge
```

#### Production Docker Compose

```yaml
version: '3.8'

services:
  turtifications:
    image: turtifications:latest
    restart: unless-stopped
    environment:
      - FLASK_DEBUG=false
      - DATA_DIR=/app/data
      - SECRET_KEY_FILE=/run/secrets/secret_key
    volumes:
      - turtifications_data:/app/data
      - /var/log/turtifications:/app/logs
    secrets:
      - secret_key
    networks:
      - internal
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx:/etc/nginx/conf.d:ro
      - certbot_certs:/etc/letsencrypt:ro
    depends_on:
      - turtifications
    networks:
      - internal
      - external

volumes:
  turtifications_data:
  certbot_certs:

networks:
  internal:
    driver: overlay
  external:
    driver: overlay

secrets:
  secret_key:
    external: true
```

---

## Database Configuration

### SQLite (Default)

Turtifications uses file-based storage by default, but you can configure SQLite for better performance:

```python
# config.py addition
import sqlite3
import os

DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/turtifications.db')

def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    # Initialize tables
    conn.close()
```

### External Database Support

For large deployments, consider external databases:

#### PostgreSQL

```bash
# Environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/turtifications"
export DATABASE_POOL_SIZE=20
```

#### Redis for Caching

```bash
# Environment variables
export REDIS_URL="redis://localhost:6379/0"
export CACHE_TYPE="redis"
```

---

## Monitoring & Logging

### Application Logging

Configure structured logging:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "/var/log/turtifications/app.log",
    "max_size": "100MB",
    "backup_count": 5,
    "structured": true
  }
}
```

### Health Checks

Configure health check endpoints:

```bash
# Health check script
#!/bin/bash
curl -f http://localhost:5000/api/health || exit 1
```

### Monitoring Integration

#### Prometheus Metrics

Add to configuration:

```json
{
  "monitoring": {
    "prometheus_enabled": true,
    "metrics_endpoint": "/metrics",
    "collect_system_metrics": true
  }
}
```

#### Grafana Dashboard

Import the provided Grafana dashboard for monitoring:
- Application metrics
- Flow statistics  
- Error rates
- Response times

---

## Security Hardening

### Basic Security

1. **Change default secret key**
2. **Use HTTPS in production**
3. **Implement rate limiting**
4. **Validate webhook sources**
5. **Regular security updates**

### Advanced Security

#### API Authentication

```python
# Add to configuration
API_KEY_REQUIRED = True
VALID_API_KEYS = ["your-api-key-1", "your-api-key-2"]
```

#### Webhook Security

```python
# Webhook signature validation
WEBHOOK_SECRET = "your-webhook-secret"
VALIDATE_WEBHOOK_SIGNATURES = True
```

#### Content Security Policy

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'";
```

---

## Backup & Recovery

### Data Backup

```bash
#!/bin/bash
# backup.sh - Backup script

BACKUP_DIR="/backup/turtifications"
DATA_DIR="/app/data"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration and data
tar -czf "$BACKUP_DIR/turtifications_backup_$DATE.tar.gz" \
    -C "$DATA_DIR" \
    config.json \
    logs/ \
    *.db

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /opt/turtifications/backup.sh
```

### Recovery Procedure

```bash
#!/bin/bash
# restore.sh - Restore script

BACKUP_FILE="$1"
DATA_DIR="/app/data"

# Stop service
systemctl stop turtifications

# Backup current data
mv "$DATA_DIR" "$DATA_DIR.backup.$(date +%s)"

# Restore from backup
mkdir -p "$DATA_DIR"
tar -xzf "$BACKUP_FILE" -C "$DATA_DIR"

# Set permissions
chown -R turtifications:turtifications "$DATA_DIR"

# Start service
systemctl start turtifications
```

---

## Performance Tuning

### Application Performance

```json
{
  "performance": {
    "worker_timeout": 30,
    "max_concurrent_flows": 10,
    "request_timeout": 60,
    "cache_enabled": true,
    "cache_ttl": 300
  }
}
```

### System Requirements

| Deployment Type | CPU | Memory | Storage | Network |
|----------------|-----|--------|---------|---------|
| Small (1-10 flows) | 1 core | 512MB | 1GB | 1Mbps |
| Medium (10-50 flows) | 2 cores | 1GB | 5GB | 5Mbps |
| Large (50+ flows) | 4+ cores | 2GB+ | 20GB+ | 10Mbps+ |

---

## Troubleshooting

### Common Configuration Issues

**Service won't start**
: Check systemd logs: `journalctl -u turtifications -f`

**High memory usage**  
: Reduce concurrent flows or increase system memory

**Slow response times**
: Check nginx/proxy configuration and network latency

**Database locks**
: Ensure proper file permissions and disk space

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting).

---

## Next Steps

- Set up [monitoring and alerting](troubleshooting#monitoring)
- Configure [backup automation](#backup--recovery)
- Implement [security hardening](#security-hardening)
- Scale for [high availability](#load-balancing)