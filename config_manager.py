"""
Configuration Management Module for Himanshi Travels
Provides a structured interface for managing application configuration.

This module provides backward compatibility with the old config_manager.py
while using the new modular configuration system.
"""

import logging
from typing import Dict, List, Any, Optional

# Import the new modular config system
from config import ConfigManager as ModularConfigManager
from config import ConfigType, ConfigCategory, ConfigField

logger = logging.getLogger(__name__)

# Create the global config manager instance for backward compatibility
config_manager = ModularConfigManager()

# Backward compatibility class
class ConfigManager:
    """Legacy ConfigManager wrapper for backward compatibility"""
    
    def __init__(self):
        self._modular_manager = ModularConfigManager()
    
    def get_categories(self):
        """Get all available configuration categories"""
        return self._modular_manager.get_categories()
    
    def get_config_by_category(self, category):
        """Get configuration fields by category"""
        return self._modular_manager.get_fields_by_category(category)
    
    def get_category_info(self, category):
        """Get category information"""
        return {
            'name': self._modular_manager.get_category_display_name(category),
            'icon': self._modular_manager.get_category_icon(category),
            'description': self._modular_manager.get_category_description(category)
        }
    
    def get_config_schema(self):
        """Get the complete configuration schema"""
        return self._modular_manager.get_schema()
    
    def validate_config_value(self, field, value):
        """Validate a configuration value"""
        return self._modular_manager.validate_config(field.key, value)

# For backward compatibility, create a global instance
_legacy_config_manager = ConfigManager()

# Export the legacy interface
def get_categories():
    return config_manager.get_categories()

def get_config_by_category(category):
    return config_manager.get_fields_by_category(category)

def get_category_info(category):
    return {
        'name': config_manager.get_category_display_name(category),
        'icon': config_manager.get_category_icon(category),
        'description': config_manager.get_category_description(category)
    }

def get_config_schema():
    return config_manager.get_schema()

def validate_config_value(field, value):
    return config_manager.validate_config(field.key, value)
