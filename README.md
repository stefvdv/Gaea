# Wildpluk v0.3.0

Persoonlijke PWA voor eetbare en medicinale planten, bomen en paddenstoelen:
vinden, herkennen, pinnen, bewaren en gebruiken. Vanilla JS, één `index.html`.
Alles lokaal (IndexedDB). Geen account, geen server, behalve de GBIF-proxy.

## Deployen (Netlify)
Map in een Git-repo, koppelen aan Netlify. Geen build step.
`_redirects` moet mee in de publish directory — die regelt de GBIF-proxy:

    /gbif/*  https://api.gbif.org/v1/:splat  200

De app valt automatisch terug op `https://api.gbif.org/v1/` als de proxy er niet is.

Lokaal: `npx serve .` — geolocatie en service worker vragen https of localhost.

## Bestanden
    index.html            app: stijl, soorten, recepten, logica
    sw.js                 service worker; VERSION == APP_VERSION
    _redirects            GBIF-proxy voor Netlify
    manifest.webmanifest  PWA-manifest
    icon-*.png            iconen

## Conventies
- APP_VERSION en sw.js VERSION altijd in lockstep.
- localStorage-prefix `wildpluk:` — alleen voorkeuren (kaartlaag, positie, filters, taxonKeys, streak).
- IndexedDB `wildpluk` v3, stores: `pins`, `photos`, `maaksels`, `srs`, `meta`, `gbif`.
- Foto's als Blob, nooit in localStorage.
- Tegelcache `wildpluk-tiles` overleeft versiewissels, LRU op 1500.
- De service worker cachet GBIF nooit — dat doet de app zelf met een TTL van 30 dagen.

## Waar de informatie vandaan komt
Drie soorten herkomst, en de app zegt het er per soortenblad bij:

1. **Namen en taxonomie** — GBIF. Elk soortenblad heeft een knop naar het GBIF-profiel.
   `species/match` levert de taxonKey, die wordt lokaal onthouden.
2. **Beeld** — waarnemingen in GBIF met `mediaType=StillImage`, inclusief fotograaf
   en licentie onder elke foto.
3. **Veldkenmerken, waarschuwingen, gebruik en recepten** — geschreven door Claude.
   Algemene kennis, geen geverifieerde bron, geen citaties. Voor 16 soorten bestaat
   een Europese HMPC-monografie; die is leidend en staat gelinkt.

Dat onderscheid staat ook in Instellingen, onder "Waar komt de informatie vandaan".

## Gids
122 soorten: 70 kruiden, 24 bomen en struiken, 28 paddenstoelen.
30 daarvan zijn giftig en staan er juist in om te leren kennen en te pinnen.
30 soorten hebben expliciete verwarringssoorten.

## Ontdek-laag (GBIF)
Vergrootglasknop op de kaart. Kies maximaal 3 soorten; de app haalt waarnemingen
op voor het huidige kaartbeeld vanaf zoom 11. Gestippelde open markers, visueel
apart van je eigen volle pins. Seriële wachtrij op 140 ms.

Belangrijk: veel records zijn afgerond op honderden meters tot een kilometer en
gevoelige soorten worden bewust vervaagd. Het is een zoekgebied, geen vindplaats.
"Eigen vondst hier zetten" maakt een pin met status "nog te bevestigen".

## Voorraadkast en recepten
Store `maaksels`; 16 typen met eigen rijpingstijd en houdbaarheid, batchcode
WP-JJMM-NN, status rijpend/klaar/over datum/op, en de weergave "Waarvoor" die
alles groepeert op gebruik.

22 recepten (12 keuken, 10 lijf) met ingrediëntenlijst en stappen. "Zet in de
voorraadkast" maakt het maaksel aan met de juiste rijpings- en houdbaarheidsdatum.

## Veldschool
Leitner, dozen 0–7, intervallen 0/1/2/4/8/16/32/64 dagen. Zeven vraagsoorten:
NL↔Latijn, verwarringsgevaar, let-op-regel, veldkenmerk, plantdeel, oogstmaand,
en vanaf drie gefotografeerde soorten herkenning op je eigen foto's.
Weging: eigen plekken > gifplanten > paddenstoelen > eerder foute antwoorden.

## Dagelijkse herinnering
Periodic Background Sync (`wildpluk-dagelijks`, min. 6 u). Werkt alleen als de app
op het startscherm staat. Chrome bepaalt het exacte moment; marge van ongeveer een uur.

## Nog te doen
- Waarneming.nl-koppeling (API-sleutel aanvragen) voor veel dichtere NL-dekking
- Determinatiehulp via Pl@ntNet, met verplichte verwarringscheck vóór "eetbaar"
- Zebra ZD421-labels rechtstreeks vanuit de voorraadkast
- Per-veld bronvermelding zodra er een geverifieerde tekstbron is gekozen
