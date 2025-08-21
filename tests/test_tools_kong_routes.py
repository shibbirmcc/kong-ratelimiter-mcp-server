"""Tests for Kong routes tools."""

from unittest.mock import AsyncMock, patch

import pytest

from kong_mcp_server.tools.kong_routes import (
    create_route,
    delete_route,
    get_routes,
    update_route,
)


class TestKongRoutesTools:
    """Test Kong routes tools."""

    @pytest.mark.asyncio
    async def test_get_routes(self) -> None:
        """Test get_routes function."""
        mock_routes = [
            {"id": "1", "name": "route1", "service": {"id": "service1"}},
            {"id": "2", "name": "route2", "service": {"id": "service2"}},
        ]

        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_routes.return_value = mock_routes
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await get_routes()

            assert result == mock_routes
            mock_client.get_routes.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_route(self) -> None:
        """Test create_route function."""
        mock_response = {
            "id": "123",
            "name": "test-route",
            "service": {"id": "service-123"},
            "protocols": ["http", "https"],
            "methods": ["GET", "POST"],
            "hosts": ["example.com"],
            "paths": ["/api", "/v1"],
        }

        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_route.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await create_route(
                service_id="service-123",
                name="test-route",
                protocols=["http", "https"],
                methods=["GET", "POST"],
                hosts=["example.com"],
                paths=["/api", "/v1"],
            )

            assert result == mock_response
            mock_client.create_route.assert_called_once_with(
                {
                    "service": {"id": "service-123"},
                    "name": "test-route",
                    "protocols": ["http", "https"],
                    "methods": ["GET", "POST"],
                    "hosts": ["example.com"],
                    "paths": ["/api", "/v1"],
                }
            )

    @pytest.mark.asyncio
    async def test_create_route_minimal(self) -> None:
        """Test create_route function with minimal parameters."""
        mock_response = {
            "id": "456",
            "service": {"id": "service-456"},
        }

        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_route.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await create_route(service_id="service-456")

            assert result == mock_response
            mock_client.create_route.assert_called_once_with(
                {
                    "service": {"id": "service-456"},
                }
            )

    @pytest.mark.asyncio
    async def test_update_route(self) -> None:
        """Test update_route function."""
        mock_response = {
            "id": "route-456",
            "name": "updated-route",
            "service": {"id": "service-789"},
            "protocols": ["https"],
            "methods": ["PUT", "DELETE"],
            "hosts": ["api.example.com"],
            "paths": ["/v2/api"],
        }

        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.update_route.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await update_route(
                route_id="route-456",
                service_id="service-789",
                name="updated-route",
                protocols=["https"],
                methods=["PUT", "DELETE"],
                hosts=["api.example.com"],
                paths=["/v2/api"],
            )

            assert result == mock_response
            mock_client.update_route.assert_called_once_with(
                "route-456",
                {
                    "service": {"id": "service-789"},
                    "name": "updated-route",
                    "protocols": ["https"],
                    "methods": ["PUT", "DELETE"],
                    "hosts": ["api.example.com"],
                    "paths": ["/v2/api"],
                },
            )

    @pytest.mark.asyncio
    async def test_update_route_minimal(self) -> None:
        """Test update_route function with minimal parameters."""
        mock_response = {"id": "route-789", "name": "existing-route"}

        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.update_route.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await update_route(route_id="route-789")

            assert result == mock_response
            mock_client.update_route.assert_called_once_with("route-789", {})

    @pytest.mark.asyncio
    async def test_update_route_partial(self) -> None:
        """Test update_route function with partial parameters."""
        mock_response = {"id": "route-321", "name": "partial-update"}

        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.update_route.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await update_route(
                route_id="route-321",
                name="partial-update",
                methods=["GET"],
            )

            assert result == mock_response
            mock_client.update_route.assert_called_once_with(
                "route-321",
                {
                    "name": "partial-update",
                    "methods": ["GET"],
                },
            )

    @pytest.mark.asyncio
    async def test_delete_route(self) -> None:
        """Test delete_route function."""
        with patch("kong_mcp_server.tools.kong_routes.KongClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.delete_route.return_value = None
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await delete_route("route-456")

            assert result == {
                "message": "Route deleted successfully",
                "route_id": "route-456",
            }
            mock_client.delete_route.assert_called_once_with("route-456")
