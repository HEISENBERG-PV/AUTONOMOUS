import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=r"C:\Users\muska\OneDrive\Desktop\AUTONOMOUS\.venv\Scripts\python.exe",
        args=[
            r"C:\Users\muska\OneDrive\Desktop\AUTONOMOUS\mcp_servers\commerce\server.py"
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.list_tools()

            print("\nTOOLS DISCOVERED:")
            for tool in result.tools:
                print("-", tool.name)


if __name__ == "__main__":
    asyncio.run(main())