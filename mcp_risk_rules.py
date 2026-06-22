import json
from mcp.server import Server
from mcp.types import TextContent, Tool

server = Server("RiskRulesDB")

def calculate_debt_to_income(income: float, existing_liabilities: float, new_loan_emi: float) -> float:
    """Calculate DTI ratio"""
    if income == 0:
        return 100.0
    total_debt = existing_liabilities + new_loan_emi
    return (total_debt / income) * 100

def calculate_loan_emi(principal: float, annual_rate: float, months: int) -> float:
    """Calculate monthly EMI"""
    if months == 0 or principal == 0:
        return 0
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return principal / months
    emi = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return emi

def assess_credit_risk(credit_score: int) -> tuple[str, float]:
    """Assess credit risk based on score"""
    if credit_score >= 750:
        return "low", 0.1
    elif credit_score >= 650:
        return "medium", 0.3
    elif credit_score >= 550:
        return "high", 0.6
    else:
        return "very_high", 0.9

def assess_loan_amount_risk(loan_amount: float, income: float, credit_score: int) -> str:
    """Assess loan amount risk"""
    loan_to_income = loan_amount / income

    if credit_score >= 700 and loan_to_income <= 3:
        return "low"
    elif credit_score >= 650 and loan_to_income <= 4:
        return "medium"
    elif credit_score >= 600 and loan_to_income <= 5:
        return "high"
    else:
        return "very_high"

def detect_anomalies(age: int, income: float, credit_score: int, loan_amount: float) -> tuple[bool, str]:
    """Detect anomalies in application"""
    anomalies = []

    if age < 21 or age > 65:
        anomalies.append("Age outside typical lending range")

    if income < 30000:
        anomalies.append("Income below minimum threshold")

    if credit_score < 300 or credit_score > 850:
        anomalies.append("Invalid credit score")

    if loan_amount > income * 10:
        anomalies.append("Loan amount extremely high relative to income")

    if anomalies:
        return True, "; ".join(anomalies)
    return False, "No anomalies detected"

@server.call_tool()
async def handle_analyze_financial_risk(
    income: float,
    credit_score: int,
    loan_amount: float,
    loan_tenure_months: int,
    existing_liabilities: float,
    age: int
) -> TextContent:
    """Analyze financial risk"""
    loan_emi = calculate_loan_emi(loan_amount, 8.5, loan_tenure_months)
    dti_ratio = calculate_debt_to_income(income, existing_liabilities, loan_emi)
    credit_risk_level, credit_risk_score = assess_credit_risk(credit_score)
    loan_risk = assess_loan_amount_risk(loan_amount, income, credit_score)
    anomaly_detected, anomaly_desc = detect_anomalies(age, income, credit_score, loan_amount)

    analysis = {
        "debt_to_income_ratio": round(dti_ratio, 2),
        "dti_risk_flag": dti_ratio > 45,
        "credit_score_risk_level": credit_risk_level,
        "credit_risk_flag": credit_risk_score > 0.5,
        "loan_amount_risk": loan_risk,
        "loan_emi": round(loan_emi, 2),
        "anomaly_detected": anomaly_detected,
        "anomaly_description": anomaly_desc,
        "reasoning": f"DTI ratio is {dti_ratio:.1f}% (threshold: 45%), Credit risk: {credit_risk_level}, Loan risk: {loan_risk}"
    }

    return TextContent(type="text", text=json.dumps(analysis))

server.add_tool(
    Tool(
        name="analyze_financial_risk",
        description="Analyze financial risk based on income, credit score, loan amount, and liabilities",
        inputSchema={
            "type": "object",
            "properties": {
                "income": {"type": "number", "description": "Annual income"},
                "credit_score": {"type": "integer", "description": "Credit score (300-850)"},
                "loan_amount": {"type": "number", "description": "Requested loan amount"},
                "loan_tenure_months": {"type": "integer", "description": "Loan tenure in months"},
                "existing_liabilities": {"type": "number", "description": "Existing liabilities"},
                "age": {"type": "integer", "description": "Applicant age"}
            },
            "required": ["income", "credit_score", "loan_amount", "loan_tenure_months", "existing_liabilities", "age"]
        }
    )
)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
