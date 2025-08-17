"""Tests for Kong services tools."""

import pytest

from kong_mcp_server.tools.kong_services import (
    create_service,
    delete_service,
    get_services,
    update_service,
)


@pytest.mark.asyncio
async def test_get_services() -> None:
    """Test get_services function returns placeholder response."""
    result = await get_services()

    assert isinstance(result, list)
    assert len(result) == 1
    assert (
        result[0]["message"] == "Kong services retrieval not yet implemented"
    )


@pytest.mark.asyncio
async def test_create_service() -> None:
    """Test create_service function returns placeholder response."""
    result = await create_service(
        name="test-service", url="http://example.com", protocol="https"
    )

    assert isinstance(result, dict)
    assert result["message"] == "Kong service creation not yet implemented"
    assert result["name"] == "test-service"
    assert result["url"] == "http://example.com"
    assert result["protocol"] == "https"


@pytest.mark.asyncio
async def test_create_service_with_optional_params() -> None:
    """Test create_service function with optional parameters."""
    result = await create_service(
        name="test-service",
        url="http://example.com",
        protocol="https",
        host="example.com",
        port=8080,
        path="/api",
    )

    assert isinstance(result, dict)
    assert result["message"] == "Kong service creation not yet implemented"
    assert result["name"] == "test-service"
    assert result["url"] == "http://example.com"
    assert result["protocol"] == "https"


@pytest.mark.asyncio
async def test_update_service() -> None:
    """Test update_service function returns placeholder response."""
    result = await update_service(service_id="test-id", name="updated-service")

    assert isinstance(result, dict)
    assert result["message"] == "Kong service update not yet implemented"
    assert result["service_id"] == "test-id"


@pytest.mark.asyncio
async def test_update_service_with_all_params() -> None:
    """Test update_service function with all parameters."""
    result = await update_service(
        service_id="test-id",
        name="updated-service",
        url="http://updated.com",
        protocol="https",
        host="updated.com",
        port=9090,
        path="/v2",
    )

    assert isinstance(result, dict)
    assert result["message"] == "Kong service update not yet implemented"
    assert result["service_id"] == "test-id"


@pytest.mark.asyncio
async def test_delete_service() -> None:
    """Test delete_service function returns placeholder response."""
    result = await delete_service(service_id="test-id")

    assert isinstance(result, dict)
    assert result["message"] == "Kong service deletion not yet implemented"
    assert result["service_id"] == "test-id"
