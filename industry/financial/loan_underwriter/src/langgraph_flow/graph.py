import os
import httpx
from typing import Any, TypedDict
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from config import settings

# Load MCP server URLs from .env
LOAN_PARSER_URL = settings.loan_parser_url
CREDIT_ANALYZER_URL = settings.credit_analyzer_url
RISK_ASSESSOR_URL = settings.risk_assessor_url


# State schema
class State(TypedDict):
    output: Any


# MCP call wrapper
def call_mcp_server(url):
    async def fn(state: State) -> State:
        print(f"[DEBUG] Calling {url} with payload:", state)
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.post(url, json=state["output"])
            response.raise_for_status()
            return {"output": response.json()}

    return RunnableLambda(fn).with_config({"run_name": f"CallMCP::{url.split(':')[2]}"})


# Build LangGraph
def build_graph():
    graph = StateGraph(State)

    graph.add_node("LoanParser", call_mcp_server(LOAN_PARSER_URL))
    graph.add_node("CreditAnalyzer", call_mcp_server(CREDIT_ANALYZER_URL))
    graph.add_node("RiskAssessor", call_mcp_server(RISK_ASSESSOR_URL))

    graph.set_entry_point("LoanParser")
    graph.add_edge("LoanParser", "CreditAnalyzer")
    graph.add_edge("CreditAnalyzer", "RiskAssessor")
    graph.set_finish_point("RiskAssessor")

    return graph.compile()
