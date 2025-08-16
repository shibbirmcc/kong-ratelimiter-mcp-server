"""Kong MCP Server main application."""

import asyncio

from fastmcp import FastMCP

mcp = FastMCP("Kong Rate Limiter MCP Server")


@mcp.tool()
async def hello_world() -> str:
    """Simple Hello World tool for testing MCP server functionality."""
    return "Hello World from Kong Rate Limiter MCP Server!"


async def main() -> None:
    """Main entry point for the MCP server."""
    from fastmcp.transports.sse import SseServerTransport  # type: ignore

    async with SseServerTransport() as transport:
        await mcp.run(transport)  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
