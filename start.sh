#!/bin/bash
# Start script for ASL Monitoring System
# This script starts the monitoring system with proper environment setup

set -e

echo "=================================================="
echo "Starting ASL Monitoring System"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your actual configuration!"
    echo "   Especially set SLACK_WEBHOOK_URL if you want Slack alerts."
    echo ""
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create data directory if it doesn't exist
mkdir -p data

echo ""
echo "=================================================="
echo "Starting monitoring system..."
echo "=================================================="
echo ""

# Start the application
python app.py
