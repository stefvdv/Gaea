"""Gaea — app-iconen.

De kop van de kruidenvrouw uit het aangeleverde portret vormt het icoon.
Het origineel is te fijn voor 48 dp, dus het beeld wordt getemperd: mediaan
tegen ruis, licht verzachten, heel licht verscherpen zodat de vormen blijven.
Daaroverheen een vignet, een gouden ring en de flacon linksonder.

De meldingsbadge blijft getekend: Android maakt daar een silhouet van en gooit
alle kleur weg, dus een foto werkt daar per definitie niet.
"""

import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import numpy as np

BRON_PORTRET = "art_src/druide.png"
BRON_FLACON = "art/fl-groen.png"

NACHT = (10, 18, 14)
BOS = (26, 44, 33)
GOUD_D = (120, 92, 24)
GOUD = (186, 150, 52)
GOUD_L = (232, 206, 128)

# uitsnede rond de kop, als fractie van het portret
UITSNEDE = (0.310, 0.105, 0.750, 0.353)


def A(c, a=255):
    return (c[0], c[1], c[2], a)


def meng(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def kop(S):
    im = Image.open(BRON_PORTRET).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = UITSNEDE
    im = im.crop((int(W * x0), int(H * y0), int(W * x1), int(H * y1)))
    # vierkant maken op de breedte
    z = min(im.width, im.height)
    im = im.crop(((im.width - z) // 2, 0, (im.width - z) // 2 + z, z))
    im = im.resize((S, S), Image.LANCZOS)

    # detail temperen zodat het op 48 dp nog leest
    im = im.filter(ImageFilter.MedianFilter(3 if S < 300 else 5))
    im = im.filter(ImageFilter.GaussianBlur(S / 900))
    im = im.filter(ImageFilter.UnsharpMask(radius=S / 200, percent=60, threshold=3))
    im = ImageEnhance.Color(im).enhance(0.92)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    return im


def vignet(im, sterkte=1.45):
    w, h = im.size
    a = np.array(im).astype(float)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w * .5) / (w * .58)) ** 2 + ((yy - h * .44) / (h * .58)) ** 2)
    v = np.clip(1 - sterkte * np.clip(r - .38, 0, None) ** 1.25, 0.03, 1)
    a *= v[..., None]
    # de donkere randen naar het bosgroen van de app trekken
    doel = np.array(BOS, dtype=float)
    m = np.clip((r - .62) * 1.4, 0, 1)[..., None]
    a = a * (1 - m * .80) + doel * m * .80
    # het hele beeld iets dieper, zodat het icoon niet uit de rij springt
    a *= 0.94
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def ring(im, band_frac=.036, straal_frac=.424):
    W = im.width
    laag = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(laag)
    cx = cy = W / 2
    r = W * straal_frac
    band = W * band_frac
    lw = max(2, int(band * .52))
    sch = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sch)
    for rr, alpha in ((r, 240), (r - band * .78, 150)):
        ds.ellipse([cx - rr + W * .005, cy - rr + W * .007, cx + rr + W * .005, cy + rr + W * .007],
                   outline=(0, 0, 0, 150), width=lw)
        for i in range(300):
            a0 = i / 300 * 2 * math.pi
            a1 = (i + 1.4) / 300 * 2 * math.pi
            t = (math.cos(a0 - math.radians(-135)) + 1) / 2
            d.line([(cx + math.cos(a0) * rr, cy + math.sin(a0) * rr),
                    (cx + math.cos(a1) * rr, cy + math.sin(a1) * rr)],
                   fill=A(meng(GOUD_D, GOUD_L, t * .92 + .04), alpha), width=lw)
    for a in (0, 90, 180, 270):
        ra = math.radians(a)
        kx, ky = cx + math.cos(ra) * (r - band * .39), cy + math.sin(ra) * (r - band * .39)
        rr = band * .92
        d.ellipse([kx - rr, ky - rr, kx + rr, ky + rr], fill=A(meng(GOUD, GOUD_L, .4), 235))
        d.ellipse([kx - rr * .40, ky - rr * .40, kx + rr * .40, ky + rr * .40], fill=A(GOUD_D, 235))
    im = im.convert("RGBA")
    im.alpha_composite(sch.filter(ImageFilter.GaussianBlur(W * .006)))
    im.alpha_composite(laag)
    return im


def flacon(im, frac=.345, pos=(.205, .715)):
    W = im.width
    fl = Image.open(BRON_FLACON).convert("RGBA")
    h = int(W * frac)
    fl = fl.resize((max(1, round(fl.width * h / fl.height)), h), Image.LANCZOS)
    x = int(W * pos[0] - fl.width / 2)
    y = int(W * pos[1] - fl.height / 2)
    # gloed erachter
    gl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dg = ImageDraw.Draw(gl)
    r = fl.width * .95
    dg.ellipse([x + fl.width / 2 - r, y + fl.height * .62 - r,
                x + fl.width / 2 + r, y + fl.height * .62 + r], fill=(126, 196, 122, 120))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(W * .035)))
    sch = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sch.alpha_composite(fl, (x + int(W * .006), y + int(W * .008)))
    sch = Image.new("RGBA", (W, W), (0, 0, 0, 0)).convert("RGBA")
    d = ImageDraw.Draw(sch)
    im.alpha_composite(fl, (x, y))
    return im


def compact(im, kleuren=128):
    """Palet terugbrengen met behoud van transparantie; scheelt fors in bytes."""
    im = im.convert("RGBA")
    q = im.convert("RGB").quantize(colors=kleuren, method=Image.MEDIANCUT).convert("RGBA")
    q.putalpha(im.split()[3])
    return q


def afronden(im, radius_frac=.215):
    W = im.width
    masker = Image.new("L", (W, W), 0)
    ImageDraw.Draw(masker).rounded_rectangle([0, 0, W, W], radius=W * radius_frac, fill=255)
    uit = Image.new("RGBA", (W, W), A(NACHT))
    uit.alpha_composite(im.convert("RGBA"))
    uit.putalpha(masker)
    return uit


def icoon(S, met_ring=True, met_flacon=True, rond=True, krimp=1.0):
    W = S * 3
    im = vignet(kop(W))
    im = im.convert("RGBA")
    if met_ring:
        im = ring(im)
    if met_flacon:
        im = flacon(im)
    if krimp != 1.0:
        n = int(W * krimp)
        klein = im.resize((n, n), Image.LANCZOS).convert("RGBA")
        # zachte ronde rand, anders zie je in de ronde uitsnede van Android
        # de vierkante rand van de foto liggen
        mk = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mk).ellipse([n * .02, n * .02, n * .98, n * .98], fill=255)
        mk = mk.filter(ImageFilter.GaussianBlur(n * .06))
        klein.putalpha(ImageChops.multiply(klein.split()[3], mk))
        im = Image.new("RGBA", (W, W), A(BOS))
        gl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse([W * .18, W * .18, W * .82, W * .82], fill=(44, 68, 49, 220))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(W * .06)))
        im.alpha_composite(klein, ((W - n) // 2, (W - n) // 2))
    if rond:
        im = afronden(im)
    else:
        vlak = Image.new("RGBA", (W, W), A(NACHT))
        vlak.alpha_composite(im)
        im = vlak
    return im.resize((S, S), Image.LANCZOS)


# ---- meldingsbadge: getekend silhouet, want Android gooit de kleur eruit ----
SS = 6


def laag(W):
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def bocht(p0, p1, p2, n=24):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1])
            for t in [i/n for i in range(n+1)]]


def bocht3(p0, p1, p2, p3, n=30):
    return [((1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0],
             (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1])
            for t in [i/n for i in range(n+1)]]


def eikprofiel(cx, cy, ang, ln, wd, lobben=0, n=160):
    boven, onder = [], []
    for i in range(n + 1):
        t = i / n
        x = -ln/2 + ln*t
        romp = math.sin(math.pi * t) ** 0.72
        lob = 1 + (0.075 * math.sin(t * math.pi * lobben * 2 - math.pi/2) if lobben else 0)
        y = romp * (wd/2) * lob * (1 - 0.30*(t - .5))
        boven.append((x, y)); onder.append((x, -y))
    pts = boven + onder[::-1]
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x*ca - y*sa, cy + x*sa + y*ca) for x, y in pts]


def gezichtsvorm(cx, fy, fw, fh):
    return (bocht3((cx - fw*.50, fy - fh*.18), (cx - fw*.53, fy + fh*.28),
                   (cx - fw*.27, fy + fh*.55), (cx, fy + fh*.60)) +
            bocht3((cx, fy + fh*.60), (cx + fw*.27, fy + fh*.55),
                   (cx + fw*.53, fy + fh*.28), (cx + fw*.50, fy - fh*.18)) +
            bocht3((cx + fw*.50, fy - fh*.18), (cx + fw*.50, fy - fh*.58),
                   (cx - fw*.50, fy - fh*.58), (cx - fw*.50, fy - fh*.18)))


def badge(S=96):
    W = S*SS
    im = laag(W); d = ImageDraw.Draw(im)
    cx = W/2
    wit = (255, 255, 255, 255); leeg = (0, 0, 0, 0)
    d.ellipse([cx - W*.215, W*.345, cx + W*.215, W*.795], fill=wit)
    for a, dist, ln, wd in [(-90, .205, .30, .125), (-115, .205, .275, .112),
                            (-65, .205, .275, .112), (-142, .190, .235, .098),
                            (-38, .190, .235, .098)]:
        r = math.radians(a)
        d.polygon(eikprofiel(cx + math.cos(r)*W*dist, W*.455 + math.sin(r)*W*dist*.80,
                             r, W*ln, W*wd, lobben=3), fill=wit)
    fw, fh = W*.42, W*.48
    fy = W*.585
    d.polygon(gezichtsvorm(cx, fy, fw, fh), fill=wit)
    for zij in (-1, 1):
        d.polygon(eikprofiel(cx + zij*fw*.225, fy - fh*.055, 0, fw*.27, fh*.135, lobben=0), fill=leeg)
    d.polygon([(cx, fy + fh*.015), (cx + fw*.06, fy + fh*.165), (cx - fw*.06, fy + fh*.165)], fill=leeg)
    d.line(bocht((cx - fw*.17, fy + fh*.265), (cx, fy + fh*.345), (cx + fw*.17, fy + fh*.265)),
           fill=leeg, width=max(3, int(W*.021)), joint="curve")
    return im.resize((S, S), Image.LANCZOS)




if __name__ == "__main__":
    compact(icoon(512), 96).save("icon-512.png", optimize=True)
    compact(icoon(192), 96).save("icon-192.png", optimize=True)
    compact(icoon(512, met_ring=False, met_flacon=False, rond=False, krimp=.66), 80) \
        .save("icon-maskable.png", optimize=True)
    badge(96).save("badge-96.png")
    print("iconen klaar")
