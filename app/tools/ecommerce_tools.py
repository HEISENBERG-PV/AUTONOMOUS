from typing import Dict


CUSTOMER = {
    "id": "CUST001",
    "name": "Prem Verma",
    "email": "prem@example.com"
}


ORDER = {
    "id": "ORD001",
    "customer_id": "CUST001",
    "product": "Sony WH-1000XM5",
    "status": "delivered",
    "amount": 29999,
    "return_eligible": True,
    "warranty": True
}


def get_customer(customer_id: str) -> Dict:
    print(f"[TOOL] get_customer({customer_id})")

    if customer_id == CUSTOMER["id"]:
        return CUSTOMER

    return {"error": "Customer not found"}


def get_order(order_id: str) -> Dict:
    print(f"[TOOL] get_order({order_id})")

    if order_id == ORDER["id"]:
        return ORDER

    return {"error": "Order not found"}


def check_return_eligibility(order_id: str) -> Dict:
    print(f"[TOOL] check_return_eligibility({order_id})")

    if order_id == ORDER["id"]:
        return {
            "eligible": ORDER["return_eligible"],
            "warranty": ORDER["warranty"]
        }

    return {"eligible": False}


def create_return(order_id: str, reason: str) -> Dict:
    print(f"[TOOL] create_return({order_id}, {reason})")

    return {
        "return_id": "RET001",
        "order_id": order_id,
        "status": "created",
        "reason": reason
    }


def schedule_pickup(return_id: str) -> Dict:
    print(f"[TOOL] schedule_pickup({return_id})")

    return {
        "pickup_id": "PICKUP001",
        "status": "scheduled"
    }


def create_replacement(order_id: str) -> Dict:
    print(f"[TOOL] create_replacement({order_id})")

    return {
        "replacement_id": "REP001",
        "status": "created"
    }


def update_shipping_address(
    order_id: str,
    new_address: str
) -> Dict:

    print(
        f"[TOOL] update_shipping_address("
        f"{order_id}, {new_address})"
    )

    return {
        "status": "updated",
        "new_address": new_address
    }