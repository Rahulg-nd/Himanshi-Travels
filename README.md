# Himanshi Travels - Travel Booking System

A modern Flask-based travel booking management system with support for hotels, flights, transport, and group bookings.

## 🚀 Quick Deployment

Choose your operating system and follow the instructions:

### 📱 One-Command Deployment

| OS | Command | Prerequisites |
|---|---|---|
| **Windows (PowerShell)** | `.\deploy.ps1 install; .\deploy.ps1 start` | PowerShell as Admin, Python 3.8+ |
| **Windows (Command Prompt)** | `deploy.bat install && deploy.bat start` | CMD as Admin, Python 3.8+ |
| **macOS/Linux** | `./deploy.sh install && ./deploy.sh start` | Python 3.8+, chmod +x deploy.sh |
| **Docker (All OS)** | `docker-compose up --build` | Docker Desktop installed |

### 🪟 Windows Quick Start

**Complete setup from scratch on Windows:**

1. **Download and Install Python**
   - Go to [python.org](https://www.python.org/downloads/windows/)
   - Download Python 3.11+ installer
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Download the Application**
   ```cmd
   # Option A: Using Git (if installed)
   git clone <repository-url>
   cd Himanshi-Travels
   
   # Option B: Download ZIP, extract, then:
   cd "C:\path\to\extracted\Himanshi-Travels"
   ```

3. **Deploy and Run**
   ```powershell
   # Open PowerShell as Administrator
   # Navigate to project folder
   cd "C:\path\to\Himanshi-Travels"
   
   # Set execution policy (first time only)
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # Deploy and start
   .\deploy.ps1 install
   .\deploy.ps1 start
   ```

4. **Access Application**
   - Open browser: `http://127.0.0.1:8080`

**That's it! Your travel booking system is now running on Windows.**

---

## 📋 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application, additional space for database and PDFs
- **Network**: Port 8080 (configurable)

---

## 🔧 Deployment Options

### Option 1: Native Deployment (Recommended)

#### macOS & Linux

```bash
# Make script executable (first time only)
chmod +x deploy.sh

# Install and setup
./deploy.sh install

# Start application
./deploy.sh start

# Other commands
./deploy.sh stop          # Stop application
./deploy.sh restart       # Restart application
./deploy.sh status        # Check status
./deploy.sh service       # Install as system service
./deploy.sh logs          # View logs
```

#### Windows Deployment

##### Prerequisites for Windows

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/windows/)
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Check "Install pip" option
   - Verify installation: Open Command Prompt and run:
   ```cmd
   python --version
   pip --version
   ```

2. **Install Git (Optional but recommended)**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use for cloning the repository

3. **Download/Clone the Application**
   ```cmd
   # Option 1: Using Git
   git clone <repository-url>
   cd HimanshiTravels
   
   # Option 2: Download ZIP and extract
   # Navigate to extracted folder in Command Prompt
   cd path\to\Himanshi-Travels
   ```

##### Method 1: PowerShell (Recommended)

**Step 1: Open PowerShell as Administrator**
- Press `Win + X` and select "Windows PowerShell (Admin)"
- Or search "PowerShell" in Start menu, right-click and "Run as administrator"

**Step 2: Navigate to Project Directory**
```powershell
cd "C:\path\to\Himanshi-Travels"
```

**Step 3: Allow Script Execution (First time only)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Step 4: Deploy Application**
```powershell
# Install and setup
.\deploy.ps1 install

# Start application
.\deploy.ps1 start

# Other commands
.\deploy.ps1 stop          # Stop application
.\deploy.ps1 restart       # Restart application
.\deploy.ps1 status        # Check status
.\deploy.ps1 service       # Install as Windows service (requires admin)
.\deploy.ps1 logs          # View logs
```

**Step 5: Access Application**
- Open browser and go to: `http://127.0.0.1:8080`

##### Method 2: Command Prompt

**Step 1: Open Command Prompt as Administrator**
- Press `Win + R`, type `cmd`, press `Ctrl + Shift + Enter`
- Or search "Command Prompt" in Start menu, right-click and "Run as administrator"

**Step 2: Navigate to Project Directory**
```cmd
cd "C:\path\to\Himanshi-Travels"
```

**Step 3: Deploy Application**
```cmd
# Install and setup
deploy.bat install

# Start application
deploy.bat start

# Other commands
deploy.bat stop          REM Stop application
deploy.bat restart       REM Restart application
deploy.bat status        REM Check status
deploy.bat logs          REM View logs
```

##### Method 3: Manual Windows Installation

**Step 1: Create Virtual Environment**
```cmd
# Navigate to project folder
cd "C:\path\to\Himanshi-Travels"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# You should see (.venv) in your command prompt
```

**Step 2: Install Dependencies**
```cmd
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**Step 3: Initialize Database**
```cmd
python -c "from database import init_db; init_db()"
```

**Step 4: Run Application**
```cmd
python app.py
```

**Step 5: Access Application**
- Open browser and go to: `http://127.0.0.1:8080`

##### Windows Service Installation (Production)

**For production deployment, install as Windows Service:**

1. **Open PowerShell as Administrator**
2. **Navigate to project directory**
3. **Install as service:**
```powershell
.\deploy.ps1 service
```

4. **Start the service:**
```cmd
sc start HimanshiTravels
```

5. **Enable auto-start:**
```cmd
sc config HimanshiTravels start= auto
```

6. **Check service status:**
```cmd
sc query HimanshiTravels
```

### Option 2: Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

### Option 3: Azure Deployment

This application includes Azure deployment templates for easy cloud deployment:

```bash
# Prerequisites: Azure CLI and Azure Developer CLI (azd)
az login
azd init
azd up
```

The application includes:
- **Infrastructure as Code**: Bicep templates in `/infra` directory
- **Azure Container Apps**: Scalable containerized deployment
- **Azure Configuration**: `azure.yaml` for azd deployment
- **Production Ready**: Configured for Azure cloud environment

### Option 4: Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

1. **Install Python 3.8+**
   - macOS: `brew install python@3.11` or download from python.org
   - Linux: `sudo apt install python3 python3-pip python3-venv` (Ubuntu/Debian)
   - Windows: Download from [python.org](https://www.python.org/downloads/)

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   
   # Activate virtual environment
   # macOS/Linux:
   source .venv/bin/activate
   
   # Windows:
   .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

5. **Run Application**
   ```bash
   python app.py
   ```

</details>

---

## 🌐 Accessing the Application

Once deployed, access the application at:
- **Local**: http://127.0.0.1:8080
- **Network**: http://YOUR_IP_ADDRESS:8080

### Default Pages
- **Main Booking Form**: http://127.0.0.1:8080/
- **Bookings Management**: http://127.0.0.1:8080/bookings
- **Test Autocomplete**: http://127.0.0.1:8080/test_autocomplete

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# config.py
DEFAULT_PAGE_SIZE = 10          # Bookings per page
GST_RATE = 0.18                # GST rate (18%)
DEFAULT_HOST = "127.0.0.1"     # Host address
DEFAULT_PORT = 8080            # Port number
```

---

## 🆕 Recent Improvements & Code Cleanup

### Latest Updates (v2.0)
- ✅ **Fixed Group Booking Creation**: Resolved issues with group booking form submission and backend detection
- ✅ **Enhanced Amount Display**: Fixed null safety and formatting in booking history
- ✅ **Terminology Consistency**: Standardized on "customer" terminology throughout the application
- ✅ **Code Cleanup**: Removed unused files, debug code, and outdated documentation
- ✅ **Modular Architecture**: Improved code organization with proper separation of concerns
- ✅ **Better Validation**: Enhanced form validation for both single and group bookings
- ✅ **UI/UX Improvements**: Cleaner interface with better error handling and notifications
- ✅ **Azure Ready**: Infrastructure as Code (Bicep) templates for Azure deployment

### Removed Files
- Removed empty `city_data.py`
- Cleaned up backup template files (`bookings_backup.html`, `bookings_new.html`, `form_new.html`)
- Removed unused `pagination.js` (functions moved inline)
- Deleted test and debug files from previous development iterations

### Code Quality Improvements
- Enhanced error handling and validation
- Consistent naming conventions
- Improved documentation and comments
- Better separation of frontend and backend logic
- Optimized database operations

---

## 🛡️ Production Deployment

### As System Service

#### Linux (systemd)
```bash
./deploy.sh service
sudo systemctl start himanshi-travels
sudo systemctl enable himanshi-travels
```

#### macOS (launchd)
```bash
./deploy.sh service
```

#### Windows Service
```powershell
# Run as Administrator
.\deploy.ps1 service
sc start HimanshiTravels
```

### Reverse Proxy Setup (Optional)

<details>
<summary>Nginx Configuration</summary>

Create `/etc/nginx/sites-available/himanshi-travels`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/himanshi-travels /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

</details>

---

## 📊 Project Structure

```
Himanshi-Travels/
├── 🚀 deploy.sh              # macOS/Linux deployment script
├── 🚀 deploy.ps1             # Windows PowerShell script
├── 🚀 deploy.bat             # Windows batch script
├── 🐳 Dockerfile             # Docker container definition
├── 🐳 docker-compose.yml     # Docker Compose configuration
├── 📱 app.py                 # Main application entry point
├── ⚙️ config.py              # Configuration settings
├── 🛣️ routes.py              # Flask routes and endpoints
├── 🗄️ database.py           # Database operations and models
├── 🏢 booking_logic.py       # Business logic for bookings
├── ✅ validators.py          # Input validation functions
├── 🔧 utils.py               # Utility functions
├── 📄 pdf_generator.py       # PDF invoice generation
├── 🌐 external_api_service.py # External API integrations
├── ☁️ azure.yaml            # Azure deployment configuration
├── 📋 requirements.txt       # Python dependencies
├── 🗃️ db.sqlite3            # SQLite database
├── 📁 bills/                # Generated PDF invoices
├── 📁 infra/                # Infrastructure as Code (Bicep)
├── 📁 static/               # Static assets (CSS, JS, images)
│   ├── 🎨 css/              # Modular stylesheets
│   ├── ⚡ js/               # Modular JavaScript files
│   └── 🖼️ images/           # Images and logos
└── 📁 templates/            # Jinja2 templates
    ├── 📝 form.html         # Main booking form
    ├── 📊 bookings.html     # Bookings management page
    └── 🧩 components/       # Reusable template components
```

---

## ✨ Features

- ✅ **Single & Group Bookings**: Support for individual and group bookings with improved form validation
- ✅ **Multiple Booking Types**: Hotels, Flights, Trains, Buses, Transport, Tour Packages
- ✅ **International Support**: City/country autocomplete with external API integration
- ✅ **PDF Generation**: Automatic invoice generation with proper formatting
- ✅ **Search & Filter**: Advanced booking search and filtering with improved pagination
- ✅ **Responsive Design**: Mobile-friendly interface with consistent customer terminology
- ✅ **GST Calculation**: Automatic tax calculation with proper amount display
- ✅ **Edit Bookings**: Full CRUD operations for bookings with enhanced validation
- ✅ **Modular Architecture**: Clean, maintainable code structure with proper separation of concerns
- ✅ **Cross-Platform**: Runs on Windows, macOS, and Linux
- ✅ **Enhanced UI/UX**: Improved booking forms, better error handling, and notification system

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main booking form |
| `POST` | `/` | Create new booking |
| `GET` | `/bookings` | Bookings management page |
| `GET` | `/api/search_bookings` | Search bookings with filters |
| `GET` | `/get_booking/{id}` | Get booking details |
| `POST` | `/update_booking/{id}` | Update existing booking |
| `POST` | `/delete_booking/{id}` | Delete booking |
| `GET` | `/invoice/{id}` | Generate PDF invoice |
| `GET` | `/api/cities` | City autocomplete suggestions |
| `GET` | `/api/countries` | Country autocomplete suggestions |

---

## 🔍 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find and kill process using port 8080
# macOS/Linux:
lsof -ti:8080 | xargs kill -9

# Windows:
netstat -ano | findstr :8080
taskkill /F /PID <PID>
```

**Python not found:**
- Ensure Python 3.8+ is installed and in PATH
- On Windows, try `py` instead of `python`

**Permission denied (Linux/macOS):**
```bash
chmod +x deploy.sh
```

**Virtual environment issues:**
```bash
# Remove and recreate
rm -rf .venv
./deploy.sh install
```

### Windows-Specific Troubleshooting

**PowerShell Execution Policy Error:**
```powershell
# If you get "execution of scripts is disabled" error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python command not recognized:**
```cmd
# Try these alternatives:
python --version     # If this fails, try:
py --version         # or
python3 --version    # or add Python to PATH manually
```

**Path with spaces issues:**
```cmd
# Always use quotes for paths with spaces
cd "C:\Program Files\HimanshiTravels"
```

**Virtual environment activation fails:**
```cmd
# If .venv\Scripts\activate doesn't work, try:
.venv\Scripts\activate.bat
# or
.venv\Scripts\Activate.ps1
```

**Permission denied errors:**
- Run Command Prompt or PowerShell as Administrator
- Ensure you have write permissions to the installation directory

**Port 8080 blocked by firewall:**
```cmd
# Allow port 8080 through Windows Firewall
netsh advfirewall firewall add rule name="HimanshiTravels" dir=in action=allow protocol=TCP localport=8080
```

**Service installation fails:**
```powershell
# Make sure you're running PowerShell as Administrator
# Check if service already exists:
Get-Service -Name "HimanshiTravels" -ErrorAction SilentlyContinue
# Remove existing service if needed:
sc delete HimanshiTravels
```

**Dependencies installation fails:**
```cmd
# Update pip first
python -m pip install --upgrade pip
# Try installing with --user flag
pip install --user -r requirements.txt
# or force reinstall
pip install --force-reinstall -r requirements.txt
```

**Database initialization errors:**
```cmd
# Ensure you're in the correct directory
cd "C:\path\to\Himanshi-Travels"
# Check if db.sqlite3 already exists
dir db.sqlite3
# If it exists and causing issues, delete it:
del db.sqlite3
# Then reinitialize:
python -c "from database import init_db; init_db()"
```

### Logs Location

- **Linux/macOS**: `./logs/app.log`
- **Windows**: `.\logs\app.log`
- **Docker**: `docker-compose logs`

---

## 🚀 Quick Start Examples

### Windows Development Setup
```powershell
# PowerShell method (Recommended for Windows)
git clone <repository>
cd Himanshi-Travels
.\deploy.ps1 install
.\deploy.ps1 start
```

```cmd
# Command Prompt method
git clone <repository>
cd Himanshi-Travels
deploy.bat install
deploy.bat start
```

### Windows Production Deployment
```powershell
# PowerShell as Administrator
cd "C:\path\to\Himanshi-Travels"
.\deploy.ps1 install
.\deploy.ps1 service
sc start HimanshiTravels
sc config HimanshiTravels start= auto
```

### Development Setup (macOS/Linux)
```bash
git clone <repository>
cd Himanshi-Travels
./deploy.sh install
./deploy.sh start
```

### Production Deployment (macOS/Linux)
```bash
./deploy.sh install
./deploy.sh service
sudo systemctl start himanshi-travels
```

### Docker Development (All Platforms)
```bash
docker-compose up --build
```

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review application logs
3. Ensure all requirements are met
4. Verify network connectivity for API features

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.
