# Kong Rate Limiting for /healthz Endpoint

This guide explains how to add rate limiting to your `/healthz` endpoint using the Kong MCP Server tools we've built.

## Overview

Based on your request log:
```json
{
  "@timestamp": ["2025-08-24T19:10:03.000Z"],
  "request_method": ["GET"],
  "request_uri": ["/healthz"],
  "request_url": ["http://localhost/healthz"],
  "client_ip": ["127.0.0.1"],
  "request_user_agent": ["PostmanRuntime/7.45.0"],
  "response_status": [200]
}
```

We've created comprehensive rate limiting tools and scripts to protect your `/healthz` endpoint from abuse while allowing normal health check traffic.

## What We've Built

### 1. Core Rate Limiting Tools (`src/kong_mcp_server/tools/kong_rate_limiting.py`)

Complete CRUD operations for Kong's rate limiting plugins:

- **Basic Rate Limiting**: Simple time-based limits (minute/hour/day)
- **Advanced Rate Limiting**: Complex sliding window limits with Redis support
- **All Scopes**: Global, service, route, and consumer-scoped rate limiting
- **Full Management**: Create, read, update, delete operations

**Available Functions:**
- `create_rate_limiting_plugin()` - Create basic rate limiting
- `get_rate_limiting_plugins()` - List rate limiting plugins
- `update_rate_limiting_plugin()` - Update existing rate limiting
- `delete_rate_limiting_plugin()` - Remove rate limiting
- `create_rate_limiting_advanced_plugin()` - Create advanced rate limiting
- `get_rate_limiting_advanced_plugins()` - List advanced plugins
- `update_rate_limiting_advanced_plugin()` - Update advanced plugins
- `delete_rate_limiting_advanced_plugin()` - Remove advanced plugins
- `get_plugin()` - Get specific plugin by ID
- `get_plugins()` - List all plugins with filters

### 2. Setup Scripts

#### `setup_healthz_complete.py` - Complete Setup (Recommended)
Interactive script that sets up everything:
- Creates health check service
- Creates `/healthz` route
- Adds rate limiting with user-selectable levels
- Provides testing instructions

**Usage:**
```bash
python3 setup_healthz_complete.py
```

#### `add_healthz_rate_limit.py` - Quick Rate Limiting
Adds rate limiting to existing `/healthz` route:
```bash
python3 add_healthz_rate_limit.py
```

#### `example_healthz_rate_limiting.py` - Advanced Example
Comprehensive example with monitoring and management features.

## Quick Start

### Option 1: Complete Setup (Recommended)

1. **Run the complete setup script:**
   ```bash
   python3 setup_healthz_complete.py
   ```

2. **Follow the prompts:**
   - Enter your backend URL (default: `http://localhost:8080`)
   - Choose rate limiting level:
     - **Generous**: 300/min, 18000/hour - For frequent health checks
     - **Standard**: 120/min, 7200/hour - Balanced protection (recommended)
     - **Strict**: 60/min, 3600/hour - Strong protection
     - **Custom**: Enter your own limits

3. **Test the setup:**
   ```bash
   curl -i http://localhost/healthz
   ```

### Option 2: Manual Setup Using MCP Tools

If you prefer to use the tools directly:

```python
import asyncio
from src.kong_mcp_server.tools.kong_rate_limiting import create_rate_limiting_plugin

async def setup_rate_limiting():
    # Add rate limiting to existing route
    plugin = await create_rate_limiting_plugin(
        route_id="your-healthz-route-id",
        minute=120,  # 120 requests per minute
        hour=7200,   # 7200 requests per hour
        limit_by="ip",
        policy="local",
        fault_tolerant=True,
        tags=["healthz", "monitoring"]
    )
    print(f"Created rate limiting: {plugin['id']}")

asyncio.run(setup_rate_limiting())
```

## Rate Limiting Configuration

### Recommended Settings for /healthz

**Standard Configuration (Recommended):**
- **120 requests/minute** (2 per second)
- **7,200 requests/hour**
- **172,800 requests/day**
- **Limited by IP address**
- **Fault tolerant** (continues serving if rate limiting fails)
- **Headers visible** (shows rate limiting info to clients)

**Why these limits?**
- Health checks are typically automated and frequent
- 2 requests per second allows for aggressive monitoring
- IP-based limiting prevents single sources from overwhelming
- Fault tolerance ensures health checks don't break

### Rate Limiting Headers

When rate limiting is active, responses include headers:
```
X-RateLimit-Limit-Minute: 120
X-RateLimit-Remaining-Minute: 119
X-RateLimit-Reset: 1629876543
```

### Rate Limiting Responses

When limits are exceeded:
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit-Minute: 120
X-RateLimit-Remaining-Minute: 0
X-RateLimit-Reset: 1629876603

{
  "message": "API rate limit exceeded"
}
```

## Testing Your Setup

### 1. Basic Test
```bash
curl -i http://localhost/healthz
```
Look for `X-RateLimit-*` headers in the response.

### 2. Rate Limiting Test
```bash
# Send 10 rapid requests
for i in {1..10}; do 
  curl -s -o /dev/null -w '%{http_code}\n' http://localhost/healthz
done
```

### 3. Monitor Rate Limiting
```bash
# Check plugin status
curl http://localhost:8001/plugins | jq '.data[] | select(.name == "rate-limiting")'
```

## Advanced Configuration

### Redis-Based Rate Limiting

For distributed Kong deployments, use Redis:

```python
await create_rate_limiting_advanced_plugin(
    route_id="your-route-id",
    limit=[{"minute": 120}, {"hour": 7200}],
    window_size=[60, 3600],
    strategy="redis",
    redis_host="your-redis-host",
    redis_port=6379,
    redis_password="your-password"
)
```

### Consumer-Based Rate Limiting

For authenticated health checks:

```python
await create_rate_limiting_plugin(
    route_id="your-route-id",
    minute=300,  # Higher limits for authenticated consumers
    limit_by="consumer",
    policy="local"
)
```

## Monitoring and Management

### Check Current Rate Limiting
```python
from src.kong_mcp_server.tools.kong_rate_limiting import get_rate_limiting_plugins

async def check_rate_limiting():
    plugins = await get_rate_limiting_plugins()
    for plugin in plugins:
        if "healthz" in plugin.get("tags", []):
            print(f"Plugin: {plugin['id']}")
            print(f"Config: {plugin['config']}")
```

### Update Rate Limiting
```python
from src.kong_mcp_server.tools.kong_rate_limiting import update_rate_limiting_plugin

async def update_limits():
    await update_rate_limiting_plugin(
        plugin_id="your-plugin-id",
        minute=200,  # Increase to 200/minute
        hour=12000   # Increase to 12000/hour
    )
```

### Remove Rate Limiting
```python
from src.kong_mcp_server.tools.kong_rate_limiting import delete_rate_limiting_plugin

async def remove_rate_limiting():
    await delete_rate_limiting_plugin("your-plugin-id")
```

## Troubleshooting

### Common Issues

1. **"No /healthz route found"**
   - Run `setup_healthz_complete.py` to create the route
   - Or check existing routes: `curl http://localhost:8001/routes`

2. **"Kong not accessible"**
   - Ensure Kong is running: `curl http://localhost:8001/status`
   - Check Kong Admin API port (default: 8001)

3. **Rate limiting not working**
   - Check plugin is enabled: `curl http://localhost:8001/plugins/{plugin-id}`
   - Verify route association
   - Check Kong error logs

### Verification Commands

```bash
# Check Kong status
curl http://localhost:8001/status

# List all services
curl http://localhost:8001/services

# List all routes
curl http://localhost:8001/routes

# List all plugins
curl http://localhost:8001/plugins

# Check specific plugin
curl http://localhost:8001/plugins/{plugin-id}
```

## Integration with Monitoring

### Prometheus Metrics

Kong can export rate limiting metrics to Prometheus:
- `kong_rate_limiting_requests_total`
- `kong_rate_limiting_requests_exceeded_total`

### Log Analysis

Rate limiting events appear in Kong logs:
```json
{
  "message": "rate limit exceeded",
  "client_ip": "127.0.0.1",
  "route": {"id": "healthz-route"},
  "plugin": {"id": "rate-limiting-plugin"}
}
```

## Best Practices

1. **Start Conservative**: Begin with generous limits and tighten as needed
2. **Monitor Usage**: Track actual health check patterns
3. **Use Fault Tolerance**: Enable for critical health checks
4. **Tag Everything**: Use consistent tags for easy management
5. **Test Thoroughly**: Verify rate limiting works as expected
6. **Document Limits**: Keep track of configured limits
7. **Regular Review**: Periodically review and adjust limits

## Summary

You now have comprehensive rate limiting for your `/healthz` endpoint that:

✅ **Protects against abuse** - Prevents overwhelming your health check endpoint  
✅ **Allows normal traffic** - Generous limits for legitimate health checks  
✅ **Provides visibility** - Rate limiting headers show current status  
✅ **Fault tolerant** - Won't break health checks if rate limiting fails  
✅ **Easy to manage** - Full CRUD operations via MCP tools  
✅ **Scalable** - Supports Redis for distributed deployments  

Your `/healthz` endpoint is now production-ready with enterprise-grade rate limiting protection!
