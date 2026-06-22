"""
Local MCP Simulation - Simulates MCP server responses for local development
This allows testing without running actual MCP servers
"""

import json
from typing import Dict, Any

class MCPSimulator:
    """Simulates MCP server responses"""

    @staticmethod
    def applicant_db(applicant_id: str, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate ApplicantDB MCP server"""
        employment_risk_map = {
            "salaried": "low",
            "self_employed": "medium",
            "business_owner": "medium",
            "student": "high",
            "retired": "high",
            "unemployed": "very_high"
        }

        employment_type = applicant_data.get("employment_type", "salaried")
        income_stability = MCPSimulator._calculate_income_stability(
            employment_type,
            applicant_data.get("age", 35)
        )

        return {
            "applicant_id": applicant_id,
            "age": applicant_data.get("age"),
            "income": applicant_data.get("income"),
            "employment_type": employment_type,
            "income_stability_score": income_stability,
            "employment_risk": employment_risk_map.get(employment_type, "medium"),
            "credit_history_summary": f"Applicant has stable credit history with income of ${applicant_data.get('income', 0):,}",
            "application_completeness": 95.0
        }

    @staticmethod
    def risk_rules_db(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate RiskRulesDB MCP server"""
        income = applicant_data.get("income", 50000)
        credit_score = applicant_data.get("credit_score", 650)
        loan_amount = applicant_data.get("loan_amount", 100000)
        loan_tenure = applicant_data.get("loan_tenure_months", 60)
        existing_liabilities = applicant_data.get("existing_liabilities", 0)

        emi = MCPSimulator._calculate_emi(loan_amount, 8.5, loan_tenure)
        dti_ratio = ((existing_liabilities + emi) / income * 100) if income > 0 else 100

        credit_risk_level = MCPSimulator._assess_credit_risk(credit_score)
        loan_risk = MCPSimulator._assess_loan_risk(loan_amount, income, credit_score)

        return {
            "debt_to_income_ratio": round(dti_ratio, 2),
            "dti_risk_flag": dti_ratio > 45,
            "credit_score_risk_level": credit_risk_level,
            "credit_risk_flag": credit_risk_level in ["high", "very_high"],
            "loan_amount_risk": loan_risk,
            "loan_emi": round(emi, 2),
            "anomaly_detected": False,
            "anomaly_description": "No anomalies detected",
            "reasoning": f"DTI {dti_ratio:.1f}%, Credit: {credit_risk_level}, Loan Risk: {loan_risk}"
        }

    @staticmethod
    def decision_synthesis(profile: Dict[str, Any], risk: Dict[str, Any], credit_score: int, age: int) -> Dict[str, Any]:
        """Simulate DecisionSynthesis MCP server"""
        risk_score = MCPSimulator._calculate_risk_score(profile, risk, credit_score, age)

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

        factors = MCPSimulator._get_decision_factors(profile, risk, risk_score)

        return {
            "decision": decision,
            "risk_score": round(risk_score, 2),
            "confidence_level": confidence,
            "key_decision_factors": factors,
            "explanation": f"Decision: {decision.upper()}. Risk Score: {risk_score:.1f}/100. "
                          f"Application analyzed based on income stability, employment history, "
                          f"credit profile, and debt-to-income ratio."
        }

    @staticmethod
    def notification_system(case_id: str, applicant_id: str, decision: str) -> Dict[str, Any]:
        """Simulate NotificationSystem MCP server"""
        from datetime import datetime

        messages = {
            "approved": f"Congratulations! Your loan application (Case ID: {case_id}) has been APPROVED.",
            "rejected": f"We regret to inform you that your loan application (Case ID: {case_id}) has been REJECTED.",
            "manual_review": f"Your loan application (Case ID: {case_id}) requires manual review. We'll contact you shortly."
        }

        return {
            "action_taken": "Notification sent via email",
            "notification_sent": True,
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "summary": messages.get(decision, "Decision notification sent"),
            "logged": True
        }

    @staticmethod
    def _calculate_income_stability(employment_type: str, age: int) -> float:
        """Calculate income stability score"""
        score = 50.0

        employment_scores = {
            "salaried": 30,
            "self_employed": 15,
            "business_owner": 10,
            "student": 0,
            "retired": 5,
            "unemployed": -50
        }

        score += employment_scores.get(employment_type, 10)

        if 30 <= age <= 55:
            score += 15
        elif 25 <= age < 30 or 55 < age <= 65:
            score += 5

        return max(0, min(100, score))

    @staticmethod
    def _calculate_emi(principal: float, annual_rate: float, months: int) -> float:
        """Calculate EMI"""
        if months == 0 or principal == 0:
            return 0
        monthly_rate = annual_rate / 12 / 100
        if monthly_rate == 0:
            return principal / months
        emi = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        return emi

    @staticmethod
    def _assess_credit_risk(credit_score: int) -> str:
        """Assess credit risk"""
        if credit_score >= 750:
            return "low"
        elif credit_score >= 650:
            return "medium"
        elif credit_score >= 550:
            return "high"
        else:
            return "very_high"

    @staticmethod
    def _assess_loan_risk(loan_amount: float, income: float, credit_score: int) -> str:
        """Assess loan amount risk"""
        loan_to_income = loan_amount / income if income > 0 else 100

        if credit_score >= 700 and loan_to_income <= 3:
            return "low"
        elif credit_score >= 650 and loan_to_income <= 4:
            return "medium"
        elif credit_score >= 600 and loan_to_income <= 5:
            return "high"
        else:
            return "very_high"

    @staticmethod
    def _calculate_risk_score(profile: Dict[str, Any], risk: Dict[str, Any], credit_score: int, age: int) -> float:
        """Calculate final risk score"""
        score = 50.0

        income_stability = profile.get("income_stability_score", 50)
        employment_risk = profile.get("employment_risk", "medium")
        dti_ratio = risk.get("debt_to_income_ratio", 40)
        credit_risk = risk.get("credit_score_risk_level", "medium")
        loan_risk = risk.get("loan_amount_risk", "medium")

        employment_scores = {"low": -10, "medium": 5, "high": 20, "very_high": 40}
        score += employment_scores.get(employment_risk, 5)

        credit_scores = {"low": -5, "medium": 10, "high": 25, "very_high": 50}
        score += credit_scores.get(credit_risk, 10)

        if dti_ratio > 45:
            score += 20
        elif dti_ratio > 35:
            score += 10

        loan_scores = {"low": -5, "medium": 5, "high": 15, "very_high": 35}
        score += loan_scores.get(loan_risk, 5)

        if income_stability > 75:
            score -= 10
        elif income_stability < 50:
            score += 15

        if age < 25 or age > 60:
            score += 5

        return max(0, min(100, score))

    @staticmethod
    def _get_decision_factors(profile: Dict[str, Any], risk: Dict[str, Any], risk_score: float) -> list:
        """Get key decision factors"""
        factors = []

        income_stability = profile.get("income_stability_score", 50)
        if income_stability > 75:
            factors.append("Strong income stability")
        elif income_stability < 50:
            factors.append("Low income stability")

        employment_risk = profile.get("employment_risk", "medium")
        if employment_risk == "low":
            factors.append("Stable employment")
        elif employment_risk == "high":
            factors.append("Employment risk concern")

        dti_ratio = risk.get("debt_to_income_ratio", 40)
        if dti_ratio > 45:
            factors.append("High debt-to-income ratio")
        else:
            factors.append("Acceptable debt levels")

        credit_risk = risk.get("credit_score_risk_level", "medium")
        if credit_risk == "low":
            factors.append("Strong credit profile")
        elif credit_risk == "high":
            factors.append("Credit score concern")

        loan_risk = risk.get("loan_amount_risk", "medium")
        if loan_risk in ["high", "very_high"]:
            factors.append("High loan amount relative to income")

        if not factors:
            factors.append("Application meets standard lending criteria")

        return factors
