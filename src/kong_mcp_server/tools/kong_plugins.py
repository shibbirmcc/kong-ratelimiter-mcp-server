"""Kong plugins management tools."""

from typing import Any, Dict, List, Optional

from kong_mcp_server.kong_client import KongClient


async def get_plugins(
    name: Optional[str] = None, offset: Optional[str] = None, size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve Kong plugins.

    Args:
    name: Filter by plugin name (e.g., "rate-limiting", "rate-limiting-advanced")
    offset: Pagination cursor returned by Kong from a previous call
    size: Page size (Kong default is typically 100)

    Returns:
        List of Kong plugins data.
    """
    if size is not None:
        if size < 1 or size > 1000:
            raise ValueError("Size must be between 1 and 1000")

    params: Dict[str, Any] = {}
    if name:
        params["name"] = name
    if offset:
        params["offset"] = offset
    if size:
        params["size"] = size

    async with KongClient() as client:
        response = await client.get_plugins(params=params)
    next_offset = response.get("offset")
    if not next_offset and "next" in response:
        next_offset = response.get("next")

    return {
        "data": response.get("data", []),
        "offset": next_offset,
    }


async def get_plugins_by_service(
    service_id: str, size: Optional[int] = None, offset: Optional[str] = None
) -> dict[str, Any]:
    """
    Retrieve plugins associated with a specific Kong service.

    Args:
        service_id: The ID (or name) of the Kong service.
        size: Optional number of plugins to return.
        offset: Optional pagination cursor.

    Returns:
        A dictionary with:
        - data: List of plugin objects
        - next: URL for next page if pagination is present
    """
    params: Dict[str, Any] = {}
    if size:
        params["size"] = size
    if offset:
        params["offset"] = offset

    async with KongClient() as client:
        return await client.get_plugins_by_service(service_id=service_id, params=params)


async def get_plugins_by_route(
    route_id: str, size: Optional[int] = None, offset: Optional[str] = None
) -> dict[str, Any]:
    """
    Retrieve plugins associated with a specific Kong route.

    Args:
        route_id: The ID (or name) of the Kong route.
        size: Optional number of plugins to return.
        offset: Optional pagination cursor.

    Returns:
        A dictionary with:
        - data: List of plugin objects
        - next: URL for next page if pagination is present
    """
    params: Dict[str, Any] = {}
    if size:
        params["size"] = size
    if offset:
        params["offset"] = offset

    async with KongClient() as client:
        return await client.get_plugins_by_route(route_id=route_id, params=params)


async def get_plugins_by_consumer(
    consumer_id: str, size: Optional[int] = None, offset: Optional[str] = None
) -> dict[str, Any]:
    """
    Retrieve plugins associated with a specific Kong consumer.

    Args:
        consumer_id: The ID (or name) of the Kong consumer.
        size: Optional number of plugins to return.
        offset: Optional pagination cursor.

    Returns:
        A dictionary with:
        - data: List of plugin objects
        - next: URL for next page if pagination is present
    """
    params: Dict[str, Any] = {}
    if size:
        params["size"] = size
    if offset:
        params["offset"] = offset

    async with KongClient() as client:
        return await client.get_plugins_by_consumer(
            consumer_id=consumer_id, params=params
        )
