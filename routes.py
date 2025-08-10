"""
Flask routes for Himanshi Travels application
"""

import os
import csv
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file, make_response, jsonify

from config import DEFAULT_PAGE_SIZE, GST_PERCENT
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
        return render_template('bookings.html', gst_percent=GST_PERCENT)

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

    @app.route('/test_autocomplete')
    def test_autocomplete():
        """Test page for autocomplete functionality"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Autocomplete Test</title>
            <link rel="stylesheet" href="/static/css/autocomplete.css">
            <style>
                body { padding: 20px; font-family: Arial, sans-serif; }
                .form-group { margin: 20px 0; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input { padding: 10px; width: 300px; border: 1px solid #ccc; border-radius: 5px; }
                .autocomplete-container { position: relative; display: inline-block; }
                .test-result { margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Autocomplete Test Page</h1>
            
            <div class="form-group">
                <div class="autocomplete-container">
                    <label for="test_city">Test City Input:</label>
                    <input type="text" id="test_city" placeholder="Type a city name (e.g., 'new')" autocomplete="off">
                    <div id="test_city_suggestions" class="autocomplete-suggestions"></div>
                </div>
            </div>
            
            <div class="form-group">
                <div class="autocomplete-container">
                    <label for="test_country">Test Country Input:</label>
                    <input type="text" id="test_country" placeholder="Type a country name (e.g., 'uni')" autocomplete="off">
                    <div id="test_country_suggestions" class="autocomplete-suggestions"></div>
                </div>
            </div>
            
            <button onclick="testAutoComplete()">Run Test</button>
            <div id="test-results" class="test-result">
                Test results will appear here...
            </div>
            
            <script src="/static/js/autocomplete.js"></script>
            <script>
                // Initialize test autocomplete
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('Test page loaded');
                    
                    // Initialize autocomplete for test fields
                    new AutoComplete('test_city', 'test_city_suggestions', '/api/cities');
                    new AutoComplete('test_country', 'test_country_suggestions', '/api/countries');
                    
                    console.log('Test autocomplete initialized');
                });
                
                // Enhanced test function
                function testAutoComplete() {
                    const results = document.getElementById('test-results');
                    results.innerHTML = '<h3>Running tests...</h3>';
                    
                    // Test API endpoints
                    fetch('/api/cities?q=new&limit=3')
                        .then(response => response.json())
                        .then(data => {
                            results.innerHTML += '<p>✅ Cities API working: ' + data.suggestions.length + ' results</p>';
                        })
                        .catch(error => {
                            results.innerHTML += '<p>❌ Cities API failed: ' + error.message + '</p>';
                        });
                    
                    fetch('/api/countries?q=uni&limit=3')
                        .then(response => response.json())
                        .then(data => {
                            results.innerHTML += '<p>✅ Countries API working: ' + data.suggestions.length + ' results</p>';
                        })
                        .catch(error => {
                            results.innerHTML += '<p>❌ Countries API failed: ' + error.message + '</p>';
                        });
                }
            </script>
        </body>
        </html>
        """

    @app.route('/test_calculations')
    def test_calculations():
        """Test page for verifying calculation logic"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Calculation Test</title>
            <style>
                body { padding: 20px; font-family: Arial, sans-serif; }
                .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
                .result { margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 3px; }
                input, button { margin: 5px; padding: 8px; }
            </style>
        </head>
        <body>
            <h1>Calculation Test</h1>
            
            <div class="test-section">
                <h3>Single Booking</h3>
                <input type="number" id="single_base" placeholder="Base Amount" value="1000">
                <input type="checkbox" id="single_gst" checked> Apply GST (18%)
                <button onclick="testSingleCalculation()">Calculate</button>
                <div class="result" id="single_result">Result will appear here</div>
            </div>
            
            <div class="test-section">
                <h3>Group Booking</h3>
                <input type="number" id="customer1_amount" placeholder="Customer 1 Amount" value="1500">
                <input type="number" id="customer2_amount" placeholder="Customer 2 Amount" value="2000">
                <input type="checkbox" id="group_gst" checked> Apply GST (18%)
                <button onclick="testGroupCalculation()">Calculate</button>
                <div class="result" id="group_result">Result will appear here</div>
            </div>
            
            <script>
                function testSingleCalculation() {
                    const base = parseFloat(document.getElementById('single_base').value) || 0;
                    const applyGst = document.getElementById('single_gst').checked;
                    
                    let gst = 0;
                    let total = base;
                    
                    if (applyGst) {
                        gst = base * 0.18;
                        total = base + gst;
                    }
                    
                    document.getElementById('single_result').innerHTML = `
                        Base: ₹${base.toFixed(2)}<br>
                        GST (18%): ₹${gst.toFixed(2)}<br>
                        <strong>Total: ₹${total.toFixed(2)}</strong>
                    `;
                }
                
                function testGroupCalculation() {
                    const amount1 = parseFloat(document.getElementById('customer1_amount').value) || 0;
                    const amount2 = parseFloat(document.getElementById('customer2_amount').value) || 0;
                    const applyGst = document.getElementById('group_gst').checked;
                    
                    const baseTotal = amount1 + amount2;
                    let gst = 0;
                    let finalTotal = baseTotal;
                    
                    if (applyGst) {
                        gst = baseTotal * 0.18;
                        finalTotal = baseTotal + gst;
                    }
                    
                    document.getElementById('group_result').innerHTML = `
                        Customer 1: ₹${amount1.toFixed(2)}<br>
                        Customer 2: ₹${amount2.toFixed(2)}<br>
                        Base Total: ₹${baseTotal.toFixed(2)}<br>
                        GST (18%): ₹${gst.toFixed(2)}<br>
                        <strong>Final Total: ₹${finalTotal.toFixed(2)}</strong>
                    `;
                }
                
                // Auto-calculate on page load
                testSingleCalculation();
                testGroupCalculation();
            </script>
        </body>
        </html>
        """


def create_and_configure_app():
    """Create and configure the complete Flask application"""
    app = create_app()
    register_routes(app)
    return app
