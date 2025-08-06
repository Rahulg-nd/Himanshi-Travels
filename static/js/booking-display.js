// Booking Card Display and Interaction
function displayBookings(bookings) {
    const container = document.getElementById('bookingsContainer');
    
    if (bookings.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <h3>📭 No bookings found</h3>
                <p>Try adjusting your search criteria or create a new booking.</p>
            </div>
        `;
        return;
    }

    let html = '';
    bookings.forEach(booking => {
        html += generateBookingCard(booking);
    });

    container.innerHTML = html;
}

function generateBookingCard(booking) {
    const date = formatBookingDate(booking.date);
    const serviceDetails = generateServiceDetails(booking);
    const timingDetails = generateTimingDetails(booking);
    const customerDetails = generateCustomerDetails(booking);
    const bookingTypeDisplay = generateBookingTypeDisplay(booking);
    const amountDetails = generateAmountDetails(booking);

    return `
        <div class="booking-card" id="booking-${booking.id}">
            <input type="checkbox" class="booking-checkbox" data-booking-id="${booking.id}" 
                   onchange="toggleBookingSelection(${booking.id})">
            <div class="booking-header">
                <div class="booking-id">Booking #${String(booking.id).padStart(6, '0')}</div>
                <div class="booking-type ${booking.booking_type}">${bookingTypeDisplay}</div>
            </div>
            <div class="booking-details">
                ${customerDetails}
                ${serviceDetails}
                ${timingDetails}
                ${amountDetails}
                <div class="detail-group">
                    <h4>Booking Date</h4>
                    <p>${date}</p>
                </div>
            </div>
            <div class="booking-actions">
                <a href="/invoice/${booking.id}" target="_blank" class="action-btn download-btn">
                    📄 Download Invoice
                </a>
                <button onclick="editBooking(${booking.id})" class="action-btn edit-btn">
                    ✏️ Edit
                </button>
                <button onclick="deleteBooking(${booking.id}, '${booking.name || 'Customer'}', this)" 
                        class="action-btn delete-btn">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `;
}

function formatBookingDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function generateServiceDetails(booking) {
    if (booking.booking_type === 'Hotel' && (booking.hotel_name || booking.hotel_city)) {
        return `
            <div class="detail-group">
                <h4>Hotel Details</h4>
                <p>${booking.hotel_name || 'N/A'} ${booking.hotel_city ? '• ' + booking.hotel_city : ''}</p>
                ${booking.vehicle_number ? `<p>Room: ${booking.vehicle_number}</p>` : ''}
            </div>
        `;
    } else if (booking.booking_type !== 'Hotel' && (booking.operator_name || booking.from_journey || booking.to_journey)) {
        return `
            <div class="detail-group">
                <h4>Journey Details</h4>
                <p>${booking.operator_name || 'N/A'}</p>
                ${(booking.from_journey || booking.to_journey) ? 
                    `<p>${booking.from_journey || 'N/A'} → ${booking.to_journey || 'N/A'}</p>` : ''}
                ${booking.vehicle_number ? `<p>Vehicle: ${booking.vehicle_number}</p>` : ''}
            </div>
        `;
    }
    return '';
}

function generateTimingDetails(booking) {
    if (booking.service_date || booking.service_time) {
        return `
            <div class="detail-group">
                <h4>Service Timing</h4>
                ${booking.service_date ? `<p>📅 ${booking.service_date}</p>` : ''}
                ${booking.service_time ? `<p>🕐 ${booking.service_time}</p>` : ''}
            </div>
        `;
    }
    return '';
}

function generateCustomerDetails(booking) {
    if (booking.is_group_booking) {
        const displayNames = booking.customer_names.slice(0, 2);
        const remainingCount = booking.customer_count - displayNames.length;
        const namesList = displayNames.join(', ') + (remainingCount > 0 ? ` + ${remainingCount} more` : '');
        
        return `
            <div class="detail-group">
                <h4>Group Booking (${booking.customer_count} customers)</h4>
                <p>${namesList}</p>
                <p>Contact: ${booking.email}</p>
                <p>${booking.phone}</p>
            </div>
        `;
    } else {
        return `
            <div class="detail-group">
                <h4>Customer</h4>
                <p>${booking.name}</p>
                <p>${booking.email}</p>
                <p>${booking.phone}</p>
            </div>
        `;
    }
}

function generateBookingTypeDisplay(booking) {
    return booking.is_group_booking ? 
        `👥 ${booking.booking_type} (Group)` : 
        `${getBookingIcon(booking.booking_type)} ${booking.booking_type}`;
}

function generateAmountDetails(booking) {
    return `
        <div class="detail-group">
            <h4>Amount Details</h4>
            <p>Base: ₹${parseFloat(booking.base_amount || 0).toFixed(2)}</p>
            <p>GST: ₹${parseFloat(booking.gst || 0).toFixed(2)}</p>
            <p><strong>Total: ₹${parseFloat(booking.total || 0).toFixed(2)}</strong></p>
        </div>
    `;
}
