import os
import requests
import tempfile
import hashlib
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse
from functions.utils import log_notification

# Temporary directory for storing downloaded images
TEMP_IMAGE_DIR = os.path.join(tempfile.gettempdir(), 'discord_notifications')

def ensure_temp_dir():
    """Ensure the temporary image directory exists"""
    if not os.path.exists(TEMP_IMAGE_DIR):
        os.makedirs(TEMP_IMAGE_DIR)
        log_notification(f"Created temporary image directory: {TEMP_IMAGE_DIR}")

def get_image_filename_from_url(url):
    """Extract or generate a filename from an image URL"""
    parsed = urlparse(url)
    path = parsed.path
    
    # Extract filename from path
    if path and '.' in os.path.basename(path):
        filename = os.path.basename(path)
    else:
        # Generate filename based on URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"image_{url_hash}.png"
    
    return filename

def download_image(url, headers=None, timeout=10):
    """
    Download an image from a URL and return the file path and content type
    Returns tuple: (file_path, content_type, success)
    """
    try:
        ensure_temp_dir()
        
        # Add default headers to appear more like a browser
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        if headers:
            default_headers.update(headers)
        
        log_notification(f"Downloading image from: {url}")
        response = requests.get(url, headers=default_headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Get content type from response
        content_type = response.headers.get('content-type', 'image/png')
        
        # Generate filename
        filename = get_image_filename_from_url(url)
        file_path = os.path.join(TEMP_IMAGE_DIR, filename)
        
        # Download and save the image
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify it's a valid image and optionally resize if too large
        try:
            with Image.open(file_path) as img:
                # Discord has a 25MB limit for attachments, let's keep images reasonable
                file_size = os.path.getsize(file_path)
                max_size_mb = 8  # Keep under 8MB to be safe
                
                if file_size > max_size_mb * 1024 * 1024:
                    log_notification(f"Image is large ({file_size/1024/1024:.1f}MB), resizing...")
                    resized_path = resize_image_if_needed(file_path, max_size_mb)
                    if resized_path != file_path:
                        file_path = resized_path
                
                log_notification(f"Successfully downloaded image: {filename} ({os.path.getsize(file_path)/1024:.1f}KB)")
                return file_path, content_type, True
                
        except Exception as img_error:
            log_notification(f"Downloaded file is not a valid image: {str(img_error)}")
            # Clean up invalid file
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, None, False
        
    except Exception as e:
        log_notification(f"Failed to download image from {url}: {str(e)}")
        return None, None, False

def resize_image_if_needed(file_path, max_size_mb=8):
    """
    Resize an image if it's larger than the specified size limit
    Returns the path to the resized image (or original if no resize needed)
    """
    try:
        file_size = os.path.getsize(file_path)
        max_bytes = max_size_mb * 1024 * 1024
        
        if file_size <= max_bytes:
            return file_path
        
        with Image.open(file_path) as img:
            # Calculate resize ratio to get under the size limit
            # Start with 80% quality and adjust dimensions if needed
            quality = 80
            resize_ratio = 1.0
            
            # Try different combinations of quality and size reduction
            for attempt in range(5):
                # Calculate new dimensions
                new_width = int(img.width * resize_ratio)
                new_height = int(img.height * resize_ratio)
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save to temporary buffer to check size
                buffer = BytesIO()
                format = img.format or 'PNG'
                
                if format == 'JPEG':
                    resized_img.save(buffer, format=format, quality=quality, optimize=True)
                else:
                    # Convert to RGB if necessary for JPEG
                    if resized_img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', resized_img.size, (255, 255, 255))
                        if resized_img.mode == 'P':
                            resized_img = resized_img.convert('RGBA')
                        rgb_img.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                        resized_img = rgb_img
                    resized_img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    format = 'JPEG'
                
                # Check if we're under the limit
                buffer_size = buffer.tell()
                if buffer_size <= max_bytes:
                    # Save the resized image
                    base_name, ext = os.path.splitext(file_path)
                    resized_path = f"{base_name}_resized{'.jpg' if format == 'JPEG' else ext}"
                    
                    with open(resized_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    log_notification(f"Resized image from {file_size/1024:.1f}KB to {buffer_size/1024:.1f}KB")
                    
                    # Remove original file
                    os.remove(file_path)
                    return resized_path
                
                # Reduce quality or size for next attempt
                if quality > 60:
                    quality -= 15
                else:
                    resize_ratio *= 0.8
        
        # If we couldn't get it small enough, return original
        log_notification(f"Warning: Could not resize image below {max_size_mb}MB limit")
        return file_path
        
    except Exception as e:
        log_notification(f"Error resizing image: {str(e)}")
        return file_path

def cleanup_temp_images(max_age_hours=24):
    """
    Clean up old temporary images
    max_age_hours: Remove files older than this many hours
    """
    try:
        if not os.path.exists(TEMP_IMAGE_DIR):
            return
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for filename in os.listdir(TEMP_IMAGE_DIR):
            file_path = os.path.join(TEMP_IMAGE_DIR, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except Exception as e:
                        log_notification(f"Failed to remove temp file {filename}: {str(e)}")
        
        if cleaned_count > 0:
            log_notification(f"Cleaned up {cleaned_count} temporary image files")
            
    except Exception as e:
        log_notification(f"Error during temp image cleanup: {str(e)}")

def extract_image_urls_from_embed(embed_config, data=None, user_variables=None):
    """
    Extract all image URLs from an embed configuration that need to be downloaded
    Returns list of (url, attachment_name) tuples
    """
    from functions.utils import format_message_template
    
    image_urls = []
    data = data or {}
    user_variables = user_variables or {}
    
    # Check for image URLs that might be local services
    url_fields = [
        ('image_url', 'embed_image'),
        ('thumbnail_url', 'embed_thumbnail'),
        ('footer_icon', 'footer_icon'),
        ('author_icon', 'author_icon')
    ]
    
    for field_key, attachment_name in url_fields:
        if embed_config.get(field_key):
            url = format_message_template(embed_config[field_key], data, user_variables)
            if url and is_local_service_url(url):
                image_urls.append((url, f"{attachment_name}.png"))
    
    return image_urls

def is_local_service_url(url):
    """
    Check if a URL points to a local service that Discord can't access
    This includes localhost, private IP ranges, and internal hostnames
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False
        
        # Check for localhost variants
        if hostname in ['localhost', '127.0.0.1', '::1']:
            return True
        
        # Check for private IP ranges
        import ipaddress
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback
        except ValueError:
            # Not an IP address, check for internal hostnames
            pass
        
        # Check for common internal hostnames or non-public domains
        internal_indicators = [
            '.local',
            '.internal',
            '.lan',
            'docker',
            'container',
            '-internal',
            'dev-',
            'test-',
            'staging-'
        ]
        
        hostname_lower = hostname.lower()
        for indicator in internal_indicators:
            if indicator in hostname_lower:
                return True
        
        # If it doesn't have a TLD, it's probably internal
        if '.' not in hostname:
            return True
        
        return False
        
    except Exception:
        # If we can't parse it, assume it's external
        return False