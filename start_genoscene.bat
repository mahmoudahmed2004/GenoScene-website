@echo off
REM GenoScene - Windows Startup Script
REM ==================================

echo.
echo ========================================
echo   GenoScene - Forensic Phenotype Prediction
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import pandas, numpy, matplotlib, scipy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

REM Ask user what they want to do
echo.
echo What would you like to do?
echo 1. Open Web Interface
echo 2. Run Demo Analysis
echo 3. Run Custom Analysis
echo 4. Install/Update Packages
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Opening web interface...
    start index.html
) else if "%choice%"=="2" (
    echo Running demo analysis...
    python run_genoscene.py --demo
    pause
) else if "%choice%"=="3" (
    set /p sample_id="Enter Sample ID: "
    set /p data_file="Enter path to CSV file: "
    python run_genoscene.py "%sample_id%" "%data_file%"
    pause
) else if "%choice%"=="4" (
    echo Installing/updating packages...
    python run_genoscene.py --install
    pause
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo Operation completed!
pause
