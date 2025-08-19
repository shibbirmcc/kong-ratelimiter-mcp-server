# Kong Rate Limiter MCP Server

[![Build Status](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/workflows/CI/badge.svg)](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/actions)
[![Coverage](https://codecov.io/gh/shibbirmcc/kong-ratelimiter-mcp-server/branch/master/graph/badge.svg)](https://codecov.io/gh/shibbirmcc/kong-ratelimiter-mcp-server)
[![Release](https://img.shields.io/github/v/release/shibbirmcc/kong-ratelimiter-mcp-server)](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/releases)
[![Docker](https://img.shields.io/docker/pulls/shibbirmcc/kong-ratelimiter-mcp-server)](https://hub.docker.com/r/shibbirmcc/kong-ratelimiter-mcp-server)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Model Context Protocol (MCP) server for Kong configuration management, built with FastMCP and Server-Sent Events (SSE) transport. This server provides tools for managing Kong services, routes, and other configuration elements through a standardized MCP interface.

## Features

- **FastMCP Integration**: Built using the FastMCP SDK for efficient MCP server implementation
- **SSE Transport**: Uses Server-Sent Events for real-time communication with MCP clients
- **Modular Architecture**: Tools are organized in separate modules for easy extension
- **JSON Configuration**: External JSON configuration for tool management
- **Comprehensive Testing**: Unit and integration tests with high coverage
- **Kong HTTP Client**: HTTP client for Kong Admin API communication with authentication support
- **Extensible Design**: Easy to add new Kong configuration tools

## Quick Start

### Option 1: Using the Virtual Environment Script (Recommended)

```bash
# Activate virtual environment and install dependencies
./venv.sh

# Run server
python -m kong_mcp_server.server

# Run tests
pytest

# Check coverage
pytest --cov=kong_mcp_server

# Deactivate when done
./venv.sh deactivate
```

### Option 2: Manual Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Run server
python -m kong_mcp_server.server

# Run tests
pytest

# Check coverage
pytest --cov=kong_mcp_server
```

### Virtual Environment Script Commands

```bash
./venv.sh           # Activate venv and install dependencies (default)
./venv.sh activate  # Same as above
./venv.sh deactivate # Deactivate current virtual environment
./venv.sh clean     # Remove virtual environment directory
```

## Architecture

The MCP server follows a modular architecture:

```
src/kong_mcp_server/
├── __init__.py              # Package initialization
├── server.py                # Main MCP server implementation
├── tools_config.json        # Tool configuration (external JSON)
└── tools/                   # Tool modules
    ├── __init__.py
    ├── basic.py             # Basic tools (hello_world)
    ├── kong_services.py     # Kong services management
    └── kong_routes.py       # Kong routes management
```

### Tool Configuration

Tools are configured in `tools_config.json`:

```json
{
  "tools": {
    "hello_world": {
      "name": "hello_world",
      "description": "Simple Hello World tool for testing",
      "module": "kong_mcp_server.tools.basic",
      "function": "hello_world",
      "enabled": true
    },
    "kong_get_services": {
      "name": "kong_get_services",
      "description": "Retrieve Kong services configuration",
      "module": "kong_mcp_server.tools.kong_services",
      "function": "get_services",
      "enabled": false
    }
  }
}
```

### Available Tools

- **hello_world**: Basic test tool that returns a greeting message
- **Kong Services**: CRUD operations for Kong services via HTTP API
  - `kong_get_services`: Retrieve services
  - `kong_create_service`: Create new service
  - `kong_update_service`: Update existing service
  - `kong_delete_service`: Delete service
- **Kong Routes**: CRUD operations for Kong routes via HTTP API
  - `kong_get_routes`: Retrieve routes
  - `kong_create_route`: Create new route
  - `kong_update_route`: Update existing route
  - `kong_delete_route`: Delete route

### Adding New Tools

1. Create a new module in `src/kong_mcp_server/tools/`
2. Implement your tool functions
3. Add tool configuration to `tools_config.json`
4. Set `"enabled": true` to activate the tool

## Testing

The project includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kong_mcp_server --cov-report=term-missing

# Generate text coverage report
pytest --cov=kong_mcp_server --cov-report=xml
coverage report > coverage.txt
```

## Development

### Code Quality

```bash
# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Formatting
black src/ tests/
isort src/ tests/
```

## Docker Deployment

### Building the Docker Image

```bash
# Build the image
docker build -t kong-mcp-server .

# Or build with a specific tag
docker build -t kong-mcp-server:0.1.2 .
```

### Running with Docker

```bash
# Run the container
docker run -p 8000:8000 kong-mcp-server

# Run in detached mode
docker run -d -p 8000:8000 --name kong-mcp kong-mcp-server

# Run with environment variables (if needed)
docker run -p 8000:8000 -e KONG_ADMIN_URL=http://kong:8001 kong-mcp-server
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  kong-mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - KONG_ADMIN_URL=http://kong:8001
    restart: unless-stopped
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## LLM Agent Configuration

### Claude Code Integration

To use this MCP server with Claude Code, add the server configuration to your MCP client:

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

### Server-Sent Events (SSE) Endpoint

The server exposes an SSE endpoint for real-time communication:

- **Endpoint**: `http://localhost:8000/sse/`
- **Protocol**: Server-Sent Events (SSE)
- **Content-Type**: `text/event-stream`

### Configuration with Other MCP Clients

For other MCP clients, configure the connection as follows:

```yaml
# Example configuration
server:
  name: "Kong Rate Limiter MCP Server"
  transport: "sse"
  url: "http://localhost:8000/sse/"
  
tools:
  - hello_world
  - kong_get_services
  - kong_create_service
  # ... other tools as enabled in tools_config.json
```

## Kong Authentication Setup

The server supports two authentication methods for Kong Admin API:

### Kong Community Edition (Username/Password)

```bash
# Set Kong Admin credentials
export KONG_ADMIN_URL=http://localhost:8001
export KONG_USERNAME=admin
export KONG_PASSWORD=your-password
```

### Kong Enterprise Edition (API Token)

```bash
# Set Kong Admin API token
export KONG_ADMIN_URL=http://localhost:8001
export KONG_API_TOKEN=your-api-token
```

### Additional Configuration Options

```bash
# Request timeout in seconds (default: 30.0)
export KONG_TIMEOUT=45.0

# SSL certificate verification (default: true)
export KONG_VERIFY_SSL=false
```

## Environment Variables

Configure the server behavior using environment variables:

### Kong Configuration

```bash
# Kong Admin API URL (default: http://localhost:8001)
export KONG_ADMIN_URL=http://your-kong-instance:8001

# Kong Community Edition authentication
export KONG_USERNAME=admin
export KONG_PASSWORD=your-password

# Kong Enterprise Edition authentication (alternative to username/password)
export KONG_API_TOKEN=your-api-token

# Request timeout in seconds (default: 30.0)
export KONG_TIMEOUT=45.0

# SSL certificate verification (default: true)
export KONG_VERIFY_SSL=false
```

### Server Configuration

```bash
# Server port (default: 8000)
export PORT=8000

# Server host (default: 127.0.0.1)
export HOST=0.0.0.0
```

## Running with Different Configurations

### Local Python with Environment Variables

Create a `.env` file in the project root:

```env
KONG_ADMIN_URL=http://localhost:8001
KONG_USERNAME=admin
KONG_PASSWORD=secret
KONG_TIMEOUT=30.0
KONG_VERIFY_SSL=true
```

Then run:

```bash
# Load environment variables and run
python -m kong_mcp_server.server
```

### Docker with Environment Variables

```bash
# Run with Kong Community Edition authentication
docker run -p 8000:8000 \
  -e KONG_ADMIN_URL=http://kong:8001 \
  -e KONG_USERNAME=admin \
  -e KONG_PASSWORD=secret \
  kong-mcp-server

# Run with Kong Enterprise Edition authentication
docker run -p 8000:8000 \
  -e KONG_ADMIN_URL=http://kong:8001 \
  -e KONG_API_TOKEN=your-api-token \
  kong-mcp-server
```

### Docker Compose with Environment File

Create a `.env` file:

```env
KONG_ADMIN_URL=http://kong:8001
KONG_USERNAME=admin
KONG_PASSWORD=secret
```

Update `docker-compose.yml`:

```yaml
version: '3.8'
services:
  kong-mcp-server:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

### Custom Tool Configuration

Enable/disable tools by modifying `tools_config.json`:

```bash
# Enable Kong services management
# Set "enabled": true for kong_get_services, kong_create_service, etc.

# Restart the server after configuration changes
docker restart kong-mcp
```