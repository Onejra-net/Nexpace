@echo off
title Nexpace - Debug Mode
cd /d "%~dp0"

echo [1/4] Checking virtual environment (.venv)...
if not exist .venv (
    py -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

:: Set paths to the virtual environment
set "PYTHON_EXE=.venv\Scripts\python.exe"
set "PIP_EXE=.venv\Scripts\pip.exe"

echo [2/4] Updating pip and installing required packages...
"%PIP_EXE%" install --quiet --upgrade pip

if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

:: Install all packages required by the application
"%PIP_EXE%" install --quiet PySide6 pypdf

if errorlevel 1 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Install additional dependencies from requirements.txt if available
if exist requirements.txt (
    "%PIP_EXE%" install --quiet -r requirements.txt

    if errorlevel 1 (
        echo Failed to install packages from requirements.txt.
        pause
        exit /b 1
    )
)

echo [3/4] Checking application files...

if not exist main.py (
    echo main.py was not found.
    pause
    exit /b 1
)

if not exist translations.json (
    echo Warning: translations.json was not found.
)

if not exist version.txt (
    echo Warning: version.txt was not found.
)

echo [4/4] Starting Nexpace in debug mode...
echo ========================================================

"%PYTHON_EXE%" main.py

echo ========================================================
echo Nexpace has been closed.
pause