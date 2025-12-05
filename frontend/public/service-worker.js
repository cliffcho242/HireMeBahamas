// Service Worker for HireMeBahamas PWA
// =======================================
// ADDICTIVE FEATURES:
// - Instant push notifications (VAPID)
// - Background sync for offline actions
// - Sound notifications
// - Badge updates
// =======================================

const CACHE_NAME = 'hiremebahamas-v3';
const STATIC_CACHE = 'hiremebahamas-static-v3';
const DYNAMIC_CACHE = 'hiremebahamas-dynamic-v3';

// Required files that must be cached
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/pwa-192x192.png',
  '/pwa-512x512.png',
  '/offline.html'
];

// Optional files that are nice to have but not required
const optionalUrlsToCache = [
  '/sounds/notification.mp3'
];

// =======================================
// INSTALL EVENT - Cache resources
// =======================================
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async (cache) => {
        console.log('[SW] Caching app shell');
        
        // Cache required files - these must succeed
        try {
          await cache.addAll(urlsToCache);
          console.log('[SW] Required files cached successfully');
        } catch (error) {
          console.error('[SW] Failed to cache required files:', error);
          throw error; // Fail installation if required files can't be cached
        }
        
        // Cache optional files - failures are OK
        const optionalResults = await Promise.allSettled(
          optionalUrlsToCache.map(url => 
            cache.add(url)
              .then(() => console.log(`[SW] Cached optional file: ${url}`))
              .catch(e => console.warn(`[SW] Failed to cache optional file ${url}:`, e.message))
          )
        );
        
        const successCount = optionalResults.filter(r => r.status === 'fulfilled').length;
        console.log(`[SW] Cached ${successCount}/${optionalUrlsToCache.length} optional files`);
      })
      .catch((error) => {
        console.error('[SW] Cache install failed:', error);
        throw error;
      })
  );
  // Skip waiting - activate immediately
  self.skipWaiting();
});

// =======================================
// ACTIVATE EVENT - Clean up old caches
// =======================================
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...');
  const cacheWhitelist = [CACHE_NAME, STATIC_CACHE, DYNAMIC_CACHE];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Claim all clients immediately
  self.clients.claim();
});

// =======================================
// FETCH EVENT - Network-first with cache fallback
// =======================================
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip API requests (handled by workbox)
  if (event.request.url.includes('/api/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }

        return fetch(event.request).then(
          (response) => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();

            caches.open(DYNAMIC_CACHE)
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

// =======================================
// PUSH NOTIFICATION EVENT - Instant delivery
// =======================================
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
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

  // Parse push data
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        title: data.title || 'HireMeBahamas',
        body: data.body || data.message || 'You have a new notification',
        icon: data.icon || '/pwa-192x192.png',
        badge: data.badge || '/pwa-192x192.png',
        tag: data.tag || `notification-${Date.now()}`,
        image: data.image,
        data: {
          url: data.url || data.click_action || '/messages',
          messageId: data.messageId,
          conversationId: data.conversationId,
          senderId: data.senderId,
          type: data.type
        }
      };
    } catch {
      notificationData.body = event.data.text() || 'You have a new notification';
    }
  }

  const options = {
    body: notificationData.body,
    icon: notificationData.icon,
    badge: notificationData.badge,
    tag: notificationData.tag,
    image: notificationData.image,
    vibrate: [200, 100, 200, 100, 200],
    renotify: true,
    requireInteraction: false,
    silent: false,
    data: notificationData.data,
    actions: [
      {
        action: 'view',
        title: 'View',
        icon: '/pwa-192x192.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  event.waitUntil(
    Promise.all([
      self.registration.showNotification(notificationData.title, options),
      // Update badge count
      updateBadgeCount(1)
    ])
  );
});

// =======================================
// NOTIFICATION CLICK - Navigate to content
// =======================================
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.action);
  event.notification.close();

  if (event.action === 'dismiss') {
    return;
  }

  const urlToOpen = event.notification.data?.url || '/messages';
  const fullUrl = new URL(urlToOpen, self.location.origin).href;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Focus existing window if found
        for (let i = 0; i < windowClients.length; i++) {
          const client = windowClients[i];
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.focus();
            client.postMessage({
              type: 'NOTIFICATION_CLICK',
              url: urlToOpen,
              data: event.notification.data
            });
            return client;
          }
        }
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(fullUrl);
        }
      })
  );
});

// =======================================
// NOTIFICATION CLOSE
// =======================================
self.addEventListener('notificationclose', (event) => {
  console.log('[SW] Notification closed:', event.notification.tag);
});

// =======================================
// BACKGROUND SYNC - Queue offline actions
// =======================================
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  } else if (event.tag === 'sync-posts') {
    event.waitUntil(syncPosts());
  } else if (event.tag === 'sync-likes') {
    event.waitUntil(syncLikes());
  } else if (event.tag === 'api-queue') {
    event.waitUntil(syncApiQueue());
  } else if (event.tag === 'messages-queue') {
    event.waitUntil(syncMessagesQueue());
  }
});

// Sync pending messages from IndexedDB
async function syncMessages() {
  console.log('[SW] Syncing pending messages...');
  try {
    const db = await openDB();
    const pendingMessages = await getAllFromStore(db, 'pending-messages');
    
    for (const msg of pendingMessages) {
      try {
        const response = await fetch('/api/messages/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(msg.data)
        });
        
        if (response.ok) {
          await deleteFromStore(db, 'pending-messages', msg.id);
          console.log('[SW] Message synced:', msg.id);
        }
      } catch (error) {
        console.error('[SW] Failed to sync message:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Sync messages failed:', error);
  }
}

// Sync pending posts
async function syncPosts() {
  console.log('[SW] Syncing pending posts...');
}

// Sync pending likes
async function syncLikes() {
  console.log('[SW] Syncing pending likes...');
}

// Sync API queue
async function syncApiQueue() {
  console.log('[SW] Syncing API queue...');
}

// Sync messages queue
async function syncMessagesQueue() {
  console.log('[SW] Syncing messages queue...');
}

// =======================================
// BADGE API - Update app badge
// =======================================
async function updateBadgeCount(count) {
  if ('setAppBadge' in navigator) {
    try {
      if (count > 0) {
        await navigator.setAppBadge(count);
      } else {
        await navigator.clearAppBadge();
      }
    } catch (error) {
      console.error('[SW] Badge API error:', error);
    }
  }
}

// =======================================
// MESSAGE HANDLER - Custom notifications
// =======================================
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data?.type);
  
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
  
  if (event.data && event.data.type === 'UPDATE_BADGE') {
    updateBadgeCount(event.data.count);
  }
  
  if (event.data && event.data.type === 'CLEAR_BADGE') {
    updateBadgeCount(0);
  }
});

// =======================================
// PERIODIC SYNC - Background refresh
// =======================================
self.addEventListener('periodicsync', (event) => {
  console.log('[SW] Periodic sync:', event.tag);
  
  if (event.tag === 'refresh-feed') {
    event.waitUntil(refreshFeed());
  }
});

async function refreshFeed() {
  console.log('[SW] Refreshing feed in background...');
  try {
    const response = await fetch('/api/posts?limit=20');
    if (response.ok) {
      const data = await response.json();
      // Cache the new posts
      const cache = await caches.open(DYNAMIC_CACHE);
      await cache.put('/api/posts?limit=20', new Response(JSON.stringify(data)));
      console.log('[SW] Feed refreshed successfully');
    }
  } catch (error) {
    console.error('[SW] Feed refresh failed:', error);
  }
}

// =======================================
// INDEXED DB HELPERS
// =======================================
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('hiremebahamas-sw', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending-messages')) {
        db.createObjectStore('pending-messages', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('pending-posts')) {
        db.createObjectStore('pending-posts', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('pending-likes')) {
        db.createObjectStore('pending-likes', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

function getAllFromStore(db, storeName) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readonly');
    const store = tx.objectStore(storeName);
    const request = store.getAll();
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function deleteFromStore(db, storeName, id) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    const request = store.delete(id);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

console.log('[SW] Service Worker loaded - HireMeBahamas Addictive Edition v3');

