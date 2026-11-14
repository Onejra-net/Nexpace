@echo off
title Nexpace - Debug Mode

:: Always work from the directory where this .bat file is located
cd /d "%~dp0"

echo ========================================================
echo Nexpace - Debug Mode
echo ========================================================
echo.

echo [1/4] Checking virtual environment (.venv)...

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Creating .venv...

    py -m venv .venv

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create the virtual environment.
        pause
        exit /b 1
    )

    echo Virtual environment created successfully.
)

:: Path to Python inside the virtual environment
set "PYTHON_EXE=.venv\Scripts\python.exe"

:: Verify Python exists
if not exist "%PYTHON_EXE%" (
    echo.
    echo ERROR: Python executable was not found:
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

echo Virtual environment is ready.
echo.

echo [2/4] Updating pip and installing required packages...
echo.

"%PYTHON_EXE%" -m pip install --quiet --upgrade pip

if errorlevel 1 (
    echo.
    echo ERROR: Failed to upgrade pip.
    pause
    exit /b 1
)

echo Installing required packages...
"%PYTHON_EXE%" -m pip install --quiet PySide6 pypdf

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages.
    pause
    exit /b 1
)

:: Install additional dependencies from requirements.txt if available
if exist "requirements.txt" (
    echo.
    echo Installing packages from requirements.txt...

    "%PYTHON_EXE%" -m pip install --quiet -r requirements.txt

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install packages from requirements.txt.
        pause
        exit /b 1
    )
)

echo.
echo Dependencies are ready.
echo.

echo [3/4] Checking application files...
echo.

if not exist "main.py" (
    echo ERROR: main.py was not found.
    echo.
    echo Current directory:
    echo %CD%
    echo.
    pause
    exit /b 1
)

if not exist "translations.json" (
    echo WARNING: translations.json was not found.
)

if not exist "version.txt" (
    echo WARNING: version.txt was not found.
)

echo Application files checked.
echo.

echo [4/4] Starting Nexpace in debug mode...
echo ========================================================
echo.

"%PYTHON_EXE%" "main.py"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ========================================================

if "%EXIT_CODE%"=="0" (
    echo Nexpace has been closed successfully.
) else (
    echo Nexpace exited with error code: %EXIT_CODE%.
)

echo ========================================================
echo.

pause
exit /b %EXIT_CODE%