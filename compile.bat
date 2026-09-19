@echo off
cd /d "%~dp0"

echo ========================================
echo        Nexpace Portable Builder
echo ========================================
echo.

:: 1. Create virtual environment if it does not exist
if not exist .venv (
    echo Creating virtual environment...
    py -m venv .venv

    if errorlevel 1 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

:: 2. Virtual environment paths
set "PYTHON_EXE=.venv\Scripts\python.exe"
set "PIP_EXE=.venv\Scripts\pip.exe"
set "PYINSTALLER_EXE=.venv\Scripts\pyinstaller.exe"

:: 3. Update pip
echo Updating pip...
"%PIP_EXE%" install --quiet --upgrade pip

if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

:: 4. Install required packages
echo Installing dependencies...
"%PIP_EXE%" install --quiet PySide6 pypdf pyinstaller

if errorlevel 1 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: 5. Install requirements.txt if available
if exist requirements.txt (
    echo Installing requirements.txt...
    "%PIP_EXE%" install --quiet -r requirements.txt

    if errorlevel 1 (
        echo Failed to install packages from requirements.txt.
        pause
        exit /b 1
    )
)

:: 6. Stop previous Nexpace instance
echo Stopping previous Nexpace instance...
taskkill /f /im Nexpace.exe >nul 2>&1

:: 7. Clean previous build
echo Cleaning previous build...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Nexpace.spec del /f /q Nexpace.spec

:: 8. Build portable application
echo.
echo Building Nexpace...
echo.

"%PYINSTALLER_EXE%" ^
    --noconsole ^
    --onedir ^
    --name Nexpace ^
    --icon=icon.ico ^
    --clean ^
    --add-data "translations.json;." ^
    --add-data "version.txt;." ^
    main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo Build failed.
    echo ========================================
    pause
    exit /b 1
)

:: 9. Copy additional files if required
if exist translations.json copy /Y translations.json dist\Nexpace\ >nul
if exist version.txt copy /Y version.txt dist\Nexpace\ >nul

:: 10. Create portable marker
echo Nexpace portable build > dist\Nexpace\PORTABLE.txt

:: 11. Remove temporary build files
if exist build rmdir /s /q build
if exist Nexpace.spec del /f /q Nexpace.spec

:: 12. Verify executable
if not exist dist\Nexpace\Nexpace.exe (
    echo.
    echo Nexpace.exe was not created.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Nexpace portable build completed!
echo ========================================
echo.
echo Output:
echo dist\Nexpace\
echo.

:: 13. Launch the portable version
start "" "dist\Nexpace\Nexpace.exe"

exit /b 0