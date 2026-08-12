"""Optional API key authentication for mutating endpoints."""

import os
from functools import wraps

from flask import jsonify, request


def is_api_key_required():
    """Return True when an API key is configured."""
    return bool(os.environ.get('API_KEY', '').strip())


def check_api_key():
    """
    Validate API key from X-API-Key header or api_key query param.
    Returns None if authorized, or (response, status_code) if not.
    """
    if not is_api_key_required():
        return None

    expected = os.environ.get('API_KEY', '').strip()
    provided = (
        request.headers.get('X-API-Key')
        or request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
        or request.args.get('api_key', '')
    )

    if provided != expected:
        return jsonify({'error': 'Unauthorized', 'message': 'Valid API key required'}), 401
    return None


def require_api_key(f):
    """Decorator for routes that require API key when API_KEY env is set."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_error = check_api_key()
        if auth_error:
            return auth_error
        return f(*args, **kwargs)

    return decorated
