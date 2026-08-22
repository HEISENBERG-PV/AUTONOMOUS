from typing import TypedDict, List, Dict, Any
from typing import Annotated
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):

    customer_request: str

    messages: Annotated[list[BaseMessage], add_messages]


    intent: str

    product: str

    reason: str

    order_id: str

    plan: List[str]

    results: Dict[str, Any]

    status: str