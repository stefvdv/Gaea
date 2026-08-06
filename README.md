# Gaea v0.8.1

Persoonlijke PWA voor eetbare en medicinale planten, bomen en paddenstoelen:
vinden, herkennen, pinnen, bewaren en gebruiken. Vanilla JS, één `index.html`.
Alles lokaal (IndexedDB). Geen account, geen server, behalve de GBIF-proxy.

**Heette tot v0.6 Wildpluk.** De opslagsleutels zijn met opzet niet meegehernoemd:
localStorage houdt het voorvoegsel `wildpluk:` en de IndexedDB heet nog `wildpluk`,
zodat bestaande vondsten, maaksels en voortgang gewoon blijven staan. Alleen wat
je ziet is veranderd. Back-ups worden weggeschreven als `app:"gaea"`; import
accepteert beide. Nieuwe batchcodes beginnen met `GA-`, oude `WP-`-codes blijven
zoals ze zijn.

## Deployen (Netlify)
Map in een Git-repo, koppelen aan Netlify. Geen build step.
`_redirects` moet mee in de publish directory — die regelt de GBIF-proxy:

    /gbif/*  https://api.gbif.org/v1/:splat  200

De app valt automatisch terug op `https://api.gbif.org/v1/` als de proxy er niet is.

Lokaal: `npx serve .` — geolocatie en service worker vragen https of localhost.

## Bestanden
    index.html            app: stijl, soorten, recepten, logica én al het sierbeeld
    sw.js                 service worker; VERSION == APP_VERSION
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

## Botanische plaat
Eén algemene plaat voor alles wat een plant is: penwortel met zijwortels,
stengel, drie bladparen met steel, middennerf en zijnerven, een gesloten knop,
een bloemscherm met zes bloempjes van elk zes kroonblaadjes, en bessen aan
zijstelen. Per soort wordt ingekleurd wat je van die soort gebruikt; de rest
blijft pentekening.

De kleur zegt welk soort deel het is: groen blad, oker bloem, rood vrucht,
bruin wortel, olijf stengel, schors bast.

Twee varianten daarnaast, omdat een plantenplaat daar niets zegt: een
plaatjeszwam (hoed, plaatjes, ring, beursje, sporenstip) en een wier (thallus
met middennerf en hechtorgaan).

`welkeDelen()` leest het veld `delen`. Nederlandse samenstellingen tellen mee —
wortelknolletje kleurt de wortel, bladsteel kleurt blad én stengel. Bij giftige
zwammen blijft alles lijn, want daar gebruik je niets van.

Dit is een schema, geen soortgetrouwe plaat. Voor herkenning zijn je eigen
foto's en het GBIF-beeld leidend.

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

## Geïllustreerde assets
De zes aangeleverde bladen zijn met `snij.py` uitgesneden: alfamasker, licht
dichtsmeren zodat losse blaadjes bij hun ornament horen, samenhangende gebieden
labelen, bijsnijden, verkleinen en kwantiseren met behoud van transparantie.

In gebruik:
- **Ronde reliëfknoppen** voor kaartlaag, instellingen, GPS, ontdekken, sluiten en
  de plus op *Pin hier*. Geen achtergrond meer, alleen de penning met een
  slagschaduw; de actieve knop krijgt een groene gloed.
- **Vierkante tegels** als navigatie: kaart, pin, mand, blad, boek. Inactief
  gedempt en grijzer, actief in kleur met gloed.
- **Scheidingslijnen** onder elke schermkop (slinger met medaillon), boven elke
  sectiekop in een blad (fijne band) en achter elke groepskop (haarlijn).
- **Hoekornamenten** in alle vier de hoeken van elk blad, en een klein eikentakje
  rechtsonder op elke kaart in de lijsten.
- **Takjes** als leeg-schermteken en als vervaagd accent in waarschuwingsblokken.
- **Flesjes** rechtsonder op elk voorraadpotje — groen glas voor natte maaksels
  (tinctuur, oxymel, azijn, siroop, olie, likeur, honing, ferment), amber voor
  droge (gedroogd, zout, thee, poeder).
- **Boommedaillon** als zegel in elke schermkop.
- **Lijst** als `border-image` rond het specimenblad, met het binnenvlak
  weggesneden zodat het papier van de app zelf zichtbaar blijft.

`snij.py` staat erbij, dus nieuwe bladen kun je met dezelfde methode uitsnijden.

**Alles zit als data-URI in `index.html`.** Er is geen `art/`-map meer. Dat scheelt
26 losse bestanden bij het deployen, en het maakt de app in één klap volledig
offline-compleet zonder aparte cachestap in de service worker. Prijs: index.html
is ongeveer 2 MB, en bij elke update haalt de browser dat opnieuw op. Voor een
persoonlijke app op wifi is dat prima; wil je het ooit terug naar losse bestanden,
draai dan `snij.py` opnieuw en vervang de data-URI's door `url(art/naam.png)`.

## Vormgeving
Alles wat een oppervlak is deelt één behandeling: lichte bovenrand, donkere
onderrand, zachte slagschaduw. Dat zit in de tokens `--relief`, `--relief-diep`
en `--relief-ink`, plus een fijne schubtextuur (`--schub`) als data-URI over de
donkere panelen.

- Kaarten (vondsten, maaksels, kwalen, instellingen) krijgen een verlopend paneel,
  een gouden haarlijn langs de bovenrand en een eikenblad in de hoek.
- Knoppen zijn geperst: verloop, binnenlicht, gouden rand op de primaire.
- De navigatiebalk heeft een gouden haarlijn en een streepje boven het actieve item.
- Elke schermkop draagt het dryade-zegel, met daaronder een knoopregel:
  gouden lijn, symbool, gouden lijn.
- Elk blad heeft een dubbele omlijsting in het papier en keltische hoekknopen
  linksboven en rechtsboven, plus de rank rechtsboven en linksonder.

## Startanimatie
De kruidenvrouw met vijzel en flacon, in een gouden lijst. Het origineel is te
druk voor een klein scherm, dus de plaat is bewerkt: bijgesneden tot kop, handen,
vijzel en flacon, mediaanfilter tegen ruis, licht verzacht en daarna heel licht
verscherpt zodat de vormen blijven, iets minder verzadigd, en een vignet dat de
randen laat wegvallen. Van 941 naar 760 px, 196 kB.

Bewegen doet hij zo:
- de plaat komt op en zoomt langzaam uit van 110% naar 100% over 4,6 s
- een groene gloed pulseert over de flacon in haar hand, 3,1 s
- een gouden gloed pulseert trager over de vijzel, 4,2 s
- de kaars linksonder flikkert onregelmatig, 1,7 s
- zestien sporen stijgen op vanaf willekeurige punten, elk met eigen duur,
  vertraging en zijwaartse drift
- de gouden lijst komt na een halve seconde op
- daarna GAEA, een uitrollende sierlijn en de ondertitel

Ongeveer 3,4 s. Tikken slaat het over; bij `prefers-reduced-motion` staat alles
stil en verdwijnt het scherm na 0,9 s.

## Iconen
`icon-192/512/maskable.png` zijn een dryadekop in Green Man-stijl. Volledig
opnieuw getekend in v0.7, met per element een schaduw-, kleur- en lichtpas:
bladeren met slagschaduw, verzachte schaduwhelft, middennerf, zijnerven en
randlicht; schorsstrengen met kern, highlight en donkere onderkant; een gezicht
met kernschaduw langs de rand, licht van linksboven, wenkbrauwrichel en randlicht;
ogen met iris-ringen, straaltjes, ooglidschaduw en twee spiegelingen; een flacon
met glasverloop, meniscus, zeven bellen en een gloed.

De ring is bewust terughoudend: twee fijne gouden cirkels met een verloop over de
omtrek en vier knoopjes op de assen, in plaats van dik vlechtwerk dat de kop
overschreeuwt. Achtergrond met radiale gloed, vignet en fijne korrel.

Gegenereerd door `maak_icoon.py` — geen SVG-rasterizer in de omgeving, dus met
PIL getekend op 6× en met LANCZOS teruggeschaald.

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
