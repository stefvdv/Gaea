"""Snijdt de aangeleverde sheets in losse assets.
Werkwijze: alfamasker -> licht dichtsmeren zodat losse blaadjes bij hun ornament
horen -> samenhangende gebieden labelen -> bijsnijden -> op maat wegschrijven."""

import os, json
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "art_src"
UIT = "art"
os.makedirs(UIT, exist_ok=True)


def masker(im, dicht=6, drempel=18):
    a = np.array(im.convert("RGBA"))
    m = a[..., 3] > drempel
    if dicht:
        m = ndimage.binary_closing(m, structure=np.ones((dicht, dicht)))
        m = ndimage.binary_dilation(m, structure=np.ones((dicht, dicht)))
    return m


def stukken(pad, dicht=6, minopp=2500, marge=4):
    im = Image.open(pad).convert("RGBA")
    m = masker(im, dicht)
    lab, n = ndimage.label(m)
    uit = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < minopp:
            continue
        y0, y1 = max(0, ys.min() - marge), min(im.height, ys.max() + marge + 1)
        x0, x1 = max(0, xs.min() - marge), min(im.width, xs.max() + marge + 1)
        stuk = im.crop((x0, y0, x1, y1))
        uit.append(((x0, y0, x1 - x0, y1 - y0), stuk))
    # links naar rechts, boven naar beneden
    uit.sort(key=lambda t: (round(t[0][1] / 60), t[0][0]))
    return uit


def bewaar(stuk, naam, maxbr=None, maxho=None, kwal=None):
    im = stuk
    if maxbr and im.width > maxbr:
        im = im.resize((maxbr, max(1, round(im.height * maxbr / im.width))), Image.LANCZOS)
    if maxho and im.height > maxho:
        im = im.resize((max(1, round(im.width * maxho / im.height)), maxho), Image.LANCZOS)
    im = im.convert("RGBA")
    # kwantiseren met behoud van alfa scheelt fors in bestandsgrootte
    if kwal:
        rgb = im.convert("RGB").quantize(colors=kwal, method=Image.MEDIANCUT).convert("RGBA")
        rgb.putalpha(im.split()[3])
        im = rgb
    pad = os.path.join(UIT, naam + ".png")
    im.save(pad, optimize=True)
    return pad, im.size


if __name__ == "__main__":
    verslag = {}
    for sheet, dicht, minopp in [("lijnen", 8, 6000), ("hoeken", 8, 3500),
                                 ("knoppen", 6, 6000), ("tegels", 6, 12000),
                                 ("frames", 8, 20000)]:
        st = stukken(os.path.join(SRC, sheet + ".png"), dicht=dicht, minopp=minopp)
        verslag[sheet] = [(b, s.size) for b, s in st]
        print(sheet, "->", len(st), "stukken")
        for i, (b, s) in enumerate(st):
            print("   ", i, b, s.size)
    json.dump({k: [[list(b), list(sz)] for b, sz in v] for k, v in verslag.items()},
              open("art_index.json", "w"), indent=1)
