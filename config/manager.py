"""
Main configuration manager for Himanshi Travels
"""

import logging
from typing import Dict, List, Any, Optional, Set
from .types import ConfigField, ConfigType, ConfigCategory
from .validators import ConfigValidator
from .categories import (
    BusinessConfig, EmailConfig, WhatsAppConfig, SMSConfig, 
    PDFConfig, DatabaseConfig, BackupConfig, SecurityConfig
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration with validation and categorization"""
    
    def __init__(self):
        self._config_schema = self._initialize_schema()
        self._validator = ConfigValidator()
    
    def _initialize_schema(self) -> Dict[str, ConfigField]:
        """Initialize the configuration schema with all available options"""
        schema = {}
        
        # Load all configuration categories
        categories = [
            BusinessConfig,
            EmailConfig,
            WhatsAppConfig,
            SMSConfig,
            PDFConfig,
            DatabaseConfig,
            BackupConfig,
            SecurityConfig
        ]
        
        # Build schema from all category fields
        for category_class in categories:
            fields = category_class.get_fields()
            for field in fields:
                schema[field.key] = field
        
        return schema
    
    def get_schema(self) -> Dict[str, ConfigField]:
        """Get the complete configuration schema"""
        return self._config_schema.copy()
    
    def get_config_schema(self) -> Dict[str, ConfigField]:
        """Get the complete configuration schema (alias for get_schema for backward compatibility)"""
        return self.get_schema()
    
    def get_categories(self) -> List[ConfigCategory]:
        """Get all available configuration categories"""
        categories = set()
        for field in self._config_schema.values():
            categories.add(field.category)
        return sorted(categories, key=lambda x: x.value)
    
    def get_fields_by_category(self, category: ConfigCategory) -> List[ConfigField]:
        """Get all configuration fields for a specific category"""
        return [
            field for field in self._config_schema.values()
            if field.category == category
        ]
    
    def get_field(self, key: str) -> Optional[ConfigField]:
        """Get a specific configuration field by key"""
        return self._config_schema.get(key)
    
    def validate_config(self, key: str, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a configuration value"""
        field = self.get_field(key)
        if not field:
            return False, f"Unknown configuration key: {key}"
        
        # Check if required field is empty
        if field.is_required and (value is None or str(value).strip() == ""):
            return False, f"Field '{key}' is required and cannot be empty"
        
        # Validate using the field's type and rules
        return self._validator.validate_config_value(
            field.type, 
            value, 
            field.validation_rules
        )
    
    def get_default_values(self) -> Dict[str, Any]:
        """Get default values for all configuration fields"""
        defaults = {}
        for key, field in self._config_schema.items():
            defaults[key] = field.value if field.default_value is None else field.default_value
        return defaults
    
    def get_required_fields(self) -> List[str]:
        """Get list of required configuration field keys"""
        return [
            key for key, field in self._config_schema.items()
            if field.is_required
        ]
    
    def get_sensitive_fields(self) -> Set[str]:
        """Get set of sensitive configuration field keys"""
        return {
            key for key, field in self._config_schema.items()
            if field.is_sensitive
        }
    
    def is_sensitive_field(self, key: str) -> bool:
        """Check if a configuration field is sensitive"""
        field = self.get_field(key)
        return field.is_sensitive if field else False
    
    def get_category_display_name(self, category: ConfigCategory) -> str:
        """Get display name for a configuration category"""
        display_names = {
            ConfigCategory.GENERAL: "General Settings",
            ConfigCategory.BUSINESS: "Business Information",
            ConfigCategory.WHATSAPP: "WhatsApp Integration",
            ConfigCategory.EMAIL: "Email Configuration",
            ConfigCategory.SMS: "SMS Configuration",
            ConfigCategory.PDF: "PDF Settings",
            ConfigCategory.DATABASE: "Database Configuration",
            ConfigCategory.BACKUP: "Backup Settings",
            ConfigCategory.SECURITY: "Security Settings"
        }
        return display_names.get(category, category.value.title())
    
    def get_category_icon(self, category: ConfigCategory) -> str:
        """Get icon for a configuration category"""
        icons = {
            ConfigCategory.GENERAL: "⚙️",
            ConfigCategory.BUSINESS: "🏢",
            ConfigCategory.WHATSAPP: "📱",
            ConfigCategory.EMAIL: "📧",
            ConfigCategory.SMS: "💬",
            ConfigCategory.PDF: "📄",
            ConfigCategory.DATABASE: "🗄️",
            ConfigCategory.BACKUP: "💾",
            ConfigCategory.SECURITY: "🔒"
        }
        return icons.get(category, "⚙️")
    
    def get_category_description(self, category: ConfigCategory) -> str:
        """Get description for a configuration category"""
        descriptions = {
            ConfigCategory.GENERAL: "General application settings and preferences",
            ConfigCategory.BUSINESS: "Company information and branding settings",
            ConfigCategory.WHATSAPP: "WhatsApp Business API integration settings",
            ConfigCategory.EMAIL: "Email server and messaging configuration",
            ConfigCategory.SMS: "SMS service provider and messaging settings",
            ConfigCategory.PDF: "PDF generation and formatting settings",
            ConfigCategory.DATABASE: "Database connection and performance settings",
            ConfigCategory.BACKUP: "Automated backup and recovery settings",
            ConfigCategory.SECURITY: "Security policies and authentication settings"
        }
        return descriptions.get(category, "Configuration settings")
    
    def validate_batch_configs(self, configs: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate multiple configuration values at once"""
        results = {
            'valid': [],
            'invalid': [],
            'errors': {}
        }
        
        for key, value in configs.items():
            is_valid, error_message = self.validate_config(key, value)
            if is_valid:
                results['valid'].append(key)
            else:
                results['invalid'].append(key)
                results['errors'][key] = error_message
        
        return results
