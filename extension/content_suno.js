// Content Script for Suno.com Integration
console.log('🎵 Son1k-Suno Bridge Content Script Loaded');

let son1kConfig = {
    apiUrl: 'https://2a73bb633652.ngrok-free.app',
    userEmail: 'soypepejaimes@gmail.com',
    connected: false
};

// Initialize when page loads
function initializeSunoBridge() {
    console.log('🔗 Initializing Suno-Son1k Bridge...');
    
    // Load config from storage
    chrome.storage.sync.get(['apiUrl', 'connected'], (result) => {
        if (result.apiUrl) {
            son1kConfig.apiUrl = result.apiUrl;
            son1kConfig.connected = result.connected || false;
        }
        
        console.log('📡 Son1k Config:', son1kConfig);
        
        if (son1kConfig.connected) {
            addSon1kButton();
            monitorSunoForms();
        }
    });
}

// Add Son1k button to Suno interface
function addSon1kButton() {
    console.log('🔘 Adding Son1k button to Suno interface...');
    
    // Wait for Suno interface to load
    const checkForSunoInterface = setInterval(() => {
        const sunoContainer = document.querySelector('[data-testid="create-form"], .create-form, form, .generation-form') ||
                             document.querySelector('textarea, input[type="text"]')?.closest('form, div') ||
                             document.querySelector('button[type="submit"], button:contains("Create"), button:contains("Generate")')?.parentElement;
        
        if (sunoContainer && !document.getElementById('son1k-bridge-btn')) {
            clearInterval(checkForSunoInterface);
            
            // Create Son1k button
            const son1kButton = document.createElement('button');
            son1kButton.id = 'son1k-bridge-btn';
            son1kButton.textContent = '🎵 Send to Son1k';
            son1kButton.style.cssText = `
                background: #00FFE7;
                color: #000;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                margin: 10px;
                font-size: 14px;
                z-index: 9999;
                position: relative;
            `;
            
            son1kButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                captureSunoData();
            });
            
            // Insert button
            sunoContainer.appendChild(son1kButton);
            console.log('✅ Son1k button added to Suno interface');
            
            // Update extension status
            chrome.runtime.sendMessage({
                type: 'SUNO_INTEGRATION_READY',
                data: { ready: true, userEmail: son1kConfig.userEmail }
            });
        }
    }, 1000);
    
    // Stop checking after 30 seconds
    setTimeout(() => clearInterval(checkForSunoInterface), 30000);
}

// Capture data from Suno forms
function captureSunoData() {
    console.log('📝 Capturing Suno data...');
    
    const sunoData = {
        prompt: '',
        lyrics: '',
        mode: 'original',
        userEmail: son1kConfig.userEmail,
        timestamp: new Date().toISOString(),
        source: 'suno.com'
    };
    
    // Try different selectors for prompt
    const promptSelectors = [
        'textarea[placeholder*="Describe"]',
        'textarea[placeholder*="prompt"]',
        'textarea[placeholder*="Song description"]',
        '[data-testid="prompt-input"]',
        'input[placeholder*="Describe"]'
    ];
    
    for (const selector of promptSelectors) {
        const promptElement = document.querySelector(selector);
        if (promptElement && promptElement.value) {
            sunoData.prompt = promptElement.value;
            break;
        }
    }
    
    // Try different selectors for lyrics
    const lyricsSelectors = [
        'textarea[placeholder*="lyrics"]',
        'textarea[placeholder*="Lyrics"]',
        'textarea[placeholder*="Custom lyrics"]',
        '[data-testid="lyrics-input"]'
    ];
    
    for (const selector of lyricsSelectors) {
        const lyricsElement = document.querySelector(selector);
        if (lyricsElement && lyricsElement.value) {
            sunoData.lyrics = lyricsElement.value;
            break;
        }
    }
    
    // Check if instrumental mode
    const instrumentalToggle = document.querySelector('input[type="checkbox"][data-testid="instrumental"], input[type="checkbox"]:checked');
    if (instrumentalToggle && instrumentalToggle.checked) {
        sunoData.mode = 'instrumental';
    }
    
    console.log('📦 Captured Suno data:', sunoData);
    
    if (sunoData.prompt || sunoData.lyrics) {
        sendToSon1k(sunoData);
    } else {
        showNotification('❌ No data found to send', 'error');
    }
}

// Send data to Son1k backend
function sendToSon1k(data) {
    console.log('🚀 Sending to Son1k backend...');
    
    showNotification('📤 Sending to Son1k...', 'info');
    
    fetch(son1kConfig.apiUrl + '/api/songs/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'any'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(result => {
        console.log('✅ Successfully sent to Son1k:', result);
        showNotification('✅ Sent to Son1k successfully!', 'success');
        
        // Notify background script
        chrome.runtime.sendMessage({
            type: 'SUNO_DATA_SENT',
            data: { success: true, result: result }
        });
    })
    .catch(error => {
        console.error('❌ Error sending to Son1k:', error);
        showNotification('❌ Error sending to Son1k: ' + error.message, 'error');
    });
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#f59e0b'};
        color: ${type === 'error' ? '#fff' : '#000'};
        padding: 12px 20px;
        border-radius: 6px;
        font-weight: bold;
        z-index: 99999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 4000);
}

// Monitor for form changes
function monitorSunoForms() {
    const observer = new MutationObserver(() => {
        if (!document.getElementById('son1k-bridge-btn')) {
            addSon1kButton();
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Listen for messages from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('📨 Content script received message:', message.type);
    
    switch (message.type) {
        case 'UPDATE_CONFIG':
            son1kConfig = { ...son1kConfig, ...message.config };
            if (son1kConfig.connected) {
                addSon1kButton();
                monitorSunoForms();
            }
            sendResponse({ success: true });
            break;
            
        case 'CAPTURE_SUNO_DATA':
            captureSunoData();
            sendResponse({ success: true });
            break;
    }
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSunoBridge);
} else {
    initializeSunoBridge();
}

// Also initialize after a delay for dynamic content
setTimeout(initializeSunoBridge, 2000);