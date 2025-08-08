import os
import requests
import tempfile
import uuid
from urllib.parse import urlparse
from functions.utils import log_notification

def download_image_to_temp(image_url):
    """
    Download an image from a URL and save it to a temporary file.
    Returns the temporary file path if successful, None otherwise.
    """
    temp_fd = None
    temp_path = None
    
    try:
        # Parse the URL to get filename and extension
        parsed_url = urlparse(image_url)
        path = parsed_url.path
        
        # Get file extension from URL
        if '.' in path:
            ext = os.path.splitext(path)[1].lower()
            # Validate image extensions
            if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
                ext = '.png'  # Default to PNG if unknown
        else:
            ext = '.png'  # Default extension
        
        # Create a temporary file with the correct extension
        temp_fd, temp_path = tempfile.mkstemp(suffix=ext, prefix='discord_img_')
        
        # Download the image
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check if response is actually an image by content-type
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            log_notification(f"Warning: URL {image_url} does not return an image (content-type: {content_type})")
        
        # Write the image data to the temporary file
        with os.fdopen(temp_fd, 'wb') as temp_file:
            temp_fd = None  # fdopen takes ownership of the file descriptor
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
        
        log_notification(f"📥 Downloaded image from {image_url} to temporary file: {temp_path}")
        return temp_path
        
    except requests.RequestException as e:
        log_notification(f"❌ Failed to download image from {image_url}: {str(e)}")
        # Clean up resources
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except:
                pass
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        return None
    except Exception as e:
        log_notification(f"❌ Error downloading image from {image_url}: {str(e)}")
        # Clean up resources
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except:
                pass
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        return None

def cleanup_temp_file(file_path):
    """
    Remove a temporary file safely.
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            log_notification(f"🗑️ Cleaned up temporary file: {file_path}")
    except Exception as e:
        log_notification(f"⚠️ Failed to cleanup temporary file {file_path}: {str(e)}")

def cleanup_temp_files(file_paths):
    """
    Remove multiple temporary files safely.
    """
    if not file_paths:
        return
    
    for file_path in file_paths:
        cleanup_temp_file(file_path)

def get_image_filename_from_url(image_url):
    """
    Extract a reasonable filename from an image URL for Discord upload.
    """
    try:
        parsed_url = urlparse(image_url)
        path = parsed_url.path
        
        if path and '/' in path:
            filename = os.path.basename(path)
            if filename and '.' in filename:
                return filename
        
        # Generate a random filename if we can't extract one
        return f"image_{uuid.uuid4().hex[:8]}.png"
        
    except Exception:
        return f"image_{uuid.uuid4().hex[:8]}.png"

def get_mime_type_from_extension(file_path):
    """
    Get the appropriate MIME type based on file extension.
    """
    if not file_path:
        return 'image/png'
    
    ext = os.path.splitext(file_path)[1].lower()
    
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp'
    }
    
    return mime_types.get(ext, 'image/png')  # Default to PNG if unknown