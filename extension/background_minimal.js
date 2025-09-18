// Minimal background worker for Son1k
console.log('Son1k Minimal Background Worker Started');

let apiUrl = 'https://2a73bb633652.ngrok-free.app';

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received:', message.type);
  
  switch (message.type) {
    case 'UPDATE_API_URL':
      apiUrl = message.apiUrl;
      sendResponse({ success: true, apiUrl: apiUrl });
      break;
      
    case 'GET_STATUS':
      sendResponse({ 
        connected: true, 
        apiUrl: apiUrl,
        status: 'online'
      });
      break;
      
    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }
});