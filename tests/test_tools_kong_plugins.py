"""Tests for Kong plugins tools."""

from unittest.mock import AsyncMock, patch
import pytest
from kong_mcp_server.tools.kong_plugins import (
    get_plugins,
    get_plugins_by_service,
    get_plugins_by_route,
    get_plugins_by_consumer,
)


class TestKongPluginsTools:
    """Test Kong plugins tools."""

    # ---------------- get_plugins ----------------
    @pytest.mark.asyncio
    async def test_get_plugins_basic(self):
        """Test get_plugins with default parameters."""
        mock_response = {
            "data": [{"id": "plugin1", "name": "jwt"}],
            "offset": None,
            "next": "cursor123",
        }

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins()

            assert result["data"] == mock_response["data"]
            assert result["offset"] == "cursor123"
            mock_client.get_plugins.assert_awaited_once_with(params={})

    @pytest.mark.asyncio
    async def test_get_plugins_with_name_size_offset(self):
        """Test get_plugins with name, size, and offset parameters."""
        mock_response = {
            "data": [{"id": "plugin2", "name": "rate-limiting"}],
            "offset": "abc123",
            "next": None,
        }

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins(name="rate-limiting", size=50, offset="cursor0")

            assert result["data"] == mock_response["data"]
            assert result["offset"] == "abc123"
            mock_client.get_plugins.assert_awaited_once_with(
                params={"name": "rate-limiting", "size": 50, "offset": "cursor0"}
            )

    @pytest.mark.asyncio
    async def test_get_plugins_invalid_size(self):
        """Test get_plugins raises ValueError for invalid size."""
        with pytest.raises(ValueError):
            await get_plugins(size=0)

        with pytest.raises(ValueError):
            await get_plugins(size=1001)

    # ---------------- get_plugins_by_service ----------------
    @pytest.mark.asyncio
    async def test_get_plugins_by_service_basic(self):
        """Test get_plugins_by_service with default parameters."""
        mock_response = {"data": [{"id": "p1", "name": "jwt"}], "offset": None}

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins_by_service.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins_by_service("service1")

            assert result == mock_response
            mock_client.get_plugins_by_service.assert_awaited_once_with(
                service_id="service1", params={}
            )

    @pytest.mark.asyncio
    async def test_get_plugins_by_service_with_params(self):
        """Test get_plugins_by_service with size and offset."""
        mock_response = {"data": [{"id": "p2"}], "offset": "cursor1"}

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins_by_service.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins_by_service("service2", size=10, offset="o1")

            assert result == mock_response
            mock_client.get_plugins_by_service.assert_awaited_once_with(
                service_id="service2", params={"size": 10, "offset": "o1"}
            )

    # ---------------- get_plugins_by_route ----------------
    @pytest.mark.asyncio
    async def test_get_plugins_by_route_basic(self):
        """Test get_plugins_by_route with default parameters."""
        mock_response = {"data": [{"id": "r1"}], "offset": None}

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins_by_route.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins_by_route("route1")

            assert result == mock_response
            mock_client.get_plugins_by_route.assert_awaited_once_with(
                route_id="route1", params={}
            )

    @pytest.mark.asyncio
    async def test_get_plugins_by_route_with_params(self):
        """Test get_plugins_by_route with size and offset."""
        mock_response = {"data": [{"id": "r2"}], "offset": "cursor2"}

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins_by_route.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins_by_route("route2", size=5, offset="o2")

            assert result == mock_response
            mock_client.get_plugins_by_route.assert_awaited_once_with(
                route_id="route2", params={"size": 5, "offset": "o2"}
            )

    # ---------------- get_plugins_by_consumer ----------------
    @pytest.mark.asyncio
    async def test_get_plugins_by_consumer_basic(self):
        """Test get_plugins_by_consumer with default parameters."""
        mock_response = {"data": [{"id": "c1"}], "offset": None}

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins_by_consumer.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins_by_consumer("consumer1")

            assert result == mock_response
            mock_client.get_plugins_by_consumer.assert_awaited_once_with(
                consumer_id="consumer1", params={}
            )

    @pytest.mark.asyncio
    async def test_get_plugins_by_consumer_with_params(self):
        """Test get_plugins_by_consumer with size and offset."""
        mock_response = {"data": [{"id": "c2"}], "offset": "cursorC"}

        with patch("kong_mcp_server.tools.kong_plugins.KongClient", autospec=True) as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get_plugins_by_consumer.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await get_plugins_by_consumer("consumer2", size=3, offset="oC")

            assert result == mock_response
            mock_client.get_plugins_by_consumer.assert_awaited_once_with(
                consumer_id="consumer2", params={"size": 3, "offset": "oC"}
            )
