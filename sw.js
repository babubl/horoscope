/* Jothidam service worker — offline app shell, cached fonts, live network for place search and AI */
const VERSION = 'subajathagam-v10';
const SHELL = ['/', '/ta/', '/ml/', '/te/', '/kn/', '/hi/', '/about.html', '/guide.html', '/privacy.html', '/terms.html', '/assets/site.css', '/manifest.webmanifest',
  '/icons/icon-192.png', '/icons/icon-512.png', '/icons/icon-maskable-512.png', '/icons/apple-touch-icon.png', '/icons/favicon-32.png', '/data/places.json'];
const FONT_CACHE = 'jothidam-fonts';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== FONT_CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(FONT_CACHE).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  if (url.origin !== location.origin) return; // place search, Gemini, ads: always network
  const isPage = req.mode === 'navigate' || /\.(html|webmanifest)$/.test(url.pathname) || url.pathname.endsWith('/');
  e.respondWith((async () => {
    const c = await caches.open(VERSION);
    const key = req.mode === 'navigate' ? new Request(url.pathname) : req;
    if (isPage) {
      // pages: network first so updates show immediately; cache only when offline
      try { const r = await fetch(req, { cache: 'no-cache' }); if (r.ok) c.put(key, r.clone()); return r; }
      catch { return (await c.match(key, { ignoreSearch: true })) || (await c.match('/')) || Response.error(); }
    }
    const hit = await c.match(req);
    const net = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; });
    if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
    try { return await net; } catch { return Response.error(); }
  })());
});
