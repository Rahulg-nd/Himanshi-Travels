"""
Business logic for Himanshi Travels booking operations
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from dynamic_config import gst_percent, whatsapp_enabled, whatsapp_send_on_booking
import dynamic_config

# Initialize constants for backward compatibility  
dynamic_config.init_module_constants()
GST_PERCENT = dynamic_config.GST_PERCENT
WHATSAPP_ENABLED = dynamic_config.WHATSAPP_ENABLED
WHATSAPP_SEND_ON_BOOKING = dynamic_config.WHATSAPP_SEND_ON_BOOKING
from database import create_booking, create_booking_customers
from validators import BookingValidator
from utils import clean_form_data, safe_float_conversion
from email_service import send_booking_email


def calculate_totals(base_amount: float, apply_gst: bool = True) -> Tuple[float, float]:
    """Calculate GST and total amount"""
    if apply_gst:
        gst = round((base_amount * GST_PERCENT) / 100, 2)
        total = base_amount + gst
    else:
        gst = 0.0
        total = base_amount
    return gst, total


def process_single_booking(form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
    """Process a single customer booking"""
    # Clean and validate data
    clean_data = clean_form_data(form_data)
    is_valid, error_msg = BookingValidator.validate_single_booking(clean_data)
    if not is_valid:
        return False, error_msg, None
    
    # Extract and clean data
    name = form_data['name'].strip()
    email = form_data.get('email', '').strip() or None
    phone = form_data['phone'].strip()
    booking_type = form_data['booking_type']
    base_amount = float(form_data['base_amount'])
    customer_address = form_data.get('customer_address', '').strip() or None
    apply_gst = form_data.get('apply_gst') == 'on'  # Checkbox value
    
    # Calculate totals
    gst, total = calculate_totals(base_amount, apply_gst)
    
    # Prepare booking data
    booking_data = {
        'name': name,
        'email': email,
        'phone': phone,
        'booking_type': booking_type,
        'base_amount': base_amount,
        'gst': gst,
        'total': total,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'hotel_name': form_data.get('hotel_name', '').strip() or None,
        'hotel_city': form_data.get('hotel_city', '').strip() or None,
        'hotel_country': form_data.get('hotel_country', '').strip() or None,
        'operator_name': form_data.get('operator_name', '').strip() or None,
        'from_journey': form_data.get('from_journey', '').strip() or None,
        'from_journey_country': form_data.get('from_journey_country', '').strip() or None,
        'to_journey': form_data.get('to_journey', '').strip() or None,
        'to_journey_country': form_data.get('to_journey_country', '').strip() or None,
        'vehicle_number': form_data.get('vehicle_number', '').strip() or None,
        'service_date': form_data.get('service_date', '').strip() or None,
        'service_time': form_data.get('service_time', '').strip() or None,
        'customer_address': customer_address,
        'apply_gst': 1 if apply_gst else 0,
        'is_group_booking': 0
    }
    
    try:
        booking_id = create_booking(booking_data)
        
        # Send WhatsApp if enabled
        if WHATSAPP_ENABLED and WHATSAPP_SEND_ON_BOOKING:
            try:
                from whatsapp_service import send_booking_whatsapp_with_pdf
                from database import get_booking_by_id
                from pdf_generator import generate_invoice_pdf
                
                # Get the created booking details
                created_booking = get_booking_by_id(booking_id)
                if created_booking:
                    customers = [{'name': created_booking['name'], 'phone': created_booking['phone']}]
                    
                    # Generate PDF invoice
                    try:
                        pdf_path = generate_invoice_pdf(booking_id, created_booking, customers)
                        success, message = send_booking_whatsapp_with_pdf(created_booking, customers, pdf_path)
                        if success:
                            print(f"WhatsApp message with PDF sent successfully for booking {booking_id}")
                        else:
                            print(f"WhatsApp with PDF failed for booking {booking_id}: {message}")
                    except Exception as pdf_error:
                        print(f"PDF generation failed for booking {booking_id}: {str(pdf_error)}")
                        # Fallback to sending message without PDF
                        from whatsapp_service import send_booking_whatsapp
                        success, message = send_booking_whatsapp(created_booking, customers)
                        if success:
                            print(f"WhatsApp message (without PDF) sent successfully for booking {booking_id}")
                        else:
                            print(f"WhatsApp failed for booking {booking_id}: {message}")
            except Exception as whatsapp_error:
                print(f"WhatsApp service error for booking {booking_id}: {str(whatsapp_error)}")
                # Don't fail the booking if WhatsApp fails
        
        # Send email notification if email provided
        try:
            if email and email.strip():
                booking_data = {
                    'id': booking_id,
                    'name': name,
                    'email': email,
                    'booking_type': booking_type,
                    'total': total,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Generate PDF path
                pdf_path = f"bills/invoice_{booking_id}.pdf"
                
                if send_booking_email(booking_data, pdf_path if os.path.exists(pdf_path) else None):
                    print(f"Booking confirmation email sent to {email}")
                else:
                    print(f"Failed to send booking confirmation email to {email}")
        except Exception as email_error:
            print(f"Email service error for booking {booking_id}: {str(email_error)}")
            # Don't fail the booking if email fails
        
        return True, 'Booking created successfully', booking_id
    except Exception as e:
        return False, f'Error creating booking: {str(e)}', None


def process_group_booking(form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
    """Process a group booking with multiple customers"""
    try:
        # Get customers data (JSON string from frontend)
        customers_json = form_data.get('customers_data', '[]')
        customers = json.loads(customers_json)
        
        # Validate data
        is_valid, error_msg = BookingValidator.validate_group_booking(form_data, customers)
        if not is_valid:
            return False, error_msg, None
        
        # Calculate totals
        total_base_amount = sum(float(customer['amount']) for customer in customers)
        apply_gst = form_data.get('apply_gst') == 'on'  # Checkbox value
        total_gst, grand_total = calculate_totals(total_base_amount, apply_gst)
        
        # Use first customer as primary contact
        primary_customer = customers[0]
        customer_address = form_data.get('customer_address', '').strip() or None
        
        # Prepare booking data
        booking_data = {
            'name': primary_customer['name'],
            'email': primary_customer['email'],
            'phone': primary_customer['phone'],
            'booking_type': form_data['booking_type'],
            'base_amount': total_base_amount,
            'gst': total_gst,
            'total': grand_total,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'hotel_name': form_data.get('hotel_name', '').strip() or None,
            'hotel_city': form_data.get('hotel_city', '').strip() or None,
            'hotel_country': form_data.get('hotel_country', '').strip() or None,
            'operator_name': form_data.get('operator_name', '').strip() or None,
            'from_journey': form_data.get('from_journey', '').strip() or None,
            'from_journey_country': form_data.get('from_journey_country', '').strip() or None,
            'to_journey': form_data.get('to_journey', '').strip() or None,
            'to_journey_country': form_data.get('to_journey_country', '').strip() or None,
            'vehicle_number': form_data.get('vehicle_number', '').strip() or None,
            'service_date': form_data.get('service_date', '').strip() or None,
            'service_time': form_data.get('service_time', '').strip() or None,
            'customer_address': customer_address,
            'apply_gst': 1 if apply_gst else 0,
            'is_group_booking': 1
        }
        
        # Create booking
        booking_id = create_booking(booking_data)
        
        # Create customers
        create_booking_customers(booking_id, customers)
        
        # Send WhatsApp if enabled
        if WHATSAPP_ENABLED and WHATSAPP_SEND_ON_BOOKING:
            try:
                from whatsapp_service import send_booking_whatsapp_with_pdf
                from database import get_booking_by_id
                from pdf_generator import generate_invoice_pdf
                
                # Get the created booking details with customers
                created_booking = get_booking_by_id(booking_id)
                if created_booking:
                    # Generate PDF invoice
                    try:
                        pdf_path = generate_invoice_pdf(booking_id, created_booking, customers)
                        success, message = send_booking_whatsapp_with_pdf(created_booking, customers, pdf_path)
                        if success:
                            print(f"Group WhatsApp with PDF sent successfully for booking {booking_id}")
                        else:
                            print(f"Group WhatsApp with PDF failed for booking {booking_id}: {message}")
                    except Exception as pdf_error:
                        print(f"PDF generation failed for group booking {booking_id}: {str(pdf_error)}")
                        # Fallback to sending message without PDF
                        from whatsapp_service import send_booking_whatsapp
                        success, message = send_booking_whatsapp(created_booking, customers)
                        if success:
                            print(f"Group WhatsApp (without PDF) sent successfully for booking {booking_id}")
                        else:
                            print(f"Group WhatsApp failed for booking {booking_id}: {message}")
            except Exception as whatsapp_error:
                print(f"WhatsApp service error for group booking {booking_id}: {str(whatsapp_error)}")
                # Don't fail the booking if WhatsApp fails
        
        # Send email notification to primary customer if email provided
        try:
            if primary_customer.get('email') and primary_customer['email'].strip():
                email_booking_data = {
                    'id': booking_id,
                    'name': primary_customer['name'],
                    'email': primary_customer['email'],
                    'booking_type': form_data['booking_type'],
                    'total': grand_total,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Generate PDF path
                pdf_path = f"bills/invoice_{booking_id}.pdf"
                
                if send_booking_email(email_booking_data, pdf_path if os.path.exists(pdf_path) else None):
                    print(f"Group booking confirmation email sent to {primary_customer['email']}")
                else:
                    print(f"Failed to send group booking confirmation email to {primary_customer['email']}")
        except Exception as email_error:
            print(f"Email service error for group booking {booking_id}: {str(email_error)}")
            # Don't fail the booking if email fails
        
        return True, 'Group booking created successfully', booking_id
        
    except json.JSONDecodeError:
        return False, 'Invalid customer data format', None
    except Exception as e:
        return False, f'Error creating group booking: {str(e)}', None


def process_booking_update(booking_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
    """Process booking update"""
    from database import update_booking
    
    try:
        # Debug: Print the received data
        print(f"Processing booking update for booking {booking_id}")
        print(f"Received data: {data}")
        
        # Validate the update data
        is_valid, error_msg = BookingValidator.validate_booking_update(data)
        if not is_valid:
            print(f"Validation failed: {error_msg}")
            return False, error_msg
        
        # Prepare booking data for update
        is_group_booking = data.get('is_group_booking', False)
        customers = data.get('customers', [])
        
        if is_group_booking:
            base_amount, booking_data = _prepare_group_booking_update(data, customers)
        else:
            base_amount, booking_data = _prepare_single_booking_update(data)
        
        # Calculate GST and total
        gst, total = calculate_totals(base_amount)
        booking_data['gst'] = gst
        booking_data['total'] = total
        
        # Update booking
        success = update_booking(booking_id, booking_data, customers if is_group_booking else None)
        
        if success:
            return True, f'Booking #{str(booking_id).zfill(6)} updated successfully'
        else:
            return False, 'No changes were made'
        
    except Exception as e:
        return False, f'Unexpected error: {str(e)}'


def _prepare_single_booking_update(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Prepare single booking data for update"""
    base_amount = safe_float_conversion(data['base_amount'])
    
    # Helper function to safely convert and strip string values
    def safe_str_strip(value):
        if value is None:
            return None
        return str(value).strip() or None
    
    booking_data = {
        'name': str(data['name']).strip(),
        'email': str(data['email']).strip(),
        'phone': str(data['phone']).strip(),
        'booking_type': str(data['booking_type']).strip(),
        'base_amount': base_amount,
        'hotel_name': safe_str_strip(data.get('hotel_name')),
        'hotel_city': safe_str_strip(data.get('hotel_city')),
        'hotel_country': safe_str_strip(data.get('hotel_country')),
        'operator_name': safe_str_strip(data.get('operator_name')),
        'from_journey': safe_str_strip(data.get('from_journey')),
        'from_journey_country': safe_str_strip(data.get('from_journey_country')),
        'to_journey': safe_str_strip(data.get('to_journey')),
        'to_journey_country': safe_str_strip(data.get('to_journey_country')),
        'service_date': safe_str_strip(data.get('service_date')),
        'service_time': safe_str_strip(data.get('service_time')),
        'vehicle_number': safe_str_strip(data.get('vehicle_train_flight_hotel_number') or data.get('vehicle_number')),
        'is_group_booking': False
    }
    
    return base_amount, booking_data


def _prepare_group_booking_update(data: Dict[str, Any], customers: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
    """Prepare group booking data for update"""
    base_amount = sum(safe_float_conversion(customer.get('customer_amount', 0)) for customer in customers)
    
    # Use first customer's details for main booking record
    first_customer = customers[0] if customers else {}
    
    # Helper function to safely convert and strip string values
    def safe_str_strip(value):
        if value is None:
            return None
        return str(value).strip() or None
    
    booking_data = {
        'name': first_customer.get('customer_name', 'Group Booking'),
        'email': first_customer.get('customer_email', 'group@booking.com'),
        'phone': first_customer.get('customer_phone', '0000000000'),
        'booking_type': str(data['booking_type']).strip(),
        'base_amount': base_amount,
        'hotel_name': safe_str_strip(data.get('hotel_name')),
        'hotel_city': safe_str_strip(data.get('hotel_city')),
        'hotel_country': safe_str_strip(data.get('hotel_country')),
        'operator_name': safe_str_strip(data.get('operator_name')),
        'from_journey': safe_str_strip(data.get('from_journey')),
        'from_journey_country': safe_str_strip(data.get('from_journey_country')),
        'to_journey': safe_str_strip(data.get('to_journey')),
        'to_journey_country': safe_str_strip(data.get('to_journey_country')),
        'service_date': safe_str_strip(data.get('service_date')),
        'service_time': safe_str_strip(data.get('service_time')),
        'vehicle_number': safe_str_strip(data.get('vehicle_train_flight_hotel_number') or data.get('vehicle_number')),
        'is_group_booking': True
    }
    
    return base_amount, booking_data


def get_vehicle_label(booking_type: str) -> str:
    """Get appropriate vehicle label based on booking type"""
    labels = {
        'Hotel': 'Room Number:',
        'Flight': 'Flight Number:',
        'Train': 'Train Number:',
        'Bus': 'Bus Number:',
        'Transport': 'Vehicle Number:'
    }
    return labels.get(booking_type, 'Vehicle Number:')
