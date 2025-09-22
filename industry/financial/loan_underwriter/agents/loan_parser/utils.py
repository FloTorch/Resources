from agents.loan_parser.model import LoanParserInput, LoanParserOutput
from agents.loan_parser.prompt import generate_prompt
from common.flotorch_chat_model import chat_llm


def parse_application(input_data: LoanParserInput) -> LoanParserOutput:
    loan_data = input_data.model_dump()
    prompt = generate_prompt(loan_data)
    response = chat_llm.invoke(prompt)
    loan_summary = str(response.content).strip()

    return LoanParserOutput(
        loan_summary=loan_summary,
        loan_data=loan_data
    )
