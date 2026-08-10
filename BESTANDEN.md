# Gaea's Natural Health — v0.23.0

De volledige repo-inhoud. Alles hieronder mag je één op één in `main` zetten;
samen is dit een werkende app.

## Wat de app draait

| bestand | wat het is |
|---|---|
| `index.html` | de hele app: stijl, 255 soorten, 78 recepten, 24 kwalen, alle logica én al het sierbeeld als data-URI |
| `sw.js` | service worker; `VERSION` staat altijd gelijk aan `APP_VERSION` in index.html |
| `manifest.webmanifest` | naam, iconen, kleuren. Android leest de naam alleen bij het installeren |
| `_redirects` | Netlify-proxy naar GBIF, iNaturalist en Wikimedia Commons |
| `icon-192.png` `icon-512.png` `icon-maskable.png` `badge-96.png` | app-iconen en het meldingsbadge |

## Gereedschap

| bestand | wat het doet |
|---|---|
| `proef.js` | `node proef.js` draait de app-code in een nagebouwde browser en roept alle schermen aan |
| `keuring.js` | de controles die proef.js uitvoert; apart bestand omdat een template literal backslashes opeet |
| `maak_icoon.py` | genereert de vier iconen. Vereist `art_nieuw/kruidenvrouw.png` en `ring-eikel.png` |
| `snijranken.py` | snijdt aangeleverde sprite sheets tot losse ranken. Vereist de bronvellen |

De twee Python-scripts kunnen niet draaien zonder hun bronmappen, die bewust
niet in de repo staan — het zijn bij elkaar tientallen megabytes en ze zijn
alleen nodig als je het beeldmateriaal wilt vervangen. Ze staan er als verslag
van hoe het gemaakt is.

## Weggehaald in deze update
`groei.py` en `vrij.py` mogen uit de repo. De eerste maakte de acht
groeistadia die in v0.21 uit de startanimatie verdwenen; de tweede verwerkte de
losse illustraties die inmiddels allemaal in `index.html` zitten.

## Voor je uitrolt
    node proef.js

Dat controleert de app-code, alle 255 soorten, elke quizvraag op alle drie de
categorieën, de familiedekking en de kaartchips. Bij "alle vragen door de
keuring" en "script geladen zonder directe fout" kun je door.
