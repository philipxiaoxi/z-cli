import asyncio
import json

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import Server

from .client import request

server = Server("zspace")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="make_request",
            description="Send an HTTP request to any URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP method",
                    },
                    "url": {"type": "string", "description": "Target URL"},
                    "headers": {
                        "type": "object",
                        "description": "Optional HTTP headers (key: value)",
                        "additionalProperties": {"type": "string"},
                    },
                    "body": {
                        "type": "object",
                        "description": "Optional JSON request body",
                    },
                },
                "required": ["method", "url"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "make_request":
        raise ValueError(f"Unknown tool: {name}")

    resp = request(
        method=arguments["method"],
        url=arguments["url"],
        headers=arguments.get("headers"),
        json=arguments.get("body"),
    )

    try:
        data = resp.json()
        text = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        text = resp.text

    return [types.TextContent(type="text", text=text)]


def serve():
    asyncio.run(_run())


async def _run():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
