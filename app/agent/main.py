import asyncio

from langchain_core.messages import HumanMessage

from graph import build_graph


async def main():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "AUTONOMOUS E-COMMERCE RESOLUTION AGENT"
    )

    print(
        "=" * 60
    )

    request = input("Customer: ")
    customer_id = input("\nCustomer ID: ")
    order_id = input("Order ID: ")

    request_with_context = f"""
    Customer ID: {customer_id}
    Order ID: {order_id}
    Customer Request:
    {request}
    """

    graph, client = await build_graph()

    initial_state = {

        "customer_request": request,

        "messages": [
            HumanMessage(
                content=request_with_context
            )
        ],

        "intent": "",

        "product": "",

        "reason": "",

        "order_id": "",

        "plan": [],

        "results": {},

        "status": "running",
    }

    result = await graph.ainvoke(
        initial_state
    )

    print(
        "\n"
        + "=" * 60
    )

    print("AGENT FINISHED")

    print(
        "=" * 60
    )

    for message in result["messages"]:

        print(
            f"\n{message}"
        )

    await client.close()


if __name__ == "__main__":

    asyncio.run(main())