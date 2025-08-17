"""Tests for basic tools."""

import pytest

from kong_mcp_server.tools.basic import hello_world


@pytest.mark.asyncio
async def test_hello_world() -> None:
    """Test hello_world function returns expected message."""
    result = await hello_world()

    assert result == "Hello World from Kong Rate Limiter MCP Server!"
    assert isinstance(result, str)
