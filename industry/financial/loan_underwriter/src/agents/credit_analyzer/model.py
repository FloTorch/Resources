from pydantic import BaseModel


class CreditAnalyzerInput(BaseModel):
    loan_summary: str
    loan_data: dict

class CreditAnalyzerOutput(BaseModel):
    credit_assessment: str
    credit_rating: str
    loan_data: dict
