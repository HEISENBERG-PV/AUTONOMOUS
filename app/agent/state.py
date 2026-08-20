from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):

    customer_request: str

    intent: str

    product: str

    reason: str

    plan: List[str]

    current_step: int

    results: Dict[str, Any]

    pending_action: Dict[str, Any]

    status: str