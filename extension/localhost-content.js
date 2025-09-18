// localhost-content.js - Handles communication with Son1k frontend
(() => {
  // Listen for backend ping and respond
  window.addEventListener('message', (event) => {
    // Only respond to messages from the same origin (localhost:8000)
    if (event.origin !== window.location.origin) {
      return;
    }
    
    if (event.data.type === 'BACKEND_PING') {
      // Respond immediately that extension is present
      window.postMessage({ type: 'EXTENSION_PING' }, '*');
      console.log('[Son1k Extension] Responded to backend ping');
    }
  });

  // Send initial ping to notify frontend that extension is loaded
  const sendInitialPing = () => {
    window.postMessage({ type: 'EXTENSION_PING' }, '*');
    console.log('[Son1k Extension] Sent initial ping to frontend');
  };

  // Send ping immediately and periodically
  sendInitialPing();
  
  // Send periodic pings to maintain connection status
  setInterval(() => {
    window.postMessage({ type: 'EXTENSION_PING' }, '*');
  }, 30000); // Every 30 seconds

  console.log('[Son1k Extension] Localhost content script loaded');
})();