from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

# Create MCP server
mcp = MCPServer(
    "Commerce MCP"
)


# --------------------------------------------------
# MOCK E-COMMERCE DATA
# --------------------------------------------------

CUSTOMERS = {
    "CUST001": {
        "id": "CUST001",
        "name": "Prem Verma",
        "email": "prem@example.com",
    }
}


ORDERS = {
    "ORD001": {
        "id": "ORD001",
        "customer_id": "CUST001",
        "product": "Sony WH-1000XM5",
        "status": "delivered",
        "amount": 29999,
        "return_window": True,
        "warranty": True,
    }
}


RETURNS = {}


# --------------------------------------------------
# TOOL 1 — GET CUSTOMER
# --------------------------------------------------

@mcp.tool()
def get_customer(customer_id: str) -> dict:
    """
    Retrieve customer information using customer ID.
    """

    customer = CUSTOMERS.get(customer_id)

    if not customer:
        return {
            "success": False,
            "error": "Customer not found"
        }

    return {
        "success": True,
        "customer": customer
    }


# --------------------------------------------------
# TOOL 2 — GET ORDER
# --------------------------------------------------

@mcp.tool()
def get_order(order_id: str) -> dict:
    """
    Retrieve order information using order ID.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "error": "Order not found"
        }

    return {
        "success": True,
        "order": order
    }


# --------------------------------------------------
# TOOL 3 — CHECK RETURN POLICY
# --------------------------------------------------

@mcp.tool()
def check_return_policy(order_id: str) -> dict:
    """
    Check whether an order is eligible for return.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "eligible": False,
            "error": "Order not found"
        }

    eligible = (
        order["status"] == "delivered"
        and order["return_window"]
    )

    return {
        "success": True,
        "eligible": eligible,
        "warranty": order["warranty"],
        "reason": (
            "Order is eligible for return"
            if eligible
            else "Order is not eligible for return"
        )
    }


# --------------------------------------------------
# TOOL 4 — CREATE RETURN
# --------------------------------------------------

@mcp.tool()
def create_return(
    order_id: str,
    reason: str
) -> dict:
    """
    Create a return request for an eligible order.
    """

    order = ORDERS.get(order_id)

    if not order:
        return {
            "success": False,
            "error": "Order not found"
        }

    if not order["return_window"]:
        return {
            "success": False,
            "error": "Order is outside return window"
        }

    return_id = f"RET{len(RETURNS) + 1:03d}"

    return_request = {
        "return_id": return_id,
        "order_id": order_id,
        "reason": reason,
        "status": "created"
    }

    RETURNS[return_id] = return_request

    return {
        "success": True,
        "return": return_request
    }


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    security = TransportSecuritySettings(
    allowed_hosts=[
        "127.0.0.1:8001",
        "localhost:8001",
    ]
)

    mcp.run(
    "streamable-http",
    host="127.0.0.1",
    port=8001,
    streamable_http_path="/mcp",
    transport_security=security,
)