"""Kong services management tools."""

from typing import Any, Dict, List, Optional

from kong_mcp_server.kong_client import KongClient


async def get_services() -> List[Dict[str, Any]]:
    """Retrieve Kong services configuration.

    Returns:
        List of Kong services configuration data.
    """
    async with KongClient() as client:
        return await client.get_services()


async def create_service(
    name: str,
    url: str,
    protocol: str = "http",
    host: Optional[str] = None,
    port: Optional[int] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new Kong service.

    Args:
        name: Service name
        url: Service URL
        protocol: Protocol (http, https)
        host: Service host
        port: Service port
        path: Service path

    Returns:
        Created service configuration data.
    """
    service_data: Dict[str, Any] = {
        "name": name,
        "url": url,
        "protocol": protocol,
    }

    if host is not None:
        service_data["host"] = host
    if port is not None:
        service_data["port"] = port
    if path is not None:
        service_data["path"] = path

    async with KongClient() as client:
        return await client.create_service(service_data)


async def update_service(
    service_id: str,
    name: Optional[str] = None,
    url: Optional[str] = None,
    protocol: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing Kong service.

    Args:
        service_id: ID of the service to update
        name: Service name
        url: Service URL
        protocol: Protocol (http, https)
        host: Service host
        port: Service port
        path: Service path

    Returns:
        Updated service configuration data.
    """
    service_data: Dict[str, Any] = {}

    if name is not None:
        service_data["name"] = name
    if url is not None:
        service_data["url"] = url
    if protocol is not None:
        service_data["protocol"] = protocol
    if host is not None:
        service_data["host"] = host
    if port is not None:
        service_data["port"] = port
    if path is not None:
        service_data["path"] = path

    async with KongClient() as client:
        return await client.update_service(service_id, service_data)


async def delete_service(service_id: str) -> Dict[str, Any]:
    """Delete a Kong service.

    Args:
        service_id: ID of the service to delete

    Returns:
        Deletion confirmation data.
    """
    async with KongClient() as client:
        await client.delete_service(service_id)
        return {"message": "Service deleted successfully", "service_id": service_id}
