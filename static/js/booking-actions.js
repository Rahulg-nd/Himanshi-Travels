// WhatsApp Functionality
function sendBookingWhatsApp(bookingId) {
    const confirmSend = confirm(`📱 Send WhatsApp Confirmation\n\nSend booking details via WhatsApp for booking #${String(bookingId).padStart(6, '0')}?\n\nThis will send booking information to the customer's phone number.`);
    
    if (!confirmSend) {
        return;
    }

    // Find the WhatsApp button and disable it temporarily
    const whatsappBtn = document.querySelector(`button[onclick="sendBookingWhatsApp(${bookingId})"]`);
    if (whatsappBtn) {
        const originalText = whatsappBtn.textContent;
        whatsappBtn.disabled = true;
        whatsappBtn.textContent = '📤 Sending...';
        
        // Re-enable after 5 seconds regardless of outcome
        setTimeout(() => {
            whatsappBtn.disabled = false;
            whatsappBtn.textContent = originalText;
        }, 5000);
    }

    fetch(`/send_whatsapp/${bookingId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`✅ WhatsApp message sent successfully for booking #${String(bookingId).padStart(6, '0')}`, 'success');
        } else {
            showNotification(`❌ Failed to send WhatsApp: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error sending WhatsApp:', error);
        showNotification('❌ Error sending WhatsApp. Please try again.', 'error');
    });
}

// Email Functionality
function sendBookingEmail(bookingId) {
    const confirmSend = confirm(`📧 Send Email Confirmation\n\nSend booking details via email for booking #${String(bookingId).padStart(6, '0')}?\n\nThis will send booking information and invoice to the customer's email address.`);
    
    if (!confirmSend) {
        return;
    }

    // Find the Email button and disable it temporarily
    const emailBtn = document.querySelector(`button[onclick="sendBookingEmail(${bookingId})"]`);
    if (emailBtn) {
        const originalText = emailBtn.textContent;
        emailBtn.disabled = true;
        emailBtn.textContent = '📤 Sending...';
        
        // Re-enable after 5 seconds regardless of outcome
        setTimeout(() => {
            emailBtn.disabled = false;
            emailBtn.textContent = originalText;
        }, 5000);
    }

    fetch(`/api/send_booking_email/${bookingId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`✅ Email sent successfully for booking #${String(bookingId).padStart(6, '0')}`, 'success');
        } else {
            showNotification(`❌ Failed to send email: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error sending email:', error);
        showNotification('❌ Error sending email. Please try again.', 'error');
    });
}

// Delete and Edit Booking Functionality
function deleteBooking(bookingId, customerName, buttonElement) {
    // First confirmation
    const firstConfirm = confirm(`⚠️ DELETE BOOKING WARNING ⚠️\n\nYou are about to delete:\nBooking #${String(bookingId).padStart(6, '0')} for ${customerName}\n\nThis will:\n• Remove the booking from the database\n• Delete the associated invoice file\n• This action CANNOT be undone\n\nAre you sure you want to continue?`);
    
    if (!firstConfirm) {
        return;
    }

    // Second confirmation for extra safety
    const secondConfirm = confirm(`🚨 FINAL CONFIRMATION 🚨\n\nLast chance to cancel!\n\nClick OK to permanently delete booking #${String(bookingId).padStart(6, '0')}\nClick Cancel to keep the booking`);
    
    if (!secondConfirm) {
        return;
    }

    // Disable the delete button temporarily
    const deleteBtn = buttonElement;
    const originalText = deleteBtn.textContent;
    deleteBtn.disabled = true;
    deleteBtn.textContent = '⏳ Deleting...';

    fetch(`/delete_booking/${bookingId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove from selection if it was selected
            selectedBookings.delete(bookingId);
            updateBulkActions();
            
            // Show success message
            showNotification(`✅ Successfully deleted booking #${String(bookingId).padStart(6, '0')}`, 'success');
            
            // Reload bookings list after a short delay
            setTimeout(() => searchBookings(currentPage), 1000);
        } else {
            // Re-enable button on error
            deleteBtn.disabled = false;
            deleteBtn.textContent = originalText;
            showNotification(`❌ Failed to delete booking: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting booking:', error);
        deleteBtn.disabled = false;
        deleteBtn.textContent = originalText;
        showNotification('❌ Network error occurred while deleting booking', 'error');
    });
}

function bulkDeleteBookings() {
    if (selectedBookings.size === 0) {
        showNotification('⚠️ No bookings selected for deletion', 'warning');
        return;
    }

    // First confirmation
    const firstConfirm = confirm(`⚠️ BULK DELETE WARNING ⚠️\n\nYou are about to delete ${selectedBookings.size} booking(s)\n\nThis will:\n• Remove all selected bookings from the database\n• Delete associated invoice files\n• This action CANNOT be undone\n\nAre you sure you want to continue?`);
    
    if (!firstConfirm) {
        return;
    }

    // Second confirmation for bulk operations
    const secondConfirm = confirm(`🚨 FINAL CONFIRMATION 🚨\n\nLast chance to cancel!\n\nClick OK to permanently delete ${selectedBookings.size} booking(s)\nClick Cancel to keep all bookings`);
    
    if (!secondConfirm) {
        return;
    }

    // Disable bulk delete button
    const bulkDeleteBtn = document.querySelector('.bulk-delete-btn');
    const originalText = bulkDeleteBtn.textContent;
    bulkDeleteBtn.disabled = true;
    bulkDeleteBtn.textContent = '⏳ Deleting...';

    fetch('/bulk_delete_bookings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            booking_ids: Array.from(selectedBookings)
        })
    })
    .then(response => response.json())
    .then(data => {
        bulkDeleteBtn.disabled = false;
        bulkDeleteBtn.textContent = originalText;
        
        if (data.success) {
            const deletedCount = data.deleted_count || selectedBookings.size;
            
            // Clear selections
            clearSelection();
            
            // Show success message
            showNotification(`✅ Successfully deleted ${deletedCount} booking(s)`, 'success');
            
            // Reload bookings list
            setTimeout(() => searchBookings(currentPage), 1000);
        } else {
            showNotification(`❌ Failed to delete bookings: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error bulk deleting bookings:', error);
        bulkDeleteBtn.disabled = false;
        bulkDeleteBtn.textContent = originalText;
        showNotification('❌ Network error occurred during bulk deletion', 'error');
    });
}

function editBooking(bookingId) {
    // Fetch booking data
    fetch(`/get_booking/${bookingId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateEditModal(data.booking);
                openEditModal();
            } else {
                showNotification(`❌ Error loading booking: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error fetching booking:', error);
            showNotification('❌ Network error occurred while loading booking', 'error');
        });
}

function populateEditModal(booking) {
    // Set booking ID
    document.getElementById('editBookingId').value = booking.id;
    
    // Set basic fields
    document.getElementById('editName').value = booking.name || '';
    document.getElementById('editEmail').value = booking.email || '';
    document.getElementById('editPhone').value = booking.phone || '';
    document.getElementById('editBookingType').value = booking.booking_type || '';
    
    // Set service fields
    document.getElementById('editHotelName').value = booking.hotel_name || '';
    document.getElementById('editHotelCity').value = booking.hotel_city || '';
    document.getElementById('editHotelCountry').value = booking.hotel_country || '';
    document.getElementById('editOperatorName').value = booking.operator_name || '';
    document.getElementById('editFromJourney').value = booking.from_journey || '';
    document.getElementById('editFromCountry').value = booking.from_journey_country || '';
    document.getElementById('editToJourney').value = booking.to_journey || '';
    document.getElementById('editToCountry').value = booking.to_journey_country || '';
    document.getElementById('editServiceDate').value = booking.service_date || '';
    document.getElementById('editServiceTime').value = booking.service_time || '';
    document.getElementById('editVehicleNumber').value = booking.vehicle_number || '';
    document.getElementById('editHotelNumber').value = booking.vehicle_number || '';
    
    // Handle group booking
    const isGroupBooking = booking.is_group_booking;
    document.getElementById('editGroupBookingToggle').checked = isGroupBooking;
    
    if (isGroupBooking && booking.customers && booking.customers.length > 0) {
        // Populate group customers
        populateEditCustomers(booking.customers);
        toggleEditGroupBooking(); // Show group fields
    } else {
        // Single booking
        document.getElementById('editBaseAmount').value = booking.base_amount || '';
        toggleEditGroupBooking(); // Show single fields
    }
    
    // Show appropriate service fields
    toggleEditServiceFields();
}

function populateEditCustomers(customers) {
    const customersList = document.getElementById('editCustomersList');
    customersList.innerHTML = '';
    
    customers.forEach((customer, index) => {
        addEditCustomer(customer, index);
    });
}

function addEditCustomer(customerData = null, index = null) {
    const customersList = document.getElementById('editCustomersList');
    const customerIndex = index !== null ? index : customersList.children.length;
    
    const customerDiv = document.createElement('div');
    customerDiv.className = 'customer-item';
    customerDiv.innerHTML = `
        <div class="customer-header">
            <div class="customer-title">
                <h4>🧑‍🤝‍🧑 Customer ${customerIndex + 1}</h4>
            </div>
            <button type="button" onclick="removeEditCustomer(this)" class="btn-remove-customer" title="Remove Customer">
                <i class="icon">🗑️</i>
                <span>Remove</span>
            </button>
        </div>
        <div class="customer-fields">
            <div class="form-row">
                <div class="form-group">
                    <label>Customer Name *</label>
                    <input type="text" name="customer_name" value="${customerData ? customerData.customer_name || '' : ''}" required placeholder="Enter customer name">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="customer_email" value="${customerData ? customerData.customer_email || '' : ''}" placeholder="Enter email address">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" name="customer_phone" value="${customerData ? customerData.customer_phone || '' : ''}" placeholder="Enter phone number">
                </div>
                <div class="form-group">
                    <label>Seat/Room Number</label>
                    <input type="text" name="seat_room_number" value="${customerData ? customerData.seat_room_number || '' : ''}" placeholder="e.g., A1, Room 101">
                </div>
            </div>
            <div class="form-group">
                <label>Amount (₹) *</label>
                <input type="number" name="customer_amount" value="${customerData ? customerData.customer_amount || '' : ''}" step="0.01" min="0" required placeholder="Enter amount" onchange="updateEditTotalAmount()">
            </div>
        </div>
    `;
    
    customersList.appendChild(customerDiv);
    updateEditCustomerNumbers();
    updateEditTotalAmount();
}

function removeEditCustomer(button) {
    button.closest('.customer-item').remove();
    updateEditCustomerNumbers();
    updateEditTotalAmount();
}

function updateEditCustomerNumbers() {
    const customers = document.querySelectorAll('#editCustomersList .customer-item');
    const customersCount = document.getElementById('editCustomersCount');
    const customersFooter = document.getElementById('editCustomersFooter');
    
    customers.forEach((customer, index) => {
        customer.querySelector('.customer-header h4').textContent = `🧑‍🤝‍🧑 Customer ${index + 1}`;
    });
    
    // Update customers count
    if (customersCount) {
        customersCount.textContent = `${customers.length} customer${customers.length !== 1 ? 's' : ''}`;
    }
    
    // Show/hide footer based on customer count
    if (customersFooter) {
        customersFooter.style.display = customers.length > 0 ? 'block' : 'none';
    }
}

function updateEditTotalAmount() {
    const customerAmounts = document.querySelectorAll('#editCustomersList input[name="customer_amount"]');
    let total = 0;
    
    customerAmounts.forEach(input => {
        const amount = parseFloat(input.value) || 0;
        total += amount;
    });
    
    const totalAmountElement = document.getElementById('editTotalAmount');
    if (totalAmountElement) {
        totalAmountElement.textContent = total.toFixed(2);
    }
}

function toggleEditGroupBooking() {
    const isGroup = document.getElementById('editGroupBookingToggle').checked;
    const singleFields = document.getElementById('editSingleCustomerFields');
    const singleAmountFields = document.getElementById('editSingleAmountFields');
    const groupSection = document.getElementById('editGroupCustomersSection');
    
    if (isGroup) {
        singleFields.style.display = 'none';
        if (singleAmountFields) singleAmountFields.style.display = 'none';
        groupSection.style.display = 'block';
        
        // If no customers exist, add one
        const customersList = document.getElementById('editCustomersList');
        if (customersList.children.length === 0) {
            addEditCustomer();
        } else {
            updateEditCustomerNumbers();
            updateEditTotalAmount();
        }
    } else {
        singleFields.style.display = 'block';
        if (singleAmountFields) singleAmountFields.style.display = 'block';
        groupSection.style.display = 'none';
    }
}

function toggleEditServiceFields() {
    const bookingType = document.getElementById('editBookingType').value;
    const hotelFields = document.getElementById('editHotelFields');
    const transportFields = document.getElementById('editTransportFields');
    
    // Hide all service fields first
    hotelFields.style.display = 'none';
    transportFields.style.display = 'none';
    
    // Show appropriate fields based on booking type
    if (bookingType === 'Hotel') {
        hotelFields.style.display = 'block';
    } else if (['Bus', 'Train', 'Flight', 'Transport'].includes(bookingType)) {
        transportFields.style.display = 'block';
    }
}

function openEditModal() {
    document.getElementById('editModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // Reset form
    document.getElementById('editBookingForm').reset();
    document.getElementById('editCustomersList').innerHTML = '';
}

// Handle edit form submission
document.getElementById('editBookingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const bookingId = document.getElementById('editBookingId').value;
    const isGroupBooking = document.getElementById('editGroupBookingToggle').checked;
    
    let formData;
    
    if (isGroupBooking) {
        // Collect group booking data
        formData = collectEditGroupBookingData();
    } else {
        // Collect single booking data
        formData = collectEditSingleBookingData();
    }
    
    // Add common fields
    formData.booking_type = document.getElementById('editBookingType').value;
    formData.hotel_name = document.getElementById('editHotelName').value;
    formData.hotel_city = document.getElementById('editHotelCity').value;
    formData.hotel_country = document.getElementById('editHotelCountry').value;
    formData.operator_name = document.getElementById('editOperatorName').value;
    formData.from_journey = document.getElementById('editFromJourney').value;
    formData.from_journey_country = document.getElementById('editFromCountry').value;
    formData.to_journey = document.getElementById('editToJourney').value;
    formData.to_journey_country = document.getElementById('editToCountry').value;
    formData.service_date = document.getElementById('editServiceDate').value;
    formData.service_time = document.getElementById('editServiceTime').value;
    formData.vehicle_train_flight_hotel_number = document.getElementById('editVehicleNumber').value || document.getElementById('editHotelNumber').value;
    
    // Submit the update
    fetch(`/update_booking/${bookingId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`✅ ${data.message}`, 'success');
            closeEditModal();
            // Refresh the bookings list
            searchBookings();
        } else {
            showNotification(`❌ Update failed: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error updating booking:', error);
        showNotification('❌ Network error occurred during update', 'error');
    });
});

function collectEditSingleBookingData() {
    return {
        is_group_booking: false,
        name: document.getElementById('editName').value,
        email: document.getElementById('editEmail').value,
        phone: document.getElementById('editPhone').value,
        base_amount: document.getElementById('editBaseAmount').value
    };
}

function collectEditGroupBookingData() {
    const customers = [];
    const customerItems = document.querySelectorAll('#editCustomersList .customer-item');
    
    customerItems.forEach(item => {
        const customer = {
            customer_name: item.querySelector('input[name="customer_name"]').value,
            customer_email: item.querySelector('input[name="customer_email"]').value,
            customer_phone: item.querySelector('input[name="customer_phone"]').value,
            seat_room_number: item.querySelector('input[name="seat_room_number"]').value,
            customer_amount: item.querySelector('input[name="customer_amount"]').value
        };
        
        if (customer.customer_name.trim()) {
            customers.push(customer);
        }
    });
    
    return {
        is_group_booking: true,
        customers: customers
    };
}
