@echo off
REM SMF Type 30 Analysis Runner for Windows
REM Disables Python alias and runs the pipeline

echo ======================================
echo SMF Type 30 Record Analysis Pipeline
echo ======================================
echo.

REM Disable Windows Store Python alias by running from real Python installation
REM First, try to find python in PATH (excluding Windows Store alias)

setlocal enabledelayedexpansion

REM Look for Python in common installation paths
set PYTHONFOUND=0

for /D %%P in ("C:\Python*") do (
    if exist "%%P\python.exe" (
        set PYTHONEXE=%%P\python.exe
        set PYTHONFOUND=1
        goto foundpython
    )
)

:foundpython
if %PYTHONFOUND%==0 (
    echo ERROR: Python not found in standard locations.
    echo Please install Python from python.org and ensure it's in PATH
    echo.
    echo For development/testing, you can also run:
    echo   1. Open Python REPL
    echo   2. Copy-paste the code from run_full_pipeline.py
    pause
    exit /b 1
)

echo Found Python at: !PYTHONEXE!
echo.

REM Install dependencies
echo Installing required packages...
"!PYTHONEXE!" -m pip install --quiet -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    echo.
    echo You may need to run:
    echo   pip install matplotlib pandas numpy
    pause
    exit /b 1
)

REM Run the pipeline
echo.
echo Running full analysis pipeline...
echo.

"!PYTHONEXE!" run_full_pipeline.py

echo.
echo ======================================
echo Pipeline Complete!
echo ======================================
echo.
echo Output files generated in: reports/
echo.
pause
