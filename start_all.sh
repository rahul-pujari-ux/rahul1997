#!/bin/bash

echo "🏦 Starting Loan Assist - Agentic AI Banking System"
echo "=================================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "📦 Checking Python dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Starting services..."
echo ""

tmux new-session -d -s loan-assist

tmux send-keys -t loan-assist "echo '🚀 Starting FastAPI Server (Port 8000)' && python main.py" Enter
sleep 3

tmux new-window -t loan-assist
tmux send-keys -t loan-assist "echo '🎨 Starting Streamlit UI (Port 8501)' && streamlit run streamlit_app.py --server.port 8501" Enter
sleep 2

echo ""
echo "=================================================="
echo "✅ Services Started Successfully!"
echo "=================================================="
echo ""
echo "📍 Access Points:"
echo "   🌐 Web UI:   http://localhost:8501"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   ❤️  Health:   http://localhost:8000/health"
echo ""
echo "📋 tmux Sessions:"
echo "   Attach: tmux attach -t loan-assist"
echo "   Kill:   tmux kill-session -t loan-assist"
echo ""
echo "💡 To test API:"
echo "   curl http://localhost:8000/health"
echo ""
