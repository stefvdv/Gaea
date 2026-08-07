# Gaea's Natural Health — v0.18.0

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
    manifest.webmanifest  naam, iconen, kleuren
    proef.js              droogloop in een neppe DOM, zie hieronder

## Naam
`manifest.webmanifest` bepaalt wat Android onder het icoon zet:
`name` is "Gaea's Natural Health", `short_name` is "Gaea". Android leest die
naam alleen bij het installeren, dus na een naamswijziging moet je de app van je
startscherm halen en opnieuw toevoegen. In de app zelf staat kortweg "Gaea",
want de volledige naam past niet in een balk van 390 px.

## proef.js — droogloop
`node proef.js` draait de volledige app-code in een nagebouwde browser: neppe
DOM, localStorage, IndexedDB, Leaflet en fetch. Daarna roept het de vijf schermen
aan, bouwt het een vraag voor alle 219 soorten, tekent alle botanische platen en
loopt de kwaalpictogrammen af.

Dat vangt precies wat `node --check` niet ziet: een verwijzing naar een functie
die niet bestaat. In v0.11.0 verwees de niveaukoppeling naar `qVerwar`, terwijl
de generator `qDubbel` heet — syntactisch correct, en toch bleef de app op het
opstartscherm hangen. Draai dit voor elke release.
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
255 soorten: 115 kruiden, 42 bomen en struiken, 46 paddenstoelen en 52 tuin-,
keuken- en apotheekkruiden. 59 daarvan zijn giftig.

Nieuw in v0.14 vooral de soorten die al in verwarringswaarschuwingen genoemd
werden maar zelf geen blad hadden — die knoppen liepen dood. Daardoor loopt de
koppeling van `dubbelSleutel()` van 47 op 67 naar 86 op 101. Verder meer salies
(veldsalie, scharlei, ananassalie), meer tuinkruiden, en de giftige
voorjaarsbollen die naast daslook opkomen: narcis en sneeuwklokje.

### Bij het toevoegen van data
Een soort toevoegen is nooit één regel. De hele keten:
`SPECIES` → `KWALEN_MAP` en zo nodig `EMA_MAP` → recepten die ernaar verwijzen →
en dan `node proef.js`, dat controleert op dubbele sleutels, dubbele
wetenschappelijke namen, dubbele Nederlandse namen, ontbrekende `herken` of
`let`, recepten die naar onbekende soorten wijzen, en quizvragen met twee
identieke antwoorden.

Die laatste controle vond meteen iets: `vingerhoedstuin` en `kluifzwam` hadden
allebei een dubbelganger met dezelfde wetenschappelijke naam, en dat gaf
quizvragen met twee identieke keuzes. Samengevoegd.
Ze staan er juist in om te leren kennen en te pinnen.
Nieuw in v0.6 onder meer: de kust (zeekraal, zulte, strandbiet, zeesla, blaaswier,
suikerwier), de klassieke lookalike-paren bij zwammen (stobbezwammetje naast
bundelmosklokje, weidekringzwam naast weidetrechterzwam, parelamaniet naast
panteramaniet, morielje naast voorjaarskluifzwam, champignon naast
karbolchampignon, hanenkam naast valse hanenkam en gordijnzwam), en de
medicinale soorten met een Europese monografie die nog ontbraken: koningskaars,
wilg, sleutelbloem, driekleurig viooltje, witte dovenetel, zwarte bes.

## Waarvoor — kwalen
24 kwalen in zeven groepen, elk met soorten en recepten. Per soort staat
`kwalen[]`; 53 soorten hebben daarnaast `emaInfo` en gelden als officieel erkend
traditioneel gebruik. De rest is volksgebruik en staat er als zodanig bij.

Dat onderscheid blijft, want het is veiligheidsinformatie: erkend betekent lang
en veilig genoeg gebruikt om geregistreerd te worden, niet dat werkzaamheid is
aangetoond.

## Tuin, keuken en apotheek
Nieuw in v0.10: 43 kruiden die je kweekt of koopt in plaats van plukt, onder een
eigen tabblad. Salie, rozemarijn, lavendel, echte tijm, basilicum, peterselie,
bieslook, dille, venkel, koriander, dragon, kervel, bonenkruid, laurier,
pepermunt, groene munt, citroenverbena, goudsbloem, rode zonnehoed, hysop, lavas,
absintalsem, knoflook, mierikswortel, zoethout, gember, kurkuma, kaneel, anijs,
karwij, komijn, zwarte komijn, Roomse kamille, passiebloem, vrouwenmantel,
guldenroede, berendruif, bleekselderij, citroengras, ginkgo, aloë vera, en twee
die er staan om te leren mijden: wijnruit en vingerhoedskruid in de tuin.

Ze horen erbij omdat de voorraadkast en de recepten er net zo goed op draaien.

## Soortenblad
Van boven naar beneden: kop met tags en maandbalk, waarschuwingen, de botanische
plaat, veldkenmerken, medicinaal gebruik, toelichting, beeld uit GBIF, recepten,
en je eigen plekken.

**Maandbalk** — twaalf blokjes met de beginletter erboven, J F M A M J J A S O N D.
Zonder die letters moest je tellen. De blokjes zijn ook groter, en de letter van
een maand waarin je kunt oogsten is donkerder.

**Verwarbaar met** — de verwarringen staan als vrije tekst, bijvoorbeeld
"Kruidvlier (giftig, kruidachtig, rechtopstaande bestros)". `dubbelSleutel()`
pakt het stuk voor de haakjes en zoekt de soort in de gids; lukt dat, dan wordt
het een knop naar dat blad. Van de 67 verwarringen koppelen er 47. De rest zijn
soorten die niet in de gids staan of beschrijvingen zonder soortnaam, en die
blijven gewone tekst — beter dan een knop die niets doet.

**Jouw plekken** — aanklikbaar. Het blad gaat dicht, de kaart komt op en vliegt
naar die vondst op zoom 17.

**Beeld uit GBIF** — aantikken opent de loep schermvullend, met pinch-zoom tot 6×
en dubbeltik naar 2,6×. De hardwareterugknop sluit eerst de loep, dan pas het
blad. De strip komt asynchroon binnen, dus de loep wordt daar apart aangehaakt;
de binding die `showSheet()` legt is dan al geweest.

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

## GBIF-waarnemingen
Er is geen knop meer om de kaart te vullen: de waarnemingen horen er gewoon te
staan. `autoVul()` draait bij het opstarten en telkens als je stil komt te liggen
na een verplaatsing, met 900 ms vertraging.

Het bijvullen gebeurt zwijgend: je vroeg er niet om, dus hoef je er ook niets
over te lezen. Alleen de eenmalige naamophaling meldt zich, en dan alleen als
je het zelf hebt aangevraagd.

Per kaartbeeld wordt een sleutel bijgehouden — de vier hoeken op twee decimalen,
dus ongeveer een kilometer. Fijner heeft geen zin, want de meeste GBIF-records
zijn toch op honderden meters afgerond. Een beeld dat al is opgehaald wordt niet
opnieuw bevraagd, en nieuwe waarnemingen komen erbíj in plaats van de vorige te
vervangen, zodat de kaart aangroeit terwijl je rondloopt.

De eerste keer moeten de taxonKeys van alle eetbare en medicinale soorten worden
opgezocht. Dat kost even, gebeurt eenmalig en wordt daarna in localStorage
bewaard; je krijgt er één melding over en verder is het stil. Vanaf zoom 12.

De knop in de Ontdek-kiezer bestaat nog, maar heet nu "Nu opnieuw ophalen voor
dit kaartbeeld" en wist eerst de sleutel.

Belangrijk blijft: veel records zijn afgerond op honderden meters tot een
kilometer en gevoelige soorten worden bewust vervaagd. Het is een zoekgebied,
geen vindplaats. "Eigen vondst hier zetten" maakt een pin met status
"nog te bevestigen".

## Voorraadkast en recepten
Een *maaksel* heet vanaf v0.12 een **brouwsel** — in de tekst. De veldnaam
`maaksel:`, de array `MAAKSELS`, `S.maaksels` en de IndexedDB-store `maaksels`
zijn onveranderd gebleven, anders was je hele voorraadkast verdwenen.

16 soorten brouwsel met eigen rijp- en houdbaarheidstermijn, batchcode
`GA-JJMM-NN`.

Op elk potje staat een flesje met de resterende hoeveelheid eronder in woorden
(Vol, Driekwart, Half, Bijna op, Op). Het flesje is een stuk helderder dan eerst
en het dunne voorraadbalkje is weg — twee dingen die hetzelfde vertelden.

Soort brouwsel, restant en waarvoor je het gebruikt zijn keuzelijsten in plaats
van rijen knoppen. Bij "waarvoor" voegt de keuzelijst een chip toe die je weer
kunt weghalen, want dat is er meer dan één. De lijst voor het lijf is van zeven
naar 35 posten gegaan: er is veel meer waar een kruid iets bij kan betekenen dan
hoest, huid en slaap.

### Eigen recepten
Je kunt zelf recepten schrijven: naam, keuken of lijf, tijd, opbrengst,
ingrediënten (één per regel, `hoeveelheid - naam`), werkwijze, een let-op en
zoveel soorten als je wilt. Kies je een soort brouwsel, dan kun je het recept
met één tik in de voorraadkast zetten, net als de ingebouwde recepten.

Ze staan in localStorage onder `admiral_app:eigenrecepten`, gaan mee in de
back-up, staan bovenaan in de lijst met een gouden merkje **eigen**, en hebben
een eigen tabblad. `alleRecepten()` plakt ze voor `RECEPTEN`; `receptZoek()`
kijkt in beide.

78 recepten: 44 keuken en 34 voor het lijf. Nieuw in v0.12 onder meer
hondsdrafazijn, geroosterde beukennootjes, meidoornbessenketchup, ingelegde
speenkruidknoppen, lisdoddestuifmeelkoekjes, vlierbloesemlimonade, veldzuringsoep,
hopscheuten als wilde asperge, berkenbastaftreksel, kaasjeskruid als
koudwateraftreksel, eikenschorsspoeling en vlierbloesembeignets.

## Veldschool
Leitner met zeven trappen, intervallen 0/1/2/4/8/16/32/64 dagen. Drie niveaus:
makkelijk (bekende soorten, drie antwoorden), gemiddeld (alles, vier antwoorden),
moeilijk (giftig en verwarrend, afleiders uit hetzelfde geslacht).

**Om de andere vraag beeld.** Herkennen doe je met je ogen, dus de helft van de
ronde is een foto. Eerst je eigen foto's, dan GBIF.

**Tip na vijf seconden.** Loop je vast, dan verschijnt er een knop die één zetje
geeft. Hij komt niet meteen, want dan is hij te verleidelijk. `tipVoor()` neemt
de tip die de generator zelf meegaf, anders het eerste veldkenmerk, anders de
groep waar de soort in zit — en slaat elke kandidaat over die het antwoord
letterlijk bevat.

### Beeld dat ergens op slaat
Een GBIF-waarneming mag alles zijn: een winterskelet, een herbariumvel, een
bordje met een naam erop. Een dorre pol in februari zegt niets over dragon.
`soortBeeld()` vraagt daarom alleen om waarnemingen uit de maanden waarin de
soort er echt staat (`&month=`), en alleen om waarnemingen die een mens in het
veld deed (`&basisOfRecord=HUMAN_OBSERVATION`). Levert dat minder dan drie
beelden op, dan pas volgt de rest, met het buitenseizoen achteraan.

### Vraagkeuring
`keuring.js` legt elke vraag die de app kan stellen langs zeven meetlatten:
dubbele antwoorden, lege antwoorden, te weinig antwoorden, een antwoord dat niet
tussen de opties staat, een antwoord dat al in de vraag staat, een ontbrekende
tip, en een tip die het antwoord verklapt. Alle drie de niveaus, alle 255
soorten, twee rondes.

Dat vond vier soorten fouten:

- **Naam-vragen die zichzelf beantwoorden.** Taxus/*Taxus baccata*,
  Robinia/*Robinia pseudoacacia*, Narcis/*Narcissus*. `naamVerklikt()` slaat die
  over.
- **Deel-vragen die zichzelf beantwoorden.** Van goudsbloem gebruik je de bloem,
  van mierikswortel de wortel.
- **Verwarringsvragen die zichzelf beantwoorden.** Kapjesmorielje verwar je met
  de morielje.
- **Woordelijk gelijke afleiders.** "Bij een allergie voor composieten
  voorzichtig" staat bij een handvol composieten, dus stonden er twee identieke
  knoppen. `unieke()` ontdubbelt nu op tekst in plaats van op soort.

## Startanimatie
Een rank die uitgroeit tot een volledige omlijsting, met de dryade erin.

Acht stadia van dezelfde tekening liggen precies over elkaar en komen om de
0,30 seconde op, elk met een fade van 0,58s die iets van onderen opkomt. Omdat
elk volgend stadium het vorige overdekt leest de reeks als één doorgroeiende
rank en niet als een diavoorstelling. Tijdlijn:

    0,25s  stadium 1   lage rank langs de onderrand
    0,55s  stadium 2   de rank klimt langs de zijkanten
    0,85s  stadium 3   hoger, nog open bovenaan
    1,15s  stadium 4   de lijst sluit zich, kaal vlechtwerk
    1,45s  stadium 5   eerste blad
    1,75s  stadium 6   voller
    2,05s  stadium 7   vollediger
    2,35s  stadium 8   het volle blad
    2,50s  de dryade verschijnt in de lijst
    2,90s  de lichtjes bij vijzel en flacon gaan aan
    3,05s  de naam, 3,50s de ondertitel
    4,90s  weg, of eerder bij een tik

### Waarom de stadia sluitend passen
`groei.py` snijdt elk bestand bij op wat er echt zichtbaar is en zet het daarna
terug op dezelfde plek in het oorspronkelijke kader van 1024×1536. Zonder die
tweede stap zou elk stadium op zijn eigen bijgesneden maat schalen en zouden de
ranken bij elke wissel verspringen.

### Omvang
Negen illustraties op vol formaat zijn 24 MB. Als PNG met paletreductie nog
altijd 3 MB — te veel om in te lijven. Als WebP op 400 px breed en kwaliteit 55
is het geheel 428 KB, ongeveer 570 KB als data-URI. WebP kan doorschijnende
randen met verloop aan, wat een palet-PNG niet kan; dat scheelt hier een factor
zeven. Netto werd `index.html` zelfs kleiner, omdat de oude lijst en de vorige
kruidenvrouw eruit konden.

## Iconen
Vanaf v0.9 opgebouwd uit de kruidenvrouw en de gouden eikenring, dus uit
dezelfde hand als de rest van de app. `maak_icoon.py` zet haar op een donkere
bosachtergrond met radiale gloed en vignet, geeft haar een zachte slagschaduw,
en legt de eikenring als omlijsting eromheen.

- `icon-512/192.png` — afgeronde vierkant met ring
- `icon-maskable.png` — geen ring, 80% geschaald, zodat er binnen de ronde
  uitsnede van Android niets wegvalt
- `badge-96.png` — nog steeds getekend: een schorskop met geweitakken als kroon
  en worteltakken als baard. Android maakt van de badge een silhouet en gooit
  alle kleur weg, dus een illustratie werkt daar per definitie niet

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

## Indeling van het kaartscherm
**Topbalk** — het eikenmerkteken op 46 px, dezelfde maat als het zegel in de
schermkoppen, met de filterchips ernaast op dezelfde regel.

**Onderaan de kaart** — vier munten op één rij: kaartlaag, ontdekken, thuis, GPS.
Alle vier `.fab.ghost.beeld`, dus alle vier 54 px met hun eigen illustratie.
De thuisknop heeft nu `mun-huis.png` in plaats van een getekend huisje.

**Navigatiebalk** — zes plekken: kaart, vondsten, voorraad, gids, leren,
instellingen. De instellingenmunt zit in een `.tegel`, net als de andere vijf.

### Waarom die knoppen ontspoorden
`#btnLayer` en `#btnSet` hadden al ID-regels met een muntafbeelding, bedoeld voor
de kleine `.iconbtn` in de topbalk. Toen ik die ID's meenam naar de nieuwe
plekken kwamen de munten mee, op een maat die daar niet past: een munt van 54 px
in een navigatiebalk van 32. Vandaar de kolossale, half doorzichtige knoppen.

Les: een ID-regel met een afbeelding reist mee met het ID. Bij het verplaatsen
van een knop hoort de bijbehorende CSS-selector mee te verhuizen, of de knop
hoort een nieuw ID te krijgen.

## Filterchips
`soortVakken()` geeft alle eigenschappen van een soort terug, niet één.
Duizendblad is eetbaar én medicinaal en telde eerder alleen als eetbaar, omdat
`klass()` één etiket teruggeeft — die functie kiest een kleur voor een speld en
moet dus wel één antwoord geven, maar voor tellen en filteren is dat verkeerd.

De GBIF-waarnemingen tellen mee, want die staan ook op de kaart.

Bij het filteren blijft een vondst staan zolang minstens één van zijn
eigenschappen aangevinkt is. Anders zou duizendblad verdwijnen zodra je
"eetbaar" uitzet terwijl je "medicinaal" nog aan hebt.

## Swipe
Horizontaal vegen wisselt van scherm, in de volgorde kaart, vondsten, voorraad,
gids, leren.

Op de kaart staat het uit. Daar betekent slepen pannen, en een verkeerd begrepen
veeg gooit je van je vindplaats af. Verder gelden vier eisen tegelijk, zodat een
schuine of trage sleep binnen een lijst nooit per ongeluk telt: minstens 72 px
horizontaal, binnen 600 ms, horizontaal minstens 2,2 keer zo ver als verticaal,
en niet meer dan 90 px verticaal. Bladen, quiz, loep, invoervelden, segmentknoppen
en de soortenkiezer zijn uitgezonderd.

## Vondstblad
Alles wat de gids over de soort weet staat nu meteen op het vondstblad zelf; de
knop "Alles over …" is weg. Om het in één schermlengte te houden zitten de meeste
onderdelen in uitklapsecties (`klap()`, een `<details>`): wat je gebruikt,
medicinaal gebruik, recepten met deze soort, je andere plekken van die soort, en
beeld uit GBIF. Alleen de veldkenmerken staan open, want dat is wat je in het
veld wilt zien.

Het beeld wordt pas opgehaald als je die sectie openklapt. Anders zou elke
geopende vondst meteen aan het netwerk gaan trekken.

## Loep
Een venster boven het blad (`z-index:700`), niet schermvullend: 92vw bij 74vh met
een rand en een donkere waas eromheen, zodat je ziet waar je vandaan komt.
Knijpen met twee vingers tot 6×, dubbeltik naar 2,6×, terugknop sluit hem.

De CSS voor `#loep` ontbrak volledig — verloren in een van de eerdere
stijlongelukken. Daardoor stond de loep zonder positionering of z-index in de
stroom en verscheen hij achter het blad.

## Afsluiten
De terugknop klimt eerst door alles wat openstaat: loep, quiz, spookpin, blad,
en dan terug naar de kaart. Sta je op de kaart met niets open, dan vraagt de
volgende druk om bevestiging voor je de app verlaat. Zonder die vraag gooi je
jezelf eruit terwijl je alleen een blad wilde sluiten.

## Beginnen waar je bent
Bij het opstarten wordt de kaart op je positie gezet, op minstens zoom 16. Lukt
dat niet binnen zes seconden — geen signaal, geen toestemming — dan blijft het
laatste kaartbeeld staan. Heb je in die tijd al een blad geopend of een speld
gezet, dan springt de kaart niet meer weg.

## Bladen openen
`showSheet()` noteert wanneer het blad opengaat, en de achtergronddoek negeert
klikken in de eerste 400 ms. Zonder die rustperiode sluit een blad dat vanaf de
kaart wordt geopend zichzelf meteen weer: de doek verschijnt onder je vinger en
de klik die volgt op diezelfde aanraking landt er bovenop.

Dat kostte een versie om te vinden, want het blad ging wél open. Het bleef in
de DOM staan, alleen zonder de klasse `on`. De zoekbalk kreeg dus netjes focus
en het toetsenbord kwam op — alleen was er niets te zien. Dat is dezelfde
touchend-gevolgd-door-click-val als bij de spookpin, één laag hoger.

## Soort kiezen
De zoekbalk toont niets zolang je niets hebt getypt. Een willekeurige greep uit
219 soorten helpt niet; je weet zelf wat je gevonden hebt. Bij een nieuwe vondst
krijgt het veld na 320 ms de focus, zodat het toetsenbord meteen opengaat — eerder
focussen wordt tijdens de openingsanimatie van het blad door Android genegeerd.

## Randwerk
Een sierlijst langs de vier schermranden: eikenhoeken in de hoeken, gouden
haarlijnen langs boven, onder, links en rechts. Ligt boven de schermen maar onder
de bladen, en vangt geen tikken op — anders zou hij de kaart blokkeren precies
waar je wilt pinnen. Op het kaartscherm staat hij een stuk terughoudender, daar
telt elke pixel.

## Spookpin
Drie regels, en verder niets:

1. Een tik op de kaart zet een tijdelijke speld neer.
2. Een tik **op** die speld opent het formulier voor een nieuwe vondst. Pas
   **Bewaren** slaat hem op.
3. Een tik ergens anders haalt de oude speld weg en zet een nieuwe op die plek.
   Er staat er dus altijd hoogstens één.

De speld overleeft niets: van scherm wisselen, de terugknop, de app naar de
achtergrond of afsluiten — hij is weg. Hij komt nooit in `S.pins` of IndexedDB.

Twee dingen gingen hier achtereenvolgens mis. In v0.11 riep de tikafhandeling
op de speld `newPin()` aan in plaats van `nieuweVondst()`; `newPin` schrijft
direct naar IndexedDB, dus elke tik maakte meteen een naamloze vondst aan.
In v0.12.0 was dat opgelost, maar toen sloeg de speld stap 1 en 2 over: hij
verschijnt precies onder je vinger, dus de klik die volgt op dezelfde aanraking
landt er meteen bovenop en opende het formulier.

Daarom negeert de speld nu elke tik binnen 500 ms na zijn geboorte. Pas een
échte tweede aanraking opent het formulier. Het uitlegwolkje is weg; het gedrag
spreekt voor zich.

## Veldschool
Leitner, dozen 0–7, intervallen 0/1/2/4/8/16/32/64 dagen. Zeven vraagsoorten:
NL↔Latijn, verwarringsgevaar, let-op-regel, veldkenmerk, plantdeel, oogstmaand,
en vanaf drie gefotografeerde soorten herkenning op je eigen foto's.
Weging: eigen plekken > gifplanten > paddenstoelen > eerder foute antwoorden.

## Dagelijkse herinnering
Periodic Background Sync (`wildpluk-dagelijks`, min. 6 u). Werkt alleen als de app
op het startscherm staat. Chrome bepaalt het exacte moment; marge van ongeveer een uur.

## Geïllustreerde assets
Alle sierbeeld komt uit de aangeleverde illustraties. Er zit geen getekend
lijnwerk meer tussen; dat was precies wat de app een gemengd gevoel gaf.

`vrij.py` doet de voorbewerking: bijsnijden op de zichtbare inhoud, schalen naar
de maat waarop iets werkelijk getoond wordt, en het palet terugbrengen. Bij dat
laatste worden de RGB-waarden onder volledig transparante pixels eerst met de
gemiddelde zichtbare kleur gevuld — anders trekt die rommel het palet scheef en
krijg je vuile randen.

Van 42 aangeleverde stukken zijn er 24 in gebruik:

| waar | beeld |
|---|---|
| kaartlaag, instellingen, ontdekken, sluiten, plus | gouden penningen |
| back-up en herstel | penning met pijl |
| GPS-knop en kaartspelden | eikenspeld |
| navigatie | speld, mand, flacon, open boek, gesloten boek |
| schermkop | boommedaillon en een vlechtlijn met boom |
| sectiekop in een blad | fijne eikenlijn, plus vijzel, ketel of sikkel waar dat past |
| groepskop | vlechtlijn |
| hoeken van elk blad | eikenhoek, vier keer gespiegeld |
| kaarten in lijsten | dezelfde hoek, klein en vervaagd |
| lege schermen | mand of open boek |
| voorraadpotjes | flacon, amber gefilterd voor droge maaksels |
| kwalen | gereedschap per groep |
| maanstand | maan in de gouden eikenring |
| startscherm | kruidenvrouw in de gotische lijst |

De kaartspeld draagt de soortklasse niet meer in zijn vorm maar in een gekleurde
gloed eromheen en een steentje in de kop. Zo blijft één illustratie voldoende
voor eetbaar, medicinaal, giftig en zwam.

Waar geen passend pictogram bestond staat er niets. Een half passend beeld is
erger dan geen beeld.

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
De kruidenvrouw in de gotische lijst. In lagen:
- de lijst komt op en schaalt van 94% naar 100%
- de vrouw verschijnt daarna en ademt heel licht door, 6 s per cyclus
- een groene gloed pulseert over de flacon in haar linkerhand, 3,2 s
- een gouden gloed pulseert trager over de vijzel, 4,4 s
- veertien sporen stijgen op vanaf willekeurige punten, elk met eigen duur,
  vertraging en zijwaartse drift
- daarna GAEA, een uitrollende vlechtlijn en de ondertitel

Ongeveer 3,4 s. Tikken slaat het over; bij `prefers-reduced-motion` staat alles
stil en verdwijnt het scherm na 0,9 s.

De vrouw zit als JPEG in de app, samengesteld op een donkere bosachtergrond.
Transparantie is daar niet nodig en dat scheelt een factor zes: 105 kB in plaats
van 600 kB.

## Iconen
Vanaf v0.9 opgebouwd uit de kruidenvrouw en de gouden eikenring, dus uit
dezelfde hand als de rest van de app. `maak_icoon.py` zet haar op een donkere
bosachtergrond met radiale gloed en vignet, geeft haar een zachte slagschaduw,
en legt de eikenring als omlijsting eromheen.

- `icon-512/192.png` — afgeronde vierkant met ring
- `icon-maskable.png` — geen ring, 80% geschaald, zodat er binnen de ronde
  uitsnede van Android niets wegvalt
- `badge-96.png` — nog steeds getekend: een schorskop met geweitakken als kroon
  en worteltakken als baard. Android maakt van de badge een silhouet en gooit
  alle kleur weg, dus een illustratie werkt daar per definitie niet

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

## Kaartknoppen
Alle knoppen staan op één rij onderaan de kaart, gecentreerd boven de
navigatiebalk. Rechtsonder was hinderlijk bij het navigeren. De knop "Pin hier"
is weg: een vondst begint bij de spookpin.

## Randwerk
Een sierlijst langs de vier schermranden: eikenhoeken in de hoeken, gouden
haarlijnen langs boven, onder, links en rechts. Ligt boven de schermen maar onder
de bladen, en vangt geen tikken op — anders zou hij de kaart blokkeren precies
waar je wilt pinnen. Op het kaartscherm staat hij een stuk terughoudender, daar
telt elke pixel.

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


## Jaarwiel
Acht stations met hun gangbare volksnamen: Yule, Imbolc, Ostara, Beltane, Litha,
Lughnasadh, Mabon, Samhain. Waar een Nederlandse naam bestaat staat die erbij in
het bijschrift — midwinter, lichtmis, lente-evening, meifeest, midzomer,
herfst-evening. Lammas heette in v0.15 nog met zijn Angelsaksische kerknaam; dat
is nu Lughnasadh.


## Een val in proef.js zelf
De keuringen stonden eerst in een template literal binnen `proef.js`. Daar wordt
`\s` stilletjes `s`, dus `/\s+/g` werd `/s+/g` en haalde elke letter s uit de
tekst. Dat gaf vals alarm op "hysop" in "hyssopus". De keuringen staan nu in
`keuring.js` en worden met `readFileSync` ingelezen, zodat er niets meer aan de
broncode geknabbeld wordt.
