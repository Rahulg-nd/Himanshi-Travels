/**
 * Single Booking Management
 * Functions for handling single customer bookings
 */

/**
 * Handle single booking form submission
 */
function handleSingleBookingSubmission() {
    setSubmitButtonLoading(true);
    
    const formData = new FormData(document.getElementById('bookingForm'));
    
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
                updateGstCalculation();
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
