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
- **Kong Tools**: Placeholder implementations for Kong services and routes management
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
- **Kong Services**: CRUD operations for Kong services (placeholder)
  - `kong_get_services`: Retrieve services
  - `kong_create_service`: Create new service
  - `kong_update_service`: Update existing service
  - `kong_delete_service`: Delete service
- **Kong Routes**: CRUD operations for Kong routes (placeholder)
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
pytest --cov=kong_mcp_server --cov-report=txt
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