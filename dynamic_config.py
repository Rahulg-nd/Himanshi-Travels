"""
Dynamic configuration management for Himanshi Travels application
Reads configuration from database with fallback to static values
"""

from typing import Any, Union
import logging

logger = logging.getLogger(__name__)

# Static fallback configuration (will be overridden by database values)
DATABASE_FILE = 'db.sqlite3'
DEFAULT_PAGE_SIZE = 25

class ConfigManager:
    """Dynamic configuration manager that reads from database"""
    
    def __init__(self):
        self._cache = {}
        self._initialized = False
    
    def _init_from_db(self):
        """Initialize configuration from database"""
        if self._initialized:
            return
            
        try:
            # Import database functions locally to avoid circular import
            import database
            configs = database.get_all_config()
            
            for config in configs:
                key = config['config_key']
                value = config['config_value']
                config_type = config['config_type']
                
                # Convert values based on type
                if config_type == 'boolean':
                    self._cache[key] = value.lower() == 'true'
                elif config_type == 'number':
                    try:
                        # Try int first, then float
                        if '.' in value:
                            self._cache[key] = float(value)
                        else:
                            self._cache[key] = int(value)
                    except ValueError:
                        self._cache[key] = value
                else:
                    self._cache[key] = value
            
            self._initialized = True
            logger.info(f"Loaded {len(self._cache)} configuration values from database")
            
        except Exception as e:
            logger.warning(f"Could not load config from database: {e}")
            self._load_static_fallback()
    
    def _load_static_fallback(self):
        """Load static fallback configuration"""
        self._cache = {
            # Business configuration
            'gst_percent': 5,
            'agency_name': "Himanshi Travels",
            'agency_tagline': "Your Journey, Our Passion",
            'gstin': "29ABCDE1234F2Z5",
            'agency_address': "123 Travel Street, Adventure City, State 123456",
            'agency_phone': "+91 98765 43210",
            'agency_email': "info@himanshitravels.com",
            
            # WhatsApp configuration
            'whatsapp_enabled': True,
            'whatsapp_send_on_booking': True,
            'whatsapp_send_to_group_customers': False,
            'whatsapp_provider': 'mock',
            
            # Twilio configuration
            'twilio_account_sid': 'your_twilio_account_sid',
            'twilio_auth_token': 'your_twilio_auth_token',
            'twilio_whatsapp_number': '+14155238886',
            
            # Green API configuration
            'green_api_instance_id': '',
            'green_api_token': '',
            
            # Application settings
            'app_debug': False,
            'app_port': 8081,
            'backup_enabled': True,
            'backup_frequency': 'daily',
            
            # Email configuration
            'email_enabled': False,
            'smtp_server': '',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'smtp_use_tls': True,
            'from_email': '',
        }
        self._initialized = True
        logger.info("Loaded static fallback configuration")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        if not self._initialized:
            self._init_from_db()
        
        return self._cache.get(key, default)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_str(self, key: str, default: str = '') -> str:
        """Get string configuration value"""
        value = self.get(key, default)
        return str(value) if value is not None else default
    
    def refresh(self):
        """Refresh configuration from database"""
        self._cache.clear()
        self._initialized = False
        self._init_from_db()
        logger.info("Configuration refreshed from database")
    
    def get_category(self, category: str) -> dict:
        """Get all configurations for a specific category"""
        if not self._initialized:
            self._init_from_db()
        
        try:
            # Import database functions locally to avoid circular import
            import database
            configs = database.get_all_config(category)
            
            result = {}
            for config in configs:
                key = config['config_key']
                value = config['config_value']
                config_type = config['config_type']
                
                # Convert values based on type
                if config_type == 'boolean':
                    result[key] = value.lower() == 'true'
                elif config_type == 'number':
                    try:
                        if '.' in value:
                            result[key] = float(value)
                        else:
                            result[key] = int(value)
                    except ValueError:
                        result[key] = value
                else:
                    result[key] = value
            
            return result
        except Exception as e:
            logger.warning(f"Could not get category {category} from database: {e}")
            return {}

# Global configuration manager instance
config = ConfigManager()

# Backward compatibility - expose as module-level functions
def _get_config_property(key: str, default: Any = None):
    """Helper to get configuration as module property"""
    return config.get(key, default)

# Business configuration functions
def gst_percent():
    return config.get_float('gst_percent', 5.0)

def agency_name():
    return config.get_str('agency_name', 'Himanshi Travels')

def agency_tagline():
    return config.get_str('agency_tagline', 'Your Journey, Our Passion')

def gstin():
    return config.get_str('gstin', '29ABCDE1234F2Z5')

def agency_address():
    return config.get_str('agency_address', '123 Travel Street, Adventure City, State 123456')

def agency_phone():
    return config.get_str('agency_phone', '+91 98765 43210')

def agency_email():
    return config.get_str('agency_email', 'info@himanshitravels.com')

# WhatsApp configuration functions
def whatsapp_enabled():
    return config.get_bool('whatsapp_enabled', True)

def whatsapp_send_on_booking():
    return config.get_bool('whatsapp_send_on_booking', True)

def whatsapp_send_to_group_customers():
    return config.get_bool('whatsapp_send_to_group_customers', False)

def whatsapp_provider():
    return config.get_str('whatsapp_provider', 'mock')

# Twilio configuration functions
def twilio_account_sid():
    return config.get_str('twilio_account_sid', '')

def twilio_auth_token():
    return config.get_str('twilio_auth_token', '')

def twilio_whatsapp_number():
    return config.get_str('twilio_whatsapp_number', '+14155238886')

# Green API configuration functions
def green_api_instance_id():
    return config.get_str('green_api_instance_id', '')

def green_api_token():
    return config.get_str('green_api_token', '')

# Application settings functions
def app_debug():
    return config.get_bool('app_debug', False)

def app_port():
    return config.get_int('app_port', 8081)

def backup_enabled():
    return config.get_bool('backup_enabled', True)

def backup_frequency():
    return config.get_str('backup_frequency', 'daily')

# Email configuration functions
def email_enabled():
    return config.get_bool('email_enabled', False)

def smtp_server():
    return config.get_str('smtp_server', '')

def smtp_port():
    return config.get_int('smtp_port', 587)

def smtp_username():
    return config.get_str('smtp_username', '')

def smtp_password():
    return config.get_str('smtp_password', '')

def smtp_use_tls():
    return config.get_bool('smtp_use_tls', True)

def from_email():
    return config.get_str('from_email', '')

# Legacy constants for compatibility (keeping DATABASE_FILE separate as it's needed early)
DATABASE_FILE = 'db.sqlite3'
DEFAULT_PAGE_SIZE = 25

# Legacy constants for backward compatibility - these will be function calls (delayed loading)
def _get_module_constants():
    """Get module constants with delayed loading"""
    global GST_PERCENT, AGENCY_NAME, AGENCY_TAGLINE, GSTIN, AGENCY_ADDRESS
    global AGENCY_PHONE, AGENCY_EMAIL, WHATSAPP_ENABLED, WHATSAPP_SEND_ON_BOOKING
    global WHATSAPP_SEND_TO_GROUP_CUSTOMERS, WHATSAPP_PROVIDER, TWILIO_ACCOUNT_SID
    global TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, GREEN_API_INSTANCE_ID, GREEN_API_TOKEN
    global APP_DEBUG, APP_PORT, BACKUP_ENABLED, BACKUP_FREQUENCY, EMAIL_ENABLED
    global SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, LOGO_PATH, BILLS_DIRECTORY
    
    # Only initialize if not already done
    if 'GST_PERCENT' not in globals():
        GST_PERCENT = gst_percent()
        AGENCY_NAME = agency_name()
        AGENCY_TAGLINE = agency_tagline()
        GSTIN = gstin()
        AGENCY_ADDRESS = agency_address()
        AGENCY_PHONE = agency_phone()
        AGENCY_EMAIL = agency_email()
        WHATSAPP_ENABLED = whatsapp_enabled()
        WHATSAPP_SEND_ON_BOOKING = whatsapp_send_on_booking()
        WHATSAPP_SEND_TO_GROUP_CUSTOMERS = whatsapp_send_to_group_customers()
        WHATSAPP_PROVIDER = whatsapp_provider()
        TWILIO_ACCOUNT_SID = twilio_account_sid()
        TWILIO_AUTH_TOKEN = twilio_auth_token()
        TWILIO_WHATSAPP_NUMBER = twilio_whatsapp_number()
        GREEN_API_INSTANCE_ID = green_api_instance_id()
        GREEN_API_TOKEN = green_api_token()
        APP_DEBUG = app_debug()
        APP_PORT = app_port()
        BACKUP_ENABLED = backup_enabled()
        BACKUP_FREQUENCY = backup_frequency()
        EMAIL_ENABLED = email_enabled()
        SMTP_SERVER = smtp_server()
        SMTP_PORT = smtp_port()
        SMTP_USERNAME = smtp_username()
        SMTP_PASSWORD = smtp_password()
        
        # Additional constants needed by some modules
        LOGO_PATH = "static/images/himanshi_travels_logo.png"
        BILLS_DIRECTORY = "bills"

# Module-level function to access constants (call this when needed)
def init_module_constants():
    """Initialize module-level constants for backward compatibility"""
    _get_module_constants()

# Utility functions for easy access
def get_config(key: str, default: Any = None) -> Any:
    """Simple function to get any configuration value"""
    return config.get(key, default)

def get_business_config():
    """Get all business configuration"""
    return config.get_category('business')

def get_whatsapp_config():
    """Get all WhatsApp configuration"""
    return config.get_category('whatsapp')

def get_app_config():
    """Get all application configuration"""
    return config.get_category('app')

def refresh_config():
    """Refresh configuration from database"""
    config.refresh()
