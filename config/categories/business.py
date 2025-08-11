"""
Business configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class BusinessConfig:
    """Business configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all business configuration fields"""
        return [
            ConfigField(
                key="AGENCY_NAME",
                value="Himanshi Travels",
                type=ConfigType.STRING,
                category=ConfigCategory.BUSINESS,
                description="Travel agency name displayed on invoices and documents",
                is_required=True,
                help_text="This name appears on all customer-facing documents"
            ),
            ConfigField(
                key="AGENCY_TAGLINE",
                value="Your Journey, Our Passion",
                type=ConfigType.STRING,
                category=ConfigCategory.BUSINESS,
                description="Agency tagline or slogan",
                help_text="A catchy phrase that represents your brand"
            ),
            ConfigField(
                key="GSTIN",
                value="29ABCDE1234F2Z5",
                type=ConfigType.STRING,
                category=ConfigCategory.BUSINESS,
                description="GST Identification Number",
                is_required=True,
                validation_rules={"pattern": r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$"},
                help_text="15-character alphanumeric GST identification number"
            ),
            ConfigField(
                key="BUSINESS_ADDRESS",
                value="123 Travel Street, Tourism City, State 123456",
                type=ConfigType.STRING,
                category=ConfigCategory.BUSINESS,
                description="Complete business address",
                is_required=True,
                help_text="Full address including street, city, state, and postal code"
            ),
            ConfigField(
                key="BUSINESS_PHONE",
                value="+91-9876543210",
                type=ConfigType.PHONE,
                category=ConfigCategory.BUSINESS,
                description="Primary business contact number",
                is_required=True,
                help_text="Main phone number for customer inquiries"
            ),
            ConfigField(
                key="BUSINESS_EMAIL",
                value="info@himanshitravels.com",
                type=ConfigType.EMAIL,
                category=ConfigCategory.BUSINESS,
                description="Primary business email address",
                is_required=True,
                help_text="Main email for business correspondence"
            ),
            ConfigField(
                key="WEBSITE_URL",
                value="https://www.himanshitravels.com",
                type=ConfigType.URL,
                category=ConfigCategory.BUSINESS,
                description="Company website URL",
                help_text="Your agency's official website"
            ),
            ConfigField(
                key="BUSINESS_HOURS",
                value="Mon-Sat: 9:00 AM - 8:00 PM, Sun: 10:00 AM - 6:00 PM",
                type=ConfigType.STRING,
                category=ConfigCategory.BUSINESS,
                description="Business operating hours",
                help_text="Display hours for customer reference"
            ),
            ConfigField(
                key="LOGO_PATH",
                value="static/images/himanshi_travels_logo.png",
                type=ConfigType.STRING,
                category=ConfigCategory.BUSINESS,
                description="Path to company logo file",
                help_text="Logo used in documents and website"
            ),
            ConfigField(
                key="LOGO_WIDTH",
                value="150",
                type=ConfigType.NUMBER,
                category=ConfigCategory.BUSINESS,
                description="Logo display width in pixels",
                help_text="Width for logo display in documents"
            ),
            ConfigField(
                key="LOGO_HEIGHT",
                value="75",
                type=ConfigType.NUMBER,
                category=ConfigCategory.BUSINESS,
                description="Logo display height in pixels",
                help_text="Height for logo display in documents"
            )
        ]
