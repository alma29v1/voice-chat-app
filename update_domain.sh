#!/bin/bash

echo "🔄 ThreeWayChat Domain Updater"
echo "================================"

# Check if Python script exists
if [ ! -f "domain_checker.py" ]; then
    echo "❌ domain_checker.py not found!"
    exit 1
fi

# Run the domain checker
echo "🔍 Checking for current domain..."
python3 domain_checker.py

echo ""
echo "📋 Next steps:"
echo "1. If the domain was updated, rebuild your iOS app"
echo "2. If no domain found, restart your Replit server"
echo "3. Run this script again after restarting"
