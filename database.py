"""
Database operations for Himanshi Travels application
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dynamic_config import DATABASE_FILE


def get_db_connection():
    """Get database connection with row factory"""
    con = sqlite3.connect(DATABASE_FILE)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    """Initialize database with required tables and indexes"""
    with sqlite3.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        
        # Create main bookings table
        cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            booking_type TEXT,
            base_amount REAL,
            gst REAL,
            total REAL,
            date TEXT
        )''')
        
        # Create customers table for multi-customer bookings
        cur.execute('''CREATE TABLE IF NOT EXISTS booking_customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT,
            customer_phone TEXT,
            seat_room_number TEXT,
            customer_amount REAL NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE
        )''')
        
        # Create configuration table for app settings
        cur.execute('''CREATE TABLE IF NOT EXISTS app_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE NOT NULL,
            config_value TEXT,
            config_type TEXT DEFAULT 'string',
            category TEXT DEFAULT 'general',
            description TEXT,
            is_sensitive INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Add new columns if they don't exist
        additional_columns = [
            ('hotel_name', 'TEXT'),
            ('hotel_city', 'TEXT'),
            ('operator_name', 'TEXT'),
            ('from_journey', 'TEXT'),
            ('to_journey', 'TEXT'),
            ('vehicle_number', 'TEXT'),
            ('service_date', 'TEXT'),
            ('service_time', 'TEXT'),
            ('is_group_booking', 'INTEGER DEFAULT 0'),
            ('customer_address', 'TEXT'),
            ('apply_gst', 'INTEGER DEFAULT 1'),
            ('hotel_country', 'TEXT'),
            ('from_journey_country', 'TEXT'),
            ('to_journey_country', 'TEXT')
        ]
        
        for column_name, column_type in additional_columns:
            try:
                cur.execute(f'ALTER TABLE bookings ADD COLUMN {column_name} {column_type}')
            except sqlite3.OperationalError:
                pass  # Column already exists
        
        # Create indexes for better search performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_bookings_name ON bookings(name)',
            'CREATE INDEX IF NOT EXISTS idx_bookings_email ON bookings(email)',
            'CREATE INDEX IF NOT EXISTS idx_bookings_phone ON bookings(phone)',
            'CREATE INDEX IF NOT EXISTS idx_bookings_type ON bookings(booking_type)',
            'CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date DESC)',
            'CREATE INDEX IF NOT EXISTS idx_bookings_hotel_name ON bookings(hotel_name)',
            'CREATE INDEX IF NOT EXISTS idx_bookings_operator ON bookings(operator_name)',
            'CREATE INDEX IF NOT EXISTS idx_booking_customers_booking_id ON booking_customers(booking_id)',
            'CREATE INDEX IF NOT EXISTS idx_booking_customers_name ON booking_customers(customer_name)'
        ]
        
        for index_sql in indexes:
            try:
                cur.execute(index_sql)
            except sqlite3.OperationalError:
                pass  # Index might already exist
        
        con.commit()
        
        # Initialize default configuration values
        initialize_default_config()


def create_booking(booking_data: Dict[str, Any]) -> int:
    """Create a new booking and return the booking ID"""
    with get_db_connection() as con:
        cur = con.cursor()
        
        cur.execute('''INSERT INTO bookings (name, email, phone, booking_type, base_amount, gst, total, date,
                    hotel_name, hotel_city, operator_name, from_journey, to_journey, vehicle_number, 
                    service_date, service_time, is_group_booking, customer_address, apply_gst, 
                    hotel_country, from_journey_country, to_journey_country)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (booking_data['name'], booking_data.get('email') or None, booking_data['phone'], 
                     booking_data['booking_type'], booking_data['base_amount'], booking_data['gst'], 
                     booking_data['total'], booking_data['date'], booking_data.get('hotel_name'),
                     booking_data.get('hotel_city'), booking_data.get('operator_name'),
                     booking_data.get('from_journey'), booking_data.get('to_journey'),
                     booking_data.get('vehicle_number'), booking_data.get('service_date'),
                     booking_data.get('service_time'), booking_data.get('is_group_booking', 0),
                     booking_data.get('customer_address'), booking_data.get('apply_gst', 1),
                     booking_data.get('hotel_country'), booking_data.get('from_journey_country'),
                     booking_data.get('to_journey_country')))
        
        booking_id = cur.lastrowid
        con.commit()
        return booking_id


def create_booking_customers(booking_id: int, customers: List[Dict[str, Any]]):
    """Create booking customers for group bookings"""
    with get_db_connection() as con:
        cur = con.cursor()
        
        for customer in customers:
            cur.execute('''INSERT INTO booking_customers (booking_id, customer_name, customer_email, 
                        customer_phone, seat_room_number, customer_amount)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (booking_id, customer['name'], customer['email'], customer['phone'],
                         customer['seat_room'], float(customer['amount'])))
        
        con.commit()


def get_booking_by_id(booking_id: int) -> Optional[Dict[str, Any]]:
    """Get booking details by ID"""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        booking = cur.fetchone()
        
        if booking:
            booking_dict = dict(booking)
            
            # Get customers for group bookings
            if booking_dict['is_group_booking']:
                cur.execute("SELECT * FROM booking_customers WHERE booking_id = ? ORDER BY id", (booking_id,))
                customers = [dict(row) for row in cur.fetchall()]
                booking_dict['customers'] = customers
            else:
                booking_dict['customers'] = []
            
            return booking_dict
        
        return None


def search_bookings(query: str = "", booking_type: str = "", page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Search bookings with pagination"""
    offset = (page - 1) * per_page
    
    with get_db_connection() as con:
        cur = con.cursor()
        
        # Build dynamic query for counting total results
        count_sql = 'SELECT COUNT(*) FROM bookings WHERE 1=1'
        params = []
        
        # Build dynamic query for fetching results
        sql = '''SELECT id, name, email, phone, booking_type, base_amount, gst, total, date, 
                        hotel_name, hotel_city, operator_name, from_journey, to_journey,
                        vehicle_number, service_date, service_time, is_group_booking
                 FROM bookings WHERE 1=1'''
        
        if query:
            search_condition = ''' AND (name LIKE ? OR email LIKE ? OR phone LIKE ? 
                          OR hotel_name LIKE ? OR operator_name LIKE ? 
                          OR from_journey LIKE ? OR to_journey LIKE ? OR vehicle_number LIKE ?)'''
            count_sql += search_condition
            sql += search_condition
            search_term = f'%{query}%'
            params.extend([search_term] * 8)
        
        if booking_type:
            type_condition = ' AND booking_type = ?'
            count_sql += type_condition
            sql += type_condition
            params.append(booking_type)
        
        # Get total count for pagination
        cur.execute(count_sql, params)
        total_count = cur.fetchone()[0]
        
        # Add ordering and pagination to main query
        sql += ' ORDER BY date DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        cur.execute(sql, params)
        rows = cur.fetchall()
        
        # Convert to list of dictionaries and add customer info for group bookings
        bookings = []
        for row in rows:
            booking = dict(row)
            
            # If it's a group booking, get customer count and details
            if booking['is_group_booking']:
                cur.execute('SELECT COUNT(*) FROM booking_customers WHERE booking_id = ?', (booking['id'],))
                customer_count = cur.fetchone()[0]
                booking['customer_count'] = customer_count
                
                # Get customer names for display
                cur.execute('SELECT customer_name FROM booking_customers WHERE booking_id = ? ORDER BY id LIMIT 3', (booking['id'],))
                customer_names = [row[0] for row in cur.fetchall()]
                booking['customer_names'] = customer_names
            else:
                booking['customer_count'] = 1
                booking['customer_names'] = [booking['name']]
            
            # Clean up None values
            for key, value in booking.items():
                if value is None:
                    booking[key] = ''
                    
            bookings.append(booking)
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'bookings': bookings,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }


def update_booking(booking_id: int, booking_data: Dict[str, Any], customers: List[Dict[str, Any]] = None) -> bool:
    """Update an existing booking"""
    with get_db_connection() as con:
        cur = con.cursor()
        
        # Check if booking exists
        cur.execute('SELECT id FROM bookings WHERE id = ?', (booking_id,))
        if not cur.fetchone():
            return False
        
        # Update booking
        cur.execute('''
            UPDATE bookings SET 
                name = ?, email = ?, phone = ?, booking_type = ?,
                base_amount = ?, gst = ?, total = ?,
                hotel_name = ?, hotel_city = ?, hotel_country = ?,
                operator_name = ?, from_journey = ?, from_journey_country = ?,
                to_journey = ?, to_journey_country = ?, service_date = ?,
                service_time = ?, vehicle_number = ?, is_group_booking = ?
            WHERE id = ?
        ''', (
            booking_data['name'],
            booking_data.get('email') or None,
            booking_data['phone'],
            booking_data['booking_type'],
            booking_data['base_amount'],
            booking_data['gst'],
            booking_data['total'],
            booking_data.get('hotel_name'),
            booking_data.get('hotel_city'),
            booking_data.get('hotel_country'),
            booking_data.get('operator_name'),
            booking_data.get('from_journey'),
            booking_data.get('from_journey_country'),
            booking_data.get('to_journey'),
            booking_data.get('to_journey_country'),
            booking_data.get('service_date'),
            booking_data.get('service_time'),
            booking_data.get('vehicle_number'),
            booking_data.get('is_group_booking', 0),
            booking_id
        ))
        
        rows_affected = cur.rowcount
        
        # Handle group booking customers
        if customers is not None:
            # Delete existing customers
            cur.execute('DELETE FROM booking_customers WHERE booking_id = ?', (booking_id,))
            
            # Insert updated customers
            for customer in customers:
                if customer.get('customer_name', '').strip():
                    cur.execute('''INSERT INTO booking_customers 
                                 (booking_id, customer_name, customer_email, customer_phone, 
                                  seat_room_number, customer_amount)
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (booking_id,
                               customer['customer_name'].strip(),
                               customer.get('customer_email', '').strip() or None,
                               customer.get('customer_phone', '').strip() or None,
                               customer.get('seat_room_number', '').strip() or None,
                               float(customer.get('customer_amount', 0))))
        else:
            # Remove any existing customers for non-group bookings
            cur.execute('DELETE FROM booking_customers WHERE booking_id = ?', (booking_id,))
        
        con.commit()
        
        # Return True if any changes were made (either booking update or customer changes)
        return rows_affected > 0 or customers is not None


def delete_booking(booking_id: int) -> Tuple[bool, str]:
    """Delete a booking by ID"""
    with get_db_connection() as con:
        cur = con.cursor()
        
        # First check if booking exists and get info
        cur.execute("SELECT id, name, is_group_booking FROM bookings WHERE id = ?", (booking_id,))
        booking = cur.fetchone()
        
        if not booking:
            return False, 'Booking not found'
        
        # If it's a group booking, delete associated customers first
        if booking[2]:  # is_group_booking
            cur.execute("DELETE FROM booking_customers WHERE booking_id = ?", (booking_id,))
        
        # Delete the booking
        cur.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        deleted_rows = cur.rowcount
        con.commit()
        
        if deleted_rows == 0:
            return False, 'No booking was deleted'
        
        booking_type = "Group Booking" if booking[2] else "Booking"
        message = f'{booking_type} #{str(booking_id).zfill(6)} for {booking[1]} has been deleted successfully'
        return True, message


def bulk_delete_bookings(booking_ids: List[int]) -> Tuple[bool, str, int]:
    """Delete multiple bookings at once"""
    deleted_count = 0
    
    with get_db_connection() as con:
        cur = con.cursor()
        
        for booking_id in booking_ids:
            try:
                # Check if booking exists before deleting
                cur.execute("SELECT id FROM bookings WHERE id = ?", (booking_id,))
                if cur.fetchone():
                    # Delete customers first for group bookings
                    cur.execute("DELETE FROM booking_customers WHERE booking_id = ?", (booking_id,))
                    # Delete the booking
                    cur.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
                    if cur.rowcount > 0:
                        deleted_count += 1
            except sqlite3.Error as e:
                print(f"Error deleting booking {booking_id}: {e}")
                continue
        
        con.commit()
    
    if deleted_count == 0:
        return False, 'No bookings were deleted', 0
    
    elif deleted_count == 1:
        return True, '1 booking has been deleted successfully', deleted_count
    else:
        return True, f'{deleted_count} bookings have been deleted successfully', deleted_count


# Configuration Management Functions

def get_config_value(key: str, default_value: str = None) -> str:
    """Get a configuration value by key"""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT config_value FROM app_config WHERE config_key = ?", (key,))
        result = cur.fetchone()
        return result[0] if result else default_value


def set_config_value(key: str, value: str, config_type: str = 'string', 
                    category: str = 'general', description: str = '', 
                    is_sensitive: bool = False) -> bool:
    """Set a configuration value"""
    with get_db_connection() as con:
        cur = con.cursor()
        
        # Check if key exists
        cur.execute("SELECT id FROM app_config WHERE config_key = ?", (key,))
        exists = cur.fetchone()
        
        if exists:
            # Update existing
            cur.execute("""UPDATE app_config 
                          SET config_value = ?, config_type = ?, category = ?, 
                              description = ?, is_sensitive = ?, updated_at = CURRENT_TIMESTAMP 
                          WHERE config_key = ?""", 
                       (value, config_type, category, description, int(is_sensitive), key))
        else:
            # Insert new
            cur.execute("""INSERT INTO app_config 
                          (config_key, config_value, config_type, category, description, is_sensitive) 
                          VALUES (?, ?, ?, ?, ?, ?)""", 
                       (key, value, config_type, category, description, int(is_sensitive)))
        
        con.commit()
        return True


def get_all_config(category: str = None) -> List[Dict[str, Any]]:
    """Get all configuration values, optionally filtered by category"""
    with get_db_connection() as con:
        cur = con.cursor()
        
        if category:
            cur.execute("""SELECT config_key, config_value, config_type, category, 
                                 description, is_sensitive, created_at, updated_at 
                          FROM app_config WHERE category = ? 
                          ORDER BY category, config_key""", (category,))
        else:
            cur.execute("""SELECT config_key, config_value, config_type, category, 
                                 description, is_sensitive, created_at, updated_at 
                          FROM app_config 
                          ORDER BY category, config_key""")
        
        return [dict(row) for row in cur.fetchall()]


def get_config_categories() -> List[str]:
    """Get all configuration categories"""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT DISTINCT category FROM app_config ORDER BY category")
        return [row[0] for row in cur.fetchall()]


def delete_config(key: str) -> bool:
    """Delete a configuration value"""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM app_config WHERE config_key = ?", (key,))
        con.commit()
        return cur.rowcount > 0


def delete_all_config() -> bool:
    """Delete all configuration values"""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM app_config")
        con.commit()
        return cur.rowcount >= 0


def get_all_bookings_for_export() -> List[Dict[str, Any]]:
    """Get all bookings for export purposes"""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute('''SELECT b.*, 
                              GROUP_CONCAT(bc.customer_name, '; ') as all_customer_names,
                              GROUP_CONCAT(bc.customer_email, '; ') as all_customer_emails,
                              GROUP_CONCAT(bc.customer_phone, '; ') as all_customer_phones
                       FROM bookings b 
                       LEFT JOIN booking_customers bc ON b.id = bc.booking_id 
                       GROUP BY b.id 
                       ORDER BY b.date DESC''')
        return [dict(row) for row in cur.fetchall()]


def initialize_default_config():
    """Initialize default configuration values"""
    default_configs = [
        # Business Information
        ('agency_name', 'Himanshi Travels', 'string', 'business', 'Travel agency name'),
        ('agency_tagline', 'Your Journey, Our Passion', 'string', 'business', 'Agency tagline'),
        ('gstin', '29ABCDE1234F2Z5', 'string', 'business', 'GST identification number'),
        ('agency_address', '123 Travel Street, Adventure City, State 123456', 'string', 'business', 'Business address'),
        ('agency_phone', '+91 98765 43210', 'string', 'business', 'Contact phone number'),
        ('agency_email', 'info@himanshitravels.com', 'string', 'business', 'Contact email address'),
        ('gst_percent', '5', 'number', 'business', 'GST percentage to apply'),
        
        # WhatsApp Configuration
        ('whatsapp_enabled', 'true', 'boolean', 'whatsapp', 'Enable WhatsApp messaging'),
        ('whatsapp_send_on_booking', 'true', 'boolean', 'whatsapp', 'Send WhatsApp automatically on booking creation'),
        ('whatsapp_send_to_group_customers', 'false', 'boolean', 'whatsapp', 'Send individual WhatsApp to each customer in group bookings'),
        ('whatsapp_provider', 'mock', 'string', 'whatsapp', 'WhatsApp provider (mock, twilio, green_api, business_api)'),
        
        # Twilio Configuration
        ('twilio_account_sid', '', 'string', 'twilio', 'Twilio Account SID', True),
        ('twilio_auth_token', '', 'string', 'twilio', 'Twilio Auth Token', True),
        ('twilio_whatsapp_number', '+14155238886', 'string', 'twilio', 'Twilio WhatsApp number'),
        
        # Green API Configuration
        ('green_api_instance_id', '', 'string', 'green_api', 'Green API Instance ID', True),
        ('green_api_token', '', 'string', 'green_api', 'Green API Token', True),
        
        # Application Settings
        ('app_debug', 'false', 'boolean', 'app', 'Enable debug mode'),
        ('app_port', '8081', 'number', 'app', 'Application port'),
        ('backup_enabled', 'true', 'boolean', 'app', 'Enable automatic database backups'),
        ('backup_frequency', 'daily', 'string', 'app', 'Backup frequency (daily, weekly, monthly)'),
        
        # Email Configuration (for future use)
        ('email_enabled', 'false', 'boolean', 'email', 'Enable email notifications'),
        ('smtp_server', '', 'string', 'email', 'SMTP server address'),
        ('smtp_port', '587', 'number', 'email', 'SMTP server port'),
        ('smtp_username', '', 'string', 'email', 'SMTP username', True),
        ('smtp_password', '', 'string', 'email', 'SMTP password', True),
    ]
    
    for key, value, config_type, category, description, *is_sensitive in default_configs:
        sensitive = is_sensitive[0] if is_sensitive else False
        # Only set if not already exists
        if not get_config_value(key):
            set_config_value(key, value, config_type, category, description, sensitive)
