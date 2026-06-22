import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    ApplicationStatus,
    DecisionStatus
)
from orchestration import LoanOrchestrator
from database import init_database, get_application
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Loan Assist - Agentic AI System",
    description="Multi-Agent AI Loan Approval System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = LoanOrchestrator()
init_database()

@app.on_event("startup")
async def startup_event():
    logger.info("Loan Assist API starting up")
    init_database()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Loan Assist API",
        "version": "1.0.0"
    }

@app.post("/loan-application", response_model=LoanApplicationResponse)
async def submit_loan_application(request: LoanApplicationRequest):
    """Submit a new loan application"""
    try:
        application_data = request.dict()

        logger.info(f"Received loan application from {request.applicant_id}")

        result = orchestrator.process_application(application_data)

        response = LoanApplicationResponse(
            case_id=result["case_id"],
            status="completed",
            decision=DecisionStatus(result["decision"]["decision"]),
            risk_score=result["decision"]["risk_score"],
            confidence_level=result["decision"]["confidence_level"],
            explanation=result["decision"]["explanation"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        logger.info(f"Application {result['case_id']} processed: {result['decision']['decision']}")

        return response

    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/application-status/{case_id}", response_model=ApplicationStatus)
async def get_application_status(case_id: str):
    """Get status of a loan application"""
    try:
        app_data = get_application(case_id)

        if not app_data:
            raise HTTPException(status_code=404, detail=f"Application {case_id} not found")

        return ApplicationStatus(
            case_id=case_id,
            status=app_data.get("status", "processing"),
            decision=app_data.get("decision"),
            applicant_id=app_data.get("applicant_id"),
            loan_amount=app_data.get("loan_amount"),
            created_at=datetime.fromisoformat(app_data.get("created_at")),
            updated_at=datetime.fromisoformat(app_data.get("updated_at"))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching application status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/applications")
async def list_applications():
    """List all applications"""
    try:
        from database import get_all_applications

        apps = get_all_applications()

        return {
            "total": len(apps),
            "applications": [
                {
                    "case_id": app.get("case_id"),
                    "applicant_id": app.get("applicant_id"),
                    "loan_amount": app.get("loan_amount"),
                    "status": app.get("status"),
                    "decision": app.get("decision"),
                    "created_at": app.get("created_at")
                }
                for app in apps
            ]
        }

    except Exception as e:
        logger.error(f"Error listing applications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api-info")
async def api_info():
    """Get API information"""
    return {
        "service": "Loan Assist - Agentic AI System",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "submit_application": "POST /loan-application",
            "get_status": "GET /application-status/{case_id}",
            "list_applications": "GET /applications",
            "api_docs": "/docs",
            "openapi_schema": "/openapi.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
