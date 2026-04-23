@echo off
echo ========================================
echo BPM-Nova Backend AI Service Setup
echo ========================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo [4/5] Please configure .env file now
echo Copy .env.example to .env and fill in your configuration:
echo   - DATABASE_URL (PostgreSQL connection string)
echo   - AI_API_KEY (DeepSeek or Qwen API key)
echo   - AI_BASE_URL (API endpoint)
echo   - AI_MODEL (model name)
echo.
pause

echo [5/5] Initializing database...
python init_db.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    echo Please check your database connection in .env file
    pause
    exit /b 1
)
echo ✓ Database initialized
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the server, run:
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Or simply run: start.bat
echo.
pause

@REM Made with Bob
