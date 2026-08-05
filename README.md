# Wildpluk v0.4.0

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
    icon-*.png            app-iconen (dryadekop)
    badge-96.png          monochroom silhouet voor de statusbalk-melding
    maak_icoon.py         generator voor alle iconen, PIL op 8x met LANCZOS

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

## Iconen
`icon-192/512/maskable.png` zijn een dryadekop in Green Man-stijl: bladerkroon,
schorsranken, gouden ring, op diep bosgroen. Gegenereerd door `maak_icoon.py`
(geen SVG-rasterizer in de omgeving, dus met PIL geteakend op 8x en teruggeschaald).

`badge-96.png` is apart en essentieel: Android maakt van de meldings-badge een
silhouet en gooit alle kleur weg. Een dekkend vierkant icoon wordt dan een blok.
De badge is daarom wit-op-transparant met marge, en het silhouet is één geheel
(kroon en gezicht overlappen), anders valt het uiteen op 24 dp.

Ook in het manifest als `purpose: monochrome`.

## Betrouwbaarheid
Store `keur`, sleutel = soortsleutel of `r:receptsleutel`.
Vier standen: open, nagekeken, twijfel, klopt niet. Per stand een bron en notitie.

Tien invoeren zijn tijdens de bouw vergeleken met externe bronnen en staan al
ingevuld (NVIC, NMV, Het Acute Boekje, Wildpluk wiki): daslook, lelietje-van-dalen,
herfsttijloos, gevlekte aronskelk, groene knolamaniet, weidechampignon,
bundelmosklokje, morielje, plus witte knolamaniet en hanenkam op *twijfel*.
De rest staat op open — dat is de eerlijke stand van zaken.

Gids heeft een tabblad **Te controleren**. Instellingen exporteert de hele
controlelijst als markdown, handig om mee naar een flora of een kenner te nemen.

Giftige soorten krijgen een noodblok: huisarts of 112, zeg wat en hoeveel,
bewaar een restant, en wacht niet op klachten.

## Kaartgedrag
- Twee vingers knijpen om te zoomen (`touchZoom`, `tap:false`, `zoomSnap:.25`).
- Eén tik op de kaart zet een **spookpin**: gouden stippelring met een plus.
- Hardware terug laat de spookpin vallen; dat gaat vóór het sluiten van een blad.
- Nog een tik op de spookpin maakt de echte vondst aan.
- Lang indrukken werkt nog steeds als kortere weg.

## Kaart vullen
Instellingen → **Vul de kaart**, of de knop in de Ontdek-kiezer.
Resolvet eerst de taxonKeys van alle eetbare en medicinale soorten (eenmalig,
daarna gecachet), en vraagt dan GBIF in groepen van 45 taxonKeys tegelijk —
`occurrence/search` accepteert `taxonKey` meerdere keren als OR. Eén tot drie
verzoeken dekken zo de hele gids voor het huidige kaartbeeld.

Vraagt zoom 10 of dieper. De vulling blijft staan tot je de laag uitzet.

## Ornament
Zestien SVG-symbolen (varenkrul, zwam, gewei, vijzel, ketel, maan, jaarwiel,
sleutel, veder, vlam, pot, oog, ster, hand, hart, blad) als sectiekoppen,
lege-schermtekens en accenten. Krullijn onderaan elk blad, rank in beide hoeken.

**Maanstand en jaarwiel** staan bovenaan Gids → Nu en bovenaan Veldschool:
de maanfase wordt berekend uit de synodische maand vanaf de nieuwe maan van
6 januari 2000, en het jaarwiel toont welk feest geweest is en hoeveel dagen
tot het volgende — met wat er dan in het veld gebeurt.

## Nog te doen
- Waarneming.nl-koppeling (API-sleutel aanvragen) voor veel dichtere NL-dekking
- Determinatiehulp via Pl@ntNet, met verplichte verwarringscheck vóór "eetbaar"
- Zebra ZD421-labels rechtstreeks vanuit de voorraadkast
- Per-veld bronvermelding zodra er een geverifieerde tekstbron is gekozen
