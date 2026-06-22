# 🚀 Loan Assist - Quick Start Guide

## ⚡ 30-Second Setup

### 1. Install Dependencies
```bash
cd /home/ubuntu/My_Final_Project
pip install -r requirements.txt
```

### 2. Start Services (Choose One)

**Option A: Automatic (Linux/Mac)**
```bash
chmod +x start_all.sh
./start_all.sh
```

**Option B: Manual (All Platforms) - Open 2 terminals:**

Terminal 1:
```bash
python main.py
```

Terminal 2:
```bash
streamlit run streamlit_app.py --server.port 8501
```

### 3. Access the Application

Open in your browser:
- 🌐 **Web UI**: http://localhost:8501
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️  **Health**: http://localhost:8000/health

---

## 📝 Quick Test

### Option 1: Use Streamlit UI (Easiest)
1. Go to http://localhost:8501
2. Fill the loan form with your details
3. Click "Submit Application"
4. See instant decision with risk score

### Option 2: Use Python Test Script
```bash
python test_api.py
```

### Option 3: Use cURL
```bash
# Health check
curl http://localhost:8000/health

# Submit application
curl -X POST http://localhost:8000/loan-application \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "DEMO-001",
    "age": 35,
    "income": 75000,
    "employment_type": "salaried",
    "credit_score": 720,
    "loan_amount": 200000,
    "loan_tenure_months": 60,
    "existing_liabilities": 50000,
    "location": "NYC",
    "purpose": "home",
    "marital_status": "married",
    "dependents": 2
  }'
```

---

## 🎯 Sample Applications to Test

### ✅ Approved Application
```json
{
  "applicant_id": "DEMO-APPROVED",
  "age": 35,
  "income": 100000,
  "employment_type": "salaried",
  "credit_score": 750,
  "loan_amount": 200000,
  "loan_tenure_months": 60,
  "existing_liabilities": 30000,
  "location": "New York",
  "purpose": "home",
  "marital_status": "married",
  "dependents": 2
}
```

### 🟡 Manual Review Application
```json
{
  "applicant_id": "DEMO-REVIEW",
  "age": 42,
  "income": 60000,
  "employment_type": "self_employed",
  "credit_score": 650,
  "loan_amount": 250000,
  "loan_tenure_months": 84,
  "existing_liabilities": 80000,
  "location": "Los Angeles",
  "purpose": "auto",
  "marital_status": "single",
  "dependents": 0
}
```

### ❌ Rejected Application
```json
{
  "applicant_id": "DEMO-REJECTED",
  "age": 58,
  "income": 40000,
  "employment_type": "retired",
  "credit_score": 550,
  "loan_amount": 300000,
  "loan_tenure_months": 120,
  "existing_liabilities": 150000,
  "location": "Chicago",
  "purpose": "personal",
  "marital_status": "divorced",
  "dependents": 1
}
```

---

## 📂 Project Structure

```
My_Final_Project/
├── main.py                  ← FastAPI backend (run this)
├── streamlit_app.py         ← Streamlit UI (run this)
├── orchestration.py         ← Agent orchestration
├── agents.py                ← AI agents
├── models.py                ← Data models
├── database.py              ← Data persistence
├── config.py                ← Configuration
├── requirements.txt         ← Dependencies
├── .env                     ← API key & settings
├── start_all.sh             ← Startup script
├── test_api.py              ← Test suite
└── README.md                ← Full documentation
```

---

## ✅ System Architecture

```
User (Browser)
    ↓
Streamlit UI (Port 8501)
    ↓
FastAPI Backend (Port 8000)
    ↓
LangGraph Orchestrator
    ↓
4 AI Agents:
├─ Applicant Profile Agent
├─ Financial Risk Agent
├─ Decision Agent
└─ Compliance Agent
    ↓
Database (JSON)
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Not Found
```bash
# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### Can't Connect to API
- Make sure FastAPI is running: `python main.py`
- Check if port 8000 is accessible: `curl http://localhost:8000/health`

### Permission Denied on start_all.sh
```bash
chmod +x start_all.sh
./start_all.sh
```

---

## 📊 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/loan-application` | Submit application |
| GET | `/application-status/{case_id}` | Check status |
| GET | `/applications` | List all apps |
| GET | `/docs` | API documentation |

---

## 🎓 How It Works

1. **Submit Application** via UI or API
2. **FastAPI receives** and validates data
3. **Orchestrator starts** 4-agent workflow
4. **Agents analyze** in parallel:
   - Profile (income stability)
   - Risk (DTI, credit score)
   - Decision (synthesis)
   - Compliance (notification)
5. **Return decision** with risk score (0-100)
6. **User sees** Approved/Rejected/Manual Review

---

## 📈 Decision Logic

```
Risk Score Ranges:
0-25    → 🟢 APPROVED (95% confidence)
25-45   → 🟢 APPROVED (75% confidence)
45-65   → 🟡 MANUAL REVIEW
65-100  → 🔴 REJECTED
```

---

## 🚀 Next Steps

1. ✅ Run `python main.py`
2. ✅ Run `streamlit run streamlit_app.py --server.port 8501`
3. ✅ Open http://localhost:8501
4. ✅ Submit a test application
5. ✅ See instant AI decision with explanation

---

## 💡 Tips

- **Fastest way to test**: Use Streamlit UI
- **For developers**: Use `/docs` endpoint
- **Batch testing**: Use `test_api.py`
- **Monitor logs**: Both terminals show real-time logs

---

## 🎯 Key Files to Understand

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server & endpoints |
| `streamlit_app.py` | Web UI interface |
| `orchestration.py` | Agent workflow engine |
| `agents.py` | AI agent implementations |
| `models.py` | Request/response schemas |

---

**Questions?** Check `README.md` for detailed documentation.

**Ready?** Start with: `python main.py` & `streamlit run streamlit_app.py --server.port 8501`
