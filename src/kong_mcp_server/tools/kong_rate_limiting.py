"""Kong rate limiting plugin management tools."""

from typing import Any, Dict, List, Optional

from kong_mcp_server.kong_client import KongClient


# Basic Rate Limiting Plugin Tools

async def create_rate_limiting_plugin(
    minute: Optional[int] = None,
    hour: Optional[int] = None,
    day: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    second: Optional[int] = None,
    limit_by: str = "consumer",
    policy: str = "local",
    fault_tolerant: bool = True,
    hide_client_headers: bool = False,
    redis_host: Optional[str] = None,
    redis_port: int = 6379,
    redis_password: Optional[str] = None,
    redis_timeout: int = 2000,
    redis_database: int = 0,
    service_id: Optional[str] = None,
    route_id: Optional[str] = None,
    consumer_id: Optional[str] = None,
    enabled: bool = True,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a basic rate limiting plugin.

    Args:
        minute: Number of requests per minute
        hour: Number of requests per hour
        day: Number of requests per day
        month: Number of requests per month
        year: Number of requests per year
        second: Number of requests per second
        limit_by: Entity to limit by (consumer, credential, ip, service, header,
            path, consumer-group)
        policy: Rate limiting policy (local, cluster, redis)
        fault_tolerant: Whether to allow requests when rate limiting service
            is unavailable
        hide_client_headers: Whether to hide rate limiting headers from client
        redis_host: Redis host for redis policy
        redis_port: Redis port
        redis_password: Redis password
        redis_timeout: Redis timeout in milliseconds
        redis_database: Redis database number
        service_id: Service ID to apply plugin to (optional for service scope)
        route_id: Route ID to apply plugin to (optional for route scope)
        consumer_id: Consumer ID to apply plugin to (optional for consumer scope)
        enabled: Whether plugin is enabled
        tags: Plugin tags

    Returns:
        Created rate limiting plugin data.
    """
    config: Dict[str, Any] = {
        "limit_by": limit_by,
        "policy": policy,
        "fault_tolerant": fault_tolerant,
        "hide_client_headers": hide_client_headers,
    }

    # Add time-based limits
    if second is not None:
        config["second"] = second
    if minute is not None:
        config["minute"] = minute
    if hour is not None:
        config["hour"] = hour
    if day is not None:
        config["day"] = day
    if month is not None:
        config["month"] = month
    if year is not None:
        config["year"] = year

    # Add Redis configuration for redis policy
    if policy == "redis":
        if redis_host:
            config["redis_host"] = redis_host
        config["redis_port"] = redis_port
        config["redis_timeout"] = redis_timeout
        config["redis_database"] = redis_database
        if redis_password:
            config["redis_password"] = redis_password

    plugin_data: Dict[str, Any] = {
        "name": "rate-limiting",
        "config": config,
        "enabled": enabled,
    }

    if tags:
        plugin_data["tags"] = tags

    # Determine endpoint based on scope
    endpoint = "/plugins"
    if service_id:
        endpoint = f"/services/{service_id}/plugins"
    elif route_id:
        endpoint = f"/routes/{route_id}/plugins"
    elif consumer_id:
        endpoint = f"/consumers/{consumer_id}/plugins"

    async with KongClient() as client:
        return await client.post(endpoint, json_data=plugin_data)


async def get_rate_limiting_plugins(
    service_id: Optional[str] = None,
    route_id: Optional[str] = None,
    consumer_id: Optional[str] = None,
    name: str = "rate-limiting",
    size: int = 100,
    offset: Optional[str] = None,
    tags: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve rate limiting plugins with filtering.

    Args:
        service_id: Filter by service ID
        route_id: Filter by route ID
        consumer_id: Filter by consumer ID
        name: Plugin name to filter by
        size: Number of plugins to retrieve
        offset: Offset for pagination
        tags: Filter by tags

    Returns:
        List of rate limiting plugin data.
    """
    params: Dict[str, Any] = {
        "name": name,
        "size": size,
    }

    if offset:
        params["offset"] = offset
    if tags:
        params["tags"] = tags

    # Determine endpoint based on scope
    endpoint = "/plugins"
    if service_id:
        endpoint = f"/services/{service_id}/plugins"
    elif route_id:
        endpoint = f"/routes/{route_id}/plugins"
    elif consumer_id:
        endpoint = f"/consumers/{consumer_id}/plugins"

    async with KongClient() as client:
        response = await client.get(endpoint, params=params)
        return response.get("data", [])


async def update_rate_limiting_plugin(
    plugin_id: str,
    minute: Optional[int] = None,
    hour: Optional[int] = None,
    day: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    second: Optional[int] = None,
    limit_by: Optional[str] = None,
    policy: Optional[str] = None,
    fault_tolerant: Optional[bool] = None,
    hide_client_headers: Optional[bool] = None,
    redis_host: Optional[str] = None,
    redis_port: Optional[int] = None,
    redis_password: Optional[str] = None,
    redis_timeout: Optional[int] = None,
    redis_database: Optional[int] = None,
    enabled: Optional[bool] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Update a rate limiting plugin configuration.

    Args:
        plugin_id: Plugin ID to update
        minute: Number of requests per minute
        hour: Number of requests per hour
        day: Number of requests per day
        month: Number of requests per month
        year: Number of requests per year
        second: Number of requests per second
        limit_by: Entity to limit by
        policy: Rate limiting policy
        fault_tolerant: Whether to allow requests when rate limiting service
            is unavailable
        hide_client_headers: Whether to hide rate limiting headers from client
        redis_host: Redis host for redis policy
        redis_port: Redis port
        redis_password: Redis password
        redis_timeout: Redis timeout in milliseconds
        redis_database: Redis database number
        enabled: Whether plugin is enabled
        tags: Plugin tags

    Returns:
        Updated rate limiting plugin data.
    """
    config: Dict[str, Any] = {}
    plugin_data: Dict[str, Any] = {}

    # Update time-based limits
    if second is not None:
        config["second"] = second
    if minute is not None:
        config["minute"] = minute
    if hour is not None:
        config["hour"] = hour
    if day is not None:
        config["day"] = day
    if month is not None:
        config["month"] = month
    if year is not None:
        config["year"] = year

    # Update other configuration
    if limit_by is not None:
        config["limit_by"] = limit_by
    if policy is not None:
        config["policy"] = policy
    if fault_tolerant is not None:
        config["fault_tolerant"] = fault_tolerant
    if hide_client_headers is not None:
        config["hide_client_headers"] = hide_client_headers

    # Update Redis configuration
    if redis_host is not None:
        config["redis_host"] = redis_host
    if redis_port is not None:
        config["redis_port"] = redis_port
    if redis_password is not None:
        config["redis_password"] = redis_password
    if redis_timeout is not None:
        config["redis_timeout"] = redis_timeout
    if redis_database is not None:
        config["redis_database"] = redis_database

    if config:
        plugin_data["config"] = config

    if enabled is not None:
        plugin_data["enabled"] = enabled
    if tags is not None:
        plugin_data["tags"] = tags

    async with KongClient() as client:
        return await client.patch(f"/plugins/{plugin_id}", json_data=plugin_data)


async def delete_rate_limiting_plugin(plugin_id: str) -> Dict[str, Any]:
    """Delete a rate limiting plugin.

    Args:
        plugin_id: Plugin ID to delete

    Returns:
        Deletion confirmation data.
    """
    async with KongClient() as client:
        await client.delete(f"/plugins/{plugin_id}")
        return {
            "message": "Rate limiting plugin deleted successfully",
            "plugin_id": plugin_id
        }


# General Plugin Management Tools

async def get_plugin(plugin_id: str) -> Dict[str, Any]:
    """Get a specific plugin by ID.

    Args:
        plugin_id: Plugin ID

    Returns:
        Plugin data.
    """
    async with KongClient() as client:
        return await client.get_plugin(plugin_id)


async def get_plugins(
    name: Optional[str] = None,
    service_id: Optional[str] = None,
    route_id: Optional[str] = None,
    consumer_id: Optional[str] = None,
    size: int = 100,
    offset: Optional[str] = None,
    tags: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get all plugins with optional filtering.

    Args:
        name: Filter by plugin name
        service_id: Filter by service ID
        route_id: Filter by route ID
        consumer_id: Filter by consumer ID
        size: Number of plugins to retrieve
        offset: Offset for pagination
        tags: Filter by tags

    Returns:
        List of plugin data.
    """
    params: Dict[str, Any] = {"size": size}

    if name:
        params["name"] = name
    if offset:
        params["offset"] = offset
    if tags:
        params["tags"] = tags

    # Determine endpoint based on scope
    endpoint = "/plugins"
    if service_id:
        endpoint = f"/services/{service_id}/plugins"
    elif route_id:
        endpoint = f"/routes/{route_id}/plugins"
    elif consumer_id:
        endpoint = f"/consumers/{consumer_id}/plugins"

    async with KongClient() as client:
        response = await client.get(endpoint, params=params)
        return response.get("data", [])
