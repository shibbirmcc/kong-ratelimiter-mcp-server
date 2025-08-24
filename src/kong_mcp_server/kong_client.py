"""Kong Admin API HTTP client."""

import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


class KongClientConfig(BaseModel):
    """Kong client configuration."""

    base_url: str = Field(
        default="http://localhost:8001", description="Kong Admin API base URL"
    )
    username: Optional[str] = Field(
        default=None, description="Kong Admin username (Community Edition)"
    )
    password: Optional[str] = Field(
        default=None, description="Kong Admin password (Community Edition)"
    )
    api_token: Optional[str] = Field(
        default=None, description="Kong Admin API token (Enterprise Edition)"
    )
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    @classmethod
    def from_env(cls) -> "KongClientConfig":
        """Create configuration from environment variables.

        Environment variables:
        - KONG_ADMIN_URL: Kong Admin API URL (default: http://localhost:8001)
        - KONG_USERNAME: Kong Admin username (Community Edition)
        - KONG_PASSWORD: Kong Admin password (Community Edition)
        - KONG_API_TOKEN: Kong Admin API token (Enterprise Edition)
        - KONG_TIMEOUT: Request timeout in seconds (default: 30.0)
        - KONG_VERIFY_SSL: Verify SSL certificates (default: True)

        Returns:
            KongClientConfig instance
        """
        return cls(
            base_url=os.getenv("KONG_ADMIN_URL", "http://localhost:8001"),
            username=os.getenv("KONG_USERNAME"),
            password=os.getenv("KONG_PASSWORD"),
            api_token=os.getenv("KONG_API_TOKEN"),
            timeout=float(os.getenv("KONG_TIMEOUT", "30.0")),
            verify_ssl=os.getenv("KONG_VERIFY_SSL", "True").lower()
            in ("true", "1", "yes", "on"),
        )


class KongClient:
    """HTTP client for Kong Admin API communication."""

    def __init__(self, config: Optional[KongClientConfig] = None) -> None:
        """Initialize Kong client.

        Args:
            config: Kong client configuration. If None, configuration is loaded
                from environment variables.
        """
        self.config = config or KongClientConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "KongClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}

            # Add authentication headers
            if self.config.api_token:
                # Enterprise Edition API token authentication
                headers["Authorization"] = f"Bearer {self.config.api_token}"
            elif self.config.username and self.config.password:
                # Community Edition basic authentication
                auth = httpx.BasicAuth(self.config.username, self.config.password)
            else:
                auth = None

            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                auth=auth if not self.config.api_token else None,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Kong Admin API.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        await self._ensure_client()

        if not self._client:
            raise RuntimeError("HTTP client not initialized")

        response = await self._client.request(
            method=method,
            url=path,
            params=params,
            json=json_data,
        )

        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make POST request.

        Args:
            path: API endpoint path
            json_data: JSON request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("POST", path, params=params, json_data=json_data)

    async def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request.

        Args:
            path: API endpoint path
            json_data: JSON request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("PUT", path, params=params, json_data=json_data)

    async def patch(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PATCH request.

        Args:
            path: API endpoint path
            json_data: JSON request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("PATCH", path, params=params, json_data=json_data)

    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        return await self._request("DELETE", path, params=params)

    # Kong Admin API specific methods

    async def get_services(self, **params: Any) -> List[Dict[str, Any]]:
        """Get all Kong services.

        Args:
            **params: Query parameters (offset, size, tags, etc.)

        Returns:
            List of Kong services
        """
        response = await self.get("/services", params=params)
        return response.get("data", [])  # type: ignore[no-any-return]

    async def get_service(self, service_id: str) -> Dict[str, Any]:
        """Get Kong service by ID.

        Args:
            service_id: Service ID or name

        Returns:
            Kong service data
        """
        return await self.get(f"/services/{service_id}")

    async def create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kong service.

        Args:
            service_data: Service configuration

        Returns:
            Created service data
        """
        return await self.post("/services", json_data=service_data)

    async def update_service(
        self, service_id: str, service_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Kong service.

        Args:
            service_id: Service ID or name
            service_data: Service configuration updates

        Returns:
            Updated service data
        """
        return await self.patch(f"/services/{service_id}", json_data=service_data)

    async def delete_service(self, service_id: str) -> None:
        """Delete Kong service.

        Args:
            service_id: Service ID or name
        """
        await self.delete(f"/services/{service_id}")

    async def get_routes(self, **params: Any) -> List[Dict[str, Any]]:
        """Get all Kong routes.

        Args:
            **params: Query parameters (offset, size, tags, etc.)

        Returns:
            List of Kong routes
        """
        response = await self.get("/routes", params=params)
        return response.get("data", [])  # type: ignore[no-any-return]

    async def get_route(self, route_id: str) -> Dict[str, Any]:
        """Get Kong route by ID.

        Args:
            route_id: Route ID or name

        Returns:
            Kong route data
        """
        return await self.get(f"/routes/{route_id}")

    async def create_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kong route.

        Args:
            route_data: Route configuration

        Returns:
            Created route data
        """
        return await self.post("/routes", json_data=route_data)

    async def update_route(
        self, route_id: str, route_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Kong route.

        Args:
            route_id: Route ID or name
            route_data: Route configuration updates

        Returns:
            Updated route data
        """
        return await self.patch(f"/routes/{route_id}", json_data=route_data)

    async def delete_route(self, route_id: str) -> None:
        """Delete Kong route.

        Args:
            route_id: Route ID or name
        """
        await self.delete(f"/routes/{route_id}")

    async def get_plugins_as_list(self, **params: Any) -> List[Dict[str, Any]]:
        """Get all Kong plugins.

        Args:
            **params: Query parameters (offset, size, tags, etc.)

        Returns:
            List of Kong plugins
        """
        response = await self.get("/plugins", params=params)
        return response.get("data", [])  # type: ignore[no-any-return]

    async def get_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Get Kong plugin by ID.

        Args:
            plugin_id: Plugin ID

        Returns:
            Kong plugin data
        """
        return await self.get(f"/plugins/{plugin_id}")

    async def create_plugin(self, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kong plugin.

        Args:
            plugin_data: Plugin configuration

        Returns:
            Created plugin data
        """
        return await self.post("/plugins", json_data=plugin_data)

    async def update_plugin(
        self, plugin_id: str, plugin_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Kong plugin.

        Args:
            plugin_id: Plugin ID
            plugin_data: Plugin configuration updates

        Returns:
            Updated plugin data
        """
        return await self.patch(f"/plugins/{plugin_id}", json_data=plugin_data)

    async def delete_plugin(self, plugin_id: str) -> None:
        """Delete Kong plugin.

        Args:
            plugin_id: Plugin ID
        """
        await self.delete(f"/plugins/{plugin_id}")

    async def health_check(self) -> Dict[str, Any]:
        """Check Kong Admin API health.

        Returns:
            Kong status information
        """
        return await self.get("/status")

    async def get_plugins(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET /plugins with optional query params.
        Returns the full Kong pagination envelope: {"data": [...], "offset": "..."}
        """
        return await self._request("GET", "/plugins", params=params,json_data=None,)
    
    async def get_plugins_by_service(self,service_id:str,params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET /plugins by service id.
        Returns the full Kong pagination envelope: {"data": [...], "offset": "..."}
        """
        return await self._request("GET", f"/services/{service_id}/plugins", params=params,json_data=None,)
    
    async def get_plugins_by_route(self,route_id:str,params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET /plugins by route id.
        Returns the full Kong pagination envelope: {"data": [...], "offset": "..."}
        """
        return await self._request("GET", f"/routes/{route_id}/plugins", params=params,json_data=None,)
    
    async def get_plugins_by_consumer(self,consumer_id:str,params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET /plugins by consumer id.
        Returns the full Kong pagination envelope: {"data": [...], "offset": "..."}
        """
        return await self._request("GET", f"/consumers/{consumer_id}/plugins", params=params,json_data=None)