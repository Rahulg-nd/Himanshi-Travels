"""
Security configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class SecurityConfig:
    """Security configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all security configuration fields"""
        return [
            ConfigField(
                key="SECURITY_SECRET_KEY",
                value="your-secret-key-here",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.SECURITY,
                description="Application secret key",
                is_sensitive=True,
                is_required=True,
                help_text="Secret key for session security and encryption"
            ),
            ConfigField(
                key="SECURITY_SESSION_TIMEOUT",
                value="3600",
                type=ConfigType.NUMBER,
                category=ConfigCategory.SECURITY,
                description="Session timeout in seconds",
                help_text="How long user sessions remain active"
            ),
            ConfigField(
                key="SECURITY_PASSWORD_MIN_LENGTH",
                value="8",
                type=ConfigType.NUMBER,
                category=ConfigCategory.SECURITY,
                description="Minimum password length",
                help_text="Minimum required password length"
            ),
            ConfigField(
                key="SECURITY_ENABLE_2FA",
                value=False,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.SECURITY,
                description="Enable two-factor authentication",
                help_text="Require 2FA for user accounts"
            ),
            ConfigField(
                key="SECURITY_LOGIN_ATTEMPTS",
                value="5",
                type=ConfigType.NUMBER,
                category=ConfigCategory.SECURITY,
                description="Maximum login attempts",
                help_text="Number of failed login attempts before lockout"
            ),
            ConfigField(
                key="SECURITY_LOCKOUT_DURATION",
                value="300",
                type=ConfigType.NUMBER,
                category=ConfigCategory.SECURITY,
                description="Account lockout duration in seconds",
                help_text="How long accounts remain locked after failed attempts"
            ),
            ConfigField(
                key="SECURITY_ENABLE_AUDIT_LOG",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.SECURITY,
                description="Enable security audit logging",
                help_text="Log security-related events and actions"
            ),
            ConfigField(
                key="SECURITY_ALLOWED_IPS",
                value="",
                type=ConfigType.STRING,
                category=ConfigCategory.SECURITY,
                description="Allowed IP addresses (comma-separated)",
                help_text="Restrict access to specific IP addresses"
            ),
            ConfigField(
                key="SECURITY_SSL_REQUIRED",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.SECURITY,
                description="Require SSL/HTTPS connections",
                help_text="Force secure connections only"
            ),
            ConfigField(
                key="SECURITY_API_RATE_LIMIT",
                value="100",
                type=ConfigType.NUMBER,
                category=ConfigCategory.SECURITY,
                description="API rate limit per hour",
                help_text="Maximum API requests per hour per user"
            )
        ]
