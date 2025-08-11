"""
PDF configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class PDFConfig:
    """PDF configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all PDF configuration fields"""
        return [
            ConfigField(
                key="PDF_ENABLED",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.PDF,
                description="Enable/disable PDF generation",
                help_text="Turn PDF generation features on or off"
            ),
            ConfigField(
                key="PDF_TEMPLATE_PATH",
                value="templates/pdf/",
                type=ConfigType.STRING,
                category=ConfigCategory.PDF,
                description="PDF template directory path",
                help_text="Directory containing PDF templates"
            ),
            ConfigField(
                key="PDF_OUTPUT_PATH",
                value="bills/",
                type=ConfigType.STRING,
                category=ConfigCategory.PDF,
                description="PDF output directory path",
                help_text="Directory where generated PDFs are saved"
            ),
            ConfigField(
                key="PDF_FONT_SIZE",
                value="12",
                type=ConfigType.NUMBER,
                category=ConfigCategory.PDF,
                description="Default PDF font size",
                help_text="Font size for PDF content"
            ),
            ConfigField(
                key="PDF_FONT_FAMILY",
                value="Arial",
                type=ConfigType.STRING,
                category=ConfigCategory.PDF,
                description="Default PDF font family",
                help_text="Font family for PDF content"
            ),
            ConfigField(
                key="PDF_PAGE_FORMAT",
                value="A4",
                type=ConfigType.STRING,
                category=ConfigCategory.PDF,
                description="PDF page format",
                help_text="Page size format (A4, Letter, etc.)"
            ),
            ConfigField(
                key="PDF_MARGIN_TOP",
                value="20",
                type=ConfigType.NUMBER,
                category=ConfigCategory.PDF,
                description="PDF top margin in mm",
                help_text="Top margin for PDF pages"
            ),
            ConfigField(
                key="PDF_MARGIN_BOTTOM",
                value="20",
                type=ConfigType.NUMBER,
                category=ConfigCategory.PDF,
                description="PDF bottom margin in mm",
                help_text="Bottom margin for PDF pages"
            ),
            ConfigField(
                key="PDF_MARGIN_LEFT",
                value="15",
                type=ConfigType.NUMBER,
                category=ConfigCategory.PDF,
                description="PDF left margin in mm",
                help_text="Left margin for PDF pages"
            ),
            ConfigField(
                key="PDF_MARGIN_RIGHT",
                value="15",
                type=ConfigType.NUMBER,
                category=ConfigCategory.PDF,
                description="PDF right margin in mm",
                help_text="Right margin for PDF pages"
            )
        ]
