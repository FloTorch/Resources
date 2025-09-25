from agents.loan_parser.model import LoanParserInput, LoanParserOutput
from agents.loan_parser.utils import parse_application


from fastapi import FastAPI
app = FastAPI()

@app.post("/process", response_model=LoanParserOutput)
async def process_application(input_data: LoanParserInput):
    return parse_application(input_data)
