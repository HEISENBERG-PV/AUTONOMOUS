from langgraph.graph import StateGraph, START, END

from .state import AgentState

from tools.ecommerce_tools import (
    get_customer,
    get_order,
    check_return_eligibility,
    create_return,
    schedule_pickup,
    create_replacement,
    update_shipping_address
)



def understand_intent(state: AgentState):

    request = state["customer_request"]

    print("\n[AGENT] Understanding customer request...")

    state["intent"] = "product_replacement"
    state["product"] = "headphones"
    state["reason"] = "defective"

    print(f"[AGENT] Intent: {state['intent']}")
    print(f"[AGENT] Product: {state['product']}")
    print(f"[AGENT] Reason: {state['reason']}")

    return state


def create_plan(state: AgentState):

    print("\n[AGENT] Creating execution plan...")

    plan = [
        "get_customer",
        "get_order",
        "check_return_eligibility",
        "create_return",
        "schedule_pickup",
        "create_replacement"
    ]

    state["plan"] = plan

    print("\nPLAN")

    for i, step in enumerate(plan, 1):
        print(f"{i}. {step}")

    return state



def execute_resolution(state: AgentState):

    print("\n[AGENT] Executing resolution...\n")

    customer = get_customer("CUST001")

    order = get_order("ORD001")

    eligibility = check_return_eligibility(
        "ORD001"
    )

    if not eligibility["eligible"]:

        state["status"] = "failed"

        return state

    return_request = create_return(
        "ORD001",
        "defective product"
    )

    pickup = schedule_pickup(
        return_request["return_id"]
    )

    replacement = create_replacement(
        "ORD001"
    )

    state["results"] = {
        "customer": customer,
        "order": order,
        "eligibility": eligibility,
        "return": return_request,
        "pickup": pickup,
        "replacement": replacement
    }

    state["status"] = "completed"

    return state



def attempt_unauthorized_action(state: AgentState):

    print(
        "\n[AGENT] I think changing the "
        "shipping address would help the customer..."
    )

    state["pending_action"] = {
        "tool": "update_shipping_address",
        "arguments": {
            "order_id": "ORD001",
            "new_address": "New Delhi, India"
        }
    }

    state["status"] = "pending_authorization"

    return state



from governance.armoriq import authorize


def authorization_check(state: AgentState):

    action = state["pending_action"]["tool"]

    decision = authorize(action)

    if decision["decision"] == "ALLOW":

        state["status"] = "authorized"

    else:

        state["status"] = "held"

    return state



def human_approval(state: AgentState):

    action = state["pending_action"]

    print("\n" + "=" * 50)
    print("⚠️  HUMAN APPROVAL REQUIRED")
    print("=" * 50)

    print(f"Action: {action['tool']}")

    print(
        f"Arguments: "
        f"{action['arguments']}"
    )

    print(
        "\nReason: "
        "Action is outside declared authorization."
    )

    choice = input(
        "\nApprove action? (yes/no): "
    )

    if choice.lower() == "yes":

        state["status"] = "approved"

    else:

        state["status"] = "rejected"

    return state





def execute_pending_action(state: AgentState):

    action = state["pending_action"]

    if action["tool"] == "update_shipping_address":

        result = update_shipping_address(
            action["arguments"]["order_id"],
            action["arguments"]["new_address"]
        )

        state["results"]["address_update"] = result

    state["status"] = "completed"

    return state




def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node(
        "understand_intent",
        understand_intent
    )

    graph.add_node(
        "create_plan",
        create_plan
    )

    graph.add_node(
        "execute_resolution",
        execute_resolution
    )

    graph.add_node(
        "attempt_unauthorized_action",
        attempt_unauthorized_action
    )

    graph.add_node(
        "authorization_check",
        authorization_check
    )

    graph.add_node(
        "human_approval",
        human_approval
    )

    graph.add_node(
        "execute_pending_action",
        execute_pending_action
    )

    graph.add_edge(
        START,
        "understand_intent"
    )

    graph.add_edge(
        "understand_intent",
        "create_plan"
    )

    graph.add_edge(
        "create_plan",
        "execute_resolution"
    )

    graph.add_edge(
        "execute_resolution",
        "attempt_unauthorized_action"
    )

    graph.add_edge(
        "attempt_unauthorized_action",
        "authorization_check"
    )

    graph.add_conditional_edges(
        "authorization_check",

        lambda state: state["status"],

        {
            "authorized":
                "execute_pending_action",

            "held":
                "human_approval"
        }
    )

    graph.add_conditional_edges(
        "human_approval",

        lambda state: state["status"],

        {
            "approved":
                "execute_pending_action",

            "rejected":
                END
        }
    )

    graph.add_edge(
        "execute_pending_action",
        END
    )

    return graph.compile()








