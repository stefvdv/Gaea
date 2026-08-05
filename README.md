# Wildpluk v0.2.0

Persoonlijke PWA voor eetbare en medicinale planten: vinden, herkennen, pinnen, gebruiken.
Vanilla JS, één `index.html`. Alles lokaal op het toestel (IndexedDB). Geen server, geen account.

## Deployen
Zet deze map in een Git-repo en koppel aan Netlify (of sleep de map naar Netlify Drop).
Geen build step. Publish directory = de map zelf.

Lokaal testen:
    npx serve .
Let op: geolocatie en service worker vereisen https of localhost.

## Bestanden
    index.html            app (UI, data, kaart, opslag) + SPECIES-lijst
    sw.js                 service worker, VERSION altijd gelijk aan APP_VERSION
    manifest.webmanifest  PWA-manifest
    icon-*.png            iconen

## Conventies
- APP_VERSION (index.html) en VERSION (sw.js) altijd in lockstep.
- localStorage-prefix `wildpluk:` — alleen voor voorkeuren (kaartlaag, kaartpositie, filters).
- IndexedDB `wildpluk`, stores `pins` en `photos`. Foto's als Blob, nooit in localStorage.
- Tegelcache (`wildpluk-tiles`) overleeft versiewissels; LRU op 1500 tegels.

## Kaartlagen
Doorlopen met de lagenknop rechtsboven:
1. PDOK BRT achtergrondkaart (topografie)
2. PDOK BRT grijs
3. PDOK luchtfoto (Actueel_ortho25)
4. OpenStreetMap

Controleer de PDOK-URL's op het toestel; PDOK herziet endpoints af en toe.
Vervangen kan bovenin `index.html`, in de `LAYERS`-array.

## Datamodel (pin)
    { id, lat, lng, acc, spec, naam, latijn, plek, habitat, hoev,
      toegang, zeker, vervuiling[], notitie, fotos[], oogst[], gemaakt, gewijzigd }

Foto: `{ id, pin, blob, stage, t }` — stage uit STAGES
(kiemplant, blad, knop, bloei, vrucht, winter, standplaats).

## Back-up
Instellingen → exporteer. Zonder foto's = klein JSON-bestand. Met foto's = volledig herstelbaar.
Import voegt samen en overschrijft op id.

## Voorraadkast
Store `maaksels`. Per maaksel:

    { id, naam, type, soorten[], pin, gemaakt, rijp, houdbaar,
      verhouding, hoeveelheid, restant, locatie, gebruik[], notitie, batch }

- 16 typen (tinctuur, oxymel, azijn, siroop, gedroogd, zout, ferment, ingelegd,
  olie, zalf, jam, likeur, thee, pesto, poeder, honing), elk met standaard
  rijpingstijd en houdbaarheid — datums worden automatisch ingevuld en blijven
  handmatig aanpasbaar.
- Batchcode WP-JJMM-NN, oplopend per maand.
- Status wordt berekend: rijpend / klaar / over datum / op.
- Weergave "Waarvoor" groepeert alles op gebruik, van dressing tot hoest & keel.
- Vanuit een vondst: "Hier iets van maken" vult soort en herkomst voor.
- "Etikettekst kopiëren" levert de regels voor een label; de ZD421-koppeling
  komt in een volgende versie.

## Veldschool
Leitner-systeem, dozen 0–7, intervallen 0/1/2/4/8/16/32/64 dagen.
Store `srs`: `{ k, box, due, goed, fout }`. Streak in `wildpluk:leer`.

Vraagsoorten: NL↔Latijn, verwarringsgevaar, let-op-regel, plantdeel, oogstmaand,
en vanaf drie gefotografeerde soorten ook herkenning op je eigen foto's.
Selectie weegt eigen plekken, gifplanten en eerdere fouten zwaarder.

## Dagelijkse herinnering
Zonder server bestaat echte web push niet. Wildpluk gebruikt
**Periodic Background Sync** (`wildpluk-dagelijks`, min. 6 u). De service worker
leest `meta.push` uit IndexedDB, kijkt of het ingestelde tijdstip vandaag
gepasseerd is en of er nog niet gemeld is, en toont dan de melding.

Voorwaarden op Android:
1. App op het startscherm zetten (geïnstalleerd, niet als tab).
2. Meldingen toestaan.
3. Chrome bepaalt zelf het exacte moment — reken op een marge van een uur.

Op iOS werkt periodic sync niet; daar port de app alleen als je hem opent.
Test met Instellingen → Test de melding.

## Nog te doen (v0.3+)
- GBIF / Nederlands Soortenregister import om de soortenlijst te vullen
- EMA HMPC-monografieën als bron voor het medicinale deel
- Recepten: van maaksel naar bereiding, met verhoudingen en timers
- Determinatiehulp via Pl@ntNet API, met verplichte verwarringscheck
- Zebra ZD421-labels vanuit de voorraadkast
