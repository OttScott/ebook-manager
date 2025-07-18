@echo off
REM Add Python Scripts to PATH for ebook-manager
REM Run this as Administrator if you want system-wide installation

echo Adding Python Scripts directory to PATH...

REM Get the Python Scripts directory dynamically
for /f "tokens=*" %%i in ('python -c "import site; import sys; import os; user_base = site.USER_BASE; python_version = f'Python{sys.version_info.major}{sys.version_info.minor}'; versioned_scripts = os.path.join(user_base, python_version, 'Scripts'); generic_scripts = os.path.join(user_base, 'Scripts'); print(versioned_scripts if os.path.exists(versioned_scripts) else generic_scripts)"') do set SCRIPTS_DIR=%%i

echo Python Scripts directory: %SCRIPTS_DIR%

REM Check if directory exists
if not exist "%SCRIPTS_DIR%" (
    echo Error: Scripts directory does not exist: %SCRIPTS_DIR%
    echo Please install ebook-manager first with: pip install -e .
    pause
    exit /b 1
)

REM Add to user PATH (current user only)
echo Adding to user PATH...
setx PATH "%PATH%;%SCRIPTS_DIR%"

if %ERRORLEVEL% == 0 (
    echo Success! Python Scripts directory added to PATH.
    echo Please restart your command prompt or PowerShell to use:
    echo   ebook-manager scan C:/Books/
    echo   ebm scan C:/Books/
) else (
    echo Error: Failed to add to PATH
    echo You can manually add this directory to your PATH:
    echo %SCRIPTS_DIR%
)

echo.
echo Press any key to exit...
pause >nul
