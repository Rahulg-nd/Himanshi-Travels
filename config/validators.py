"""
Configuration validators for Himanshi Travels
"""

import re
import logging
from typing import Any, Dict, Optional, List
from .types import ConfigType

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration values according to their types and rules"""
    
    @staticmethod
    def validate_email(value: str) -> tuple[bool, Optional[str]]:
        """Validate email address format"""
        if not value:  # Allow empty values for non-required fields
            return True, None
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, "Invalid email format"
        return True, None
    
    @staticmethod
    def validate_url(value: str) -> tuple[bool, Optional[str]]:
        """Validate URL format"""
        if not value:  # Allow empty values for non-required fields
            return True, None
            
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value):
            return False, "Invalid URL format (must start with http:// or https://)"
        return True, None
    
    @staticmethod
    def validate_phone(value: str) -> tuple[bool, Optional[str]]:
        """Validate phone number format"""
        if not value:  # Allow empty values for non-required fields
            return True, None
            
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', value)
        if len(digits_only) < 10 or len(digits_only) > 15:
            return False, "Phone number must be between 10-15 digits"
        return True, None
    
    @staticmethod
    def validate_gstin(value: str) -> tuple[bool, Optional[str]]:
        """Validate GSTIN format"""
        if not value:
            return True, None
            
        gstin_pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$'
        if not re.match(gstin_pattern, value):
            return False, "Invalid GSTIN format"
        return True, None
    
    @staticmethod
    def validate_number(value: Any) -> tuple[bool, Optional[str]]:
        """Validate numeric value"""
        try:
            float(value)
            return True, None
        except (ValueError, TypeError):
            return False, "Value must be a number"
    
    @staticmethod
    def validate_boolean(value: Any) -> tuple[bool, Optional[str]]:
        """Validate boolean value"""
        if isinstance(value, bool):
            return True, None
        if isinstance(value, str):
            if value.lower() in ('true', 'false', '1', '0', 'yes', 'no'):
                return True, None
        return False, "Value must be true or false"
    
    @staticmethod
    def validate_config_value(config_type: ConfigType, value: Any, validation_rules: Optional[Dict] = None) -> tuple[bool, Optional[str]]:
        """Validate a configuration value based on its type and rules"""
        
        # Convert value to string for validation
        str_value = str(value) if value is not None else ""
        
        # Type-specific validation
        if config_type == ConfigType.EMAIL:
            return ConfigValidator.validate_email(str_value)
        elif config_type == ConfigType.URL:
            return ConfigValidator.validate_url(str_value)
        elif config_type == ConfigType.PHONE:
            return ConfigValidator.validate_phone(str_value)
        elif config_type == ConfigType.NUMBER:
            return ConfigValidator.validate_number(value)
        elif config_type == ConfigType.BOOLEAN:
            return ConfigValidator.validate_boolean(value)
        
        # Custom validation rules
        if validation_rules:
            return ConfigValidator._validate_custom_rules(str_value, validation_rules)
        
        return True, None
    
    @staticmethod
    def _validate_custom_rules(str_value: str, validation_rules: Dict) -> tuple[bool, Optional[str]]:
        """Validate custom validation rules"""
        if 'pattern' in validation_rules:
            pattern = validation_rules['pattern']
            if pattern == r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$':
                return ConfigValidator.validate_gstin(str_value)
            elif not re.match(pattern, str_value):
                return False, "Value does not match required pattern"
        
        if 'min_length' in validation_rules:
            if len(str_value) < validation_rules['min_length']:
                return False, f"Minimum length is {validation_rules['min_length']}"
        
        if 'max_length' in validation_rules:
            if len(str_value) > validation_rules['max_length']:
                return False, f"Maximum length is {validation_rules['max_length']}"
        
        return True, None
