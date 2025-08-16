"""Tests for Kong MCP Server."""

from kong_mcp_server.server import mcp


def test_mcp_server_creation() -> None:
    """Test that MCP server is properly created."""
    assert mcp.name == "Kong Rate Limiter MCP Server"
    assert mcp is not None


def test_mcp_server_is_fastmcp_instance() -> None:
    """Test that MCP server is a FastMCP instance."""
    # Just verify the server is the right type
    from fastmcp import FastMCP

    assert isinstance(mcp, FastMCP)
