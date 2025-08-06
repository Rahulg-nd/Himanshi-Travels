/**
 * AutoComplete Component
 * Enhanced autocomplete functionality for cities and countries
 */

class AutoComplete {
    constructor(inputId, suggestionsId, apiEndpoint, options = {}) {
        this.inputId = inputId;
        this.suggestionsId = suggestionsId;
        this.input = document.getElementById(inputId);
        this.apiEndpoint = apiEndpoint;
        this.options = options;
        this.selectedIndex = -1;
        this.currentSuggestions = [];
        this.debounceTimer = null;
        
        this.init();
    }
    
    init() {
        if (!this.input) {
            console.warn(`AutoComplete: Input element not found: ${this.inputId}`);
            return;
        }
        
        console.log(`AutoComplete: Initializing for input ${this.inputId}`);
        
        // Find or create suggestions container
        this.suggestionsContainer = document.getElementById(this.suggestionsId);
        if (!this.suggestionsContainer) {
            console.log(`AutoComplete: Suggestions container not found, creating one for: ${this.inputId}`);
            this.suggestionsContainer = document.createElement('div');
            this.suggestionsContainer.id = this.suggestionsId;
            this.suggestionsContainer.className = 'autocomplete-suggestions';
            
            // Find the autocomplete container or use the input's parent
            let container = this.input.closest('.autocomplete-container');
            if (!container) {
                console.log(`AutoComplete: No autocomplete-container found for ${this.inputId}, using parent`);
                container = this.input.parentNode;
            }
            container.appendChild(this.suggestionsContainer);
        } else {
            console.log(`AutoComplete: Found existing suggestions container for ${this.inputId}`);
        }
        
        this.bindEvents();
        console.log(`AutoComplete: Successfully initialized for ${this.inputId}`);
    }
    
    bindEvents() {
        // Input event with debouncing
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.handleInput(e.target.value);
            }, 300);
        });
        
        // Keyboard navigation
        this.input.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
        
        // Hide suggestions when input loses focus
        this.input.addEventListener('blur', (e) => {
            // Delay hiding to allow for click on suggestions
            setTimeout(() => {
                if (!this.suggestionsContainer.contains(document.activeElement)) {
                    this.hideSuggestions();
                }
            }, 200);
        });
    }
    
    async handleInput(value) {
        console.log(`AutoComplete input: ${value} for ${this.inputId}`);
        
        if (value.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        try {
            const url = this.buildApiUrl(value);
            console.log(`Fetching: ${url}`);
            
            const response = await fetch(url);
            const data = await response.json();
            
            console.log('API Response:', data);
            
            if (data.suggestions && Array.isArray(data.suggestions) && data.suggestions.length > 0) {
                this.showSuggestions(data.suggestions);
            } else {
                console.log('No suggestions found or empty response');
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('AutoComplete API error:', error);
            this.hideSuggestions();
        }
    }
    
    buildApiUrl(query) {
        let url = `${this.apiEndpoint}?q=${encodeURIComponent(query)}`;
        
        // Add country filter if specified
        if (this.options.countryFilter) {
            const countryInput = document.getElementById(this.options.countryFilter);
            if (countryInput && countryInput.value) {
                url += `&country=${encodeURIComponent(countryInput.value)}`;
            }
        }
        
        return url;
    }
    
    showSuggestions(suggestions) {
        this.currentSuggestions = suggestions;
        this.selectedIndex = -1;
        
        this.suggestionsContainer.innerHTML = '';
        
        suggestions.forEach((suggestion, index) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-suggestion';
            div.innerHTML = this.formatSuggestion(suggestion);
            
            div.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });
            
            this.suggestionsContainer.appendChild(div);
        });
        
        this.suggestionsContainer.style.display = 'block';
    }
    
    formatSuggestion(suggestion) {
        if (this.apiEndpoint.includes('countries')) {
            // Format country suggestions
            const popular = suggestion.popular ? '<span class="suggestion-type">Popular</span>' : '';
            return `
                <div class="suggestion-main">${suggestion.name}</div>
                <div class="suggestion-detail">${suggestion.code}${popular}</div>
            `;
        } else {
            // Format city suggestions - show state/region if available
            return `
                <div class="suggestion-main">${suggestion.name}</div>
                <div class="suggestion-detail">${suggestion.region || ''}${suggestion.region ? ', ' : ''}${suggestion.country}</div>
            `;
        }
    }
    
    selectSuggestion(suggestion) {
        this.input.value = suggestion.name;
        this.hideSuggestions();
        
        // Trigger change event for any listeners
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // If this is a country field, trigger city field update
        if (this.apiEndpoint.includes('countries')) {
            this.triggerCityUpdate();
        }
    }
    
    triggerCityUpdate() {
        // Find associated city field and trigger its autocomplete
        const inputId = this.input.id;
        let cityFieldId = '';
        
        if (inputId === 'hotel_country') {
            cityFieldId = 'hotel_city';
        } else if (inputId === 'from_country') {
            cityFieldId = 'from_journey';
        } else if (inputId === 'to_country') {
            cityFieldId = 'to_journey';
        }
        
        if (cityFieldId) {
            const cityField = document.getElementById(cityFieldId);
            if (cityField && cityField.value) {
                // Trigger re-search with country filter
                const event = new Event('input', { bubbles: true });
                cityField.dispatchEvent(event);
            }
        }
    }
    
    handleKeydown(e) {
        if (!this.currentSuggestions.length) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.currentSuggestions.length - 1);
                this.highlightSuggestion();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.highlightSuggestion();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectSuggestion(this.currentSuggestions[this.selectedIndex]);
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }
    
    highlightSuggestion() {
        const suggestions = this.suggestionsContainer.querySelectorAll('.autocomplete-suggestion');
        
        suggestions.forEach((suggestion, index) => {
            if (index === this.selectedIndex) {
                suggestion.classList.add('selected');
            } else {
                suggestion.classList.remove('selected');
            }
        });
    }
    
    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
        this.selectedIndex = -1;
        this.currentSuggestions = [];
    }
}

/**
 * Initialize autocomplete instances for all relevant fields
 */
function initializeAutoComplete() {
    console.log('Initializing AutoComplete...');
    
    // Store autocomplete instances
    window.autocompleteInstances = window.autocompleteInstances || [];
    
    // Clear existing instances
    window.autocompleteInstances = [];
    
    // Debug: List all available input fields
    const allInputs = document.querySelectorAll('input[type="text"]');
    console.log('Available text inputs:', Array.from(allInputs).map(input => input.id).filter(id => id));
    
    // Always available fields (customer info, etc.)
    
    // Initialize autocomplete for all visible fields
    const fieldsToInitialize = [
        { id: 'hotel_city', suggestions: 'hotel_city_suggestions', endpoint: '/api/cities', options: { countryFilter: 'hotel_country' } },
        { id: 'hotel_country', suggestions: 'hotel_country_suggestions', endpoint: '/api/countries' },
        { id: 'from_journey', suggestions: 'from_journey_suggestions', endpoint: '/api/cities', options: { countryFilter: 'from_country' } },
        { id: 'from_country', suggestions: 'from_country_suggestions', endpoint: '/api/countries' },
        { id: 'to_journey', suggestions: 'to_journey_suggestions', endpoint: '/api/cities', options: { countryFilter: 'to_country' } },
        { id: 'to_country', suggestions: 'to_country_suggestions', endpoint: '/api/countries' }
    ];
    
    fieldsToInitialize.forEach(field => {
        const element = document.getElementById(field.id);
        if (element) {
            // Check if element is visible (not in a hidden conditional field)
            const isVisible = element.offsetParent !== null || element.style.display !== 'none';
            
            if (isVisible || element.closest('.conditional-fields.active')) {
                console.log(`Initializing autocomplete for ${field.id}`);
                window.autocompleteInstances.push(new AutoComplete(field.id, field.suggestions, field.endpoint, field.options || {}));
            } else {
                console.log(`Skipping ${field.id} - not visible yet`);
            }
        } else {
            console.log(`Field ${field.id} not found in DOM`);
        }
    });
    
    console.log(`Initialized ${window.autocompleteInstances.length} autocomplete instances`);
}

/**
 * Re-initialize autocomplete when conditional fields become visible
 */
function reinitializeAutoCompleteForVisibleFields() {
    console.log('Reinitializing AutoComplete for visible fields...');
    
    // Wait a bit for the fields to be fully rendered and visible
    setTimeout(() => {
        // Clear existing instances for fields that might have been hidden
        if (window.autocompleteInstances) {
            window.autocompleteInstances.forEach(instance => {
                if (instance.input && instance.input.offsetParent === null) {
                    console.log(`Removing autocomplete instance for hidden field: ${instance.inputId}`);
                }
            });
        }
        
        // Reinitialize all autocomplete
        initializeAutoComplete();
    }, 100);
}

/**
 * Test function to verify autocomplete is working
 */
function testAutoComplete() {
    console.log('Testing AutoComplete...');
    
    // Check if functions exist
    console.log('initializeAutoComplete function exists:', typeof initializeAutoComplete);
    console.log('reinitializeAutoCompleteForVisibleFields function exists:', typeof reinitializeAutoCompleteForVisibleFields);
    
    // Check instances
    console.log('Current autocomplete instances:', window.autocompleteInstances?.length || 0);
    
    // Test API directly
    fetch('/api/cities?q=new&limit=1')
        .then(response => response.json())
        .then(data => {
            console.log('API test successful:', data);
        })
        .catch(error => {
            console.error('API test failed:', error);
        });
    
    // Check for form elements
    const testFields = ['hotel_city', 'from_journey', 'to_journey'];
    testFields.forEach(fieldId => {
        const element = document.getElementById(fieldId);
        console.log(`Field ${fieldId}:`, {
            exists: !!element,
            visible: element ? element.offsetParent !== null : false,
            container: element ? element.closest('.conditional-fields')?.classList.contains('active') : false
        });
    });
}

// Make it available globally for testing
window.testAutoComplete = testAutoComplete;
