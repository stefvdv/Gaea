/* Gaea service worker — VERSION altijd gelijk aan APP_VERSION in index.html */
const VERSION = "0.24.0";
const SHELL = "wildpluk-shell-v" + VERSION;
const LIB   = "wildpluk-lib-v" + VERSION;
const TILES = "wildpluk-tiles";          /* niet versiegebonden */
const BEELD = "wildpluk-beeld";          /* foto's van soorten, ook niet versiegebonden */
const BEELD_MAX = 900;
const TILE_MAX = 1500;

const SHELL_FILES = ["./", "./index.html", "./manifest.webmanifest",
  "./icon-192.png", "./icon-512.png", "./badge-96.png"];

/* Al het sierbeeld zit als data-URI in index.html, dus er is geen
   losse art-map meer om te cachen. */
const LIB_FILES = [
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js",
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
];

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(SHELL);
    await c.addAll(SHELL_FILES);
    const l = await caches.open(LIB);
    await Promise.all(LIB_FILES.map(u => fetch(u, {mode:"cors"}).then(r => r.ok && l.put(u, r)).catch(()=>{})));
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) {
      if (k !== SHELL && k !== LIB && k !== TILES && k !== BEELD && k.startsWith("wildpluk-")) await caches.delete(k);
    }
    await self.clients.claim();
  })());
});

const isTile = u => /service\.pdok\.nl|tile\.openstreetmap\.org/.test(u.hostname);

async function trimTiles() {
  const c = await caches.open(TILES);
  const keys = await c.keys();
  for (let i = 0; i < keys.length - TILE_MAX; i++) await c.delete(keys[i]);
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  /* GBIF nooit via de service worker cachen — dat doet de app zelf in IndexedDB */
  /* Netwerkverkeer naar de beeld- en soortbronnen laten we met rust: dat is
     verse data, geen app-bestand. Naast GBIF nu ook iNaturalist en Wikimedia,
     die als reserve dienen wanneer GBIF niets heeft. */
  if (url.pathname.startsWith("/gbif/") || /(^|\.)gbif\.org$/.test(url.hostname)) return;
  if (url.pathname.startsWith("/inat/") || /(^|\.)inaturalist\.org$/.test(url.hostname)) return;
  if (url.pathname.startsWith("/wiki/") || /(^|\.)wikimedia\.org$/.test(url.hostname)
      || /(^|\.)wikipedia\.org$/.test(url.hostname)) return;
  if (/(^|\.)staticflickr\.com$/.test(url.hostname)) return;

  /* kaarttegels: cache-first, zo werkt een eerder bezocht gebied offline */
  if (isTile(url)) {
    e.respondWith((async () => {
      const c = await caches.open(TILES);
      const hit = await c.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && (res.ok || res.type === "opaque")) { c.put(req, res.clone()); trimTiles(); }
        return res;
      } catch (err) { return new Response("", {status:504}); }
    })());
    return;
  }

  /* soortfoto's van willekeurige hosts: cache-first, ook ondoorzichtige antwoorden.
     Zo blijft alles wat je een keer hebt gezien of voorgeladen offline werken. */
  if (req.destination === "image" && url.origin !== self.location.origin && !isTile(url)) {
    e.respondWith((async () => {
      const c = await caches.open(BEELD);
      const hit = await c.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && (res.ok || res.type === "opaque")) {
          c.put(req, res.clone());
          const keys = await c.keys();
          for (let i = 0; i < keys.length - BEELD_MAX; i++) await c.delete(keys[i]);
        }
        return res;
      } catch (err) { return new Response("", { status: 504 }); }
    })());
    return;
  }

  /* libs en fonts: cache-first */
  if (/cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com/.test(url.hostname)) {
    e.respondWith((async () => {
      const c = await caches.open(LIB);
      const hit = await c.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone());
        return res;
      } catch (err) { return hit || new Response("", {status:504}); }
    })());
    return;
  }

  /* eigen bestanden: network-first met terugval op cache */
  if (url.origin === self.location.origin) {
    e.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res && res.ok) (await caches.open(SHELL)).put(req, res.clone());
        return res;
      } catch (err) {
        return (await caches.match(req)) || caches.match("./index.html");
      }
    })());
  }
});

/* ---------------- dagelijkse herinnering ---------------- */
const openDB = () => new Promise((res, rej) => {
  const rq = indexedDB.open("wildpluk", 4);
  rq.onsuccess = () => res(rq.result);
  rq.onerror = () => rej(rq.error);
});
const readStore = (db, n) => new Promise(res => {
  try {
    const r = db.transaction(n, "readonly").objectStore(n).getAll();
    r.onsuccess = () => res(r.result || []);
    r.onerror = () => res([]);
  } catch (e) { res([]); }
});
const writeMeta = (db, v) => new Promise(res => {
  try {
    const r = db.transaction("meta", "readwrite").objectStore("meta").put(v);
    r.onsuccess = () => res(true);
    r.onerror = () => res(false);
  } catch (e) { res(false); }
});
const vandaag = () => new Date().toISOString().slice(0, 10);

async function checkHerinnering() {
  let db;
  try { db = await openDB(); } catch (e) { return; }
  const push = (await readStore(db, "meta")).find(m => m.k === "push");
  if (!push || !push.aan || push.laatst === vandaag()) return;

  const [uu, mm] = (push.tijd || "09:00").split(":").map(Number);
  const nu = new Date();
  if (nu.getHours() * 60 + nu.getMinutes() < uu * 60 + mm) return;

  const srs = await readStore(db, "srs");
  const t = vandaag();
  const klaar = srs.filter(r => r.due <= t).length;

  await writeMeta(db, {k:"push", aan:true, tijd:push.tijd, laatst:t});

  const PORTJES = [
    ["Er staat iets te bloeien", "Vijf soorten, twee minuten, en je weet ze morgen nog."],
    ["Gaea heeft iets voor je", "Vijf minuten planten kijken zonder je jas aan te doen."],
    ["Het bos vraagt naar je", "Een paar planten wachten op herhaling. Kop thee erbij?"],
    ["Even langs de veldschool", "Wie je vandaag oefent, herken je straks in de berm."],
    ["De dryade tikt op je schouder", "Kleine ronde. Namen, gebruik, en waar je voor moet oppassen."],
    ["Tijd voor een paar bladeren", "Korte oefening. Je streak blijft staan, en dat scheelt weer."]
  ];
  const p = PORTJES[new Date().getDate() % PORTJES.length];
  const body = srs.length === 0
    ? "Nog niet begonnen. Tien vragen en je kent je eerste soorten uit je hoofd."
    : klaar > 0
      ? klaar + " soorten staan klaar. " + p[1]
      : "Alles herhaald. Zin in een extra ronde?";

  /* absolute paden: een relatief pad valt op sommige toestellen terug
     op het browsericoon, en dan zie je een blokje in de statusbalk */
  const basis = self.registration.scope;
  return self.registration.showNotification(p[0], {
    body,
    icon: new URL("icon-192.png", basis).href,
    badge: new URL("badge-96.png", basis).href,
    tag: "gaea-quiz",
    data: { scr: "leer" }
  });
}

self.addEventListener("periodicsync", e => {
  if (e.tag === "wildpluk-dagelijks") e.waitUntil(checkHerinnering());
});
self.addEventListener("message", e => {
  if (e.data && e.data.type === "check") e.waitUntil(checkHerinnering());
});
self.addEventListener("notificationclick", e => {
  e.notification.close();
  const scr = (e.notification.data && e.notification.data.scr) || "leer";
  e.waitUntil((async () => {
    for (const c of await self.clients.matchAll({type:"window", includeUncontrolled:true})) {
      if (c.url.includes(self.registration.scope)) { c.postMessage({type:"open", scr}); return c.focus(); }
    }
    return self.clients.openWindow("./index.html#" + scr);
  })());
});
