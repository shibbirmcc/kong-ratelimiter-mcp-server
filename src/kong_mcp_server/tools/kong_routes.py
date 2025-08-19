"""Kong routes management tools."""

from typing import Any, Dict, List, Optional

from kong_mcp_server.kong_client import KongClient


async def get_routes() -> List[Dict[str, Any]]:
    """Retrieve Kong routes configuration.

    Returns:
        List of Kong routes configuration data.
    """
    async with KongClient() as client:
        return await client.get_routes()


async def create_route(
    service_id: str,
    name: Optional[str] = None,
    protocols: Optional[List[str]] = None,
    methods: Optional[List[str]] = None,
    hosts: Optional[List[str]] = None,
    paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new Kong route.

    Args:
        service_id: ID of the service this route belongs to
        name: Route name
        protocols: List of protocols (http, https)
        methods: List of HTTP methods
        hosts: List of hostnames
        paths: List of paths

    Returns:
        Created route configuration data.
    """
    route_data: Dict[str, Any] = {"service": {"id": service_id}}

    if name is not None:
        route_data["name"] = name
    if protocols is not None:
        route_data["protocols"] = protocols
    if methods is not None:
        route_data["methods"] = methods
    if hosts is not None:
        route_data["hosts"] = hosts
    if paths is not None:
        route_data["paths"] = paths

    async with KongClient() as client:
        return await client.create_route(route_data)


async def update_route(
    route_id: str,
    service_id: Optional[str] = None,
    name: Optional[str] = None,
    protocols: Optional[List[str]] = None,
    methods: Optional[List[str]] = None,
    hosts: Optional[List[str]] = None,
    paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Update an existing Kong route.

    Args:
        route_id: ID of the route to update
        service_id: ID of the service this route belongs to
        name: Route name
        protocols: List of protocols (http, https)
        methods: List of HTTP methods
        hosts: List of hostnames
        paths: List of paths

    Returns:
        Updated route configuration data.
    """
    route_data: Dict[str, Any] = {}

    if service_id is not None:
        route_data["service"] = {"id": service_id}
    if name is not None:
        route_data["name"] = name
    if protocols is not None:
        route_data["protocols"] = protocols
    if methods is not None:
        route_data["methods"] = methods
    if hosts is not None:
        route_data["hosts"] = hosts
    if paths is not None:
        route_data["paths"] = paths

    async with KongClient() as client:
        return await client.update_route(route_id, route_data)


async def delete_route(route_id: str) -> Dict[str, Any]:
    """Delete a Kong route.

    Args:
        route_id: ID of the route to delete

    Returns:
        Deletion confirmation data.
    """
    async with KongClient() as client:
        await client.delete_route(route_id)
        return {"message": "Route deleted successfully", "route_id": route_id}
