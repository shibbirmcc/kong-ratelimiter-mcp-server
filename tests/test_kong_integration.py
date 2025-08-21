"""Integration tests for Kong HTTP client."""

import os
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from kong_mcp_server.kong_client import KongClient, KongClientConfig

try:
    from testcontainers.kong import KongContainer  # type: ignore

    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False


class TestKongClientIntegration:
    """Integration tests for Kong client with mock HTTP responses."""

    @pytest.fixture
    def mock_kong_responses(self) -> Dict[str, Any]:
        """Mock Kong API responses."""
        return {
            "services": {
                "data": [
                    {
                        "id": "service-1",
                        "name": "test-service",
                        "url": "http://httpbin.org",
                        "protocol": "http",
                        "host": "httpbin.org",
                        "port": 80,
                        "path": "/",
                        "created_at": 1618846400,
                        "updated_at": 1618846400,
                    }
                ]
            },
            "routes": {
                "data": [
                    {
                        "id": "route-1",
                        "name": "test-route",
                        "protocols": ["http", "https"],
                        "methods": ["GET", "POST"],
                        "hosts": ["example.com"],
                        "paths": ["/test"],
                        "service": {"id": "service-1"},
                        "created_at": 1618846400,
                        "updated_at": 1618846400,
                    }
                ]
            },
            "plugins": {
                "data": [
                    {
                        "id": "plugin-1",
                        "name": "rate-limiting",
                        "config": {"minute": 100, "hour": 1000},
                        "service": {"id": "service-1"},
                        "created_at": 1618846400,
                    }
                ]
            },
            "status": {
                "database": {"reachable": True},
                "server": {"connections_accepted": 100},
            },
        }

    @pytest.mark.asyncio
    async def test_kong_client_basic_auth_integration(
        self, mock_kong_responses: Dict[str, Any]
    ) -> None:
        """Test Kong client with basic authentication."""
        config = KongClientConfig(
            base_url="http://kong-admin:8001",
            username="admin",
            password="secret",
            timeout=10.0,
        )

        async with KongClient(config) as client:
            with patch.object(client, "_request") as mock_request:
                mock_request.return_value = mock_kong_responses["services"]

                services = await client.get_services()

                assert len(services) == 1
                assert services[0]["name"] == "test-service"
                mock_request.assert_called_once_with("GET", "/services", params={})

    @pytest.mark.asyncio
    async def test_kong_client_token_auth_integration(
        self, mock_kong_responses: Dict[str, Any]
    ) -> None:
        """Test Kong client with API token authentication."""
        config = KongClientConfig(
            base_url="http://kong-admin:8001",
            api_token="kong-admin-token-123",
            timeout=10.0,
        )

        async with KongClient(config) as client:
            with patch.object(client, "_request") as mock_request:
                mock_request.return_value = mock_kong_responses["status"]

                status = await client.health_check()

                assert status["database"]["reachable"] is True
                mock_request.assert_called_once_with("GET", "/status", params=None)

    @pytest.mark.asyncio
    async def test_kong_client_service_operations_integration(
        self, mock_kong_responses: Dict[str, Any]
    ) -> None:
        """Test Kong client service operations integration."""
        config = KongClientConfig(base_url="http://kong-admin:8001")

        async with KongClient(config) as client:
            with patch.object(client, "_request") as mock_request:
                # Test create service
                service_data = {
                    "name": "integration-service",
                    "url": "http://integration.test",
                }
                created_service = {
                    "id": "new-service-id",
                    **service_data,
                    "created_at": 1618846400,
                }
                mock_request.return_value = created_service

                result = await client.create_service(service_data)

                assert result == created_service
                mock_request.assert_called_with(
                    "POST", "/services", params=None, json_data=service_data
                )

                # Test get service
                mock_request.return_value = created_service

                service = await client.get_service("new-service-id")

                assert service == created_service
                mock_request.assert_called_with(
                    "GET", "/services/new-service-id", params=None
                )

                # Test update service
                update_data = {"name": "updated-integration-service"}
                updated_service = {**created_service, **update_data}
                mock_request.return_value = updated_service

                result = await client.update_service("new-service-id", update_data)

                assert result == updated_service
                mock_request.assert_called_with(
                    "PATCH",
                    "/services/new-service-id",
                    params=None,
                    json_data=update_data,
                )

                # Test delete service
                mock_request.return_value = {}

                await client.delete_service("new-service-id")

                mock_request.assert_called_with(
                    "DELETE", "/services/new-service-id", params=None
                )

    @pytest.mark.asyncio
    async def test_kong_client_route_operations_integration(
        self, mock_kong_responses: Dict[str, Any]
    ) -> None:
        """Test Kong client route operations integration."""
        config = KongClientConfig(base_url="http://kong-admin:8001")

        async with KongClient(config) as client:
            with patch.object(client, "_request") as mock_request:
                # Test create route
                route_data = {
                    "name": "integration-route",
                    "service": {"id": "service-1"},
                    "paths": ["/integration"],
                }
                created_route = {
                    "id": "new-route-id",
                    **route_data,
                    "created_at": 1618846400,
                }
                mock_request.return_value = created_route

                result = await client.create_route(route_data)

                assert result == created_route
                mock_request.assert_called_with(
                    "POST", "/routes", params=None, json_data=route_data
                )

                # Test get routes
                mock_request.return_value = mock_kong_responses["routes"]

                routes = await client.get_routes(size=10)

                assert len(routes) == 1
                assert routes[0]["name"] == "test-route"
                mock_request.assert_called_with("GET", "/routes", params={"size": 10})

    @pytest.mark.asyncio
    async def test_kong_client_error_handling_integration(self) -> None:
        """Test Kong client error handling in integration scenarios."""
        config = KongClientConfig(base_url="http://kong-admin:8001")

        async with KongClient(config) as client:
            with patch.object(client, "_request") as mock_request:
                # Mock HTTP error response
                mock_request.side_effect = httpx.HTTPStatusError(
                    "Not Found", request=AsyncMock(), response=AsyncMock()
                )

                with pytest.raises(httpx.HTTPStatusError):
                    await client.get_service("non-existent-service")

    @pytest.mark.asyncio
    async def test_kong_client_environment_config_integration(self) -> None:
        """Test Kong client configuration from environment variables."""
        env_vars = {
            "KONG_ADMIN_URL": "http://test-kong:8001",
            "KONG_USERNAME": "test-admin",
            "KONG_PASSWORD": "test-password",
            "KONG_TIMEOUT": "45.0",
            "KONG_VERIFY_SSL": "false",
        }

        with patch.dict(os.environ, env_vars):
            config = KongClientConfig.from_env()

            assert config.base_url == "http://test-kong:8001"
            assert config.username == "test-admin"
            assert config.password == "test-password"
            assert config.timeout == 45.0
            assert config.verify_ssl is False

            async with KongClient(config) as client:
                with patch.object(client, "_ensure_client") as mock_ensure:
                    # Just test that client initializes correctly
                    await mock_ensure()

    @pytest.mark.asyncio
    async def test_kong_tools_integration_with_client(
        self, mock_kong_responses: Dict[str, Any]
    ) -> None:
        """Test Kong tools integration with the HTTP client."""
        from kong_mcp_server.tools.kong_routes import create_route, get_routes
        from kong_mcp_server.tools.kong_services import create_service, get_services

        # Test Kong services tools
        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_services.return_value = mock_kong_responses["services"][
                "data"
            ]
            mock_client_class.return_value.__aenter__.return_value = mock_client

            services = await get_services()

            assert len(services) == 1
            assert services[0]["name"] == "test-service"

        # Test Kong routes tools
        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_routes.return_value = mock_kong_responses["routes"]["data"]
            mock_client_class.return_value.__aenter__.return_value = mock_client

            routes = await get_routes()

            assert len(routes) == 1
            assert routes[0]["name"] == "test-route"

        # Test service creation tool
        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            created_service = {
                "id": "created-service-id",
                "name": "new-service",
                "url": "http://new.service",
                "protocol": "http",
            }
            mock_client.create_service.return_value = created_service
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await create_service("new-service", "http://new.service")

            assert result == created_service
            mock_client.create_service.assert_called_once()

        # Test route creation tool
        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            created_route = {
                "id": "created-route-id",
                "name": "new-route",
                "service": {"id": "service-1"},
                "paths": ["/new"],
            }
            mock_client.create_route.return_value = created_route
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await create_route("service-1", name="new-route", paths=["/new"])

            assert result == created_route
            mock_client.create_route.assert_called_once()


@pytest.mark.skipif(
    not TESTCONTAINERS_AVAILABLE or os.getenv("RUN_LIVE_TESTS") != "true",
    reason="Live Kong tests require testcontainers and RUN_LIVE_TESTS=true",
)
class TestKongClientLive:
    """Live integration tests with actual Kong instance (optional)."""

    @pytest.fixture(scope="class")
    def kong_container(self):
        """Start Kong container for live testing."""
        if not TESTCONTAINERS_AVAILABLE:
            pytest.skip("testcontainers not available")
        container = KongContainer()
        container.start()
        # Wait for Kong to be ready
        container.get_exposed_port(8001)  # Admin API port
        return container

    @pytest.mark.asyncio
    async def test_live_kong_health_check(self, kong_container) -> None:
        """Test health check against live Kong instance."""
        admin_port = kong_container.get_exposed_port(8001)
        config = KongClientConfig(
            base_url=f"http://localhost:{admin_port}",
            timeout=10.0,
        )

        async with KongClient(config) as client:
            status = await client.health_check()

            assert "database" in status
            # Kong Community Edition may not have database in containerized setup
            assert isinstance(status, dict)

    @pytest.mark.asyncio
    async def test_live_kong_service_operations(self, kong_container) -> None:
        """Test service operations against live Kong instance."""
        admin_port = kong_container.get_exposed_port(8001)
        config = KongClientConfig(
            base_url=f"http://localhost:{admin_port}",
            timeout=10.0,
        )

        async with KongClient(config) as client:
            # Create a service
            service_data = {
                "name": "live-test-service",
                "url": "http://httpbin.org",
            }

            created_service = await client.create_service(service_data)
            service_id = created_service["id"]

            try:
                assert created_service["name"] == "live-test-service"
                assert created_service["url"] == "http://httpbin.org"

                # Get the service
                retrieved_service = await client.get_service(service_id)
                assert retrieved_service["id"] == service_id

                # Update the service
                update_data = {"name": "updated-live-test-service"}
                updated_service = await client.update_service(service_id, update_data)
                assert updated_service["name"] == "updated-live-test-service"

                # List services
                services = await client.get_services()
                service_names = [s["name"] for s in services]
                assert "updated-live-test-service" in service_names

            finally:
                # Clean up: delete the service
                await client.delete_service(service_id)
