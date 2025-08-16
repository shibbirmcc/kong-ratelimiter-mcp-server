"""Kong MCP Server - MCP Server for Kong Rate Limiter Configuration."""

try:
    from importlib.metadata import version

    __version__ = version("kong-ratelimiter-mcp-server")
except ImportError:
    __version__ = "unknown"
