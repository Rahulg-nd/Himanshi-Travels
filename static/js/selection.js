// Selection and Bulk Actions
function toggleBookingSelection(bookingId) {
    const checkbox = document.querySelector(`input[data-booking-id="${bookingId}"]`);
    const card = document.getElementById(`booking-${bookingId}`);
    
    if (checkbox.checked) {
        selectedBookings.add(bookingId);
        card.classList.add('selected');
    } else {
        selectedBookings.delete(bookingId);
        card.classList.remove('selected');
    }
    
    updateBulkActions();
    updateSelectAllCheckbox();
}

// Toggle select all on current page
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const bookingCheckboxes = document.querySelectorAll('.booking-checkbox');
    
    bookingCheckboxes.forEach(checkbox => {
        const bookingId = parseInt(checkbox.dataset.bookingId);
        checkbox.checked = selectAllCheckbox.checked;
        
        if (selectAllCheckbox.checked) {
            selectedBookings.add(bookingId);
            document.getElementById(`booking-${bookingId}`).classList.add('selected');
        } else {
            selectedBookings.delete(bookingId);
            document.getElementById(`booking-${bookingId}`).classList.remove('selected');
        }
    });
    
    updateBulkActions();
}

// Update select all checkbox state
function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const bookingCheckboxes = document.querySelectorAll('.booking-checkbox');
    const checkedCheckboxes = document.querySelectorAll('.booking-checkbox:checked');
    
    if (checkedCheckboxes.length === 0) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = false;
    } else if (checkedCheckboxes.length === bookingCheckboxes.length) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = true;
    } else {
        selectAllCheckbox.indeterminate = true;
        selectAllCheckbox.checked = false;
    }
}

// Update bulk actions visibility
function updateBulkActions() {
    const bulkActions = document.getElementById('bulkActions');
    const selectedCount = document.getElementById('selectedCount');
    
    selectedCount.textContent = selectedBookings.size;
    
    if (selectedBookings.size > 0) {
        bulkActions.classList.add('active');
    } else {
        bulkActions.classList.remove('active');
    }
}

// Clear all selections
function clearSelection() {
    const previousCount = selectedBookings.size;
    selectedBookings.clear();
    document.querySelectorAll('.booking-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    document.querySelectorAll('.booking-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.getElementById('selectAll').checked = false;
    document.getElementById('selectAll').indeterminate = false;
    updateBulkActions();
    
    if (previousCount > 0) {
        showNotification(`✅ Cleared selection of ${previousCount} booking(s)`, 'success', 2000);
    }
}
