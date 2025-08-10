"""
Himanshi Travels - Travel Booking Management System
Modular Flask application for managing travel bookings, invoices, and customer data.

This is the main application file that now imports from modular components.
For the original monolithic version, see app_backup.py
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from database import init_db
from routes import create_and_configure_app


def setup_logging():
    """Setup application logging"""
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    log_file = os.path.join(logs_dir, 'app.log')
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=1024*1024*10,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    console_handler.setLevel(logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    return logging.getLogger(__name__)


def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Himanshi Travels application...")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    
    # Create and configure app
    logger.info("Creating Flask application...")
    app = create_and_configure_app()
    logger.info("Flask application created and configured successfully")
    
    # Configure Flask app logging
    app.logger.setLevel(logging.INFO)
    
    return app


if __name__ == '__main__':
    try:
        logger = logging.getLogger(__name__)
        logger.info("Starting Himanshi Travels development server...")
        app = main()
        logger.info("Starting server on port 8081...")
        app.run(debug=True, port=8081, host='127.0.0.1')
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error starting application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error starting application: {e}")
        traceback.print_exc()
