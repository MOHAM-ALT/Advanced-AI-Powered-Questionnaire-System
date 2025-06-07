@echo off
title Advanced OSINT System - Professional Builder
color 0A
chcp 65001 >nul

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

echo [✓] Administrator privileges confirmed
echo [INFO] Starting professional build process...
echo.

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

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [✓] Python %PYTHON_VERSION% detected

:: Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorLevel% neq 0 (
    echo [✗] Python 3.8+ required. Current version: %PYTHON_VERSION%
    echo [INFO] Please upgrade Python to version 3.8 or higher
    pause
    exit /b 1
)

echo [✓] Python version compatible

:: Check available disk space
for /f "tokens=3" %%i in ('dir /-c %~dp0 ^| find "bytes free"') do set FREE_SPACE=%%i
set /a FREE_SPACE_GB=%FREE_SPACE:~0,-9%
if %FREE_SPACE_GB% LSS 2 (
    echo [⚠] Warning: Low disk space. Available: %FREE_SPACE_GB%GB, Recommended: 2GB+
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo [✓] Disk space check passed

:: Create project structure
echo.
echo [SETUP] Creating project structure...
if not exist "core" mkdir "core"
if not exist "collectors" mkdir "collectors"
if not exist "utils" mkdir "utils"
if not exist "gui" mkdir "gui"
if not exist "config" mkdir "config"
if not exist "data" mkdir "data"
if not exist "data\cache" mkdir "data\cache"
if not exist "data\exports" mkdir "data\exports"
if not exist "build" mkdir "build"
if not exist "logs" mkdir "logs"

echo [✓] Project structure created

:: Install/upgrade pip
echo.
echo [INSTALL] Upgrading pip to latest version...
python -m pip install --upgrade pip --quiet --no-warn-script-location
if %errorLevel% neq 0 (
    echo [⚠] Warning: pip upgrade failed, continuing...
)

echo [✓] Pip upgraded

:: Install core dependencies
echo.
echo [INSTALL] Installing core dependencies...
echo [INFO] This may take 5-10 minutes depending on your internet connection...

:: Core packages for basic functionality
set CORE_PACKAGES=aiohttp requests beautifulsoup4 sqlalchemy pandas openpyxl jinja2 validators dnspython python-whois cryptography textblob

echo [INFO] Installing essential packages...
for %%p in (%CORE_PACKAGES%) do (
    echo   Installing %%p...
    python -m pip install "%%p" --quiet --no-warn-script-location
    if errorlevel 1 (
        echo   [⚠] Warning: Failed to install %%p
    ) else (
        echo   [✓] %%p installed
    )
)

:: Build tools
echo.
echo [INSTALL] Installing build tools...
python -m pip install pyinstaller setuptools wheel --quiet --no-warn-script-location
echo [✓] Build tools installed

:: Optional packages (best effort)
echo.
echo [INSTALL] Installing optional packages (best effort)...
set OPTIONAL_PACKAGES=selenium nltk scikit-learn matplotlib tweepy

for %%p in (%OPTIONAL_PACKAGES%) do (
    echo   Trying to install %%p...
    python -m pip install "%%p" --quiet --no-warn-script-location >nul 2>&1
    if errorlevel 1 (
        echo   [−] Skipped %%p (optional)
    ) else (
        echo   [✓] %%p installed
    )
)

:: Check if we have the main files needed
echo.
echo [CHECK] Verifying project files...

set MISSING_FILES=0

if not exist "main.py" (
    echo [⚠] main.py not found - will be created
    set MISSING_FILES=1
)

if not exist "build_script.py" (
    echo [⚠] build_script.py not found - will be created  
    set MISSING_FILES=1
)

if %MISSING_FILES%==1 (
    echo.
    echo [INFO] Some essential files are missing.
    echo [INFO] You need to have the following files in this directory:
    echo   • main.py (main entry point)
    echo   • build_script.py (enhanced build script)
    echo   • Core modules in the 'core' folder
    echo.
    echo [ACTION] Please ensure you have all the Python files from the system.
    echo [ACTION] Then run this script again to build the executable.
    echo.
    pause
    exit /b 1
)

:: Run the enhanced build script
echo.
echo [BUILD] Starting enhanced build process...
echo [INFO] This will create a professional portable executable
echo [INFO] Build time: 10-20 minutes depending on system performance
echo.

set /p CONFIRM="Start professional build? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo [INFO] Build cancelled by user
    pause
    exit /b 0
)

echo.
echo [BUILD] Launching enhanced build script...
python build_script.py

if %errorLevel% equ 0 (
    echo.
    echo ================================================================
    echo                   BUILD COMPLETED SUCCESSFULLY!
    echo ================================================================
    echo.
    echo [✓] Professional executable created
    echo [✓] Portable package ready for distribution
    echo [✓] All dependencies included
    echo [✓] Documentation generated
    echo.
    echo NEXT STEPS:
    echo 1. Check the "AdvancedOSINT_Professional" folder
    echo 2. Test the executable: Launch_OSINT_System.bat
    echo 3. Distribute the ZIP file to end users
    echo.
    echo FILES CREATED:
    echo • AdvancedOSINT.exe (main executable)
    echo • Launch_OSINT_System.bat (launcher)
    echo • Complete documentation (README.md)
    echo • Configuration files and examples
    echo • Distribution ZIP package
    echo.
) else (
    echo.
    echo ================================================================
    echo                     BUILD FAILED
    echo ================================================================
    echo.
    echo [✗] The build process encountered errors
    echo [INFO] Common solutions:
    echo   1. Run as administrator
    echo   2. Disable antivirus temporarily
    echo   3. Ensure stable internet connection
    echo   4. Check available disk space
    echo   5. Update Python to latest version
    echo.
    echo [INFO] Check the error messages above for specific issues
    echo.
)

echo [INFO] Build process complete
echo [INFO] Check logs above for any issues
echo.
pause