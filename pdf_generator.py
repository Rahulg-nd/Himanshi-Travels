"""
PDF generation utilities for Himanshi Travels invoices
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from config import (AGENCY_NAME, AGENCY_TAGLINE, AGENCY_ADDRESS, 
                   AGENCY_PHONE, AGENCY_EMAIL, LOGO_PATH, BILLS_DIRECTORY, GST_PERCENT)
from booking_logic import get_vehicle_label


def setup_pdf_styles():
    """Setup custom PDF styles"""
    styles = getSampleStyleSheet()
    
    # Define custom colors
    primary_color = HexColor('#667eea')
    secondary_color = HexColor('#764ba2')
    
    # Custom styles - optimized for single page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,  # Further reduced for single page
        textColor=primary_color,
        spaceAfter=8,  # Further reduced spacing
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=11,  # Further reduced
        textColor=secondary_color,
        spaceAfter=6,  # Further reduced spacing
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=8,  # Further reduced for more content
        spaceAfter=2,  # Minimal spacing
        fontName='Helvetica'
    )
    
    return {
        'title': title_style,
        'header': header_style,
        'normal': normal_style,
        'primary_color': primary_color,
        'secondary_color': secondary_color
    }


def create_header_section(story: List, styles: Dict):
    """Create header section with logo and company info"""
    if os.path.exists(LOGO_PATH):
        # Create header table with logo and company info
        logo = RLImage(LOGO_PATH, width=1.5*inch, height=0.4*inch)  # Even smaller logo
        company_info = Paragraph(f'''
            <b>{AGENCY_NAME}</b><br/>
            <font size="7">{AGENCY_TAGLINE}</font><br/>
            <font size="6">{AGENCY_ADDRESS}</font><br/>
            <font size="6">📞 {AGENCY_PHONE} | 📧 {AGENCY_EMAIL}</font>
        ''', styles['normal'])
        
        header_table = Table([[logo, company_info]], colWidths=[2*inch, 4.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(header_table)
    else:
        # Fallback header without logo
        story.append(Paragraph(f"<b>{AGENCY_NAME}</b>", styles['title']))
        story.append(Paragraph(f"{AGENCY_TAGLINE}", styles['normal']))
    
    story.append(Spacer(1, 6))  # Further reduced spacing
    
    # Add a colored line separator
    line_table = Table([['']], colWidths=[6.5*inch], rowHeights=[0.02*inch])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), styles['primary_color']),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 6))  # Further reduced spacing


def create_invoice_details_section(story: List, booking: Dict[str, Any], customers: List, styles: Dict):
    """Create invoice details section"""
    # Invoice title
    booking_type_title = "GROUP BOOKING" if booking['is_group_booking'] else "TRAVEL BOOKING"
    story.append(Paragraph(f"{booking_type_title} INVOICE", styles['title']))
    
    # Invoice details table - more compact
    invoice_date = datetime.strptime(booking['date'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y")
    invoice_details = [
        ['Invoice #:', f'{str(booking["id"]).zfill(6)}'],
        ['Date:', invoice_date],
        ['Type:', booking['booking_type']]
    ]
    
    if booking['is_group_booking']:
        invoice_details.append(['Customers:', str(len(customers))])
    
    details_table = Table(invoice_details, colWidths=[1.5*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Further reduced font size
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Further reduced padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 3),  # Further reduced padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 6))  # Further reduced spacing


def create_service_details_section(story: List, booking: Dict[str, Any], styles: Dict):
    """Create service details section"""
    story.append(Paragraph("SERVICE DETAILS", styles['header']))
    service_data = [['Service:', booking['booking_type']]]
    
    # Add booking-specific details
    if booking['booking_type'] == 'Hotel' and (booking['hotel_name'] or booking['hotel_city']):
        if booking['hotel_name']:
            service_data.append(['Hotel:', booking['hotel_name']])
        if booking['hotel_city']:
            service_data.append(['City:', booking['hotel_city']])
    elif booking['booking_type'] in ['Flight', 'Train', 'Bus', 'Transport']:
        if booking['operator_name']:
            service_data.append(['Operator:', booking['operator_name']])
        if booking['from_journey']:
            service_data.append(['From:', booking['from_journey']])
        if booking['to_journey']:
            service_data.append(['To:', booking['to_journey']])
    
    # Add service details
    if booking['vehicle_number']:
        vehicle_label = get_vehicle_label(booking['booking_type'])
        service_data.append([vehicle_label, booking['vehicle_number']])
    if booking['service_date']:
        service_data.append(['Date:', booking['service_date']])
    if booking['service_time']:
        service_data.append(['Time:', booking['service_time']])
    
    service_table = Table(service_data, colWidths=[1.5*inch, 3*inch])
    service_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Further reduced font size
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Further reduced padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 3),  # Further reduced padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(service_table)
    story.append(Spacer(1, 6))  # Further reduced spacing


def create_customer_details_section(story: List, booking: Dict[str, Any], customers: List, styles: Dict):
    """Create customer details section"""
    if booking['is_group_booking'] and customers:
        story.append(Paragraph("CUSTOMER DETAILS", styles['header']))
        
        # Create customer table with compact layout
        customer_headers = ['#', 'Name', 'Contact', 'Seat/Room', 'Amount']
        customer_data = [customer_headers]
        
        for i, customer in enumerate(customers):
            customer_data.append([
                str(i + 1),
                customer['customer_name'],
                f"{customer['customer_phone'] or ''}",  # Only phone for space
                customer['seat_room_number'] or '-',
                f"₹{customer['customer_amount']:.0f}"  # No decimals for space
            ])
        
        customer_table = Table(customer_data, colWidths=[0.3*inch, 1.6*inch, 1.0*inch, 0.7*inch, 0.7*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Further reduced font size for customer table
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), styles['secondary_color']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Further reduced padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Further reduced padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 6))  # Further reduced spacing
    else:
        # Single customer details - more compact
        story.append(Paragraph("CUSTOMER DETAILS", styles['header']))
        customer_data = [
            ['Name:', booking['name']],
            ['Phone:', booking['phone']]
        ]
        
        # Add email only if provided
        if booking.get('email'):
            customer_data.insert(1, ['Email:', booking['email']])
        
        customer_table = Table(customer_data, colWidths=[1.5*inch, 3*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Further reduced font size
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Further reduced padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),  # Further reduced padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 6))  # Further reduced spacing


def create_billing_summary_section(story: List, booking: Dict[str, Any], styles: Dict):
    """Create billing summary section - shows GST breakdown but hides GST number"""
    story.append(Paragraph("BILLING SUMMARY", styles['header']))
    
    # Extract base amount and GST from booking data
    base_amount = booking.get('base', booking.get('base_amount', 0))
    gst_amount = booking.get('gst', 0)
    total_amount = booking.get('total', 0)
    
    # Billing breakdown with GST calculation shown
    billing_data = [
        ['Base Amount:', f'₹ {base_amount:.2f}'],
        [f'GST ({GST_PERCENT}%):', f'₹ {gst_amount:.2f}'],
        ['', ''],  # Empty row for spacing
        ['TOTAL AMOUNT:', f'₹ {total_amount:.2f}']
    ]
    
    billing_table = Table(billing_data, colWidths=[3*inch, 2*inch])
    billing_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),  # Bold total row
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTSIZE', (0, 3), (-1, 3), 11),  # Slightly larger for total
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, 2), HexColor('#333333')),  # Normal text color for breakdown
        ('TEXTCOLOR', (0, 3), (-1, 3), styles['primary_color']),  # Highlight total
        ('BACKGROUND', (0, 3), (-1, 3), HexColor('#f0f0f0')),  # Background for total row
        ('GRID', (0, 0), (-1, 1), 0.5, HexColor('#e1e5e9')),  # Light grid for breakdown
        ('GRID', (0, 3), (-1, 3), 1, styles['primary_color']),  # Bold grid for total
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 2), (-1, 2), 2),  # Reduce spacing row padding
        ('BOTTOMPADDING', (0, 2), (-1, 2), 2),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 10))


def create_footer_section(story: List, styles: Dict):
    """Create footer section"""
    footer_text = f'''
        <para align="center">
        <font size="7" color="#666666">
        Thank you for choosing {AGENCY_NAME}! | For queries: {AGENCY_PHONE} | {AGENCY_EMAIL}<br/>
        <i>Safe travels!</i>
        </font>
        </para>
    '''
    story.append(Paragraph(footer_text, styles['normal']))


def generate_invoice_pdf(booking_id: int, booking: Dict[str, Any], customers: List = None) -> str:
    """Generate PDF invoice for a booking"""
    file_path = f'{BILLS_DIRECTORY}/invoice_{booking_id}.pdf'
    os.makedirs(BILLS_DIRECTORY, exist_ok=True)
    
    # Create PDF document with reduced margins for single page
    doc = SimpleDocTemplate(
        file_path, 
        pagesize=letter, 
        topMargin=0.25*inch,   # Further reduced margins
        bottomMargin=0.25*inch, 
        leftMargin=0.4*inch,   # Further reduced margins
        rightMargin=0.4*inch
    )
    story = []
    
    # Setup styles
    styles = setup_pdf_styles()
    
    # Create sections
    create_header_section(story, styles)
    create_invoice_details_section(story, booking, customers or [], styles)
    create_service_details_section(story, booking, styles)
    create_customer_details_section(story, booking, customers or [], styles)
    create_billing_summary_section(story, booking, styles)
    create_footer_section(story, styles)
    
    # Build PDF
    doc.build(story)
    return file_path
