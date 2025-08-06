@echo off
:: Himanshi Travels - Deployment Script for Windows (Batch)
:: Simple batch script for Windows deployment

setlocal enabledelayedexpansion

:: Configuration
set APP_NAME=Himanshi Travels
set APP_DIR=%~dp0
set VENV_DIR=%APP_DIR%.venv
set DEFAULT_PORT=8080
set DEFAULT_HOST=127.0.0.1

:: Colors (if supported)
set "ESC="

:: Get command line argument
set ACTION=%1
if "%ACTION%"=="" set ACTION=install

echo.
echo ================================================
echo    %APP_NAME% - Windows Deployment Script
echo ================================================
echo.

goto %ACTION% 2>nul
echo Error: Unknown action '%ACTION%'
goto usage

:install
echo [INFO] Starting installation...
call :check_python
call :setup_venv
call :install_deps
call :setup_db
call :test_app
echo.
echo [SUCCESS] Installation completed successfully!
echo [INFO] Run 'deploy.bat start' to start the application
pause
goto :eof

:start
echo [INFO] Starting %APP_NAME%...
call :check_venv
call :check_port
cd /d "%APP_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
echo [SUCCESS] Application will be available at: http://%DEFAULT_HOST%:%DEFAULT_PORT%
echo [INFO] Press Ctrl+C to stop the application
python app.py
goto :eof

:stop
echo [INFO] Stopping application...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%DEFAULT_PORT%') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [SUCCESS] Application stopped
pause
goto :eof

:restart
call :stop
timeout /t 2 /nobreak >nul
call :start
goto :eof

:status
echo [INFO] Checking application status...
netstat -an | findstr :%DEFAULT_PORT% >nul
if %errorlevel%==0 (
    echo [SUCCESS] Application is running on port %DEFAULT_PORT%
    echo Available at: http://%DEFAULT_HOST%:%DEFAULT_PORT%
) else (
    echo [WARNING] Application is not running
)
pause
goto :eof

:logs
echo [INFO] Showing application logs...
if exist "%APP_DIR%logs\app.log" (
    type "%APP_DIR%logs\app.log"
) else (
    echo [WARNING] No log file found
)
pause
goto :eof

:service
echo [INFO] Installing Windows service...
echo [WARNING] This requires administrator privileges
echo [INFO] Please run as administrator or use deploy.ps1 for service installation
pause
goto :eof

:help
:usage
echo.
echo Usage: deploy.bat [ACTION]
echo.
echo Actions:
echo   install     - Install and setup the application
echo   start       - Start the application
echo   stop        - Stop the application
echo   restart     - Restart the application
echo   status      - Check application status
echo   service     - Install as Windows service
echo   logs        - Show application logs
echo   help        - Show this help message
echo.
echo Examples:
echo   deploy.bat install
echo   deploy.bat start
echo   deploy.bat stop
echo.
pause
goto :eof

:: Helper functions
:check_python
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo [INFO] Please install Python from: https://www.python.org/downloads/
    echo [INFO] Make sure to add Python to PATH during installation
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found
goto :eof

:setup_venv
echo [INFO] Setting up virtual environment...
if exist "%VENV_DIR%" (
    echo [WARNING] Removing existing virtual environment...
    rmdir /s /q "%VENV_DIR%"
)
python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
echo [SUCCESS] Virtual environment created and activated
goto :eof

:install_deps
echo [INFO] Installing dependencies...
if not exist "%APP_DIR%requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)
pip install -r "%APP_DIR%requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
goto :eof

:setup_db
echo [INFO] Setting up database...
cd /d "%APP_DIR%"
python -c "from database import init_db; init_db(); print('Database initialized successfully')"
if %errorlevel% neq 0 (
    echo [ERROR] Database setup failed
    pause
    exit /b 1
)
echo [SUCCESS] Database setup complete
goto :eof

:test_app
echo [INFO] Testing application...
cd /d "%APP_DIR%"
python -c "import app; print('Application imports successful')"
if %errorlevel% neq 0 (
    echo [ERROR] Application test failed
    pause
    exit /b 1
)
echo [SUCCESS] Application test passed
goto :eof

:check_venv
if not exist "%VENV_DIR%" (
    echo [ERROR] Virtual environment not found!
    echo [INFO] Run 'deploy.bat install' first
    pause
    exit /b 1
)
goto :eof

:check_port
netstat -an | findstr :%DEFAULT_PORT% >nul
if %errorlevel%==0 (
    echo [WARNING] Port %DEFAULT_PORT% is already in use
    echo [INFO] Stopping existing process...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%DEFAULT_PORT%') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)
goto :eof
