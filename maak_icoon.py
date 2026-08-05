import math
from PIL import Image, ImageDraw, ImageFilter

SS = 8  # supersampling

BOS      = (20, 32, 26, 255)
GOUD     = (201, 162, 39, 255)
HUID     = (150, 178, 118, 255)
HUID_D   = (108, 138, 84, 255)
HUID_L   = (183, 205, 152, 255)
BLAD     = (124, 158, 88, 255)
BLAD_D   = (78, 106, 56, 255)
BLAD_L   = (168, 196, 124, 255)
SCHORS   = (96, 74, 48, 255)
OOG      = (28, 44, 30, 255)
IRIS     = (196, 214, 140, 255)
LICHT    = (238, 244, 214, 255)


def leafpts(cx, cy, ang, ln, wd, curve=0.55, n=26):
    """Blad als lensvorm met punt aan beide uiteinden, gedraaid over ang (radialen)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = -ln / 2 + ln * t
        y = math.sin(math.pi * t) * (wd / 2) * (1 - curve * (t - .5))
        pts.append((x, y))
    for i in range(n, -1, -1):
        t = i / n
        x = -ln / 2 + ln * t
        y = -math.sin(math.pi * t) * (wd / 2) * (1 - curve * (t - .5))
        pts.append((x, y))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def leaf(d, cx, cy, ang, ln, wd, fill, nerf=None, curve=.55):
    d.polygon(leafpts(cx, cy, ang, ln, wd, curve), fill=fill)
    if nerf:
        ca, sa = math.cos(ang), math.sin(ang)
        x0, y0 = cx - ln / 2 * ca, cy - ln / 2 * sa
        x1, y1 = cx + ln / 2 * ca, cy + ln / 2 * sa
        d.line([(x0, y0), (x1, y1)], fill=nerf, width=max(1, int(wd * .07)))


def rank(d, pts, w, fill):
    """Dikke gebogen tak/rank langs een reeks punten, taps toelopend."""
    n = len(pts)
    for i in range(n - 1):
        ww = w * (1 - .62 * i / max(1, n - 2))
        d.line([pts[i], pts[i + 1]], fill=fill, width=max(1, int(ww)))
        d.ellipse([pts[i + 1][0] - ww / 2, pts[i + 1][1] - ww / 2,
                   pts[i + 1][0] + ww / 2, pts[i + 1][1] + ww / 2], fill=fill)


def bocht(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
            for t in [i / n for i in range(n + 1)]]


def dryade(S, pad=0.10, achtergrond=True, ring=True):
    W = S * SS
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = W * pad
    cx = W / 2

    if achtergrond:
        d.rounded_rectangle([0, 0, W, W], radius=W * .21, fill=BOS)
    if ring:
        d.ellipse([p * .62, p * .62, W - p * .62, W - p * .62],
                  outline=GOUD + () if False else (201, 162, 39, 120), width=max(2, int(W * .009)))

    # ---- takken/haar links en rechts (schors) ----
    for zij in (-1, 1):
        for j, (sx, sy, mx, my, ex, ey, bw) in enumerate([
            (.06, .30, .30, .48, .34, .82, .046),
            (.03, .26, .21, .40, .26, .90, .034),
            (.09, .38, .34, .58, .28, .70, .028),
            (.05, .22, .26, .30, .33, .46, .024),
        ]):
            pts = bocht((cx + zij * sx * W, W * sy),
                        (cx + zij * mx * W, W * my),
                        (cx + zij * ex * W, W * ey))
            rank(d, pts, W * bw, SCHORS)
            leaf(d, cx + zij * ex * W, W * ey, math.radians(70 * zij + 90),
                 W * .13, W * .055, BLAD_D, nerf=BLAD)

    # ---- bladerkroon ----
    kroon_y = W * .30
    for i, (a, dist, ln, wd) in enumerate([
        (-90, .225, .40, .165), (-116, .225, .37, .150), (-64, .225, .37, .150),
        (-140, .215, .33, .135), (-40, .215, .33, .135),
        (-162, .195, .28, .115), (-18, .195, .28, .115),
    ]):
        r = math.radians(a)
        lx = cx + math.cos(r) * W * dist
        ly = kroon_y + math.sin(r) * W * dist * .80 + W * .07
        leaf(d, lx, ly, r, W * ln, W * wd,
             BLAD if i % 2 == 0 else BLAD_D, nerf=BLAD_L, curve=.72)

    # ---- gezicht ----
    fw, fh = W * .425, W * .52
    fy = W * .545
    d.ellipse([cx - fw / 2, fy - fh / 2, cx + fw / 2, fy + fh / 2], fill=HUID)
    # kaaklijn schaduw
    d.polygon(bocht((cx - fw * .49, fy - fh * .06),
                    (cx, fy + fh * .66), (cx + fw * .49, fy - fh * .06)) +
              bocht((cx + fw * .49, fy - fh * .06),
                    (cx, fy - fh * .30), (cx - fw * .49, fy - fh * .06)), fill=HUID)

    # wangschaduw
    for zij in (-1, 1):
        leaf(d, cx + zij * fw * .32, fy + fh * .06, math.radians(80 * zij),
             fh * .30, fw * .14, (128, 158, 100, 255), curve=.3)

    # ---- bladeren op het voorhoofd ----
    for zij in (-1, 1):
        leaf(d, cx + zij * fw * .17, fy - fh * .34, math.radians(-30 * zij),
             fw * .40, fw * .20, BLAD_D, nerf=BLAD)
    leaf(d, cx, fy - fh * .43, math.radians(-90), fw * .32, fw * .19, BLAD, nerf=BLAD_L)

    # ---- wenkbrauwen als bladen ----
    for zij in (-1, 1):
        leaf(d, cx + zij * fw * .24, fy - fh * .14, math.radians(-13 * zij),
             fw * .34, fw * .085, BLAD_D)

    # ---- ogen ----
    ow, oh = fw * .27, fh * .115
    oy = fy - fh * .02
    for zij in (-1, 1):
        ox = cx + zij * fw * .235
        d.polygon(leafpts(ox, oy, 0, ow, oh, curve=.18), fill=LICHT)
        d.ellipse([ox - oh * .62, oy - oh * .62, ox + oh * .62, oy + oh * .62], fill=IRIS)
        d.ellipse([ox - oh * .30, oy - oh * .30, ox + oh * .30, oy + oh * .30], fill=OOG)
        d.ellipse([ox - oh * .46, oy - oh * .52, ox - oh * .10, oy - oh * .16], fill=LICHT)
        # bovenlijn
        d.line(bocht((ox - ow / 2, oy), (ox, oy - oh * 1.05), (ox + ow / 2, oy)),
               fill=OOG, width=max(2, int(W * .008)), joint="curve")

    # ---- neus ----
    d.polygon([(cx, fy - fh * .02), (cx + fw * .085, fy + fh * .155),
               (cx, fy + fh * .195), (cx - fw * .085, fy + fh * .155)], fill=HUID_D)
    d.polygon([(cx, fy + fh * .03), (cx + fw * .05, fy + fh * .16),
               (cx, fy + fh * .185), (cx - fw * .05, fy + fh * .16)], fill=HUID_L)

    # ---- mond ----
    my = fy + fh * .285
    d.line(bocht((cx - fw * .15, my), (cx, my + fh * .055), (cx + fw * .15, my)),
           fill=HUID_D, width=max(2, int(W * .011)), joint="curve")

    # ---- bladbaard ----
    for i, (dx, dy, a, sc) in enumerate([
        (-.34, .40, 124, 0.95), (.34, .40, 56, 0.95),
        (-.19, .52, 104, 0.86), (.19, .52, 76, 0.86),
        (-.44, .24, 140, 0.80), (.44, .24, 40, 0.80),
        (0.00, .58, 90, 0.80),
    ]):
        leaf(d, cx + fw * dx, fy + fh * dy, math.radians(a),
             fh * .34 * sc, fw * .17 * sc,
             BLAD if i % 2 == 0 else BLAD_D, nerf=BLAD_L, curve=.35)

    # ---- kleine ranken langs de wangen ----
    for zij in (-1, 1):
        pts = bocht((cx + zij * fw * .46, fy - fh * .22),
                    (cx + zij * fw * .60, fy + fh * .05),
                    (cx + zij * fw * .40, fy + fh * .34))
        rank(d, pts, W * .016, SCHORS)

    return im.resize((S, S), Image.LANCZOS)


def badge(S=96):
    """Monochroom silhouet met transparantie — Android kleurt dit zelf in."""
    W = S * SS
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W / 2
    wit = (255, 255, 255, 255)
    leeg = (0, 0, 0, 0)

    # basisvorm zodat kroon en gezicht één silhouet worden
    d.ellipse([cx - W * .225, W * .335, cx + W * .225, W * .80], fill=wit)
    # bladerkroon — met marge, Android snijdt de badge bij
    for a, dist, ln, wd in [(-90, .205, .30, .120), (-116, .205, .28, .110), (-64, .205, .28, .110),
                            (-143, .190, .24, .098), (-37, .190, .24, .098)]:
        r = math.radians(a)
        leaf(d, cx + math.cos(r) * W * dist, W * .455 + math.sin(r) * W * dist * .8,
             r, W * ln, W * wd, wit, curve=.72)
    # gezicht: ovaal met echte kin
    fw, fh = W * .44, W * .50
    fy = W * .585
    d.polygon(bocht((cx - fw * .49, fy - fh * .06), (cx, fy + fh * .66), (cx + fw * .49, fy - fh * .06)) +
              bocht((cx + fw * .49, fy - fh * .06), (cx, fy - fh * .34), (cx - fw * .49, fy - fh * .06)),
              fill=wit)
    # uitgesneden ogen, neus en mond
    for zij in (-1, 1):
        d.polygon(leafpts(cx + zij * fw * .225, fy - fh * .06, 0, fw * .28, fh * .125, .18), fill=leeg)
    d.line(bocht((cx - fw * .18, fy + fh * .26), (cx, fy + fh * .35), (cx + fw * .18, fy + fh * .26)),
           fill=leeg, width=max(3, int(W * .020)), joint="curve")
    d.polygon([(cx, fy + fh * .01), (cx + fw * .06, fy + fh * .16), (cx - fw * .06, fy + fh * .16)], fill=leeg)
    return im.resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    dryade(512).save("icon-512.png")
    dryade(192).save("icon-192.png")
    dryade(512, pad=0.20).save("icon-maskable.png")
    badge(96).save("badge-96.png")
    dryade(384, achtergrond=False, ring=False).save("dryade-vlak.png")
    print("iconen klaar")
