# 🚀 Loan Assist - Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.9+
- bash/shell
- ~500MB disk space
- 2GB RAM minimum
- Internet connection (for Claude API)

### Step 1: Clone/Navigate to Project
```bash
cd /home/ubuntu/My_Final_Project
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Verify .env file exists with:
cat .env
```

Expected output:
```
ANTHROPIC_API_KEY=sk-g6E6zqc1nd2IbiNfFgprIA
MODEL=global.anthropic.claude-sonnet-4-6
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./loan_assist.db
```

### Step 5: Start Services

**Option A: Automated (Linux/Mac)**
```bash
chmod +x run.sh
./run.sh
```

**Option B: Manual (All Platforms)**

Terminal 1:
```bash
source venv/bin/activate
python3 main.py
```

Terminal 2:
```bash
source venv/bin/activate
streamlit run streamlit_app.py --server.port 8501
```

### Step 6: Access Application
- **Web UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Testing

### Quick Health Check
```bash
curl http://localhost:8000/health
```

### Run Full Test Suite
```bash
source venv/bin/activate
python3 test_api.py
```

### Manual Testing with cURL

**Submit Application**:
```bash
curl -X POST http://localhost:8000/loan-application \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST-001",
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

**Check Status**:
```bash
curl http://localhost:8000/application-status/CASE-000001
```

**List All**:
```bash
curl http://localhost:8000/applications
```

---

## Production Deployment

### Option 1: Docker Deployment

**Create Dockerfile** (if needed):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python3", "main.py"]
```

**Build and Run**:
```bash
docker build -t loan-assist .
docker run -p 8000:8000 -p 8501:8501 --env-file .env loan-assist
```

### Option 2: Heroku Deployment

**Create Procfile**:
```
web: python3 main.py
worker: streamlit run streamlit_app.py --server.port 8501
```

**Deploy**:
```bash
heroku create loan-assist
heroku config:set ANTHROPIC_API_KEY=<your-key>
git push heroku main
```

### Option 3: AWS EC2 Deployment

**1. Launch EC2 Instance**:
- AMI: Ubuntu 22.04 LTS
- Instance: t3.medium
- Security Groups: Allow 8000, 8501

**2. Connect and Setup**:
```bash
ssh -i your-key.pem ubuntu@<instance-ip>
sudo apt update
sudo apt install python3.11 python3-pip
cd /home/ubuntu/My_Final_Project
```

**3. Deploy Application**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3 main.py > api.log 2>&1 &
nohup streamlit run streamlit_app.py --server.port 8501 > ui.log 2>&1 &
```

**4. Configure Reverse Proxy (nginx)**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Option 4: Kubernetes Deployment

**Create k8s-deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loan-assist
spec:
  replicas: 2
  selector:
    matchLabels:
      app: loan-assist
  template:
    metadata:
      labels:
        app: loan-assist
    spec:
      containers:
      - name: api
        image: loan-assist:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
---
apiVersion: v1
kind: Service
metadata:
  name: loan-assist-service
spec:
  selector:
    app: loan-assist
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy**:
```bash
kubectl create secret generic api-keys --from-literal=anthropic=<key>
kubectl apply -f k8s-deployment.yaml
```

---

## Environment Configuration

### Development (.env)
```env
ANTHROPIC_API_KEY=sk-...
MODEL=global.anthropic.claude-sonnet-4-6
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./loan_assist.db
```

### Production (.env.prod)
```env
ANTHROPIC_API_KEY=<production-key>
MODEL=global.anthropic.claude-sonnet-4-6
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@db.example.com/loanassist
ALLOWED_HOSTS=loan-assist.example.com
```

---

## Monitoring & Logging

### View FastAPI Logs
```bash
tail -f /path/to/api.log
```

### View Streamlit Logs
```bash
tail -f /path/to/ui.log
```

### Monitor Resources
```bash
# Check CPU/Memory
top
ps aux | grep python

# Check Ports
lsof -i :8000
lsof -i :8501

# Check Disk
df -h
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Module Import Errors
```bash
# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

### API Connection Errors
```bash
# Check if service is running
curl http://localhost:8000/health

# Restart services
pkill -f "python3 main.py"
python3 main.py
```

### Database Errors
```bash
# Reset database
rm loan_assist_db.json
# Restart application
python3 main.py
```

### Out of Memory
```bash
# Monitor memory
free -h

# Increase swap
sudo dd if=/dev/zero of=/swapfile bs=1G count=2
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Performance Optimization

### Database Optimization
```python
# Add indexes for faster queries
import sqlite3
conn = sqlite3.connect('loan_assist.db')
conn.execute('CREATE INDEX idx_case_id ON applications(case_id)')
conn.execute('CREATE INDEX idx_applicant_id ON applications(applicant_id)')
conn.commit()
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_risk_thresholds():
    return {...}
```

### Database Connection Pooling
```python
# Use connection pool for PostgreSQL
from sqlalchemy.pool import QueuePool
engine = create_engine('postgresql://...', 
    poolclass=QueuePool, pool_size=10, max_overflow=20)
```

---

## Backup & Recovery

### Backup JSON Database
```bash
# Manual backup
cp loan_assist_db.json loan_assist_db.backup_$(date +%Y%m%d_%H%M%S).json

# Automated daily backup
0 2 * * * cp /path/to/loan_assist_db.json /backups/db_$(date +\%Y\%m\%d).json
```

### Restore from Backup
```bash
cp loan_assist_db.backup.json loan_assist_db.json
python3 main.py
```

---

## Security Hardening

### 1. API Security
```python
# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/loan-application")
@limiter.limit("100/minute")
async def submit_application(request: LoanApplicationRequest):
    ...
```

### 2. CORS Configuration
```python
# Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. HTTPS/SSL
```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d yourdomain.com
```

### 4. Environment Variables
```bash
# Don't commit .env file
echo ".env" >> .gitignore

# Use environment variables
export ANTHROPIC_API_KEY="..."
```

### 5. Input Validation
```python
# Already implemented in models.py
# But can add additional validators
from pydantic import validator

class LoanApplicationRequest(BaseModel):
    @validator('email')
    def email_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

---

## Scaling Strategies

### Horizontal Scaling
```bash
# Run multiple instances with load balancer
python3 main.py --port 8000 &
python3 main.py --port 8001 &
python3 main.py --port 8002 &

# Use nginx to distribute
```

### Vertical Scaling
```bash
# Increase server resources
# - More CPU cores
# - More RAM
# - SSD storage
```

### Database Scaling
```bash
# Move to PostgreSQL
# Add read replicas
# Implement caching (Redis)
```

---

## Monitoring Setup (Prometheus/Grafana)

### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'loan-assist'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboards
- Request rate
- Response time
- Error rate
- Application decisions distribution
- Risk score histogram

---

## Continuous Integration/Deployment

### GitHub Actions Workflow
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: docker build -t loan-assist .
      - run: docker push myregistry/loan-assist
      - run: kubectl apply -f k8s-deployment.yaml
```

---

## Maintenance

### Regular Tasks
- **Daily**: Monitor logs, check error rates
- **Weekly**: Backup database, review metrics
- **Monthly**: Update dependencies, security scan
- **Quarterly**: Performance review, capacity planning

### Dependency Updates
```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade fastapi

# Update all
pip install --upgrade -r requirements.txt
```

---

## Disaster Recovery Plan

### 1. Data Loss
- **Prevention**: Regular automated backups
- **Recovery**: Restore from latest backup (< 1 hour old)

### 2. Service Outage
- **Prevention**: Health checks, automated restarts
- **Recovery**: Manual restart, failover to secondary instance

### 3. API Failure
- **Prevention**: Error handling, circuit breakers
- **Recovery**: Restart service, check logs, roll back if needed

### 4. Database Corruption
- **Prevention**: Validation, transactions
- **Recovery**: Restore from backup

---

**Version**: 1.0.0  
**Last Updated**: 2024-06-19

## Support

For issues:
1. Check logs: `tail -f api.log`
2. Review TROUBLESHOOTING section
3. Check GitHub issues
4. Contact support team
