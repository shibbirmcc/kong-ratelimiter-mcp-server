# Kong Rate Limiter MCP Server

[![Build Status](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/workflows/CI/badge.svg)](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/actions)
[![Coverage](https://codecov.io/gh/shibbirmcc/kong-ratelimiter-mcp-server/branch/master/graph/badge.svg)](https://codecov.io/gh/shibbirmcc/kong-ratelimiter-mcp-server)
[![Release](https://img.shields.io/github/v/release/shibbirmcc/kong-ratelimiter-mcp-server)](https://github.com/shibbirmcc/kong-ratelimiter-mcp-server/releases)
[![Docker](https://img.shields.io/docker/pulls/shibbirmcc/kong-ratelimiter-mcp-server)](https://hub.docker.com/r/shibbirmcc/kong-ratelimiter-mcp-server)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

MCP Server for Kong Rate Limiter Configuration using FastMCP and SSE Transport.

## Quick Start

```bash
# Install dependencies
pip install -e .[dev]

# Run server
python -m kong_mcp_server.server

# Run tests
pytest

# Check coverage
pytest --cov=kong_mcp_server
```