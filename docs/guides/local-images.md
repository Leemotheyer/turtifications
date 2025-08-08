# Local Image Upload for Discord Notifications

This guide explains how the automatic local image upload feature works for Discord notifications.

## Overview

Previously, Discord embeds and messages could only display images from publicly accessible URLs. If your notification system referenced images from local services (localhost, private IPs, internal hostnames), Discord would show broken image links because it couldn't access these URLs.

The new local image upload feature automatically detects when embed images point to local services and uploads them as Discord attachments instead.

## How It Works

### Automatic Detection

The system automatically detects local service URLs by checking for:

- **Localhost addresses**: `localhost`, `127.0.0.1`, `::1`
- **Private IP ranges**: `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`
- **Internal hostnames**: Contains `.local`, `.internal`, `.lan`, `docker`, `container`, etc.
- **Development domains**: Hostnames starting with `dev-`, `test-`, `staging-`
- **Single-word hostnames**: Names without TLDs (like `api`, `server`)

### Image Processing

When a local image URL is detected:

1. **Download**: The image is downloaded from the local service
2. **Validation**: Verify it's a valid image file
3. **Optimization**: Resize if larger than 8MB (Discord's practical limit)
4. **Upload**: Send as Discord attachment using multipart form data
5. **Cleanup**: Remove temporary files after sending

### Supported Image Locations

The feature works with these embed image fields:

- `image_url` - Main embed image
- `thumbnail_url` - Embed thumbnail
- `footer_icon` - Footer icon
- `author_icon` - Author icon

## Configuration

No additional configuration is required. The feature is automatically enabled and works with existing embed configurations.

### Example Embed Configuration

```json
{
  "embed_config": {
    "enabled": true,
    "title": "Server Status",
    "description": "Current server screenshot",
    "image_url": "http://localhost:3000/api/screenshot",
    "thumbnail_url": "http://192.168.1.100:8080/thumbnail",
    "footer_icon": "http://internal-service.local/icon.png"
  }
}
```

All three image URLs in this example would be automatically detected as local services and uploaded as attachments.

## Technical Details

### Attachment References

When local images are detected, the embed URLs are automatically converted to Discord attachment references:

- `http://localhost:3000/api/screenshot` → `attachment://embed_image.png`
- `http://internal-service.local/thumbnail` → `attachment://embed_thumbnail.png`
- `http://192.168.1.100/icon.png` → `attachment://footer_icon.png`

### File Handling

- **Temporary Storage**: Images are temporarily downloaded to the system temp directory
- **Size Limits**: Images larger than 8MB are automatically resized
- **Format Support**: All common image formats (PNG, JPEG, GIF, WebP, etc.)
- **Cleanup**: Temporary files are automatically removed after 24 hours

### Error Handling

If an image fails to download or process:

- The notification still sends without that specific image
- Error details are logged for troubleshooting
- Other images in the same embed continue to work normally

## Performance Considerations

### Download Timeouts

- Image downloads have a 10-second timeout
- Large images may take longer but are automatically resized
- Failed downloads don't block the notification

### Bandwidth Usage

- Only downloads images from local services
- Public URLs continue to work normally (no bandwidth impact)
- Images are only downloaded when notifications are sent

### Storage

- Temporary files are stored in the system temp directory
- Automatic cleanup prevents disk space issues
- Average image size after optimization: 100KB - 2MB

## Testing

Use the provided test script to verify the functionality:

```bash
cd /workspace
python test_image_upload.py
```

This will:

1. Test URL detection logic
2. Create a local test server
3. Send a test notification with local images
4. Verify the upload process works correctly

## Troubleshooting

### Common Issues

**Images still appear broken:**
- Verify the local service is accessible from the notification system
- Check if the image URLs return valid image data
- Review logs for download errors

**Large file upload failures:**
- Images larger than 25MB will fail (Discord limit)
- The system attempts to resize, but very large images may still fail
- Consider optimizing images at the source

**Network connectivity:**
- Ensure the notification system can reach your local services
- Check firewall rules and network configuration
- Verify authentication if required by the image service

### Log Messages

Look for these log entries to monitor the feature:

- `"Downloading image from: {url}"` - Image download started
- `"Successfully downloaded image: {filename}"` - Download completed
- `"Prepared image attachment: {name}"` - Ready for upload
- `"Sending Discord notification with X image attachments"` - Upload in progress

## API Reference

### Functions

#### `is_local_service_url(url)`
Determines if a URL points to a local service.

**Parameters:**
- `url` (str): The URL to check

**Returns:**
- `bool`: True if the URL is considered local

#### `download_image(url, headers=None, timeout=10)`
Downloads an image from a URL and saves it temporarily.

**Parameters:**
- `url` (str): Image URL to download
- `headers` (dict, optional): HTTP headers for the request
- `timeout` (int): Request timeout in seconds

**Returns:**
- `tuple`: (file_path, content_type, success)

#### `cleanup_temp_images(max_age_hours=24)`
Removes old temporary image files.

**Parameters:**
- `max_age_hours` (int): Remove files older than this many hours

## Security Considerations

### Access Control

The feature respects your existing network security:

- Only downloads from URLs your notification system can already access
- No additional network exposure required
- Uses same authentication/headers as your application

### File Safety

- Downloaded files are validated as images
- Temporary files are isolated in system temp directory
- Automatic cleanup prevents accumulation of files
- No persistent storage of sensitive images

### Privacy

- Images are only downloaded when notifications are sent
- Temporary storage is minimal (typically seconds to minutes)
- No logging of image content, only metadata

## Migration

### From Previous Versions

No migration is required. The feature is backward compatible:

- Existing embed configurations continue to work
- Public image URLs are unchanged
- Local URLs are automatically detected and handled

### Testing Migration

1. Identify notification flows using local image URLs
2. Run the test script to verify functionality
3. Monitor logs during initial deployments
4. Verify Discord channels receive images correctly

## Best Practices

### Image Optimization

- Keep source images reasonably sized (< 5MB when possible)
- Use appropriate formats (PNG for graphics, JPEG for photos)
- Consider compression at the source to reduce processing time

### URL Patterns

- Use consistent URL patterns for easier debugging
- Include file extensions when possible
- Avoid URLs that require complex authentication

### Monitoring

- Monitor logs for download failures
- Set up alerts for high error rates
- Regularly clean up temp directory if running in constrained environments

## Examples

### Basic Local Image

```json
{
  "embed_config": {
    "enabled": true,
    "title": "Application Screenshot",
    "image_url": "http://localhost:8080/screenshot.png"
  }
}
```

### Multiple Local Images

```json
{
  "embed_config": {
    "enabled": true,
    "title": "Server Dashboard",
    "image_url": "http://monitoring.internal/dashboard.png",
    "thumbnail_url": "http://192.168.1.50/status-icon.png",
    "author_icon": "http://localhost:3000/avatar.jpg"
  }
}
```

### Mixed Local and Public Images

```json
{
  "embed_config": {
    "enabled": true,
    "title": "System Report",
    "image_url": "http://internal-api:8080/chart.png",
    "footer_icon": "https://cdn.example.com/logo.png"
  }
}
```

In this example, the chart image would be uploaded as an attachment, while the footer logo would remain a regular URL link.