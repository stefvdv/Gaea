/* Wildpluk service worker — versie in lockstep met APP_VERSION in index.html */
const VERSION = "0.2.0";
const SHELL = "wildpluk-shell-v" + VERSION;
const LIB   = "wildpluk-lib-v" + VERSION;
const TILES = "wildpluk-tiles";      /* niet versiegebonden: tegels blijven staan */
const TILE_MAX = 1500;

const SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png"
];

const LIB_FILES = [
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js",
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
];

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(SHELL);
    await c.addAll(SHELL_FILES);
    const l = await caches.open(LIB);
    await Promise.all(LIB_FILES.map(u =>
      fetch(u, { mode: "cors" }).then(r => r.ok && l.put(u, r)).catch(() => {})
    ));
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => {
      if (k === SHELL || k === LIB || k === TILES) return null;
      if (k.startsWith("wildpluk-")) return caches.delete(k);
      return null;
    }));
    await self.clients.claim();
  })());
});

function isTile(url) {
  return /service\.pdok\.nl|tile\.openstreetmap\.org/.test(url.hostname);
}

async function trimTiles() {
  const c = await caches.open(TILES);
  const keys = await c.keys();
  if (keys.length <= TILE_MAX) return;
  for (let i = 0; i < keys.length - TILE_MAX; i++) await c.delete(keys[i]);
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  /* kaarttegels: cache-first, zo werkt een eerder bezocht gebied offline */
  if (isTile(url)) {
    e.respondWith((async () => {
      const c = await caches.open(TILES);
      const hit = await c.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && (res.ok || res.type === "opaque")) {
          c.put(req, res.clone());
          trimTiles();
        }
        return res;
      } catch (err) {
        return new Response("", { status: 504 });
      }
    })());
    return;
  }

  /* fonts en libs: cache-first met stille verversing */
  if (/cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com/.test(url.hostname)) {
    e.respondWith((async () => {
      const c = await caches.open(LIB);
      const hit = await c.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone());
        return res;
      } catch (err) {
        return hit || new Response("", { status: 504 });
      }
    })());
    return;
  }

  /* eigen bestanden: network-first, val terug op cache */
  if (url.origin === self.location.origin) {
    e.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res && res.ok) (await caches.open(SHELL)).put(req, res.clone());
        return res;
      } catch (err) {
        const hit = await caches.match(req);
        return hit || caches.match("./index.html");
      }
    })());
  }
});

/* =========================================================
   Dagelijkse herinnering
   Geen server: we gebruiken Periodic Background Sync.
   Android Chrome bepaalt zelf wanneer dit draait; wij checken
   of het tijdstip vandaag al gepasseerd is en of er al gemeld is.
   ========================================================= */

function openDB() {
  return new Promise((res, rej) => {
    const rq = indexedDB.open("wildpluk", 2);
    rq.onsuccess = () => res(rq.result);
    rq.onerror = () => rej(rq.error);
  });
}
function readStore(db, name) {
  return new Promise((res) => {
    try {
      const r = db.transaction(name, "readonly").objectStore(name).getAll();
      r.onsuccess = () => res(r.result || []);
      r.onerror = () => res([]);
    } catch (e) { res([]); }
  });
}
function writeMeta(db, val) {
  return new Promise((res) => {
    try {
      const r = db.transaction("meta", "readwrite").objectStore("meta").put(val);
      r.onsuccess = () => res(true);
      r.onerror = () => res(false);
    } catch (e) { res(false); }
  });
}
const vandaag = () => new Date().toISOString().slice(0, 10);

async function checkHerinnering() {
  let db;
  try { db = await openDB(); } catch (e) { return; }

  const meta = await readStore(db, "meta");
  const push = meta.find(m => m.k === "push");
  if (!push || !push.aan) return;
  if (push.laatst === vandaag()) return;

  const [uu, mm] = (push.tijd || "09:00").split(":").map(Number);
  const nu = new Date();
  if (nu.getHours() * 60 + nu.getMinutes() < uu * 60 + mm) return;

  /* hoeveel soorten staan er klaar? */
  const srs = await readStore(db, "srs");
  const t = vandaag();
  const klaar = srs.filter(r => r.due <= t).length;
  const nieuw = srs.length === 0;

  await writeMeta(db, { k: "push", aan: true, tijd: push.tijd, laatst: t });

  const body = nieuw
    ? "Nog niet begonnen. Tien vragen en je weet je eerste soorten uit je hoofd."
    : klaar > 0
      ? klaar + " soorten staan klaar. Twee minuten, en je streak blijft staan."
      : "Alles herhaald. Zin in een extra ronde?";

  return self.registration.showNotification("Tijd voor de veldschool", {
    body,
    icon: "icon-192.png",
    badge: "icon-192.png",
    tag: "wildpluk-quiz",
    renotify: false,
    data: { scr: "leer" }
  });
}

self.addEventListener("periodicsync", e => {
  if (e.tag === "wildpluk-dagelijks") e.waitUntil(checkHerinnering());
});

/* handmatige trigger vanuit de app */
self.addEventListener("message", e => {
  if (e.data && e.data.type === "check") e.waitUntil(checkHerinnering());
});

self.addEventListener("notificationclick", e => {
  e.notification.close();
  const scr = (e.notification.data && e.notification.data.scr) || "leer";
  e.waitUntil((async () => {
    const all = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of all) {
      if (c.url.includes(self.registration.scope)) {
        c.postMessage({ type: "open", scr });
        return c.focus();
      }
    }
    return self.clients.openWindow("./index.html#" + scr);
  })());
});
