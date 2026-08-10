"""
snijranken.py — haalt het wit weg en snijdt de vellen in losse ranken.

Het wit wegnemen op helderheid alleen zou de bleke huid van de dryade half
doorzichtig maken. Daarom eerst een vulling vanaf de rand: alleen wit dat
aaneengesloten met de buitenrand verbonden is telt als achtergrond. Binnen een
smalle band langs die achtergrond wordt de dekking daarna alsnog met de
helderheid verzacht, zodat de pluizige uiteinden van de ranken niet als een
uitgeknipte kartelrand eindigen.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import os

BRON = "/mnt/user-data/uploads/"
os.makedirs("rank_tegels", exist_ok=True)


def vrijmaken(im, wit=232, band=4, zacht=48):
    """RGBA terug met echte alfa; wit dat aan de rand vastzit verdwijnt."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

    licht = lum > wit
    # alleen het lichte dat met de buitenrand verbonden is, is achtergrond
    merk, _ = ndimage.label(licht)
    randmerken = set(merk[0, :]) | set(merk[-1, :]) | set(merk[:, 0]) | set(merk[:, -1])
    randmerken.discard(0)
    achter = np.isin(merk, list(randmerken))

    alfa = np.where(achter, 0.0, 1.0)

    # binnen een band langs de achtergrond de dekking met de helderheid verzachten
    dichtbij = ndimage.binary_dilation(achter, iterations=band) & ~achter
    ramp = np.clip((wit + 12 - lum) / zacht, 0.0, 1.0)
    alfa = np.where(dichtbij, np.minimum(alfa, ramp), alfa)
    alfa = ndimage.gaussian_filter(alfa, 0.6)

    uit = np.dstack([a, np.clip(alfa * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(uit, "RGBA")


def tegels(im, kolommen, rijen, minopp=1500):
    """Snijdt een vel in een raster en levert per cel de bijgesneden inhoud."""
    b, h = im.size
    uit = []
    for r in range(rijen):
        for k in range(kolommen):
            cel = im.crop((k * b // kolommen, r * h // rijen,
                           (k + 1) * b // kolommen, (r + 1) * h // rijen))
            vak = cel.split()[3].point(lambda x: 255 if x > 24 else 0).getbbox()
            if not vak:
                continue
            knip = cel.crop(vak)
            if knip.size[0] * knip.size[1] < minopp:
                continue
            uit.append(((r, k), knip))
    return uit


VELLEN = [
    ("ChatGPT_Image_7_aug_2026__21_41_01__4_.png", "a", 2, 6),   # kleine onderstukken
    ("ChatGPT_Image_7_aug_2026__21_41_01__3_.png", "b", 4, 5),   # groeiend naar hoekvorm
    ("ChatGPT_Image_7_aug_2026__21_41_01__2_.png", "c", 2, 4),   # grote hoeken
    ("ChatGPT_Image_7_aug_2026__21_41_01__1_.png", "d", 2, 6),   # onderlijst met hoeken
]

for bestand, merk, kol, rij in VELLEN:
    im = vrijmaken(Image.open(BRON + bestand))
    gevonden = tegels(im, kol, rij)
    for (r, k), knip in gevonden:
        naam = f"rank_tegels/{merk}{r}{k}.png"
        knip.save(naam)
    print(f"{bestand[-10:]}  {merk}: {len(gevonden)} tegels, "
          f"maten {sorted(set(t.size for _, t in gevonden))[:3]}…")

# de dryade blijft heel
dry = vrijmaken(Image.open(BRON + "ChatGPT_Image_7_aug_2026__21_42_21.png"))
vak = dry.split()[3].point(lambda x: 255 if x > 24 else 0).getbbox()
dry.crop(vak).save("rank_tegels/dryade.png")
print("dryade:", dry.crop(vak).size)
