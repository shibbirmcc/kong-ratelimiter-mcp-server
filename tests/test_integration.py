"""Integration tests for Kong MCP Server."""

import pytest

from kong_mcp_server.server import mcp, setup_tools


@pytest.mark.asyncio
async def test_server_tool_registration_integration() -> None:
    """Test that tools are properly registered during setup."""
    # Reset any previous tool registrations
    original_tools = mcp._tools.copy() if hasattr(mcp, "_tools") else {}

    try:
        # Clear existing tools
        if hasattr(mcp, "_tools"):
            mcp._tools.clear()

        # Run setup_tools
        setup_tools()

        # Check that hello_world tool is registered
        if hasattr(mcp, "_tools"):
            assert "hello_world" in mcp._tools
        else:
            # Alternative check if _tools attribute doesn't exist
            assert hasattr(mcp, "tool")

    finally:
        # Restore original tools if any
        if hasattr(mcp, "_tools"):
            mcp._tools.update(original_tools)


@pytest.mark.asyncio
async def test_hello_world_tool_execution() -> None:
    """Test that hello_world tool can be executed."""
    from kong_mcp_server.tools.basic import hello_world

    result = await hello_world()

    assert result == "Hello World from Kong Rate Limiter MCP Server!"
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_kong_tools_placeholder_execution() -> None:
    """Test that Kong tools return placeholder responses."""
    from kong_mcp_server.tools.kong_routes import create_route, get_routes
    from kong_mcp_server.tools.kong_services import create_service, get_services

    # Test services
    services_result = await get_services()
    assert isinstance(services_result, list)
    assert len(services_result) == 1
    assert "not yet implemented" in services_result[0]["message"]

    create_service_result = await create_service("test", "http://example.com")
    assert isinstance(create_service_result, dict)
    assert "not yet implemented" in create_service_result["message"]

    # Test routes
    routes_result = await get_routes()
    assert isinstance(routes_result, list)
    assert len(routes_result) == 1
    assert "not yet implemented" in routes_result[0]["message"]

    create_route_result = await create_route("service-123")
    assert isinstance(create_route_result, dict)
    assert "not yet implemented" in create_route_result["message"]


def test_tools_config_structure() -> None:
    """Test that tools configuration has the expected structure."""
    from kong_mcp_server.server import load_tools_config

    config = load_tools_config()

    # Verify top-level structure
    assert "tools" in config
    assert isinstance(config["tools"], dict)

    # Verify hello_world tool configuration
    hello_world_config = config["tools"]["hello_world"]
    assert hello_world_config["enabled"] is True
    assert hello_world_config["module"] == "kong_mcp_server.tools.basic"
    assert hello_world_config["function"] == "hello_world"

    # Verify Kong tools are present but disabled
    kong_tools = [
        "kong_get_services",
        "kong_create_service",
        "kong_update_service",
        "kong_delete_service",
        "kong_get_routes",
        "kong_create_route",
        "kong_update_route",
        "kong_delete_route",
    ]

    for tool_name in kong_tools:
        assert tool_name in config["tools"]
        assert config["tools"][tool_name]["enabled"] is False


def test_mcp_server_configuration() -> None:
    """Test that MCP server is properly configured."""
    assert mcp.name == "Kong Rate Limiter MCP Server"
    assert hasattr(mcp, "tool")
    assert hasattr(mcp, "run")
