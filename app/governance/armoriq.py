AUTHORIZED_ACTIONS = {
    "get_customer",
    "get_order",
    "check_return_eligibility",
    "create_return",
    "schedule_pickup",
    "create_replacement"
}


def authorize(action: str):

    print(
        f"\n[ARMORIQ] Checking authorization: {action}"
    )

    if action in AUTHORIZED_ACTIONS:

        print("[ARMORIQ] ✓ ALLOWED")

        return {
            "decision": "ALLOW",
            "reason": "Action is inside declared plan"
        }

    print("[ARMORIQ] 🛑 HOLD")

    return {
        "decision": "HOLD",
        "reason": "Action is outside declared authorization"
    }