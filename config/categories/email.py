"""
Email configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class EmailConfig:
    """Email configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all email configuration fields"""
        return [
            ConfigField(
                key="EMAIL_ENABLED",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.EMAIL,
                description="Enable/disable email functionality",
                help_text="Turn email features on or off"
            ),
            ConfigField(
                key="SMTP_HOST",
                value="smtp.gmail.com",
                type=ConfigType.STRING,
                category=ConfigCategory.EMAIL,
                description="SMTP server hostname",
                is_required=True,
                help_text="SMTP server for sending emails"
            ),
            ConfigField(
                key="SMTP_PORT",
                value="587",
                type=ConfigType.NUMBER,
                category=ConfigCategory.EMAIL,
                description="SMTP server port",
                is_required=True,
                help_text="Usually 587 for TLS or 465 for SSL"
            ),
            ConfigField(
                key="SMTP_USE_TLS",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.EMAIL,
                description="Use TLS encryption for SMTP",
                help_text="Enable for secure email transmission"
            ),
            ConfigField(
                key="SMTP_USERNAME",
                value="your-email@gmail.com",
                type=ConfigType.EMAIL,
                category=ConfigCategory.EMAIL,
                description="SMTP authentication username",
                is_required=True,
                help_text="Email account for sending messages"
            ),
            ConfigField(
                key="SMTP_PASSWORD",
                value="your-app-password",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.EMAIL,
                description="SMTP authentication password",
                is_sensitive=True,
                is_required=True,
                help_text="App password or account password"
            ),
            ConfigField(
                key="FROM_EMAIL",
                value="noreply@himanshitravels.com",
                type=ConfigType.EMAIL,
                category=ConfigCategory.EMAIL,
                description="Default sender email address",
                is_required=True,
                help_text="Email address shown as sender"
            ),
            ConfigField(
                key="FROM_NAME",
                value="Himanshi Travels",
                type=ConfigType.STRING,
                category=ConfigCategory.EMAIL,
                description="Default sender name",
                help_text="Name shown as sender in emails"
            ),
            ConfigField(
                key="REPLY_TO_EMAIL",
                value="support@himanshitravels.com",
                type=ConfigType.EMAIL,
                category=ConfigCategory.EMAIL,
                description="Reply-to email address",
                help_text="Where replies should be sent"
            ),
            ConfigField(
                key="EMAIL_TEMPLATE_HEADER",
                value="Thank you for choosing Himanshi Travels!",
                type=ConfigType.STRING,
                category=ConfigCategory.EMAIL,
                description="Email template header text",
                help_text="Header text for email templates"
            ),
            ConfigField(
                key="EMAIL_TEMPLATE_FOOTER",
                value="Best regards,\nHimanshi Travels Team",
                type=ConfigType.STRING,
                category=ConfigCategory.EMAIL,
                description="Email template footer text",
                help_text="Footer text for email templates"
            )
        ]
