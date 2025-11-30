// Service Worker for HireMeBahamas PWA
const CACHE_NAME = 'hiremebahamas-v2';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/pwa-192x192.png',
  '/pwa-512x512.png',
  '/sounds/notification.mp3'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        // Use addAll with catch to handle missing files gracefully
        return cache.addAll(urlsToCache).catch((error) => {
          console.warn('Some cache files may not have been cached:', error);
          // Still proceed with what we can cache
          return Promise.allSettled(
            urlsToCache.map(url => 
              cache.add(url).catch(e => console.warn(`Failed to cache ${url}:`, e))
            )
          );
        });
      })
      .catch((error) => {
        console.error('Cache install failed:', error);
      })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        return fetch(event.request).then(
          (response) => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
      .catch(() => {
        // Return offline page if available
        return caches.match('/offline.html');
      })
  );
});

// Push notification event - handles incoming push messages
self.addEventListener('push', (event) => {
  let notificationData = {
    title: 'HireMeBahamas',
    body: 'You have a new notification',
    icon: '/pwa-192x192.png',
    badge: '/pwa-192x192.png',
    tag: 'default',
    data: {
      url: '/'
    }
  };

  // Try to parse push data
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        title: data.title || 'HireMeBahamas',
        body: data.body || data.message || 'You have a new notification',
        icon: data.icon || '/pwa-192x192.png',
        badge: data.badge || '/pwa-192x192.png',
        tag: data.tag || 'message-' + Date.now(),
        data: {
          url: data.url || data.click_action || '/messages',
          messageId: data.messageId,
          conversationId: data.conversationId,
          senderId: data.senderId
        }
      };
    } catch {
      // Use text data if JSON parsing fails
      notificationData.body = event.data.text() || 'You have a new notification';
    }
  }

  const options = {
    body: notificationData.body,
    icon: notificationData.icon,
    badge: notificationData.badge,
    tag: notificationData.tag,
    vibrate: [200, 100, 200],
    renotify: true,
    requireInteraction: false,
    data: notificationData.data,
    actions: [
      {
        action: 'view',
        title: 'View Message'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Notification click event - handles user clicking on notification
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  // Handle action buttons
  if (event.action === 'dismiss') {
    return;
  }

  // Get the URL to open (from notification data or default to messages)
  const urlToOpen = event.notification.data?.url || '/messages';
  // Create full URL
  const fullUrl = new URL(urlToOpen, self.location.origin).href;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Check if there is already a window/tab open with the app
        for (let i = 0; i < windowClients.length; i++) {
          const client = windowClients[i];
          // If so, focus it and send a message to navigate
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.focus();
            // Use postMessage to tell the client to navigate
            // The client should listen for this message and use React Router
            client.postMessage({
              type: 'NOTIFICATION_CLICK',
              url: urlToOpen
            });
            return client;
          }
        }
        // If not, open a new window/tab with the full URL
        if (clients.openWindow) {
          return clients.openWindow(fullUrl);
        }
      })
  );
});

// Handle notification close event
self.addEventListener('notificationclose', (event) => {
  console.log('Notification closed:', event.notification.tag);
});

// Background sync event
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  } else if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

// Sync messages in background
async function syncMessages() {
  console.log('Background sync: syncing messages');
  // This would be implemented to sync pending messages
  // when network connectivity is restored
}

async function syncData() {
  // Implement your sync logic here
  console.log('Background sync triggered');
}

// Handle message from main thread (for custom notifications)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SHOW_NOTIFICATION') {
    const { title, options } = event.data;
    self.registration.showNotification(title, {
      ...options,
      icon: options.icon || '/pwa-192x192.png',
      badge: options.badge || '/pwa-192x192.png',
    });
  }
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

