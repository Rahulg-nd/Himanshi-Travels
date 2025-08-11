"""
Database configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class DatabaseConfig:
    """Database configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all database configuration fields"""
        return [
            ConfigField(
                key="DATABASE_TYPE",
                value="sqlite",
                type=ConfigType.STRING,
                category=ConfigCategory.DATABASE,
                description="Database type (sqlite, mysql, postgresql)",
                help_text="Type of database being used"
            ),
            ConfigField(
                key="DATABASE_NAME",
                value="db.sqlite3",
                type=ConfigType.STRING,
                category=ConfigCategory.DATABASE,
                description="Database name or file path",
                help_text="Database name or file path for SQLite"
            ),
            ConfigField(
                key="DATABASE_HOST",
                value="localhost",
                type=ConfigType.STRING,
                category=ConfigCategory.DATABASE,
                description="Database host server",
                help_text="Database server hostname or IP"
            ),
            ConfigField(
                key="DATABASE_PORT",
                value="5432",
                type=ConfigType.NUMBER,
                category=ConfigCategory.DATABASE,
                description="Database port number",
                help_text="Port number for database connection"
            ),
            ConfigField(
                key="DATABASE_USERNAME",
                value="admin",
                type=ConfigType.STRING,
                category=ConfigCategory.DATABASE,
                description="Database username",
                help_text="Username for database authentication"
            ),
            ConfigField(
                key="DATABASE_PASSWORD",
                value="password",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.DATABASE,
                description="Database password",
                is_sensitive=True,
                help_text="Password for database authentication"
            ),
            ConfigField(
                key="DATABASE_POOL_SIZE",
                value="10",
                type=ConfigType.NUMBER,
                category=ConfigCategory.DATABASE,
                description="Database connection pool size",
                help_text="Maximum number of database connections"
            ),
            ConfigField(
                key="DATABASE_TIMEOUT",
                value="30",
                type=ConfigType.NUMBER,
                category=ConfigCategory.DATABASE,
                description="Database connection timeout (seconds)",
                help_text="Connection timeout in seconds"
            )
        ]
