#!/bin/bash

echo "🏦 Loan Assist - Agentic AI Banking System"
echo "=========================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip > /dev/null 2>&1
        echo "✅ Virtual environment created"
    fi
}

install_deps() {
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
}

activate_venv
install_deps

echo ""
echo "✅ Starting services..."
echo ""

tmux new-session -d -s loan-assist -x 250 -y 50

echo "🚀 Starting FastAPI Server (Port 8000)..."
tmux send-keys -t loan-assist "source venv/bin/activate && python3 main.py" Enter
sleep 3

tmux new-window -t loan-assist
echo "🎨 Starting Streamlit UI (Port 8501)..."
tmux send-keys -t loan-assist "source venv/bin/activate && streamlit run streamlit_app.py --server.port 8501" Enter
sleep 2

echo ""
echo "=========================================="
echo "✅ All Services Started Successfully!"
echo "=========================================="
echo ""
echo "📍 Access Points:"
echo "   🌐 Web UI:   http://localhost:8501"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   ❤️  Health:   http://localhost:8000/health"
echo ""
echo "📋 Manage Sessions:"
echo "   View logs:   tmux attach -t loan-assist"
echo "   Stop all:    tmux kill-session -t loan-assist"
echo ""
echo "💡 Test the API:"
echo "   Python:      source venv/bin/activate && python3 test_api.py"
echo "   cURL:        curl http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop or use 'tmux attach -t loan-assist' to monitor"
