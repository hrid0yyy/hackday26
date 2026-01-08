@echo off
echo Starting FastAPI Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Run the FastAPI application
echo Starting FastAPI server...
echo Server will be available at http://127.0.0.1:8000
echo API documentation at http://127.0.0.1:8000/docs
echo.
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

REM Keep window open if there's an error
if errorlevel 1 pause
