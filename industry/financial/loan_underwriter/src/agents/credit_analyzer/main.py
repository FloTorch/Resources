from agents.credit_analyzer.model import CreditAnalyzerInput, CreditAnalyzerOutput
from agents.credit_analyzer.utils import evaluate_credit


from fastapi import FastAPI
app = FastAPI()

@app.post("/process", response_model=CreditAnalyzerOutput)
async def process_credit(input_data: CreditAnalyzerInput):
    return evaluate_credit(input_data)

