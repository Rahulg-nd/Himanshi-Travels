/**
 * Group Booking Management
 * Functions for handling multiple customers in group bookings
 */

/**
 * Add a new customer to the group booking
 */
function addCustomer() {
    // Access global customerCount variable
    window.customerCount++;
    const customersList = document.getElementById('customers-list');
    
    const customerHtml = `
        <div class="customer-item" id="customer-${window.customerCount}">
            <div class="customer-header">
                <span class="customer-number">Customer ${window.customerCount}</span>
                ${window.customerCount > 1 ? `<button type="button" class="remove-customer" onclick="removeCustomer(${window.customerCount})">×</button>` : ''}
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Full Name *</label>
                    <input type="text" name="customer_name_${window.customerCount}" required placeholder="Enter customer name" onchange="validateCustomers()">
                </div>
                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="tel" name="customer_phone_${window.customerCount}" placeholder="Enter phone number">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="customer_email_${window.customerCount}" placeholder="Enter email address">
                </div>
                <div class="form-group">
                    <label id="seat_label_${window.customerCount}">Seat/Room Number</label>
                    <input type="text" name="customer_seat_${window.customerCount}" placeholder="Enter seat/room number">
                </div>
            </div>
            <div class="form-group">
                <label>Amount (₹) *</label>
                <input type="number" name="customer_amount_${window.customerCount}" required placeholder="Enter amount" min="1" step="0.01" onchange="updateTotal()">
            </div>
        </div>
    `;
    
    customersList.insertAdjacentHTML('beforeend', customerHtml);
    updateSeatLabels();
    updateTotal();
}

/**
 * Remove a customer from the group booking
 */
function removeCustomer(customerId) {
    const customerElement = document.getElementById(`customer-${customerId}`);
    if (customerElement) {
        customerElement.remove();
        renumberCustomers();
        updateTotal();
    }
}

/**
 * Renumber customers after removal
 */
function renumberCustomers() {
    const customers = document.querySelectorAll('.customer-item');
    window.customerCount = 0;
    
    customers.forEach((customer, index) => {
        window.customerCount = index + 1;
        customer.id = `customer-${customerCount}`;
        
        // Update customer number display
        const numberSpan = customer.querySelector('.customer-number');
        numberSpan.textContent = `Customer ${customerCount}`;
        
        // Update remove button if it exists
        const removeBtn = customer.querySelector('.remove-customer');
        if (removeBtn) {
            removeBtn.setAttribute('onclick', `removeCustomer(${customerCount})`);
        }
        
        // Update input names
        const inputs = customer.querySelectorAll('input');
        inputs.forEach(input => {
            const name = input.name;
            if (name.includes('customer_')) {
                const baseName = name.substring(0, name.lastIndexOf('_'));
                input.name = `${baseName}_${customerCount}`;
            }
        });
        
        // Update seat label ID
        const seatLabel = customer.querySelector('[id^="seat_label_"]');
        if (seatLabel) {
            seatLabel.id = `seat_label_${customerCount}`;
        }
    });
}

/**
 * Update seat/room labels based on booking type
 */
function updateSeatLabels() {
    const bookingType = document.getElementById('booking_type').value;
    const seatLabels = document.querySelectorAll('[id^="seat_label_"]');
    
    seatLabels.forEach(label => {
        if (bookingType === 'Hotel') {
            label.textContent = 'Room Number';
        } else {
            label.textContent = 'Seat Number';
        }
    });
}

/**
 * Validate customers data for group booking
 */
function validateCustomers() {
    const customerNames = document.querySelectorAll('input[name^="customer_name_"]');
    const customerAmounts = document.querySelectorAll('input[name^="customer_amount_"]');
    let isValid = true;
    
    // Check customer names
    customerNames.forEach((input, index) => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#dc3545';
        } else {
            input.style.borderColor = '#e1e5e9';
        }
    });
    
    // Check customer amounts
    customerAmounts.forEach((input, index) => {
        if (!input.value || parseFloat(input.value) <= 0) {
            isValid = false;
            input.style.borderColor = '#dc3545';
        } else {
            input.style.borderColor = '#e1e5e9';
        }
    });
    
    return isValid;
}

/**
 * Handle group booking form submission
 */
function handleGroupBookingSubmission() {
    console.log('handleGroupBookingSubmission called');
    
    // Validate customers
    if (!validateCustomers()) {
        console.log('Customer validation failed');
        showNotification('Please fill in all required customer information.', 'error');
        return;
    }
    
    console.log('Customer validation passed');
    setSubmitButtonLoading(true);
    
    // Collect customers data
    const customers = [];
    for (let i = 1; i <= window.customerCount; i++) {
        const name = document.querySelector(`input[name="customer_name_${i}"]`)?.value?.trim();
        const email = document.querySelector(`input[name="customer_email_${i}"]`)?.value?.trim();
        const phone = document.querySelector(`input[name="customer_phone_${i}"]`)?.value?.trim();
        const seat = document.querySelector(`input[name="customer_seat_${i}"]`)?.value?.trim();
        const amount = document.querySelector(`input[name="customer_amount_${i}"]`)?.value;
        
        if (name && amount) {
            customers.push({
                name: name,
                email: email || '',
                phone: phone || '',
                seat_room: seat || '',
                amount: parseFloat(amount)
            });
        }
    }
    
    if (customers.length === 0) {
        showNotification('Please add at least one customer.', 'error');
        setSubmitButtonLoading(false);
        return;
    }
    
    // Prepare form data
    const formData = new FormData(document.getElementById('bookingForm'));
    formData.append('customers_data', JSON.stringify(customers));
    formData.append('is_group_booking', 'true'); // Explicitly set group booking flag
    
    // Submit the form
    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        setSubmitButtonLoading(false);
        
        if (data.success) {
            showNotification(data.message, 'success');
            
            // Redirect to PDF after a short delay
            setTimeout(() => {
                window.open(data.pdf_url, '_blank');
                
                // Reset form
                document.getElementById('bookingForm').reset();
                document.getElementById('customers-list').innerHTML = '';
                window.customerCount = 0;
                toggleGroupBooking(); // Reset to single booking mode
            }, 1500);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        setSubmitButtonLoading(false);
        showNotification('An error occurred while processing your booking. Please try again.', 'error');
        console.error('Error:', error);
    });
}
