// Extension Utilities
console.log('📦 Extension utils loaded');

// Utility functions for Son1k Extension
window.extensionUtils = {
    // Generate unique ID
    generateId: () => {
        return 'ext_' + Math.random().toString(36).substr(2, 9);
    },
    
    // Format timestamp
    formatTime: (timestamp) => {
        return new Date(timestamp).toLocaleTimeString();
    },
    
    // Log with timestamp
    log: (message, type = 'info') => {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] [Son1k] ${message}`);
    },
    
    // API configuration
    apiConfig: {
        baseUrl: 'https://2a73bb633652.ngrok-free.app',
        timeout: 10000,
        headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'any'
        }
    }
};