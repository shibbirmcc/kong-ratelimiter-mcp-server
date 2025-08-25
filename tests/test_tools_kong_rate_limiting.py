"""Unit tests for Kong rate limiting plugin management tools."""

import pytest
from unittest.mock import AsyncMock, patch

from kong_mcp_server.tools.kong_rate_limiting import (
    create_rate_limiting_plugin,
    get_rate_limiting_plugins,
    update_rate_limiting_plugin,
    delete_rate_limiting_plugin,
    get_plugin,
    get_plugins,
)


@pytest.fixture
def mock_kong_client():
    """Mock Kong client fixture."""
    client = AsyncMock()
    with patch(
        "kong_mcp_server.tools.kong_rate_limiting.KongClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = client
        yield client


class TestBasicRateLimitingPlugin:
    """Test basic rate limiting plugin operations."""

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_minimal(self, mock_kong_client):
        """Test creating a basic rate limiting plugin with minimal configuration."""
        expected_response = {
            "id": "plugin-123",
            "name": "rate-limiting",
            "config": {
                "minute": 100,
                "limit_by": "consumer",
                "policy": "local",
                "fault_tolerant": True,
                "hide_client_headers": False,
            },
            "enabled": True,
        }
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin(minute=100)

        mock_kong_client.post.assert_called_once_with(
            "/plugins",
            json_data={
                "name": "rate-limiting",
                "config": {
                    "minute": 100,
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_full_config(self, mock_kong_client):
        """Test creating a rate limiting plugin with full configuration."""
        expected_response = {
            "id": "plugin-456",
            "name": "rate-limiting",
            "config": {
                "second": 10,
                "minute": 100,
                "hour": 1000,
                "day": 10000,
                "month": 100000,
                "year": 1000000,
                "limit_by": "ip",
                "policy": "redis",
                "fault_tolerant": False,
                "hide_client_headers": True,
                "redis_host": "redis.example.com",
                "redis_port": 6380,
                "redis_password": "secret",
                "redis_timeout": 5000,
                "redis_database": 1,
            },
            "enabled": True,
            "tags": ["production", "api"],
        }
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin(
            second=10,
            minute=100,
            hour=1000,
            day=10000,
            month=100000,
            year=1000000,
            limit_by="ip",
            policy="redis",
            fault_tolerant=False,
            hide_client_headers=True,
            redis_host="redis.example.com",
            redis_port=6380,
            redis_password="secret",
            redis_timeout=5000,
            redis_database=1,
            tags=["production", "api"],
        )

        expected_config = {
            "second": 10,
            "minute": 100,
            "hour": 1000,
            "day": 10000,
            "month": 100000,
            "year": 1000000,
            "limit_by": "ip",
            "policy": "redis",
            "fault_tolerant": False,
            "hide_client_headers": True,
            "redis_host": "redis.example.com",
            "redis_port": 6380,
            "redis_password": "secret",
            "redis_timeout": 5000,
            "redis_database": 1,
        }

        mock_kong_client.post.assert_called_once_with(
            "/plugins",
            json_data={
                "name": "rate-limiting",
                "config": expected_config,
                "enabled": True,
                "tags": ["production", "api"],
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_service_scope(self, mock_kong_client):
        """Test creating a rate limiting plugin scoped to a service."""
        expected_response = {"id": "plugin-789", "name": "rate-limiting"}
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin(
            minute=50, service_id="service-123"
        )

        mock_kong_client.post.assert_called_once_with(
            "/services/service-123/plugins",
            json_data={
                "name": "rate-limiting",
                "config": {
                    "minute": 50,
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_route_scope(self, mock_kong_client):
        """Test creating a rate limiting plugin scoped to a route."""
        expected_response = {"id": "plugin-101", "name": "rate-limiting"}
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin(
            hour=200, route_id="route-456"
        )

        mock_kong_client.post.assert_called_once_with(
            "/routes/route-456/plugins",
            json_data={
                "name": "rate-limiting",
                "config": {
                    "hour": 200,
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_consumer_scope(self, mock_kong_client):
        """Test creating a rate limiting plugin scoped to a consumer."""
        expected_response = {"id": "plugin-202", "name": "rate-limiting"}
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin(
            day=1000, consumer_id="consumer-789"
        )

        mock_kong_client.post.assert_called_once_with(
            "/consumers/consumer-789/plugins",
            json_data={
                "name": "rate-limiting",
                "config": {
                    "day": 1000,
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_rate_limiting_plugins(self, mock_kong_client):
        """Test retrieving rate limiting plugins."""
        expected_response = {
            "data": [
                {"id": "plugin-1", "name": "rate-limiting"},
                {"id": "plugin-2", "name": "rate-limiting"},
            ]
        }
        mock_kong_client.get.return_value = expected_response

        result = await get_rate_limiting_plugins()

        mock_kong_client.get.assert_called_once_with(
            "/plugins",
            params={
                "name": "rate-limiting",
                "size": 100,
            },
        )
        assert result == expected_response["data"]

    @pytest.mark.asyncio
    async def test_get_rate_limiting_plugins_with_filters(self, mock_kong_client):
        """Test retrieving rate limiting plugins with filters."""
        expected_response = {"data": [{"id": "plugin-3", "name": "rate-limiting"}]}
        mock_kong_client.get.return_value = expected_response

        result = await get_rate_limiting_plugins(
            service_id="service-123",
            size=50,
            offset="next-page",
            tags="production",
        )

        mock_kong_client.get.assert_called_once_with(
            "/services/service-123/plugins",
            params={
                "name": "rate-limiting",
                "size": 50,
                "offset": "next-page",
                "tags": "production",
            },
        )
        assert result == expected_response["data"]

    @pytest.mark.asyncio
    async def test_update_rate_limiting_plugin(self, mock_kong_client):
        """Test updating a rate limiting plugin."""
        expected_response = {
            "id": "plugin-123",
            "name": "rate-limiting",
            "config": {"minute": 200, "policy": "cluster"},
        }
        mock_kong_client.patch.return_value = expected_response

        result = await update_rate_limiting_plugin(
            plugin_id="plugin-123",
            minute=200,
            policy="cluster",
            enabled=False,
        )

        mock_kong_client.patch.assert_called_once_with(
            "/plugins/plugin-123",
            json_data={
                "config": {
                    "minute": 200,
                    "policy": "cluster",
                },
                "enabled": False,
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_update_rate_limiting_plugin_redis_config(self, mock_kong_client):
        """Test updating a rate limiting plugin with Redis configuration."""
        expected_response = {"id": "plugin-456", "name": "rate-limiting"}
        mock_kong_client.patch.return_value = expected_response

        result = await update_rate_limiting_plugin(
            plugin_id="plugin-456",
            redis_host="new-redis.example.com",
            redis_port=6381,
            redis_timeout=3000,
        )

        mock_kong_client.patch.assert_called_once_with(
            "/plugins/plugin-456",
            json_data={
                "config": {
                    "redis_host": "new-redis.example.com",
                    "redis_port": 6381,
                    "redis_timeout": 3000,
                },
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_delete_rate_limiting_plugin(self, mock_kong_client):
        """Test deleting a rate limiting plugin."""
        mock_kong_client.delete.return_value = None

        result = await delete_rate_limiting_plugin("plugin-123")

        mock_kong_client.delete.assert_called_once_with("/plugins/plugin-123")
        assert result == {
            "message": "Rate limiting plugin deleted successfully",
            "plugin_id": "plugin-123",
        }


class TestGeneralPluginManagement:
    """Test general plugin management operations."""

    @pytest.mark.asyncio
    async def test_get_plugin(self, mock_kong_client):
        """Test getting a specific plugin by ID."""
        expected_response = {
            "id": "plugin-123",
            "name": "rate-limiting",
            "config": {"minute": 100},
        }
        mock_kong_client.get_plugin.return_value = expected_response

        result = await get_plugin("plugin-123")

        mock_kong_client.get_plugin.assert_called_once_with("plugin-123")
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_plugins_no_filters(self, mock_kong_client):
        """Test getting all plugins without filters."""
        expected_response = {
            "data": [
                {"id": "plugin-1", "name": "rate-limiting"},
                {"id": "plugin-2", "name": "cors"},
            ]
        }
        mock_kong_client.get.return_value = expected_response

        result = await get_plugins()

        mock_kong_client.get.assert_called_once_with(
            "/plugins",
            params={"size": 100},
        )
        assert result == expected_response["data"]

    @pytest.mark.asyncio
    async def test_get_plugins_with_filters(self, mock_kong_client):
        """Test getting plugins with filters."""
        expected_response = {
            "data": [{"id": "plugin-3", "name": "rate-limiting"}]
        }
        mock_kong_client.get.return_value = expected_response

        result = await get_plugins(
            name="rate-limiting",
            service_id="service-123",
            size=50,
            offset="next-page",
            tags="production",
        )

        mock_kong_client.get.assert_called_once_with(
            "/services/service-123/plugins",
            params={
                "name": "rate-limiting",
                "size": 50,
                "offset": "next-page",
                "tags": "production",
            },
        )
        assert result == expected_response["data"]

    @pytest.mark.asyncio
    async def test_get_plugins_route_scope(self, mock_kong_client):
        """Test getting plugins scoped to a route."""
        expected_response = {"data": [{"id": "plugin-4", "name": "cors"}]}
        mock_kong_client.get.return_value = expected_response

        result = await get_plugins(route_id="route-456")

        mock_kong_client.get.assert_called_once_with(
            "/routes/route-456/plugins",
            params={"size": 100},
        )
        assert result == expected_response["data"]

    @pytest.mark.asyncio
    async def test_get_plugins_consumer_scope(self, mock_kong_client):
        """Test getting plugins scoped to a consumer."""
        expected_response = {"data": [{"id": "plugin-5", "name": "key-auth"}]}
        mock_kong_client.get.return_value = expected_response

        result = await get_plugins(consumer_id="consumer-789")

        mock_kong_client.get.assert_called_once_with(
            "/consumers/consumer-789/plugins",
            params={"size": 100},
        )
        assert result == expected_response["data"]


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_no_limits(self, mock_kong_client):
        """Test creating a rate limiting plugin with no time limits specified."""
        expected_response = {
            "id": "plugin-no-limits",
            "name": "rate-limiting",
            "config": {
                "limit_by": "consumer",
                "policy": "local",
                "fault_tolerant": True,
                "hide_client_headers": False,
            },
            "enabled": True,
        }
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin()

        mock_kong_client.post.assert_called_once_with(
            "/plugins",
            json_data={
                "name": "rate-limiting",
                "config": {
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
            },
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_update_rate_limiting_plugin_no_changes(self, mock_kong_client):
        """Test updating a rate limiting plugin with no changes."""
        expected_response = {"id": "plugin-123", "name": "rate-limiting"}
        mock_kong_client.patch.return_value = expected_response

        result = await update_rate_limiting_plugin("plugin-123")

        mock_kong_client.patch.assert_called_once_with(
            "/plugins/plugin-123",
            json_data={},
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_local_policy_no_redis(
        self, mock_kong_client
    ):
        """Test creating a rate limiting plugin with local policy (no Redis config)."""
        expected_response = {
            "id": "plugin-local",
            "name": "rate-limiting",
            "config": {
                "minute": 50,
                "limit_by": "consumer",
                "policy": "local",
                "fault_tolerant": True,
                "hide_client_headers": False,
            },
            "enabled": True,
        }
        mock_kong_client.post.return_value = expected_response

        result = await create_rate_limiting_plugin(
            minute=50,
            policy="local",
            redis_host="redis.example.com",  # Should be ignored for local policy
            redis_port=6380,
        )

        # Redis config should not be included for local policy
        mock_kong_client.post.assert_called_once_with(
            "/plugins",
            json_data={
                "name": "rate-limiting",
                "config": {
                    "minute": 50,
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
            },
        )
        assert result == expected_response
