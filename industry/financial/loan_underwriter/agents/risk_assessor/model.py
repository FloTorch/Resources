from pydantic import BaseModel


class RiskAssessorInput(BaseModel):
    credit_assessment: str
    credit_rating: str
    loan_data: dict

class RiskAssessorOutput(BaseModel):
    loan_decision: str
    risk_assessment: str
