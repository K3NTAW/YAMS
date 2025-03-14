@echo off
echo Building YAMS Windows Application...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Install required packages
echo Installing required packages...
python -m pip install -r ..\requirements.txt

REM Build the executable
echo Building executable...
python build_windows.py

REM Check if NSIS is installed
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo NSIS is not installed or not in PATH. Installer will not be created.
    echo You can download NSIS from https://nsis.sourceforge.io/Download
    exit /b 1
)

REM Create the installer
echo Creating installer...
makensis windows_installer.nsi

echo Build completed!
echo Installer is available at: dist\YAMS_Setup.exe
