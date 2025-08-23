#!/bin/bash

# EVA Interface Launcher Script
echo "🚗 Starting EVA Vehicle Data Analyzer..."

# Check if virtual environment exists
if [ ! -d "eva_env" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source eva_env/bin/activate

# Check if required packages are installed
echo "📦 Checking required packages..."
python -c "import tkinter, PIL, pandas, numpy; print('✅ All required packages found')" 2>/dev/null || {
    echo "❌ Missing required packages. Installing..."
    pip install -r requirements.txt
}

# Run the EVA interface
echo "🎯 Launching EVA Interface..."
python run_eva.py

# Deactivate virtual environment
deactivate
echo "👋 EVA Interface closed" 