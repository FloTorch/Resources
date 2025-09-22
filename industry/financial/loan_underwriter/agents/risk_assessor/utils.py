from agents.risk_assessor.model import RiskAssessorInput, RiskAssessorOutput
from agents.risk_assessor.prompt import generate_prompt
from common.flotorch_chat_model import chat_llm


def assess_risk(input_data: RiskAssessorInput) -> RiskAssessorOutput:
    prompt = generate_prompt(
        credit_assessment=input_data.credit_assessment,
        credit_rating=input_data.credit_rating,
        loan_data=input_data.loan_data
    )
    
    response = chat_llm.invoke(prompt)
    risk_assessment = str(response.content).strip()
    risk_assessment_lower = risk_assessment.lower()

    if "decision: approved" in risk_assessment_lower:
        loan_decision = "Approved"
    elif "decision: denied" in risk_assessment_lower:
        loan_decision = "Denied"
    else:
        loan_decision = "Undetermined"

    return RiskAssessorOutput(
        loan_decision=loan_decision,
        risk_assessment=risk_assessment
    )
