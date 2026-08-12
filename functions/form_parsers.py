"""Shared parsers for flow and embed configuration from forms or JSON."""

import secrets


def parse_embed_fields(form):
    """Parse static embed fields from a form-like mapping."""
    fields = []

    def getlist(key):
        if hasattr(form, 'getlist'):
            return form.getlist(key)
        value = form.get(key, []) if isinstance(form, dict) else []
        return value if isinstance(value, list) else ([value] if value else [])

    def get(key, default=''):
        if hasattr(form, 'get'):
            return form.get(key, default)
        return form.get(key, default) if isinstance(form, dict) else default

    names = getlist('embed_field_name[]')
    values = getlist('embed_field_value[]')

    for index, (name, value) in enumerate(zip(names, values)):
        if name and value:
            inline = get(f'embed_field_inline_{index}', '') in ('true', 'on', '1', True)
            fields.append({
                'name': name,
                'value': value,
                'inline': inline,
            })
    return fields


def parse_embed_config_from_form(form):
    """Parse embed configuration from a Flask form or dict-like object."""

    def get(key, default=''):
        if hasattr(form, 'get'):
            return form.get(key, default)
        return form.get(key, default) if isinstance(form, dict) else default

    def getlist(key):
        if hasattr(form, 'getlist'):
            return form.getlist(key)
        value = form.get(key, []) if isinstance(form, dict) else []
        return value if isinstance(value, list) else ([value] if value else [])

    if get('embed_enabled') not in ('true', True):
        return {}

    color_mode = get('embed_color_mode', 'static')
    embed_config = {
        'enabled': True,
        'title': get('embed_title', ''),
        'description': get('embed_description', ''),
        'url': get('embed_url', ''),
        'color_mode': color_mode,
        'timestamp': get('embed_timestamp', 'true') == 'true',
        'footer_text': get('embed_footer_text', ''),
        'footer_icon': get('embed_footer_icon', ''),
        'author_name': get('embed_author_name', ''),
        'author_icon': get('embed_author_icon', ''),
        'author_url': get('embed_author_url', ''),
        'thumbnail_url': get('embed_thumbnail_url', ''),
        'image_url': get('embed_image_url', ''),
        'fields': parse_embed_fields(form),
        'dynamic_fields': [],
    }

    if color_mode == 'static':
        embed_config['color'] = get('embed_color', '')
    elif color_mode == 'if':
        embed_config['color_monitor'] = get('embed_color_monitor', '')
        tests = getlist('embed_color_if_test[]')
        colors = getlist('embed_color_if_color[]')
        rules = []
        for test, color in zip(tests, colors):
            if test and color:
                rules.append({'test': test, 'color': color})
        embed_config['color_rules'] = rules
    elif color_mode == 'gradient':
        embed_config['color_monitor'] = get('embed_color_monitor', '')
        embed_config['gradient'] = {
            'start_value': get('embed_gradient_start_value', ''),
            'start_color': get('embed_gradient_start_color', '#00ff00'),
            'end_value': get('embed_gradient_end_value', ''),
            'end_color': get('embed_gradient_end_color', '#ff0000'),
        }

    return embed_config


def parse_api_headers(form):
    """Parse custom API headers from form data."""

    def getlist(key):
        if hasattr(form, 'getlist'):
            return form.getlist(key)
        value = form.get(key, []) if isinstance(form, dict) else []
        return value if isinstance(value, list) else ([value] if value else [])

    headers = []
    keys = getlist('header_key[]')
    values = getlist('header_value[]')
    for key, value in zip(keys, values):
        if key:
            headers.append({'key': key, 'value': value})
    return headers


def build_flow_from_form(form, editing_flow=None):
    """Build a flow dict from submitted form data."""

    def get(key, default=''):
        return form.get(key, default)

    trigger_type = get('trigger_type', 'on_change')
    webhook_url = get('webhook_url', '').strip()
    accept_webhooks = trigger_type == 'webhook'
    require_webhook_secret = get('require_webhook_secret', 'false') == 'true'

    embed_config = parse_embed_config_from_form(form)

    flow = {
        'name': get('flow_name'),
        'trigger_type': trigger_type,
        'webhook_url': webhook_url,
        'webhook_name': get('webhook_name', '').strip(),
        'webhook_avatar': get('webhook_avatar', '').strip(),
        'message_template': get('message_template', ''),
        'active': get('active', 'false') == 'true',
        'endpoint': get('endpoint', ''),
        'field': get('field', ''),
        'interval': int(get('interval', 5) or 5) if trigger_type == 'timer' else None,
        'accept_webhooks': accept_webhooks,
        'embed_config': embed_config,
        'category': get('category', 'General'),
        'condition_enabled': get('condition_enabled', 'false') == 'true',
        'condition': get('condition', ''),
        'api_headers': parse_api_headers(form),
        'api_request_body': get('api_request_body', ''),
    }

    if accept_webhooks and require_webhook_secret:
        if editing_flow and editing_flow.get('webhook_secret'):
            flow['webhook_secret'] = editing_flow['webhook_secret']
        else:
            flow['webhook_secret'] = secrets.token_urlsafe(16)

    if editing_flow:
        for key in ('last_value', 'last_run', 'last_data'):
            if key in editing_flow:
                flow[key] = editing_flow[key]

    return flow


def build_flow_from_json(data, existing_flow=None):
    """Build a flow dict from JSON API payload."""

    if not isinstance(data, dict):
        raise ValueError('Request body must be a JSON object')

    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Flow name is required')

    trigger_type = data.get('trigger_type', 'on_change')
    if trigger_type not in ('timer', 'on_change', 'webhook'):
        raise ValueError('Invalid trigger_type')

    flow = {
        'name': name,
        'trigger_type': trigger_type,
        'webhook_url': data.get('webhook_url', ''),
        'webhook_name': data.get('webhook_name', ''),
        'webhook_avatar': data.get('webhook_avatar', ''),
        'message_template': data.get('message_template', ''),
        'active': bool(data.get('active', True)),
        'endpoint': data.get('endpoint', ''),
        'field': data.get('field', ''),
        'interval': data.get('interval', 5) if trigger_type == 'timer' else None,
        'accept_webhooks': trigger_type == 'webhook',
        'embed_config': data.get('embed_config', {}),
        'category': data.get('category', 'General'),
        'condition_enabled': bool(data.get('condition_enabled', False)),
        'condition': data.get('condition', ''),
        'api_headers': data.get('api_headers', []),
        'api_request_body': data.get('api_request_body', ''),
    }

    if trigger_type == 'webhook' and data.get('require_webhook_secret'):
        if existing_flow and existing_flow.get('webhook_secret'):
            flow['webhook_secret'] = existing_flow['webhook_secret']
        else:
            flow['webhook_secret'] = secrets.token_urlsafe(16)
    elif existing_flow and existing_flow.get('webhook_secret') and data.get('keep_webhook_secret'):
        flow['webhook_secret'] = existing_flow['webhook_secret']

    if existing_flow:
        for key in ('last_value', 'last_run', 'last_data'):
            if key in existing_flow and key not in data:
                flow[key] = existing_flow[key]

    return flow
