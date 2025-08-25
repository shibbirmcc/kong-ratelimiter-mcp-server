"""Integration tests for Kong rate limiting plugin management tools."""

import os
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
def kong_admin_url():
    """Kong Admin API URL fixture."""
    return os.getenv("KONG_ADMIN_URL", "http://localhost:8001")


@pytest.fixture
def mock_kong_responses():
    """Mock Kong API responses for integration tests."""
    return {
        "services": [
            {
                "id": "test-service-1",
                "name": "test-service",
                "url": "http://httpbin.org",
                "protocol": "http",
                "host": "httpbin.org",
                "port": 80,
                "path": "/",
            }
        ],
        "routes": [
            {
                "id": "test-route-1",
                "name": "test-route",
                "paths": ["/test"],
                "methods": ["GET", "POST"],
                "service": {"id": "test-service-1"},
            }
        ],
        "consumers": [
            {
                "id": "test-consumer-1",
                "username": "test-user",
                "custom_id": "test-123",
            }
        ],
        "plugins": {
            "basic": {
                "id": "test-plugin-basic-1",
                "name": "rate-limiting",
                "config": {
                    "minute": 100,
                    "limit_by": "consumer",
                    "policy": "local",
                    "fault_tolerant": True,
                    "hide_client_headers": False,
                },
                "enabled": True,
                "service": {"id": "test-service-1"},
            },
            "advanced": {
                "id": "test-plugin-advanced-1",
                "name": "rate-limiting-advanced",
                "config": {
                    "limit": [{"minute": 5}, {"hour": 100}],
                    "window_size": [60, 3600],
                    "identifier": "consumer",
                    "strategy": "local",
                    "hide_client_headers": False,
                },
                "enabled": True,
                "route": {"id": "test-route-1"},
            },
        },
    }


class TestBasicRateLimitingIntegration:
    """Integration tests for basic rate limiting plugin operations."""

    @pytest.mark.asyncio
    async def test_create_and_delete_global_rate_limiting_plugin(self, mock_kong_responses):
        """Test creating and deleting a global rate limiting plugin."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock create plugin response
            create_response = mock_kong_responses["plugins"]["basic"].copy()
            create_response["id"] = "integration-test-plugin-1"
            mock_client.request.return_value = create_response

            # Create plugin
            result = await create_rate_limiting_plugin(
                minute=50,
                hour=500,
                limit_by="ip",
                policy="local",
                fault_tolerant=True,
            )

            assert result["id"] == "integration-test-plugin-1"
            assert result["name"] == "rate-limiting"
            assert result["config"]["minute"] == 100  # From mock response
            
            # Verify the request was made correctly
            mock_client.request.assert_called_with(
                method="POST",
                url="/plugins",
                params=None,
                json={
                    "name": "rate-limiting",
                    "config": {
                        "minute": 50,
                        "hour": 500,
                        "limit_by": "ip",
                        "policy": "local",
                        "fault_tolerant": True,
                        "hide_client_headers": False,
                    },
                    "enabled": True,
                },
            )

            # Mock delete response
            mock_client.request.return_value = {}
            
            # Delete plugin
            delete_result = await delete_rate_limiting_plugin("integration-test-plugin-1")
            
            assert delete_result["message"] == "Rate limiting plugin deleted successfully"
            assert delete_result["plugin_id"] == "integration-test-plugin-1"

    @pytest.mark.asyncio
    async def test_create_service_scoped_rate_limiting_plugin(self, mock_kong_responses):
        """Test creating a service-scoped rate limiting plugin."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            create_response = mock_kong_responses["plugins"]["basic"].copy()
            create_response["id"] = "service-scoped-plugin-1"
            mock_client.request.return_value = create_response

            result = await create_rate_limiting_plugin(
                minute=25,
                service_id="test-service-1",
                limit_by="consumer",
                policy="local",
            )

            assert result["id"] == "service-scoped-plugin-1"
            
            # Verify service-scoped endpoint was used
            mock_client.request.assert_called_with(
                method="POST",
                url="/services/test-service-1/plugins",
                params=None,
                json={
                    "name": "rate-limiting",
                    "config": {
                        "minute": 25,
                        "limit_by": "consumer",
                        "policy": "local",
                        "fault_tolerant": True,
                        "hide_client_headers": False,
                    },
                    "enabled": True,
                },
            )

    @pytest.mark.asyncio
    async def test_create_route_scoped_rate_limiting_plugin(self, mock_kong_responses):
        """Test creating a route-scoped rate limiting plugin."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            create_response = mock_kong_responses["plugins"]["basic"].copy()
            create_response["id"] = "route-scoped-plugin-1"
            mock_client.request.return_value = create_response

            result = await create_rate_limiting_plugin(
                hour=100,
                route_id="test-route-1",
                limit_by="ip",
                policy="cluster",
            )

            assert result["id"] == "route-scoped-plugin-1"
            
            # Verify route-scoped endpoint was used
            mock_client.request.assert_called_with(
                method="POST",
                url="/routes/test-route-1/plugins",
                params=None,
                json={
                    "name": "rate-limiting",
                    "config": {
                        "hour": 100,
                        "limit_by": "ip",
                        "policy": "cluster",
                        "fault_tolerant": True,
                        "hide_client_headers": False,
                    },
                    "enabled": True,
                },
            )

    @pytest.mark.asyncio
    async def test_create_consumer_scoped_rate_limiting_plugin(self, mock_kong_responses):
        """Test creating a consumer-scoped rate limiting plugin."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            create_response = mock_kong_responses["plugins"]["basic"].copy()
            create_response["id"] = "consumer-scoped-plugin-1"
            mock_client.request.return_value = create_response

            result = await create_rate_limiting_plugin(
                day=1000,
                consumer_id="test-consumer-1",
                limit_by="consumer",
                policy="redis",
                redis_host="redis.example.com",
                redis_port=6379,
                redis_password="secret",
            )

            assert result["id"] == "consumer-scoped-plugin-1"
            
            # Verify consumer-scoped endpoint was used
            mock_client.request.assert_called_with(
                method="POST",
                url="/consumers/test-consumer-1/plugins",
                params=None,
                json={
                    "name": "rate-limiting",
                    "config": {
                        "day": 1000,
                        "limit_by": "consumer",
                        "policy": "redis",
                        "fault_tolerant": True,
                        "hide_client_headers": False,
                        "redis_host": "redis.example.com",
                        "redis_port": 6379,
                        "redis_password": "secret",
                        "redis_timeout": 2000,
                        "redis_database": 0,
                    },
                    "enabled": True,
                },
            )

    @pytest.mark.asyncio
    async def test_get_rate_limiting_plugins_with_pagination(self, mock_kong_responses):
        """Test retrieving rate limiting plugins with pagination."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock paginated response
            paginated_response = {
                "data": [
                    mock_kong_responses["plugins"]["basic"],
                    {
                        "id": "test-plugin-basic-2",
                        "name": "rate-limiting",
                        "config": {"minute": 200},
                        "enabled": True,
                    },
                ],
                "next": "http://localhost:8001/plugins?offset=next-page-token",
            }
            mock_client.request.return_value = paginated_response

            result = await get_rate_limiting_plugins(
                size=50,
                offset="current-page-token",
                tags="production",
            )

            assert len(result) == 2
            assert result[0]["id"] == "test-plugin-basic-1"
            assert result[1]["id"] == "test-plugin-basic-2"
            
            # Verify request parameters
            mock_client.request.assert_called_with(
                method="GET",
                url="/plugins",
                params={
                    "name": "rate-limiting",
                    "size": 50,
                    "offset": "current-page-token",
                    "tags": "production",
                },
                json=None,
            )

    @pytest.mark.asyncio
    async def test_update_rate_limiting_plugin_configuration(self, mock_kong_responses):
        """Test updating rate limiting plugin configuration."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock update response
            updated_response = mock_kong_responses["plugins"]["basic"].copy()
            updated_response["config"]["minute"] = 150
            updated_response["config"]["policy"] = "cluster"
            updated_response["enabled"] = False
            mock_client.request.return_value = updated_response

            result = await update_rate_limiting_plugin(
                plugin_id="test-plugin-basic-1",
                minute=150,
                policy="cluster",
                enabled=False,
                tags=["updated", "production"],
            )

            assert result["config"]["minute"] == 150
            assert result["config"]["policy"] == "cluster"
            assert result["enabled"] == False
            
            # Verify update request
            mock_client.request.assert_called_with(
                method="PATCH",
                url="/plugins/test-plugin-basic-1",
                params=None,
                json={
                    "config": {
                        "minute": 150,
                        "policy": "cluster",
                    },
                    "enabled": False,
                    "tags": ["updated", "production"],
                },
            )


class TestAdvancedRateLimitingIntegration:
    """Integration tests for advanced rate limiting plugin operations."""

    @pytest.mark.asyncio
    async def test_create_advanced_rate_limiting_plugin_with_multiple_limits(self, mock_kong_responses):
        """Test creating an advanced rate limiting plugin with multiple limits."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            create_response = mock_kong_responses["plugins"]["advanced"].copy()
            create_response["id"] = "advanced-multi-limit-1"
            mock_client.request.return_value = create_response

            result = await create_rate_limiting_advanced_plugin(
                limit=[{"minute": 10}, {"hour": 200}, {"day": 2000}],
                window_size=[60, 3600, 86400],
                identifier="ip",
                strategy="redis",
                sync_rate=0.8,
                namespace="api-v2",
                redis_host="redis-cluster.example.com",
                redis_port=6380,
                redis_ssl=True,
                redis_ssl_verify=True,
                tags=["advanced", "multi-limit"],
            )

            assert result["id"] == "advanced-multi-limit-1"
            assert result["name"] == "rate-limiting-advanced"
            
            # Verify the complex configuration was sent correctly
            mock_client.request.assert_called_with(
                method="POST",
                url="/plugins",
                params=None,
                json={
                    "name": "rate-limiting-advanced",
                    "config": {
                        "limit": [{"minute": 10}, {"hour": 200}, {"day": 2000}],
                        "window_size": [60, 3600, 86400],
                        "identifier": "ip",
                        "strategy": "redis",
                        "sync_rate": 0.8,
                        "namespace": "api-v2",
                        "hide_client_headers": False,
                        "redis_host": "redis-cluster.example.com",
                        "redis_port": 6380,
                        "redis_timeout": 2000,
                        "redis_database": 0,
                        "redis_ssl": True,
                        "redis_ssl_verify": True,
                    },
                    "enabled": True,
                    "tags": ["advanced", "multi-limit"],
                },
            )

    @pytest.mark.asyncio
    async def test_create_advanced_rate_limiting_plugin_service_scoped(self, mock_kong_responses):
        """Test creating a service-scoped advanced rate limiting plugin."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            create_response = mock_kong_responses["plugins"]["advanced"].copy()
            create_response["id"] = "advanced-service-scoped-1"
            mock_client.request.return_value = create_response

            result = await create_rate_limiting_advanced_plugin(
                limit=[{"second": 5}, {"minute": 100}],
                window_size=[1, 60],
                service_id="test-service-1",
                identifier="consumer",
                strategy="local",
            )

            assert result["id"] == "advanced-service-scoped-1"
            
            # Verify service-scoped endpoint was used
            mock_client.request.assert_called_with(
                method="POST",
                url="/services/test-service-1/plugins",
                params=None,
                json={
                    "name": "rate-limiting-advanced",
                    "config": {
                        "limit": [{"second": 5}, {"minute": 100}],
                        "window_size": [1, 60],
                        "identifier": "consumer",
                        "strategy": "local",
                        "hide_client_headers": False,
                    },
                    "enabled": True,
                },
            )

    @pytest.mark.asyncio
    async def test_get_advanced_rate_limiting_plugins_filtered(self, mock_kong_responses):
        """Test retrieving advanced rate limiting plugins with filters."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            filtered_response = {
                "data": [mock_kong_responses["plugins"]["advanced"]],
            }
            mock_client.request.return_value = filtered_response

            result = await get_rate_limiting_advanced_plugins(
                route_id="test-route-1",
                size=25,
                tags="advanced,production",
            )

            assert len(result) == 1
            assert result[0]["id"] == "test-plugin-advanced-1"
            assert result[0]["name"] == "rate-limiting-advanced"
            
            # Verify filtered request
            mock_client.request.assert_called_with(
                method="GET",
                url="/routes/test-route-1/plugins",
                params={
                    "name": "rate-limiting-advanced",
                    "size": 25,
                    "tags": "advanced,production",
                },
                json=None,
            )

    @pytest.mark.asyncio
    async def test_update_advanced_rate_limiting_plugin_redis_config(self, mock_kong_responses):
        """Test updating advanced rate limiting plugin Redis configuration."""
        with patch("kong_mcp_server.tools.kong_rate_limiting.KongClient") as mock_client_class:
            # Mock the Kong client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            updated_response = mock_kong_responses["plugins"]["advanced"].copy()
            updated_response["config"]["strategy"] = "redis"
            updated_response["config"]["redis_host"] = "new-redis.example.com"
            mock_client.request.return_value = updated_response

            result = await update_rate_limiting_advanced_plugin(
                plugin_id="test-plugin-advanced-1",
                strategy="redis",
                redis_host="new-redis.example.com",
                redis_port=6381,
                redis_password="new-secret",
                redis_timeout=5000,
                redis_ssl=True,
                redis_server_name="redis.example.com",
            )

            assert result["config"]["strategy"] == "redis"
            assert result["config"]["redis_host"] == "new-redis.example.com"
            
            # Verify Redis configuration update
            mock_client.request.assert_called_with(
                method="PATCH",
                url="/plugins/test-plugin-advanced-1",
                params=None,
                json={
                    "config": {
                        "strategy": "redis",
                        "redis_host": "new-redis.example.com",
                        "redis_port": 6381,
                        "redis_password": "new-secret",
                        "redis_timeout": 5000,
                        "redis_ssl": True,
                        "redis_server_name": "redis.example.com",
                    },
                },
            )


class TestGeneralPluginIntegration:
    """Integration tests for general plugin management operations."""

    @pytest.mark.asyncio
    async def test_get_plugin_by_id(self, mock_kong_responses):
        """Test getting a specific plugin by ID."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            plugin_response = mock_kong_responses["plugins"]["basic"]
            mock_instance.request.return_value.json.return_value = plugin_response
            mock_instance.request.return_value.raise_for_status.return_value = None

            result = await get_plugin("test-plugin-basic-1")

            assert result["id"] == "test-plugin-basic-1"
            assert result["name"] == "rate-limiting"
            
            # Verify get plugin request
            mock_instance.request.assert_called_with(
                method="GET",
                url="/plugins/test-plugin-basic-1",
                params=None,
                json=None,
            )

    @pytest.mark.asyncio
    async def test_get_all_plugins_with_filters(self, mock_kong_responses):
        """Test getting all plugins with various filters."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            all_plugins_response = {
                "data": [
                    mock_kong_responses["plugins"]["basic"],
                    mock_kong_responses["plugins"]["advanced"],
                    {
                        "id": "test-plugin-cors-1",
                        "name": "cors",
                        "config": {"origins": ["*"]},
                        "enabled": True,
                    },
                ],
            }
            mock_instance.request.return_value.json.return_value = all_plugins_response
            mock_instance.request.return_value.raise_for_status.return_value = None

            result = await get_plugins(
                name="rate-limiting",
                size=100,
                tags="production",
            )

            assert len(result) == 3
            plugin_names = [plugin["name"] for plugin in result]
            assert "rate-limiting" in plugin_names
            assert "rate-limiting-advanced" in plugin_names
            assert "cors" in plugin_names
            
            # Verify filtered request
            mock_instance.request.assert_called_with(
                method="GET",
                url="/plugins",
                params={
                    "name": "rate-limiting",
                    "size": 100,
                    "tags": "production",
                },
                json=None,
            )

    @pytest.mark.asyncio
    async def test_get_plugins_multiple_scopes(self, mock_kong_responses):
        """Test getting plugins from different scopes."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            # Test service-scoped plugins
            service_plugins_response = {
                "data": [mock_kong_responses["plugins"]["basic"]],
            }
            mock_instance.request.return_value.json.return_value = service_plugins_response
            mock_instance.request.return_value.raise_for_status.return_value = None

            service_result = await get_plugins(service_id="test-service-1")
            assert len(service_result) == 1
            assert service_result[0]["id"] == "test-plugin-basic-1"

            # Test route-scoped plugins
            route_plugins_response = {
                "data": [mock_kong_responses["plugins"]["advanced"]],
            }
            mock_instance.request.return_value.json.return_value = route_plugins_response

            route_result = await get_plugins(route_id="test-route-1")
            assert len(route_result) == 1
            assert route_result[0]["id"] == "test-plugin-advanced-1"

            # Test consumer-scoped plugins
            consumer_plugins_response = {
                "data": [
                    {
                        "id": "test-plugin-consumer-1",
                        "name": "key-auth",
                        "config": {"key_names": ["apikey"]},
                        "enabled": True,
                    }
                ],
            }
            mock_instance.request.return_value.json.return_value = consumer_plugins_response

            consumer_result = await get_plugins(consumer_id="test-consumer-1")
            assert len(consumer_result) == 1
            assert consumer_result[0]["id"] == "test-plugin-consumer-1"
            assert consumer_result[0]["name"] == "key-auth"


class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_create_rate_limiting_plugin_with_invalid_config(self):
        """Test creating a rate limiting plugin with invalid configuration."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock HTTP error response
            from httpx import HTTPStatusError, Response, Request
            
            error_response = Response(
                status_code=400,
                json={"message": "Invalid configuration"},
                request=Request("POST", "http://localhost:8001/plugins"),
            )
            mock_instance.request.return_value = error_response
            mock_instance.request.return_value.raise_for_status.side_effect = HTTPStatusError(
                "Bad Request", request=error_response.request, response=error_response
            )

            with pytest.raises(HTTPStatusError) as exc_info:
                await create_rate_limiting_plugin(
                    minute=-1,  # Invalid negative value
                    limit_by="invalid_entity",  # Invalid limit_by value
                )
            
            assert exc_info.value.response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_nonexistent_plugin(self):
        """Test getting a plugin that doesn't exist."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock 404 response
            from httpx import HTTPStatusError, Response, Request
            
            error_response = Response(
                status_code=404,
                json={"message": "Not found"},
                request=Request("GET", "http://localhost:8001/plugins/nonexistent"),
            )
            mock_instance.request.return_value = error_response
            mock_instance.request.return_value.raise_for_status.side_effect = HTTPStatusError(
                "Not Found", request=error_response.request, response=error_response
            )

            with pytest.raises(HTTPStatusError) as exc_info:
                await get_plugin("nonexistent-plugin-id")
            
            assert exc_info.value.response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_plugin_with_conflicting_config(self):
        """Test updating a plugin with conflicting configuration."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock conflict response
            from httpx import HTTPStatusError, Response, Request
            
            error_response = Response(
                status_code=409,
                json={"message": "Configuration conflict"},
                request=Request("PATCH", "http://localhost:8001/plugins/test-plugin"),
            )
            mock_instance.request.return_value = error_response
            mock_instance.request.return_value.raise_for_status.side_effect = HTTPStatusError(
                "Conflict", request=error_response.request, response=error_response
            )

            with pytest.raises(HTTPStatusError) as exc_info:
                await update_rate_limiting_plugin(
                    plugin_id="test-plugin",
                    policy="redis",
                    # Missing required Redis configuration
                )
            
            assert exc_info.value.response.status_code == 409

    @pytest.mark.asyncio
    async def test_delete_nonexistent_plugin(self):
        """Test deleting a plugin that doesn't exist."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock 404 response for delete
            from httpx import HTTPStatusError, Response, Request
            
            error_response = Response(
                status_code=404,
                json={"message": "Not found"},
                request=Request("DELETE", "http://localhost:8001/plugins/nonexistent"),
            )
            mock_instance.request.return_value = error_response
            mock_instance.request.return_value.raise_for_status.side_effect = HTTPStatusError(
                "Not Found", request=error_response.request, response=error_response
            )

            with pytest.raises(HTTPStatusError) as exc_info:
                await delete_rate_limiting_plugin("nonexistent-plugin-id")
            
            assert exc_info.value.response.status_code == 404


class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_complete_rate_limiting_workflow(self, mock_kong_responses):
        """Test a complete workflow: create, get, update, delete."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.request.return_value.raise_for_status.return_value = None

            # Step 1: Create a rate limiting plugin
            create_response = mock_kong_responses["plugins"]["basic"].copy()
            create_response["id"] = "workflow-plugin-1"
            mock_instance.request.return_value.json.return_value = create_response

            created_plugin = await create_rate_limiting_plugin(
                minute=100,
                hour=1000,
                service_id="test-service-1",
                limit_by="consumer",
                policy="local",
                tags=["workflow", "test"],
            )
            
            assert created_plugin["id"] == "workflow-plugin-1"

            # Step 2: Get the created plugin
            mock_instance.request.return_value.json.return_value = create_response
            
            retrieved_plugin = await get_plugin("workflow-plugin-1")
            assert retrieved_plugin["id"] == "workflow-plugin-1"

            # Step 3: Update the plugin
            updated_response = create_response.copy()
            updated_response["config"]["minute"] = 200
            updated_response["config"]["policy"] = "cluster"
            mock_instance.request.return_value.json.return_value = updated_response

            updated_plugin = await update_rate_limiting_plugin(
                plugin_id="workflow-plugin-1",
                minute=200,
                policy="cluster",
            )
            
            assert updated_plugin["config"]["minute"] == 200
            assert updated_plugin["config"]["policy"] == "cluster"

            # Step 4: Delete the plugin
            mock_instance.request.return_value.json.return_value = {}
            
            delete_result = await delete_rate_limiting_plugin("workflow-plugin-1")
            assert delete_result["message"] == "Rate limiting plugin deleted successfully"
            assert delete_result["plugin_id"] == "workflow-plugin-1"

    @pytest.mark.asyncio
    async def test_api_rate_limiting_scenario(self, mock_kong_responses):
        """Test a real-world API rate limiting scenario."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.request.return_value.raise_for_status.return_value = None

            # Scenario: Set up rate limiting for different API tiers
            
            # 1. Create basic rate limiting for free tier (service-scoped)
            free_tier_response = mock_kong_responses["plugins"]["basic"].copy()
            free_tier_response["id"] = "free-tier-plugin"
            free_tier_response["config"]["minute"] = 10
            free_tier_response["config"]["hour"] = 100
            mock_instance.request.return_value.json.return_value = free_tier_response

            free_tier_plugin = await create_rate_limiting_plugin(
                minute=10,
                hour=100,
                service_id="api-service-free",
                limit_by="consumer",
                policy="local",
                tags=["free-tier", "api"],
            )
            
            assert free_tier_plugin["id"] == "free-tier-plugin"

            # 2. Create advanced rate limiting for premium tier (route-scoped)
            premium_tier_response = mock_kong_responses["plugins"]["advanced"].copy()
            premium_tier_response["id"] = "premium-tier-plugin"
            mock_instance.request.return_value.json.return_value = premium_tier_response

            premium_tier_plugin = await create_rate_limiting_advanced_plugin(
                limit=[{"minute": 100}, {"hour": 5000}, {"day": 50000}],
                window_size=[60, 3600, 86400],
                route_id="api-route-premium",
                identifier="consumer",
                strategy="redis",
                redis_host="redis.api.example.com",
                tags=["premium-tier", "api"],
            )
            
            assert premium_tier_plugin["id"] == "premium-tier-plugin"

            # 3. Get all rate limiting plugins for monitoring
            all_plugins_response = {
                "data": [free_tier_response, premium_tier_response],
            }
            mock_instance.request.return_value.json.return_value = all_plugins_response

            all_rate_limiting_plugins = await get_plugins(name="rate-limiting")
            assert len(all_rate_limiting_plugins) == 2

    @pytest.mark.asyncio
    async def test_redis_cluster_configuration(self, mock_kong_responses):
        """Test Redis cluster configuration for advanced rate limiting."""
        with patch("kong_mcp_server.kong_client.httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.request.return_value.raise_for_status.return_value = None

            # Create advanced rate limiting with Redis cluster configuration
            redis_cluster_response = mock_kong_responses["plugins"]["advanced"].copy()
            redis_cluster_response["id"] = "redis-cluster-plugin"
            redis_cluster_response["config"]["strategy"] = "redis"
            redis_cluster_response["config"]["redis_host"] = "redis-cluster.example.com"
            redis_cluster_response["config"]["redis_ssl"] = True
            mock_instance.request.return_value.json.return_value = redis_cluster_response

            result = await create_rate_limiting_advanced_plugin(
                limit=[{"minute": 50}, {"hour": 1000}],
                window_size=[60, 3600],
                strategy="redis",
                redis_host="redis-cluster.example.com",
                redis_port=6380,
                redis_password="cluster-secret",
                redis_timeout=3000,
                redis_database=1,
                redis_ssl=True,
                redis_ssl_verify=True,
                redis_server_name="redis-cluster.example.com",
                namespace="api-cluster",
                sync_rate=0.9,
                tags=["redis-cluster", "high-availability"],
            )

            assert result["id"] == "redis-cluster-plugin"
            
            # Verify Redis cluster configuration was sent
            expected_config = {
                "limit": [{"minute": 50}, {"hour": 1000}],
                "window_size": [60, 3600],
                "identifier": "consumer",
                "strategy": "redis",
                "hide_client_headers": False,
                "redis_host": "redis-cluster.example.com",
                "redis_port": 6380,
                "redis_password": "cluster-secret",
                "redis_timeout": 3000,
                "redis_database": 1,
                "redis_ssl": True,
                "redis_ssl_verify": True,
                "redis_server_name": "redis-cluster.example.com",
                "namespace": "api-cluster",
                "sync_rate": 0.9,
            }

            mock_instance.request.assert_called_with(
                method="POST",
                url="/plugins",
                params=None,
                json={
                    "name": "rate-limiting-advanced",
                    "config": expected_config,
                    "enabled": True,
                    "tags": ["redis-cluster", "high-availability"],
                },
            )
