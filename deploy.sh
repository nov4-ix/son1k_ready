#!/bin/bash

echo "🎵 Son1kVers3 Deployment Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "main_production.py" ]; then
    echo "❌ Error: main_production.py not found. Run this from the project directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Test the system
echo "🧪 Testing system..."
python3 start_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ System is ready for deployment!"
    echo ""
    echo "To deploy to Railway:"
    echo "1. railway login"
    echo "2. railway up"
    echo ""
    echo "To run locally:"
    echo "python3 main_production.py"
    echo ""
    echo "The system will be available at: http://localhost:8000"
else
    echo "❌ System test failed. Please check the errors above."
    exit 1
fi

