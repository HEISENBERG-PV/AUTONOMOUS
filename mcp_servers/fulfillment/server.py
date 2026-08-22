from mcp.server import MCPServer

from mcp.server.transport_security import TransportSecuritySettings

# --------------------------------------------------
# CREATE MCP SERVER
# --------------------------------------------------

mcp = MCPServer(
    "Fulfillment MCP"
)


# --------------------------------------------------
# MOCK DATA
# --------------------------------------------------

PICKUPS = {}

REPLACEMENTS = {}

ORDERS = {
    "ORD001": {
        "id": "ORD001",
        "product": "Sony WH-1000XM5",
        "customer_id": "CUST001",
        "shipping_address": "Delhi, India",
    }
}


# --------------------------------------------------
# TOOL 1 — SCHEDULE PICKUP
# --------------------------------------------------

@mcp.tool()
def schedule_pickup(
    return_id: str
) -> dict:
    """
    Schedule a pickup for a return request.
    """

    pickup_id = f"PICKUP{len(PICKUPS) + 1:03d}"

    pickup = {
        "pickup_id": pickup_id,
        "return_id": return_id,
        "status": "scheduled",
        "pickup_date": "2026-08-22"
    }

    PICKUPS[pickup_id] = pickup

    return {
        "success": True,
        "pickup": pickup
    }


# --------------------------------------------------
# TOOL 2 — CREATE REPLACEMENT
# --------------------------------------------------

@mcp.tool()
def create_replacement(
    order_id: str
) -> dict:
    """
    Create a replacement shipment for an order.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "error": "Order not found"
        }

    replacement_id = (
        f"REP{len(REPLACEMENTS) + 1:03d}"
    )

    replacement = {
        "replacement_id": replacement_id,
        "order_id": order_id,
        "product": order["product"],
        "status": "created",
        "shipping_address": order["shipping_address"]
    }

    REPLACEMENTS[replacement_id] = replacement

    return {
        "success": True,
        "replacement": replacement
    }


# --------------------------------------------------
# TOOL 3 — UPDATE SHIPPING ADDRESS
# --------------------------------------------------

@mcp.tool()
def update_shipping_address(
    order_id: str,
    new_address: str
) -> dict:
    """
    Update the shipping address for an order.

    NOTE:
    This is intentionally a high-impact action.
    The MCP server does NOT perform authorization.
    Authorization will be handled by ArmorIQ.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "error": "Order not found"
        }

    old_address = order["shipping_address"]

    order["shipping_address"] = new_address

    return {
        "success": True,
        "order_id": order_id,
        "old_address": old_address,
        "new_address": new_address,
        "status": "updated"
    }


# --------------------------------------------------
# START SERVER
# --------------------------------------------------



if __name__ == "__main__":
    security = TransportSecuritySettings(
        allowed_hosts=[
                "127.0.0.1:8002",
                "localhost:8002",
            ]
    )

    mcp.run(
        "streamable-http",
        host="127.0.0.1",
        port=8002,
        streamable_http_path="/mcp",
        transport_security=security,
    )