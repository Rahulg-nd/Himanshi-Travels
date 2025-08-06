# Himanshi Travels - Deployment Script for Windows
# This PowerShell script sets up and deploys the travel booking application

param(
    [Parameter(Position=0)]
    [ValidateSet("install", "start", "stop", "restart", "status", "service", "logs", "help")]
    [string]$Action = "install"
)

# Configuration
$APP_NAME = "Himanshi Travels"
$APP_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $APP_DIR ".venv"
$DEFAULT_PORT = "8081"
$DEFAULT_HOST = "127.0.0.1"
$PYTHON_MIN_VERSION = [Version]"3.8.0"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Function to check admin privileges
function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Python
function Install-Python {
    Write-Status "Installing Python..."
    
    if (Test-Command "winget") {
        Write-Status "Using winget to install Python..."
        winget install Python.Python.3.11
    } elseif (Test-Command "choco") {
        Write-Status "Using Chocolatey to install Python..."
        choco install python -y
    } else {
        Write-Error "Neither winget nor Chocolatey found."
        Write-Error "Please install Python manually from: https://www.python.org/downloads/"
        Write-Error "Or install Chocolatey from: https://chocolatey.org/"
        exit 1
    }
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Function to check Python installation
function Test-PythonInstallation {
    Write-Status "Checking Python installation..."
    
    $pythonCmd = $null
    if (Test-Command "python") {
        $pythonCmd = "python"
    } elseif (Test-Command "python3") {
        $pythonCmd = "python3"
    } elseif (Test-Command "py") {
        $pythonCmd = "py"
    }
    
    if (-not $pythonCmd) {
        Write-Error "Python not found. Installing Python..."
        Install-Python
        
        # Re-check after installation
        if (Test-Command "python") {
            $pythonCmd = "python"
        } elseif (Test-Command "py") {
            $pythonCmd = "py"
        } else {
            Write-Error "Python installation failed or not in PATH"
            exit 1
        }
    }
    
    # Check Python version
    try {
        $versionOutput = & $pythonCmd --version 2>&1
        $versionMatch = $versionOutput -match "Python (\d+\.\d+\.\d+)"
        if ($versionMatch) {
            $pythonVersion = [Version]$matches[1]
            Write-Success "Python $pythonVersion found"
            
            if ($pythonVersion -ge $PYTHON_MIN_VERSION) {
                Write-Success "Python version is adequate"
                return $pythonCmd
            } else {
                Write-Error "Python 3.8+ required. Current version: $pythonVersion"
                exit 1
            }
        } else {
            Write-Error "Could not determine Python version"
            exit 1
        }
    } catch {
        Write-Error "Error checking Python version: $_"
        exit 1
    }
}

# Function to setup virtual environment
function Set-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Status "Setting up virtual environment..."
    
    if (Test-Path $VENV_DIR) {
        Write-Warning "Virtual environment already exists. Removing..."
        Remove-Item -Recurse -Force $VENV_DIR
    }
    
    & $PythonCmd -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    Write-Success "Virtual environment created"
    
    # Activate virtual environment
    $activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        . $activateScript
        Write-Success "Virtual environment activated"
    } else {
        Write-Error "Could not find activation script"
        exit 1
    }
    
    # Upgrade pip
    python -m pip install --upgrade pip
    Write-Success "pip upgraded"
}

# Function to install dependencies
function Install-Dependencies {
    Write-Status "Installing Python dependencies..."
    
    $requirementsFile = Join-Path $APP_DIR "requirements.txt"
    if (-not (Test-Path $requirementsFile)) {
        Write-Error "requirements.txt not found!"
        exit 1
    }
    
    pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
    Write-Success "Dependencies installed"
}

# Function to setup database
function Set-Database {
    Write-Status "Setting up database..."
    
    Set-Location $APP_DIR
    & (Join-Path $VENV_DIR "Scripts\python.exe") -c @"
from database import init_db
init_db()
print('Database initialized successfully')
"@
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Database setup failed"
        exit 1
    }
    Write-Success "Database setup complete"
}

# Function to test application
function Test-Application {
    Write-Status "Testing application..."
    
    Set-Location $APP_DIR
    & (Join-Path $VENV_DIR "Scripts\python.exe") -c @"
import app
print('Application imports successful')
"@
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Application test failed"
        exit 1
    }
    Write-Success "Application test passed"
}

# Function to create Windows service
function New-WindowsService {
    if (-not (Test-AdminPrivileges)) {
        Write-Error "Administrator privileges required to create Windows service"
        Write-Status "Run PowerShell as Administrator and try again"
        return
    }
    
    Write-Status "Creating Windows service..."
    
    $serviceName = "HimanshiTravels"
    $pythonExe = Join-Path $VENV_DIR "Scripts\python.exe"
    $appScript = Join-Path $APP_DIR "app.py"
    
    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Status "Service already exists. Removing..."
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        sc.exe delete $serviceName
    }
    
    # Create batch file to run the application
    $batchFile = Join-Path $APP_DIR "start_service.bat"
    @"
@echo off
cd /d "$APP_DIR"
"$pythonExe" "$appScript"
"@ | Out-File -FilePath $batchFile -Encoding ASCII
    
    # Create the service
    sc.exe create $serviceName binPath="$batchFile" start=auto DisplayName="Himanshi Travels Web Application"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Windows service created successfully"
        Write-Status "Service name: $serviceName"
        Write-Status "Use 'sc start $serviceName' to start the service"
    } else {
        Write-Error "Failed to create Windows service"
    }
}

# Function to check if port is in use
function Test-PortInUse {
    param([int]$Port)
    
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet
        return $connection
    } catch {
        return $false
    }
}

# Function to start application
function Start-Application {
    Write-Status "Starting application..."
    
    Set-Location $APP_DIR
    
    # Check if port is in use
    if (Test-PortInUse -Port $DEFAULT_PORT) {
        Write-Warning "Port $DEFAULT_PORT is already in use"
        Write-Status "Attempting to stop existing process..."
        Stop-Application
        Start-Sleep -Seconds 2
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        . $activateScript
    } else {
        Write-Error "Virtual environment not found. Run installation first."
        exit 1
    }
    
    Write-Success "Starting $APP_NAME..."
    Write-Success "Application will be available at: http://${DEFAULT_HOST}:${DEFAULT_PORT}"
    Write-Status "Press Ctrl+C to stop the application"
    
    & (Join-Path $VENV_DIR "Scripts\python.exe") app.py
}

# Function to stop application
function Stop-Application {
    Write-Status "Stopping application..."
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $DEFAULT_PORT -ErrorAction SilentlyContinue | 
                    Select-Object -ExpandProperty OwningProcess | 
                    ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }
        
        if ($processes) {
            $processes | Stop-Process -Force
            Write-Success "Application stopped"
        } else {
            Write-Warning "Application is not running"
        }
    } catch {
        Write-Warning "Could not stop application: $_"
    }
}

# Function to check status
function Get-ApplicationStatus {
    if (Test-PortInUse -Port $DEFAULT_PORT) {
        Write-Success "Application is running on port $DEFAULT_PORT"
        Write-Host "Available at: http://${DEFAULT_HOST}:${DEFAULT_PORT}"
    } else {
        Write-Warning "Application is not running"
    }
}

# Function to show logs
function Show-Logs {
    $logFile = Join-Path $APP_DIR "logs\app.log"
    if (Test-Path $logFile) {
        Get-Content $logFile -Wait -Tail 50
    } else {
        Write-Warning "No log file found. Run application to generate logs."
    }
}

# Function to show usage
function Show-Usage {
    Write-Host @"
Usage: .\deploy.ps1 [ACTION]

Actions:
  install     - Install and setup the application
  start       - Start the application
  stop        - Stop the application
  restart     - Restart the application
  status      - Check application status
  service     - Install as Windows service (requires admin)
  logs        - Show application logs
  help        - Show this help message

Examples:
  .\deploy.ps1 install
  .\deploy.ps1 start
  .\deploy.ps1 service
"@
}

# Main deployment function
function Invoke-Deployment {
    Write-Status "Starting deployment of $APP_NAME on Windows..."
    
    # Check prerequisites
    $pythonCmd = Test-PythonInstallation
    
    # Setup environment
    Set-VirtualEnvironment -PythonCmd $pythonCmd
    
    # Install dependencies
    Install-Dependencies
    
    # Setup database
    Set-Database
    
    # Test application
    Test-Application
    
    Write-Success "Deployment completed successfully!"
    Write-Status "Run '.\deploy.ps1 start' to start the application"
}

# Main script logic
switch ($Action) {
    "install" {
        Invoke-Deployment
    }
    "start" {
        Start-Application
    }
    "stop" {
        Stop-Application
    }
    "restart" {
        Stop-Application
        Start-Sleep -Seconds 2
        Start-Application
    }
    "status" {
        Get-ApplicationStatus
    }
    "service" {
        New-WindowsService
    }
    "logs" {
        Show-Logs
    }
    "help" {
        Show-Usage
    }
    default {
        Write-Error "Unknown action: $Action"
        Show-Usage
        exit 1
    }
}
