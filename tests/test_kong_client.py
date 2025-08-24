"""Tests for Kong HTTP client."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from kong_mcp_server.kong_client import KongClient, KongClientConfig


class TestKongClientConfig:
    """Test KongClientConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = KongClientConfig()

        assert config.base_url == "http://localhost:8001"
        assert config.username is None
        assert config.password is None
        assert config.api_token is None
        assert config.timeout == 30.0
        assert config.verify_ssl is True

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = KongClientConfig(
            base_url="https://kong.example.com:8444",
            username="admin",
            password="secret",
            api_token="token123",
            timeout=60.0,
            verify_ssl=False,
        )

        assert config.base_url == "https://kong.example.com:8444"
        assert config.username == "admin"
        assert config.password == "secret"
        assert config.api_token == "token123"
        assert config.timeout == 60.0
        assert config.verify_ssl is False

    @patch.dict(
        os.environ,
        {
            "KONG_ADMIN_URL": "https://kong.test:8444",
            "KONG_USERNAME": "testuser",
            "KONG_PASSWORD": "testpass",
            "KONG_API_TOKEN": "test_token",
            "KONG_TIMEOUT": "45.0",
            "KONG_VERIFY_SSL": "false",
        },
    )
    def test_from_env(self) -> None:
        """Test configuration from environment variables."""
        config = KongClientConfig.from_env()

        assert config.base_url == "https://kong.test:8444"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.api_token == "test_token"
        assert config.timeout == 45.0
        assert config.verify_ssl is False

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_defaults(self) -> None:
        """Test configuration from environment variables with defaults."""
        config = KongClientConfig.from_env()

        assert config.base_url == "http://localhost:8001"
        assert config.username is None
        assert config.password is None
        assert config.api_token is None
        assert config.timeout == 30.0
        assert config.verify_ssl is True

    @pytest.mark.parametrize(
        "ssl_value,expected",
        [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("invalid", False),
        ],
    )
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_ssl_values(self, ssl_value: str, expected: bool) -> None:
        """Test SSL verification parsing from environment."""
        with patch.dict(os.environ, {"KONG_VERIFY_SSL": ssl_value}):
            config = KongClientConfig.from_env()
            assert config.verify_ssl is expected


class TestKongClient:
    """Test KongClient class."""

    @pytest.fixture
    def config(self) -> KongClientConfig:
        """Test configuration fixture."""
        return KongClientConfig(
            base_url="http://localhost:8001",
            username="admin",
            password="secret",
            timeout=30.0,
            verify_ssl=True,
        )

    @pytest.fixture
    def config_with_token(self) -> KongClientConfig:
        """Test configuration with API token."""
        return KongClientConfig(
            base_url="http://localhost:8001",
            api_token="test_token",
            timeout=30.0,
            verify_ssl=True,
        )

    def test_init_with_config(self, config: KongClientConfig) -> None:
        """Test initialization with configuration."""
        client = KongClient(config)
        assert client.config == config
        assert client._client is None

    def test_init_without_config(self) -> None:
        """Test initialization without configuration."""
        with patch.object(KongClientConfig, "from_env") as mock_from_env:
            mock_config = KongClientConfig()
            mock_from_env.return_value = mock_config

            client = KongClient()

            mock_from_env.assert_called_once()
            assert client.config == mock_config

    @pytest.mark.asyncio
    async def test_context_manager(self, config: KongClientConfig) -> None:
        """Test async context manager."""
        client = KongClient(config)

        with patch.object(client, "_ensure_client") as mock_ensure:
            with patch.object(client, "close") as mock_close:
                async with client as ctx_client:
                    assert ctx_client is client
                    mock_ensure.assert_called_once()

                mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_client_basic_auth(self, config: KongClientConfig) -> None:
        """Test HTTP client initialization with basic auth."""
        client = KongClient(config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await client._ensure_client()

            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args

            assert call_args.kwargs["base_url"] == config.base_url
            assert call_args.kwargs["timeout"] == config.timeout
            assert call_args.kwargs["verify"] == config.verify_ssl
            assert "Authorization" not in call_args.kwargs["headers"]
            assert call_args.kwargs["auth"] is not None

    @pytest.mark.asyncio
    async def test_ensure_client_token_auth(
        self, config_with_token: KongClientConfig
    ) -> None:
        """Test HTTP client initialization with token auth."""
        client = KongClient(config_with_token)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await client._ensure_client()

            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args

            assert call_args.kwargs["base_url"] == config_with_token.base_url
            assert call_args.kwargs["headers"]["Authorization"] == "Bearer test_token"
            assert call_args.kwargs["auth"] is None

    @pytest.mark.asyncio
    async def test_ensure_client_no_auth(self) -> None:
        """Test HTTP client initialization without authentication."""
        config = KongClientConfig()
        client = KongClient(config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await client._ensure_client()

            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args

            assert "Authorization" not in call_args.kwargs["headers"]
            assert call_args.kwargs["auth"] is None

    @pytest.mark.asyncio
    async def test_close(self, config: KongClientConfig) -> None:
        """Test client closing."""
        client = KongClient(config)
        mock_http_client = AsyncMock()
        client._client = mock_http_client

        await client.close()

        mock_http_client.aclose.assert_called_once()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_close_no_client(self, config: KongClientConfig) -> None:
        """Test closing when no client exists."""
        client = KongClient(config)

        await client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_request_success(self, config: KongClientConfig) -> None:
        """Test successful HTTP request."""
        client = KongClient(config)
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_http_client.request.return_value = mock_response
        client._client = mock_http_client

        result = await client._request(
            "GET", "/test", params={"key": "value"}, json_data={"field": "data"}
        )

        assert result == {"data": "test"}
        mock_http_client.request.assert_called_once_with(
            method="GET",
            url="/test",
            params={"key": "value"},
            json={"field": "data"},
        )
        mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_http_error(self, config: KongClientConfig) -> None:
        """Test HTTP request with error response."""
        client = KongClient(config)
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=MagicMock()
        )
        mock_http_client.request.return_value = mock_response
        client._client = mock_http_client

        with pytest.raises(httpx.HTTPStatusError):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_request_no_client(self, config: KongClientConfig) -> None:
        """Test request when client is not initialized."""
        client = KongClient(config)

        with patch.object(client, "_ensure_client") as mock_ensure:
            mock_ensure.side_effect = lambda: None  # Don't actually create client

            with pytest.raises(RuntimeError, match="HTTP client not initialized"):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_get(self, config: KongClientConfig) -> None:
        """Test GET request."""
        client = KongClient(config)

        with patch.object(
            client, "_request", return_value={"result": "data"}
        ) as mock_request:
            result = await client.get("/services", params={"size": 10})

            assert result == {"result": "data"}
            mock_request.assert_called_once_with(
                "GET", "/services", params={"size": 10}
            )

    @pytest.mark.asyncio
    async def test_post(self, config: KongClientConfig) -> None:
        """Test POST request."""
        client = KongClient(config)

        with patch.object(
            client, "_request", return_value={"id": "123"}
        ) as mock_request:
            result = await client.post("/services", json_data={"name": "test"})

            assert result == {"id": "123"}
            mock_request.assert_called_once_with(
                "POST", "/services", params=None, json_data={"name": "test"}
            )

    @pytest.mark.asyncio
    async def test_put(self, config: KongClientConfig) -> None:
        """Test PUT request."""
        client = KongClient(config)

        with patch.object(
            client, "_request", return_value={"updated": True}
        ) as mock_request:
            result = await client.put("/services/123", json_data={"name": "updated"})

            assert result == {"updated": True}
            mock_request.assert_called_once_with(
                "PUT", "/services/123", params=None, json_data={"name": "updated"}
            )

    @pytest.mark.asyncio
    async def test_patch(self, config: KongClientConfig) -> None:
        """Test PATCH request."""
        client = KongClient(config)

        with patch.object(
            client, "_request", return_value={"patched": True}
        ) as mock_request:
            result = await client.patch("/services/123", json_data={"name": "patched"})

            assert result == {"patched": True}
            mock_request.assert_called_once_with(
                "PATCH", "/services/123", params=None, json_data={"name": "patched"}
            )

    @pytest.mark.asyncio
    async def test_delete(self, config: KongClientConfig) -> None:
        """Test DELETE request."""
        client = KongClient(config)

        with patch.object(client, "_request", return_value={}) as mock_request:
            result = await client.delete("/services/123")

            assert result == {}
            mock_request.assert_called_once_with("DELETE", "/services/123", params=None)

    @pytest.mark.asyncio
    async def test_get_services(self, config: KongClientConfig) -> None:
        """Test get_services method."""
        client = KongClient(config)
        mock_response = {"data": [{"id": "1", "name": "service1"}]}

        with patch.object(client, "get", return_value=mock_response) as mock_get:
            result = await client.get_services(size=10, offset=0)

            assert result == [{"id": "1", "name": "service1"}]
            mock_get.assert_called_once_with(
                "/services", params={"size": 10, "offset": 0}
            )

    @pytest.mark.asyncio
    async def test_get_service(self, config: KongClientConfig) -> None:
        """Test get_service method."""
        client = KongClient(config)
        mock_service = {"id": "123", "name": "test-service"}

        with patch.object(client, "get", return_value=mock_service) as mock_get:
            result = await client.get_service("123")

            assert result == mock_service
            mock_get.assert_called_once_with("/services/123")

    @pytest.mark.asyncio
    async def test_create_service(self, config: KongClientConfig) -> None:
        """Test create_service method."""
        client = KongClient(config)
        service_data = {"name": "test-service", "url": "http://example.com"}
        mock_response = {"id": "123", **service_data}

        with patch.object(client, "post", return_value=mock_response) as mock_post:
            result = await client.create_service(service_data)

            assert result == mock_response
            mock_post.assert_called_once_with("/services", json_data=service_data)

    @pytest.mark.asyncio
    async def test_update_service(self, config: KongClientConfig) -> None:
        """Test update_service method."""
        client = KongClient(config)
        service_data = {"name": "updated-service"}
        mock_response = {"id": "123", **service_data}

        with patch.object(client, "patch", return_value=mock_response) as mock_patch:
            result = await client.update_service("123", service_data)

            assert result == mock_response
            mock_patch.assert_called_once_with("/services/123", json_data=service_data)

    @pytest.mark.asyncio
    async def test_delete_service(self, config: KongClientConfig) -> None:
        """Test delete_service method."""
        client = KongClient(config)

        with patch.object(client, "delete", return_value={}) as mock_delete:
            await client.delete_service("123")

            mock_delete.assert_called_once_with("/services/123")

    @pytest.mark.asyncio
    async def test_get_routes(self, config: KongClientConfig) -> None:
        """Test get_routes method."""
        client = KongClient(config)
        mock_response = {"data": [{"id": "1", "name": "route1"}]}

        with patch.object(client, "get", return_value=mock_response) as mock_get:
            result = await client.get_routes(size=10)

            assert result == [{"id": "1", "name": "route1"}]
            mock_get.assert_called_once_with("/routes", params={"size": 10})

    @pytest.mark.asyncio
    async def test_get_route(self, config: KongClientConfig) -> None:
        """Test get_route method."""
        client = KongClient(config)
        mock_route = {"id": "123", "name": "test-route"}

        with patch.object(client, "get", return_value=mock_route) as mock_get:
            result = await client.get_route("123")

            assert result == mock_route
            mock_get.assert_called_once_with("/routes/123")

    @pytest.mark.asyncio
    async def test_create_route(self, config: KongClientConfig) -> None:
        """Test create_route method."""
        client = KongClient(config)
        route_data = {"name": "test-route", "service": {"id": "service-123"}}
        mock_response = {"id": "123", **route_data}

        with patch.object(client, "post", return_value=mock_response) as mock_post:
            result = await client.create_route(route_data)

            assert result == mock_response
            mock_post.assert_called_once_with("/routes", json_data=route_data)

    @pytest.mark.asyncio
    async def test_update_route(self, config: KongClientConfig) -> None:
        """Test update_route method."""
        client = KongClient(config)
        route_data = {"name": "updated-route"}
        mock_response = {"id": "123", **route_data}

        with patch.object(client, "patch", return_value=mock_response) as mock_patch:
            result = await client.update_route("123", route_data)

            assert result == mock_response
            mock_patch.assert_called_once_with("/routes/123", json_data=route_data)

    @pytest.mark.asyncio
    async def test_delete_route(self, config: KongClientConfig) -> None:
        """Test delete_route method."""
        client = KongClient(config)

        with patch.object(client, "delete", return_value={}) as mock_delete:
            await client.delete_route("123")

            mock_delete.assert_called_once_with("/routes/123")

    @pytest.mark.asyncio
    async def test_get_plugins(self, config: KongClientConfig) -> None:
        """Test get_plugins method."""
        client = KongClient(config)
        mock_response = {"data": [{"id": "1", "name": "rate-limiting"}]}

        with patch.object(client, "get", return_value=mock_response) as mock_get:
            result = await client.get_plugins_as_list()

            assert result == [{"id": "1", "name": "rate-limiting"}]
            mock_get.assert_called_once_with("/plugins", params={})

    @pytest.mark.asyncio
    async def test_get_plugin(self, config: KongClientConfig) -> None:
        """Test get_plugin method."""
        client = KongClient(config)
        mock_plugin = {"id": "123", "name": "rate-limiting"}

        with patch.object(client, "get", return_value=mock_plugin) as mock_get:
            result = await client.get_plugin("123")

            assert result == mock_plugin
            mock_get.assert_called_once_with("/plugins/123")

    @pytest.mark.asyncio
    async def test_create_plugin(self, config: KongClientConfig) -> None:
        """Test create_plugin method."""
        client = KongClient(config)
        plugin_data = {"name": "rate-limiting", "config": {"minute": 100}}
        mock_response = {"id": "123", **plugin_data}

        with patch.object(client, "post", return_value=mock_response) as mock_post:
            result = await client.create_plugin(plugin_data)

            assert result == mock_response
            mock_post.assert_called_once_with("/plugins", json_data=plugin_data)

    @pytest.mark.asyncio
    async def test_update_plugin(self, config: KongClientConfig) -> None:
        """Test update_plugin method."""
        client = KongClient(config)
        plugin_data = {"config": {"minute": 200}}
        mock_response = {"id": "123", **plugin_data}

        with patch.object(client, "patch", return_value=mock_response) as mock_patch:
            result = await client.update_plugin("123", plugin_data)

            assert result == mock_response
            mock_patch.assert_called_once_with("/plugins/123", json_data=plugin_data)

    @pytest.mark.asyncio
    async def test_delete_plugin(self, config: KongClientConfig) -> None:
        """Test delete_plugin method."""
        client = KongClient(config)

        with patch.object(client, "delete", return_value={}) as mock_delete:
            await client.delete_plugin("123")

            mock_delete.assert_called_once_with("/plugins/123")

    @pytest.mark.asyncio
    async def test_health_check(self, config: KongClientConfig) -> None:
        """Test health_check method."""
        client = KongClient(config)
        mock_status = {"database": {"reachable": True}}

        with patch.object(client, "get", return_value=mock_status) as mock_get:
            result = await client.health_check()

            assert result == mock_status
            mock_get.assert_called_once_with("/status")
