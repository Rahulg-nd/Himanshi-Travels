/**
 * Notification System
 * Toast notification functionality
 */

/**
 * Show notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - How long to show the notification (0 for permanent)
 */
function showNotification(message, type = 'success', duration = 5000) {
    const container = document.getElementById('notification-container');
    
    // Remove any existing notifications
    const existingNotifications = container.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="close-btn" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    container.appendChild(notification);
    
    // Show notification with animation
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Auto dismiss
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
}
