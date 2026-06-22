import logging
import time
from typing import Any, Dict
from datetime import datetime
from agents import (
    run_applicant_agent,
    run_risk_agent,
    run_decision_agent,
    run_compliance_agent,
    check_hard_reject_criteria
)
from database import save_application, update_application

logger = logging.getLogger(__name__)

class LoanOrchestrator:
    """LangGraph-based orchestration engine for loan processing"""

    def __init__(self):
        self.state = {}

    def process_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration workflow"""
        start_time = time.time()
        try:
            case_id = save_application(application_data)
            logger.info(f"Processing application: {case_id}")

            initial_state = {
                "case_id": case_id,
                "application_data": application_data,
                "status": "processing",
                "start_time": start_time
            }

            step_1_result = self._step_1_applicant_profile(initial_state)
            logger.info(f"Step 1 completed: {case_id}")

            step_2_result = self._step_2_financial_risk(step_1_result)
            logger.info(f"Step 2 completed: {case_id}")

            hard_reject_triggered, hard_reject_reason = check_hard_reject_criteria(
                application_data, step_2_result.get("financial_risk")
            )
            step_2_result["hard_reject_triggered"] = hard_reject_triggered
            step_2_result["hard_reject_reason"] = hard_reject_reason

            if hard_reject_triggered:
                logger.warning(f"Hard reject triggered for {case_id}: {hard_reject_reason}")

            step_3_result = self._step_3_decision(step_2_result)
            logger.info(f"Step 3 completed: {case_id}")

            step_4_result = self._step_4_compliance(step_3_result)
            logger.info(f"Step 4 completed: {case_id}")

            processing_time = time.time() - start_time

            final_result = {
                **step_4_result,
                "status": "completed",
                "processing_time_seconds": processing_time
            }

            update_application(case_id, {
                "status": "completed",
                "decision": step_3_result["decision"]["decision"],
                "risk_score": step_3_result["decision"]["risk_score"],
                "confidence_level": step_3_result["decision"]["confidence_level"],
                "explanation": step_3_result["decision"]["explanation"],
                "audit_log_id": step_3_result["decision"].get("audit_log_id"),
                "processing_time_seconds": processing_time,
                "requires_human_override": step_3_result["decision"].get("requires_human_override", False),
                "composite_risk_breakdown": step_3_result["decision"].get("composite_risk_breakdown", {}),
                "agent_reasoning": step_3_result["decision"].get("agent_reasoning"),
                "timestamp": datetime.utcnow().isoformat()
            })

            return final_result

        except Exception as e:
            logger.error(f"Error processing application: {str(e)}")
            raise

    def _step_1_applicant_profile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Applicant Profile Analysis"""
        application_data = state["application_data"]

        result = run_applicant_agent(application_data)

        state.update({
            "applicant_profile": result["applicant_profile"],
            "step_1_complete": True
        })

        return state

    def _step_2_financial_risk(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Financial Risk Analysis"""
        application_data = state["application_data"]

        result = run_risk_agent(application_data)

        state.update({
            "financial_risk": result["financial_risk"],
            "step_2_complete": True
        })

        return state

    def _step_3_decision(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Loan Decision"""
        applicant_profile = state["applicant_profile"]
        financial_risk = state["financial_risk"]
        application_data = state["application_data"]
        hard_reject_triggered = state.get("hard_reject_triggered", False)
        hard_reject_reason = state.get("hard_reject_reason", "")

        result = run_decision_agent(
            applicant_profile,
            financial_risk,
            application_data["credit_score"],
            application_data["age"],
            hard_reject=hard_reject_triggered,
            hard_reject_reason=hard_reject_reason
        )

        if hard_reject_triggered:
            result["requires_human_override"] = False
        else:
            result["requires_human_override"] = result.get("decision") == "manual_review"

        state.update({
            "decision": result,
            "step_3_complete": True
        })

        return state

    def _step_4_compliance(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Compliance & Notification"""
        case_id = state["case_id"]
        application_data = state["application_data"]
        decision = state["decision"]

        result = run_compliance_agent(case_id, application_data, decision)

        state.update({
            "compliance": result,
            "step_4_complete": True
        })

        return state

    def get_application_status(self, case_id: str) -> Dict[str, Any]:
        """Retrieve application status"""
        from database import get_application

        app = get_application(case_id)
        if not app:
            raise ValueError(f"Application {case_id} not found")

        return {
            "case_id": case_id,
            "status": app.get("status"),
            "decision": app.get("decision"),
            "risk_score": app.get("risk_score"),
            "confidence_level": app.get("confidence_level"),
            "explanation": app.get("explanation"),
            "applicant_id": app.get("applicant_id"),
            "loan_amount": app.get("loan_amount"),
            "created_at": app.get("created_at"),
            "updated_at": app.get("updated_at")
        }
