#!/bin/bash
# Launch Binance Algo Bot Dashboard

echo "🤖 Starting Binance Algo Bot Dashboard..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✏️  Please edit .env with your API keys!"
    echo ""
fi

# Launch dashboard
echo "🚀 Launching dashboard at http://localhost:8501"
echo "=================================="
streamlit run dashboard.py
