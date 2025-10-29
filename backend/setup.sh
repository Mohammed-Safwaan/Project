#!/bin/bash

# Skin Lesion Detection Backend Setup Script

echo "🚀 Setting up Skin Lesion Detection Backend..."

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads
mkdir -p models
mkdir -p logs

# Initialize database
echo "Initializing database..."
python -c "
from utils.database import get_database_manager
db = get_database_manager()
print('Database initialized successfully!')
"

echo "✅ Backend setup completed successfully!"
echo ""
echo "To start the server:"
echo "1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Run the server: python app.py"
echo ""
echo "Server will be available at: http://localhost:5000"