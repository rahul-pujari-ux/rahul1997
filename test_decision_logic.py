#!/usr/bin/env python3
"""
Test script for new decision logic implementation
Tests: hard reject path, score-based tiering, explainability, auditability
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def print_detail(label: str, value: Any):
    print(f"  {Colors.CYAN}{label}:{Colors.END} {value}")

def validate_decision_response(response_data: Dict[str, Any], expected_decision: str = None) -> bool:
    """Validate response contains all required new fields"""
    required_fields = [
        "case_id", "decision", "risk_score", "confidence_level",
        "explanation", "audit_log_id", "processing_time_seconds",
        "requires_human_override", "composite_risk_breakdown",
        "key_decision_factors"
    ]

    missing_fields = []
    for field in required_fields:
        if field not in response_data:
            missing_fields.append(field)

    if missing_fields:
        print_error(f"Missing fields: {', '.join(missing_fields)}")
        return False

    # Validate case_id format: CASE-YYYYMMDD-XXXXXXXX
    case_id = response_data.get("case_id", "")
    if not case_id.startswith("CASE-") or len(case_id.split("-")) != 3:
        print_error(f"Invalid case_id format: {case_id}")
        return False

    # Validate audit_log_id format: AUDIT-XXXXXXXXXXXX
    audit_id = response_data.get("audit_log_id", "")
    if not audit_id.startswith("AUDIT-"):
        print_error(f"Invalid audit_log_id format: {audit_id}")
        return False

    if expected_decision and response_data.get("decision") != expected_decision:
        print_error(f"Expected decision '{expected_decision}', got '{response_data.get('decision')}'")
        return False

    print_success("All required fields present with correct formats")
    return True

def print_decision_details(response_data: Dict[str, Any]):
    """Print detailed decision information"""
    print("\n  Decision Details:")
    print_detail("    Case ID", response_data.get("case_id"))
    print_detail("    Audit Log ID", response_data.get("audit_log_id"))
    print_detail("    Decision", response_data.get("decision").upper())
    print_detail("    Risk Score", f"{response_data.get('risk_score'):.2f}/100")
    print_detail("    Confidence", f"{response_data.get('confidence_level'):.2%}")
    print_detail("    Processing Time", f"{response_data.get('processing_time_seconds', 0):.3f}s")
    print_detail("    Requires Human Review", response_data.get("requires_human_override"))
    print_detail("    Agent Reasoning", response_data.get("agent_reasoning") or "Normal path")

    if response_data.get("composite_risk_breakdown"):
        print("\n  Composite Risk Breakdown:")
        for component, score in response_data.get("composite_risk_breakdown", {}).items():
            print_detail(f"    {component.replace('_', ' ').title()}", f"{score:.2f}")

    print("\n  Key Decision Factors:")
    for factor in response_data.get("key_decision_factors", []):
        print(f"    • {factor}")

    print(f"\n  Explanation:\n    {response_data.get('explanation')}")

def test_case_1_unemployed_hard_reject():
    """Test Case 1: Unemployed applicant should trigger hard reject"""
    print_header("Test Case 1: Hard Reject - Unemployed Applicant")

    test_data = {
        "applicant_id": "HARD-REJECT-UNEMPLOYED-001",
        "age": 35,
        "income": 0,
        "employment_type": "unemployed",
        "credit_score": 700,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "existing_liabilities": 10000,
        "location": "New York, NY",
        "purpose": "personal",
        "marital_status": "single",
        "dependents": 0
    }

    try:
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print_info("Expected: Hard reject (risk_score=95.0, confidence=0.98)")

            if result.get("decision") == "rejected":
                print_success(f"Correct decision: REJECTED")
                if result.get("risk_score") == 95.0 and result.get("confidence_level") == 0.98:
                    print_success("Correct hard reject scores (95.0/0.98)")
                else:
                    print_error(f"Incorrect scores: {result.get('risk_score')}/{result.get('confidence_level')}")

                if "Policy violation" in result.get("explanation", ""):
                    print_success("Hard reject reason in explanation")
                else:
                    print_error("Missing hard reject reason in explanation")

                if validate_decision_response(result, "rejected"):
                    print_decision_details(result)
                    return True
            else:
                print_error(f"Expected 'rejected', got '{result.get('decision')}'")
        else:
            print_error(f"API error: {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def test_case_2_low_risk_approved():
    """Test Case 2: Low risk applicant should get approved"""
    print_header("Test Case 2: Score-Based Decision - Low Risk (Approved)")

    test_data = {
        "applicant_id": "LOW-RISK-APPROVED-001",
        "age": 35,
        "income": 120000,
        "employment_type": "salaried",
        "credit_score": 780,
        "loan_amount": 150000,
        "loan_tenure_months": 60,
        "existing_liabilities": 20000,
        "location": "San Francisco, CA",
        "purpose": "home",
        "marital_status": "married",
        "dependents": 2
    }

    try:
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print_info("Expected: Approved (risk_score ≤ 40)")

            if result.get("decision") == "approved":
                print_success(f"Correct decision: APPROVED")
                risk_score = result.get("risk_score", 0)
                if risk_score <= 40:
                    print_success(f"Risk score within approved range: {risk_score:.2f}")
                else:
                    print_error(f"Risk score outside approved range: {risk_score:.2f}")

                if validate_decision_response(result, "approved"):
                    print_decision_details(result)
                    return True
            else:
                print_error(f"Expected 'approved', got '{result.get('decision')}'")
        else:
            print_error(f"API error: {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def test_case_3_borderline_manual_review():
    """Test Case 3: Borderline applicant should get manual review"""
    print_header("Test Case 3: Score-Based Decision - Borderline (Manual Review)")

    test_data = {
        "applicant_id": "BORDERLINE-MANUAL-REVIEW-001",
        "age": 42,
        "income": 65000,
        "employment_type": "self_employed",
        "credit_score": 680,
        "loan_amount": 200000,
        "loan_tenure_months": 84,
        "existing_liabilities": 50000,
        "location": "Austin, TX",
        "purpose": "auto",
        "marital_status": "single",
        "dependents": 1
    }

    try:
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print_info("Expected: Manual Review (40 < risk_score ≤ 65)")

            if result.get("decision") == "manual_review":
                print_success(f"Correct decision: MANUAL_REVIEW")
                risk_score = result.get("risk_score", 0)
                if 40 < risk_score <= 65:
                    print_success(f"Risk score in manual review range: {risk_score:.2f}")
                else:
                    print_error(f"Risk score outside manual review range: {risk_score:.2f}")

                if result.get("requires_human_override"):
                    print_success("Correctly flagged for human override")
                else:
                    print_error("Should be flagged for human override")

                if validate_decision_response(result, "manual_review"):
                    print_decision_details(result)
                    return True
            else:
                print_error(f"Expected 'manual_review', got '{result.get('decision')}'")
        else:
            print_error(f"API error: {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def test_case_4_high_risk_rejected():
    """Test Case 4: High risk applicant should get rejected"""
    print_header("Test Case 4: Score-Based Decision - High Risk (Rejected)")

    test_data = {
        "applicant_id": "HIGH-RISK-REJECTED-001",
        "age": 58,
        "income": 35000,
        "employment_type": "retired",
        "credit_score": 550,
        "loan_amount": 350000,
        "loan_tenure_months": 120,
        "existing_liabilities": 100000,
        "location": "Miami, FL",
        "purpose": "personal",
        "marital_status": "divorced",
        "dependents": 0
    }

    try:
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print_info("Expected: Rejected (risk_score > 65)")

            if result.get("decision") == "rejected":
                print_success(f"Correct decision: REJECTED")
                risk_score = result.get("risk_score", 0)
                if risk_score > 65:
                    print_success(f"Risk score in rejected range: {risk_score:.2f}")
                else:
                    print_error(f"Risk score outside rejected range: {risk_score:.2f}")

                if validate_decision_response(result, "rejected"):
                    print_decision_details(result)
                    return True
            else:
                print_error(f"Expected 'rejected', got '{result.get('decision')}'")
        else:
            print_error(f"API error: {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def test_explainability():
    """Test explainability: component breakdown in explanation"""
    print_header("Test Case 5: Explainability - Component Breakdown")

    test_data = {
        "applicant_id": "EXPLAINABILITY-TEST-001",
        "age": 40,
        "income": 90000,
        "employment_type": "salaried",
        "credit_score": 720,
        "loan_amount": 180000,
        "loan_tenure_months": 60,
        "existing_liabilities": 40000,
        "location": "Boston, MA",
        "purpose": "home",
        "marital_status": "married",
        "dependents": 1
    }

    try:
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code == 200:
            result = response.json()
            explanation = result.get("explanation", "")
            composite_breakdown = result.get("composite_risk_breakdown", {})

            print_info("Checking explanation quality and component breakdown")

            if composite_breakdown:
                print_success(f"Component breakdown present with {len(composite_breakdown)} components")
                for component, score in composite_breakdown.items():
                    print(f"  • {component}: {score:.2f}")
            else:
                print_error("Missing composite risk breakdown")
                return False

            if "Decision:" in explanation and "Risk Score:" in explanation:
                print_success("Explanation contains decision and risk score")
            else:
                print_error("Explanation missing key components")
                return False

            if result.get("key_decision_factors"):
                print_success(f"Key decision factors: {len(result.get('key_decision_factors'))} factors")
                return True
            else:
                print_error("Missing key decision factors")
                return False

    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def test_auditability():
    """Test auditability: case ID format, audit log ID, timestamps"""
    print_header("Test Case 6: Auditability - Audit Trail")

    test_data = {
        "applicant_id": "AUDIT-TRAIL-TEST-001",
        "age": 32,
        "income": 95000,
        "employment_type": "salaried",
        "credit_score": 740,
        "loan_amount": 160000,
        "loan_tenure_months": 60,
        "existing_liabilities": 25000,
        "location": "Seattle, WA",
        "purpose": "home",
        "marital_status": "single",
        "dependents": 0
    }

    try:
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code == 200:
            result = response.json()
            case_id = result.get("case_id", "")
            audit_log_id = result.get("audit_log_id", "")
            processing_time = result.get("processing_time_seconds", 0)

            print_info("Checking audit trail components")

            # Validate case ID format: CASE-YYYYMMDD-XXXXXXXX
            if case_id.startswith("CASE-"):
                parts = case_id.split("-")
                if len(parts) == 3 and len(parts[1]) == 8:  # YYYYMMDD
                    print_success(f"Valid case ID format: {case_id}")
                else:
                    print_error(f"Invalid case ID format: {case_id}")
                    return False
            else:
                print_error(f"Invalid case ID: {case_id}")
                return False

            # Validate audit log ID format: AUDIT-XXXXXXXXXXXX
            if audit_log_id.startswith("AUDIT-") and len(audit_log_id) > 6:
                print_success(f"Valid audit log ID format: {audit_log_id}")
            else:
                print_error(f"Invalid audit log ID: {audit_log_id}")
                return False

            # Validate processing time
            if processing_time > 0:
                print_success(f"Processing time tracked: {processing_time:.3f}s")
            else:
                print_error(f"Invalid processing time: {processing_time}")
                return False

            # Check timestamp
            if result.get("timestamp"):
                print_success(f"UTC timestamp recorded: {result.get('timestamp')}")
            else:
                print_info("Timestamp not in response (may be in status endpoint)")

            return True

    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def test_status_endpoint():
    """Test status endpoint returns all audit fields"""
    print_header("Test Case 7: Status Endpoint - Full Audit Trail")

    test_data = {
        "applicant_id": "STATUS-ENDPOINT-TEST-001",
        "age": 38,
        "income": 88000,
        "employment_type": "salaried",
        "credit_score": 710,
        "loan_amount": 140000,
        "loan_tenure_months": 60,
        "existing_liabilities": 30000,
        "location": "Denver, CO",
        "purpose": "auto",
        "marital_status": "married",
        "dependents": 2
    }

    try:
        # Submit application
        response = requests.post(f"{BASE_URL}/loan-application", json=test_data)
        if response.status_code != 200:
            print_error(f"Failed to submit application: {response.status_code}")
            return False

        result = response.json()
        case_id = result.get("case_id")

        time.sleep(0.5)

        # Get status
        status_response = requests.get(f"{BASE_URL}/application-status/{case_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()

            print_info(f"Retrieved status for {case_id}")

            required_fields = [
                "audit_log_id", "processing_time_seconds", "requires_human_override",
                "composite_risk_breakdown", "risk_score", "confidence_level", "explanation"
            ]

            missing_fields = []
            for field in required_fields:
                if field not in status_data or status_data[field] is None:
                    missing_fields.append(field)

            if missing_fields:
                print_error(f"Missing audit fields in status: {', '.join(missing_fields)}")
                return False
            else:
                print_success("All audit fields present in status endpoint")
                return True
        else:
            print_error(f"Failed to get status: {status_response.status_code}")
            return False

    except Exception as e:
        print_error(f"Exception: {str(e)}")

    return False

def run_all_tests():
    """Run all decision logic tests"""
    print(f"{Colors.BLUE}")
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║       DECISION LOGIC TEST SUITE                                 ║
    ║       Enhanced Loan Approval System - Score-Based Tiering       ║
    ║       Hard Reject Path | Manual Review | Explainability         ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")

    tests = [
        ("Hard Reject Path", test_case_1_unemployed_hard_reject),
        ("Low Risk - Approved", test_case_2_low_risk_approved),
        ("Borderline - Manual Review", test_case_3_borderline_manual_review),
        ("High Risk - Rejected", test_case_4_high_risk_rejected),
        ("Explainability", test_explainability),
        ("Auditability", test_auditability),
        ("Status Endpoint", test_status_endpoint),
    ]

    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
        time.sleep(1)

    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed_flag else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name}: {status}")

    print(f"\n  Overall: {Colors.GREEN}{passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print_success("All tests passed! Decision logic implementation is working correctly.")
    else:
        print_error(f"{total - passed} test(s) failed. Check implementation.")

if __name__ == "__main__":
    run_all_tests()
