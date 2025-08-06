"""
Utility functions for Himanshi Travels application
"""

import re
from typing import Dict, Any, List, Tuple


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip()
    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone or not isinstance(phone, str):
        return False
    
    phone = phone.strip()
    # Remove common separators and check if it's numeric
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    return clean_phone.isdigit() and len(clean_phone) >= 10


def sanitize_string(value: str) -> str:
    """Sanitize string input"""
    if not value or not isinstance(value, str):
        return ''
    return value.strip()


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"₹ {amount:.2f}"


def format_booking_id(booking_id: int) -> str:
    """Format booking ID with leading zeros"""
    return f"#{str(booking_id).zfill(6)}"


def clean_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and sanitize form data"""
    cleaned_data = {}
    
    for key, value in form_data.items():
        if isinstance(value, str):
            cleaned_data[key] = sanitize_string(value)
        else:
            cleaned_data[key] = value
    
    return cleaned_data


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
    """Validate that all required fields are present and not empty"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f'Missing required field: {field}'
    
    return True, ''


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def get_booking_type_specific_fields(booking_type: str) -> List[str]:
    """Get fields specific to a booking type"""
    hotel_fields = ['hotel_name', 'hotel_city']
    travel_fields = ['operator_name', 'from_journey', 'to_journey']
    
    if booking_type == 'Hotel':
        return hotel_fields
    elif booking_type in ['Flight', 'Train', 'Bus', 'Transport']:
        return travel_fields
    else:
        return []


def format_customer_contact(email: str, phone: str) -> str:
    """Format customer contact information for display"""
    contact_parts = []
    if email and email.strip():
        contact_parts.append(email.strip())
    if phone and phone.strip():
        contact_parts.append(phone.strip())
    
    return '\n'.join(contact_parts) if contact_parts else '-'


def calculate_pagination_range(current_page: int, total_pages: int, max_visible: int = 5) -> List[int]:
    """Calculate pagination range for display"""
    if total_pages <= max_visible:
        return list(range(1, total_pages + 1))
    
    start = max(1, current_page - max_visible // 2)
    end = min(total_pages, start + max_visible - 1)
    
    # Adjust start if we're near the end
    if end - start + 1 < max_visible:
        start = max(1, end - max_visible + 1)
    
    return list(range(start, end + 1))
