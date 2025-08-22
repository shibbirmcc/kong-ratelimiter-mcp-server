# Kong Rate Limiter MCP Server

[![Build Status](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/workflows/CI/badge.svg)](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/actions)
[![Coverage](https://codecov.io/gh/shibbirmcc/kong-ratelimiter-mcp-server/branch/master/graph/badge.svg)](https://codecov.io/gh/shibbirmcc/kong-ratelimiter-mcp-server)
[![Release](https://img.shields.io/github/v/release/shibbirmcc/kong-ratelimiter-mcp-server)](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/releases)

A Model Context Protocol (MCP) server for Kong configuration management using FastMCP and Server-Sent Events (SSE).

## Quick Start

### Option 1: Virtual Environment Script (Recommended)
```bash
./venv.sh                                    # Setup and activate
python -m kong_mcp_server.server            # Run server
pytest --cov=kong_mcp_server                # Run tests with coverage
./venv.sh deactivate                         # Cleanup
```

### Option 2: Server Management Script
```bash
./scripts/server.sh start                    # Start server
./scripts/server.sh status                   # Check status
./scripts/server.sh health                   # Health check
./scripts/server.sh logs                     # View logs
./scripts/server.sh stop                     # Stop server
```

### Option 3: Manual Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -e .[dev]
python -m kong_mcp_server.server
```

## Configuration

### Environment Variables
```bash
# Server Configuration
export FASTMCP_PORT=8080                     # Server port (default: 8080)
export HOST=127.0.0.1                       # Server host (default: 127.0.0.1)

# Kong Configuration
export KONG_ADMIN_URL=http://localhost:8001  # Kong Admin API URL
export KONG_USERNAME=admin                   # Kong CE username
export KONG_PASSWORD=secret                  # Kong CE password
export KONG_API_TOKEN=token                  # Kong EE API token (alternative)
export KONG_TIMEOUT=30.0                     # Request timeout (seconds)
export KONG_VERIFY_SSL=true                  # SSL verification
```

### Kong Authentication

**Community Edition (Username/Password):**
```bash
export KONG_USERNAME=admin
export KONG_PASSWORD=your-password
```

**Enterprise Edition (API Token):**
```bash
export KONG_API_TOKEN=your-api-token
```

### Port Configuration Examples
```bash
# Use default port 8080 (no environment variable needed)
python -m kong_mcp_server.server
./scripts/server.sh start

# Change to custom port
FASTMCP_PORT=9000 python -m kong_mcp_server.server
FASTMCP_PORT=9000 ./scripts/server.sh start

# Docker with custom port
docker run -p 9000:9000 -e FASTMCP_PORT=9000 kong-mcp-server
```

## Tools

Tools are configured in `tools_config.json`. Set `"enabled": true` to activate:

- **hello_world**: Test tool
- **Kong Services**: CRUD operations for Kong services
  - `kong_get_services`, `kong_create_service`, `kong_update_service`, `kong_delete_service`
- **Kong Routes**: CRUD operations for Kong routes  
  - `kong_get_routes`, `kong_create_route`, `kong_update_route`, `kong_delete_route`

### Adding New Tools

1. Create module in `src/kong_mcp_server/tools/`
2. Implement tool functions
3. Add configuration to `tools_config.json`
4. Set `"enabled": true`

### Architecture

```
src/kong_mcp_server/
├── server.py                # Main MCP server
├── tools_config.json        # Tool configuration
├── kong_client.py          # Kong HTTP client
└── tools/                  # Tool modules
    ├── basic.py
    ├── kong_services.py
    └── kong_routes.py
```

## Development

### Code Quality
```bash
flake8 src/ tests/
mypy src/
black src/ tests/
isort src/ tests/
```

### Testing
```bash
pytest                                       # Run tests
pytest --cov=kong_mcp_server --cov-report=term-missing
pytest --cov=kong_mcp_server --cov-report=xml           # Generate XML report
```

### Integration Testing
```bash
RUN_LIVE_TESTS=true pytest tests/test_kong_integration.py  # Requires testcontainers
```

## Docker

```bash
# Build and run
docker build -t kong-mcp-server .
docker run -p 8080:8080 kong-mcp-server

# With environment variables
docker run -p 8080:8080 -e KONG_ADMIN_URL=http://kong:8001 kong-mcp-server
```

## MCP Client Configuration

### Claude Code Integration
```json
{
  "mcpServers": {
    "kong-rate-limiter": {
      "command": "kong-mcp-server",
      "args": [],
      "env": {
        "KONG_ADMIN_URL": "http://localhost:8001"
      }
    }
  }
}
```

### SSE Endpoint
- **URL**: `http://localhost:8080/sse/`
- **Protocol**: Server-Sent Events (SSE)
- **Content-Type**: `text/event-stream`

## Testing with MCP Inspector

```bash
# Start server
python -m kong_mcp_server.server

# In new terminal, run inspector
npx @modelcontextprotocol/inspector http://localhost:8080/sse/
```

## License

Apache 2.0