"""
Himanshi Travels - Travel Booking Management System
Modular Flask application for managing travel bookings, invoices, and customer data.

This is the main application file that now imports from modular components.
For the original monolithic version, see app_backup.py
"""

from database import init_db
from routes import create_and_configure_app


def main():
    """Main application entry point"""
    # Initialize database
    init_db()
    
    # Create and configure app
    app = create_and_configure_app()
    
    # Run the application
    return app


if __name__ == '__main__':
    try:
        print("Starting Himanshi Travels application...")
        app = main()
        print("App created successfully. Starting server on port 8081...")
        app.run(debug=True, port=8081, host='127.0.0.1')
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
