"""
WhatsApp messaging service for Himanshi Travels application
Supports multiple WhatsApp API providers
"""

import logging
from typing import Tuple, Optional
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppProvider(ABC):
    """Abstract base class for WhatsApp providers"""
    
    @abstractmethod
    def send_message(self, phone: str, message: str) -> Tuple[bool, str]:
        """Send WhatsApp message to phone number"""
        pass
    
    @abstractmethod
    def send_document(self, phone: str, message: str, file_path: str, filename: str = None) -> Tuple[bool, str]:
        """Send WhatsApp message with document attachment"""
        pass


class MockWhatsAppProvider(WhatsAppProvider):
    """Mock WhatsApp provider for testing"""
    
    def send_message(self, phone: str, message: str) -> Tuple[bool, str]:
        logger.info(f"MOCK WHATSAPP to {phone}: {message}")
        return True, "Mock WhatsApp message sent successfully"
    
    def send_document(self, phone: str, message: str, file_path: str, filename: str = None) -> Tuple[bool, str]:
        import os
        filename = filename or os.path.basename(file_path)
        logger.info(f"MOCK WHATSAPP DOCUMENT to {phone}: {message}")
        logger.info(f"MOCK WHATSAPP ATTACHMENT: {filename} ({file_path})")
        return True, f"Mock WhatsApp message with attachment '{filename}' sent successfully"


class TwilioWhatsAppProvider(WhatsAppProvider):
    """Twilio WhatsApp provider"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number  # Must be whatsapp:+14155238886 format
        
    def send_message(self, phone: str, message: str) -> Tuple[bool, str]:
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # Format phone numbers for WhatsApp
            to_whatsapp = f"whatsapp:{phone}"
            from_whatsapp = f"whatsapp:{self.from_number}"
            
            message_instance = client.messages.create(
                body=message,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            
            logger.info(f"WhatsApp message sent via Twilio to {phone}, SID: {message_instance.sid}")
            return True, f"Message sent successfully via Twilio WhatsApp, SID: {message_instance.sid}"
            
        except ImportError:
            return False, "Twilio library not installed. Run: pip install twilio"
        except Exception as e:
            logger.error(f"Twilio WhatsApp message failed: {str(e)}")
            return False, f"Failed to send WhatsApp message: {str(e)}"
    
    def send_document(self, phone: str, message: str, file_path: str, filename: str = None) -> Tuple[bool, str]:
        try:
            from twilio.rest import Client
            import os
            
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            client = Client(self.account_sid, self.auth_token)
            
            # Format phone numbers for WhatsApp
            to_whatsapp = f"whatsapp:{phone}"
            from_whatsapp = f"whatsapp:{self.from_number}"
            
            # Create a publicly accessible URL for the file (you might need to implement file hosting)
            # For now, sending as text message with file info
            filename = filename or os.path.basename(file_path)
            combined_message = f"{message}\n\n📎 Invoice: {filename}"
            
            message_instance = client.messages.create(
                body=combined_message,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            
            logger.info(f"WhatsApp document message sent via Twilio to {phone}, SID: {message_instance.sid}")
            return True, f"Message with document reference sent via Twilio WhatsApp, SID: {message_instance.sid}"
            
        except ImportError:
            return False, "Twilio library not installed. Run: pip install twilio"
        except Exception as e:
            logger.error(f"Twilio WhatsApp document message failed: {str(e)}")
            return False, f"Failed to send WhatsApp document: {str(e)}"


class WhatsAppBusinessAPIProvider(WhatsAppProvider):
    """WhatsApp Business API provider (Meta/Facebook)"""
    
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        
    def send_message(self, phone: str, message: str) -> Tuple[bool, str]:
        try:
            import requests
            
            # Clean phone number (remove + and spaces)
            clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            result = response.json()
            
            if response.status_code == 200 and 'messages' in result:
                message_id = result['messages'][0]['id']
                logger.info(f"WhatsApp message sent via Business API to {clean_phone}, ID: {message_id}")
                return True, f"Message sent successfully via WhatsApp Business API, ID: {message_id}"
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                logger.error(f"WhatsApp Business API failed: {error_msg}")
                return False, f"Failed to send WhatsApp message: {error_msg}"
                
        except ImportError:
            return False, "Requests library not installed"
        except Exception as e:
            logger.error(f"WhatsApp Business API failed: {str(e)}")
            return False, f"Failed to send WhatsApp message: {str(e)}"
    
    def send_document(self, phone: str, message: str, file_path: str, filename: str = None) -> Tuple[bool, str]:
        try:
            import requests
            import os
            
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            # Clean phone number (remove + and spaces)
            clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            filename = filename or os.path.basename(file_path)
            
            # First upload the media file
            upload_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/media"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            files = {
                'file': (filename, open(file_path, 'rb'), 'application/pdf'),
                'type': (None, 'document'),
                'messaging_product': (None, 'whatsapp')
            }
            
            upload_response = requests.post(upload_url, headers=headers, files=files, timeout=30)
            upload_result = upload_response.json()
            
            files['file'][1].close()  # Close the file
            
            if upload_response.status_code != 200 or 'id' not in upload_result:
                error_msg = upload_result.get('error', {}).get('message', 'Media upload failed')
                return False, f"Failed to upload document: {error_msg}"
            
            media_id = upload_result['id']
            
            # Now send the message with document
            message_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "document",
                "document": {
                    "id": media_id,
                    "caption": message,
                    "filename": filename
                }
            }
            
            response = requests.post(message_url, json=data, headers=headers, timeout=30)
            result = response.json()
            
            if response.status_code == 200 and 'messages' in result:
                message_id = result['messages'][0]['id']
                logger.info(f"WhatsApp document sent via Business API to {clean_phone}, ID: {message_id}")
                return True, f"Document sent successfully via WhatsApp Business API, ID: {message_id}"
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                logger.error(f"WhatsApp Business API document failed: {error_msg}")
                return False, f"Failed to send WhatsApp document: {error_msg}"
                
        except ImportError:
            return False, "Requests library not installed"
        except Exception as e:
            logger.error(f"WhatsApp Business API document failed: {str(e)}")
            return False, f"Failed to send WhatsApp document: {str(e)}"


class GreenAPIProvider(WhatsAppProvider):
    """Green API WhatsApp provider (Indian service)"""
    
    def __init__(self, instance_id: str, api_token: str):
        self.instance_id = instance_id
        self.api_token = api_token
        
    def send_message(self, phone: str, message: str) -> Tuple[bool, str]:
        try:
            import requests
            
            # Clean phone number and add country code if needed
            clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            if not clean_phone.startswith("91") and len(clean_phone) == 10:
                clean_phone = "91" + clean_phone
            
            url = f"https://api.green-api.com/waInstance{self.instance_id}/sendMessage/{self.api_token}"
            
            data = {
                "chatId": f"{clean_phone}@c.us",
                "message": message
            }
            
            response = requests.post(url, json=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200 and result.get('idMessage'):
                message_id = result['idMessage']
                logger.info(f"WhatsApp message sent via Green API to {clean_phone}, ID: {message_id}")
                return True, f"Message sent successfully via Green API, ID: {message_id}"
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Green API failed: {error_msg}")
                return False, f"Failed to send WhatsApp message: {error_msg}"
                
        except ImportError:
            return False, "Requests library not installed"
        except Exception as e:
            logger.error(f"Green API failed: {str(e)}")
            return False, f"Failed to send WhatsApp message: {str(e)}"
    
    def send_document(self, phone: str, message: str, file_path: str, filename: str = None) -> Tuple[bool, str]:
        try:
            import requests
            import base64
            import os
            
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            # Clean phone number and add country code if needed
            clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            if not clean_phone.startswith("91") and len(clean_phone) == 10:
                clean_phone = "91" + clean_phone
            
            filename = filename or os.path.basename(file_path)
            
            # Read and encode file as base64
            with open(file_path, 'rb') as file:
                file_content = base64.b64encode(file.read()).decode('utf-8')
            
            url = f"https://api.green-api.com/waInstance{self.instance_id}/sendFileByUpload/{self.api_token}"
            
            data = {
                "chatId": f"{clean_phone}@c.us",
                "file": file_content,
                "fileName": filename,
                "caption": message
            }
            
            response = requests.post(url, json=data, timeout=60)  # Longer timeout for file upload
            result = response.json()
            
            if response.status_code == 200 and result.get('idMessage'):
                message_id = result['idMessage']
                logger.info(f"WhatsApp document sent via Green API to {clean_phone}, ID: {message_id}")
                return True, f"Document sent successfully via Green API, ID: {message_id}"
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Green API document failed: {error_msg}")
                return False, f"Failed to send WhatsApp document: {error_msg}"
                
        except ImportError:
            return False, "Requests library not installed"
        except Exception as e:
            logger.error(f"Green API document failed: {str(e)}")
            return False, f"Failed to send WhatsApp document: {str(e)}"


# Global WhatsApp service instance
whatsapp_service: Optional[WhatsAppProvider] = None


def get_whatsapp_service() -> WhatsAppProvider:
    """Get configured WhatsApp service instance"""
    global whatsapp_service
    
    if whatsapp_service is None:
        whatsapp_service = create_whatsapp_service()
    
    return whatsapp_service


def create_whatsapp_service() -> WhatsAppProvider:
    """Create WhatsApp service based on configuration"""
    provider = dynamic_config.config.get_str('WHATSAPP_PROVIDER', 'mock').lower()
    
    try:
        if provider == 'twilio':
            account_sid = dynamic_config.config.get_str('TWILIO_ACCOUNT_SID', '')
            auth_token = dynamic_config.config.get_str('TWILIO_AUTH_TOKEN', '')
            from_number = dynamic_config.config.get_str('TWILIO_WHATSAPP_NUMBER', '')
            
            if account_sid and auth_token and from_number:
                return TwilioWhatsAppProvider(account_sid, auth_token, from_number)
            else:
                logger.warning("Twilio WhatsApp credentials not configured. Using mock provider.")
                
        elif provider == 'business_api':
            access_token = dynamic_config.config.get_str('WHATSAPP_ACCESS_TOKEN', '')
            phone_number_id = dynamic_config.config.get_str('WHATSAPP_PHONE_NUMBER_ID', '')
            
            if access_token and phone_number_id:
                return WhatsAppBusinessAPIProvider(access_token, phone_number_id)
            else:
                logger.warning("WhatsApp Business API credentials not configured. Using mock provider.")
                
        elif provider == 'green_api':
            instance_id = dynamic_config.config.get_str('GREEN_API_INSTANCE_ID', '')
            api_token = dynamic_config.config.get_str('GREEN_API_TOKEN', '')
            
            if instance_id and api_token:
                return GreenAPIProvider(instance_id, api_token)
            else:
                logger.warning("Green API credentials not configured. Using mock provider.")
                
        elif provider == 'mock':
            logger.info("Using mock WhatsApp provider for testing.")
        else:
            logger.warning(f"Unknown WhatsApp provider: {provider}. Using mock provider.")
            
    except Exception as e:
        logger.error(f"Error creating WhatsApp service: {str(e)}. Using mock provider.")
    
    logger.warning("No WhatsApp provider configured. Using mock provider.")
    return MockWhatsAppProvider()


# Import dynamic config module
import dynamic_config


def send_booking_whatsapp(booking_data: dict, customers: list) -> Tuple[bool, str]:
    """Send WhatsApp message for booking confirmation"""
    try:
        service = get_whatsapp_service()
        
        if not customers:
            return False, "No customer data provided"
        
        # Get primary customer (first customer for group bookings)
        primary_customer = customers[0]
        customer_name = primary_customer.get('name', 'Customer')
        customer_phone = primary_customer.get('phone', '')
        
        if not customer_phone:
            return False, "No phone number provided"
        
        # Format booking details
        booking_id = booking_data.get('id', 'N/A')
        booking_type = 'group' if len(customers) > 1 else 'single'
        total_amount = booking_data.get('total', booking_data.get('amount', '0'))
        
        # Create WhatsApp message
        message = f"""🎉 *Booking Confirmed - Himanshi Travels*

Dear {customer_name},

Your {booking_type} booking is confirmed! ✅

📋 *Booking Details:*
🆔 Booking ID: #{str(booking_id).zfill(6)}
💰 Amount: ₹{total_amount}

📞 For queries, call: +91 98765 43210
✉️ Email: info@himanshitravels.com

Thank you for choosing *Himanshi Travels* 🚗
_Your Journey, Our Passion_"""
        
        # Send WhatsApp message
        success, response = service.send_message(customer_phone, message)
        
        if success:
            logger.info(f"WhatsApp message sent successfully for booking {booking_id}")
            return True, response
        else:
            logger.error(f"WhatsApp message failed for booking {booking_id}: {response}")
            return False, response
            
    except Exception as e:
        logger.error(f"Error sending booking WhatsApp: {str(e)}")
        return False, f"Error sending WhatsApp message: {str(e)}"


def send_booking_whatsapp_with_pdf(booking_data: dict, customers: list, pdf_path: str) -> Tuple[bool, str]:
    """Send WhatsApp message for booking confirmation with PDF invoice attachment"""
    try:
        service = get_whatsapp_service()
        
        if not customers:
            return False, "No customer data provided"
        
        # Get primary customer (first customer for group bookings)
        primary_customer = customers[0]
        customer_name = primary_customer.get('name', 'Customer')
        customer_phone = primary_customer.get('phone', '')
        
        if not customer_phone:
            return False, "No phone number provided"
        
        # Format booking details
        booking_id = booking_data.get('id', 'N/A')
        booking_type = 'group' if len(customers) > 1 else 'single'
        total_amount = booking_data.get('total', booking_data.get('amount', '0'))
        
        # Create WhatsApp message
        message = f"""🎉 *Booking Confirmed - Himanshi Travels*

Dear {customer_name},

Your {booking_type} booking is confirmed! ✅

📋 *Booking Details:*
🆔 Booking ID: #{str(booking_id).zfill(6)}
💰 Amount: ₹{total_amount}

📄 Please find your invoice attached.

📞 For queries, call: +91 98765 43210
✉️ Email: info@himanshitravels.com

Thank you for choosing *Himanshi Travels* 🚗
_Your Journey, Our Passion_"""
        
        # Generate PDF filename
        invoice_filename = f"Invoice_{str(booking_id).zfill(6)}.pdf"
        
        # Send WhatsApp message with PDF attachment
        success, response = service.send_document(customer_phone, message, pdf_path, invoice_filename)
        
        if success:
            logger.info(f"WhatsApp message with PDF sent successfully for booking {booking_id}")
            return True, response
        else:
            logger.error(f"WhatsApp message with PDF failed for booking {booking_id}: {response}")
            return False, response
            
    except Exception as e:
        logger.error(f"Error sending booking WhatsApp with PDF: {str(e)}")
        return False, f"Error sending WhatsApp message with PDF: {str(e)}"


def send_custom_whatsapp(phone: str, message: str) -> Tuple[bool, str]:
    """Send custom WhatsApp message"""
    try:
        service = get_whatsapp_service()
        
        if not phone:
            return False, "Phone number is required"
        
        if not message:
            return False, "Message is required"
        
        # Add Himanshi Travels branding to custom messages
        formatted_message = f"""*Himanshi Travels* 🚗

{message}

📞 Contact: +91 98765 43210
✉️ Email: info@himanshitravels.com"""
        
        success, response = service.send_message(phone, formatted_message)
        
        if success:
            logger.info(f"Custom WhatsApp message sent successfully to {phone}")
        else:
            logger.error(f"Custom WhatsApp message failed to {phone}: {response}")
        
        return success, response
        
    except Exception as e:
        logger.error(f"Error sending custom WhatsApp: {str(e)}")
        return False, f"Error sending WhatsApp message: {str(e)}"


# Test function
def test_whatsapp_service():
    """Test WhatsApp service configuration"""
    try:
        service = get_whatsapp_service()
        provider_name = service.__class__.__name__
        
        test_phone = "+91 9876543210"
        test_message = "Test WhatsApp message from Himanshi Travels!"
        
        success, response = service.send_message(test_phone, test_message)
        
        return {
            'provider': provider_name,
            'test_success': success,
            'test_response': response,
            'whatsapp_enabled': dynamic_config.whatsapp_enabled(),
            'auto_send_on_booking': dynamic_config.config.get_bool('WHATSAPP_SEND_ON_BOOKING', False)
        }
        
    except Exception as e:
        return {
            'provider': 'Unknown',
            'test_success': False,
            'test_response': str(e),
            'whatsapp_enabled': False,
            'auto_send_on_booking': False
        }
