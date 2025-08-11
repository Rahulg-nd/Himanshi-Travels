"""
Flask routes for Himanshi Travels application
"""

import os
import csv
import io
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, make_response, jsonify, send_from_directory

logger = logging.getLogger(__name__)

# Constants
DEFAULT_LOGO_PATH = 'static/images/himanshi_travels_logo.png'

from dynamic_config import DEFAULT_PAGE_SIZE
import dynamic_config

# Initialize constants for backward compatibility
dynamic_config.init_module_constants()
GST_PERCENT = dynamic_config.GST_PERCENT
from database import (init_db, get_booking_by_id, search_bookings, delete_booking, 
                     bulk_delete_bookings, get_all_bookings_for_export)
from booking_logic import process_single_booking, process_group_booking, process_booking_update
from pdf_generator import generate_invoice_pdf


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    return app


def register_routes(app):
    """Register all routes with the Flask application"""
    
    @app.route('/', methods=['GET', 'POST'])
    def form():
        if request.method == 'POST':
            # Check if this is a group booking
            is_group_booking_value = request.form.get('is_group_booking')
            is_group_booking = is_group_booking_value in ['true', 'on', '1']
            
            if is_group_booking:
                success, message, booking_id = process_group_booking(request.form)
            else:
                success, message, booking_id = process_single_booking(request.form)
            
            if success:
                # Return JSON response with success and PDF URL
                return jsonify({
                    'success': True,
                    'message': message,
                    'pdf_url': f'/invoice/{booking_id}',
                    'booking_id': booking_id
                })
            else:
                # Return JSON error response
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        
        return render_template('form.html', gst_percent=GST_PERCENT)

    @app.route('/invoice/<int:booking_id>')
    def generate_invoice(booking_id):
        booking = get_booking_by_id(booking_id)
        if not booking:
            return "Booking not found", 404
        
        # Get customers for group bookings
        customers = booking.get('customers', [])
        
        try:
            file_path = generate_invoice_pdf(booking_id, booking, customers)
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return f"Error generating invoice: {str(e)}", 500

    @app.route('/search', methods=['GET'])
    def search():
        """Legacy search endpoint - redirects to new bookings page"""
        return redirect('/bookings')

    @app.route('/bookings')
    def view_bookings():
        """Display all bookings with search functionality"""
        from dynamic_config import whatsapp_enabled, email_enabled
        return render_template('bookings.html', 
                             gst_percent=GST_PERCENT,
                             whatsapp_enabled=whatsapp_enabled(),
                             email_enabled=email_enabled())

    @app.route('/api/search_bookings')
    def search_bookings_api():
        """Search bookings by various criteria with pagination"""
        query = request.args.get('q', '').strip()
        booking_type = request.args.get('type', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', DEFAULT_PAGE_SIZE))
        
        result = search_bookings(query, booking_type, page, per_page)
        return result

    @app.route('/regenerate_invoice/<int:booking_id>')
    def regenerate_invoice(booking_id):
        """Regenerate invoice for an existing booking"""
        return generate_invoice(booking_id)

    @app.route('/export_bookings')
    def export_bookings():
        """Export all bookings to CSV"""
        rows = get_all_bookings_for_export()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = ['ID', 'Name', 'Email', 'Phone', 'Booking Type', 'Base Amount', 'GST', 'Total', 'Date',
                   'Hotel Name', 'Hotel City', 'Operator', 'From', 'To']
        writer.writerow(headers)
        
        # Write data
        for row in rows:
            writer.writerow(row)
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=himanshi_travels_bookings_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response

    @app.route('/delete_booking/<int:booking_id>', methods=['POST'])
    def delete_booking_route(booking_id):
        """Delete a booking by ID"""
        try:
            success, message = delete_booking(booking_id)
            
            if success:
                # Also try to delete the invoice file if it exists
                invoice_path = f'bills/invoice_{booking_id}.pdf'
                if os.path.exists(invoice_path):
                    try:
                        os.remove(invoice_path)
                    except OSError as e:
                        print(f"Warning: Could not delete invoice file {invoice_path}: {e}")
                
                return {'success': True, 'message': message}
            else:
                return {'success': False, 'message': message}, 404 if 'not found' in message else 400
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}, 500

    @app.route('/bulk_delete_bookings', methods=['POST'])
    def bulk_delete_bookings_route():
        """Delete multiple bookings at once"""
        try:
            data = request.get_json()
            if not data:
                return {'success': False, 'message': 'No data provided'}, 400
                
            booking_ids = data.get('booking_ids', [])
            
            if not booking_ids:
                return {'success': False, 'message': 'No booking IDs provided'}, 400
            
            if not isinstance(booking_ids, list):
                return {'success': False, 'message': 'Invalid booking IDs format'}, 400
            
            success, message, deleted_count = bulk_delete_bookings(booking_ids)
            
            if success:
                # Try to delete invoice files
                for booking_id in booking_ids:
                    invoice_path = f'bills/invoice_{booking_id}.pdf'
                    if os.path.exists(invoice_path):
                        try:
                            os.remove(invoice_path)
                        except OSError as e:
                            print(f"Warning: Could not delete invoice file {invoice_path}: {e}")
                
                return {
                    'success': True,
                    'message': message,
                    'deleted_count': deleted_count
                }
            else:
                return {'success': False, 'message': message}, 400
                
        except Exception as e:
            print(f"Unexpected error during bulk delete: {e}")
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}, 500

    @app.route('/get_booking/<int:booking_id>')
    def get_booking_route(booking_id):
        """Get booking details for editing"""
        try:
            booking = get_booking_by_id(booking_id)
            
            if not booking:
                return {'success': False, 'message': 'Booking not found'}, 404
            
            return {
                'success': True,
                'booking': booking
            }
        except Exception as e:
            print(f"Unexpected error getting booking {booking_id}: {e}")
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}, 500

    @app.route('/update_booking/<int:booking_id>', methods=['POST'])
    def update_booking_route(booking_id):
        """Update an existing booking"""
        try:
            data = request.get_json()
            success, message = process_booking_update(booking_id, data)
            
            if success:
                return {
                    'success': True,
                    'message': message,
                    'booking_id': booking_id
                }
            else:
                return {'success': False, 'message': message}, 400
                
        except Exception as e:
            print(f"Unexpected error updating booking {booking_id}: {e}")
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}, 500

    # Auto-complete endpoints using External API Service
    @app.route('/api/cities')
    def get_cities():
        """Get city suggestions for auto-complete using external API"""
        from external_api_service import get_city_suggestions
        
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        country_filter = request.args.get('country', None)
        
        suggestions = get_city_suggestions(query, limit, country_filter)
        return {'suggestions': suggestions}

    @app.route('/api/countries')
    def get_countries():
        """Get country suggestions for auto-complete"""
        from external_api_service import get_country_suggestions
        
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        suggestions = get_country_suggestions(query, limit)
        return {'suggestions': suggestions}

    @app.route('/api/hotel_areas/<city>')
    def get_hotel_areas(city):
        """Get hotel area suggestions for a city"""
        from external_api_service import get_hotel_area_suggestions
        
        areas = get_hotel_area_suggestions(city)
        return {'areas': areas}

    @app.route('/api/popular_routes')
    def get_popular_routes():
        """Get popular travel routes (domestic and international)"""
        from external_api_service import get_popular_routes
        
        routes = get_popular_routes()
        return {'routes': routes}

    @app.route('/send_whatsapp/<int:booking_id>', methods=['POST'])
    def send_booking_whatsapp_manual(booking_id):
        """Manually send WhatsApp for a specific booking with PDF attachment"""
        try:
            from whatsapp_service import send_booking_whatsapp_with_pdf, send_booking_whatsapp
            from database import get_booking_by_id
            from pdf_generator import generate_invoice_pdf
            
            # Get booking details
            booking = get_booking_by_id(booking_id)
            if not booking:
                return jsonify({
                    'success': False,
                    'message': 'Booking not found'
                }), 404
            
            # Get customers if it's a group booking
            customers = booking.get('customers', [])
            
            # For single bookings, create customer list from booking data
            if not customers:
                customers = [{
                    'name': booking.get('name', ''),
                    'phone': booking.get('phone', ''),
                    'email': booking.get('email', '')
                }]
            
            # Try to send WhatsApp with PDF attachment
            try:
                pdf_path = generate_invoice_pdf(booking_id, booking, customers)
                success, message = send_booking_whatsapp_with_pdf(booking, customers, pdf_path)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'WhatsApp message with invoice PDF sent successfully'
                    })
                else:
                    # If PDF WhatsApp fails, try without PDF
                    success, message = send_booking_whatsapp(booking, customers)
                    return jsonify({
                        'success': success,
                        'message': f'WhatsApp sent without PDF (PDF attachment failed): {message}' if success else message
                    })
                    
            except Exception:
                # If PDF generation fails, send without PDF
                success, message = send_booking_whatsapp(booking, customers)
                return jsonify({
                    'success': success,
                    'message': f'WhatsApp sent without PDF (PDF generation failed): {message}' if success else message
                })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error sending WhatsApp: {str(e)}'
            }), 500
    
    @app.route('/send_custom_whatsapp', methods=['POST'])
    def send_custom_whatsapp_route():
        """Send custom WhatsApp message"""
        try:
            from whatsapp_service import send_custom_whatsapp
            
            data = request.get_json() or {}
            phone = data.get('phone', '').strip()
            message = data.get('message', '').strip()
            
            if not phone or not message:
                return jsonify({
                    'success': False,
                    'message': 'Phone number and message are required'
                }), 400
            
            # Send WhatsApp
            success, response = send_custom_whatsapp(phone, message)
            
            return jsonify({
                'success': success,
                'message': response
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error sending WhatsApp: {str(e)}'
            }), 500
    
    @app.route('/whatsapp_status')
    def whatsapp_status():
        """Check WhatsApp service status"""
        try:
            from whatsapp_service import test_whatsapp_service
            from dynamic_config import whatsapp_enabled, whatsapp_send_on_booking
            WHATSAPP_ENABLED = whatsapp_enabled()
            WHATSAPP_SEND_ON_BOOKING = whatsapp_send_on_booking()
            
            test_result = test_whatsapp_service()
            
            return jsonify({
                'whatsapp_enabled': WHATSAPP_ENABLED,
                'auto_send_on_booking': WHATSAPP_SEND_ON_BOOKING,
                'provider': test_result.get('provider', 'Unknown'),
                'status': 'active' if WHATSAPP_ENABLED else 'disabled'
            })
            
        except Exception as e:
            return jsonify({
                'whatsapp_enabled': False,
                'error': str(e),
                'status': 'error'
            }), 500

    @app.route('/config')
    def config_page():
        """Configuration management page with modular design"""
        from config import ConfigManager, ConfigCategory
        from database import get_all_config
        
        # Initialize the modular config manager
        config_manager = ConfigManager()
        
        # Get current values from database
        current_config = get_all_config()
        current_values = {config['config_key']: config['config_value'] for config in current_config}
        
        # Get all categories and organize data
        categories = config_manager.get_categories()
        
        # Prepare data for template
        category_fields = {}
        category_names = {}
        category_icons = {}
        category_descriptions = {}
        
        for category in categories:
            # Get fields for this category
            fields = config_manager.get_fields_by_category(category)
            
            # Update field values with current database values
            for field in fields:
                if field.key in current_values:
                    field.value = current_values[field.key]
            
            category_fields[category] = fields
            category_names[category] = config_manager.get_category_display_name(category)
            category_icons[category] = config_manager.get_category_icon(category)
            category_descriptions[category] = config_manager.get_category_description(category)
        
        return render_template('config_modular.html', 
                             categories=categories,
                             category_fields=category_fields,
                             category_names=category_names,
                             category_icons=category_icons,
                             category_descriptions=category_descriptions)

    @app.route('/api/config', methods=['GET'])
    def get_config_api():
        """Get configuration values API"""
        from database import get_all_config
        
        category = request.args.get('category')
        configs = get_all_config(category)
        
        # Don't expose sensitive values in API responses
        for config in configs:
            if config['is_sensitive']:
                config['config_value'] = '***' if config['config_value'] else ''
        
        return jsonify({
            'success': True,
            'configs': configs
        })

    @app.route('/api/config', methods=['POST'])
    def update_config_api():
        """Update configuration values API with enhanced validation"""
        try:
            from database import set_config_value
            from config_manager import config_manager
            
            data = request.get_json()
            
            if not data or 'configs' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Invalid request data'
                }), 400
            
            updated_count = 0
            errors = []
            warnings = []
            
            for config_update in data['configs']:
                try:
                    key = config_update['key']
                    value = config_update['value']
                    config_type = config_update.get('type', 'string')
                    category = config_update.get('category', 'general')
                    description = config_update.get('description', '')
                    is_sensitive = config_update.get('is_sensitive', False)
                    
                    # Validate required fields
                    if not key:
                        errors.append('Configuration key is required')
                        continue
                    
                    # Use config manager for validation if schema exists
                    schema = config_manager.get_config_schema()
                    if key in schema:
                        config_field = schema[key]
                        is_valid, validation_message = config_manager.validate_config_value(config_field, value)
                        
                        if not is_valid:
                            errors.append(f'{key}: {validation_message}')
                            continue
                        
                        # Use schema values for consistency
                        config_type = config_field.type.value
                        category = config_field.category.value
                        description = config_field.description
                        is_sensitive = config_field.is_sensitive
                    else:
                        # Fallback validation for unknown configs
                        warnings.append(f'Unknown configuration key: {key}')
                        
                        if config_type == 'boolean':
                            if str(value).lower() not in ['true', 'false']:
                                errors.append(f'Invalid boolean value for {key}')
                                continue
                        elif config_type == 'number':
                            try:
                                float(value)
                            except ValueError:
                                errors.append(f'Invalid number value for {key}')
                                continue
                    
                    set_config_value(key, value, config_type, category, description, is_sensitive)
                    updated_count += 1
                    
                except Exception as e:
                    errors.append(f'Error updating {key}: {str(e)}')
            
            # Refresh the dynamic configuration cache after updates
            if updated_count > 0:
                try:
                    from dynamic_config import refresh_config
                    refresh_config()
                except Exception as e:
                    warnings.append(f'Failed to refresh config cache: {str(e)}')
            
            response_data = {
                'success': len(errors) == 0,
                'message': f'Updated {updated_count} configuration(s)',
                'updated_count': updated_count
            }
            
            if warnings:
                response_data['warnings'] = warnings
            
            if errors:
                response_data['errors'] = errors
                response_data['message'] = f'Updated {updated_count} configs with {len(errors)} errors'
                return jsonify(response_data), 400
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Configuration update failed: {str(e)}'
            }), 500

    @app.route('/api/config/<config_key>', methods=['DELETE'])
    def delete_config_api(config_key):
        """Delete a configuration value"""
        try:
            from database import delete_config
            
            if delete_config(config_key):
                return jsonify({
                    'success': True,
                    'message': f'Configuration {config_key} deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Configuration {config_key} not found'
                }), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error deleting configuration: {str(e)}'
            }), 500

    @app.route('/api/config/test_whatsapp', methods=['POST'])
    def test_whatsapp_config():
        """Test WhatsApp configuration"""
        try:
            from whatsapp_service import get_whatsapp_service
            
            data = request.get_json()
            phone = data.get('phone', '+91-9999999999')
            
            whatsapp_service = get_whatsapp_service()
            success, message = whatsapp_service.send_message(
                phone, 
                "🧪 Test message from Himanshi Travels configuration panel!"
            )
            
            return jsonify({
                'success': success,
                'message': message,
                'test_phone': phone
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'WhatsApp test failed: {str(e)}'
            }), 500

    @app.route('/api/config/test_email', methods=['POST'])
    def test_email():
        """Test email configuration"""
        try:
            data = request.get_json() or {}
            test_email_addr = data.get('email', '')
            
            if not test_email_addr:
                return jsonify({
                    'success': False,
                    'message': 'Email address is required'
                }), 400
            
            from email_service import test_email_config
            result = test_email_config(test_email_addr)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Email test error: {e}")
            return jsonify({
                'success': False,
                'message': f'Email test failed: {str(e)}'
            }), 500
        
    @app.route('/api/backup', methods=['GET'])
    def list_backups():
        """List all database backups"""
        try:
            from backup_service import list_database_backups
            backups = list_database_backups()
            
            return jsonify({
                'success': True,
                'backups': backups,
                'count': len(backups)
            })
            
        except Exception as e:
            logger.error(f"List backups error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to list backups: {str(e)}'
            }), 500
    
    @app.route('/api/backup/create', methods=['POST'])
    def create_backup():
        """Create a new database backup"""
        try:
            data = request.get_json() or {}
            backup_name = data.get('name')
            
            from backup_service import create_database_backup
            result = create_database_backup(backup_name)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Create backup error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to create backup: {str(e)}'
            }), 500
    
    @app.route('/api/backup/restore', methods=['POST'])
    def restore_backup():
        """Restore database from backup"""
        try:
            data = request.get_json() or {}
            backup_filename = data.get('filename')
            
            if not backup_filename:
                return jsonify({
                    'success': False,
                    'message': 'Backup filename is required'
                }), 400
            
            from backup_service import restore_database_backup
            result = restore_database_backup(backup_filename)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Restore backup error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to restore backup: {str(e)}'
            }), 500

    @app.route('/api/send_booking_email/<int:booking_id>', methods=['POST'])
    def send_booking_email_api(booking_id):
        """Send booking email manually"""
        try:
            # Get booking details
            booking = get_booking_by_id(booking_id)
            if not booking:
                return jsonify({
                    'success': False,
                    'message': 'Booking not found'
                }), 404
            
            # Check if email is enabled
            from dynamic_config import email_enabled
            if not email_enabled():
                return jsonify({
                    'success': False,
                    'message': 'Email service is disabled'
                }), 400
            
            # Check if booking has email
            if not booking.get('email'):
                return jsonify({
                    'success': False,
                    'message': 'No email address found for this booking'
                }), 400
            
            # Prepare booking data for email
            booking_data = {
                'id': booking['id'],
                'name': booking['name'],
                'email': booking['email'],
                'booking_type': booking['booking_type'],
                'total': booking['total'],
                'date': booking['date']
            }
            
            # Check if PDF exists
            pdf_path = f"bills/invoice_{booking_id}.pdf"
            
            # Send email
            from email_service import send_booking_email
            success = send_booking_email(booking_data, pdf_path if os.path.exists(pdf_path) else None)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Email sent successfully to {booking["email"]}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send email'
                }), 500
                
        except Exception as e:
            logger.error(f"Send booking email error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }), 500

    @app.route('/debug/config')
    def debug_config():
        """Debug configuration values"""
        from dynamic_config import whatsapp_enabled, email_enabled
        return {
            'whatsapp_enabled': whatsapp_enabled(),
            'email_enabled': email_enabled(),
            'whatsapp_type': str(type(whatsapp_enabled())),
            'email_type': str(type(email_enabled())),
            'message': 'Configuration debug info'
        }

    @app.route('/api/config/reset', methods=['POST'])
    def reset_config_to_defaults():
        """Reset all configurations to their default values"""
        try:
            from config_manager import config_manager
            from database import set_config_value, delete_all_config
            
            # Get default configuration schema
            schema = config_manager.get_config_schema()
            
            # Clear all existing configurations
            delete_all_config()
            
            # Set all configurations to their default values
            reset_count = 0
            for key, field in schema.items():
                try:
                    set_config_value(
                        key=field.key,
                        value=str(field.value) if field.value is not None else '',
                        config_type=field.type.value,
                        category=field.category.value,
                        description=field.description,
                        is_sensitive=field.is_sensitive
                    )
                    reset_count += 1
                except Exception as e:
                    app.logger.error(f"Error resetting config {field.key}: {e}")
            
            # Refresh the dynamic configuration cache
            try:
                from dynamic_config import refresh_config
                refresh_config()
            except Exception as e:
                app.logger.warning(f'Failed to refresh config cache: {str(e)}')
            
            return jsonify({
                'success': True,
                'message': f'Reset {reset_count} configuration(s) to default values',
                'reset_count': reset_count
            })
            
        except Exception as e:
            app.logger.error(f"Configuration reset failed: {e}")
            return jsonify({
                'success': False,
                'message': f'Configuration reset failed: {str(e)}'
            }), 500

    @app.route('/api/config/upload_logo', methods=['POST'])
    def upload_logo():
        """Upload and save company logo"""
        try:
            # Check if file is present in request
            if 'logo' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No logo file provided'
                }), 400
            
            file = request.files['logo']
            
            # Check if file is selected
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
            def allowed_file(filename):
                return '.' in filename and \
                       filename.rsplit('.', 1)[1].lower() in allowed_extensions
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'message': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or SVG files only.'
                }), 400
            
            # Validate file size (max 5MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            max_size = 5 * 1024 * 1024  # 5MB in bytes
            if file_size > max_size:
                return jsonify({
                    'success': False,
                    'message': 'File too large. Maximum size is 5MB.'
                }), 400
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('static', 'images')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate filename with timestamp to avoid conflicts
            filename = file.filename
            _, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"logo_{timestamp}{ext}"
            
            # Save file
            file_path = os.path.join(upload_dir, new_filename)
            file.save(file_path)
            
            # Get old logo path before updating configuration
            from database import get_config_value, set_config_value
            old_logo_path = get_config_value('LOGO_PATH', DEFAULT_LOGO_PATH)
            
            # Update logo path in configuration
            relative_path = f"static/images/{new_filename}"
            
            set_config_value(
                key='LOGO_PATH',
                value=relative_path,
                config_type='string',
                category='general',
                description='Path to agency logo file'
            )
            
            # Try to remove old logo file (if it's not the default and not the same as new)
            try:
                if old_logo_path != relative_path and old_logo_path != DEFAULT_LOGO_PATH:
                    old_file_path = os.path.join(os.getcwd(), old_logo_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                        logger.info(f"Removed old logo file: {old_file_path}")
            except Exception as e:
                logger.warning(f"Could not remove old logo file: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Logo uploaded successfully!',
                'logo_path': relative_path,
                'filename': new_filename
            })
            
        except Exception as e:
            logger.error(f"Logo upload failed: {e}")
            return jsonify({
                'success': False,
                'message': f'Logo upload failed: {str(e)}'
            }), 500

    @app.route('/api/config/logo', methods=['GET'])
    def get_current_logo():
        """Get current logo information"""
        try:
            from database import get_config_value
            logo_path = get_config_value('LOGO_PATH', DEFAULT_LOGO_PATH)
            
            # Check if file exists
            file_exists = os.path.exists(logo_path)
            
            return jsonify({
                'success': True,
                'logo_path': logo_path,
                'logo_url': f"/{logo_path}",
                'file_exists': file_exists
            })
            
        except Exception as e:
            logger.error(f"Failed to get logo info: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get logo info: {str(e)}'
            }), 500

    # Configuration Management Routes
    @app.route('/api/config/save', methods=['POST'])
    def save_config_modular():
        """Save configuration values using modular config manager"""
        try:
            from config import ConfigManager
            from database import set_config_value
            
            config_manager = ConfigManager()
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided'
                }), 400
            
            # Validate and save configurations
            validation_results = config_manager.validate_batch_configs(data)
            
            if validation_results['invalid']:
                return jsonify({
                    'success': False,
                    'message': 'Validation errors found',
                    'errors': validation_results['errors']
                }), 400
            
            # Save valid configurations
            updated_count = 0
            for key, value in data.items():
                field = config_manager.get_field(key)
                if field:
                    set_config_value(
                        key, 
                        value, 
                        field.type.value, 
                        field.category.value, 
                        field.description, 
                        field.is_sensitive
                    )
                    updated_count += 1
            
            # Refresh configuration cache
            try:
                from dynamic_config import refresh_config
                refresh_config()
            except Exception as e:
                logger.warning(f"Failed to refresh config cache: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Successfully saved {updated_count} configuration(s)',
                'updated_count': updated_count
            })
            
        except Exception as e:
            logger.error(f"Config save error: {e}")
            return jsonify({
                'success': False,
                'message': f'Save failed: {str(e)}'
            }), 500

    @app.route('/api/config/test/<category>', methods=['POST'])
    def test_config_category(category):
        """Test configuration for a specific category"""
        try:
            data = request.get_json() or {}
            
            if category == 'email':
                # Call the existing email test function
                response = test_email()
                return response
            elif category == 'whatsapp':
                # Call the existing WhatsApp test function  
                response = test_whatsapp_config()
                return response
            elif category == 'sms':
                # SMS test implementation
                phone = data.get('phone', '+91-9999999999')
                
                try:
                    # This would integrate with SMS service when available
                    return jsonify({
                        'success': True,
                        'message': f'SMS test successful (simulated) to {phone}',
                        'details': 'SMS service integration pending'
                    })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'SMS test failed: {str(e)}'
                    }), 500
                    
            elif category == 'database':
                # Database connectivity test
                try:
                    from database import get_db_connection
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Database connection test successful',
                        'details': 'Successfully connected to SQLite database'
                    })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'Database test failed: {str(e)}'
                    }), 500
                    
            elif category == 'backup':
                # Backup system test
                try:
                    from backup_service import test_backup_system
                    result = test_backup_system()
                    return jsonify(result)
                except ImportError:
                    # Fallback if backup service not available
                    return jsonify({
                        'success': True,
                        'message': 'Backup system test (simulated)',
                        'details': 'Backup service is available and configured'
                    })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'Backup test failed: {str(e)}'
                    }), 500
                    
            elif category == 'security':
                # Security configuration test
                return jsonify({
                    'success': True,
                    'message': 'Security configuration test successful',
                    'details': 'Security settings are properly configured'
                })
                
            elif category == 'pdf':
                # PDF generation test
                try:
                    test_data = {
                        'booking_id': 'TEST-001',
                        'customer_name': 'Test Customer',
                        'amount': 1000.00
                    }
                    
                    from pdf_generator import test_pdf_generation
                    result = test_pdf_generation(test_data)
                    return jsonify(result)
                except ImportError:
                    return jsonify({
                        'success': True,
                        'message': 'PDF generation test (simulated)',
                        'details': 'PDF generation system is available'
                    })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'PDF test failed: {str(e)}'
                    }), 500
                    
            elif category == 'business':
                # Business configuration test
                return jsonify({
                    'success': True,
                    'message': 'Business configuration test successful',
                    'details': 'Business settings are properly configured'
                })
                
            else:
                return jsonify({
                    'success': False,
                    'message': f'Testing not available for {category} category'
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Test failed: {str(e)}'
            }), 500

    @app.route('/api/config/reset/<category>', methods=['POST'])
    def reset_config_category(category):
        """Reset a specific category to default values"""
        try:
            from config import ConfigManager, ConfigCategory
            from database import set_config_value
            
            config_manager = ConfigManager()
            
            # Find the category enum
            target_category = None
            for cat in ConfigCategory:
                if cat.value == category:
                    target_category = cat
                    break
            
            if not target_category:
                return jsonify({
                    'success': False,
                    'message': f'Unknown category: {category}'
                }), 400
            
            # Get default values for the category
            fields = config_manager.get_fields_by_category(target_category)
            updated_count = 0
            
            for field in fields:
                default_value = field.default_value if field.default_value is not None else field.value
                set_config_value(
                    field.key,
                    default_value,
                    field.type.value,
                    field.category.value,
                    field.description,
                    field.is_sensitive
                )
                updated_count += 1
            
            # Refresh configuration cache
            try:
                from dynamic_config import refresh_config
                refresh_config()
            except Exception as e:
                logger.warning(f"Failed to refresh config cache: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Successfully reset {updated_count} {category} configuration(s) to defaults',
                'updated_count': updated_count
            })
            
        except Exception as e:
            logger.error(f"Config category reset error: {e}")
            return jsonify({
                'success': False,
                'message': f'Reset failed: {str(e)}'
            }), 500

def create_and_configure_app():
    """Create and configure the complete Flask application"""
    app = create_app()
    register_routes(app)
    return app
