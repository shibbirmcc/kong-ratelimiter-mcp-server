"""Kong MCP Server main application."""

import importlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

mcp = FastMCP("Kong Rate Limiter MCP Server")


# Add missing standard MCP endpoints
@mcp.custom_route("/api", methods=["GET"])
async def api_discovery(request: Request) -> JSONResponse:
    """Standard MCP API discovery endpoint."""
    return JSONResponse(
        {
            "name": "Kong Rate Limiter MCP Server",
            "version": "0.1.2",
            "protocol_version": "2025-06-18",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False,
                "sampling": False,
            },
            "endpoints": {
                "sse": "/sse/",
                "ping": "/sse/ping",
                "request": "/sse/request",
            },
        }
    )


@mcp.custom_route("/apis", methods=["GET"])
async def apis_discovery(request: Request) -> Response:
    """Alternative API discovery endpoint for compatibility."""
    return await api_discovery(request)


@mcp.custom_route("/sse/ping", methods=["GET", "POST"])
async def sse_ping(request: Request) -> JSONResponse:
    """SSE ping endpoint for health checks."""
    return JSONResponse(
        {
            "jsonrpc": "2.0",
            "method": "ping",
            "result": {"status": "ok", "timestamp": time.time()},
        }
    )


@mcp.custom_route("/sse/request", methods=["POST"])
async def sse_request(request: Request) -> JSONResponse:
    """SSE request endpoint for MCP JSON-RPC messages."""
    try:
        body = await request.json()

        # Handle tool calls
        if body.get("method") == "tools/call":
            tool_name = body.get("params", {}).get("name")
            if tool_name:
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Tool {tool_name} executed via SSE request",  # noqa: E501
                                }
                            ]
                        },
                    }
                )

        # Default response for other requests
        return JSONResponse(
            {"jsonrpc": "2.0", "id": body.get("id"), "result": {"status": "received"}}
        )

    except Exception as e:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error", "data": str(e)},
            },
            status_code=500,
        )


def load_tools_config() -> Dict[str, Any]:
    """Load tools configuration from JSON file.

    Returns:
        Dictionary containing tools configuration.
    """
    config_path = Path(__file__).parent / "tools_config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def register_tool(tool_config: Dict[str, Any]) -> None:
    """Register a tool with the MCP server.

    Args:
        tool_config: Tool configuration dictionary.
    """
    module_name = tool_config["module"]
    function_name = tool_config["function"]

    try:
        module = importlib.import_module(module_name)
        tool_function = getattr(module, function_name)

        # Register the tool with MCP
        mcp.tool(name=tool_config["name"], description=tool_config["description"])(
            tool_function
        )
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not load tool {tool_config['name']}: {e}")


def setup_tools() -> None:
    """Set up all enabled tools from configuration."""
    config = load_tools_config()

    for tool_name, tool_config in config["tools"].items():
        if tool_config.get("enabled", False):
            register_tool(tool_config)


def main() -> None:
    """Main entry point for the MCP server."""
    # Set up tools before starting the server
    setup_tools()

    # Get port from environment variable with fallback to 8080
    port = int(os.environ.get("FASTMCP_PORT", "8080"))

    # Run the server with SSE transport on /sse/ endpoint
    mcp.run("sse", path="/sse/", port=port)


if __name__ == "__main__":
    main()
