#!/bin/bash
# Convenient 1-Click Startup Script for Livestock Health Monitoring Assistant

# Move to the script's directory
cd "$(dirname "$0")"

echo "========================================================"
echo "🐄 Starting Livestock Health Monitoring Assistant..."
echo "========================================================"

# Activate virtual environment if present
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run the app
python3 app.py
