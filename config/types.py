"""
Configuration types and enums for Himanshi Travels
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ConfigType(Enum):
    """Configuration value types"""
    STRING = "string"
    BOOLEAN = "boolean"
    NUMBER = "number"
    PASSWORD = "password"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"


class ConfigCategory(Enum):
    """Configuration categories"""
    GENERAL = "general"
    BUSINESS = "business"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    PDF = "pdf"
    DATABASE = "database"
    BACKUP = "backup"
    SECURITY = "security"


@dataclass
class ConfigField:
    """Represents a configuration field with metadata"""
    key: str
    value: Any
    type: ConfigType
    category: ConfigCategory
    description: str
    is_sensitive: bool = False
    is_required: bool = False
    default_value: Any = None
    validation_rules: Optional[Dict[str, Any]] = None
    help_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'config_key': self.key,
            'config_value': str(self.value) if self.value is not None else '',
            'config_type': self.type.value,
            'category': self.category.value,
            'description': self.description,
            'is_sensitive': self.is_sensitive
        }
