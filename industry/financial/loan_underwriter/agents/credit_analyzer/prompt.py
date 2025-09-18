import inspect


def generate_prompt(loan_summary: str, loan_data: dict) -> list:
    role = inspect.cleandoc("""
    You are a credit analyst.
    Rate the applicant’s creditworthiness as Low, Medium, or High.
    Output the decision explicitly as 'Rating: Low' or 'Rating: Medium' or 'Rating: High'.
    """)
    
    task = inspect.cleandoc(f"""
    Loan Summary:
    {loan_summary}
    Loan Data:
    {loan_data}
    """)
    
    return [
        {
            "role": "system",
            "content": role,
        },
        {
            "role": "user",
            "content": task,
        },
    ]
