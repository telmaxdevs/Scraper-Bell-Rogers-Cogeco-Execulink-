@echo off
echo ========================================
echo    Telmax Execulink Service Checker
echo ========================================
echo.

REM Check if telmax.csv exists
if not exist "telmax.csv" (
    echo ERROR: telmax.csv file not found!
    echo Please make sure you have a telmax.csv file with the required columns:
    echo - civic_num ^(street number^)
    echo - streetname ^(street name^)
    echo - town ^(city/town name^)
    echo.
    echo Example CSV format:
    echo civic_num,streetname,town
    echo 123,Main Street,Toronto
    echo 456,Oak Avenue,Burlington
    echo.
    pause
    exit /b 1
)

echo Found telmax.csv file. Checking if Python is installed...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python is installed. Checking dependencies...

REM Check if required packages are installed
pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
) else (
    echo Dependencies are already installed.
)

echo.
echo Starting Execulink service checker...
echo This will process all addresses in telmax.csv
echo Progress will be shown as the script runs.
echo You can safely close this window to stop processing.
echo.

REM Run the main script
python execulink_check.py

echo.
echo ========================================
echo Processing complete!
echo Check the execulink_results folder for output files.
echo Main results file: execulink_results\all_results.csv
echo ========================================
pause
