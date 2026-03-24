@echo off
set "START_DIR=C:\Users\David\Documents\Local_Python\aix"

REM Navigate to the project directory.
cd /d "%START_DIR%"

if not exist "%START_DIR%\venv\Scripts\activate.bat" (
    echo Could not find virtual environment activation script:
    echo   %START_DIR%\venv\Scripts\activate.bat
    echo Recreate it with: python -m venv venv
    exit /b 1
)

REM Activate the virtual environment in the current shell.
echo Starting Project AIX in local directory %START_DIR%
echo Activating virtual environment from venv\Scripts\activate.bat...
call "%START_DIR%\venv\Scripts\activate.bat"

if errorlevel 1 (
    echo Virtual environment activation failed.
    exit /b 1
)

echo Environment ready. If needed, install deps with:
echo   python -m pip install -r requirements.txt
