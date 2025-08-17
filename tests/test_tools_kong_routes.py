"""Tests for Kong routes tools."""

import pytest

from kong_mcp_server.tools.kong_routes import (
    create_route,
    delete_route,
    get_routes,
    update_route,
)


@pytest.mark.asyncio
async def test_get_routes() -> None:
    """Test get_routes function returns placeholder response."""
    result = await get_routes()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["message"] == "Kong routes retrieval not yet implemented"


@pytest.mark.asyncio
async def test_create_route() -> None:
    """Test create_route function returns placeholder response."""
    result = await create_route(service_id="service-123", name="test-route")

    assert isinstance(result, dict)
    assert result["message"] == "Kong route creation not yet implemented"
    assert result["service_id"] == "service-123"
    assert result["name"] == "test-route"


@pytest.mark.asyncio
async def test_create_route_with_optional_params() -> None:
    """Test create_route function with optional parameters."""
    result = await create_route(
        service_id="service-123",
        name="test-route",
        protocols=["http", "https"],
        methods=["GET", "POST"],
        hosts=["example.com"],
        paths=["/api", "/v1"],
    )

    assert isinstance(result, dict)
    assert result["message"] == "Kong route creation not yet implemented"
    assert result["service_id"] == "service-123"
    assert result["name"] == "test-route"


@pytest.mark.asyncio
async def test_update_route() -> None:
    """Test update_route function returns placeholder response."""
    result = await update_route(route_id="route-456", name="updated-route")

    assert isinstance(result, dict)
    assert result["message"] == "Kong route update not yet implemented"
    assert result["route_id"] == "route-456"


@pytest.mark.asyncio
async def test_update_route_with_all_params() -> None:
    """Test update_route function with all parameters."""
    result = await update_route(
        route_id="route-456",
        service_id="service-789",
        name="updated-route",
        protocols=["https"],
        methods=["PUT", "DELETE"],
        hosts=["api.example.com"],
        paths=["/v2/api"],
    )

    assert isinstance(result, dict)
    assert result["message"] == "Kong route update not yet implemented"
    assert result["route_id"] == "route-456"


@pytest.mark.asyncio
async def test_delete_route() -> None:
    """Test delete_route function returns placeholder response."""
    result = await delete_route(route_id="route-456")

    assert isinstance(result, dict)
    assert result["message"] == "Kong route deletion not yet implemented"
    assert result["route_id"] == "route-456"
