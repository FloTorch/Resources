import inspect


def generate_prompt(loan_data: dict) -> list:
    role = inspect.cleandoc("""
    You are a loan officer who summarizes and highlights important details about the loan application.
    """)

    task = inspect.cleandoc(f"""
    Summarize the following loan application:
    Name: {loan_data['name']}
    Age: {loan_data['age']}
    Income: {loan_data['income']}
    Loan Amount: {loan_data['loan_amount']}
    Credit Score: {loan_data['credit_score']}
    Existing Liabilities: {loan_data['existing_liabilities']}
    Purpose: {loan_data.get('purpose', 'N/A')}
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
