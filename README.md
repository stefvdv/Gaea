# Wildpluk v0.6.0

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
175 soorten: 96 kruiden, 39 bomen en struiken, 40 paddenstoelen.
46 daarvan zijn giftig en staan er juist in om te leren kennen en te pinnen.
Nieuw in v0.6 onder meer: de kust (zeekraal, zulte, strandbiet, zeesla, blaaswier,
suikerwier), de klassieke lookalike-paren bij zwammen (stobbezwammetje naast
bundelmosklokje, weidekringzwam naast weidetrechterzwam, parelamaniet naast
panteramaniet, morielje naast voorjaarskluifzwam, champignon naast
karbolchampignon, hanenkam naast valse hanenkam en gordijnzwam), en de
medicinale soorten met een Europese monografie die nog ontbraken: koningskaars,
wilg, sleutelbloem, driekleurig viooltje, witte dovenetel, zwarte bes.

## Waarvoor — kwalen
24 kwalen in zeven groepen, elk met soorten en recepten. Per soort staat
`kwalen[]`; 26 soorten hebben daarnaast `emaInfo` met de monografiereferentie,
het plantendeel en waarvoor het is vastgelegd.

Het onderscheid dat de app overal maakt:
- **EMA** — het Comité voor Kruidengeneesmiddelen heeft een monografie
  vastgesteld. Dat is erkenning van traditioneel gebruik, geen bewijs van
  werkzaamheid. Geverifieerd tijdens de bouw voor Urtica, Plantago lanceolata,
  Tilia, Achillea, Capsella, Filipendula, Matricaria, Sambucus, Althaea en
  Equisetum, plus de combinatiemonografie *Species pectorales* voor borstthee.
- **Volksgebruik** — alles zonder die vlag. Interessant, niet gedekt.

## Gebruikstekening
Elk soortenblad opent met een schematische pentekening. Wat je gebruikt is
ingekleurd, de rest blijft lijn, en de kleur zegt welk soort deel het is:
groen blad, oker bloem, rood vrucht, bruin wortel, schors bast.

Vier groeivormen (kruid, boom, zwam, wier) en een parser die `delen` leest.
Nederlandse samenstellingen tellen mee — wortelknolletje kleurt de wortel,
bladsteel kleurt blad én stengel. Bij giftige zwammen blijft alles lijn,
want daar gebruik je niets van.

Dit is een schema, geen soortgetrouwe botanische plaat. Voor herkenning zijn
je eigen foto's en het GBIF-beeld leidend.

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

## Waarom de kaart leeg bleef
`occurrence/search` geeft per waarneming een `taxonKey` terug die vaak van een
andere rang is dan de soortsleutel waarop je zoekt — een ondersoort, een synoniem,
of juist het geslacht. De oude code deed `omgekeerd[o.taxonKey]` en gooide alles
weg wat niet exact matchte, dus meestal alles.

`koppelSoort()` probeert nu op volgorde: `taxonKey`, `speciesKey`,
`acceptedTaxonKey`, `usageKey`, dan de wetenschappelijke naam (volledig en op de
eerste twee woorden), dan het geslacht. Wat dan nog niet koppelt blijft staan met
de GBIF-naam erbij in plaats van te verdwijnen.

Er is nu ook terugkoppeling: als geen enkel verzoek antwoordt zegt de app dat,
en als GBIF wel records geeft maar niets koppelt zie je dat ook.

## Open databases voor gebruik en gevaren
- **Dr. Duke's Phytochemical and Ethnobotanical Databases** (USDA ARS) — de
  serieuze open bron voor plantgebruik. **CC0**, dus vrij te hergebruiken, met
  ethnobotanische toepassingen per soort, fytochemie, biologische activiteit en
  LD-toxiciteitsgegevens, met literatuurverwijzing per regel. Downloadbaar als
  `Duke-Source-CSV.zip` via Ag Data Commons; web-interface op phytochem.nal.usda.gov.
  Dit is een **build-time import**, geen live API: het CSV-pakket wordt omgezet
  naar een `GEBRUIK_DB`-tabel in de app.
- **EMA HMPC-monografieën** — gezaghebbend voor traditioneel gebruik,
  contra-indicaties en interacties, maar geen API. Handmatig per soort.
- **Wikidata** — open en machineleesbaar, dekking wisselend.
- **NVIC** — beste Nederlandse bron voor vergiftigingen, geen open API.

Duke's is Engelstalig en Amerikaans-gecentreerd, en zegt weinig over
verwarringssoorten in Nederlandse bermen. Het vult de kolom "gebruik" goed,
niet de kolom "gevaar".

## Beeld
Foto's komen uit GBIF-waarnemingen, met fotograaf en licentie eronder.
Elke foto is aan te tikken voor het vergrootglas: knijpen om te zoomen tot 6×,
dubbeltik voor 2,6×, slepen om te pannen.

**Instellingen → Beeld voorladen** loopt alle soorten af en haalt maximaal drie
foto's per soort op. Dat gebeurt met `fetch(url, {mode:"no-cors"})`: we mogen de
inhoud niet lezen, maar de service worker bewaart het ondoorzichtige antwoord in
de cache `wildpluk-beeld` (LRU op 900), en daarna werkt het offline. Nogmaals
tikken stopt de kuur. Reken op enkele tientallen MB — doe het op wifi.

## Spookpin
De spookpin slaat niets op. Hij is puur om te zien of je de juiste plek raakt.
- Nieuwe spookpin laat de vorige vallen.
- Terug-knop laat hem vallen.
- Van scherm wisselen laat hem vallen.
- Pas een tik óp de spookpin opent het formulier, en pas **Bewaren** maakt de
  vondst aan. Weggooien laat niets achter — er zit geen half opgeslagen pin meer
  in de lijst zoals in v0.5.

Intern: `nieuweVondst()` zet een concept in `S.concept` en slaat pas op bij
Bewaren. `newPin()` bestaat nog voor de GBIF-laag, waar je een waarneming
direct wilt overnemen.

## Veldschool
Afleiders komen nu altijd uit dezelfde wereld: bij een zwamvraag alleen zwammen,
bij een plantvraag alleen planten. Drie planten naast één paddenstoel maakt de
vraag te makkelijk en leert je niets. Nieuwe vraagsoort: waarvoor een soort
traditioneel gebruikt wordt, met in de uitleg of het EMA-gedekt is.

## Nog te doen
- Waarneming.nl-koppeling (API-sleutel aanvragen) voor veel dichtere NL-dekking
- Determinatiehulp via Pl@ntNet, met verplichte verwarringscheck vóór "eetbaar"
- Zebra ZD421-labels rechtstreeks vanuit de voorraadkast
- Per-veld bronvermelding zodra er een geverifieerde tekstbron is gekozen
