import json
from datetime import datetime
from mcp.server import Server
from mcp.types import TextContent, Tool

server = Server("NotificationSystem")

notifications_log = []

@server.call_tool()
async def handle_send_notification(
    case_id: str,
    applicant_id: str,
    decision: str,
    notification_type: str = "email"
) -> TextContent:
    """Send notification to applicant"""

    notification = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "decision": decision,
        "notification_type": notification_type,
        "timestamp": datetime.now().isoformat(),
        "status": "sent"
    }

    notifications_log.append(notification)

    action_messages = {
        "approved": f"Congratulations! Your loan application (Case ID: {case_id}) has been APPROVED.",
        "rejected": f"We regret to inform you that your loan application (Case ID: {case_id}) has been REJECTED.",
        "manual_review": f"Your loan application (Case ID: {case_id}) requires manual review. We'll contact you shortly."
    }

    result = {
        "action_taken": f"Notification sent via {notification_type}",
        "notification_sent": True,
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "summary": action_messages.get(decision, "Loan decision notification sent."),
        "message_details": {
            "to": f"{applicant_id}@bank.com",
            "subject": f"Loan Application Decision - {case_id}",
            "type": notification_type
        }
    }

    return TextContent(type="text", text=json.dumps(result))

@server.call_tool()
async def handle_log_decision(
    case_id: str,
    applicant_id: str,
    decision: str,
    risk_score: float,
    confidence_level: float
) -> TextContent:
    """Log decision in compliance system"""

    log_entry = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "decision": decision,
        "risk_score": risk_score,
        "confidence_level": confidence_level,
        "timestamp": datetime.now().isoformat(),
        "logged": True
    }

    result = {
        "action_taken": "Decision logged in compliance system",
        "logged": True,
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "summary": f"Loan decision ({decision.upper()}) logged with risk score {risk_score:.2f} and confidence {confidence_level:.2%}",
        "audit_trail": log_entry
    }

    return TextContent(type="text", text=json.dumps(result))

server.add_tool(
    Tool(
        name="send_notification",
        description="Send notification to applicant about loan decision",
        inputSchema={
            "type": "object",
            "properties": {
                "case_id": {"type": "string"},
                "applicant_id": {"type": "string"},
                "decision": {"type": "string", "enum": ["approved", "rejected", "manual_review"]},
                "notification_type": {"type": "string", "default": "email"}
            },
            "required": ["case_id", "applicant_id", "decision"]
        }
    )
)

server.add_tool(
    Tool(
        name="log_decision",
        description="Log decision in compliance and audit system",
        inputSchema={
            "type": "object",
            "properties": {
                "case_id": {"type": "string"},
                "applicant_id": {"type": "string"},
                "decision": {"type": "string"},
                "risk_score": {"type": "number"},
                "confidence_level": {"type": "number"}
            },
            "required": ["case_id", "applicant_id", "decision", "risk_score", "confidence_level"]
        }
    )
)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
