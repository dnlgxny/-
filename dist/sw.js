/* ═══════════════════════════════════════════════════════════════
   开源工作台 · Service Worker
   目标：加到手机主屏后可离线打开（页面为自包含单页，缓存体积极小）
   策略：
     - 导航请求：network-first（有网拿最新，无网回退缓存）
     - 静态资源：cache-first（图标等，命中缓存即可）
   ⚠️ 缓存名含版本号：每次部署新版本必须改 CACHE，否则用户拿到旧页面
   ═══════════════════════════════════════════════════════════════ */

const CACHE = 'openwork-20261016054015';          // 部署新版时改这里的 v1 → v2 …
const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png',
  './icons/apple-touch-icon.png'
];

// 安装：预缓存
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())   // 某个资源缺失也不阻塞安装
  );
});

// 激活：清理旧版本缓存
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;

  // 导航请求（HTML）：network-first，离线回退缓存
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put('./index.html', copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match('./index.html').then(r => r || caches.match('./')))
    );
    return;
  }

  // 同源静态资源：cache-first
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        if (res && res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
        }
        return res;
      }).catch(() => hit))
    );
  }
});
