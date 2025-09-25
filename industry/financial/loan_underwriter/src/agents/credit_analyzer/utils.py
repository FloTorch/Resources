from agents.credit_analyzer.model import CreditAnalyzerInput, CreditAnalyzerOutput
from agents.credit_analyzer.prompt import generate_prompt
from common.flotorch_chat_model import chat_llm


def evaluate_credit(input_data: CreditAnalyzerInput) -> CreditAnalyzerOutput:
    prompt = generate_prompt(input_data.loan_summary, input_data.loan_data)
    response = chat_llm.invoke(prompt)
    credit_assessment = str(response.content).strip()

    # basic score bucketing through text parsing
    credit_assessment_lower = credit_assessment.lower()
    if "rating: low" in credit_assessment_lower:
        credit_rating = "Low"
    elif "rating: high" in credit_assessment_lower:
        credit_rating = "High"
    elif "rating: medium" in credit_assessment_lower:
        credit_rating = "Medium"
    else:
        credit_rating = "N/A"

    return CreditAnalyzerOutput(
        credit_assessment=credit_assessment,
        credit_rating=credit_rating,
        loan_data=input_data.loan_data
    )
