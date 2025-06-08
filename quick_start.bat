@echo off
setlocal EnableDelayedExpansion
title Advanced OSINT System - Professional Builder
color 0A
chcp 65001 >nul

:: Initialize
set "REQUIRED_SPACE=2"
set "MIN_PYTHON=3.8"
set "SUCCESS_COUNT=0"
set "ERROR_COUNT=0"

echo ================================================================
echo    Advanced OSINT Intelligence System - Professional Builder
echo    Automated Setup and Build Process
echo ================================================================
echo.

:: Force admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

echo [+] Admin rights verified

:: Check Python installation
echo [CHECK] Verifying Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [✗] Python is not installed
    echo [INFO] Please install Python 3.8+ from https://www.python.org/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [+] Python %PYTHON_VERSION% compatible

:: Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorLevel% neq 0 (
    echo [✗] Python %MIN_PYTHON%+ required. Current version: %PYTHON_VERSION%
    echo [INFO] Please upgrade Python to version 3.8 or higher
    pause
    exit /b 1
)

echo [+] Python version compatible

:: Check available disk space
for /f "tokens=3" %%i in ('dir /-c %~dp0 ^| find "bytes free"') do set "FREE_SPACE=%%i"
set /a "FREE_SPACE_GB=!FREE_SPACE:~0,-9!"
if !FREE_SPACE_GB! LSS %REQUIRED_SPACE% (
    choice /m "[?] Low disk space (!FREE_SPACE_GB!GB). Continue"
    if !errorlevel!==2 exit /b 1
)

echo [+] Disk space check passed

:: Create project structure
echo.
echo [SETUP] Creating project structure...
set "DIRS=core collectors utils gui config data data\cache data\exports build logs tests"
for %%d in (%DIRS%) do mkdir "%%d" 2>nul

echo [+] Project structure created

:: Setup pip and venv
echo [*] Configuring Python environment...
python -m pip install --upgrade pip --quiet --no-warn-script-location
if not exist "venv" (
    python -m venv venv
    call venv\Scripts\activate.bat
)

:: Install dependencies
echo [*] Installing packages...
set "PACKAGES=aiohttp requests beautifulsoup4 sqlalchemy pandas openpyxl jinja2 validators dnspython python-whois cryptography textblob pyinstaller setuptools wheel"
set "OPTIONAL=selenium nltk scikit-learn matplotlib tweepy"

:: Install main packages
for %%p in (%PACKAGES%) do (
    echo  Installing %%p...
    python -m pip install "%%p" --quiet --no-warn-script-location
    if !errorlevel!==0 (
        set /a "SUCCESS_COUNT+=1"
    ) else (
        echo  [!] Failed: %%p
        set /a "ERROR_COUNT+=1"
    )
)

:: Try optional packages
echo [*] Installing optional packages...
for %%p in (%OPTIONAL%) do (
    python -m pip install "%%p" --quiet --no-warn-script-location >nul 2>&1
    if !errorlevel!==0 (
        echo  [+] Added: %%p
        set /a "SUCCESS_COUNT+=1"
    )
)

:: Check if we have the main files needed
echo.
echo [CHECK] Verifying project files...

set "REQUIRED_FILES=main.py build_script.py"
set "MISSING=0"
for %%f in (%REQUIRED_FILES%) do if not exist "%%f" set /a "MISSING+=1"

if !MISSING! GTR 0 (
    echo [!] Missing required files
    echo [i] Please ensure all source files are present
    pause & exit /b 1
)

:: Build process
echo.
echo [*] Ready to build
echo  Successful installations: !SUCCESS_COUNT!
if !ERROR_COUNT! GTR 0 echo  Failed installations: !ERROR_COUNT!

choice /m "[?] Start build process"
if !errorlevel!==2 exit /b 0

echo [*] Building system...
python build_script.py
if !errorlevel!==0 (
    echo [+] Build successful
    echo [i] Check 'build' directory for output
) else (
    echo [!] Build failed
    echo [i] Check logs for details
)

echo.
echo Complete! Press any key to exit...
pause >nul