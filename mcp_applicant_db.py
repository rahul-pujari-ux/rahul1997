import json
from typing import Any
from mcp.server import Server
from mcp.types import TextContent, Tool
import mcp.types as types

server = Server("ApplicantDB")

applicants_db = {
    "APPLICANT_001": {
        "age": 35,
        "income": 75000,
        "employment_type": "salaried",
        "years_employed": 8,
        "previous_defaults": 0,
        "accounts_opened": 3
    },
    "APPLICANT_002": {
        "age": 42,
        "income": 120000,
        "employment_type": "self_employed",
        "years_employed": 12,
        "previous_defaults": 1,
        "accounts_opened": 5
    }
}

def calculate_income_stability(years_employed: int, employment_type: str, previous_defaults: int) -> float:
    """Calculate income stability score (0-100)"""
    score = 50.0

    if employment_type == "salaried":
        score += 30
    elif employment_type == "self_employed":
        score += 15
    elif employment_type == "business_owner":
        score += 10

    if years_employed >= 10:
        score += 15
    elif years_employed >= 5:
        score += 10
    elif years_employed >= 2:
        score += 5

    score -= previous_defaults * 20

    return max(0, min(100, score))

def determine_employment_risk(employment_type: str, years_employed: int) -> str:
    """Determine employment risk level"""
    if employment_type == "salaried" and years_employed >= 2:
        return "low"
    elif employment_type == "self_employed" or employment_type == "business_owner":
        return "medium" if years_employed >= 3 else "high"
    else:
        return "high"

@server.call_tool()
async def handle_get_applicant_profile(applicant_id: str) -> TextContent:
    """Get comprehensive applicant profile"""
    if applicant_id not in applicants_db:
        return TextContent(
            type="text",
            text=json.dumps({"error": f"Applicant {applicant_id} not found"})
        )

    applicant = applicants_db[applicant_id]
    income_stability = calculate_income_stability(
        applicant["years_employed"],
        applicant["employment_type"],
        applicant["previous_defaults"]
    )
    employment_risk = determine_employment_risk(
        applicant["employment_type"],
        applicant["years_employed"]
    )

    profile = {
        "applicant_id": applicant_id,
        "age": applicant["age"],
        "income": applicant["income"],
        "employment_type": applicant["employment_type"],
        "years_employed": applicant["years_employed"],
        "income_stability_score": income_stability,
        "employment_risk": employment_risk,
        "credit_history_summary": f"Applicant has {applicant['previous_defaults']} previous defaults and {applicant['accounts_opened']} active accounts",
        "application_completeness": 95.0
    }

    return TextContent(type="text", text=json.dumps(profile))

server.add_tool(
    Tool(
        name="get_applicant_profile",
        description="Retrieve comprehensive applicant profile including income stability, employment risk, and credit history",
        inputSchema={
            "type": "object",
            "properties": {
                "applicant_id": {
                    "type": "string",
                    "description": "Unique applicant identifier"
                }
            },
            "required": ["applicant_id"]
        }
    )
)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
