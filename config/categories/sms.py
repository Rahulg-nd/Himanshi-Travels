"""
SMS configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class SMSConfig:
    """SMS configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all SMS configuration fields"""
        return [
            ConfigField(
                key="SMS_ENABLED",
                value=False,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.SMS,
                description="Enable/disable SMS functionality",
                help_text="Turn SMS features on or off"
            ),
            ConfigField(
                key="SMS_PROVIDER",
                value="twilio",
                type=ConfigType.STRING,
                category=ConfigCategory.SMS,
                description="SMS service provider",
                help_text="SMS provider (twilio, msg91, textlocal, etc.)"
            ),
            ConfigField(
                key="SMS_API_URL",
                value="https://api.twilio.com/2010-04-01/Accounts",
                type=ConfigType.URL,
                category=ConfigCategory.SMS,
                description="SMS API endpoint URL",
                help_text="API URL for SMS service"
            ),
            ConfigField(
                key="SMS_API_KEY",
                value="your-sms-api-key",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.SMS,
                description="SMS API key/SID",
                is_sensitive=True,
                help_text="API key or Account SID for SMS service"
            ),
            ConfigField(
                key="SMS_API_SECRET",
                value="your-sms-api-secret",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.SMS,
                description="SMS API secret/token",
                is_sensitive=True,
                help_text="API secret or auth token for SMS service"
            ),
            ConfigField(
                key="SMS_FROM_NUMBER",
                value="+1234567890",
                type=ConfigType.PHONE,
                category=ConfigCategory.SMS,
                description="SMS sender phone number",
                help_text="Phone number for sending SMS"
            ),
            ConfigField(
                key="SMS_BOOKING_TEMPLATE",
                value="Hi {{customer_name}}, your booking with Himanshi Travels is confirmed. Booking ID: {{booking_id}}. Thank you!",
                type=ConfigType.STRING,
                category=ConfigCategory.SMS,
                description="SMS booking confirmation template",
                help_text="Template for booking confirmation SMS"
            )
        ]
