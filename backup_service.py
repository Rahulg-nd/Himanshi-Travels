"""
Backup Service for Himanshi Travels
Provides database backup functionality using configuration settings
"""

import os
import shutil
import sqlite3
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class BackupService:
    """Database backup service"""
    
    def __init__(self):
        self.config = None
        self._initialized = False
        self._scheduler_running = False
        self._scheduler_thread = None
    
    def _init_config(self):
        """Initialize backup configuration"""
        if self._initialized:
            return
            
        try:
            from dynamic_config import config, DATABASE_FILE
            self.config = config
            self.database_file = DATABASE_FILE
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize backup config: {e}")
            self._initialized = False
    
    def is_enabled(self) -> bool:
        """Check if backup is enabled"""
        self._init_config()
        if not self.config:
            return False
        return self.config.get_bool('backup_enabled', False)
    
    def get_backup_frequency(self) -> str:
        """Get backup frequency"""
        self._init_config()
        if not self.config:
            return 'daily'
        return self.config.get_str('backup_frequency', 'daily')
    
    def get_backup_directory(self) -> str:
        """Get backup directory path"""
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a database backup"""
        self._init_config()
        
        if not self._initialized:
            return {
                'success': False,
                'message': 'Backup service not initialized'
            }
        
        try:
            backup_dir = self.get_backup_directory()
            
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"himanshi_travels_backup_{timestamp}.db"
            
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Check if source database exists
            if not os.path.exists(self.database_file):
                return {
                    'success': False,
                    'message': f'Source database not found: {self.database_file}'
                }
            
            # Create backup using SQLite backup API (more reliable than file copy)
            source_conn = sqlite3.connect(self.database_file)
            backup_conn = sqlite3.connect(backup_path)
            
            try:
                source_conn.backup(backup_conn)
                logger.info(f"Database backup created: {backup_path}")
                
                # Get backup file size
                backup_size = os.path.getsize(backup_path)
                
                return {
                    'success': True,
                    'message': f'Backup created successfully: {backup_name}',
                    'backup_path': backup_path,
                    'backup_size': backup_size,
                    'timestamp': datetime.now().isoformat()
                }
            finally:
                source_conn.close()
                backup_conn.close()
                
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {
                'success': False,
                'message': f'Backup failed: {str(e)}'
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backup_dir = self.get_backup_directory()
            backups = []
            
            if not os.path.exists(backup_dir):
                return backups
            
            for filename in os.listdir(backup_dir):
                if filename.endswith('.db'):
                    filepath = os.path.join(backup_dir, filename)
                    stat = os.stat(filepath)
                    
                    backups.append({
                        'filename': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def restore_backup(self, backup_filename: str) -> Dict[str, Any]:
        """Restore database from backup"""
        self._init_config()
        
        if not self._initialized:
            return {
                'success': False,
                'message': 'Backup service not initialized'
            }
        
        try:
            backup_dir = self.get_backup_directory()
            backup_path = os.path.join(backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                return {
                    'success': False,
                    'message': f'Backup file not found: {backup_filename}'
                }
            
            # Create a backup of current database before restoring
            current_backup_result = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            if not current_backup_result['success']:
                logger.warning(f"Failed to backup current database before restore: {current_backup_result['message']}")
            
            # Restore backup
            shutil.copy2(backup_path, self.database_file)
            
            logger.info(f"Database restored from backup: {backup_filename}")
            return {
                'success': True,
                'message': f'Database restored successfully from {backup_filename}',
                'restored_from': backup_path,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return {
                'success': False,
                'message': f'Restore failed: {str(e)}'
            }
    
    def cleanup_old_backups(self, keep_count: int = 10) -> Dict[str, Any]:
        """Clean up old backups, keeping only the most recent ones"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return {
                    'success': True,
                    'message': f'No cleanup needed. Current backups: {len(backups)}',
                    'deleted_count': 0
                }
            
            # Delete old backups
            deleted_count = 0
            for backup in backups[keep_count:]:
                try:
                    os.remove(backup['path'])
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup['filename']}")
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup['filename']}: {e}")
            
            return {
                'success': True,
                'message': f'Cleanup completed. Deleted {deleted_count} old backups',
                'deleted_count': deleted_count,
                'remaining_count': len(backups) - deleted_count
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
            return {
                'success': False,
                'message': f'Cleanup failed: {str(e)}'
            }
    
    def start_scheduler(self):
        """Start the backup scheduler"""
        if not self.is_enabled():
            logger.info("Backup service is disabled")
            return
        
        if self._scheduler_running:
            logger.info("Backup scheduler is already running")
            return
        
        frequency = self.get_backup_frequency()
        
        # Clear any existing schedules
        schedule.clear('backup')
        
        # Schedule based on frequency
        if frequency == 'daily':
            schedule.every().day.at("02:00").do(self._scheduled_backup).tag('backup')
        elif frequency == 'weekly':
            schedule.every().week.at("02:00").do(self._scheduled_backup).tag('backup')
        elif frequency == 'monthly':
            schedule.every(30).days.at("02:00").do(self._scheduled_backup).tag('backup')
        else:
            logger.warning(f"Unknown backup frequency: {frequency}, defaulting to daily")
            schedule.every().day.at("02:00").do(self._scheduled_backup).tag('backup')
        
        self._scheduler_running = True
        
        # Start scheduler in a separate thread
        def run_scheduler():
            logger.info(f"Backup scheduler started with {frequency} frequency")
            while self._scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self._scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        logger.info("Backup scheduler thread started")
    
    def stop_scheduler(self):
        """Stop the backup scheduler"""
        self._scheduler_running = False
        schedule.clear('backup')
        logger.info("Backup scheduler stopped")
    
    def _scheduled_backup(self):
        """Perform a scheduled backup"""
        try:
            result = self.create_backup()
            if result['success']:
                logger.info(f"Scheduled backup completed: {result['message']}")
                
                # Cleanup old backups
                cleanup_result = self.cleanup_old_backups()
                if cleanup_result['success']:
                    logger.info(f"Backup cleanup: {cleanup_result['message']}")
            else:
                logger.error(f"Scheduled backup failed: {result['message']}")
                
        except Exception as e:
            logger.error(f"Scheduled backup error: {e}")

# Global backup service instance
backup_service = BackupService()

def create_database_backup(backup_name: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to create a backup"""
    return backup_service.create_backup(backup_name)

def list_database_backups() -> List[Dict[str, Any]]:
    """Convenience function to list backups"""
    return backup_service.list_backups()

def restore_database_backup(backup_filename: str) -> Dict[str, Any]:
    """Convenience function to restore a backup"""
    return backup_service.restore_backup(backup_filename)

def start_backup_scheduler():
    """Convenience function to start backup scheduler"""
    backup_service.start_scheduler()

def stop_backup_scheduler():
    """Convenience function to stop backup scheduler"""
    backup_service.stop_scheduler()
