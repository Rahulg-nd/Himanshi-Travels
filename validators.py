"""
Validation functions for Himanshi Travels application
"""

from typing import Dict, Any, List, Tuple
from utils import validate_email, validate_phone, safe_float_conversion


class BookingValidator:
    """Validator class for booking data"""
    
    @staticmethod
    def validate_single_booking(form_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate single customer booking data"""
        required_fields = ['name', 'phone', 'booking_type', 'base_amount']
        
        # Check required fields
        for field in required_fields:
            value = form_data.get(field)
            
            if field == 'base_amount':
                # For numeric fields, check if it exists and is valid
                if value is None or safe_float_conversion(value) <= 0:
                    return False, f'Missing or invalid field: {field}'
            else:
                # For string fields, check if it exists and is not empty after stripping
                if not value or not str(value).strip():
                    return False, f'Missing required field: {field}'
        
        # Validate email format if provided
        email = form_data.get('email', '')
        if email and not validate_email(str(email).strip()):
            return False, 'Please enter a valid email address'
        
        # Validate phone number
        if not validate_phone(str(form_data['phone']).strip()):
            return False, 'Please enter a valid phone number (minimum 10 digits)'
        
        # Validate base amount
        base_amount = safe_float_conversion(form_data['base_amount'])
        if base_amount <= 0:
            return False, 'Base amount must be greater than 0'
        
        return True, ''
    
    @staticmethod
    def validate_group_booking(form_data: Dict[str, Any], customers: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate group booking data"""
        # Check booking type
        booking_type = form_data.get('booking_type')
        if not booking_type or not str(booking_type).strip():
            return False, 'Missing booking type'
        
        # Check customers
        if not customers:
            return False, 'Group booking must have at least one customer'
        
        # Validate each customer
        for i, customer in enumerate(customers):
            customer_num = i + 1
            
            # Check customer name (can be 'name', 'customer_name')
            customer_name = customer.get('customer_name') or customer.get('name', '')
            if not customer_name or not str(customer_name).strip():
                return False, f'Customer {customer_num} name is required'
            
            # Check customer amount (can be 'amount', 'customer_amount')
            amount = customer.get('customer_amount') or customer.get('amount')
            if safe_float_conversion(amount) <= 0:
                return False, f'Customer {customer_num} amount must be greater than 0'
            
            # Validate email if provided (can be 'email', 'customer_email')
            email = customer.get('customer_email') or customer.get('email', '')
            if email and not validate_email(str(email).strip()):
                return False, f'Customer {customer_num} has invalid email format'
            
            # Validate phone if provided (can be 'phone', 'customer_phone')
            phone = customer.get('customer_phone') or customer.get('phone', '')
            if phone and not validate_phone(str(phone).strip()):
                return False, f'Customer {customer_num} has invalid phone number'
        
        return True, ''
    
    @staticmethod
    def validate_booking_update(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate booking update data"""
        is_group_booking = data.get('is_group_booking', False)
        customers = data.get('customers', [])
        
        if is_group_booking:
            return BookingValidator.validate_group_booking(data, customers)
        else:
            return BookingValidator.validate_single_booking(data)


class SearchValidator:
    """Validator class for search parameters"""
    
    @staticmethod
    def validate_search_params(query: str, booking_type: str, page: int, per_page: int) -> Tuple[bool, str]:
        """Validate search parameters"""
        # Validate page number
        if page < 1:
            return False, 'Page number must be greater than 0'
        
        # Validate per_page
        if per_page < 1 or per_page > 100:
            return False, 'Items per page must be between 1 and 100'
        
        # Validate booking type if provided
        valid_booking_types = ['Hotel', 'Flight', 'Train', 'Bus', 'Transport']
        if booking_type and booking_type not in valid_booking_types:
            return False, f'Invalid booking type. Must be one of: {", ".join(valid_booking_types)}'
        
        return True, ''


class PDFValidator:
    """Validator class for PDF generation"""
    
    @staticmethod
    def validate_booking_for_pdf(booking: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate booking data for PDF generation"""
        required_fields = ['id', 'name', 'phone', 'booking_type', 'base_amount', 'gst', 'total', 'date']
        
        for field in required_fields:
            if field not in booking:
                return False, f'Missing required field for PDF: {field}'
        
        # Validate amounts
        for amount_field in ['base_amount', 'gst', 'total']:
            if not isinstance(booking[amount_field], (int, float)) or booking[amount_field] < 0:
                return False, f'Invalid {amount_field} for PDF generation'
        
        return True, ''
