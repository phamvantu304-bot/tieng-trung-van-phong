// Offline cache. Tăng VERSION mỗi khi cập nhật nội dung để iPhone tải bản mới.
const VERSION = "ttvp-v10";
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Âm thanh: để trình duyệt tự tải (hỗ trợ tua, phát nền khi khoá máy).
  if (url.pathname.includes("/audio/") && url.pathname.endsWith(".m4a")) return;
  // Trang chính: lấy bản mới khi có mạng, mất mạng thì dùng bản đã lưu.
  if (req.mode === "navigate") {
    e.respondWith(fetch(req.url, { cache: "no-cache" }).then(r => {
      const copy = r.clone(); caches.open(VERSION).then(c => c.put("index.html", copy)); return r;
    }).catch(() => caches.match("index.html")));
    return;
  }
  // Dữ liệu hội thoại: luôn lấy bản mới khi có mạng, mất mạng thì dùng bản đã lưu.
  if (url.origin === location.origin && (url.pathname.endsWith(".json") || url.pathname.endsWith("version.txt"))) {
    e.respondWith(fetch(req.url, { cache: "no-cache" }).then(r => {
      const copy = r.clone(); caches.open(VERSION).then(c => c.put(req, copy)); return r;
    }).catch(() => caches.match(req)));
    return;
  }
  // Font Google và file tĩnh: dùng bản đã lưu, nếu chưa có thì tải rồi lưu lại.
  if (url.origin === location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
      const copy = r.clone(); caches.open(VERSION).then(c => c.put(req, copy)); return r;
    })));
  }
});
