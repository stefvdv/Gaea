"""Verwerkt aangeleverde losse illustraties voor gebruik in de app.

De bestanden hebben al een alfakanaal, dus er wordt niets weggesneden.
Wel: bijsnijden op de zichtbare inhoud, schalen, en het palet terugbrengen.

Let op bij kwantiseren: de RGB-waarden onder volledig transparante pixels zijn
rommel. Die worden eerst met de gemiddelde zichtbare kleur gevuld, anders trekt
die rommel het palet scheef en krijg je vuile randen.
"""

import os
import numpy as np
from PIL import Image


def opschonen(pad, marge=4):
    im = Image.open(pad).convert("RGBA")
    bb = im.split()[3].point(lambda v: 255 if v > 6 else 0).getbbox()
    if bb:
        x0, y0, x1, y1 = bb
        im = im.crop((max(0, x0 - marge), max(0, y0 - marge),
                      min(im.width, x1 + marge), min(im.height, y1 + marge)))
    return im


def bewaar(im, naam, map_uit="art_nieuw", maxbr=None, maxho=None, kleuren=None):
    os.makedirs(map_uit, exist_ok=True)
    if maxbr and im.width > maxbr:
        im = im.resize((maxbr, max(1, round(im.height * maxbr / im.width))), Image.LANCZOS)
    if maxho and im.height > maxho:
        im = im.resize((max(1, round(im.width * maxho / im.height)), maxho), Image.LANCZOS)
    im = im.convert("RGBA")
    if kleuren:
        a = np.array(im)
        alpha = a[..., 3]
        zicht = alpha > 24
        if zicht.any():
            gem = a[..., :3][zicht].mean(axis=0)
            rgb = a[..., :3].astype(float)
            rgb[~zicht] = gem
            schoon = Image.fromarray(rgb.astype(np.uint8), "RGB")
        else:
            schoon = im.convert("RGB")
        q = schoon.quantize(colors=kleuren, method=Image.MEDIANCUT).convert("RGBA")
        q.putalpha(Image.fromarray(alpha))
        im = q
    pad = os.path.join(map_uit, naam + ".png")
    im.save(pad, optimize=True)
    return pad, im.size, os.path.getsize(pad)
