const CACHE_NAME = 'syrius-v1';

// Instala e já tenta armazenar o básico (mesmo que você não liste tudo)
self.addEventListener('install', (event) => {
    self.skipWaiting(); // Força o novo SW a assumir
});

// Ativa e limpa caches antigos
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Intercepta as requisições (O básico para não dar erro de offline)
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});