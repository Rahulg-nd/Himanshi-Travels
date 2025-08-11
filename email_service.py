"""
Email Service for Himanshi Travels
Provides email notification functionality using configuration settings
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class EmailService:
    """Email service using SMTP configuration"""
    
    def __init__(self):
        self.config = None
        self._initialized = False
    
    def _init_config(self):
        """Initialize email configuration"""
        if self._initialized:
            return
            
        try:
            from dynamic_config import config
            self.config = config
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize email config: {e}")
            self._initialized = False
    
    def is_enabled(self) -> bool:
        """Check if email is enabled"""
        self._init_config()
        if not self.config:
            return False
        return self.config.get_bool('EMAIL_ENABLED', False)
    
    def get_smtp_config(self) -> Dict[str, Any]:
        """Get SMTP configuration"""
        self._init_config()
        if not self.config:
            return {}
            
        return {
            'server': self.config.get_str('SMTP_HOST', ''),
            'port': self.config.get_int('SMTP_PORT', 587),
            'username': self.config.get_str('SMTP_USERNAME', ''),
            'password': self.config.get_str('SMTP_PASSWORD', ''),
            'use_tls': True,  # Always use TLS for security
            'from_email': self.config.get_str('FROM_EMAIL', '') or self.config.get_str('SMTP_USERNAME', ''),
        }
    
    def send_email(self, to_emails: List[str], subject: str, body: str, 
                   is_html: bool = False, attachments: Optional[List[str]] = None) -> bool:
        """Send email to recipients"""
        if not self.is_enabled():
            logger.info("Email service is disabled")
            return False
            
        smtp_config = self.get_smtp_config()
        
        # Validate configuration
        if not all([smtp_config['server'], smtp_config['username'], smtp_config['password']]):
            logger.error("Incomplete SMTP configuration")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
                    else:
                        logger.warning(f"Attachment not found: {file_path}")
            
            # Send email
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                if smtp_config['use_tls']:
                    server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_booking_notification(self, booking_data: Dict[str, Any], 
                                 pdf_path: Optional[str] = None) -> bool:
        """Send booking confirmation email"""
        if not booking_data.get('email'):
            logger.info("No email address provided for booking notification")
            return False
        
        # Get business configuration
        from dynamic_config import agency_name, agency_email
        
        subject = f"Booking Confirmation - {booking_data.get('booking_type', 'Travel Service')}"
        
        # Create email body
        body = f"""
Dear {booking_data.get('name', 'Customer')},

Thank you for choosing {agency_name()}! Your booking has been confirmed.

Booking Details:
- Booking ID: {booking_data.get('id', 'N/A')}
- Service Type: {booking_data.get('booking_type', 'N/A')}
- Total Amount: ₹{booking_data.get('total', 0):.2f}
- Date: {booking_data.get('date', 'N/A')}

A detailed invoice is attached to this email.

For any queries, please contact us at {agency_email()}.

Best regards,
{agency_name()} Team
"""
        
        attachments = [pdf_path] if pdf_path and os.path.exists(pdf_path) else []
        
        return self.send_email(
            to_emails=[booking_data['email']],
            subject=subject,
            body=body,
            attachments=attachments
        )
    
    def test_email_configuration(self, test_email: str) -> Dict[str, Any]:
        """Test email configuration by sending a test email"""
        if not self.is_enabled():
            return {
                'success': False,
                'message': 'Email service is disabled'
            }
        
        smtp_config = self.get_smtp_config()
        if not all([smtp_config['server'], smtp_config['username'], smtp_config['password']]):
            return {
                'success': False,
                'message': 'Incomplete SMTP configuration'
            }
        
        try:
            # Get business info
            from dynamic_config import agency_name
            
            subject = f"Test Email from {agency_name()}"
            body = f"""
This is a test email from {agency_name()} booking system.

If you received this email, your email configuration is working correctly!

Configuration Details:
- SMTP Server: {smtp_config['server']}
- SMTP Port: {smtp_config['port']}
- Username: {smtp_config['username']}

Test sent at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            success = self.send_email([test_email], subject, body)
            
            if success:
                return {
                    'success': True,
                    'message': f'Test email sent successfully to {test_email}'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to send test email'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Email test failed: {str(e)}'
            }

# Global email service instance
email_service = EmailService()

def send_booking_email(booking_data: Dict[str, Any], pdf_path: Optional[str] = None) -> bool:
    """Convenience function to send booking email"""
    return email_service.send_booking_notification(booking_data, pdf_path)

def test_email_config(test_email: str) -> Dict[str, Any]:
    """Convenience function to test email configuration"""
    return email_service.test_email_configuration(test_email)
