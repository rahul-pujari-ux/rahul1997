import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

st.set_page_config(
    page_title="Loan Assist - AI Banking System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

st.title("🏦 Loan Assist - Agentic AI Banking System")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📝 New Application", "📊 Status Check", "📋 All Applications", "ℹ️ About"]
)

with tab1:
    st.header("Submit Loan Application")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Applicant Information")
        applicant_id = st.text_input("Applicant ID", placeholder="APP-001", key="app_id")
        age = st.slider("Age", min_value=18, max_value=70, value=35)
        income = st.number_input("Annual Income ($)", min_value=30000, value=75000, step=5000)
        employment_type = st.selectbox(
            "Employment Type",
            ["salaried", "self_employed", "business_owner", "student", "retired"]
        )

    with col2:
        st.subheader("Credit & Loan Details")
        credit_score = st.slider("Credit Score", min_value=300, max_value=850, value=700)
        loan_amount = st.number_input("Loan Amount ($)", min_value=5000, value=200000, step=10000)
        loan_tenure = st.slider("Loan Tenure (months)", min_value=6, max_value=360, value=60)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Financial & Personal Info")
        existing_liabilities = st.number_input("Existing Liabilities ($)", min_value=0, value=0, step=5000)
        location = st.text_input("Location", placeholder="New York, NY")
        purpose = st.selectbox(
            "Loan Purpose",
            ["home", "auto", "personal", "business", "education"]
        )

    with col4:
        st.subheader("Additional Details")
        marital_status = st.selectbox("Marital Status", ["single", "married", "divorced", "widowed"])
        dependents = st.slider("Number of Dependents", min_value=0, max_value=10, value=0)

    if st.button("🚀 Submit Application", use_container_width=True, type="primary"):
        if not applicant_id:
            st.error("❌ Please enter Applicant ID")
        else:
            with st.spinner("⏳ Processing your application through AI agents..."):
                try:
                    payload = {
                        "applicant_id": applicant_id,
                        "age": age,
                        "income": income,
                        "employment_type": employment_type,
                        "credit_score": credit_score,
                        "loan_amount": loan_amount,
                        "loan_tenure_months": loan_tenure,
                        "existing_liabilities": existing_liabilities,
                        "location": location,
                        "purpose": purpose,
                        "marital_status": marital_status,
                        "dependents": dependents
                    }

                    response = requests.post(f"{API_URL}/loan-application", json=payload)

                    if response.status_code == 200:
                        result = response.json()

                        st.success("✅ Application Processed Successfully!")

                        col_result1, col_result2, col_result3 = st.columns(3)

                        with col_result1:
                            st.metric("Case ID", result["case_id"])

                        with col_result2:
                            decision_color = "🟢" if result["decision"] == "approved" else "🔴" if result["decision"] == "rejected" else "🟡"
                            st.metric("Decision", f"{decision_color} {result['decision'].upper()}")

                        with col_result3:
                            st.metric("Risk Score", f"{result['risk_score']:.1f}/100")

                        with st.expander("📈 Detailed Results"):
                            col_detail1, col_detail2 = st.columns(2)

                            with col_detail1:
                                st.metric("Confidence Level", f"{result['confidence_level']:.1%}")
                                st.metric("Loan Amount", f"${loan_amount:,.2f}")

                            with col_detail2:
                                st.metric("Annual Income", f"${income:,.2f}")
                                st.metric("Credit Score", credit_score)

                            st.subheader("Explanation")
                            st.info(result["explanation"])

                        st.session_state.last_case_id = result["case_id"]

                    else:
                        st.error(f"❌ Error: {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Ensure the FastAPI server is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("Check Application Status")

    search_col1, search_col2 = st.columns([3, 1])

    with search_col1:
        case_id = st.text_input(
            "Enter Case ID",
            placeholder="CASE-000001",
            key="search_case_id"
        )

    with search_col2:
        if st.button("🔍 Search", use_container_width=True):
            if not case_id:
                st.error("❌ Please enter a Case ID")
            else:
                try:
                    response = requests.get(f"{API_URL}/application-status/{case_id}")

                    if response.status_code == 200:
                        status = response.json()

                        st.success("✅ Application Found")

                        col_status1, col_status2, col_status3 = st.columns(3)

                        with col_status1:
                            st.metric("Case ID", status["case_id"])

                        with col_status2:
                            decision = status["decision"] if status["decision"] else "Processing"
                            decision_color = "🟢" if decision == "approved" else "🔴" if decision == "rejected" else "🟡"
                            st.metric("Decision", f"{decision_color} {decision.upper() if decision != 'Processing' else decision}")

                        with col_status3:
                            st.metric("Status", status["status"].upper())

                        with st.expander("📋 Application Details"):
                            col_detail1, col_detail2 = st.columns(2)

                            with col_detail1:
                                st.write(f"**Applicant ID:** {status['applicant_id']}")
                                st.write(f"**Loan Amount:** ${status['loan_amount']:,.2f}")

                            with col_detail2:
                                st.write(f"**Created:** {status['created_at']}")
                                st.write(f"**Updated:** {status['updated_at']}")

                    elif response.status_code == 404:
                        st.warning("⚠️ Application not found")

                    else:
                        st.error(f"❌ Error: {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Ensure the FastAPI server is running.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab3:
    st.header("All Applications")

    if st.button("🔄 Refresh", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/applications")

            if response.status_code == 200:
                data = response.json()
                total = data["total"]

                st.metric("Total Applications", total)

                if total > 0:
                    st.subheader("Application List")

                    applications = data["applications"]

                    for app in applications:
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.write(f"**{app['case_id']}**")

                        with col2:
                            decision_color = "🟢" if app.get("decision") == "approved" else "🔴" if app.get("decision") == "rejected" else "🟡"
                            st.write(f"{decision_color} {app.get('decision', 'Pending').upper()}")

                        with col3:
                            st.write(f"${app['loan_amount']:,.0f}")

                        with col4:
                            st.write(f"📅 {app['created_at'][:10]}")

                        st.divider()

                else:
                    st.info("No applications found")

            else:
                st.error(f"❌ Error: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Ensure the FastAPI server is running.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with tab4:
    st.header("About Loan Assist")

    st.subheader("🤖 Multi-Agent Agentic AI System")

    st.markdown("""
    **Loan Assist** is an advanced banking system that uses multi-agent AI to automate loan approvals.

    ### Key Features:
    - ✅ **Intelligent Analysis**: 4 specialized AI agents analyze loan applications
    - ✅ **Real-time Processing**: Fast decision-making with explainable outcomes
    - ✅ **Risk Assessment**: Comprehensive financial risk analysis
    - ✅ **Compliance Ready**: Audit trails and compliance logging
    - ✅ **Scalable Architecture**: Microservices-based design

    ### Agent Workflow:
    1. **Applicant Profile Agent** - Analyzes applicant background and income stability
    2. **Financial Risk Agent** - Evaluates debt-to-income ratio and credit risk
    3. **Decision Agent** - Synthesizes all factors for final decision
    4. **Compliance Agent** - Sends notifications and logs decisions

    ### Technology Stack:
    - **LLM**: Anthropic Claude Sonnet 4.6
    - **Backend**: FastAPI + LangGraph
    - **Frontend**: Streamlit
    - **Architecture**: Multi-agent Agentic AI

    ### Decisions:
    - 🟢 **Approved**: Application meets all criteria
    - 🟡 **Manual Review**: Requires human assessment
    - 🔴 **Rejected**: Does not meet lending criteria

    ---
    **API Base URL**: http://localhost:8000
    **Documentation**: http://localhost:8000/docs
    """)

    with st.expander("📚 API Endpoints"):
        st.code("""
GET  /health                    - Health check
POST /loan-application          - Submit new application
GET  /application-status/{case_id} - Check status
GET  /applications              - List all applications
        """, language="text")

st.sidebar.markdown("---")
st.sidebar.subheader("📞 Support")
st.sidebar.info("""
**API**: http://localhost:8000
**Docs**: http://localhost:8000/docs
**Health**: http://localhost:8000/health
""")

st.sidebar.markdown("---")
st.sidebar.write("Loan Assist v1.0.0")
