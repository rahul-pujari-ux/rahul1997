import json
from mcp.server import Server
from mcp.types import TextContent, Tool

server = Server("DecisionSynthesis")

@server.call_tool()
async def handle_synthesize_decision(
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_score_risk_level: str,
    loan_amount_risk: str,
    anomaly_detected: bool,
    credit_score: int,
    age: int
) -> TextContent:
    """Synthesize final loan decision"""

    risk_score = 0.0
    factors = []

    if employment_risk == "low":
        risk_score += 10
    elif employment_risk == "medium":
        risk_score += 25
    else:
        risk_score += 50
        factors.append("High employment risk")

    if credit_score_risk_level == "low":
        risk_score += 5
    elif credit_score_risk_level == "medium":
        risk_score += 20
    elif credit_score_risk_level == "high":
        risk_score += 40
        factors.append("High credit risk")
    else:
        risk_score += 60
        factors.append("Very high credit risk")

    if dti_ratio <= 30:
        risk_score += 5
    elif dti_ratio <= 45:
        risk_score += 15
    else:
        risk_score += 35
        factors.append("High debt-to-income ratio")

    if loan_amount_risk == "low":
        risk_score += 5
    elif loan_amount_risk == "medium":
        risk_score += 15
    elif loan_amount_risk == "high":
        risk_score += 30
        factors.append("High loan amount risk")
    else:
        risk_score += 50
        factors.append("Very high loan amount risk")

    if income_stability_score >= 75:
        risk_score -= 10
        factors.append("Strong income stability")
    elif income_stability_score < 50:
        risk_score += 20
        factors.append("Low income stability")

    if anomaly_detected:
        risk_score += 30
        factors.append("Anomalies detected in application")

    if age < 25 or age > 60:
        risk_score += 10
        factors.append("Age outside optimal lending range")

    risk_score = max(0, min(100, risk_score))

    if risk_score < 25:
        decision = "approved"
        confidence = 0.95
    elif risk_score < 45:
        decision = "approved"
        confidence = 0.75
    elif risk_score < 65:
        decision = "manual_review"
        confidence = 0.80
    else:
        decision = "rejected"
        confidence = 0.85

    if not factors:
        factors.append("Application meets standard lending criteria")

    result = {
        "decision": decision,
        "risk_score": round(risk_score, 2),
        "confidence_level": confidence,
        "key_decision_factors": factors,
        "explanation": f"Decision: {decision.upper()}. Risk Score: {risk_score:.1f}/100. Application analyzed based on income stability, employment history, credit profile, debt-to-income ratio, and loan parameters."
    }

    return TextContent(type="text", text=json.dumps(result))

server.add_tool(
    Tool(
        name="synthesize_decision",
        description="Synthesize final loan decision based on all risk factors",
        inputSchema={
            "type": "object",
            "properties": {
                "income_stability_score": {"type": "number"},
                "employment_risk": {"type": "string"},
                "dti_ratio": {"type": "number"},
                "credit_score_risk_level": {"type": "string"},
                "loan_amount_risk": {"type": "string"},
                "anomaly_detected": {"type": "boolean"},
                "credit_score": {"type": "integer"},
                "age": {"type": "integer"}
            },
            "required": ["income_stability_score", "employment_risk", "dti_ratio", "credit_score_risk_level", "loan_amount_risk", "anomaly_detected", "credit_score", "age"]
        }
    )
)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
