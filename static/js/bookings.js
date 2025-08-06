// Bookings Management JavaScript
let currentPage = 1;
let currentPagination = null;
let selectedBookings = new Set();

// Load bookings on page load
document.addEventListener('DOMContentLoaded', function() {
    searchBookings(1);
});

// Search functionality with pagination
function searchBookings(page = 1) {
    const query = document.getElementById('searchQuery').value;
    const type = document.getElementById('bookingType').value;
    const perPage = document.getElementById('perPage').value;
    
    currentPage = page;
    
    // Clear selections when searching
    clearSelection();
    
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (type) params.append('type', type);
    params.append('page', page);
    params.append('per_page', perPage);
    
    // Show loading state
    document.getElementById('bookingsContainer').innerHTML = `
        <div class="loading">
            <h3>🔄 Loading bookings...</h3>
            <p>Please wait while we fetch your booking history.</p>
        </div>
    `;
    
    fetch(`/api/search_bookings?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            currentPagination = data.pagination;
            displayBookings(data.bookings);
            updateResultsCount(data.pagination);
            updatePaginationControls(data.pagination);
        })
        .catch(error => {
            console.error('Error searching bookings:', error);
            showNotification('❌ Failed to load bookings. Please try again.', 'error');
            document.getElementById('bookingsContainer').innerHTML = 
                '<div class="no-results"><h3>❌ Error</h3><p>Failed to load bookings. Please try again.</p></div>';
            hidePaginationControls();
        });
}

// Update results count
function updateResultsCount(pagination) {
    const resultsCount = document.getElementById('resultsCount');
    if (pagination.total === 0) {
        resultsCount.textContent = 'No bookings found';
    } else {
        const start = (pagination.page - 1) * pagination.per_page + 1;
        const end = Math.min(start + pagination.per_page - 1, pagination.total);
        resultsCount.textContent = `Showing ${start}-${end} of ${pagination.total} bookings`;
    }
}

// Get booking type icon
function getBookingIcon(type) {
    const icons = {
        'Hotel': '🏨',
        'Flight': '✈️',
        'Train': '🚆',
        'Bus': '🚌',
        'Transport': '🚐',
        'Tour Package': '🎒',
        'Other': '📋'
    };
    return icons[type] || '📋';
}
