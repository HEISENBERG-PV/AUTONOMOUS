from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings


# --------------------------------------------------
# CREATE MCP SERVER
# --------------------------------------------------

mcp = MCPServer(
    "Payment MCP"
)


# --------------------------------------------------
# MOCK PAYMENT DATA
# --------------------------------------------------

PAYMENTS = {
    "PAY001": {
        "id": "PAY001",
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "amount": 29999,
        "currency": "INR",
        "method": "UPI",
        "status": "completed"
    }
}


REFUNDS = {}


# --------------------------------------------------
# TOOL 1 — GET PAYMENT
# --------------------------------------------------

@mcp.tool()
def get_payment(
    order_id: str
) -> dict:
    """
    Retrieve payment information for an order.
    """

    payment = None

    for value in PAYMENTS.values():

        if value["order_id"] == order_id:
            payment = value
            break

    if not payment:

        return {
            "success": False,
            "error": "Payment not found"
        }

    return {
        "success": True,
        "payment": payment
    }


# --------------------------------------------------
# TOOL 2 — ISSUE REFUND
# --------------------------------------------------

@mcp.tool()
def issue_refund(
    order_id: str,
    amount: float,
    reason: str
) -> dict:
    """
    Issue a refund for an order.

    NOTE:
    This is a high-impact action.
    Authorization is intentionally NOT handled here.
    ArmorIQ will later decide whether the agent
    is allowed to perform this action.
    """

    payment = None

    for value in PAYMENTS.values():

        if value["order_id"] == order_id:
            payment = value
            break

    if not payment:

        return {
            "success": False,
            "error": "Payment not found"
        }

    if amount > payment["amount"]:

        return {
            "success": False,
            "error": "Refund exceeds payment amount"
        }

    refund_id = f"REF{len(REFUNDS) + 1:03d}"

    refund = {
        "refund_id": refund_id,
        "order_id": order_id,
        "amount": amount,
        "currency": payment["currency"],
        "reason": reason,
        "status": "processed"
    }

    REFUNDS[refund_id] = refund

    return {
        "success": True,
        "refund": refund
    }


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    security = TransportSecuritySettings(
        allowed_hosts=[
                "127.0.0.1:8003",
                "localhost:8003",
            ]
    )

    mcp.run(
        "streamable-http",
        host="127.0.0.1",
        port=8003,
        streamable_http_path="/mcp",
        transport_security=security,
    )