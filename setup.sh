#!/bin/bash

echo "RSS to PDF Converter - Setup Script"
echo "==================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test the installation
echo "Testing installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "To use the RSS to PDF converter:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Run the converter: python rss_to_pdf.py 'RSS_URL'"
    echo ""
    echo "Example:"
    echo "  source venv/bin/activate"
    echo "  python rss_to_pdf.py 'https://news.ycombinator.com/rss' -m 10"
    echo ""
else
    echo "❌ Installation test failed"
    exit 1
fi 