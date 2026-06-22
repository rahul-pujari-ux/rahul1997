from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    BUSINESS_OWNER = "business_owner"
    STUDENT = "student"
    RETIRED = "retired"
    UNEMPLOYED = "unemployed"

class LoanPurpose(str, Enum):
    HOME = "home"
    AUTO = "auto"
    PERSONAL = "personal"
    BUSINESS = "business"
    EDUCATION = "education"

class DecisionStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"

class LoanApplicationRequest(BaseModel):
    applicant_id: str
    age: int = Field(ge=18, le=70)
    income: float = Field(gt=0)
    employment_type: EmploymentType
    credit_score: int = Field(ge=300, le=850)
    loan_amount: float = Field(gt=0)
    loan_tenure_months: int = Field(ge=6, le=360)
    existing_liabilities: float = Field(ge=0)
    location: str
    purpose: LoanPurpose
    marital_status: str = "single"
    dependents: int = Field(ge=0, le=10)

class ApplicantProfile(BaseModel):
    applicant_id: str
    age: int
    income: float
    employment_type: str
    income_stability_score: float
    employment_risk: str
    credit_history_summary: str
    application_completeness: float

class FinancialRiskAnalysis(BaseModel):
    debt_to_income_ratio: float
    credit_score_risk_level: str
    loan_amount_risk: str
    dti_risk_flag: bool
    credit_risk_flag: bool
    anomaly_detected: bool
    anomaly_description: Optional[str] = None
    reasoning: str

class LoanDecision(BaseModel):
    case_id: str
    decision: DecisionStatus
    risk_score: float
    confidence_level: float
    key_decision_factors: List[str]
    explanation: str

class ComplianceAction(BaseModel):
    action_taken: str
    notification_sent: bool
    case_id: str
    timestamp: datetime
    summary: str

class LoanApplicationResponse(BaseModel):
    case_id: str
    status: str
    decision: Optional[DecisionStatus]
    risk_score: Optional[float]
    confidence_level: Optional[float]
    explanation: Optional[str]
    created_at: datetime
    updated_at: datetime

class ApplicationStatus(BaseModel):
    case_id: str
    status: str
    decision: Optional[str]
    applicant_id: str
    loan_amount: float
    created_at: datetime
    updated_at: datetime
