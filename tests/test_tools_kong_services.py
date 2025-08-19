"""Tests for Kong services tools."""

from unittest.mock import AsyncMock, patch

import pytest

from kong_mcp_server.tools.kong_services import (
    create_service,
    delete_service,
    get_services,
    update_service,
)


class TestKongServicesTools:
    """Test Kong services tools."""

    @pytest.mark.asyncio
    async def test_get_services(self) -> None:
        """Test get_services function."""
        mock_services = [
            {"id": "1", "name": "service1", "url": "http://example1.com"},
            {"id": "2", "name": "service2", "url": "http://example2.com"},
        ]

        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_services.return_value = mock_services
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await get_services()

            assert result == mock_services
            mock_client.get_services.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_service(self) -> None:
        """Test create_service function."""
        mock_response = {
            "id": "123",
            "name": "test-service",
            "url": "http://example.com",
            "protocol": "https",
            "host": "example.com",
            "port": 443,
            "path": "/api",
        }

        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_service.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await create_service(
                name="test-service",
                url="http://example.com",
                protocol="https",
                host="example.com",
                port=443,
                path="/api",
            )

            assert result == mock_response
            mock_client.create_service.assert_called_once_with(
                {
                    "name": "test-service",
                    "url": "http://example.com",
                    "protocol": "https",
                    "host": "example.com",
                    "port": 443,
                    "path": "/api",
                }
            )

    @pytest.mark.asyncio
    async def test_create_service_minimal(self) -> None:
        """Test create_service function with minimal parameters."""
        mock_response = {
            "id": "456",
            "name": "minimal-service",
            "url": "http://minimal.com",
            "protocol": "http",
        }

        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.create_service.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await create_service(
                name="minimal-service",
                url="http://minimal.com",
            )

            assert result == mock_response
            mock_client.create_service.assert_called_once_with(
                {
                    "name": "minimal-service",
                    "url": "http://minimal.com",
                    "protocol": "http",
                }
            )

    @pytest.mark.asyncio
    async def test_update_service(self) -> None:
        """Test update_service function."""
        mock_response = {
            "id": "123",
            "name": "updated-service",
            "url": "http://updated.com",
            "protocol": "https",
        }

        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.update_service.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await update_service(
                service_id="123",
                name="updated-service",
                url="http://updated.com",
                protocol="https",
            )

            assert result == mock_response
            mock_client.update_service.assert_called_once_with(
                "123",
                {
                    "name": "updated-service",
                    "url": "http://updated.com",
                    "protocol": "https",
                },
            )

    @pytest.mark.asyncio
    async def test_update_service_minimal(self) -> None:
        """Test update_service function with minimal parameters."""
        mock_response = {"id": "456", "name": "existing-service"}

        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.update_service.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await update_service(service_id="456")

            assert result == mock_response
            mock_client.update_service.assert_called_once_with("456", {})

    @pytest.mark.asyncio
    async def test_update_service_partial(self) -> None:
        """Test update_service function with partial parameters."""
        mock_response = {"id": "789", "name": "partial-update"}

        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.update_service.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await update_service(
                service_id="789",
                name="partial-update",
                port=8080,
            )

            assert result == mock_response
            mock_client.update_service.assert_called_once_with(
                "789",
                {
                    "name": "partial-update",
                    "port": 8080,
                },
            )

    @pytest.mark.asyncio
    async def test_delete_service(self) -> None:
        """Test delete_service function."""
        with patch(
            "kong_mcp_server.tools.kong_services.KongClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client.delete_service.return_value = None
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await delete_service("789")

            assert result == {
                "message": "Service deleted successfully",
                "service_id": "789",
            }
            mock_client.delete_service.assert_called_once_with("789")
