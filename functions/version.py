"""
Version management for turtifications
"""

import os
import json
from datetime import datetime

VERSION_FILE = 'data/version.txt'

def get_version():
    """Get the current version from the version file"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                version = f.read().strip()
                return version if version else '0.0.0'
        else:
            # Default version if file doesn't exist
            return '0.0.0'
    except Exception as e:
        print(f"Error reading version file: {e}")
        return '0.0.0'

def set_version(version):
    """Set the version in the version file"""
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(VERSION_FILE), exist_ok=True)
        
        with open(VERSION_FILE, 'w') as f:
            f.write(version)
        
        return True
    except Exception as e:
        print(f"Error writing version file: {e}")
        return False

def get_version_info():
    """Get complete version information"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                version = f.read().strip()
                return {
                    'version': version if version else '0.0.0',
                    'last_updated': datetime.now().isoformat(),
                    'build_date': datetime.now().isoformat()
                }
        else:
            return {
                'version': '0.0.0',
                'last_updated': datetime.now().isoformat(),
                'build_date': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error reading version info: {e}")
        return {
            'version': '0.0.0',
            'last_updated': datetime.now().isoformat(),
            'build_date': datetime.now().isoformat()
        }

def initialize_version():
    """Initialize version file if it doesn't exist"""
    if not os.path.exists(VERSION_FILE):
        set_version('0.0.0')
        print(f"Initialized version file with version 0.0.0") 