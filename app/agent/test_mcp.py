import asyncio
from mcp_client import MCPClient


async def main():

    client = MCPClient()

    await client.connect(
        "commerce",
        "mcp_servers/commerce/server.py"
    )

    await client.connect(
        "fulfillment",
        "mcp_servers/fulfillment/server.py"
    )

    await client.connect(
        "payment",
        "mcp_servers/payment/server.py"
    )

    tools = await client.list_tools()

    print("\n" + "=" * 60)
    print("AVAILABLE MCP TOOLS")
    print("=" * 60)

    for server, server_tools in tools.items():

        print(f"\n{server.upper()}")

        for tool in server_tools:

            print(
                f"  • {tool.name}"
            )

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())