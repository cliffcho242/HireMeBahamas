/// <reference lib="webworker" />

const CACHE_VERSION = "v1";
const CACHE_NAME = `hiremebahamas-${CACHE_VERSION}`;

// Assets to cache immediately
const STATIC_ASSETS = [
  "/",
  "/manifest.json",
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
];

// API routes to cache with stale-while-revalidate
const API_CACHE_ROUTES = [
  "/api/jobs",
];

// Install event - cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  // Activate immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith("hiremebahamas-") && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  // Take control immediately
  self.clients.claim();
});

// Fetch event - serve from cache with network fallback
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== "GET") {
    return;
  }

  // API routes - stale-while-revalidate
  if (API_CACHE_ROUTES.some((route) => url.pathname.startsWith(route))) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((cachedResponse) => {
          const fetchPromise = fetch(event.request).then((networkResponse) => {
            if (networkResponse.ok) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          });

          return cachedResponse || fetchPromise;
        });
      })
    );
    return;
  }

  // Static assets - cache first
  if (url.pathname.startsWith("/_next/static") || STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return cachedResponse || fetch(event.request).then((networkResponse) => {
          if (networkResponse.ok) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // Network first for everything else
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          return cachedResponse || caches.match("/");
        });
      })
  );
});

// Push notification event
self.addEventListener("push", (event) => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body || "You have a new notification",
    icon: "/icons/icon-192x192.png",
    badge: "/icons/badge-72x72.png",
    vibrate: [100, 50, 100],
    data: {
      url: data.url || "/",
    },
    actions: [
      { action: "open", title: "Open" },
      { action: "close", title: "Close" },
    ],
    tag: data.tag || "default",
    renotify: true,
    requireInteraction: data.requireInteraction || false,
  };

  event.waitUntil(self.registration.showNotification(data.title || "HireMeBahamas", options));
});

// Notification click event
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "close") {
    return;
  }

  const url = event.notification.data?.url || "/";

  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      // Focus existing window if available
      for (const client of clients) {
        if (client.url === url && "focus" in client) {
          return client.focus();
        }
      }
      // Open new window
      return self.clients.openWindow(url);
    })
  );
});

// Background sync for offline form submissions
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-messages") {
    event.waitUntil(syncMessages());
  }
  if (event.tag === "sync-applications") {
    event.waitUntil(syncApplications());
  }
});

async function syncMessages() {
  // Sync pending messages from IndexedDB
  console.log("Syncing messages...");
}

async function syncApplications() {
  // Sync pending job applications from IndexedDB
  console.log("Syncing applications...");
}
