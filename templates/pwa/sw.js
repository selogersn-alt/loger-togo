// ============================================
// Loger Togo - Service Worker PWA
// Version: 2.0 - Production Safe
// ============================================

const CACHE_NAME = 'Logertogo-v2';
const STATIC_CACHE = 'Logertogo-static-v2';

// Ressources critiques mises en cache au démarrage
const PRECACHE_URLS = [
  '/',
  '/annonces/',
  '/static/img/icon-192x192.png',
  '/static/img/icon-512x512.png',
  '/static/img/og_banner.png',
];

// ---- Installation ----
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      // On met en cache les ressources essentielles de façon sécurisée
      return Promise.allSettled(
        PRECACHE_URLS.map(url =>
          cache.add(url).catch(err => {
            console.warn('[SW] Impossible de mettre en cache:', url, err);
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

// ---- Activation (nettoyage des anciens caches) ----
self.addEventListener('activate', event => {
  const validCaches = [CACHE_NAME, STATIC_CACHE];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => !validCaches.includes(name))
          .map(name => {
            console.log('[SW] Suppression ancien cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// ---- Stratégie de fetch : Network-First avec fallback cache ----
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorer les requêtes non-GET et les APIs
  if (request.method !== 'GET') return;
  if (url.pathname.startsWith('/api/')) return;
  if (url.pathname.startsWith('/admin/')) return;
  if (url.pathname.includes('media/')) return; // Ne pas cacher les photos uploadées

  // Stratégie : Réseau en priorité, cache en secours
  event.respondWith(
    fetch(request)
      .then(response => {
        // Mettre à jour le cache avec la réponse fraîche
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        // Si hors-ligne, retourner le cache
        return caches.match(request).then(cached => {
          if (cached) return cached;
          // Fallback vers la page d'accueil si disponible
          if (request.destination === 'document') {
            return caches.match('/');
          }
        });
      })
  );
});
