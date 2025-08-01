---
layout: default
title: API
nav_order: 4
has_children: true
permalink: /api/
---

# API Documentation
{: .no_toc }

Complete documentation for the Turtifications REST API.
{: .fs-6 .fw-300 }

The Turtifications API provides programmatic access to all application features, enabling integration with external systems, automation tools, and custom applications.

## API Overview

The REST API offers endpoints for:

- **Status monitoring** - Check application health and flow status
- **Flow management** - Retrieve flow information and statistics
- **Notification testing** - Send test notifications to verify configuration
- **Webhook handling** - Receive data from external services
- **Log access** - Retrieve application logs and analytics
- **Statistics** - Get detailed usage and performance metrics

## Available Documentation

### [API Reference](reference)
Complete reference documentation for all available endpoints, including:

- Request/response formats
- Authentication requirements
- Error handling
- Rate limiting
- Code examples in multiple languages

## Base URL

All API requests should be made to:
```
http://localhost:5000/api
```

Replace `localhost:5000` with your actual server address and port.

## Quick Examples

### Check Application Status
```bash
curl http://localhost:5000/api/status
```

### Send Test Notification
```bash
curl -X POST http://localhost:5000/api/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from API!"}'
```

### Get Flow Statistics
```bash
curl http://localhost:5000/api/statistics
```

## Authentication

Currently, the API does not require authentication by default. For production deployments, consider implementing authentication through:

- Reverse proxy authentication
- API key validation
- OAuth integration
- Custom middleware

## Rate Limiting

While there are no built-in rate limits, consider implementing them in production:

- Status endpoints: 60 requests/minute
- Data endpoints: 30 requests/minute  
- Webhook endpoints: 100 requests/minute

## Error Handling

All API errors follow a consistent JSON format:

```json
{
  "error": true,
  "message": "Description of the error",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Integration Examples

The API is designed to be easily integrated with:

- **Monitoring dashboards** (Grafana, custom dashboards)
- **CI/CD pipelines** (GitHub Actions, Jenkins, GitLab CI)
- **Infrastructure automation** (Ansible, Terraform)
- **Custom applications** (Python, JavaScript, Go, etc.)
- **Webhook providers** (GitHub, Docker Hub, custom services)

## Getting Started

1. **Read the [API Reference](reference)** for complete endpoint documentation
2. **Review the [API Usage Guide](../guides/api)** for practical integration examples
3. **Test with curl or Postman** to understand request/response formats
4. **Implement error handling** and retries in your applications
5. **Monitor API usage** and implement appropriate rate limiting

## Support

For API-related questions:

- Check the [Troubleshooting Guide](../troubleshooting) for common issues
- Review [integration examples](../guides/api) for best practices
- Open an issue on [GitHub](https://github.com/yourusername/turtifications/issues) for bugs
- Join discussions on [GitHub Discussions](https://github.com/yourusername/turtifications/discussions) for general questions