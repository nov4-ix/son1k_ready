/**
 * Son1kVers3 Service Worker
 * Progressive Web App functionality with offline support
 */

const CACHE_NAME = 'son1kvers3-v1.0.0';
const OFFLINE_CACHE = 'son1kvers3-offline-v1';

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  'https://cdn.tailwindcss.com',
  // Add more critical assets as needed
];

// API endpoints that should be cached
const API_CACHE_PATTERNS = [
  '/api/health',
  '/api/user/session',
  '/api/tracker/stats'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Son1kVers3 Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      }),
      // Force activation of new service worker
      self.skipWaiting()
    ])
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Son1kVers3 Service Worker activated');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Take control of all pages
      self.clients.claim()
    ])
  );
});

// Fetch event - network strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle different types of requests with appropriate strategies
  if (request.method === 'GET') {
    if (isStaticAsset(url)) {
      // Cache first for static assets
      event.respondWith(cacheFirst(request));
    } else if (isAPIRequest(url)) {
      // Network first for API requests
      event.respondWith(networkFirst(request));
    } else if (isAudioRequest(url)) {
      // Special handling for audio files
      event.respondWith(audioStreamHandler(request));
    } else {
      // Network first with cache fallback for other requests
      event.respondWith(networkFirst(request));
    }
  }
});

// Background sync for music generation
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'music-generation-retry') {
    event.waitUntil(retryFailedGenerations());
  }
});

// Push notifications for generation completion
self.addEventListener('push', (event) => {
  console.log('🔔 Push notification received');
  
  const data = event.data ? event.data.json() : {};
  
  const options = {
    body: data.message || '¡Tu música está lista!',
    icon: '/manifest-icon-192.png',
    badge: '/manifest-icon-96.png',
    tag: 'music-generation',
    data: data,
    actions: [
      {
        action: 'play',
        title: '▶️ Reproducir'
      },
      {
        action: 'download',
        title: '⬇️ Descargar'
      }
    ],
    vibrate: [200, 100, 200],
    requireInteraction: true
  };
  
  event.waitUntil(
    self.registration.showNotification('Son1kVers3', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('🖱️ Notification clicked:', event.action);
  
  event.notification.close();
  
  const action = event.action;
  const data = event.notification.data;
  
  if (action === 'play') {
    // Open app and play the track
    event.waitUntil(
      clients.openWindow(`/?play=${data.trackId}`)
    );
  } else if (action === 'download') {
    // Trigger download
    event.waitUntil(
      clients.openWindow(`/api/download/${data.trackId}`)
    );
  } else {
    // Default: open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Utility functions

function isStaticAsset(url) {
  const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.woff', '.woff2'];
  return staticExtensions.some(ext => url.pathname.endsWith(ext)) ||
         url.hostname === 'cdn.tailwindcss.com';
}

function isAPIRequest(url) {
  return url.pathname.startsWith('/api/');
}

function isAudioRequest(url) {
  const audioExtensions = ['.mp3', '.wav', '.m4a', '.aac'];
  return audioExtensions.some(ext => url.pathname.endsWith(ext));
}

async function cacheFirst(request) {
  try {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      // Refresh cache in background
      fetch(request).then(response => {
        if (response.ok) {
          cache.put(request, response.clone());
        }
      }).catch(() => {
        // Ignore network errors during background refresh
      });
      
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Cache first strategy failed:', error);
    return new Response('Offline content not available', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok && shouldCache(request)) {
      const cache = await caches.open(OFFLINE_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', request.url);
    
    const cache = await caches.open(OFFLINE_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for API requests
    if (isAPIRequest(new URL(request.url))) {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'Offline mode - feature not available',
          offline: true
        }),
        {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response('Content not available offline', { status: 503 });
  }
}

async function audioStreamHandler(request) {
  try {
    // First try network for fresh audio
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful audio requests
      const cache = await caches.open(OFFLINE_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network failed');
  } catch (error) {
    // Fall back to cached audio
    const cache = await caches.open(OFFLINE_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response('Audio not available offline', { status: 503 });
  }
}

function shouldCache(request) {
  const url = new URL(request.url);
  
  // Cache API responses that are safe to cache
  const cachableAPI = API_CACHE_PATTERNS.some(pattern => 
    url.pathname.includes(pattern)
  );
  
  return cachableAPI || isStaticAsset(url);
}

async function retryFailedGenerations() {
  try {
    // Get failed generations from IndexedDB
    const failedGenerations = await getFailedGenerations();
    
    for (const generation of failedGenerations) {
      try {
        const response = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(generation.data)
        });
        
        if (response.ok) {
          // Remove from failed queue
          await removeFailedGeneration(generation.id);
          
          // Notify user
          const data = await response.json();
          self.registration.showNotification('Son1kVers3', {
            body: '¡Generación completada desde segundo plano!',
            icon: '/manifest-icon-192.png',
            data: { trackId: data.tracks?.[0]?.id }
          });
        }
      } catch (error) {
        console.error('Failed to retry generation:', error);
      }
    }
  } catch (error) {
    console.error('Background sync error:', error);
  }
}

// IndexedDB helpers for background sync
async function getFailedGenerations() {
  return new Promise((resolve) => {
    // Mock implementation - replace with actual IndexedDB
    resolve([]);
  });
}

async function removeFailedGeneration(id) {
  return new Promise((resolve) => {
    // Mock implementation - replace with actual IndexedDB
    resolve();
  });
}

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'CACHE_AUDIO':
      cacheAudio(data.url);
      break;
      
    case 'CLEAR_CACHE':
      clearAllCaches();
      break;
      
    default:
      console.log('Unknown message type:', type);
  }
});

async function cacheAudio(url) {
  try {
    const cache = await caches.open(OFFLINE_CACHE);
    await cache.add(url);
    console.log('✅ Audio cached:', url);
  } catch (error) {
    console.error('Failed to cache audio:', error);
  }
}

async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
  console.log('🗑️ All caches cleared');
}

console.log('🎵 Son1kVers3 Service Worker loaded successfully');