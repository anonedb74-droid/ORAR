// ORAR – service worker: rețeaua întâi, apoi cache (merge și fără semnal)
const CACHE_NAME = "orar-cache-v4";
const FISIERE = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(FISIERE))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== CACHE_NAME).map(n => caches.delete(n))))); self.clients.claim(); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return; // nu punem în cache Google/Firebase
  e.respondWith(fetch(e.request).then(r => { const copie = r.clone(); caches.open(CACHE_NAME).then(c => c.put(e.request, copie)); return r; })
    .catch(() => caches.match(e.request).then(r => r || caches.match("./index.html"))));
});
