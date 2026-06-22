# Decision Logic Implementation - Loan Approval System

## Overview

This document describes the implementation of the enhanced decision logic for the loan approval system, based on the requirements in `Decisionlogic.txt`. The implementation introduces score-based tiering, a hard reject fast path, explainability, and comprehensive auditability.

---

## Key Features Implemented

### 1. Score-Based Tiering

The loan approval decision is now based on a composite risk score with clear thresholds:

| Risk Score | Decision | Confidence | Outcome |
|-----------|----------|-----------|---------|
| ≤ 40 | APPROVED | High (0.95/0.85) | Immediate approval |
| 40-65 | MANUAL_REVIEW | Medium (0.70-0.95) | Requires human officer review |
| > 65 | REJECTED | High (0.85) | Automatic rejection |
| Hard Reject | REJECTED | 0.98 | Policy violation rejection |

**Example Score Calculation:**
```
Base Score = 0
+ Employment Risk (low/medium/high): 10/25/50
+ Credit Risk (low/medium/high/very_high): 5/20/40/60
+ DTI Ratio (≤30/≤45/>45): 5/15/35
+ Loan Amount Risk (low/medium/high/very_high): 5/15/30/50
+ Income Stability (≥75/-10, <50/+20)
+ Anomalies Detected: +30
+ Age (outside 25-60): +10
= Final Risk Score (clamped 0-100)
```

### 2. Hard Reject Fast Path

Certain applications are immediately rejected without running the normal decision agent:

**Hard Reject Criteria:**
- **Unemployed applicants** - Policy violation (immediate rejection)
- **Critical financial risk**:
  - DTI ratio > 50%
  - Very high credit risk + DTI > 40%

**Hard Reject Characteristics:**
- Risk Score: 95.0 (fixed)
- Confidence: 0.98 (fixed)
- Decision: REJECTED
- Agent Reasoning: "Hard reject fast path — Decision Agent bypassed per conditional routing"
- Specific policy reason in explanation

**Implementation Location:** [agents.py:9-28]
```python
def check_hard_reject_criteria(application_data: dict, financial_risk: dict = None) -> tuple[bool, str]:
    # Returns (should_hard_reject, reason)
```

### 3. Enhanced Auditability

#### Case ID Format
**New Format:** `CASE-YYYYMMDD-XXXXXXXX`
- Date component ensures chronological ordering
- Sequence number ensures uniqueness
- Example: `CASE-20260622-00000001`

**Implementation:** [database.py:18-25]

#### Audit Log ID
**Format:** `AUDIT-XXXXXXXXXXXX`
- Random hex component + sequential counter
- Unique identifier for each decision audit entry
- Example: `AUDIT-a7f2c1e900000001`

**Implementation:** [database.py:27-37]

#### Decision Metadata Tracked
- `processing_time_seconds`: End-to-end processing duration
- `timestamp`: UTC timestamp of decision
- `is_ai_decision`: Flag indicating AI-made decision
- `requires_human_override`: Flag for manual_review outcomes
- `agent_reasoning`: Notes if decision agent was bypassed
- `composite_risk_breakdown`: Component-level scores

**Implementation:** [orchestration.py:22-60]

### 4. Explainability

#### Plain-English Explanation
Every decision includes a detailed explanation covering:
1. Decision type (APPROVED/REJECTED/MANUAL REVIEW)
2. Risk score with component breakdown
3. Top risk factors with specific values
4. Contextual guidance (e.g., threshold warnings)

**Example:**
```
Decision: APPROVED. Risk Score: 35.50/100 (Composite: Employment: 10.00, 
Credit Risk: 5.00, DTI Ratio: 5.00, Loan Amount: 5.00, Income Stability: 
-10.00). Key Factors: Strong income stability: 85/100. Consider possible 
loan amount adjustment for borderline cases.
```

#### Component Breakdown
The `composite_risk_breakdown` dict provides visibility into each scoring component:
```json
{
  "employment": 25,
  "credit_risk": 40,
  "dti_ratio": 15,
  "loan_amount": 15,
  "income_stability": -10,
  "anomalies": 0,
  "age": 0
}
```

#### Key Decision Factors
Specific, human-readable factors driving the decision:
```
[
  "Employment Risk: medium",
  "Credit Risk: high (Score: 680)",
  "DTI Ratio: 45.5%",
  "Strong income stability: 82/100"
]
```

**Implementation:** [mcp_decision_synthesis.py:38-51, 101-113]

### 5. Manual Review as First-Class Outcome

Manual Review is now a distinct decision path:
- **When**: Risk score between 40-65 (borderline cases)
- **Flag**: `requires_human_override = true`
- **Process**: Application held for human loan officer review
- **Guidance**: Explanation includes context for officer decision

**Implementation:** [orchestration.py:109-111, mcp_decision_synthesis.py:122-124]

---

## Architecture Changes

### Modified Files

#### 1. **models.py** - Data Structures
- Enhanced `LoanDecision` model with audit fields
- Updated `LoanApplicationResponse` to expose new fields
- Enhanced `ApplicationStatus` for full audit trail retrieval

**New Fields in LoanDecision:**
```python
audit_log_id: str
processing_time_seconds: float
requires_human_override: bool
is_ai_decision: bool
composite_risk_breakdown: dict
agent_reasoning: Optional[str]
recommended_loan_amount: Optional[float]
timestamp: datetime
```

#### 2. **database.py** - Case ID & Audit Log Generation
- Updated `get_case_id()` to generate `CASE-YYYYMMDD-XXXXXXXX` format
- New `get_audit_log_id()` function for `AUDIT-XXXXXXXXXXXX` format
- Updated `save_application()` to generate audit_log_id

#### 3. **agents.py** - Hard Reject Detection
- New `check_hard_reject_criteria()` function
- Updated `run_decision_agent()` to accept hard_reject parameters
- Enhanced prompt for decision agent explaining new thresholds

#### 4. **mcp_decision_synthesis.py** - Decision Logic
- Implemented score-based tiering with three decision paths
- Enhanced `synthesize_decision()` with hard_reject path
- New `build_decision_explanation()` for plain-English explanations
- Composite risk breakdown generation
- Confidence scoring based on proximity to thresholds

#### 5. **orchestration.py** - Workflow
- Added processing time tracking (start to finish)
- Hard reject criteria check after financial risk analysis
- Decision agent bypass logic for hard rejects
- Audit metadata propagation to database

#### 6. **main.py** - API Endpoints
- Updated `/loan-application` to expose new decision fields
- Enhanced `/application-status/{case_id}` to return full audit trail
- Both endpoints now include:
  - audit_log_id
  - processing_time_seconds
  - requires_human_override
  - composite_risk_breakdown
  - agent_reasoning

---

## Data Flow

```
┌─────────────────────────────┐
│   Loan Application Received │
│   (employment_type, etc.)   │
└──────────────┬──────────────┘
               │
        ┌──────▼──────┐
        │ Step 1: Get │
        │   Profile   │
        └──────┬──────┘
               │
        ┌──────▼────────────┐
        │ Step 2: Financial │
        │      Risk         │
        └──────┬────────────┘
               │
        ┌──────▼──────────────────────┐
        │ Check Hard Reject Criteria  │
        │ (unemployed, critical risk) │
        └──────┬──────────┬───────────┘
               │          │
         ┌─────▼─┐   ┌────▼──────────┐
         │ Hard  │   │ Normal Scoring│
         │Reject?│   │ Path          │
         └─────┬─┘   └────┬──────────┘
               │          │
         ┌─────▼──────────▼─────────┐
         │ Step 3: Synthesize       │
         │ Decision                 │
         │ - risk_score = 95.0      │ (Hard Reject)
         │ - confidence = 0.98      │
         │ OR                       │
         │ - score-based tiering    │ (Normal Path)
         └─────┬──────────────────┬─┘
               │                  │
         ┌─────▼───┐      ┌──────▼──────┐
         │ APPROVED │      │ MANUAL_     │  or  REJECTED
         │          │      │ REVIEW      │
         └─────┬────┘      └──────┬──────┘
               │                  │
         ┌─────▼──────────────────▼─────────┐
         │ Step 4: Compliance & Notification│
         │ - Send notification              │
         │ - Log audit trail                │
         └─────┬──────────────────────────┬─┘
               │                          │
         ┌─────▼──────┐          ┌────────▼────────┐
         │ Response   │          │ Store in DB     │
         │ to Client  │          │ with full audit │
         └────────────┘          └─────────────────┘
```

---

## API Response Examples

### Example 1: Hard Reject (Unemployed)
```json
{
  "case_id": "CASE-20260622-00000001",
  "audit_log_id": "AUDIT-a7f2c1e900000001",
  "decision": "rejected",
  "risk_score": 95.0,
  "confidence_level": 0.98,
  "requires_human_override": false,
  "processing_time_seconds": 1.234,
  "composite_risk_breakdown": {
    "policy_violation": 95.0
  },
  "key_decision_factors": [
    "Policy violation: Unemployed applicants are not eligible for loans"
  ],
  "agent_reasoning": "Hard reject fast path — Decision Agent bypassed per conditional routing",
  "explanation": "HARD REJECT: Policy violation: Unemployed applicants are not eligible for loans. Risk Score: 95.0/100. Decision made immediately per policy violation criteria."
}
```

### Example 2: Manual Review (Borderline)
```json
{
  "case_id": "CASE-20260622-00000002",
  "audit_log_id": "AUDIT-b8g3d2f900000002",
  "decision": "manual_review",
  "risk_score": 52.5,
  "confidence_level": 0.82,
  "requires_human_override": true,
  "processing_time_seconds": 2.567,
  "composite_risk_breakdown": {
    "employment": 25,
    "credit_risk": 20,
    "dti_ratio": 15,
    "loan_amount": 15,
    "income_stability": 0,
    "anomalies": 0,
    "age": 0
  },
  "key_decision_factors": [
    "Employment Risk: medium",
    "Credit Risk: medium (Score: 680)",
    "DTI Ratio: 45.5%"
  ],
  "agent_reasoning": null,
  "explanation": "Decision: MANUAL REVIEW. Risk Score: 52.50/100 (Composite: Employment: 25.00, Credit Risk: 20.00, DTI Ratio: 15.00, Loan Amount: 15.00). Key Factors: Employment Risk: medium; Credit Risk: medium (Score: 680); DTI Ratio: 45.5%. This application is close to approval threshold and requires human officer review."
}
```

### Example 3: Approved (Low Risk)
```json
{
  "case_id": "CASE-20260622-00000003",
  "audit_log_id": "AUDIT-c9h4e3g900000003",
  "decision": "approved",
  "risk_score": 25.0,
  "confidence_level": 0.95,
  "requires_human_override": false,
  "processing_time_seconds": 1.890,
  "composite_risk_breakdown": {
    "employment": 10,
    "credit_risk": 5,
    "dti_ratio": 5,
    "loan_amount": 5,
    "income_stability": -10,
    "anomalies": 0,
    "age": 0
  },
  "key_decision_factors": [
    "Strong income stability: 85/100"
  ],
  "agent_reasoning": null,
  "explanation": "Decision: APPROVED. Risk Score: 25.00/100 (Composite: Employment: 10.00, Credit Risk: 5.00, DTI Ratio: 5.00, Loan Amount: 5.00, Income Stability: -10.00). Key Factors: Application meets standard lending criteria. Consider possible loan amount adjustment for borderline cases."
}
```

---

## Testing

### Test Suite
Run comprehensive tests with: `python test_decision_logic.py`

**Test Cases:**
1. ✅ Hard Reject - Unemployed Applicant
2. ✅ Score-Based Decision - Low Risk (Approved)
3. ✅ Score-Based Decision - Borderline (Manual Review)
4. ✅ Score-Based Decision - High Risk (Rejected)
5. ✅ Explainability - Component Breakdown
6. ✅ Auditability - Audit Trail Format
7. ✅ Status Endpoint - Full Audit Trail

### Manual Testing
1. Start API: `python -m uvicorn main:app --reload`
2. Run tests: `python test_decision_logic.py`
3. Check logs for decision reasoning and processing times

---

## Implementation Details

### Threshold Calculation
The boundaries between decision paths (40, 65) were chosen to:
- 40: High confidence approval threshold - low total risk
- 65: Clear rejection threshold - unacceptable risk
- 40-65: Manual review zone - requires human judgment

### Confidence Scoring
Confidence levels are calculated based on:
- Distance from decision boundary
- Anomaly count (increases uncertainty)
- Consistency of risk factors

**Formula for Manual Review Zone:**
```
confidence = min(0.95, 0.70 + (proximity_to_boundary / 25) * 0.15)
```

### Processing Time
Tracked end-to-end from application submission through all 4 orchestration steps:
1. Applicant profile analysis
2. Financial risk analysis
3. Decision synthesis
4. Compliance & notification

---

## Compliance & Governance

### Audit Trail Fields
Every decision includes:
- ✅ Case ID with date component
- ✅ Audit Log ID for unique identification
- ✅ Processing timestamp (UTC)
- ✅ Processing time duration
- ✅ AI decision flag
- ✅ Manual override requirement flag
- ✅ Agent bypass reasoning (if applicable)
- ✅ Component scores for transparency
- ✅ Key factors for officer reference

### Policy Violations
Hard rejects are traced with specific policy reasons:
- "Unemployed applicants are not eligible"
- "DTI ratio exceeds maximum threshold"
- "Critical risk: Very high credit risk + elevated DTI"

---

## Future Enhancements

1. **Recommended Loan Amount** - For borderline cases near approval threshold
2. **Risk Factor Weighting** - Configurable component weights by region/product
3. **Decision Explanation API** - Detailed breakdown of scoring for officer review
4. **Batch Processing** - Process multiple applications with audit trail
5. **Appeal Process** - Systematic handling of rejected applications

---

## Summary

The enhanced decision logic transforms the loan approval system from binary (approve/reject) to a nuanced three-tier system with:
- **Immediate rejections** for policy violations
- **Approved** for low-risk applications
- **Manual review** as an explicit path for borderline cases
- **Full transparency** through component breakdowns
- **Complete auditability** for compliance and governance

All changes maintain backward compatibility with existing APIs while exposing new decision metadata for transparency and audit purposes.
