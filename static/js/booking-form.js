/**
 * Himanshi Travels - Booking Form JavaScript
 * Main functionality for the travel booking form
 */

// Global variables
window.customerCount = 0;

/**
 * Toggle conditional fields based on booking type
 */
function toggleConditionalFields() {
    const bookingType = document.getElementById('booking_type').value;
    const hotelFields = document.getElementById('hotel-fields');
    const transportFields = document.getElementById('transport-fields');
    const serviceDetails = document.getElementById('service-details');
    const vehicleLabel = document.getElementById('vehicle_label');

    // Hide all conditional fields first
    hotelFields.classList.remove('active');
    transportFields.classList.remove('active');
    serviceDetails.style.display = 'none';

    // Show relevant fields based on booking type
    if (bookingType === 'Hotel') {
        hotelFields.classList.add('active');
        serviceDetails.style.display = 'block';
        vehicleLabel.textContent = 'Room Number';
        document.getElementById('vehicle_number').placeholder = 'Enter room number';
        showNotification('🏨 Hotel booking selected. Add hotel details and enable group booking for multiple guests!', 'info', 3000);
        
        // Reinitialize autocomplete for hotel fields
        if (typeof reinitializeAutoCompleteForVisibleFields === 'function') {
            reinitializeAutoCompleteForVisibleFields();
        }
    } else if (['Flight', 'Train', 'Bus', 'Transport'].includes(bookingType)) {
        transportFields.classList.add('active');
        serviceDetails.style.display = 'block';
        
        // Update labels based on type
        if (bookingType === 'Flight') {
            vehicleLabel.textContent = 'Flight Number';
            document.getElementById('vehicle_number').placeholder = 'Enter flight number';
            showNotification('✈️ Flight booking selected. Add flight details and enable group booking for multiple customers!', 'info', 3000);
        } else if (bookingType === 'Train') {
            vehicleLabel.textContent = 'Train Number';
            document.getElementById('vehicle_number').placeholder = 'Enter train number';
            showNotification('🚆 Train booking selected. Add train details and enable group booking for multiple customers!', 'info', 3000);
        } else if (bookingType === 'Bus') {
            vehicleLabel.textContent = 'Bus Number';
            document.getElementById('vehicle_number').placeholder = 'Enter bus number';
            showNotification('🚌 Bus booking selected. Add bus details and enable group booking for multiple customers!', 'info', 3000);
        } else if (bookingType === 'Transport') {
            vehicleLabel.textContent = 'Vehicle Number';
            document.getElementById('vehicle_number').placeholder = 'Enter vehicle number';
            showNotification('🚐 Transport booking selected. Add vehicle details and enable group booking for multiple customers!', 'info', 3000);
        }
        
        // Reinitialize autocomplete for transport fields
        if (typeof reinitializeAutoCompleteForVisibleFields === 'function') {
            reinitializeAutoCompleteForVisibleFields();
        }
    }
}

/**
 * Toggle between single and group booking modes
 */
function toggleGroupBooking() {
    const isGroupBooking = document.getElementById('is_group_booking').checked;
    const groupCustomers = document.getElementById('group-customers');
    const singleAmount = document.getElementById('single-amount');
    
    if (isGroupBooking) {
        groupCustomers.style.display = 'block';
        singleAmount.style.display = 'none';
        document.getElementById('base_amount').removeAttribute('required');
        
        // Remove required attributes from main customer fields for group bookings
        document.getElementById('name').removeAttribute('required');
        document.getElementById('email').removeAttribute('required');
        document.getElementById('phone').removeAttribute('required');
        
        // Add first customer if none exist
        if (window.customerCount === 0) {
            addCustomer();
        }
        
        showNotification('👥 Group booking mode enabled. Add multiple customers below.', 'info', 3000);
    } else {
        groupCustomers.style.display = 'none';
        singleAmount.style.display = 'block';
        document.getElementById('base_amount').setAttribute('required', 'required');
        
        // Restore required attributes for main customer fields in single booking
        document.getElementById('name').setAttribute('required', 'required');
        document.getElementById('email').setAttribute('required', 'required');
        document.getElementById('phone').setAttribute('required', 'required');
        
        // Clear customers
        document.getElementById('customers-list').innerHTML = '';
        window.customerCount = 0;
        updateTotal();
        
        showNotification('👤 Single booking mode enabled.', 'info', 2000);
    }
}

/**
 * Calculate and update totals
 */
function updateTotal() {
    const amounts = document.querySelectorAll('input[name^="customer_amount_"]');
    const singleAmountInput = document.getElementById('base_amount');
    const isGroupBooking = document.getElementById('is_group_booking').checked;
    let baseTotal = 0;
    
    if (isGroupBooking) {
        // For group bookings, sum all customer amounts
        amounts.forEach(input => {
            const value = parseFloat(input.value) || 0;
            baseTotal += value;
        });
        
        // Update the base amount field with the calculated total
        singleAmountInput.value = baseTotal.toFixed(2);
        
        // Update group booking total display
        document.getElementById('total-amount').textContent = baseTotal.toFixed(2);
        
        // Also update GST calculation based on group total
        updateGstCalculation();
    } else {
        // For single bookings, use base amount
        baseTotal = parseFloat(singleAmountInput.value) || 0;
        updateGstCalculation();
    }
}

/**
 * Update GST calculation display
 */
function updateGstCalculation() {
    const baseAmountInput = document.getElementById('base_amount');
    const applyGstCheckbox = document.getElementById('apply_gst');
    const gstRow = document.getElementById('gst-row');
    const gstDisplay = document.getElementById('gst-display');
    const finalTotalDisplay = document.getElementById('final-total');
    const baseDisplay = document.getElementById('base-display');
    const isGroupBooking = document.getElementById('is_group_booking').checked;
    
    let baseAmount = parseFloat(baseAmountInput.value) || 0;
    let gstAmount = 0;
    let finalAmount = baseAmount;
    
    if (applyGstCheckbox.checked) {
        // Use GST percentage from configuration
        const gstPercentage = window.GST_PERCENT || 5; // Default to 5% if not set
        gstAmount = baseAmount * (gstPercentage / 100);
        finalAmount += gstAmount;
        gstRow.style.display = 'block';
    } else {
        gstRow.style.display = 'none';
    }
    
    // Update displays
    baseDisplay.textContent = baseAmount.toFixed(2);
    gstDisplay.textContent = gstAmount.toFixed(2);
    finalTotalDisplay.textContent = finalAmount.toFixed(2);
    
    // If group booking, also update the group total display
    if (isGroupBooking) {
        const groupTotalDisplay = document.getElementById('total-amount');
        if (groupTotalDisplay) {
            groupTotalDisplay.textContent = finalAmount.toFixed(2);
        }
    }
}

/**
 * Set submit button loading state
 */
function setSubmitButtonLoading(loading) {
    const submitBtn = document.querySelector('.submit-btn');
    if (loading) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
    } else {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        submitBtn.textContent = '🎯 Create Booking & Generate Invoice';
    }
}

/**
 * Initialize form event listeners
 */
function initializeForm() {
    // Form submission handler
    document.getElementById('bookingForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const isGroupBooking = document.getElementById('is_group_booking').checked;
        
        if (isGroupBooking) {
            handleGroupBookingSubmission();
        } else {
            handleSingleBookingSubmission();
        }
    });

    // Initialize GST calculation
    updateGstCalculation();
    
    // Initialize AutoComplete functionality
    if (typeof initializeAutoComplete === 'function') {
        console.log('Initializing AutoComplete...');
        initializeAutoComplete();
    } else {
        console.warn('AutoComplete initialization function not found');
    }
}
