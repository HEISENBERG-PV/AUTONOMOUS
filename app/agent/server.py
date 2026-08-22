from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from graph import build_graph

app = FastAPI(title="E-commerce Resolution Agent")


class AgentRequest(BaseModel):
    message: str


@app.get("/")
async def health():
    return {
        "status": "online",
        "agent": "E-commerce Resolution Agent"
    }


@app.post("/run")
async def run_agent(request: AgentRequest):

    graph, client = await build_graph()

    initial_state = {
        "customer_request": request.message,
        "messages": [
            HumanMessage(content=request.message)
        ],
        "intent": "",
        "product": "",
        "reason": "",
        "order_id": "",
        "plan": [],
        "results": {},
        "status": "running",
    }

    try:
        result = await graph.ainvoke(initial_state)

        return {
            "status": result.get("status", "completed"),
            "intent": result.get("intent", ""),
            "product": result.get("product", ""),
            "reason": result.get("reason", ""),
            "order_id": result.get("order_id", ""),
            "plan": result.get("plan", []),
            "results": result.get("results", {}),
        }

    finally:
        await client.close()