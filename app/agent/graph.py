import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.prebuilt import ToolNode

from state import AgentState
from mcp_client import MCPClient
from tools import MCPToolManager


load_dotenv()

model = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
)
# model = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
# )



SYSTEM_PROMPT = """
You are an autonomous e-commerce resolution agent.

Your job is to resolve customer requests by using the available
MCP tools. You should act autonomously whenever the required
information can be obtained from the tools.

IMPORTANT RULES:

1. NEVER ask the customer for an order ID if you can identify
   the order using the available tools.

2. NEVER invent customer information, order IDs, product IDs,
   payment information, or other data.

3. For a replacement request, follow this workflow:

   - Identify the customer using available customer/order tools.
   - Find the relevant order.
   - Check return eligibility.
   - Check payment information if required.
   - Create the return.
   - Schedule the pickup.
   - Create the replacement.

4. Routine actions required to resolve the customer's request
   should be performed autonomously.

5. Do NOT perform actions outside the customer's requested
   resolution.

6. If an action is potentially high-impact or outside the
   declared resolution plan, do not attempt to bypass
   authorization controls.

7. Use the MCP tools whenever they can provide the information
   or perform the action you need.

For example:

Customer:
"My headphones are defective. I want a replacement."

You should NOT respond:
"Please provide your order ID."

Instead, use the available tools to identify the customer/order
and continue the resolution workflow.
"""




async def agent_node(
    state: AgentState
):

    messages = state.get(
        "messages",
        []
    )

    response = await model.ainvoke(
        [
            (
                "system",
                SYSTEM_PROMPT
            ),
            *messages
        ]
    )

    return {
        "messages": [
            response
        ]
    }







def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if hasattr(
        last_message,
        "tool_calls"
    ):

        if last_message.tool_calls:
            return "tools"

    return "end"



async def build_graph():

    client = MCPClient()

    await client.connect(
    "commerce",
    "http://127.0.0.1:8001/mcp"
)

    await client.connect(
    "fulfillment",
    "http://127.0.0.1:8002/mcp"
)

    await client.connect(
    "payment",
    "http://127.0.0.1:8003/mcp"
)

    manager = MCPToolManager(client)

    tools = await manager.get_tools()

    print("\nTOOL SCHEMAS:")

    for tool in tools:
        print(f"  ✓ {tool.name}")
        print(tool.args_schema.model_json_schema())

    model_with_tools = model.bind_tools(
        tools
    )

    async def agent(
        state: AgentState
    ):

        # print("\n===== MESSAGES BEFORE GEMINI =====")

        # for i, msg in enumerate(state["messages"]):
        #     print(f"\nMESSAGE {i}")
        #     print("TYPE:", type(msg))
        #     print("CONTENT:", repr(msg.content))
        #     print("TOOL_CALLS:", getattr(msg, "tool_calls", None))
        #     print("TOOL_CALL_ID:", getattr(msg, "tool_call_id", None))

        # print("\n==================================")

        response = await model_with_tools.ainvoke(
            [
                (
                    "system",
                    SYSTEM_PROMPT
                ),
                *state["messages"]
            ]
        )

        return {
            "messages": state["messages"] + [response]
}

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "agent",
        agent
    )

    graph.add_node(
        "tools",
        ToolNode(tools)
    )

    graph.add_edge(
        START,
        "agent"
    )

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )

    graph.add_edge(
        "tools",
        "agent"
    )

    return graph.compile(), client























