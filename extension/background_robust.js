// Robust Service Worker for Son1k Extension
console.log('🚀 Son1k Service Worker Starting...');

let extensionConfig = {
    apiUrl: 'http://localhost:8000',
    connected: false,
    lastPing: null,
    userEmail: 'soypepejaimes@gmail.com'
};

// Initialize extension on startup
chrome.runtime.onStartup.addListener(() => {
    console.log('🔄 Extension startup - initializing config');
    initializeExtension();
});

chrome.runtime.onInstalled.addListener(() => {
    console.log('📦 Extension installed - setting up configuration');
    initializeExtension();
});

// Initialize extension configuration
async function initializeExtension() {
    try {
        // Load saved config
        const stored = await chrome.storage.sync.get(['apiUrl', 'connected', 'userEmail']);
        
        if (stored.apiUrl) {
            extensionConfig = { ...extensionConfig, ...stored };
        } else {
            // Set default config
            await chrome.storage.sync.set(extensionConfig);
        }
        
        console.log('⚙️ Extension config loaded:', extensionConfig);
        
        // Test initial connection
        await testApiConnection();
        
    } catch (error) {
        console.error('❌ Error initializing extension:', error);
    }
}

// Test API connection with robust error handling
async function testApiConnection() {
    console.log('🔍 Testing API connection...');
    
    try {
        const response = await fetch(extensionConfig.apiUrl + '/api/health', {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': 'any',
                'Content-Type': 'application/json'
            },
            signal: AbortSignal.timeout(10000) // 10 second timeout
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.ok) {
                extensionConfig.connected = true;
                extensionConfig.lastPing = Date.now();
                
                await chrome.storage.sync.set({
                    connected: true,
                    lastPing: extensionConfig.lastPing
                });
                
                console.log('✅ API connection successful');
                notifyConnectionStatus(true, 'Connected to Son1k backend');
                
                // Notify frontend about extension status
                notifyFrontendConnection();
                
                return true;
            }
        }
        
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        
    } catch (error) {
        console.error('❌ API connection failed:', error.message);
        
        extensionConfig.connected = false;
        await chrome.storage.sync.set({ connected: false });
        
        notifyConnectionStatus(false, 'Connection failed: ' + error.message);
        return false;
    }
}

// Notify frontend about extension connection status
async function notifyFrontendConnection() {
    try {
        // Find Son1k frontend tabs
        const tabs = await chrome.tabs.query({
            url: [
                extensionConfig.apiUrl + "/*",
                "https://2a73bb633652.ngrok-free.app/*"
            ]
        });
        
        if (tabs.length > 0) {
            for (const tab of tabs) {
                try {
                    await chrome.tabs.sendMessage(tab.id, {
                        type: 'EXTENSION_CONNECTED',
                        config: extensionConfig,
                        timestamp: Date.now()
                    });
                    console.log('📡 Notified frontend tab about extension connection');
                } catch (error) {
                    // Content script might not be loaded yet
                    console.log('📝 Frontend tab not ready for messages yet');
                }
            }
        }
        
        // Also inject connection info into frontend tabs
        for (const tab of tabs) {
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        localStorage.setItem('son1k_extension_connected', 'true');
                        localStorage.setItem('son1k_extension_timestamp', Date.now().toString());
                        
                        // Add extension indicator to DOM
                        if (!document.querySelector('[data-son1k-extension]')) {
                            const indicator = document.createElement('div');
                            indicator.setAttribute('data-son1k-extension', 'connected');
                            indicator.style.display = 'none';
                            document.body.appendChild(indicator);
                        }
                        
                        // Trigger frontend status check
                        if (window.checkSystemStatus) {
                            window.checkSystemStatus();
                        }
                    }
                });
                console.log('💉 Injected extension status into frontend');
            } catch (error) {
                console.log('⚠️ Could not inject into tab:', error.message);
            }
        }
        
    } catch (error) {
        console.error('❌ Error notifying frontend:', error);
    }
}

// Notify popup about connection status
function notifyConnectionStatus(connected, message) {
    // Try to send message to popup if it's open
    chrome.runtime.sendMessage({
        type: 'CONNECTION_STATUS',
        connected: connected,
        message: message,
        timestamp: Date.now()
    }).catch(() => {
        // Popup not open - this is expected behavior
    });
}

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('📨 Service Worker received message:', message.type);
    
    switch (message.type) {
        case 'GET_CONFIG':
            sendResponse({
                success: true,
                config: extensionConfig
            });
            break;
            
        case 'UPDATE_API_URL':
            updateApiUrl(message.apiUrl)
                .then(() => sendResponse({ success: true }))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true; // Keep message channel open for async response
            
        case 'TEST_CONNECTION':
            testApiConnection()
                .then(result => sendResponse({ success: result }))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true; // Keep message channel open for async response
            
        case 'PING_API':
            pingApi()
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true; // Keep message channel open for async response
            
        case 'EXTENSION_CONFIGURED':
            extensionConfig = { ...extensionConfig, ...message.config };
            console.log('⚙️ Extension configured via popup:', extensionConfig);
            sendResponse({ success: true });
            break;
            
        case 'SUNO_INTEGRATION_READY':
            console.log('🎵 Suno integration ready:', message.data);
            sendResponse({ success: true });
            break;
            
        case 'SUNO_DATA_SENT':
            console.log('📤 Suno data sent successfully:', message.data);
            sendResponse({ success: true });
            break;
            
        default:
            console.log('❓ Unknown message type:', message.type);
            sendResponse({ success: false, error: 'Unknown message type' });
    }
});

// Update API URL and test connection
async function updateApiUrl(newUrl) {
    extensionConfig.apiUrl = newUrl;
    await chrome.storage.sync.set({ apiUrl: newUrl });
    
    console.log('🔄 API URL updated to:', newUrl);
    return await testApiConnection();
}

// Ping API endpoint with detailed response
async function pingApi() {
    console.log('🏓 Pinging API...');
    
    try {
        const startTime = performance.now();
        
        const response = await fetch(extensionConfig.apiUrl + '/api/health', {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': 'any',
                'Content-Type': 'application/json'
            },
            signal: AbortSignal.timeout(5000)
        });
        
        const endTime = performance.now();
        const responseTime = Math.round(endTime - startTime);
        
        if (response.ok) {
            const data = await response.json();
            
            return {
                success: true,
                status: response.status,
                responseTime: responseTime,
                data: data,
                message: `API responding in ${responseTime}ms`
            };
        } else {
            return {
                success: false,
                status: response.status,
                responseTime: responseTime,
                message: `HTTP ${response.status}: ${response.statusText}`
            };
        }
        
    } catch (error) {
        return {
            success: false,
            message: 'Ping failed: ' + error.message,
            error: error.name
        };
    }
}

// Periodic health check (every 30 seconds when extension is active)
setInterval(async () => {
    if (extensionConfig.connected) {
        await testApiConnection();
    }
}, 30000);

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    console.log('🖱️ Extension icon clicked');
    // The popup will handle this - this is just for logging
});

console.log('✅ Son1k Service Worker initialized');