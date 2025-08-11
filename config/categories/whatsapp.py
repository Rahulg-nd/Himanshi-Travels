"""
WhatsApp configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class WhatsAppConfig:
    """WhatsApp configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all WhatsApp configuration fields"""
        return [
            ConfigField(
                key="WHATSAPP_ENABLED",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.WHATSAPP,
                description="Enable/disable WhatsApp functionality",
                help_text="Turn WhatsApp features on or off"
            ),
            ConfigField(
                key="WHATSAPP_API_URL",
                value="https://api.whatsapp.com/send",
                type=ConfigType.URL,
                category=ConfigCategory.WHATSAPP,
                description="WhatsApp API endpoint URL",
                help_text="API URL for WhatsApp integration"
            ),
            ConfigField(
                key="WHATSAPP_TOKEN",
                value="your-whatsapp-token",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.WHATSAPP,
                description="WhatsApp API access token",
                is_sensitive=True,
                help_text="Token for WhatsApp Business API"
            ),
            ConfigField(
                key="WHATSAPP_PHONE_NUMBER_ID",
                value="your-phone-number-id",
                type=ConfigType.STRING,
                category=ConfigCategory.WHATSAPP,
                description="WhatsApp phone number ID",
                help_text="Phone number ID from WhatsApp Business"
            ),
            ConfigField(
                key="WHATSAPP_BUSINESS_PHONE",
                value="+91-9876543210",
                type=ConfigType.PHONE,
                category=ConfigCategory.WHATSAPP,
                description="Business WhatsApp number",
                help_text="WhatsApp number for customer communication"
            ),
            ConfigField(
                key="WHATSAPP_WELCOME_MESSAGE",
                value="Welcome to Himanshi Travels! How can we help you today?",
                type=ConfigType.STRING,
                category=ConfigCategory.WHATSAPP,
                description="Default welcome message",
                help_text="Automated welcome message for new chats"
            ),
            ConfigField(
                key="WHATSAPP_BOOKING_TEMPLATE",
                value="Thank you for your booking! Your booking ID is {{booking_id}}. We will contact you soon with further details.",
                type=ConfigType.STRING,
                category=ConfigCategory.WHATSAPP,
                description="Booking confirmation message template",
                help_text="Template for booking confirmation messages"
            )
        ]
