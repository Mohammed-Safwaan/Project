@echo off
REM Skin Lesion Detection Backend Setup Script for Windows

echo 🚀 Setting up Skin Lesion Detection Backend...

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "models" mkdir models
if not exist "logs" mkdir logs

REM Initialize database
echo Initializing database...
python -c "from utils.database import get_database_manager; db = get_database_manager(); print('Database initialized successfully!')"

echo ✅ Backend setup completed successfully!
echo.
echo To start the server:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run the server: python app.py
echo.
echo Server will be available at: http://localhost:5000

pause