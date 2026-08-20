from agent.graph import build_graph


def main():

    print("\n")
    print("=" * 60)
    print("AUTONOMOUS E-COMMERCE RESOLUTION AGENT")
    print("=" * 60)

    request = input(
        "\nCustomer: "
    )

    graph = build_graph()

    initial_state = {

        "customer_request": request,

        "intent": "",

        "product": "",

        "reason": "",

        "plan": [],

        "current_step": 0,

        "results": {},

        "pending_action": {},

        "status": "started"
    }

    result = graph.invoke(
        initial_state
    )

    print("\n")
    print("=" * 60)
    print("FINAL STATUS")
    print("=" * 60)

    print(result["status"])


if __name__ == "__main__":
    main()