"""
PDF generation utilities for Himanshi Travels invoices
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from config import (AGENCY_NAME, AGENCY_TAGLINE, GSTIN, AGENCY_ADDRESS, 
                   AGENCY_PHONE, AGENCY_EMAIL, LOGO_PATH, BILLS_DIRECTORY)
from booking_logic import get_vehicle_label


def setup_pdf_styles():
    """Setup custom PDF styles"""
    styles = getSampleStyleSheet()
    
    # Define custom colors
    primary_color = HexColor('#667eea')
    secondary_color = HexColor('#764ba2')
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=primary_color,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=secondary_color,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
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
        logo = RLImage(LOGO_PATH, width=2*inch, height=0.6*inch)
        company_info = Paragraph(f'''
            <b>{AGENCY_NAME}</b><br/>
            <font size="10">{AGENCY_TAGLINE}</font><br/>
            <font size="9">{AGENCY_ADDRESS}</font><br/>
            <font size="9">📞 {AGENCY_PHONE} | 📧 {AGENCY_EMAIL}</font><br/>
            <font size="9">GSTIN: {GSTIN}</font>
        ''', styles['normal'])
        
        header_table = Table([[logo, company_info]], colWidths=[2.5*inch, 4*inch])
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
    
    story.append(Spacer(1, 20))
    
    # Add a colored line separator
    line_table = Table([['']], colWidths=[6.5*inch], rowHeights=[0.02*inch])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), styles['primary_color']),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 20))


def create_invoice_details_section(story: List, booking: Dict[str, Any], customers: List, styles: Dict):
    """Create invoice details section"""
    # Invoice title
    booking_type_title = "GROUP BOOKING" if booking['is_group_booking'] else "TRAVEL BOOKING"
    story.append(Paragraph(f"{booking_type_title} INVOICE", styles['title']))
    
    # Invoice details table
    invoice_date = datetime.strptime(booking['date'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y")
    invoice_details = [
        ['Invoice Number:', f'#{str(booking["id"]).zfill(6)}'],
        ['Invoice Date:', invoice_date],
        ['Booking Type:', booking['booking_type']]
    ]
    
    if booking['is_group_booking']:
        invoice_details.append(['Total Customers:', str(len(customers))])
    
    details_table = Table(invoice_details, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))


def create_service_details_section(story: List, booking: Dict[str, Any], styles: Dict):
    """Create service details section"""
    story.append(Paragraph("SERVICE DETAILS", styles['header']))
    service_data = [['Service Type:', booking['booking_type']]]
    
    # Add booking-specific details
    if booking['booking_type'] == 'Hotel' and (booking['hotel_name'] or booking['hotel_city']):
        if booking['hotel_name']:
            service_data.append(['Hotel Name:', booking['hotel_name']])
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
        service_data.append(['Service Date:', booking['service_date']])
    if booking['service_time']:
        service_data.append(['Service Time:', booking['service_time']])
    
    service_table = Table(service_data, colWidths=[2*inch, 4*inch])
    service_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(service_table)
    story.append(Spacer(1, 20))


def create_customer_details_section(story: List, booking: Dict[str, Any], customers: List, styles: Dict):
    """Create customer details section"""
    if booking['is_group_booking'] and customers:
        story.append(Paragraph("CUSTOMER DETAILS", styles['header']))
        
        # Create customer table
        customer_headers = ['S.No.', 'Customer Name', 'Contact', 'Seat/Room', 'Amount (₹)']
        customer_data = [customer_headers]
        
        for i, customer in enumerate(customers):
            customer_data.append([
                str(i + 1),
                customer['customer_name'],
                f"{customer['customer_email'] or ''}\n{customer['customer_phone'] or ''}".strip(),
                customer['seat_room_number'] or '-',
                f"{customer['customer_amount']:.2f}"
            ])
        
        customer_table = Table(customer_data, colWidths=[0.5*inch, 2*inch, 1.8*inch, 1*inch, 1*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), styles['secondary_color']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 20))
    else:
        # Single customer details
        story.append(Paragraph("CUSTOMER DETAILS", styles['header']))
        customer_data = [
            ['Customer Name:', booking['name']],
            ['Email Address:', booking['email']],
            ['Phone Number:', booking['phone']]
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e1e5e9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 20))


def create_billing_summary_section(story: List, booking: Dict[str, Any], styles: Dict):
    """Create billing summary section"""
    from config import GST_PERCENT
    
    story.append(Paragraph("BILLING SUMMARY", styles['header']))
    billing_data = [
        ['Base Amount:', f'₹ {booking["base_amount"]:.2f}'],
        [f'GST ({GST_PERCENT}%):', f'₹ {booking["gst"]:.2f}'],
        ['', ''],  # Empty row for spacing
        ['TOTAL AMOUNT:', f'₹ {booking["total"]:.2f}']
    ]
    
    billing_table = Table(billing_data, colWidths=[3*inch, 2*inch])
    billing_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 2), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, 2), 'Helvetica'),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTSIZE', (0, 3), (-1, 3), 14),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 3), (-1, 3), styles['primary_color']),
        ('ROWBACKGROUNDS', (0, 0), (-1, 2), [white, HexColor('#f8f9fa')]),
        ('BACKGROUND', (0, 3), (-1, 3), HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, 2), 0.5, HexColor('#e1e5e9')),
        ('GRID', (0, 3), (-1, 3), 1, styles['primary_color']),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 40))


def create_footer_section(story: List, styles: Dict):
    """Create footer section"""
    footer_text = f'''
        <para align="center">
        <font size="10" color="#666666">
        Thank you for choosing {AGENCY_NAME}!<br/>
        For any queries, please contact us at {AGENCY_PHONE} or {AGENCY_EMAIL}<br/>
        <i>Safe travels and happy journey!</i>
        </font>
        </para>
    '''
    story.append(Paragraph(footer_text, styles['normal']))


def generate_invoice_pdf(booking_id: int, booking: Dict[str, Any], customers: List = None) -> str:
    """Generate PDF invoice for a booking"""
    file_path = f'{BILLS_DIRECTORY}/invoice_{booking_id}.pdf'
    os.makedirs(BILLS_DIRECTORY, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=0.5*inch)
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
