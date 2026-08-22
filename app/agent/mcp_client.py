from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPClient:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions = {}

    async def connect(
        self,
        name: str,
        server_url: str
    ):
        transport = await self.exit_stack.enter_async_context(
            streamable_http_client(server_url)
        )

        read_stream, write_stream = transport

        session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        await session.initialize()

        self.sessions[name] = session

        print(f"✓ Connected to {name} MCP")

    async def list_tools(self):
        all_tools = {}

        for name, session in self.sessions.items():
            response = await session.list_tools()
            all_tools[name] = response.tools

        return all_tools

    async def call_tool(
        self,
        server: str,
        tool: str,
        arguments: dict
    ):
        session = self.sessions[server]

        return await session.call_tool(
            tool,
            arguments
        )

    async def close(self):
        await self.exit_stack.aclose()