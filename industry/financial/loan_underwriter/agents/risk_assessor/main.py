from agents.risk_assessor.model import RiskAssessorInput, RiskAssessorOutput
from agents.risk_assessor.utils import assess_risk


from fastapi import FastAPI
app = FastAPI()

@app.post("/process", response_model=RiskAssessorOutput)
async def process_risk(input_data: RiskAssessorInput):
    return assess_risk(input_data)
