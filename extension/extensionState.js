// Extension State Management
console.log('📊 Extension state loaded');

// Global extension state manager
window.extensionState = {
    // Current state
    connected: false,
    apiUrl: 'https://2a73bb633652.ngrok-free.app',
    userEmail: 'soypepejaimes@gmail.com',
    lastPing: null,
    errors: [],
    
    // State methods
    updateConnection: (status) => {
        window.extensionState.connected = status;
        window.extensionState.lastPing = Date.now();
        console.log(`🔄 Connection status updated: ${status}`);
    },
    
    addError: (error) => {
        window.extensionState.errors.push({
            timestamp: Date.now(),
            message: error
        });
        console.error(`❌ Extension error: ${error}`);
    },
    
    clearErrors: () => {
        window.extensionState.errors = [];
        console.log('🧹 Errors cleared');
    },
    
    getStatus: () => {
        return {
            connected: window.extensionState.connected,
            apiUrl: window.extensionState.apiUrl,
            userEmail: window.extensionState.userEmail,
            lastPing: window.extensionState.lastPing,
            errorCount: window.extensionState.errors.length
        };
    }
};