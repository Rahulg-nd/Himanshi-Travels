// Configuration Management JavaScript Module

class ConfigManager {
    constructor() {
        console.log('ConfigManager constructor called');
        try {
            this.changedConfigs = new Set();
            console.log('changedConfigs initialized:', this.changedConfigs);
            this.initializeEventListeners();
            // Note: loadCurrentLogo is handled by logo-manager.js
            console.log('ConfigManager constructor complete');
        } catch (error) {
            console.error('Error in ConfigManager constructor:', error);
            throw error;
        }
    }

    initializeEventListeners() {
        console.log('ConfigManager: Initializing event listeners');
        try {
            // Logo file input
            const logoFileInput = document.getElementById('logo-file');
            if (logoFileInput) {
                logoFileInput.addEventListener('change', this.handleFileSelect.bind(this));
                console.log('Logo file input listener added');
            }

            // Drag and drop for upload area
            const uploadArea = document.getElementById('upload-area');
            if (uploadArea) {
                uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
                uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
                uploadArea.addEventListener('drop', this.handleDrop.bind(this));
                console.log('Upload area listeners added');
            }

            // Keyboard accessibility for section headers
            const sectionHeaders = document.querySelectorAll('.section-header');
            console.log('Found section headers:', sectionHeaders.length);
            sectionHeaders.forEach(header => {
                header.addEventListener('keydown', this.handleKeyDown.bind(this));
            });
            
            console.log('All event listeners initialized successfully');
        } catch (error) {
            console.error('Error initializing event listeners:', error);
        }
    }

    handleKeyDown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            const sectionId = event.target.getAttribute('onclick').match(/'([^']+)'/)[1];
            this.toggleSection(sectionId);
        }
    }

    toggleSection(sectionId) {
        const header = document.querySelector(`[onclick*="${sectionId}"]`);
        const content = document.getElementById(`section-${sectionId}`);
        const toggle = header.querySelector('.section-toggle');
        
        if (content.classList.contains('expanded')) {
            content.classList.remove('expanded');
            header.setAttribute('aria-expanded', 'false');
            toggle.textContent = '▶';
        } else {
            content.classList.add('expanded');
            header.setAttribute('aria-expanded', 'true');
            toggle.textContent = '▼';
        }
    }

    markConfigChanged(configKey) {
        console.log('markConfigChanged called with:', configKey);
        this.changedConfigs.add(configKey);
        const configItem = document.querySelector(`[data-config-key="${configKey}"]`);
        if (configItem) {
            configItem.classList.add('changed');
        }
        this.validateField(configKey);
        console.log('changedConfigs now contains:', this.changedConfigs);
    }

    validateField(configKey) {
        const field = document.getElementById(configKey);
        
        // Skip validation if field doesn't exist
        if (!field) {
            console.log(`Field ${configKey} not found, skipping validation`);
            return true;
        }
        
        const validationDiv = document.getElementById(`validation-${configKey}`);
        const value = field.type === 'checkbox' ? field.checked : field.value;
        
        console.log(`Validating field ${configKey}: type=${field.type}, value="${value}", required=${field.hasAttribute('required')}`);
        
        // Clear any existing validation messages first
        if (validationDiv) {
            validationDiv.textContent = '';
            validationDiv.className = 'validation-message';
        }
        
        // Only validate if field is required and empty
        if (field.hasAttribute('required') && (!value || value.toString().trim() === '')) {
            if (validationDiv) {
                this.showValidationError(validationDiv, 'This field is required');
            }
            console.log(`Validation failed for required field: ${configKey} - field is empty`);
            return false;
        }

        // Only validate format if field has value
        if (value && value.toString().trim() !== '') {
            // Email validation
            if (field.type === 'email') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    if (validationDiv) {
                        this.showValidationError(validationDiv, 'Invalid email format');
                    }
                    console.log(`Email validation failed for ${configKey}: "${value}"`);
                    return false;
                }
                console.log(`Email validation passed for ${configKey}: "${value}"`);
            }

            // URL validation
            if (field.type === 'url') {
                try {
                    new URL(value);
                } catch {
                    if (validationDiv) {
                        this.showValidationError(validationDiv, 'Invalid URL format');
                    }
                    console.log(`URL validation failed for ${configKey}: "${value}"`);
                    return false;
                }
                console.log(`URL validation passed for ${configKey}: "${value}"`);
            }

            // Phone validation (more lenient)
            if (field.type === 'tel') {
                const phoneRegex = /^[\+]?[\d\s\-\(\)]{7,}$/;
                if (!phoneRegex.test(value)) {
                    if (validationDiv) {
                        this.showValidationError(validationDiv, 'Invalid phone number format');
                    }
                    console.log(`Phone validation failed for ${configKey}: "${value}"`);
                    return false;
                }
                console.log(`Phone validation passed for ${configKey}: "${value}"`);
            }

            // Additional validation for SMTP_HOST (should be a valid hostname)
            if (configKey === 'SMTP_HOST') {
                // More lenient hostname validation - allow common SMTP hosts
                const hostRegex = /^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,253}[a-zA-Z0-9])?$/;
                if (!hostRegex.test(value) && value.length > 0) {
                    if (validationDiv) {
                        this.showValidationError(validationDiv, 'Invalid hostname format');
                    }
                    console.log(`SMTP_HOST validation failed for ${configKey}: "${value}"`);
                    return false;
                }
                console.log(`SMTP_HOST validation passed for ${configKey}: "${value}"`);
            }
        }

        // Show success if validation div exists
        if (validationDiv) {
            this.showValidationSuccess(validationDiv, 'Valid');
        }
        return true;
    }

    showValidationError(element, message) {
        element.textContent = message;
        element.className = 'validation-message error';
    }

    showValidationSuccess(element, message) {
        element.textContent = message;
        element.className = 'validation-message success';
    }

    togglePassword(fieldId) {
        const field = document.getElementById(fieldId);
        const button = field.parentNode.querySelector('.password-toggle');
        
        if (field.type === 'password') {
            field.type = 'text';
            button.textContent = '🙈';
        } else {
            field.type = 'password';
            button.textContent = '👁️';
        }
    }

    async saveAllConfigs() {
        console.log('saveAllConfigs called');
        console.log('changedConfigs:', this.changedConfigs);
        
        // Collect configuration values from config items only
        const configItems = document.querySelectorAll('.config-item');
        const configs = {};
        let hasValidationErrors = false;
        let configCount = 0;
        let validationErrors = [];
        
        // Process all config items to get current values
        for (const item of configItems) {
            const configKey = item.getAttribute('data-config-key');
            if (!configKey) continue;
            
            const input = item.querySelector('input, select, textarea');
            if (!input) continue;
            
            configCount++;
            console.log(`Processing config: ${configKey}`);
            
            // Only validate required fields that are empty
            const hasValue = input.type === 'checkbox' ? input.checked : (input.value && input.value.trim() !== '');
            const isRequired = input.hasAttribute('required');
            
            // Only fail validation for truly required empty fields
            if (isRequired && !hasValue) {
                console.log(`Checking required field ${configKey}: hasValue=${hasValue}`);
                if (!this.validateField(configKey)) {
                    hasValidationErrors = true;
                    validationErrors.push(configKey);
                    console.log(`Validation failed for required field: ${configKey}`);
                    continue;
                }
            } else if (hasValue) {
                // Only validate format if field has a value
                console.log(`Checking format for field ${configKey} with value: "${input.value}"`);
                if (!this.validateField(configKey)) {
                    hasValidationErrors = true;
                    validationErrors.push(configKey);
                    console.log(`Format validation failed for: ${configKey}`);
                    continue;
                }
            } else {
                console.log(`Skipping validation for optional empty field: ${configKey}`);
            }
            
            // Get value based on input type
            configs[configKey] = input.type === 'checkbox' ? input.checked : input.value;
        }
        
        console.log(`Processed ${configCount} config items, collected ${Object.keys(configs).length} configs`);
        console.log('Collected configs:', configs);
        
        if (Object.keys(configs).length === 0) {
            this.showNotification('No configuration fields found to save', 'warning');
            return;
        }
        
        if (hasValidationErrors) {
            this.showNotification(`Validation errors in fields: ${validationErrors.join(', ')}. Please check and fix them before saving.`, 'error');
            return;
        }

        try {
            this.showNotification('Saving configurations...', 'info');
            
            const response = await fetch('/api/config/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configs)
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('All configurations saved successfully!', 'success');
                // Clear the changed configs set since everything is now saved
                this.changedConfigs.clear();
                document.querySelectorAll('.config-item.changed').forEach(item => {
                    item.classList.remove('changed');
                });
            } else {
                this.showNotification(`Save failed: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Save failed: ${error.message}`, 'error');
        }
    }

    async resetToDefaults() {
        if (!confirm('Are you sure you want to reset all configurations to default values? This action cannot be undone.')) {
            return;
        }

        try {
            this.showNotification('Resetting to defaults...', 'info');
            
            const response = await fetch('/api/config/reset', {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Configuration reset to defaults successfully!', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showNotification(`Reset failed: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Reset failed: ${error.message}`, 'error');
        }
    }

    async testConfiguration(category) {
        try {
            this.showNotification(`Testing ${category} configuration...`, 'info');
            
            const response = await fetch(`/api/config/test/${category}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(result.message || `${category} configuration test successful!`, 'success');
            } else {
                this.showNotification(`Test failed: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Test failed: ${error.message}`, 'error');
        }
    }

    async resetCategory(category) {
        if (!confirm(`Are you sure you want to reset ${category} settings to defaults?`)) {
            return;
        }

        try {
            this.showNotification(`Resetting ${category} to defaults...`, 'info');
            
            const response = await fetch(`/api/config/reset/${category}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(`${category} settings reset successfully!`, 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showNotification(`Reset failed: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Reset failed: ${error.message}`, 'error');
        }
    }

    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
        } else if (document.getElementById('notification-container')) {
            // Create a simple notification element if container exists
            const container = document.getElementById('notification-container');
            const notification = document.createElement('div');
            notification.style.cssText = `
                padding: 15px;
                margin: 10px 0;
                border-radius: 4px;
                background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#fff3cd'};
                color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#856404'};
                border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#ffeaa7'};
            `;
            notification.textContent = message;
            
            // Clear existing notifications
            container.innerHTML = '';
            container.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 5000);
        } else {
            // Ultimate fallback
            alert(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Global ConfigManager instance
let configManagerInstance = null;

// Ensure initialization happens
function initializeConfigManager() {
    console.log('initializeConfigManager called');
    try {
        if (!configManagerInstance) {
            console.log('Creating new ConfigManager instance');
            configManagerInstance = new ConfigManager();
            console.log('ConfigManager instance created:', configManagerInstance);
            
            // Initialize all sections as expanded by default for better UX
            const allSections = document.querySelectorAll('.section-content');
            const allHeaders = document.querySelectorAll('.section-header');
            
            console.log('Found sections:', allSections.length, 'headers:', allHeaders.length);
            
            allSections.forEach(section => {
                section.classList.add('expanded');
            });
            
            allHeaders.forEach(header => {
                header.setAttribute('aria-expanded', 'true');
                const toggle = header.querySelector('.section-toggle');
                if (toggle) toggle.textContent = '▼';
            });
            
            console.log('ConfigManager initialization complete');
        } else {
            console.log('ConfigManager instance already exists');
        }
    } catch (error) {
        console.error('Error initializing ConfigManager:', error);
    }
}

// Global functions for template onclick handlers
function toggleSection(sectionId) {
    if (configManagerInstance) {
        configManagerInstance.toggleSection(sectionId);
    }
}

function handleKeyDown(event, sectionId) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleSection(sectionId);
    }
}

function saveAllConfigs() {
    console.log('Global saveAllConfigs called');
    console.log('configManagerInstance:', configManagerInstance);
    
    // Try to initialize if not available
    if (!configManagerInstance) {
        console.log('ConfigManager not initialized, attempting to initialize...');
        initializeConfigManager();
    }
    
    if (configManagerInstance) {
        configManagerInstance.saveAllConfigs();
    } else {
        console.error('configManagerInstance is still null after initialization attempt');
        alert('Configuration system not ready. Please refresh the page and try again.');
    }
}

function resetToDefaults() {
    console.log('Global resetToDefaults called');
    console.log('configManagerInstance:', configManagerInstance);
    
    // Try to initialize if not available
    if (!configManagerInstance) {
        console.log('ConfigManager not initialized, attempting to initialize...');
        initializeConfigManager();
    }
    
    if (configManagerInstance) {
        configManagerInstance.resetToDefaults();
    } else {
        console.error('configManagerInstance is still null after initialization attempt');
        alert('Configuration system not ready. Please refresh the page and try again.');
    }
}

function markConfigChanged(configKey) {
    if (configManagerInstance) {
        configManagerInstance.markConfigChanged(configKey);
    }
}

function testConfiguration(category) {
    if (configManagerInstance) {
        configManagerInstance.testConfiguration(category);
    }
}

function resetCategory(category) {
    if (configManagerInstance) {
        configManagerInstance.resetCategory(category);
    }
}

function togglePassword(fieldKey) {
    const passwordInput = document.getElementById(fieldKey);
    const toggleButton = passwordInput.nextElementSibling;
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = '🙈';
        toggleButton.setAttribute('aria-label', 'Hide password');
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = '👁️';
        toggleButton.setAttribute('aria-label', 'Show password');
    }
}

function testNotification() {
    console.log('testNotification called');
    
    // Try to initialize if not available
    if (!configManagerInstance) {
        console.log('ConfigManager not initialized, attempting to initialize...');
        initializeConfigManager();
    }
    
    if (configManagerInstance) {
        configManagerInstance.showNotification('Test notification is working!', 'success');
    } else {
        console.error('ConfigManager instance still not available');
        alert('ConfigManager instance not available - check console for errors');
    }
}

// Debug function to check current field values
window.debugFieldValues = function() {
    const fields = ['SMTP_HOST', 'SMTP_USERNAME', 'FROM_EMAIL'];
    console.log('=== Debug Field Values ===');
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            const value = field.type === 'checkbox' ? field.checked : field.value;
            console.log(`${fieldId}: "${value}" (type: ${field.type}, required: ${field.hasAttribute('required')})`);
        } else {
            console.log(`${fieldId}: FIELD NOT FOUND`);
        }
    });
    console.log('=========================');
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - Initializing ConfigManager');
    initializeConfigManager();
});

// Check if ConfigManager is available globally
window.checkConfigManager = function() {
    console.log('ConfigManager check:', configManagerInstance);
    return configManagerInstance !== null;
};

// Backup initialization in case DOMContentLoaded already fired
if (document.readyState === 'loading') {
    console.log('Document still loading, waiting for DOMContentLoaded');
} else {
    console.log('Document already loaded, initializing immediately');
    setTimeout(initializeConfigManager, 100); // Small delay to ensure scripts are loaded
}
