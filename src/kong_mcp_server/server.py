"""Kong MCP Server main application."""

import importlib
import json
import os
from pathlib import Path
from typing import Any, Dict

from fastmcp import FastMCP

mcp = FastMCP("Kong Rate Limiter MCP Server")


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
