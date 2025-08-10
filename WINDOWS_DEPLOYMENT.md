# Windows Deployment Guide

## Using deploy.ps1

The `deploy.ps1` script is a PowerShell script for deploying the Himanshi Travels application on Windows systems.

### Prerequisites

1. **Windows 10/11** or **Windows Server 2016+**
2. **PowerShell 5.1+** or **PowerShell Core 7+**
3. **Python 3.8+** (will be installed automatically if missing)

### Initial Setup

1. **Enable PowerShell Script Execution** (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Navigate to the project directory** in PowerShell:
   ```powershell
   cd "C:\path\to\Himanshi-Travels"
   ```

### Usage

#### First Time Installation
```powershell
.\deploy.ps1 install
```
This will:
- Check and install Python if needed
- Create a virtual environment
- Install all dependencies
- Initialize the database
- Test the application

#### Start the Application
```powershell
.\deploy.ps1 start
```

#### Stop the Application
```powershell
.\deploy.ps1 stop
```

#### Restart the Application
```powershell
.\deploy.ps1 restart
```

#### Check Status
```powershell
.\deploy.ps1 status
```

#### Install as Windows Service (requires admin)
```powershell
.\deploy.ps1 service
```

#### View Help
```powershell
.\deploy.ps1 help
```

### Access the Application

After starting, the application will be available at:
- **URL**: http://127.0.0.1:8081
- **Port**: 8081

### Troubleshooting

1. **Execution Policy Error**:
   ```
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Python Not Found**:
   - The script will try to install Python automatically
   - If this fails, install Python manually from https://python.org

3. **Port Already in Use**:
   - The script will automatically try to stop existing processes
   - You can manually stop with `.\deploy.ps1 stop`

4. **Permission Issues**:
   - Run PowerShell as Administrator for service installation
   - Ensure you have write permissions to the project directory

### File Structure Created

After installation, you'll have:
```
Himanshi-Travels/
├── .venv/                 # Virtual environment
├── app.py                 # Main application
├── deploy.ps1            # This deployment script
├── requirements.txt       # Python dependencies
├── db.sqlite3            # SQLite database
└── ...other files
```

### Manual Installation (Alternative)

If the script doesn't work, you can install manually:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Start application
python app.py
```
