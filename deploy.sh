#!/bin/bash
# Himanshi Travels - Deployment Script for macOS/Linux
# This script sets up and deploys the travel booking application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Himanshi Travels"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
PYTHON_VERSION="3.8"
DEFAULT_PORT="8080"
DEFAULT_HOST="127.0.0.1"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Linux"
    else
        echo "Unknown"
    fi
}

# Function to install Python on macOS
install_python_macos() {
    print_status "Installing Python on macOS..."
    if command_exists brew; then
        brew install python@3.11
    else
        print_error "Homebrew not found. Please install Homebrew first:"
        print_error "Visit: https://brew.sh/"
        exit 1
    fi
}

# Function to install Python on Linux
install_python_linux() {
    print_status "Installing Python on Linux..."
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip
    elif command_exists dnf; then
        sudo dnf install -y python3 python3-pip
    elif command_exists pacman; then
        sudo pacman -S python python-pip
    else
        print_error "Package manager not supported. Please install Python 3.8+ manually."
        exit 1
    fi
}

# Function to check Python installation
check_python() {
    print_status "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Installing Python..."
        OS=$(detect_os)
        case $OS in
            "macOS")
                install_python_macos
                ;;
            "Linux")
                install_python_linux
                ;;
            *)
                print_error "Unsupported OS: $OS"
                exit 1
                ;;
        esac
        PYTHON_CMD="python3"
    fi
    
    # Check Python version
    PYTHON_VER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VER found"
    
    # Check if version is adequate
    if $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python version is adequate"
    else
        print_error "Python 3.8+ required. Current version: $PYTHON_VER"
        exit 1
    fi
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "$APP_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    pip install -r "$APP_DIR/requirements.txt"
    print_success "Dependencies installed"
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    cd "$APP_DIR"
    $PYTHON_CMD -c "
from database import init_db
init_db()
print('Database initialized successfully')
"
    print_success "Database setup complete"
}

# Function to test application
test_application() {
    print_status "Testing application..."
    
    cd "$APP_DIR"
    $PYTHON_CMD -c "
import app
print('Application imports successful')
"
    print_success "Application test passed"
}

# Function to create systemd service (Linux)
create_systemd_service() {
    if [[ "$(detect_os)" == "Linux" ]]; then
        print_status "Creating systemd service..."
        
        SERVICE_FILE="/etc/systemd/system/himanshi-travels.service"
        
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Himanshi Travels Web Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable himanshi-travels
        print_success "Systemd service created"
    fi
}

# Function to create LaunchAgent (macOS)
create_launchd_service() {
    if [[ "$(detect_os)" == "macOS" ]]; then
        print_status "Creating LaunchAgent for macOS..."
        
        PLIST_FILE="$HOME/Library/LaunchAgents/com.himanshitravels.app.plist"
        
        cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.himanshitravels.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_DIR/bin/python</string>
        <string>$APP_DIR/app.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$APP_DIR/logs/app.log</string>
    <key>StandardErrorPath</key>
    <string>$APP_DIR/logs/error.log</string>
</dict>
</plist>
EOF
        
        mkdir -p "$APP_DIR/logs"
        launchctl load "$PLIST_FILE"
        print_success "LaunchAgent created"
    fi
}

# Function to start application
start_application() {
    print_status "Starting application..."
    
    cd "$APP_DIR"
    
    # Check if port is in use
    if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 8081 is already in use"
        print_status "Killing existing process..."
        lsof -ti:8081 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start application
    source "$VENV_DIR/bin/activate"
    
    print_success "Starting $APP_NAME..."
    print_success "Application will be available at: http://$DEFAULT_HOST:8081"
    print_status "Press Ctrl+C to stop the application"
    
    "$VENV_DIR/bin/python" app.py
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install     - Install and setup the application"
    echo "  start       - Start the application"
    echo "  stop        - Stop the application"
    echo "  restart     - Restart the application"
    echo "  status      - Check application status"
    echo "  service     - Install as system service"
    echo "  logs        - Show application logs"
    echo "  help        - Show this help message"
    echo ""
}

# Function to stop application
stop_application() {
    print_status "Stopping application..."
    
    if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null ; then
        lsof -ti:8081 | xargs kill -9 2>/dev/null || true
        print_success "Application stopped"
    else
        print_warning "Application is not running"
    fi
}

# Function to check status
check_status() {
    if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null ; then
        print_success "Application is running on port 8081"
        echo "Available at: http://$DEFAULT_HOST:8081"
    else
        print_warning "Application is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$APP_DIR/logs/app.log" ]; then
        tail -f "$APP_DIR/logs/app.log"
    else
        print_warning "No log file found. Run application to generate logs."
    fi
}

# Main deployment function
deploy() {
    print_status "Starting deployment of $APP_NAME..."
    print_status "Detected OS: $(detect_os)"
    
    # Check prerequisites
    check_python
    
    # Setup environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Setup database
    setup_database
    
    # Test application
    test_application
    
    print_success "Deployment completed successfully!"
    print_status "Run './deploy.sh start' to start the application"
}

# Main script logic
case "${1:-install}" in
    "install")
        deploy
        ;;
    "start")
        start_application
        ;;
    "stop")
        stop_application
        ;;
    "restart")
        stop_application
        sleep 2
        start_application
        ;;
    "status")
        check_status
        ;;
    "service")
        create_systemd_service
        create_launchd_service
        ;;
    "logs")
        show_logs
        ;;
    "help")
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
