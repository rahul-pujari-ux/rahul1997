#!/usr/bin/env python3
"""
Test script for Loan Assist API
Run this after starting the FastAPI server
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
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def test_health():
    """Test health endpoint"""
    print_header("1. Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is FastAPI server running?")
        return False

def test_loan_application(app_data: Dict[str, Any]) -> str:
    """Submit loan application"""
    print_header("2. Submitting Loan Application")
    try:
        print_info(f"Submitting application for {app_data['applicant_id']}")
        print(f"\nApplication Details:")
        print(f"  - Income: ${app_data['income']:,}")
        print(f"  - Loan Amount: ${app_data['loan_amount']:,}")
        print(f"  - Credit Score: {app_data['credit_score']}")
        print(f"  - Employment: {app_data['employment_type']}")

        response = requests.post(f"{BASE_URL}/loan-application", json=app_data)

        if response.status_code == 200:
            result = response.json()
            print_success("Application submitted successfully")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2, default=str))

            case_id = result.get("case_id")
            decision = result.get("decision")
            risk_score = result.get("risk_score")
            confidence = result.get("confidence_level")

            print(f"\n{Colors.GREEN}Decision: {decision.upper()}{Colors.END}")
            print(f"Risk Score: {risk_score:.1f}/100")
            print(f"Confidence: {confidence:.1%}")

            return case_id
        else:
            print_error(f"Application submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_application_status(case_id: str):
    """Check application status"""
    print_header(f"3. Checking Application Status: {case_id}")
    try:
        response = requests.get(f"{BASE_URL}/application-status/{case_id}")

        if response.status_code == 200:
            result = response.json()
            print_success("Status retrieved successfully")
            print(f"\nStatus:")
            print(json.dumps(result, indent=2, default=str))
            return True
        elif response.status_code == 404:
            print_error(f"Application {case_id} not found")
            return False
        else:
            print_error(f"Status check failed: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_list_applications():
    """List all applications"""
    print_header("4. Listing All Applications")
    try:
        response = requests.get(f"{BASE_URL}/applications")

        if response.status_code == 200:
            result = response.json()
            total = result.get("total", 0)
            applications = result.get("applications", [])

            print_success(f"Retrieved {total} application(s)")

            if applications:
                print(f"\nApplications:")
                for app in applications:
                    print(f"\n  Case ID: {app['case_id']}")
                    print(f"  Applicant: {app['applicant_id']}")
                    print(f"  Amount: ${app['loan_amount']:,.0f}")
                    print(f"  Decision: {app.get('decision', 'Pending')}")
                    print(f"  Status: {app['status']}")
            return True
        else:
            print_error(f"List applications failed: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_api_info():
    """Get API information"""
    print_header("5. API Information")
    try:
        response = requests.get(f"{BASE_URL}/api-info")

        if response.status_code == 200:
            result = response.json()
            print_success("API info retrieved")
            print(json.dumps(result, indent=2))
            return True
        else:
            print_error(f"API info retrieval failed: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print(f"{Colors.BLUE}")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║       LOAN ASSIST - API TEST SUITE                      ║
    ║       Agentic AI Intelligent Loan Approval System       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")

    test_cases = [
        {
            "name": "Approved Applicant",
            "applicant_id": "TEST-APPROVED-001",
            "age": 35,
            "income": 100000,
            "employment_type": "salaried",
            "credit_score": 750,
            "loan_amount": 200000,
            "loan_tenure_months": 60,
            "existing_liabilities": 30000,
            "location": "New York, NY",
            "purpose": "home",
            "marital_status": "married",
            "dependents": 2
        },
        {
            "name": "Borderline Applicant",
            "applicant_id": "TEST-BORDERLINE-001",
            "age": 42,
            "income": 60000,
            "employment_type": "self_employed",
            "credit_score": 650,
            "loan_amount": 250000,
            "loan_tenure_months": 84,
            "existing_liabilities": 80000,
            "location": "Los Angeles, CA",
            "purpose": "auto",
            "marital_status": "single",
            "dependents": 0
        },
        {
            "name": "Rejected Applicant",
            "applicant_id": "TEST-REJECTED-001",
            "age": 55,
            "income": 40000,
            "employment_type": "retired",
            "credit_score": 550,
            "loan_amount": 300000,
            "loan_tenure_months": 120,
            "existing_liabilities": 150000,
            "location": "Chicago, IL",
            "purpose": "personal",
            "marital_status": "divorced",
            "dependents": 1
        }
    ]

    if not test_health():
        print_error("Cannot proceed: API is not running")
        return

    for i, test_case in enumerate(test_cases, 1):
        print_header(f"TEST CASE {i}: {test_case['name']}")
        case_id = test_loan_application(test_case)

        if case_id:
            time.sleep(1)
            test_application_status(case_id)
            time.sleep(0.5)

    test_list_applications()
    test_api_info()

    print_header("Test Suite Complete")
    print_success("All tests completed successfully!")
    print(f"\n{Colors.YELLOW}Note: Check the Streamlit UI at http://localhost:8501{Colors.END}\n")

if __name__ == "__main__":
    run_comprehensive_test()
