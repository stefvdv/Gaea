"""Gaea — app-iconen.

De kruidenvrouw en de gouden eikenring uit de aangeleverde illustraties
vormen samen het icoon. Zo is het icoon uit dezelfde hand als alles in de app.

De meldingsbadge blijft getekend: Android maakt daar een silhouet van en gooit
alle kleur weg, dus een illustratie werkt daar per definitie niet.
"""

import math, os
from PIL import Image, ImageDraw, ImageFilter

VROUW = "art_nieuw/kruidenvrouw.png"
RING = "art_nieuw/ring-eikel.png"
NACHT = (10, 20, 14)
BOS = (30, 50, 36)
BOS_L = (48, 74, 52)


def icoon(S, ring=True, rond=True, krimp=1.0, kleuren=96):
    W = S * 3
    im = Image.new("RGBA", (W, W), NACHT + (255,))

    gl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(gl)
    d.ellipse([W*.02, -W*.12, W*.98, W*.82], fill=BOS + (255,))
    d.ellipse([W*.16, W*.00, W*.84, W*.66], fill=BOS_L + (225,))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(W*.09)))

    vg = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dv = ImageDraw.Draw(vg)
    dv.rectangle([0, 0, W, W], fill=(0, 0, 0, 175))
    dv.ellipse([W*.03, W*.00, W*.97, W*.94], fill=(0, 0, 0, 0))
    im.alpha_composite(vg.filter(ImageFilter.GaussianBlur(W*.08)))

    vr = Image.open(VROUW).convert("RGBA")
    f = W * (0.80 if ring else 0.86) * krimp / max(vr.size)
    vr = vr.resize((max(1, round(vr.width*f)), max(1, round(vr.height*f))), Image.LANCZOS)
    sch = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sil = Image.new("RGBA", vr.size, (0, 0, 0, 150)); sil.putalpha(vr.split()[3])
    sch.alpha_composite(sil, ((W-vr.width)//2 + int(W*.008), int(W*.50 - vr.height*.5) + int(W*.014)))
    im.alpha_composite(sch.filter(ImageFilter.GaussianBlur(W*.016)))
    im.alpha_composite(vr, ((W-vr.width)//2, int(W*.50 - vr.height*.5)))

    if ring:
        rg = Image.open(RING).convert("RGBA")
        rw = int(W*0.985)
        rg = rg.resize((rw, max(1, round(rg.height*rw/rg.width))), Image.LANCZOS)
        rs = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        sil = Image.new("RGBA", rg.size, (0, 0, 0, 140)); sil.putalpha(rg.split()[3])
        rs.alpha_composite(sil, ((W-rg.width)//2 + int(W*.006), (W-rg.height)//2 + int(W*.010)))
        im.alpha_composite(rs.filter(ImageFilter.GaussianBlur(W*.012)))
        im.alpha_composite(rg, ((W-rg.width)//2, (W-rg.height)//2))

    if rond:
        mk = Image.new("L", (W, W), 0)
        ImageDraw.Draw(mk).rounded_rectangle([0, 0, W, W], radius=W*.215, fill=255)
        im.putalpha(mk)

    im = im.resize((S, S), Image.LANCZOS)
    q = im.convert("RGB").quantize(colors=kleuren, method=Image.MEDIANCUT).convert("RGBA")
    q.putalpha(im.split()[3])
    return q


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


def tak(d, p0, p1, w0, w1, kleur, n=18):
    """Tapse tak van p0 naar p1, licht gebogen."""
    mx = (p0[0] + p1[0]) / 2 + (p1[1] - p0[1]) * 0.10
    my = (p0[1] + p1[1]) / 2 - (p1[0] - p0[0]) * 0.10
    pts = bocht(p0, (mx, my), p1, n)
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 1)
        w = w0 + (w1 - w0) * t
        d.line([pts[i], pts[i + 1]], fill=kleur, width=max(1, int(w)))
        d.ellipse([pts[i + 1][0] - w / 2, pts[i + 1][1] - w / 2,
                   pts[i + 1][0] + w / 2, pts[i + 1][1] + w / 2], fill=kleur)
    return pts


def badge(S=96):
    """Meldingsbadge: een dryadekop van takken.
    Android maakt hier een silhouet van en gooit alle kleur weg, dus het moet
    één gesloten witte vorm zijn met uitgesneden ogen, neus en mond."""
    W = S * SS
    im = laag(W)
    d = ImageDraw.Draw(im)
    cx = W / 2
    wit = (255, 255, 255, 255)
    leeg = (0, 0, 0, 0)

    # ---- geweitakken als kroon ----
    kruin = (cx, W * .455)
    for hoek, lengte, dikte in [(-90, .300, .062), (-119, .282, .056), (-61, .282, .056),
                                (-147, .240, .046), (-33, .240, .046)]:
        r = math.radians(hoek)
        eind = (cx + math.cos(r) * W * lengte, kruin[1] + math.sin(r) * W * lengte)
        pts = tak(d, (cx, kruin[1] + W * .02), eind, W * dikte, W * dikte * .34, wit)
        # zijtwijgen halverwege
        for f, zij in ((.58, 1),):
            i = int(len(pts) * f)
            bas = pts[i]
            zr = r + zij * .62
            tip = (bas[0] + math.cos(zr) * W * lengte * .34,
                   bas[1] + math.sin(zr) * W * lengte * .34)
            tak(d, bas, tip, W * dikte * .58, W * dikte * .22, wit, n=10)

    # ---- baard van takken ----
    for hoek, lengte, dikte in [(99, .195, .046), (81, .195, .046),
                                (126, .155, .038), (54, .155, .038)]:
        r = math.radians(hoek)
        bas = (cx + math.cos(r) * W * .085, W * .705 + math.sin(r) * W * .045)
        eind = (bas[0] + math.cos(r) * W * lengte, bas[1] + math.sin(r) * W * lengte)
        pts = tak(d, bas, eind, W * dikte, W * dikte * .30, wit)
        i = int(len(pts) * .60)
        zr = r + (.55 if hoek < 90 else -.55)
        tak(d, pts[i], (pts[i][0] + math.cos(zr) * W * lengte * .38,
                        pts[i][1] + math.sin(zr) * W * lengte * .38),
            W * dikte * .55, W * dikte * .20, wit, n=10)

    # ---- kop: gesloten vorm die de takken verbindt ----
    fw, fh = W * .40, W * .50
    fy = W * .580
    d.polygon(gezichtsvorm(cx, fy, fw, fh), fill=wit)
    d.ellipse([cx - W * .185, W * .405, cx + W * .185, W * .775], fill=wit)

    # ---- uitsnedes ----
    ow, oh = fw * .28, fh * .13
    oy = fy - fh * .07
    for zij in (-1, 1):
        d.polygon(eikprofiel(cx + zij * fw * .225, oy, math.radians(-5 * zij), ow, oh, lobben=0), fill=leeg)
    d.polygon([(cx, fy + fh * .015), (cx + fw * .068, fy + fh * .175),
               (cx - fw * .068, fy + fh * .175)], fill=leeg)
    d.line(bocht((cx - fw * .175, fy + fh * .275), (cx, fy + fh * .360), (cx + fw * .155, fy + fh * .270)),
           fill=leeg, width=max(3, int(W * .020)), joint="curve")
    # groeven in de wangen, geeft het schorsgevoel
    for zij in (-1, 1):
        d.line(bocht((cx + zij * fw * .40, fy - fh * .10),
                     (cx + zij * fw * .46, fy + fh * .08),
                     (cx + zij * fw * .33, fy + fh * .26)),
               fill=leeg, width=max(2, int(W * .011)), joint="curve")
    return im.resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    icoon(512, kleuren=72).save("icon-512.png", optimize=True)
    icoon(192, kleuren=96).save("icon-192.png", optimize=True)
    icoon(512, ring=False, krimp=.80, kleuren=64).save("icon-maskable.png", optimize=True)
    badge(96).save("badge-96.png")
    print("iconen klaar")
