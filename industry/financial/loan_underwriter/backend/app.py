from langgraph_flow.graph import build_graph
from common.loan_model import LoanRequest
from langgraph_flow.graph import State
from config import settings


from fastapi import FastAPI
app = FastAPI()

@app.on_event("startup")
async def check_env():
    print("✅ Environment variables loaded successfully")

graph = build_graph()

@app.post("/process")
async def evaluate_loan(loan_request: LoanRequest):    
    data = loan_request.model_dump()    
    loan_input = data["loan_details"]
    state : State = {
        "output": loan_input
    }
    decision = await graph.ainvoke(state)
    return decision