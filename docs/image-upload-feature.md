# Discord Image Upload Feature

This feature allows you to include images from local services in Discord notifications by automatically downloading and uploading them as attachments.

## Overview

Previously, Discord notifications could only include images that were publicly accessible on the internet. Local services (like monitoring dashboards, internal analytics tools, etc.) couldn't be referenced directly because Discord cannot access private networks.

This feature solves this problem by:
1. Detecting special `{img:url}` patterns in message templates
2. Downloading images from local URLs
3. Uploading them as file attachments to Discord
4. Automatically cleaning up temporary files

## Syntax

Use the `{img:url}` pattern in your message templates:

```
{img:http://localhost:8080/status.png}
```

### Examples

#### Basic Usage
```
Message: "Server status update! {img:http://localhost:3000/dashboard.png}"
```

#### Multiple Images
```
Message: "Report complete! Charts: {img:http://localhost:3000/chart1.png} and {img:http://localhost:3000/chart2.png}"
```

#### Dynamic URLs with Variables
```
Message: "Build #{build_id} completed! Screenshot: {img:http://localhost:9000/screenshots/{build_id}.png}"
Data: {"build_id": "123"}
Result: Downloads from http://localhost:9000/screenshots/123.png
```

## Configuration

### Notification Flow Setup

Add image patterns to your notification flow's `message_template`:

```json
{
  "name": "Build Status",
  "trigger_type": "on_change",
  "endpoint": "http://localhost:8080/api/build-status",
  "field": "status",
  "message_template": "Build {build_id} finished with status: {status}! {img:http://localhost:8080/screenshots/{build_id}.png}",
  "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
}
```

### With Embeds

Images work alongside Discord embeds:

```json
{
  "message_template": "Build completed! {img:http://localhost:8080/build-screenshot.png}",
  "embed_config": {
    "enabled": true,
    "title": "Build Report",
    "description": "Automated build completed successfully",
    "color": "#00ff00"
  }
}
```

## Technical Details

### Image Processing Flow

1. **Pattern Detection**: The system scans message templates for `{img:url}` patterns
2. **Variable Substitution**: URLs are processed for variable replacement (e.g., `{build_id}`)
3. **Download**: Images are downloaded to temporary files with appropriate extensions
4. **Upload**: Discord webhook receives both the message and file attachments
5. **Cleanup**: Temporary files are automatically removed

### Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)

### Error Handling

- **Download Failures**: Logged but don't prevent message sending
- **Invalid URLs**: Skipped with warning logs
- **Network Timeouts**: 10-second timeout for downloads
- **Cleanup Failures**: Logged but don't affect functionality

### File Management

- **Temporary Storage**: Images are stored in system temp directory
- **Unique Names**: Each download gets a unique temporary filename
- **Automatic Cleanup**: Files are removed after Discord upload (success or failure)
- **Concurrent Safe**: Multiple notifications can process images simultaneously

## Limitations

### Size Limits

- Discord file attachment limit: 8MB per file (25MB with Nitro)
- No built-in image resizing - ensure your images are appropriately sized

### Performance Considerations

- **Download Time**: Large images may increase notification delay
- **Concurrent Downloads**: Multiple images in one message are downloaded sequentially
- **Timeout**: 10-second download timeout per image

### Network Requirements

- **Local Access**: The notification service must be able to access the image URLs
- **Content-Type**: Services should return proper `image/*` content types (warning if not)

## Troubleshooting

### Common Issues

1. **Images not appearing**: Check if URLs are accessible from the notification service
2. **Download timeouts**: Verify image service response time and size
3. **Format errors**: Ensure images are in supported formats

### Logs

Image processing is logged with these prefixes:
- `📥` Download successful
- `❌` Download failed
- `🗑️` File cleanup
- `⚠️` Cleanup warnings

### Testing

Use the image test utilities:

```bash
python3 test/test_image_utils.py
```

Or run the demonstration:

```bash
python3 example_image_usage.py
```

## Migration from Existing Setups

### Before (Public Images Only)
```json
{
  "message_template": "Status: {status}",
  "embed_config": {
    "image_url": "https://public-server.com/image.png"
  }
}
```

### After (Local Images Supported)
```json
{
  "message_template": "Status: {status} {img:http://localhost:8080/status.png}",
  "embed_config": {
    "title": "Status Update"
  }
}
```

## Use Cases

### Monitoring Dashboards
```
Message: "Alert triggered! {img:http://grafana:3000/render/d/dashboard?width=800&height=400}"
```

### Build Systems
```
Message: "Build #{build_id} completed! Test coverage: {img:http://jenkins:8080/job/build-{build_id}/coverage.png}"
```

### Analytics Reports
```
Message: "Daily report ready! {img:http://analytics:5000/reports/daily/{date}.png}"
```

### Security Cameras
```
Message: "Motion detected! {img:http://camera-system:8080/snapshot/{camera_id}.jpg}"
```

## API Reference

### Template Function

```python
format_message_template(template, data, user_variables=None, extract_images=False)
```

**Returns:**
- If `extract_images=False`: formatted string
- If `extract_images=True`: tuple of (formatted_string, image_urls_list)

### Image Utilities

```python
from functions.image_utils import download_image_to_temp, cleanup_temp_files

# Download image
temp_path = download_image_to_temp("http://localhost:8080/image.png")

# Cleanup
cleanup_temp_files([temp_path])
```

## Security Considerations

- **Local Network Access**: Images are downloaded from URLs accessible to the notification service
- **No Authentication**: Currently no support for authenticated image endpoints
- **Temporary Files**: Images are temporarily stored on disk during processing
- **URL Validation**: Basic validation but no content scanning

For production deployments, consider:
- Network segmentation for image services
- Regular temp directory cleanup monitoring
- Image service access controls