import inspect


def generate_prompt(credit_assessment: str, credit_rating: str, loan_data: dict) -> list:
    role = inspect.cleandoc("""
    You are a risk manager. 
    Output the decision explicitly as 'Decision: Approved' or 'Decision: Denied'.
    """)
    
    task = inspect.cleandoc(f"""
    Credit Assessment:
    {credit_assessment}
    Credit Rating: 
    {credit_rating}
    Loan Data:
    {loan_data}
    """)
    
    return [
        {
            "role": "system",
            "content":  role,
        },
        {
            "role": "user",
            "content": task,
        },
    ]
