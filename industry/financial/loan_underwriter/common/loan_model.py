from pydantic import BaseModel


class LoanDetails(BaseModel):
    name: str
    age: int
    income: float
    loan_amount: float
    credit_score: int
    existing_liabilities: float
    purpose: str

class LoanRequest(BaseModel):
    loan_details: LoanDetails
