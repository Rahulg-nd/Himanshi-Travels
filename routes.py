"""
Flask routes for Himanshi Travels application
"""

import os
import csv
import io
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, make_response, jsonify

logger = logging.getLogger(__name__)

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
        """Configuration management page"""
        from database import get_all_config, get_config_categories
        
        categories = get_config_categories()
        all_config = get_all_config()
        
        # Group configs by category
        configs_by_category = {}
        for config in all_config:
            category = config['category']
            if category not in configs_by_category:
                configs_by_category[category] = []
            configs_by_category[category].append(config)
        
        return render_template('config.html', 
                             categories=categories, 
                             configs_by_category=configs_by_category)

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
        """Update configuration values API"""
        try:
            from database import set_config_value
            
            data = request.get_json()
            
            if not data or 'configs' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Invalid request data'
                }), 400
            
            updated_count = 0
            errors = []
            
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
                    
                    # Type validation
                    if config_type == 'boolean':
                        if value.lower() not in ['true', 'false']:
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
                    errors.append(f'Warning: Failed to refresh config cache: {str(e)}')
            
            if errors:
                return jsonify({
                    'success': False,
                    'message': f'Updated {updated_count} configs with {len(errors)} errors',
                    'errors': errors
                }), 400
            
            return jsonify({
                'success': True,
                'message': f'Successfully updated {updated_count} configuration(s)',
                'updated_count': updated_count
            })
            
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

    # Configuration Management Routes
def create_and_configure_app():
    """Create and configure the complete Flask application"""
    app = create_app()
    register_routes(app)
    return app
