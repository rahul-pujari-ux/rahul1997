import json
from mcp.server import Server
from mcp.types import TextContent, Tool

server = Server("DecisionSynthesis")

def build_decision_explanation(decision: str, risk_score: float, composite_scores: dict,
                               factors: list, hard_reject: bool = False,
                               hard_reject_reason: str = "") -> str:
    """Build comprehensive plain-English explanation with component breakdown"""

    if hard_reject:
        return f"HARD REJECT: {hard_reject_reason}. Risk Score: 95.0/100. Decision made immediately per policy violation criteria."

    decision_text = decision.upper().replace("_", " ")

    component_breakdown = []
    for component, score in composite_scores.items():
        if score != 0:
            component_label = component.replace("_", " ").title()
            component_breakdown.append(f"{component_label}: {score:+.1f}")

    breakdown_str = ", ".join(component_breakdown) if component_breakdown else "Baseline factors applied"

    factors_str = "; ".join(factors) if factors else "Application meets standard criteria"

    threshold_note = ""
    if decision == "manual_review":
        threshold_note = " This application is close to approval threshold and requires human officer review."
    elif decision == "approved" and risk_score > 35:
        threshold_note = " Consider possible loan amount adjustment for borderline cases."

    explanation = (
        f"Decision: {decision_text}. Risk Score: {risk_score:.1f}/100 (Composite: {breakdown_str}). "
        f"Key Factors: {factors_str}.{threshold_note}"
    )

    return explanation

@server.call_tool()
async def handle_synthesize_decision(
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_score_risk_level: str,
    loan_amount_risk: str,
    anomaly_detected: bool,
    credit_score: int,
    age: int,
    hard_reject: bool = False,
    hard_reject_reason: str = ""
) -> TextContent:
    """Synthesize final loan decision with score-based tiering"""

    composite_scores = {}

    employment_score = 0
    if employment_risk == "low":
        employment_score = 10
    elif employment_risk == "medium":
        employment_score = 25
    else:
        employment_score = 50
    composite_scores["employment"] = employment_score

    credit_score_component = 0
    if credit_score_risk_level == "low":
        credit_score_component = 5
    elif credit_score_risk_level == "medium":
        credit_score_component = 20
    elif credit_score_risk_level == "high":
        credit_score_component = 40
    else:
        credit_score_component = 60
    composite_scores["credit_risk"] = credit_score_component

    dti_score = 0
    if dti_ratio <= 30:
        dti_score = 5
    elif dti_ratio <= 45:
        dti_score = 15
    else:
        dti_score = 35
    composite_scores["dti_ratio"] = dti_score

    loan_amount_score = 0
    if loan_amount_risk == "low":
        loan_amount_score = 5
    elif loan_amount_risk == "medium":
        loan_amount_score = 15
    elif loan_amount_risk == "high":
        loan_amount_score = 30
    else:
        loan_amount_score = 50
    composite_scores["loan_amount"] = loan_amount_score

    income_stability_adjustment = 0
    if income_stability_score >= 75:
        income_stability_adjustment = -10
    elif income_stability_score < 50:
        income_stability_adjustment = 20
    composite_scores["income_stability"] = income_stability_adjustment

    anomaly_score = 30 if anomaly_detected else 0
    composite_scores["anomalies"] = anomaly_score

    age_adjustment = 10 if (age < 25 or age > 60) else 0
    composite_scores["age"] = age_adjustment

    if hard_reject:
        risk_score = 95.0
        composite_scores["policy_violation"] = 95.0
        decision = "rejected"
        confidence = 0.98
        agent_reasoning = "Hard reject fast path — Decision Agent bypassed per conditional routing"
        factors = [hard_reject_reason]
    else:
        risk_score = sum(composite_scores.values())
        risk_score = max(0, min(100, risk_score))

        agent_reasoning = None

        if risk_score <= 40:
            decision = "approved"
            confidence = 0.95 if risk_score <= 25 else 0.85
        elif risk_score <= 65:
            decision = "manual_review"
            proximity_to_boundary = 65 - risk_score
            confidence = min(0.95, 0.70 + (proximity_to_boundary / 25) * 0.15)
        else:
            decision = "rejected"
            confidence = 0.85

        factors = []
        if employment_risk != "low":
            factors.append(f"Employment Risk: {employment_risk}")
        if credit_score_risk_level != "low":
            factors.append(f"Credit Risk: {credit_score_risk_level} (Score: {credit_score})")
        if dti_ratio > 30:
            factors.append(f"DTI Ratio: {dti_ratio:.1f}%")
        if anomaly_detected:
            factors.append("Anomalies detected in application")
        if income_stability_score >= 75:
            factors.append(f"Strong income stability: {income_stability_score:.0f}/100")
        if not factors:
            factors.append("Application meets standard lending criteria")

    result = {
        "decision": decision,
        "risk_score": round(risk_score, 2),
        "confidence_level": round(confidence, 2),
        "key_decision_factors": factors,
        "composite_risk_breakdown": composite_scores,
        "agent_reasoning": agent_reasoning,
        "explanation": build_decision_explanation(
            decision,
            risk_score,
            composite_scores,
            factors,
            hard_reject,
            hard_reject_reason
        )
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
