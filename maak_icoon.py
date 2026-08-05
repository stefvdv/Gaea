import math
from PIL import Image, ImageDraw, ImageFilter

SS = 6

BOS_D   = (12, 22, 16)
BOS_L   = (32, 52, 38)
GOUD    = (201, 162, 39)
SCHORS  = (92, 68, 44)
SCHORS_D= (58, 42, 26)
SCHORS_L= (134, 104, 70)
HUID    = (156, 184, 124)
HUID_D  = (104, 134, 82)
HUID_DD = (74, 100, 60)
HUID_L  = (196, 216, 166)
HUID_LL = (226, 238, 202)
BLAD    = (118, 154, 82)
BLAD_D  = (72, 102, 52)
BLAD_DD = (48, 72, 38)
BLAD_L  = (166, 196, 118)
BLAD_LL = (206, 228, 158)
OOG_D   = (24, 38, 26)
IRIS    = (168, 208, 118)
IRIS_D  = (86, 128, 62)
LICHT   = (244, 250, 226)
GLAS    = (196, 224, 214)
DRANK   = (126, 196, 122)
DRANK_L = (186, 232, 160)


def A(c, a=255):
    return (c[0], c[1], c[2], a)


def laag(W):
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def zacht(im, r):
    return im.filter(ImageFilter.GaussianBlur(r))


def bocht(p0, p1, p2, n=22):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1])
            for t in [i/n for i in range(n+1)]]


def bocht3(p0, p1, p2, p3, n=26):
    return [((1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0],
             (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1])
            for t in [i/n for i in range(n+1)]]


def leafpts(cx, cy, ang, ln, wd, curve=.55, punt=1.0, n=30):
    boven, onder = [], []
    for i in range(n+1):
        t = i/n
        x = -ln/2 + ln*t
        s = math.sin(math.pi*t) ** punt
        y = s * (wd/2) * (1 - curve*(t-.5))
        boven.append((x, y)); onder.append((x, -y))
    pts = boven + onder[::-1]
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x*ca - y*sa, cy + x*sa + y*ca) for x, y in pts]


def blad(d, cx, cy, ang, ln, wd, kleur, donker, licht, curve=.55, punt=1.0, tanden=0):
    pts = leafpts(cx, cy, ang, ln, wd, curve, punt)
    if tanden:
        ca, sa = math.cos(ang), math.sin(ang)
        nieuw = []
        for i, (x, y) in enumerate(pts):
            f = 1 + (tanden if i % 4 < 2 else -tanden)
            lx = (x - cx)*ca + (y - cy)*sa
            ly = (-(x - cx)*sa + (y - cy)*ca) * f
            nieuw.append((cx + lx*ca - ly*sa, cy + lx*sa + ly*ca))
        pts = nieuw
    d.polygon(pts, fill=A(kleur))
    ca, sa = math.cos(ang), math.sin(ang)
    half = pts[len(pts)//2:]
    d.polygon(half + [(cx + ln/2*ca, cy + ln/2*sa), (cx - ln/2*ca, cy - ln/2*sa)], fill=A(donker))
    x0, y0 = cx - ln/2*ca, cy - ln/2*sa
    x1, y1 = cx + ln/2*ca, cy + ln/2*sa
    d.line([(x0, y0), (x1, y1)], fill=A(licht), width=max(1, int(wd*.055)))
    for t in (.30, .48, .66):
        mx, my = x0 + (x1-x0)*t, y0 + (y1-y0)*t
        for zij in (-1, 1):
            d.line([(mx, my), (mx + math.cos(ang + zij*1.05)*ln*.20,
                               my + math.sin(ang + zij*1.05)*ln*.20)],
                   fill=A(licht, 150), width=max(1, int(wd*.032)))


def streng(d, pts, w, kleur, licht=None):
    n = len(pts)
    for i in range(n-1):
        ww = w * (1 - .70*i/max(1, n-2))
        d.line([pts[i], pts[i+1]], fill=A(kleur), width=max(1, int(ww)))
        d.ellipse([pts[i+1][0]-ww/2, pts[i+1][1]-ww/2,
                   pts[i+1][0]+ww/2, pts[i+1][1]+ww/2], fill=A(kleur))
    if licht:
        for i in range(n-1):
            ww = w * (1 - .70*i/max(1, n-2))
            dx, dy = pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy/L*ww*.24, dx/L*ww*.24
            d.line([(pts[i][0]+nx, pts[i][1]+ny), (pts[i+1][0]+nx, pts[i+1][1]+ny)],
                   fill=A(licht, 130), width=max(1, int(ww*.26)))


def keltische_ring(im, W, r, dikte, kleur, lussen=16):
    d = ImageDraw.Draw(im)
    cx = cy = W/2
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=A(kleur, 95), width=max(2, int(dikte*.30)))
    for faze in (0, math.pi):
        pts = []
        for i in range(721):
            a = math.radians(i/2)
            rr = r + math.sin(a*lussen + faze) * dikte*0.72
            pts.append((cx + math.cos(a)*rr, cy + math.sin(a)*rr))
        for i in range(len(pts)-1):
            d.line([pts[i], pts[i+1]], fill=A(kleur, 205), width=max(2, int(dikte*.40)))


def gezicht(im, W, cx, fy, fw, fh):
    d = ImageDraw.Draw(im)
    vorm = bocht3((cx - fw*.50, fy - fh*.16), (cx - fw*.52, fy + fh*.30),
                  (cx - fw*.26, fy + fh*.56), (cx, fy + fh*.60)) + \
           bocht3((cx, fy + fh*.60), (cx + fw*.26, fy + fh*.56),
                  (cx + fw*.52, fy + fh*.30), (cx + fw*.50, fy - fh*.16)) + \
           bocht3((cx + fw*.50, fy - fh*.16), (cx + fw*.48, fy - fh*.56),
                  (cx - fw*.48, fy - fh*.56), (cx - fw*.50, fy - fh*.16))
    d.polygon(vorm, fill=A(HUID))

    sch = laag(W); ds = ImageDraw.Draw(sch)
    ds.polygon(vorm, fill=A(HUID_DD, 195))
    ds.polygon([(cx + (x-cx)*.80, fy + (y-fy)*.84 - fh*.03) for x, y in vorm], fill=(0, 0, 0, 0))
    im.alpha_composite(zacht(sch, W*.013))

    lic = laag(W); dl = ImageDraw.Draw(lic)
    dl.ellipse([cx - fw*.22, fy - fh*.44, cx + fw*.22, fy - fh*.10], fill=A(HUID_L, 155))
    dl.ellipse([cx - fw*.055, fy - fh*.16, cx + fw*.055, fy + fh*.16], fill=A(HUID_L, 140))
    for zij in (-1, 1):
        dl.ellipse([cx + zij*fw*.34 - fw*.15, fy + fh*.02,
                    cx + zij*fw*.34 + fw*.15, fy + fh*.24], fill=A(HUID_L, 110))
    im.alpha_composite(zacht(lic, W*.017))


def ogen(im, W, cx, fy, fw, fh):
    ow, oh = fw*.235, fh*.050
    oy = fy - fh*.02
    for zij in (-1, 1):
        ox = cx + zij*fw*.225
        kas = laag(W); dk = ImageDraw.Draw(kas)
        dk.ellipse([ox - ow*.80, oy - oh*3.6, ox + ow*.80, oy + oh*3.4], fill=A(HUID_DD, 125))
        im.alpha_composite(zacht(kas, W*.011))
        d = ImageDraw.Draw(im)
        d.polygon(leafpts(ox, oy, math.radians(-4*zij), ow, oh*4, curve=.16, punt=.72), fill=A(LICHT))
        r = oh*1.62
        d.ellipse([ox-r, oy-r, ox+r, oy+r], fill=A(IRIS_D))
        d.ellipse([ox-r*.86, oy-r*.86, ox+r*.86, oy+r*.86], fill=A(IRIS))
        for i in range(14):
            a = i/14*2*math.pi
            d.line([(ox + math.cos(a)*r*.22, oy + math.sin(a)*r*.22),
                    (ox + math.cos(a)*r*.84, oy + math.sin(a)*r*.84)],
                   fill=A(IRIS_D, 170), width=max(1, int(W*.0022)))
        d.ellipse([ox-r*.40, oy-r*.40, ox+r*.40, oy+r*.40], fill=A(OOG_D))
        d.ellipse([ox-r*.46, oy-r*.62, ox-r*.10, oy-r*.26], fill=A(LICHT, 235))
        d.ellipse([ox+r*.16, oy+r*.24, ox+r*.40, oy+r*.48], fill=A(LICHT, 110))
        d.line(bocht((ox-ow/2, oy+oh*.4), (ox, oy-oh*2.6), (ox+ow/2, oy+oh*.2)),
               fill=A(OOG_D), width=max(2, int(W*.0078)), joint="curve")
        d.line(bocht((ox-ow/2, oy+oh*.4), (ox, oy+oh*2.2), (ox+ow/2, oy+oh*.2)),
               fill=A(HUID_DD), width=max(1, int(W*.0042)), joint="curve")


def flacon(im, W, cx, cy, h):
    gl = laag(W); dg = ImageDraw.Draw(gl)
    b = h*.50
    dg.ellipse([cx-b*1.2, cy-h*.10, cx+b*1.2, cy+h*.66], fill=A(DRANK, 130))
    im.alpha_composite(zacht(gl, W*.024))
    d = ImageDraw.Draw(im)
    hals = h*.28
    lw = max(2, int(W*.0058))
    d.ellipse([cx-b/2, cy+h*.06, cx+b/2, cy+h*.54], fill=A(GLAS, 95), outline=A(GLAS, 210), width=lw)
    d.rounded_rectangle([cx-b*.18, cy-hals*.55, cx+b*.18, cy+h*.18],
                        radius=b*.10, fill=A(GLAS, 95), outline=A(GLAS, 210), width=lw)
    d.pieslice([cx-b/2+lw, cy+h*.06+lw, cx+b/2-lw, cy+h*.54-lw], start=0, end=180, fill=A(DRANK, 238))
    d.ellipse([cx-b*.42, cy+h*.245, cx+b*.42, cy+h*.325], fill=A(DRANK_L, 238))
    for bx, by, br in [(-.11, .42, .055), (.08, .35, .042), (-.03, .26, .032),
                       (.14, .47, .030), (-.16, .32, .026), (.02, .18, .022)]:
        d.ellipse([cx+b*bx-b*br, cy+h*by-b*br, cx+b*bx+b*br, cy+h*by+b*br],
                  fill=A(DRANK_L, 205), outline=A(LICHT, 160), width=1)
    d.line([(cx-b*.30, cy+h*.18), (cx-b*.345, cy+h*.38)], fill=A(LICHT, 170), width=max(2, int(W*.0072)))
    d.rounded_rectangle([cx-b*.23, cy-hals*.88, cx+b*.23, cy-hals*.38], radius=b*.06, fill=A(SCHORS))
    d.rounded_rectangle([cx-b*.23, cy-hals*.88, cx+b*.23, cy-hals*.66], radius=b*.06, fill=A(SCHORS_L))
    streng(d, bocht((cx+b*.18, cy-hals*.08), (cx+b*.58, cy+h*.04), (cx+b*.42, cy+h*.22)), W*.0085, SCHORS)
    blad(d, cx+b*.50, cy+h*.18, math.radians(58), h*.22, h*.09, BLAD, BLAD_D, BLAD_LL, punt=.85)


def dryade(S, ring=True, metflacon=True, achtergrond=True, krimp=1.0):
    W = S*SS
    im = laag(W)
    cx = W/2

    if achtergrond:
        bg = laag(W); db = ImageDraw.Draw(bg)
        db.rounded_rectangle([0, 0, W, W], radius=W*.215, fill=A(BOS_D))
        gl = laag(W); dg = ImageDraw.Draw(gl)
        dg.ellipse([W*.08, -W*.12, W*.92, W*.74], fill=A(BOS_L, 235))
        gl = zacht(gl, W*.09)
        masker = Image.new("L", (W, W), 0)
        ImageDraw.Draw(masker).rounded_rectangle([0, 0, W, W], radius=W*.215, fill=255)
        gl.putalpha(Image.composite(gl.split()[3], Image.new("L", (W, W), 0), masker))
        bg.alpha_composite(gl)
        im.alpha_composite(bg)

    if ring:
        rg = laag(W)
        keltische_ring(rg, W, W*.420, W*.021, GOUD)
        im.alpha_composite(rg)

    fig = laag(W)
    d = ImageDraw.Draw(fig)
    fw, fh = W*.395, W*.475
    fy = W*.545

    for zij in (-1, 1):
        for sx, sy, mx, my, ex, ey, bw in [
            (.10, .28, .30, .46, .335, .84, .040),
            (.05, .24, .225, .40, .275, .90, .030),
            (.14, .34, .345, .60, .295, .74, .024),
            (.075, .21, .275, .30, .345, .50, .020),
            (.03, .30, .16, .56, .20, .88, .017),
        ]:
            pts = bocht((cx + zij*sx*W, W*sy), (cx + zij*mx*W, W*my), (cx + zij*ex*W, W*ey))
            streng(d, pts, W*bw, SCHORS_D if bw < .025 else SCHORS, SCHORS_L)
            blad(d, cx + zij*ex*W, W*ey, math.radians(72*zij + 90),
                 W*.115, W*.050, BLAD_D, BLAD_DD, BLAD_L, punt=.85)

    for a, dist, ln, wd in [(-155, .218, .258, .142), (-25, .218, .258, .142),
                            (-172, .198, .222, .120), (-8, .198, .222, .120)]:
        r = math.radians(a)
        blad(d, cx + math.cos(r)*W*dist, W*.315 + math.sin(r)*W*dist*.80,
             r, W*ln, W*wd, BLAD_D, BLAD_DD, BLAD_L, curve=.42, punt=1.05, tanden=.055)

    gezicht(fig, W, cx, fy, fw, fh)
    d = ImageDraw.Draw(fig)

    for a, dist, ln, wd in [(-90, .225, .330, .190), (-114, .222, .305, .172), (-66, .222, .305, .172),
                            (-138, .212, .272, .152), (-42, .212, .272, .152)]:
        r = math.radians(a)
        blad(d, cx + math.cos(r)*W*dist, W*.315 + math.sin(r)*W*dist*.80,
             r, W*ln, W*wd, BLAD, BLAD_D, BLAD_LL, curve=.42, punt=1.05, tanden=.055)

    for zij in (-1, 1):
        blad(d, cx + zij*fw*.19, fy - fh*.345, math.radians(-32*zij),
             fw*.34, fw*.145, BLAD_D, BLAD_DD, BLAD_L, punt=.85)
    blad(d, cx, fy - fh*.415, math.radians(-90), fw*.26, fw*.135, BLAD, BLAD_D, BLAD_LL, punt=.85)
    for zij in (-1, 1):
        blad(d, cx + zij*fw*.235, fy - fh*.155, math.radians(-14*zij),
             fw*.32, fw*.072, BLAD_D, BLAD_DD, BLAD_L, punt=.7)

    ogen(fig, W, cx, fy, fw, fh)
    d = ImageDraw.Draw(fig)

    ns = laag(W); dn = ImageDraw.Draw(ns)
    dn.polygon([(cx, fy - fh*.05), (cx + fw*.095, fy + fh*.155),
                (cx, fy + fh*.205), (cx - fw*.095, fy + fh*.155)], fill=A(HUID_DD, 175))
    fig.alpha_composite(zacht(ns, W*.006))
    d = ImageDraw.Draw(fig)
    d.polygon([(cx, fy + fh*.01), (cx + fw*.045, fy + fh*.16),
               (cx, fy + fh*.185), (cx - fw*.045, fy + fh*.16)], fill=A(HUID_L, 210))
    for zij in (-1, 1):
        d.ellipse([cx + zij*fw*.062 - fw*.022, fy + fh*.155,
                   cx + zij*fw*.062 + fw*.022, fy + fh*.192], fill=A(HUID_DD, 190))

    my = fy + fh*.295
    d.polygon(bocht((cx - fw*.165, my), (cx, my - fh*.050), (cx + fw*.165, my)) +
              bocht((cx + fw*.165, my), (cx, my + fh*.082), (cx - fw*.165, my)),
              fill=A((132, 108, 96), 195))
    d.line(bocht((cx - fw*.165, my), (cx, my + fh*.024), (cx + fw*.165, my)),
           fill=A(HUID_DD), width=max(2, int(W*.006)), joint="curve")
    d.line(bocht((cx - fw*.07, my + fh*.055), (cx, my + fh*.078), (cx + fw*.07, my + fh*.055)),
           fill=A(HUID_LL, 125), width=max(1, int(W*.004)), joint="curve")

    for i, (dx, dy, a, sc) in enumerate([
        (-.42, .455, 128, .92), (.42, .455, 52, .92),
        (-.25, .575, 106, .85), (.25, .575, 74, .85),
        (-.52, .295, 144, .80), (.52, .295, 36, .80),
        (0.0, .625, 90, .78),
    ]):
        blad(d, cx + fw*dx, fy + fh*dy, math.radians(a), fh*.32*sc, fw*.155*sc,
             BLAD if i % 2 == 0 else BLAD_D, BLAD_DD, BLAD_LL, curve=.40, punt=.85)

    if metflacon:
        flacon(fig, W, cx - W*.300, W*.705, W*.240)

    if krimp != 1.0:
        n = int(W*krimp)
        klein = fig.resize((n, n), Image.LANCZOS)
        fig = laag(W)
        fig.alpha_composite(klein, ((W-n)//2, (W-n)//2))
    im.alpha_composite(fig)
    return im.resize((S, S), Image.LANCZOS)


def badge(S=96):
    W = S*SS
    im = laag(W); d = ImageDraw.Draw(im)
    cx = W/2
    wit = (255, 255, 255, 255); leeg = (0, 0, 0, 0)
    d.ellipse([cx - W*.215, W*.345, cx + W*.215, W*.795], fill=wit)
    for a, dist, ln, wd in [(-90, .205, .30, .120), (-115, .205, .275, .108),
                            (-65, .205, .275, .108), (-142, .190, .235, .095),
                            (-38, .190, .235, .095)]:
        r = math.radians(a)
        d.polygon(leafpts(cx + math.cos(r)*W*dist, W*.455 + math.sin(r)*W*dist*.80,
                          r, W*ln, W*wd, .72, .78), fill=wit)
    fw, fh = W*.42, W*.48
    fy = W*.585
    d.polygon(bocht3((cx - fw*.50, fy - fh*.14), (cx - fw*.52, fy + fh*.30),
                     (cx - fw*.26, fy + fh*.56), (cx, fy + fh*.60)) +
              bocht3((cx, fy + fh*.60), (cx + fw*.26, fy + fh*.56),
                     (cx + fw*.52, fy + fh*.30), (cx + fw*.50, fy - fh*.14)) +
              [(cx + fw*.50, fy - fh*.40), (cx - fw*.50, fy - fh*.40)], fill=wit)
    for zij in (-1, 1):
        d.polygon(leafpts(cx + zij*fw*.225, fy - fh*.055, 0, fw*.27, fh*.135, .18, .72), fill=leeg)
    d.polygon([(cx, fy + fh*.015), (cx + fw*.06, fy + fh*.165), (cx - fw*.06, fy + fh*.165)], fill=leeg)
    d.line(bocht((cx - fw*.17, fy + fh*.265), (cx, fy + fh*.345), (cx + fw*.17, fy + fh*.265)),
           fill=leeg, width=max(3, int(W*.021)), joint="curve")
    return im.resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    dryade(512).save("icon-512.png")
    dryade(192).save("icon-192.png")
    dryade(512, ring=False, metflacon=False, krimp=.66).save("icon-maskable.png")
    badge(96).save("badge-96.png")
    print("iconen klaar")
