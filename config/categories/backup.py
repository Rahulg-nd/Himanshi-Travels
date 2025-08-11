"""
Backup configuration settings for Himanshi Travels
"""

from typing import List
from ..types import ConfigField, ConfigType, ConfigCategory


class BackupConfig:
    """Backup configuration category"""
    
    @staticmethod
    def get_fields() -> List[ConfigField]:
        """Get all backup configuration fields"""
        return [
            ConfigField(
                key="BACKUP_ENABLED",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.BACKUP,
                description="Enable/disable automatic backups",
                help_text="Turn automatic backup features on or off"
            ),
            ConfigField(
                key="BACKUP_SCHEDULE",
                value="daily",
                type=ConfigType.STRING,
                category=ConfigCategory.BACKUP,
                description="Backup schedule frequency",
                help_text="How often to create backups (daily, weekly, monthly)"
            ),
            ConfigField(
                key="BACKUP_TIME",
                value="02:00",
                type=ConfigType.STRING,
                category=ConfigCategory.BACKUP,
                description="Backup execution time (HH:MM)",
                help_text="Time of day to run backups (24-hour format)"
            ),
            ConfigField(
                key="BACKUP_PATH",
                value="backups/",
                type=ConfigType.STRING,
                category=ConfigCategory.BACKUP,
                description="Backup storage directory",
                help_text="Local directory where backups are stored"
            ),
            ConfigField(
                key="BACKUP_RETENTION_DAYS",
                value="30",
                type=ConfigType.NUMBER,
                category=ConfigCategory.BACKUP,
                description="Backup retention period in days",
                help_text="How long to keep backup files"
            ),
            ConfigField(
                key="BACKUP_COMPRESSION",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.BACKUP,
                description="Enable backup compression",
                help_text="Compress backup files to save space"
            ),
            ConfigField(
                key="BACKUP_INCLUDE_FILES",
                value=True,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.BACKUP,
                description="Include uploaded files in backup",
                help_text="Whether to backup uploaded files and documents"
            ),
            ConfigField(
                key="BACKUP_CLOUD_ENABLED",
                value=False,
                type=ConfigType.BOOLEAN,
                category=ConfigCategory.BACKUP,
                description="Enable cloud backup storage",
                help_text="Upload backups to cloud storage"
            ),
            ConfigField(
                key="BACKUP_CLOUD_PROVIDER",
                value="aws_s3",
                type=ConfigType.STRING,
                category=ConfigCategory.BACKUP,
                description="Cloud backup provider",
                help_text="Cloud storage provider (aws_s3, google_drive, dropbox)"
            ),
            ConfigField(
                key="BACKUP_CLOUD_API_KEY",
                value="your-cloud-api-key",
                type=ConfigType.PASSWORD,
                category=ConfigCategory.BACKUP,
                description="Cloud storage API key",
                is_sensitive=True,
                help_text="API key for cloud storage service"
            )
        ]
