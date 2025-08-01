---
layout: default
title: Reference
nav_order: 5
has_children: true
permalink: /reference/
---

# Reference Documentation
{: .no_toc }

Detailed reference materials and specifications for Turtifications.
{: .fs-6 .fw-300 }

This section contains comprehensive reference documentation for developers and advanced users who need detailed technical information about Turtifications features and capabilities.

## Available References

### [Template Variables](variables)
Complete reference for all available template variables and their usage in notification messages. This includes:

- **System variables** - Time, flow information, execution data
- **API data access** - Accessing fields from API responses and webhooks
- **Conditional logic** - Control flow and dynamic content
- **Advanced features** - Loops, string manipulation, formatting
- **Service-specific examples** - Variables for popular services
- **Error handling** - Safe variable access and debugging
- **Best practices** - Performance and security considerations

## Template System

Turtifications uses a powerful template system based on Jinja2 that allows you to create dynamic, data-driven notifications. Key features include:

- **Variable substitution** with `{variable}` syntax
- **Conditional logic** with `{#if condition}...{#endif}`
- **Loops and iteration** with `{#for item in list}...{#endfor}`
- **String manipulation** with filters like `|upper`, `|truncate`, `|default`
- **Safe field access** with fallback values and existence checks
- **Raw data debugging** for troubleshooting templates

## Data Sources

Templates can access data from multiple sources:

### API Responses
Data from timer-based and change detection flows:
```yaml
# Example API response
{
  "status": "healthy",
  "cpu_usage": 45,
  "memory_usage": 67,
  "services": [
    {"name": "web", "status": "running"},
    {"name": "db", "status": "running"}
  ]
}

# Template usage
CPU: {result['cpu_usage']}%
Services: {result['services']|length} running
```

### Webhook Data
Data from external services via webhooks:
```yaml
# GitHub webhook payload
{
  "repository": {"full_name": "user/repo"},
  "commits": [
    {
      "message": "Fix bug in user auth",
      "author": {"name": "Developer"}
    }
  ]
}

# Template usage
Repo: {repository['full_name']}
Commit: {commits['0']['message']}
Author: {commits['0']['author']['name']}
```

### System Information
Built-in system variables:
```yaml
# Always available
Flow: {flow_name}
Time: {time}
Trigger: {trigger_type}

# Change detection only
Current: {value}
Previous: {old_value}
Change: {change}
```

## Field Access Patterns

### Basic Access
```yaml
{result['field_name']}
{result['nested']['field']}
{result['array']['0']['field']}
```

### Safe Access with Defaults
```yaml
{result['optional_field']|default('Not provided')}
{result['nested']['field']|default('Unknown')}
```

### Conditional Access
```yaml
{#if result['field']}
Field value: {result['field']}
{#else}
Field not available
{#endif}
```

## Common Patterns

### Status Indicators
```yaml
{#if result['status'] == 'success'}
✅ Success
{#elif result['status'] == 'warning'}
⚠️ Warning
{#else}
❌ Error
{#endif}
```

### Data Lists
```yaml
{#for item in result['items']}
- {item['name']}: {item['status']}
{#endfor}
```

### Formatted Numbers
```yaml
CPU: {result['cpu_usage']|round(1)}%
Memory: {result['memory_bytes']|filesizeformat}
Response: {result['response_time']}ms
```

## Debugging Templates

### Show Raw Data
```yaml
Raw response: {result|tojson(indent=2)}
```

### Field Existence
```yaml
Field exists: {result['field'] is defined}
Field type: {result['field']|string}
```

### Preview Mode
Use the preview feature in the web interface to test templates with real API data before saving flows.

## Best Practices

1. **Always provide fallbacks** for optional fields
2. **Test with real data** using the preview feature
3. **Keep templates readable** with proper formatting
4. **Use meaningful variable names** in webhook payloads
5. **Limit template complexity** for better performance
6. **Handle missing data gracefully** with conditionals
7. **Don't expose sensitive information** in notifications

## Performance Considerations

- Complex templates may impact notification speed
- Avoid deep nesting in conditional statements
- Use simple conditions when possible
- Cache complex calculations outside templates if needed

## Security Notes

- Sanitize user input in webhook data
- Don't expose API keys or secrets in templates
- Use allowlists for acceptable field values when possible
- Validate webhook sources when implementing custom integrations

## Getting Help

For template-related questions:

- Check the [Template Variables Reference](variables) for specific variable documentation
- Review the [Notification Flows Guide](../guides/notification-flows) for practical examples
- Use the preview feature to debug template issues
- Open an issue on GitHub for template system bugs or feature requests