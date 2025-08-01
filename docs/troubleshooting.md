---
layout: default
title: Troubleshooting
nav_order: 4
---

# Troubleshooting Guide
{: .no_toc }

Common issues, solutions, and debugging techniques for Turtifications.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Installation Issues

### Application Won't Start

**Symptoms:**
- Command `python app.py` fails
- ImportError or ModuleNotFoundError
- Permission denied errors

**Solutions:**

1. **Check Python Version**
   ```bash
   python --version  # Should be 3.7+
   python3 --version
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   # or if using Python 3 specifically
   pip3 install -r requirements.txt
   ```

3. **Check File Permissions**
   ```bash
   chmod +x app.py
   chmod -R 755 .
   ```

4. **Virtual Environment Issues**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

### Port Already in Use

**Symptoms:**
- Error: "Address already in use"
- Cannot access web interface

**Solutions:**

1. **Find Process Using Port**
   ```bash
   # Linux/Mac
   lsof -i :5000
   netstat -tulpn | grep :5000
   
   # Windows
   netstat -ano | findstr :5000
   ```

2. **Kill Process or Use Different Port**
   ```bash
   # Kill process (Linux/Mac)
   kill -9 <PID>
   
   # Use different port
   export FLASK_PORT=8080
   python app.py
   ```

---

## Configuration Issues

### Discord Webhook Not Working

**Symptoms:**
- Test notifications don't appear in Discord
- Error: "Failed to send notification"
- Webhook URL invalid errors

**Debugging Steps:**

1. **Verify Webhook URL**
   ```bash
   # Test webhook manually
   curl -X POST "YOUR_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"content": "Test message"}'
   ```

2. **Check Discord Channel**
   - Ensure webhook wasn't deleted
   - Verify channel permissions
   - Check if channel still exists

3. **Validate URL Format**
   ```
   Correct format:
   https://discord.com/api/webhooks/123456789012345678/AbCdEfGhIjKlMnOpQrStUvWxYz...
   
   Common mistakes:
   - Missing /api/ in URL
   - Extra spaces or characters
   - Truncated webhook token
   ```

4. **Test in Application**
   - Go to Configure page
   - Click "Send Test Message"
   - Check browser console for errors

### Flows Not Triggering

**Symptoms:**
- Flows appear active but don't send notifications
- No logs showing execution
- "Last Check" time not updating

**Debugging Steps:**

1. **Check Flow Status**
   ```
   - Ensure flow is marked as "Active"
   - Verify trigger type is correct
   - Check check interval setting
   ```

2. **Test API Endpoint Manually**
   ```bash
   curl -v "YOUR_API_ENDPOINT"
   # Check for:
   # - HTTP status code
   # - Response format
   # - Authentication requirements
   ```

3. **Review Flow Configuration**
   ```yaml
   Common Issues:
   - Incorrect URL format
   - Missing authentication headers
   - Wrong field path for change detection
   - Invalid conditions
   ```

4. **Check Application Logs**
   ```bash
   # View recent logs
   tail -f data/app.log
   
   # Or through web interface
   # Go to Logs page in application
   ```

### Template Variables Not Working

**Symptoms:**
- Variables show as empty: `{result['field']}`
- Error: "KeyError" in logs
- Malformed notification messages

**Solutions:**

1. **Use Preview Feature**
   - Test your template with real API data
   - Verify variable paths are correct
   - Check data structure

2. **Debug API Response**
   ```bash
   # Get raw API response
   curl "YOUR_API_ENDPOINT" | jq '.'
   
   # Check if field exists
   curl "YOUR_API_ENDPOINT" | jq '.field_name'
   ```

3. **Common Variable Path Issues**
   ```yaml
   # Incorrect
   {result.field}           # Use brackets, not dots
   {result['field']['sub']} # Check nesting level
   
   # Correct
   {result['field']}
   {result['nested']['field']}
   {result['array']['0']['field']}
   ```

4. **Handle Missing Fields**
   ```yaml
   # Use conditional logic
   {#if result['field']}
   Field value: {result['field']}
   {#else}
   Field not available
   {#endif}
   ```

---

## Runtime Issues

### High Memory Usage

**Symptoms:**
- System becomes slow
- Out of memory errors
- Application crashes

**Diagnosis:**

1. **Check Memory Usage**
   ```bash
   # Linux
   ps aux | grep python
   top -p $(pgrep -f app.py)
   
   # Memory details
   cat /proc/$(pgrep -f app.py)/status | grep VmRSS
   ```

2. **Monitor Flow Statistics**
   - Check number of active flows
   - Review check intervals
   - Look for memory leaks in logs

**Solutions:**

1. **Optimize Flow Configuration**
   ```yaml
   # Reduce check frequency
   check_interval: 300  # 5 minutes instead of 1 minute
   
   # Limit concurrent flows
   max_concurrent_flows: 5
   ```

2. **System Configuration**
   ```bash
   # Increase swap space (Linux)
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Application Tuning**
   ```python
   # Add to configuration
   {
     "performance": {
       "max_concurrent_flows": 5,
       "request_timeout": 30,
       "cache_enabled": true
     }
   }
   ```

### Slow Response Times

**Symptoms:**
- Web interface loads slowly
- API calls timeout
- Notification delays

**Diagnosis:**

1. **Check System Resources**
   ```bash
   # CPU usage
   top
   htop
   
   # Disk I/O
   iotop
   iostat -x 1
   
   # Network
   iftop
   netstat -i
   ```

2. **Profile Application**
   ```bash
   # Enable debug mode temporarily
   export FLASK_DEBUG=true
   python app.py
   ```

**Solutions:**

1. **Optimize Flow Intervals**
   ```yaml
   # Stagger check times
   Flow 1: check_interval: 300  # 5 minutes
   Flow 2: check_interval: 420  # 7 minutes  
   Flow 3: check_interval: 600  # 10 minutes
   ```

2. **Use Reverse Proxy**
   ```nginx
   # Add caching to nginx
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   
   location /api/ {
       proxy_cache api_cache;
       proxy_cache_valid 200 5m;
   }
   ```

3. **Database Optimization**
   ```bash
   # Clean up old logs
   # Go to Logs page and click "Clear Old Logs"
   # Or manually delete old log files
   ```

### SSL/HTTPS Issues

**Symptoms:**
- Certificate errors
- Mixed content warnings
- Webhook delivery failures

**Solutions:**

1. **Certificate Verification**
   ```bash
   # Check certificate
   openssl x509 -in certificate.crt -text -noout
   
   # Test SSL connection
   openssl s_client -connect yourdomain.com:443
   ```

2. **Nginx SSL Configuration**
   ```nginx
   # Strong SSL configuration
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
   ssl_prefer_server_ciphers off;
   
   # HSTS
   add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
   ```

3. **Let's Encrypt Setup**
   ```bash
   # Install certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot --nginx -d yourdomain.com
   
   # Auto-renewal
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

---

## Webhook Issues

### Webhooks Not Receiving Data

**Symptoms:**
- External services report webhook failures
- No webhook data in logs
- Webhook flows never trigger

**Debugging Steps:**

1. **Verify Webhook URL**
   ```bash
   # Test accessibility
   curl -X POST "https://yourdomain.com/api/webhook/your-flow" \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

2. **Check Firewall Settings**
   ```bash
   # Linux iptables
   sudo iptables -L
   
   # UFW
   sudo ufw status
   
   # Allow webhook port
   sudo ufw allow 5000
   sudo ufw allow 443
   ```

3. **Review Reverse Proxy Logs**
   ```bash
   # Nginx access logs
   tail -f /var/log/nginx/access.log
   
   # Error logs
   tail -f /var/log/nginx/error.log
   ```

4. **Test with Webhook Tools**
   - Use webhook.site for testing
   - Set up temporary webhook endpoint
   - Verify JSON payload format

### Webhook Security Issues

**Symptoms:**
- Unauthorized webhook calls
- Failed signature validation
- Security warnings in logs

**Solutions:**

1. **Implement Webhook Secrets**
   ```python
   # Add to flow configuration
   {
     "webhook_secret": "your-secret-key",
     "validate_signatures": true
   }
   ```

2. **IP Whitelisting**
   ```nginx
   # Nginx IP restriction for webhooks
   location /api/webhook/ {
       allow 192.168.1.0/24;
       allow 10.0.0.0/8;
       deny all;
       
       proxy_pass http://backend;
   }
   ```

3. **Rate Limiting**
   ```nginx
   # Limit webhook requests
   limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;
   
   location /api/webhook/ {
       limit_req zone=webhook burst=20 nodelay;
       proxy_pass http://backend;
   }
   ```

---

## API Issues

### API Endpoints Not Responding

**Symptoms:**
- 404 errors on API calls
- Timeout errors
- Empty responses

**Diagnosis:**

1. **Check Route Registration**
   ```bash
   # View available routes
   curl http://localhost:5000/api/docs
   
   # Test basic endpoint
   curl http://localhost:5000/api/status
   ```

2. **Verify Flask Configuration**
   ```python
   # Check if API routes are initialized
   # Look for init_api_routes(app) in app.py
   ```

3. **Review Application Logs**
   ```bash
   # Check for route errors
   grep "404\|500" data/app.log
   ```

### Authentication Issues

**Symptoms:**
- Unauthorized access errors
- API key validation failures
- CORS errors

**Solutions:**

1. **CORS Configuration**
   ```python
   # Add CORS headers if needed
   from flask_cors import CORS
   CORS(app)
   ```

2. **API Key Setup**
   ```bash
   # Set API key environment variable
   export API_KEY="your-api-key"
   
   # Use in requests
   curl -H "X-API-Key: your-api-key" http://localhost:5000/api/flows
   ```

---

## Performance Issues

### Database Locks

**Symptoms:**
- "Database is locked" errors
- Slow database operations
- Application hangs

**Solutions:**

1. **Check File Permissions**
   ```bash
   # Ensure proper ownership
   chown -R app:app /app/data/
   chmod 644 /app/data/*.json
   ```

2. **Disk Space**
   ```bash
   # Check available space
   df -h
   
   # Clean up if needed
   # Remove old log files
   find /app/data/logs -name "*.log" -mtime +30 -delete
   ```

3. **Database Optimization**
   ```bash
   # Backup and recreate config
   cp data/config.json data/config.json.backup
   # Restart application to rebuild indexes
   ```

### Memory Leaks

**Symptoms:**
- Gradual memory increase
- Application becomes unresponsive
- System swap usage

**Diagnosis:**

1. **Memory Profiling**
   ```python
   # Add memory monitoring
   import psutil
   import os
   
   process = psutil.Process(os.getpid())
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

2. **Monitor Over Time**
   ```bash
   # Log memory usage
   while true; do
     ps aux | grep python | grep -v grep >> memory_log.txt
     sleep 60
   done
   ```

**Solutions:**

1. **Restart Service Periodically**
   ```bash
   # Add to crontab for weekly restart
   0 2 * * 0 systemctl restart turtifications
   ```

2. **Optimize Flow Configuration**
   ```yaml
   # Reduce memory usage
   settings:
     max_concurrent_flows: 3
     cache_enabled: false
     request_timeout: 30
   ```

---

## Monitoring & Debugging

### Enabling Debug Mode

**Temporary Debug Mode:**
```bash
# Environment variable
export FLASK_DEBUG=true
python app.py

# Or command line
python app.py --debug
```

**Debug Configuration:**
```json
{
  "debug": {
    "enabled": true,
    "log_level": "DEBUG",
    "detailed_errors": true,
    "profile_requests": true
  }
}
```

### Log Analysis

**Viewing Logs:**
```bash
# Live log monitoring
tail -f data/app.log

# Search for errors
grep -i error data/app.log

# Filter by timestamp
grep "2024-01-15" data/app.log

# Count error types
grep -c "ERROR\|WARNING\|INFO" data/app.log
```

**Log Rotation:**
```bash
# Setup logrotate
sudo tee /etc/logrotate.d/turtifications << EOF
/app/data/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    postrotate
        systemctl reload turtifications
    endscript
}
EOF
```

### Health Monitoring

**Health Check Script:**
```bash
#!/bin/bash
# health_check.sh

API_URL="http://localhost:5000/api/health"
WEBHOOK_URL="YOUR_DISCORD_WEBHOOK"

# Check application health
if ! curl -f -s "$API_URL" > /dev/null; then
    # Send alert to Discord
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d '{"content": "🚨 Turtifications health check failed!"}'
    
    # Try to restart service
    systemctl restart turtifications
fi
```

**Automated Monitoring:**
```bash
# Add to crontab
*/5 * * * * /opt/turtifications/health_check.sh
```

---

## Getting Help

### Collecting Debug Information

When reporting issues, include:

1. **System Information**
   ```bash
   # OS version
   uname -a
   cat /etc/os-release
   
   # Python version
   python --version
   
   # Application version
   grep version data/config.json
   ```

2. **Configuration (Sanitized)**
   ```bash
   # Remove sensitive data before sharing
   jq 'del(.discord_webhook, .webhook_secret)' data/config.json
   ```

3. **Recent Logs**
   ```bash
   # Last 100 lines
   tail -100 data/app.log
   
   # Recent errors only
   grep -i error data/app.log | tail -20
   ```

4. **Network Information**
   ```bash
   # Port usage
   netstat -tulpn | grep :5000
   
   # DNS resolution (if using domain)
   nslookup yourdomain.com
   ```

### Support Channels

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/yourusername/turtifications/issues)
- **Discussions**: [Community support and questions](https://github.com/yourusername/turtifications/discussions)
- **Documentation**: [Complete documentation](https://yourusername.github.io/turtifications/)

### Creating a Good Bug Report

Include the following information:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **System information** (OS, Python version, etc.)
5. **Configuration** (sanitized)
6. **Logs** showing the error
7. **Screenshots** if UI-related

**Example Bug Report:**
```markdown
## Bug Description
Webhook notifications are not being received from GitHub

## Steps to Reproduce
1. Configure GitHub webhook with URL: https://myserver.com/api/webhook/github
2. Push code to repository
3. Check Discord channel - no notification received

## Expected Behavior
Should receive notification in Discord with commit details

## System Information
- OS: Ubuntu 20.04
- Python: 3.8.10
- Turtifications: 1.0.0

## Configuration
{
  "name": "GitHub Webhook",
  "trigger_type": "webhook",
  "active": true,
  "message_template": "New commit: {commits[0].message}"
}

## Logs
2024-01-15 14:30:00 - ERROR - No webhook data received for flow 'GitHub Webhook'
```

---

## Prevention Tips

### Regular Maintenance

1. **Update Dependencies**
   ```bash
   # Check for updates
   pip list --outdated
   
   # Update packages
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor Disk Space**
   ```bash
   # Check disk usage
   df -h
   
   # Clean old logs
   find /app/data/logs -name "*.log" -mtime +30 -delete
   ```

3. **Backup Configuration**
   ```bash
   # Daily backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   cp data/config.json "backups/config_$DATE.json"
   ```

### Best Practices

1. **Use version control** for configuration
2. **Test changes** in development environment
3. **Monitor application metrics** regularly
4. **Keep documentation** up to date
5. **Regular security updates**

### Monitoring Checklist

- [ ] Application responding to health checks
- [ ] Disk space above 20% free
- [ ] Memory usage below 80%
- [ ] No critical errors in logs
- [ ] SSL certificate not expiring soon
- [ ] Backup system working
- [ ] All flows executing as expected

---

For issues not covered in this guide, please check the [GitHub Issues](https://github.com/yourusername/turtifications/issues) or create a new issue with detailed information about your problem.