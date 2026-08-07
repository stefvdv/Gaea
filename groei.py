"""
groei.py — verwerkt de acht groeistadia plus de dryade tot lichte PNG's.

De aangeleverde bestanden zijn 1024×1536 met alfa. Ze zijn te groot om acht
keer in te lijven, dus:
  1. bijsnijden op wat écht zichtbaar is (alfa > 8);
  2. terugzetten in het oorspronkelijke kader, zodat alle acht stadia over
     elkaar heen passen — dat is de hele truc van de animatie;
  3. schalen naar een breedte die op een telefoon scherp genoeg is;
  4. paletreductie met behoud van transparantie.

Onder een transparante pixel zit vaak rommel in de RGB-kanalen. Die kleurt mee
bij het reduceren, dus die vullen we eerst met de gemiddelde zichtbare kleur.
"""
import os
from PIL import Image

BRON = "/mnt/user-data/uploads/"
UIT = "art_groei"
os.makedirs(UIT, exist_ok=True)

# volgorde zoals aangeleverd: van kleine rank tot volle lijst, dan de dryade
REEKS = [
    ("1000007605.png", "groei1", 560, 72),
    ("1000007606.png", "groei2", 560, 72),
    ("1000007607.png", "groei3", 560, 72),
    ("1000007608.png", "groei4", 560, 80),
    ("1000007609.png", "groei5", 560, 80),
    ("1000007610.png", "groei6", 560, 88),
    ("1000007611.png", "groei7", 560, 88),
    ("1000007612.png", "groei8", 560, 96),
    ("1000007613.png", "dryade", 470, 128),
]


def vul_transparant(im):
    """Gemiddelde zichtbare kleur onder de transparante pixels zetten."""
    px = im.load()
    b, h = im.size
    som = [0, 0, 0]
    n = 0
    for y in range(0, h, 4):
        for x in range(0, b, 4):
            r, g, bl, a = px[x, y]
            if a > 40:
                som[0] += r
                som[1] += g
                som[2] += bl
                n += 1
    gem = tuple(s // n for s in som) if n else (150, 140, 90)
    for y in range(h):
        for x in range(b):
            r, g, bl, a = px[x, y]
            if a < 8:
                px[x, y] = (gem[0], gem[1], gem[2], 0)
    return im


for bestand, naam, breed, kleuren in REEKS:
    im = Image.open(BRON + bestand).convert("RGBA")
    kader = im.size

    # bijsnijden op zichtbare inhoud, dan terug in hetzelfde kader plakken
    vak = im.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox()
    if vak:
        knip = im.crop(vak)
        leeg = Image.new("RGBA", kader, (0, 0, 0, 0))
        leeg.paste(knip, (vak[0], vak[1]))
        im = leeg

    hoog = round(breed * kader[1] / kader[0])
    im = im.resize((breed, hoog), Image.LANCZOS)
    im = vul_transparant(im)

    alfa = im.split()[3]
    plat = im.convert("RGB").quantize(colors=kleuren, method=Image.MEDIANCUT)
    plat = plat.convert("RGBA")
    plat.putalpha(alfa)
    plat.save(f"{UIT}/{naam}.png", optimize=True)
    kb = os.path.getsize(f"{UIT}/{naam}.png") / 1024
    print(f"{naam:8s} {breed}x{hoog}  {kb:6.1f} KB")

totaal = sum(os.path.getsize(f"{UIT}/{n}.png") for _, n, _, _ in REEKS) / 1024
print(f"\ntotaal {totaal:.0f} KB, als data-URI ongeveer {totaal*1.34:.0f} KB")
