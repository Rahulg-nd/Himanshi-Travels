// Logo Management JavaScript Module

class LogoManager {
    constructor() {
        this.selectedFile = null;
        this.initializeEventListeners();
        this.loadCurrentLogo();
    }

    initializeEventListeners() {
        const logoFileInput = document.getElementById('logo-file');
        if (logoFileInput) {
            logoFileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }

        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
            uploadArea.addEventListener('drop', this.handleDrop.bind(this));
            uploadArea.addEventListener('click', this.handleUploadClick.bind(this));
            uploadArea.addEventListener('keydown', this.handleUploadKeyDown.bind(this));
        }
    }

    handleUploadClick() {
        document.getElementById('logo-file').click();
    }

    handleUploadKeyDown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.handleUploadClick();
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        // Validate file type
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml'];
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('Invalid file type. Please select a PNG, JPG, JPEG, GIF, or SVG file.', 'error');
            return;
        }

        // Validate file size (5MB max)
        const maxSize = 5 * 1024 * 1024; // 5MB in bytes
        if (file.size > maxSize) {
            this.showNotification('File size too large. Please select a file smaller than 5MB.', 'error');
            return;
        }

        this.selectedFile = file;
        this.showPreview(file);
    }

    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewArea = document.getElementById('preview-area');
            const previewImg = document.getElementById('preview-img');
            const previewFilename = document.getElementById('preview-filename');
            const previewSize = document.getElementById('preview-size');
            const previewDimensions = document.getElementById('preview-dimensions');

            previewImg.src = e.target.result;
            previewFilename.textContent = file.name;
            previewSize.textContent = this.formatFileSize(file.size);

            // Get image dimensions
            previewImg.onload = () => {
                previewDimensions.textContent = `${previewImg.naturalWidth} × ${previewImg.naturalHeight}px`;
            };

            previewArea.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadLogo() {
        if (!this.selectedFile) {
            this.showNotification('No file selected', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('logo', this.selectedFile);

        try {
            this.showNotification('Uploading logo...', 'info');

            const response = await fetch('/api/config/upload_logo', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Logo uploaded successfully!', 'success');
                this.loadCurrentLogo();
                this.cancelUpload();
            } else {
                this.showNotification(`Upload failed: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Upload failed: ${error.message}`, 'error');
        }
    }

    cancelUpload() {
        this.selectedFile = null;
        document.getElementById('logo-file').value = '';
        document.getElementById('preview-area').style.display = 'none';
        document.getElementById('upload-area').classList.remove('dragover');
    }

    async loadCurrentLogo() {
        try {
            const response = await fetch('/api/config/logo');
            const result = await response.json();

            const currentLogoImg = document.getElementById('current-logo-img');
            const logoInfo = document.getElementById('logo-info');

            if (response.ok && result.logo_url) {
                currentLogoImg.src = result.logo_url + '?t=' + Date.now(); // Cache bust
                currentLogoImg.style.display = 'block';
                logoInfo.innerHTML = `
                    <p><strong>File:</strong> ${result.filename || 'Unknown'}</p>
                    <p><strong>Size:</strong> ${result.width || 'Auto'} × ${result.height || 'Auto'}px</p>
                `;
            } else {
                currentLogoImg.style.display = 'none';
                logoInfo.innerHTML = '<p>No logo uploaded</p>';
            }
        } catch (error) {
            console.error('Failed to load current logo:', error);
        }
    }

    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
        } else if (window.configManager && window.configManager.showNotification) {
            window.configManager.showNotification(message, type);
        } else {
            // Fallback notification
            console.log(`[${type.toUpperCase()}] ${message}`);
            alert(message);
        }
    }
}

// Global functions for template compatibility
function uploadLogo() {
    window.logoManager.uploadLogo();
}

function cancelUpload() {
    window.logoManager.cancelUpload();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.logoManager = new LogoManager();
});
