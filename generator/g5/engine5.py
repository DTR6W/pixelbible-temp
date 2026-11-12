"""engine5: 16:9 pixel-art scene engine (480x270 canvas, x4 -> 1920x1080) with layered parallax scenery,
dynamic effects and an acting cast with physical poses (kneel, pray, prostrate, hammer, carry, eat, fall...)."""
import math, random, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast5

PW, PH = 480, 270
Z = 4
W, H = PW * Z, PH * Z
FPS = 30
HZ = 186            # far ground line (horizon)
WW = 960            # world width for panning
OUT = (22, 12, 18)

def lerpc(a, b, f): f = min(max(f, 0), 1); return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_c(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3
def clamp(x, a, b): return max(a, min(b, x))
def mul(c, k): return tuple(int(clamp(v * k, 0, 255)) for v in c)

# ------------------------------------------------------------------ palettes
SKY = {
 "void": ((3, 4, 14), (10, 14, 40)), "dawn": ((110, 100, 180), (255, 200, 140)), "day": ((80, 150, 230), (205, 230, 250)),
 "noon": ((60, 130, 225), (190, 225, 250)), "golden": ((80, 100, 180), (255, 210, 130)), "dusk": ((40, 28, 90), (240, 120, 80)),
 "night": ((4, 6, 28), (36, 44, 100)), "storm": ((26, 30, 52), (80, 90, 120)), "grey": ((110, 120, 140), (190, 196, 210)),
 "eden": ((100, 190, 230), (220, 245, 230)), "fire": ((50, 10, 12), (240, 110, 40)), "ash": ((60, 60, 70), (150, 140, 130)),
}
GROUND = {
 "grass": ((88, 160, 70), (58, 118, 50), (130, 190, 90)), "lush": ((70, 170, 80), (44, 120, 58), (120, 210, 110)),
 "dirt": ((160, 124, 80), (118, 88, 56), (196, 160, 110)), "sand": ((224, 192, 130), (190, 156, 98), (240, 214, 160)),
 "rock": ((110, 104, 100), (74, 70, 70), (150, 144, 140)), "mud": ((110, 86, 58), (76, 58, 40), (140, 112, 80)),
 "night": ((30, 52, 50), (18, 32, 34), (50, 80, 70)), "ash": ((70, 64, 62), (44, 40, 40), (100, 92, 90)), "snow": ((230, 236, 245), (190, 200, 215), (255, 255, 255)),
}
MTN = {"day": ((120, 140, 190), (160, 180, 220)), "noon": ((110, 135, 190), (150, 175, 220)), "dawn": ((150, 110, 160), (220, 160, 170)), "golden": ((140, 120, 140), (210, 170, 130)),
       "dusk": ((80, 50, 100), (150, 86, 100)), "night": ((20, 24, 60), (40, 46, 92)), "storm": ((44, 52, 74), (70, 80, 104)), "grey": ((120, 126, 140), (160, 166, 180)),
       "eden": ((110, 170, 170), (170, 220, 200)), "void": ((8, 10, 30), (14, 18, 46)), "fire": ((60, 20, 24), (150, 60, 40)), "ash": ((70, 66, 72), (110, 104, 110))}

# ------------------------------------------------------------------ primitives (PIL, pixel canvas)
def gradient(w, h, c0, c1, bands=14):
    yy = np.arange(h)[:, None] / max(1, h - 1)
    bay = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    B = bay[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4]
    f = np.clip(np.floor(yy * bands + B) / bands, 0, 1)[..., None]
    arr = np.array(c0, np.float32) + (np.array(c1, np.float32) - np.array(c0, np.float32)) * f
    return Image.fromarray(arr.astype(np.uint8), "RGB")

def ridge_pts(seed, base, amp, w, scale=1.0, x0=0):
    r = random.Random(seed); ph = [r.random() * 6.28 for _ in range(4)]
    pts = []
    for x in range(x0, x0 + w + 1, 2):
        h = (math.sin(x * 0.045 * scale + ph[0]) * 0.5 + math.sin(x * 0.11 * scale + ph[1]) * 0.28 + math.sin(x * 0.23 * scale + ph[2]) * 0.14 + math.sin(x * 0.5 * scale + ph[3]) * 0.06)
        pts.append((x, int(base - h * amp)))
    return pts

def mountains(d, seed, base, amp, col, hi, w=WW, scale=1.0, snow=None):
    pts = ridge_pts(seed, base, amp, w, scale)
    d.polygon(pts + [(w, PH), (0, PH)], fill=col)
    for (x, y), (x2, y2) in zip(pts, pts[1:]):
        if y2 < y: d.line([(x, y), (x2, y2)], fill=hi)
        if snow and y < base - amp * 0.55: d.line([(x, y), (x2, y2 + 1)], fill=snow)

def hills(d, seed, base, amp, col, hi, w=WW, scale=1.6):
    pts = ridge_pts(seed, base, amp, w, scale)
    d.polygon(pts + [(w, PH), (0, PH)], fill=col)
    for (x, y), (x2, y2) in zip(pts, pts[1:]):
        if y2 <= y: d.line([(x, y), (x2, y2)], fill=hi)

def ground(d, gkind, y0=HZ, w=WW, seed=5, path=None, dens=0.06):
    g = GROUND[gkind]
    for y in range(y0, PH, 2):
        f = (y - y0) / max(1, PH - y0)
        d.rectangle([0, y, w, y + 1], fill=lerpc(g[0], g[1], f * 0.8))
    r = random.Random(seed)
    for _ in range(int(w * (PH - y0) * dens / 10)):
        x, y = r.randrange(w), r.randrange(y0 + 1, PH)
        d.point((x, y), fill=g[1] if r.random() < 0.6 else g[2])
    for _ in range(int(w / 30)):  # tufts / pebbles
        x, y = r.randrange(w), r.randrange(y0 + 4, PH)
        if gkind in ("grass", "lush"):
            d.line([(x, y), (x - 1, y - 3)], fill=g[2]); d.line([(x + 1, y), (x + 2, y - 3)], fill=g[2])
        else:
            d.ellipse([x, y, x + 3, y + 2], fill=g[1]); d.point((x + 1, y), fill=g[2])
    if path:
        px, pw = path
        for y in range(y0, PH):
            f = (y - y0) / (PH - y0); hw = pw * (0.3 + f * 1.4); cx = px + math.sin(y * 0.05) * 8 * f
            d.line([(cx - hw, y), (cx + hw, y)], fill=lerpc(g[2], (170, 140, 100), 0.4))
            if y % 3 == 0: d.point((int(cx + math.sin(y) * hw * 0.7), y), fill=g[1])

def tree(d, x, yb, h, leaf=(50, 130, 60), trunk=(84, 56, 36), style="round", t=0.0, sway=1.0, fruit=None, seed=0):
    if h < 4: return
    sw = int(round(math.sin(t * 1.1 + x * 0.1) * sway))
    tw = max(2, h // 9)
    d.rectangle([x - tw // 2, yb - h, x + tw // 2, yb], fill=trunk); d.line([(x - tw // 2, yb - h), (x - tw // 2, yb)], fill=mul(trunk, 1.3))
    dk, lt = mul(leaf, 0.78), mul(leaf, 1.25)
    r = random.Random(seed + x)
    if style == "pine":
        for i in range(4):
            yy = yb - h + i * h * 0.22; wdt = (i + 1) * h * 0.14
            d.polygon([(x + sw, yy - h * 0.18), (x + sw - wdt, yy + h * 0.12), (x + sw + wdt, yy + h * 0.12)], fill=leaf if i % 2 else dk)
            d.line([(x + sw, yy - h * 0.18), (x + sw - wdt, yy + h * 0.12)], fill=lt)
    elif style == "palm":
        for k in range(7):
            a = math.pi + k / 6 * math.pi; L = h * 0.5
            pts = [(x + sw + math.cos(a) * L * s / 10 * 1.3, yb - h + math.sin(a) * L * s / 10 * 0.6 + (s * s) * 0.04 * (L / 10)) for s in range(0, 11)]
            d.line(pts, fill=leaf if k % 2 else dk, width=2)
        d.ellipse([x + sw - 3, yb - h - 3, x + sw + 3, yb - h + 3], fill=(140, 90, 40))
    elif style == "willow":
        d.ellipse([x + sw - h * 0.4, yb - h - h * 0.2, x + sw + h * 0.4, yb - h + h * 0.3], fill=dk)
        for k in range(-5, 6):
            xx = x + sw + k * h * 0.07; d.line([(xx, yb - h + h * 0.2), (xx + int(math.sin(t * 2 + k) * 2), yb - h * 0.25)], fill=leaf if k % 2 else lt)
    else:
        rr = max(4, int(h * 0.42)); cy = yb - h
        blobs = [(0, -rr // 3, rr, leaf), (-rr // 2, 0, rr * 0.75, dk), (rr // 2, 0, rr * 0.75, dk), (-rr // 4, -rr // 2, rr * 0.5, lt), (rr // 3, -rr * 0.55, rr * 0.45, lt)]
        for dx, dy, q, col in blobs:
            d.ellipse([x + dx + sw - q, cy + dy - q, x + dx + sw + q, cy + dy + q], fill=col)
        for _ in range(int(rr * 0.6)):
            px, py = x + sw + r.uniform(-rr, rr), cy + r.uniform(-rr, rr * 0.4)
            if (px - x - sw) ** 2 + (py - cy) ** 2 < rr * rr: d.point((int(px), int(py)), fill=lt if r.random() < 0.5 else dk)
        if fruit:
            for k in range(6):
                fx, fy = x + sw + r.uniform(-rr * 0.8, rr * 0.8), cy + r.uniform(-rr * 0.7, rr * 0.3)
                d.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=fruit); d.point((int(fx - 1), int(fy - 1)), fill=mul(fruit, 1.5))

def bush(d, x, yb, w, leaf=(60, 140, 70), t=0.0, flowers=None):
    dk, lt = mul(leaf, 0.75), mul(leaf, 1.25); sw = int(math.sin(t * 1.3 + x) * 0.8)
    for dx, dy, r in ((0, 0, w * 0.5), (-w * 0.35, 2, w * 0.4), (w * 0.35, 2, w * 0.4), (0, -w * 0.25, w * 0.35)):
        d.ellipse([x + dx + sw - r, yb - r * 1.2 + dy, x + dx + sw + r, yb + dy], fill=leaf if r > w * 0.42 else dk)
    d.ellipse([x + sw - w * 0.2, yb - w * 0.6, x + sw + w * 0.1, yb - w * 0.35], fill=lt)
    if flowers:
        r = random.Random(x)
        for _ in range(4): d.point((int(x + sw + r.uniform(-w * 0.4, w * 0.4)), int(yb - r.uniform(w * 0.1, w * 0.6))), fill=flowers)

def grass(d, x, y, col, t=0.0, n=3):
    for k in range(n):
        sw = math.sin(t * 2.2 + x + k) * 1.5
        d.line([(x + k * 2, y), (x + k * 2 + sw, y - 3 - (k % 2))], fill=col)

def flower(d, x, y, col, t=0.0, h=5):
    sw = int(round(math.sin(t * 2 + x) * 1))
    d.line([(x, y), (x + sw, y - h)], fill=(40, 120, 50)); d.rectangle([x + sw - 1, y - h - 1, x + sw + 1, y - h + 1], fill=col); d.point((x + sw, y - h), fill=(255, 240, 150))

def rock(d, x, y, w, h, col=(120, 116, 110)):
    d.polygon([(x - w, y), (x - w * 0.6, y - h), (x + w * 0.2, y - h * 1.1), (x + w, y - h * 0.4), (x + w * 0.9, y)], fill=col)
    d.line([(x - w * 0.6, y - h), (x + w * 0.2, y - h * 1.1)], fill=mul(col, 1.3)); d.line([(x + w * 0.2, y - h * 1.1), (x + w, y - h * 0.4)], fill=mul(col, 0.7))

def cloud(d, x, y, s=1.0, col=(250, 250, 255), shade=(214, 222, 240)):
    for dx, dy, r in ((0, 0, 8), (10, -3, 9), (21, 0, 7), (6, 4, 7), (16, 4, 7), (-8, 3, 6)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s * 0.7, x + dx * s + r * s, y + dy * s + r * s * 0.7], fill=col)
    for dx, dy, r in ((4, 5, 7), (15, 5, 6)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s * 0.5 + 2, x + dx * s + r * s, y + dy * s + r * s * 0.5 + 2], fill=shade)

def sun(d, x, y, r, t=0.0, col=(255, 210, 90), rays=True):
    if rays:
        for a in range(0, 360, 24):
            aa = math.radians(a + t * 6); L = r + 6 + 2 * math.sin(t * 3 + a)
            d.line([(x + (r + 2) * math.cos(aa), y + (r + 2) * math.sin(aa)), (x + L * math.cos(aa), y + L * math.sin(aa))], fill=mul(col, 1.1))
    d.ellipse([x - r, y - r, x + r, y + r], fill=col); d.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], fill=mul(col, 1.25))

def moon(d, x, y, r, col=(240, 240, 220)):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col); d.point((x - r // 3, y), fill=mul(col, 0.8)); d.point((x + r // 4, y + r // 3), fill=mul(col, 0.8))

def stars(d, t, n=60, seed=4, w=WW, ymax=HZ - 30, col=(240, 240, 255)):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.randrange(w), r.randrange(ymax)
        if math.sin(t * 2 + i * 1.7) > -0.4: d.point((x, y), fill=col)
        if i % 9 == 0 and math.sin(t * 1.5 + i) > 0.6: d.line([(x - 1, y), (x + 1, y)], fill=col); d.line([(x, y - 1), (x, y + 1)], fill=col)

def bird(d, x, y, t, col=(40, 40, 60), s=1.0):
    w = (2 + 2.5 * math.sin(t * 9 + x)) * s
    d.line([(x - 5 * s, y - w), (x, y)], fill=col); d.line([(x, y), (x + 5 * s, y - w)], fill=col)

def water(d, x0, x1, y0, y1, t, c0=(40, 110, 190), c1=(90, 160, 230), hi=(200, 235, 255), calm=1.0):
    for y in range(y0, y1, 2):
        f = (y - y0) / max(1, y1 - y0)
        d.rectangle([x0, y, x1, y + 1], fill=lerpc(c0, c1, f))
    for y in range(y0 + 1, y1, 5):
        for x in range(x0, x1, 3):
            if int(y + 3 * math.sin(x * 0.11 + t * 1.6 * calm + y * 0.5)) % 7 == 0: d.line([(x, y), (x + 1, y)], fill=hi)

def altar(d, x, y, w=16, col=(140, 132, 124)):
    d.rectangle([x - w, y - 10, x + w, y], fill=col); d.rectangle([x - w, y - 10, x + w, y - 8], fill=mul(col, 1.3))
    for k in range(-w, w, 6): d.line([(x + k, y - 10), (x + k, y)], fill=mul(col, 0.7))
    d.rectangle([x - w + 2, y - 14, x + w - 2, y - 10], fill=(110, 76, 46))

def fire(d, x, y, t, s=1.0, n=10, cols=((255, 90, 30), (255, 160, 40), (255, 230, 120))):
    for k in range(n):
        yy = y - k * 2.2 * s - abs(math.sin(t * 9 + k + x)) * 3 * s; ww = max(1, (n - k) * 0.5 * s)
        d.ellipse([x - ww, yy - 1.5 * s, x + ww, yy + 1.5 * s], fill=cols[min(2, k * 3 // n)])
    for k in range(5):
        px = x + math.sin(t * 3 + k) * 4 * s; py = y - n * 2.2 * s - ((t * 25 + k * 13) % 30) * s
        d.point((int(px), int(py)), fill=(255, 200, 80))

def smoke(d, x, y, t, rise=1.0, col=(200, 200, 210), n=8, drift=0.0, up=True):
    for k in range(n):
        ph = ((t * 0.9 + k * 0.17) % 1.0)
        yy = y - ph * 70 * rise if up else y + ph * 40
        xx = x + math.sin(ph * 6 + k) * 6 + ph * drift * 30; r = 2 + ph * 7
        a = 1 - ph
        if a > 0.15: d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=lerpc((120, 120, 130), col, a * 0.8 + 0.2))

def lightning(d, x, y0, y1, seed=0, col=(255, 255, 240)):
    r = random.Random(seed); pts = [(x, y0)]
    while pts[-1][1] < y1: pts.append((pts[-1][0] + r.randint(-9, 9), pts[-1][1] + r.randint(8, 18)))
    d.line(pts, fill=col, width=2)
    if r.random() < 0.7:
        k = r.randint(1, max(1, len(pts) - 2)); b = [pts[k]]
        for _ in range(3): b.append((b[-1][0] + r.randint(-12, 12), b[-1][1] + r.randint(6, 14)))
        d.line(b, fill=col, width=1)

def rainbow(d, cx, cy, r, alpha_im, a=1.0):
    cols = ((255, 60, 60), (255, 150, 40), (255, 230, 80), (90, 210, 90), (70, 150, 255), (100, 80, 220))
    ov = Image.new("RGBA", alpha_im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i, c in enumerate(cols):
        rr = r - i * 3; od.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=(*c, int(150 * a)), width=3)
    alpha_im.paste(ov, (0, 0), ov)

def ark(d, x, y, t=0.0, stage=1.0, w=190, h=58, doors_open=True, float_t=None):
    """stage 0..1 = construction progress; float_t for bobbing"""
    bob = int(round(math.sin(float_t * 1.1) * 2)) if float_t is not None else 0
    y = y + bob
    wood, dark, lt = (150, 100, 56), (100, 66, 36), (190, 136, 80)
    # hull (slightly tapered ends)
    frac = ease(stage)
    hh = int(h * min(1.0, frac * 1.3))
    # keel + ribs appear first
    d.rectangle([x - w // 2, y - 4, x + w // 2, y], fill=dark)
    for k in range(-w // 2 + 6, w // 2 - 5, 14):
        d.line([(x + k, y - 4), (x + k, y - min(hh, h))], fill=dark)
    if frac > 0.1:
        for row in range(0, hh, 6):
            yy = y - 6 - row
            d.rectangle([x - w // 2 + 2, yy - 5, x + w // 2 - 2, yy], fill=wood if (row // 6) % 2 else mul(wood, 0.9))
            d.line([(x - w // 2 + 2, yy - 5), (x + w // 2 - 2, yy - 5)], fill=lt)
            for k in range(-w // 2 + 10 + (row // 6 % 2) * 7, w // 2 - 6, 24): d.line([(x + k, yy - 5), (x + k, yy)], fill=dark)
    if frac > 0.75:
        roof_f = ease((frac - 0.75) / 0.25)
        rh = int(14 * roof_f)
        d.polygon([(x - w // 2 + 4, y - h - 2), (x, y - h - 2 - rh), (x + w // 2 - 4, y - h - 2)], fill=(120, 80, 44))
        d.line([(x - w // 2 + 4, y - h - 2), (x, y - h - 2 - rh)], fill=lt)
        # window strip
        d.rectangle([x - w // 2 + 20, y - h + 6, x + w // 2 - 20, y - h + 11], fill=(60, 40, 30))
        for k in range(-w // 2 + 24, w // 2 - 22, 14): d.rectangle([x + k, y - h + 7, x + k + 6, y - h + 10], fill=(255, 220, 140))
        # door
        if doors_open:
            d.polygon([(x + w // 2 - 30, y - 30), (x + w // 2 - 30, y - 2), (x + w // 2 + 26, y + 8), (x + w // 2 + 26, y - 4)], fill=(120, 80, 44))
            d.rectangle([x + w // 2 - 32, y - 32, x + w // 2 - 14, y - 2], fill=(30, 20, 16))
        else:
            d.rectangle([x + w // 2 - 32, y - 32, x + w // 2 - 14, y - 2], fill=(110, 72, 40)); d.line([(x + w // 2 - 32, y - 17), (x + w // 2 - 14, y - 17)], fill=dark)
    return y

def tower(d, x, yb, stage, t=0.0, maxh=150):
    """ziggurat tower growing with stage 0..1"""
    levels = 7; h = int(maxh * ease(stage)); col = (196, 150, 100); dark = (150, 108, 70); lt = (226, 186, 130)
    yy = yb
    for L in range(levels):
        lh = maxh // levels; w = 90 - L * 11
        if yb - yy >= h: break
        top = max(yy - lh, yb - h)
        d.rectangle([x - w, top, x + w, yy], fill=col if L % 2 else mul(col, 0.95))
        d.rectangle([x - w, top, x + w, top + 2], fill=lt); d.rectangle([x + w - 6, top, x + w, yy], fill=dark)
        for k in range(-w + 6, w - 6, 12):
            if (yy - top) > 6: d.rectangle([x + k, yy - 8, x + k + 4, yy - 3], fill=(60, 40, 30))
        # ramp
        d.line([(x + w, yy), (x + w - 24, top)], fill=lt, width=2)
        yy = top
    # scaffold on top
    if 0.05 < stage < 0.98:
        d.line([(x - 30, yy), (x - 30, yy - 16)], fill=(110, 80, 50)); d.line([(x + 30, yy), (x + 30, yy - 16)], fill=(110, 80, 50)); d.line([(x - 32, yy - 16), (x + 32, yy - 16)], fill=(110, 80, 50))
    return yy

def city(d, x0, x1, yb, col=(196, 160, 116), seed=2, h0=16, h1=40, tower_=False):
    r = random.Random(seed); x = x0
    while x < x1:
        w = r.randint(14, 28); h = r.randint(h0, h1)
        d.rectangle([x, yb - h, x + w, yb], fill=mul(col, 0.92 + 0.1 * r.random())); d.rectangle([x, yb - h, x + w, yb - h + 2], fill=mul(col, 1.2)); d.rectangle([x + w - 3, yb - h, x + w, yb], fill=mul(col, 0.75))
        for wy in range(yb - h + 6, yb - 6, 9):
            for wx in range(x + 4, x + w - 4, 8): d.rectangle([wx, wy, wx + 2, wy + 3], fill=(60, 36, 28) if r.random() < 0.6 else (255, 210, 120))
        x += w + r.randint(0, 3)
    if tower_: d.rectangle([(x0 + x1) // 2 - 6, yb - 60, (x0 + x1) // 2 + 6, yb], fill=col)

def tent(d, x, yb, w=28, h=20, col=(190, 160, 110)):
    d.polygon([(x - w, yb), (x, yb - h), (x + w, yb)], fill=col); d.polygon([(x - w // 3, yb), (x, yb - h * 0.6), (x + w // 3, yb)], fill=(60, 40, 30)); d.line([(x, yb - h), (x + w, yb)], fill=mul(col, 0.7))

def gate(d, x, yb, h=70, col=(210, 170, 70)):
    d.rectangle([x - 26, yb - h, x - 18, yb], fill=col); d.rectangle([x + 18, yb - h, x + 26, yb], fill=col)
    d.pieslice([x - 26, yb - h - 20, x + 26, yb - h + 20], 180, 360, fill=col); d.pieslice([x - 18, yb - h - 12, x + 18, yb - h + 12], 180, 360, fill=(255, 240, 190))
    d.rectangle([x - 18, yb - h, x + 18, yb], fill=(255, 240, 190))

def sword_flame(d, x, y, t, L=30):
    a = math.radians(-60 + 25 * math.sin(t * 2.5)); ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    d.line([(x, y), (ex, ey)], fill=(255, 240, 200), width=2)
    for k in range(6):
        f = k / 6; px, py = x + (ex - x) * f, y + (ey - y) * f
        d.ellipse([px - 3 + math.sin(t * 20 + k) * 2, py - 3, px + 3 + math.sin(t * 20 + k) * 2, py + 3], fill=((255, 90, 30), (255, 170, 40), (255, 230, 120))[k % 3])

def serpent(d, x, y, t, n=16, coil=True):
    for i in range(n):
        px = x + 4 * math.sin(i * 0.8 + t * 4); py = y - i * 2.4
        d.ellipse([px - 2.4, py - 2.4, px + 2.4, py + 2.4], fill=(70, 150, 70) if i % 2 else (50, 120, 56))
    hx = x + 4 * math.sin(t * 4 + n * 0.8); hy = y - n * 2.4
    d.ellipse([hx - 3.5, hy - 3, hx + 3.5, hy + 3], fill=(80, 165, 80)); d.point((int(hx + 2), int(hy - 1)), fill=(230, 40, 40))
    if int(t * 3) % 3 == 0: d.line([(hx + 3, hy + 1), (hx + 7, hy + 1 + math.sin(t * 30) * 2)], fill=(230, 60, 60))

def apple(d, x, y, bitten=False):
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(220, 50, 60)); d.point((x - 1, y - 2), fill=(255, 170, 170)); d.line([(x, y - 3), (x + 1, y - 5)], fill=(90, 60, 30))
    if bitten: d.ellipse([x + 1, y - 2, x + 4, y + 1], fill=(250, 240, 200))

def dove_sprite(base, x, y, t, kind="dove", flip=False):
    im = cast5.animal(kind, t);
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    base.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)

def paste_animal(base, kind, x, y, t, walk=1.0, flip=False, s=1.0):
    im = cast5.animal(kind, t, walk) if kind in ("ox", "horse", "camel", "elephant", "giraffe", "goat", "wolf", "pig", "monkey", "bear", "dove", "raven") else None
    if im is None:
        arr = cast5.sprite(kind, t, walk=walk); im = Image.fromarray(arr, "RGBA"); s *= 0.42
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    base.paste(im, (int(x - im.width / 2), int(y - im.height + 2)), im)

# ------------------------------------------------------------------ environments (static layers cached)
_ST = {}
class Layer:
    def __init__(s, par, im=None, fn=None): s.par, s.im, s.fn = par, im, fn

def new_layer(): return Image.new("RGBA", (WW, PH), (0, 0, 0, 0))

def build_env(o):
    """returns (sky_image(480x270 RGB), [Layer...static], dyn_fn). o: env dict"""
    key = repr(sorted((k, repr(v)) for k, v in o.items() if k not in ("cast", "fx", "cam", "beats", "title", "amb", "sfx")))
    if key in _ST: return _ST[key]
    kind = o.get("env", "meadow"); sky = o.get("sky", "day"); gk = o.get("ground", "grass")
    skyim = gradient(PW, HZ + 20, *SKY[sky])
    layers = []
    far = new_layer(); d = ImageDraw.Draw(far)
    mid = new_layer(); dm = ImageDraw.Draw(mid)
    gnd = new_layer(); dg = ImageDraw.Draw(gnd)
    m = MTN.get(sky, MTN["day"])
    r = random.Random(o.get("seed", 1))
    if kind in ("meadow", "eden", "field", "ararat", "plain", "camp", "hill", "vineyard"):
        if o.get("mountains", True): mountains(d, 11 + o.get("seed", 0), HZ - 50, 36, m[0], m[1], snow=(240, 240, 250) if kind == "ararat" else None)
        mountains(d, 23 + o.get("seed", 0), HZ - 26, 18, mul(m[0], 0.85), m[1], scale=1.3)
        hills(dm, 37 + o.get("seed", 0), HZ - 6, 10, lerpc(GROUND[gk][0], m[0], 0.35), lerpc(GROUND[gk][2], m[1], 0.3))
        ground(dg, gk, HZ, path=o.get("path"))
        # mid trees (behind cast)
        tl = o.get("trees", "some")
        nt = {"none": 0, "few": 4, "some": 9, "many": 18, "forest": 30}[tl]
        leaf = (56, 140, 66) if kind != "eden" else (46, 150, 80)
        if sky in ("night",): leaf = (30, 70, 50)
        if sky in ("dusk", "golden"): leaf = (70, 100, 60)
        for i in range(nt):
            x = r.randrange(0, WW); h = r.randint(26, 54); yb = HZ + r.randint(-2, 10)
            tree(dg, x, yb, h, leaf, style=o.get("tree_style", r.choice(("round", "round", "pine" if kind != "eden" else "round"))), fruit=(230, 80, 60) if (kind == "eden" and r.random() < 0.3) else None, seed=i)
        for i in range(nt // 2 + 2):
            bush(dg, r.randrange(0, WW), HZ + r.randint(4, 22), r.randint(10, 20), mul(leaf, 1.1), flowers=(255, 220, 90) if kind == "eden" else None)
        if kind == "eden":
            for i in range(40): flower(dg, r.randrange(0, WW), HZ + r.randint(6, 80), ((240, 90, 120), (255, 220, 90), (200, 130, 240), (255, 255, 255))[i % 4])
        for i in range(int(WW / 24)): grass(dg, r.randrange(0, WW), HZ + r.randint(2, 82), GROUND[gk][2])
        for i in range(4): rock(dg, r.randrange(0, WW), HZ + r.randint(10, 70), r.randint(4, 9), r.randint(3, 6), (130, 126, 120) if sky != "night" else (60, 66, 80))
        if kind == "vineyard":
            for vx in range(60, WW, 40):
                dg.line([(vx, HZ + 30), (vx, HZ + 12)], fill=(90, 60, 36)); dg.ellipse([vx - 8, HZ + 6, vx + 8, HZ + 18], fill=(60, 120, 60))
                for k in range(3): dg.ellipse([vx - 6 + k * 4, HZ + 14, vx - 3 + k * 4, HZ + 17], fill=(110, 50, 120))
        for p in o.get("props", []):
            k = p[0]
            if k == "river":
                x0, x1 = p[1], p[2]
                dg.rectangle([x0, HZ + 2, x1, PH], fill=(50, 120, 200))
            elif k == "altar": altar(dg, p[1], p[2], p[3] if len(p) > 3 else 16)
            elif k == "tent": tent(dg, p[1], p[2])
            elif k == "city": city(dg, p[1], p[2], p[3], seed=p[4] if len(p) > 4 else 2)
            elif k == "tree": tree(dg, p[1], p[2], p[3], p[4] if len(p) > 4 else leaf, style=p[5] if len(p) > 5 else "round", fruit=p[6] if len(p) > 6 else None)
            elif k == "gate": gate(dg, p[1], p[2])
            elif k == "field":
                for fx in range(p[1], p[2], 6):
                    for fy in range(HZ + 8, PH, 10): dg.line([(fx, fy), (fx, fy - 5)], fill=(230, 200, 90)); dg.point((fx, fy - 6), fill=(255, 230, 120))
            elif k == "sheepfold":
                for fx in range(p[1], p[2], 8): dg.rectangle([fx, HZ + 14, fx + 2, HZ + 30], fill=(130, 90, 50))
                dg.rectangle([p[1], HZ + 18, p[2], HZ + 20], fill=(160, 110, 60)); dg.rectangle([p[1], HZ + 26, p[2], HZ + 28], fill=(160, 110, 60))
            elif k == "logs":
                for lx in range(p[1], p[1] + 60, 12): dg.rectangle([lx, p[2] - 8, lx + 40, p[2] - 4], fill=(150, 100, 56)); dg.line([(lx, p[2] - 8), (lx + 40, p[2] - 8)], fill=(190, 136, 80))
            elif k == "bricks":
                for by in range(3):
                    for bx in range(6): dg.rectangle([p[1] + bx * 7, p[2] - by * 5 - 4, p[1] + bx * 7 + 6, p[2] - by * 5], fill=(190, 120, 80)); dg.line([(p[1] + bx * 7, p[2] - by * 5 - 4), (p[1] + bx * 7 + 6, p[2] - by * 5 - 4)], fill=(220, 150, 100))
            elif k == "huts":
                for hx in range(p[1], p[2], 40): tent(dg, hx, HZ + 8, 16, 14, (160, 120, 80))
            elif k == "vines": pass
    elif kind == "void":
        pass
    elif kind == "sea":
        mountains(d, 11, HZ - 40, 30, m[0], m[1]) if o.get("mountains") else None
        ground(dg, "sand", HZ, path=None) if o.get("shore") else None
    elif kind == "cave":
        mountains(d, 11 + o.get("seed", 0), HZ - 30, 30, m[0], m[1])
        dm.rectangle([0, 0, WW, PH], fill=(46, 38, 40))
        for i in range(90):
            x0, y0 = r.randrange(-20, WW), r.randrange(-20, HZ); w_, h_ = r.randint(12, 46), r.randint(8, 30)
            dm.ellipse([x0, y0, x0 + w_, y0 + h_], fill=(54 + r.randint(0, 18), 46 + r.randint(0, 10), 46))
        # cave mouth showing the sky
        mx = 330
        dm.ellipse([mx - 90, 40, mx + 90, HZ + 80], fill=(0, 0, 0, 0))
        dm.arc([mx - 92, 38, mx + 92, HZ + 82], 180, 360, fill=(80, 68, 66), width=4)
        for i in range(14):
            sx = r.randrange(0, WW); L = r.randint(8, 26)
            if abs(sx - mx) < 95: continue
            dm.polygon([(sx - 4, 0), (sx + 4, 0), (sx, L)], fill=(66, 56, 56))
        ground(dg, "dirt", HZ)
        dg.rectangle([0, HZ, WW, HZ + 3], fill=(70, 58, 52))
    _ST[key] = (skyim, [Layer(0.25, far), Layer(0.5, mid), Layer(1.0, gnd)])
    return _ST[key]

# ------------------------------------------------------------------ dynamic world effects (drawn per frame on composite, world coords -> screen)
def fx_sky(d, base, o, t, lt, camx):
    sky = o.get("sky", "day"); kind = o.get("env", "meadow")
    # celestial
    cel = o.get("celestial", "auto")
    if cel == "auto":
        cel = {"day": "sun", "noon": "sun", "golden": "sun_low", "dusk": "sun_set", "dawn": "sun_rise", "night": "moon", "eden": "sun"}.get(sky, None)
    if cel == "sun": sun(d, 380 - camx * 0.1, 40, 14, t)
    elif cel == "sun_low": sun(d, 400 - camx * 0.1, 95, 16, t, (255, 200, 110))
    elif cel == "sun_set": sun(d, 120 - camx * 0.1, 150, 20, t, (255, 150, 90), rays=False)
    elif cel == "sun_rise": sun(d, 90 - camx * 0.1, 140 - 30 * ease(lt / 8), 16, t, (255, 190, 120))
    elif cel == "moon": moon(d, 400 - camx * 0.1, 44, 11)
    if sky in ("night", "void", "dusk"): stars(d, t, 70 if sky != "dusk" else 20, w=PW, ymax=HZ - 50 if sky != "dusk" else 60)
    # clouds
    if kind != "void" and sky not in ("fire",):
        nc = {"storm": 6, "grey": 5}.get(sky, 3)
        for i in range(nc):
            x = ((t * (2.5 + i * 0.7) + i * 160) % (PW + 160)) - 80 - camx * 0.15
            if sky in ("storm", "grey"): col, sh = (90, 96, 112), (60, 66, 84)
            elif sky == "night": col, sh = (40, 46, 80), (28, 32, 60)
            elif sky in ("dusk", "golden", "dawn"): col, sh = (255, 200, 170), (210, 140, 130)
            else: col, sh = (252, 252, 255), (210, 218, 238)
            cloud(d, x, 22 + (i % 3) * 18, 1.0 + 0.3 * (i % 3), col, sh)
    if sky in ("day", "noon", "eden", "golden", "dawn") and o.get("birds", True):
        for i in range(3): bird(d, ((t * (18 + i * 3) + i * 90) % (PW + 60)) - 30, 50 + 14 * math.sin(t * 1.2 + i) + i * 9, t, s=1.1)

def fx_rain(d, base, t, heavy=1.0, wind=0.3):
    r = np.random.RandomState(int(t * 30) % 1000)
    n = int(160 * heavy)
    xs = r.randint(0, PW, n); ys = r.randint(0, PH, n)
    for x, y in zip(xs, ys): d.line([(x, y), (x - int(6 * wind), y + 7)], fill=(180, 200, 235))
    a = np.asarray(base).astype(np.int16); a = a - int(12 * heavy); base.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))

def fx_flash(base, k):
    a = np.asarray(base).astype(np.int16) + int(110 * k); base.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))

def fx_glow(base, x, y, r, col, k=0.6):
    x0, x1 = int(max(0, x - r)), int(min(PW, x + r)); y0, y1 = int(max(0, y - r)), int(min(PH, y + r))
    if x1 <= x0 or y1 <= y0: return
    a = np.asarray(base).astype(np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    g = np.clip(1 - ((xx - x) ** 2 + (yy - y) ** 2) / (r * r), 0, 1) ** 2
    g = np.floor(g * 6) / 6.0
    a[y0:y1, x0:x1] += g[..., None] * np.array(col, np.float32) * k
    base.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))

def fx_shafts(base, t, x0=300, n=4, a=28, slant=0.5):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(n):
        sx = x0 + i * 40 + 6 * math.sin(t * 0.6 + i)
        od.polygon([(sx, 0), (sx + 16, 0), (sx - slant * HZ + 40 + i * 6, HZ + 20), (sx - slant * HZ + 14, HZ + 20)], fill=(255, 245, 200, a))
    base.paste(ov, (0, 0), ov)

def fx_motes(d, t, n=24, col=(255, 240, 170), seed=77, up=True):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(0, PW) + 6 * math.sin(t * 0.8 + i); y = (r.uniform(0, PH) + (-1 if up else 1) * t * (5 + i % 5)) % PH
        if int(t * 3 + i) % 4: d.point((int(x), int(y)), fill=col)

def fx_vignette_dark(base, k):
    a = np.asarray(base).astype(np.float32) * (1 - k); base.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))

def fx_fog(base, y0=HZ, k=0.35, col=(200, 205, 215)):
    a = np.asarray(base).astype(np.float32); f = np.clip((np.arange(PH)[:, None] - y0) / 60.0, 0, 1)[..., None] * k
    a = a * (1 - f) + np.array(col, np.float32) * f; base.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))

# ------------------------------------------------------------------ cast
IDLE = (10, 12)
def _arm_pt(side, a1, f, bob=0):
    shx, shy = 50 + side * 14.5, 48 + bob
    el = (shx + side * 16 * math.sin(math.radians(a1)), shy + 16 * math.cos(math.radians(a1)))
    a2 = a1 + f
    return (el[0] + side * 14 * math.sin(math.radians(a2)), el[1] + 14 * math.cos(math.radians(a2)))

def pose_for(act, k, side=1):
    """act -> (pose dict, extras dict). k = seconds since act start."""
    e = ease_c(k / 0.6)
    if act == "point": return {"ra": (92 + 4 * math.sin(k * 3), -6)}, {}
    if act == "point_up": return {"ra": (150, -10)}, {}
    if act == "raise": return {"la": (150 + 6 * math.sin(k * 3), -8), "ra": (150 + 6 * math.sin(k * 3 + 1), -8)}, {}
    if act == "praise": return {"la": (140 + 10 * math.sin(k * 2), -20), "ra": (140 + 10 * math.sin(k * 2 + 1.5), -20)}, {"look_up": True}
    if act == "cower": return {"la": (125, -100), "ra": (125, -100)}, {"rot": 8 * side, "sq": 0.94}
    if act == "hide_face": return {"la": (100, -120), "ra": (100, -120)}, {"rot": 4 * side}
    if act == "bow": return {"la": (12, -60), "ra": (12, -60)}, {"rot": 9 * e * side, "sq": 1 - 0.1 * e}
    if act == "kneel": return {"la": (30, 40), "ra": (30, 40)}, {"kneel": e}
    if act == "pray": return {"la": (-3 + 2 * math.sin(k * 0.8), -122), "ra": (-3 + 2 * math.sin(k * 0.8 + 0.4), -122)}, {"kneel": e}
    if act == "pray_stand": return {"la": (-3, -122), "ra": (-3, -122)}, {}
    if act == "prostrate": return {"la": (160, -10), "ra": (160, -10)}, {"prostrate": e}
    if act == "cheer": return {"la": (140 + 15 * math.sin(k * 7), -10), "ra": (140 + 15 * math.sin(k * 7 + 2), -10)}, {"hop": abs(math.sin(k * 7)) * 3}
    if act == "talk": return {"ra": (40 + 26 * math.sin(k * 3.1), -34 + 10 * math.sin(k * 5)), "la": (14 + 8 * math.sin(k * 2.3), 10)}, {}
    if act == "cross": return {"la": (92, 0), "ra": (92, 0)}, {}
    if act == "welcome": return {"la": (75, -8), "ra": (75, -8)}, {}
    if act == "hands": return {"la": (14, -84), "ra": (14, -84)}, {}
    if act == "carry": return {"la": (80, -40), "ra": (80, -40)}, {"carry": True}
    if act == "carry_log": return {"la": (95, -20), "ra": (95, -20)}, {"log": True}
    if act == "hammer":
        sw = 0.5 + 0.5 * math.sin(k * 7); return {"ra": (40 + 90 * sw, -30 - 40 * sw), "la": (30, -10)}, {"hammer": True, "hit": sw < 0.08}
    if act == "saw":
        sw = 0.5 + 0.5 * math.sin(k * 6); return {"ra": (60 + 30 * sw, -60), "la": (20, 10)}, {"hammer": True}
    if act == "dig":
        sw = 0.5 + 0.5 * math.sin(k * 4); return {"ra": (50 + 60 * sw, -20), "la": (50 + 60 * sw, -20)}, {"hoe": True, "rot": 10 * sw * side}
    if act == "eat":
        return {"ra": (62, -95), "la": (14, 10)}, {"fruit": True}
    if act == "hold_fruit": return {"ra": (75, -40)}, {"fruit": True}
    if act == "offer": return {"la": (80, -20), "ra": (80, -20)}, {"offer": True}
    if act == "strike":
        sw = ease_c(k / 0.25); return {"ra": (160 - 150 * sw, -20)}, {"rot": 10 * sw * side}
    if act == "fall":
        f = ease_c(k / 0.5); return {"la": (100 * f, -10), "ra": (100 * f, -10)}, {"fall": f}
    if act == "lie": return {"la": (6, 8), "ra": (6, 8)}, {"fall": 1.0}
    if act == "sleep": return {"la": (20, 20), "ra": (20, 20)}, {"fall": 1.0, "sleep": True}
    if act == "wave": return {"ra": (150, 20 * math.sin(k * 8))}, {}
    if act == "shield_eyes": return {"ra": (120, -110)}, {}
    if act == "look_up": return None, {"look_up": True}
    if act == "flee": return {"la": (90, -20), "ra": (90, -20)}, {"run": True}
    if act == "hug": return {"la": (80, -60), "ra": (80, -60)}, {}
    if act == "shout": return {"la": (120, -100), "ra": (120, -100)}, {"hop": abs(math.sin(k * 10)) * 1.5}
    if act == "laugh": return {"la": (30, -60), "ra": (30, -60)}, {"rot": -4 * side * (0.5 + 0.5 * math.sin(k * 9)), "hop": abs(math.sin(k * 9)) * 1.0}
    if act == "stagger": return {"la": (60, -30), "ra": (60, -30)}, {"rot": 14 * math.sin(k * 2.2), "sq": 0.98}
    if act == "cover": return {"la": (100, -30), "ra": (100, -30)}, {"cloth": True}
    if act == "pitch":
        sw = 0.5 + 0.5 * math.sin(k * 3); return {"ra": (70 + 20 * sw, -40 + 30 * sw)}, {"brush": True}
    return None, {}


# ---------------------------------------------------------------- natural arm motion
def _ease_back(x, o=1.25):
    x = min(max(x, 0.0), 1.0); x -= 1.0
    return x * x * ((o + 1) * x + o) + 1.0

def _nz(t, seed):
    """slow organic wobble in degrees (sum of incommensurate sines)"""
    return 2.6 * math.sin(t * 1.13 + seed) + 1.7 * math.sin(t * 2.71 + seed * 1.9) + 0.9 * math.sin(t * 4.3 + seed * 3.1)

_TALK_G = ((26, 55), (36, 78), (18, 42), (42, 96), (12, -70), (30, 64), (22, 20), (48, 70))

def _talk_pose(k, seed, side):
    """speech gestures: hold / move / hold, like a real speaker"""
    seg = 1.1 + 0.35 * math.sin(seed)
    i = int(k / seg); f = (k - i * seg) / seg
    r0, r1 = random.Random(seed * 131 + i), random.Random(seed * 131 + i + 1)
    a0, b0 = _TALK_G[r0.randrange(len(_TALK_G))]
    a1, b1 = _TALK_G[r1.randrange(len(_TALK_G))]
    m = ease_c(min(1.0, f / 0.45))
    ra = (a0 + (a1 - a0) * m, b0 + (b1 - b0) * m)
    lg = r0.random() < 0.35  # off hand joins sometimes
    la = (14 + 14 * m, 14 + 40 * m) if lg else (12, 14)
    return {"ra": ra, "la": la}

def _idle_arm(t, s_, walk):
    ph = t * 5.0
    sway = math.sin(ph + (math.pi if s_ < 0 else 0)) * walk * 14
    return (10 + 2 * math.sin(t * 1.7 + s_) + sway, 12)

def natural_pose(c, act, k, prev_act, prev_k, side, t, walk, seed):
    """pose_for + transition blend with slight overshoot, arm asymmetry, organic wobble, elbow follow-through"""
    def raw(a, kk, lag=0.0):
        if a == "talk":
            tp = _talk_pose(max(0.0, kk - lag), seed, side)
            if cast5.SPECS.get(c["n"], {}).get("prop") in ("scepter", "rod", "spear", "staff", "crook", "tablets"):
                tp = {"la": tp["ra"]}  # gesture with the free hand
            return tp, {}
        p, e = pose_for(a, max(0.0, kk - lag), side)
        return (p or {}), e
    cur_l, ex = raw(act, k)
    cur_r, _ = raw(act, k, 0.09)  # right arm trails the left a little
    cur = {}
    if "la" in cur_l: cur["la"] = cur_l["la"]
    if "ra" in cur_r: cur["ra"] = cur_r["ra"]
    T = 0.42
    blend = _ease_back(k / T) if (prev_act is not None and k < T) else 1.0
    prv = {}
    if prev_act is not None and k < T:
        pl, _ = raw(prev_act, prev_k); pr_, _ = raw(prev_act, prev_k, 0.09)
        if "la" in pl: prv["la"] = pl["la"]
        if "ra" in pr_: prv["ra"] = pr_["ra"]
    out = {}
    for s_, key in ((-1, "la"), (1, "ra")):
        if key not in cur and key not in prv: continue
        idle = _idle_arm(t, s_, walk)
        a = cur.get(key, idle); b = prv.get(key, idle)
        bl = blend if key == "la" else _ease_back(max(0.0, k - 0.06) / T) if (prev_act is not None and k < T + 0.06) else 1.0
        a1 = b[0] + (a[0] - b[0]) * bl; f = b[1] + (a[1] - b[1]) * bl
        # follow-through: forearm lags upper-arm swing
        if prev_act is not None and k < T + 0.2:
            v = (a[0] - b[0]) * (1 - min(1.0, k / (T + 0.2)))
            f += clamp(-0.18 * v, -14, 14)
        if key not in cur:  # returning to rest: let the idle code take over once settled
            if bl >= 0.999: continue
        sd = seed + (0 if key == "la" else 7.3)
        a1 += _nz(t, sd) * (0.6 if act in ("pray", "pray_stand", "hands", "cross", "kneel") else 1.0)
        f += 0.6 * _nz(t * 1.2, sd + 2)
        out[key] = (a1, f)
    return (out or None), ex

def resolve_t(spec, beat_start):
    if isinstance(spec, (int, float)): return float(spec)
    b, off = spec; return beat_start[b] + off

def cast_member(base, c, t, lt, beat_start, speaker_amp, camx, speaking_name=None, ctx=None):
    name = c["n"]; x = c["x"]; y = c["y"]; s = c.get("s", 0.72); fl = c.get("flip", 0)
    acts = c.get("acts", [])
    act, t0 = c.get("idle", "idle"), 0.0
    prev_act, prev_t0 = None, 0.0
    for a in acts:
        ta = resolve_t(a[0], beat_start)
        if lt >= ta: prev_act, prev_t0 = act, t0; act, t0 = a[1], ta
    walk = 0.0; run = False
    if "walk" in c:
        for wk in (c["walk"] if isinstance(c["walk"][0], (list, tuple)) else [c["walk"]]):
            a, b, xt = resolve_t(wk[0], beat_start), resolve_t(wk[1], beat_start), wk[2]
            if lt < a: break
            if lt < b:
                f = (lt - a) / (b - a); x = x + (xt - x) * f; walk = 1.0
                if len(wk) > 3: y = y + (wk[3] - y) * f
                break
            x = xt
            if len(wk) > 3: y = wk[3]
    if "glide" in c and c["glide"]:
        ga, gb, gx, gy = resolve_t(c["glide"][0], beat_start), resolve_t(c["glide"][1], beat_start), c["glide"][2], c["glide"][3]
        if lt >= gb: x, y = gx, gy
        elif lt >= ga:
            f = ease_c((lt - ga) / (gb - ga)); x = x + (gx - x) * f; y = y + (gy - y) * f
    if "show" in c:
        ta, tb = resolve_t(c["show"][0], beat_start), resolve_t(c["show"][1], beat_start)
        if not (ta <= lt < tb): return
    if "hide" in c and lt >= resolve_t(c["hide"], beat_start): return
    k_ = lt - t0
    seed_ = (sum(map(ord, name)) % 97) * 0.37 + c.get("seed", 0)
    pose, ex = natural_pose(c, act, k_, prev_act, t0 - prev_t0, side=(-1 if fl else 1), t=t, walk=0.0, seed=seed_)
    if ex.get("run"): walk = 1.0
    amp = speaker_amp if (speaking_name == name) else 0.0
    if "scream" in c:
        sa, sb = resolve_t(c["scream"][0], beat_start), resolve_t(c["scream"][1], beat_start)
        if sa <= lt <= sb: amp = 0.7 + 0.3 * math.sin(t * 25); pose = pose or {"la": (120, -100), "ra": (120, -100)}
    blink = (t * 0.9 + c.get("seed", 0) * 0.37) % 3.4 < 0.12
    look = c.get("look", 0.0)
    if ex.get("look_up"): look = 0.0
    sp_name = name
    if c.get("eden") and name in ("Adam", "Eve"): sp_name = name + "0"
    tt = t + c.get("seed", 0)
    arr = cast5.sprite(sp_name, tt, amp, blink, pose or None, walk=(2.0 if ex.get("run") else walk), look=look)
    im = Image.fromarray(arr, "RGBA")
    # extras drawn on sprite canvas (100x120) before scaling
    if ex.get("hammer") or ex.get("hoe") or ex.get("fruit") or ex.get("brush") or ex.get("log") or ex.get("carry") or ex.get("offer") or ex.get("cloth"):
        dd = ImageDraw.Draw(im); side = 1
        pr = pose or {}
        a1, f = pr.get("ra", IDLE); hx, hy = _arm_pt(1, a1, f)
        if ex.get("hammer"):
            ang = math.radians(a1 + f - 90); L = 18
            ex_, ey_ = hx + L * math.sin(math.radians(a1 + f)), hy - L * math.cos(math.radians(a1 + f)) * 0 + L * 0.2 * math.cos(math.radians(a1 + f))
            dd.line([(hx, hy), (ex_, ey_ - 6)], fill=(120, 84, 50), width=3); dd.rectangle([ex_ - 6, ey_ - 12, ex_ + 6, ey_ - 4], fill=(90, 90, 100), outline=OUT)
        if ex.get("hoe"):
            dd.line([(hx, hy), (hx + 14, hy + 30)], fill=(120, 84, 50), width=3); dd.rectangle([hx + 10, hy + 28, hx + 22, hy + 34], fill=(110, 110, 120), outline=OUT)
        if ex.get("fruit"): apple(dd, hx + 1, hy + 2, bitten=ctx.get("bitten", False) if ctx else False)
        if ex.get("brush"):
            dd.line([(hx, hy), (hx + 6, hy + 18)], fill=(120, 84, 50), width=2); dd.rectangle([hx + 3, hy + 16, hx + 11, hy + 22], fill=(30, 26, 26))
        if ex.get("log") or ex.get("carry"):
            lx, ly = _arm_pt(-1, *pr.get("la", IDLE))
            if ex.get("log"): dd.rectangle([lx - 40, (ly + hy) / 2 - 5, hx + 40, (ly + hy) / 2 + 3], fill=(150, 100, 56), outline=OUT); dd.line([(lx - 40, (ly + hy) / 2 - 5), (hx + 40, (ly + hy) / 2 - 5)], fill=(190, 136, 80))
            else: dd.rectangle([lx - 6, (ly + hy) / 2 - 8, hx + 6, (ly + hy) / 2 + 8], fill=(200, 160, 100), outline=OUT); dd.line([(lx - 6, (ly + hy) / 2), (hx + 6, (ly + hy) / 2)], fill=(160, 120, 70))
        if ex.get("offer"):
            lx, ly = _arm_pt(-1, *pr.get("la", IDLE)); cx_, cy_ = (lx + hx) / 2, (ly + hy) / 2 - 2
            if c.get("offer") == "grain":
                for k in range(-6, 7, 3): dd.line([(cx_ + k, cy_ + 4), (cx_ + k * 1.3, cy_ - 8)], fill=(230, 200, 90)); dd.point((int(cx_ + k * 1.3), int(cy_ - 9)), fill=(255, 230, 120))
            else:
                dd.ellipse([cx_ - 9, cy_ - 6, cx_ + 9, cy_ + 4], fill=(240, 240, 235), outline=OUT); dd.ellipse([cx_ + 6, cy_ - 7, cx_ + 12, cy_ - 1], fill=(50, 50, 55))
        if ex.get("cloth"):
            lx, ly = _arm_pt(-1, *pr.get("la", IDLE)); cx2 = (lx + hx) // 2
            if name not in ("Adam", "Eve"):
                dd.rectangle([lx - 8, ly - 4, hx + 8, ly + 26], fill=(150, 110, 70), outline=OUT)
            else:
              for ox_, oy_ in ((-7, 0), (0, 3), (7, 0), (-3, 8), (4, 8)):
                dd.ellipse([cx2 + ox_ - 5, ly + oy_ - 4, cx2 + ox_ + 5, ly + oy_ + 6], fill=(70, 150, 60), outline=(30, 80, 35))
    sq = ex.get("sq", 1.0)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s * sq))), Image.NEAREST)
    if ex.get("rot"): im = im.rotate(-ex["rot"], resample=Image.NEAREST, expand=True, center=(im.width / 2, im.height))
    if fl: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    hop = ex.get("hop", 0)
    yy = y - im.height + 3 - hop
    if ex.get("kneel"):
        kn = ex["kneel"]; cut = int(26 * s * kn)
        im = im.crop((0, 0, im.width, im.height - cut)); yy = y - im.height + 3
        dd = ImageDraw.Draw(im)  # knees bump
        if kn > 0.5:
            kc = (140, 100, 70); dd.ellipse([im.width * 0.3, im.height - 6, im.width * 0.48, im.height - 1], fill=kc); dd.ellipse([im.width * 0.52, im.height - 6, im.width * 0.7, im.height - 1], fill=kc)
    if ex.get("prostrate"):
        pr_ = ex["prostrate"]; ang = 70 * pr_ * (-1 if fl else 1)
        im = im.rotate(ang, resample=Image.NEAREST, expand=True); yy = y - im.height + 3 + int(6 * pr_)
    if ex.get("fall"):
        f = ex["fall"]; ang = 88 * f * (-1 if fl else 1)
        im = im.rotate(ang, resample=Image.NEAREST, expand=True); yy = y - im.height + 3 + int(4 * f)
    base.paste(im, (int(x - im.width / 2 - camx), int(yy)), im)
    if ex.get("sleep") and int(t * 1.5) % 2 == 0:
        dz = ImageDraw.Draw(base); dz.text((int(x - camx + 10), int(yy - 8 - (t * 6) % 10)), "z", fill=(240, 240, 255))
    return (x - camx, yy)

# ------------------------------------------------------------------ frame compose
def compose(o, t, lt, beat_start, speaker_amp=0.0, speaking=None, ctx=None):
    """o: scene dict. returns RGB 480x270 image (before text/narrator)."""
    skyim, layers = build_env(o)
    base = Image.new("RGB", (PW, PH), (0, 0, 0)); base.paste(skyim, (0, 0))
    cam = o.get("cam")
    camx = 0.0
    if cam:
        x0, x1 = cam[0], cam[1]; dur = cam[2] if len(cam) > 2 else max(1.0, ctx.get("scene_dur", 10) if ctx else 10)
        camx = x0 + (x1 - x0) * ease_c(lt / dur)
    d = ImageDraw.Draw(base)
    kind = o.get("env")
    # --- sky dynamic layer
    if kind == "void":
        base.paste(gradient(PW, PH, (3, 4, 14), (10, 16, 46)), (0, 0)); d = ImageDraw.Draw(base)
        water(d, 0, PW, HZ - 30, PH, t, (8, 14, 46), (20, 32, 80), (50, 70, 130), 0.6)
        stars(d, t, 50, w=PW, ymax=HZ - 60, col=(120, 130, 190))
        # Spirit hovering: soft moving glow
        gx = PW / 2 + 40 * math.sin(t * 0.5); gy = HZ - 70 + 10 * math.sin(t * 0.8)
        fx_glow(base, gx, gy, 70 + 10 * math.sin(t), (120, 150, 255), 0.5); d = ImageDraw.Draw(base)
        fx_motes(d, t, 18, (150, 170, 240))
    elif kind == "sea":
        d = ImageDraw.Draw(base)
        fx_sky(d, base, o, t, lt, camx)
        storm = o.get("sky") == "storm"
        lvl = o.get("level", HZ - 20)
        if callable(lvl): lvl = lvl(lt)
        water(d, 0, PW, int(lvl), PH, t, (20, 50, 90) if storm else (30, 100, 180), (60, 90, 130) if storm else (90, 170, 230), (150, 180, 220) if storm else (210, 240, 255), 2.5 if storm else 1.0)
        if storm:
            for k in range(3):
                yy = int(lvl) + 2 + k * 12
                for x in range(0, PW, 2):
                    if math.sin(x * 0.08 + t * 6 + k) > 0.85: d.line([(x, yy + int(4 * math.sin(x * 0.2 + t * 8))), (x + 1, yy)], fill=(230, 240, 255))
        for lyr in layers:
            if lyr.par < 1.0: base.paste(lyr.im, (int(-camx * lyr.par), 0), lyr.im)
        if o.get("shore"):
            for lyr in layers:
                if lyr.par == 1.0: base.paste(lyr.im, (int(-camx * lyr.par), 0), lyr.im)
    else:
        fx_sky(d, base, o, t, lt, camx)
        for lyr in layers: base.paste(lyr.im, (int(-camx * lyr.par), 0), lyr.im)
    d = ImageDraw.Draw(base)
    # --- world props with animation (drawn in world coords - camx)
    for p in o.get("dyn", []):
        k = p[0]
        if k == "river":
            x0, x1 = p[1] - camx, p[2] - camx
            water(d, int(x0), int(x1), HZ + 2 if len(p) < 4 else p[3], PH, t, (50, 120, 200), (110, 180, 240), (220, 245, 255))
        elif k == "lake":
            water(d, int(p[1] - camx), int(p[2] - camx), p[3], p[4], t, (50, 120, 200), (110, 180, 240), (220, 245, 255))
        elif k == "fire":
            fire(d, p[1] - camx, p[2], t, p[3] if len(p) > 3 else 1.0)
            fx_glow(base, p[1] - camx, p[2] - 8, 36, (255, 140, 60), 0.4); d = ImageDraw.Draw(base)
        elif k == "smoke":
            ta = resolve_t(p[3], beat_start) if len(p) > 3 else 0
            if lt >= ta: smoke(d, p[1] - camx, p[2], t - ta, rise=p[4] if len(p) > 4 else 1.0, drift=p[5] if len(p) > 5 else 0.0, up=p[6] if len(p) > 6 else True)
        elif k == "ark":
            st = p[3]
            if callable(st): st = st(lt)
            ark(d, p[1] - camx, p[2], t, st, doors_open=p[4] if len(p) > 4 else True, float_t=(t if len(p) > 5 and p[5] else None))
        elif k == "tower":
            st = p[3]
            if callable(st): st = st(lt)
            tower(d, p[1] - camx, p[2], st, t)
        elif k == "tree_life":
            tree(d, p[1] - camx, p[2], p[3], (40, 150, 90), style="round", t=t, fruit=(255, 220, 90), seed=3)
            fx_glow(base, p[1] - camx, p[2] - p[3] * 0.8, 40, (255, 240, 160), 0.35); d = ImageDraw.Draw(base)
        elif k == "tree_know":
            tree(d, p[1] - camx, p[2], p[3], (36, 110, 60), style="round", t=t, fruit=(230, 50, 60), seed=4)
        elif k == "serpent":
            ta = resolve_t(p[3], beat_start) if len(p) > 3 else 0
            if lt >= ta: serpent(d, p[1] - camx, p[2], t)
        elif k == "cherub_sword":
            sword_flame(d, p[1] - camx, p[2], t)
            fx_glow(base, p[1] - camx, p[2] - 10, 30, (255, 150, 60), 0.3); d = ImageDraw.Draw(base)
        elif k == "animals_line":
            # procession of pairs walking to x_end
            ta = resolve_t(p[1], beat_start); speed = p[2]; xend = p[3]; y0 = p[4]
            kinds = cast5.ARK_ANIMALS
            for i, kd in enumerate(kinds):
                for j in range(2):
                    xs = -40 - i * 46 - j * 18 + (lt - ta) * speed
                    if xs > xend: continue
                    paste_animal(base, kd, xs - camx, y0 + (i % 3) * 5, t + i, walk=1.0, s=0.9 - 0.05 * (i % 3))
            d = ImageDraw.Draw(base)
        elif k == "animals_graze":
            for i, (kd, ax, ay) in enumerate(p[1]):
                paste_animal(base, kd, ax - camx + 3 * math.sin(t * 0.3 + i), ay, t + i, walk=0.3 if int(t * 0.2 + i) % 2 else 0.0, flip=i % 2)
            d = ImageDraw.Draw(base)
        elif k == "bird_fly":
            ta = resolve_t(p[1], beat_start); x0, y0, x1, y1, dur = p[2:7]; kd = p[7] if len(p) > 7 else "dove"
            if ta <= lt <= ta + dur + 0.5:
                f = ease_c((lt - ta) / dur); dove_sprite(base, x0 + (x1 - x0) * f - camx, y0 + (y1 - y0) * f - 10 * math.sin(math.pi * f), t, kd, flip=(x1 < x0))
            d = ImageDraw.Draw(base)
        elif k == "rainbow":
            ta = resolve_t(p[1], beat_start)
            if lt >= ta: rainbow(d, PW / 2 - camx * 0.1, HZ + 10, 170, base, ease((lt - ta) / 2.5))
            d = ImageDraw.Draw(base)
        elif k == "flood_water":
            lvl = p[1](lt); water(d, 0, PW, int(lvl), PH, t, (24, 60, 100), (60, 100, 140), (160, 190, 230), 2.2)
        elif k == "mound":
            mx, my, mw, mh = p[1] - camx, p[2], p[3], p[4]
            d.polygon([(mx - mw, my + mh), (mx - mw * 0.7, my + 4), (mx - mw * 0.3, my), (mx + mw * 0.3, my), (mx + mw * 0.7, my + 5), (mx + mw, my + mh)], fill=(118, 112, 104))
            d.line([(mx - mw * 0.7, my + 4), (mx - mw * 0.3, my), (mx + mw * 0.3, my)], fill=(160, 154, 146))
            for k_ in range(6): d.ellipse([mx - mw * 0.6 + k_ * mw * 0.22, my + 8 + (k_ % 2) * 9, mx - mw * 0.6 + k_ * mw * 0.22 + 5, my + 11 + (k_ % 2) * 9], fill=(90, 86, 80))
        elif k == "grave":
            d.rectangle([p[1] - camx - 10, p[2] - 3, p[1] - camx + 10, p[2]], fill=(110, 86, 58)); d.ellipse([p[1] - camx - 6, p[2] - 9, p[1] - camx + 6, p[2] - 1], fill=(130, 126, 120))
        elif k == "sun_rise_big":
            f = ease((lt - resolve_t(p[1], beat_start)) / 4); sun(d, PW * 0.3, HZ + 20 - 60 * f, 22, t, (255, 220, 110))
            fx_glow(base, PW * 0.3, HZ + 20 - 60 * f, 90, (255, 200, 120), 0.5 * f); d = ImageDraw.Draw(base)
        elif k == "sun_moon_day4":
            f = ease(lt / 6); sun(d, 90, 140 - 90 * f, 20, t); moon(d, 380, 150 - 100 * f, 12); stars(d, t, 40, w=PW, ymax=HZ - 60)
            fx_glow(base, 90, 140 - 90 * f, 80, (255, 220, 140), 0.45 * f); d = ImageDraw.Draw(base)
        elif k == "light_burst":
            ta = resolve_t(p[1], beat_start)
            if lt >= ta:
                rr = ease((lt - ta) / 2.0)
                fx_glow(base, PW / 2, HZ - 60, 60 + 300 * rr, (255, 250, 220), 0.9 * rr); d = ImageDraw.Draw(base)
                for a in range(0, 360, 15):
                    aa = math.radians(a + t * 10)
                    if rr > 0.1: d.line([(PW / 2, HZ - 60), (PW / 2 + 400 * math.cos(aa), HZ - 60 + 400 * math.sin(aa))], fill=lerpc((255, 250, 220), (255, 255, 255), rr))
        elif k == "fish":
            for i in range(p[1]):
                ph = (t * 0.5 + i * 0.23) % 1; xx = 30 + i * 60 + 14 * ph - camx; yy = p[2] - 40 * 4 * ph * (1 - ph)
                col = ((255, 150, 60), (120, 255, 255), (255, 210, 90), (200, 120, 230))[i % 4]
                d.ellipse([xx - 6, yy - 3, xx + 6, yy + 3], fill=col); d.polygon([(xx - 6, yy), (xx - 11, yy - 4), (xx - 11, yy + 4)], fill=col); d.point((int(xx + 3), int(yy - 1)), fill=(20, 20, 30))
        elif k == "whale":
            xx = (t * 10) % (PW + 200) - 100 - camx; yy = p[1]
            d.ellipse([xx - 40, yy - 12, xx + 40, yy + 12], fill=(60, 80, 120)); d.polygon([(xx - 40, yy), (xx - 56, yy - 12), (xx - 56, yy + 12)], fill=(60, 80, 120))
            if int(t * 2) % 3 == 0: d.line([(xx + 10, yy - 12), (xx + 10, yy - 26)], fill=(200, 230, 255))
        elif k == "plants_grow":
            ta = resolve_t(p[1], beat_start); f = ease((lt - ta) / 4)
            r = random.Random(9)
            for i in range(26):
                x = r.randrange(0, PW); yb = HZ + r.randint(2, 70); h = int(r.randint(20, 50) * f)
                tree(d, x, yb, h, (50, 140, 66), style=r.choice(("round", "round", "pine")), t=t, seed=i)
            for i in range(40):
                x = r.randrange(0, PW); yb = HZ + r.randint(4, 80)
                if f > 0.3: flower(d, x, yb, ((240, 90, 120), (255, 220, 90), (200, 130, 240))[i % 3], t, int(6 * f))
        elif k == "land_rise":
            ta = resolve_t(p[1], beat_start); f = ease((lt - ta) / 4)
            water(d, 0, PW, HZ - 10, PH, t, (30, 90, 170), (80, 150, 220), (200, 235, 255))
            pts = ridge_pts(31, HZ + 40 - 60 * f, 30 * f, PW, 1.2)
            d.polygon(pts + [(PW, PH), (0, PH)], fill=(110, 150, 70));
            for (x, y), (x2, y2) in zip(pts, pts[1:]):
                if y2 < y: d.line([(x, y), (x2, y2)], fill=(150, 190, 90))
        elif k == "firmament":
            f = ease(lt / 5)
            water(d, 0, PW, int(HZ - 10 + 0 * f), PH, t, (30, 90, 170), (80, 150, 220), (200, 235, 255))
            # waters above: clouds band rising
            for i in range(8):
                cloud(d, (i * 70 + t * 3) % (PW + 100) - 50, 120 - 90 * f + (i % 2) * 12, 1.2, (240, 245, 255), (200, 210, 235))
        elif k == "birds_many":
            for i in range(p[1]): bird(d, ((t * (16 + i * 2) + i * 50) % (PW + 60)) - 30, 30 + 18 * math.sin(t * 1.1 + i) + (i % 5) * 12, t, s=1.3)
        elif k == "butterflies":
            for i in range(p[1]):
                x = 20 + (t * 8 + i * 70) % (PW - 40); y = HZ - 30 + 12 * math.sin(t + i)
                w = int(1 + 2 * abs(math.sin(t * 12 + i))); col = ((255, 160, 80), (255, 255, 255), (170, 130, 240))[i % 3]
                d.ellipse([x - w - 1, y - 2, x, y + 1], fill=col); d.ellipse([x, y - 2, x + w + 1, y + 1], fill=col)
        elif k == "sparkle_form":
            ta = resolve_t(p[1], beat_start); k_ = lt - ta
            if 0 <= k_ < 1.6:
                for i in range(16):
                    a = i * 2.4 + t * 3; rr = 26 * ((k_ * 1.2 + i * 0.13) % 1)
                    px, py = p[2] - camx + rr * math.cos(a), p[3] - 20 - rr * 0.8 * abs(math.sin(a))
                    d.point((int(px), int(py)), fill=(255, 240, 160)); d.point((int(px) + 1, int(py)), fill=(255, 215, 110))
                fx_glow(base, p[2] - camx, p[3] - 25, 30, (255, 240, 180), 0.6 * (1 - k_ / 1.6)); d = ImageDraw.Draw(base)
        elif k == "glow":
            ta = resolve_t(p[1], beat_start) if len(p) > 4 else -1
            if lt >= ta: fx_glow(base, p[2] - camx, p[3], p[4], p[5] if len(p) > 5 else (255, 240, 180), p[6] if len(p) > 6 else 0.5); d = ImageDraw.Draw(base)
        elif k == "god_light":
            # light from above: shafts + glow at top center, pulsing with speech
            ta = resolve_t(p[1], beat_start) if len(p) > 1 else 0
            if lt >= ta:
                kk = 0.5 + 0.5 * ease((lt - ta) / 1.0)
                fx_shafts(base, t, x0=int(PW * 0.35), n=5, a=int(40 * kk), slant=0.15); fx_glow(base, PW / 2, -40, 150, (255, 245, 200), 0.5 * kk + 0.3 * speaker_amp * (1 if speaking == "God" else 0)); d = ImageDraw.Draw(base)
        elif k == "stone_pile":
            for i in range(p[3]): d.ellipse([p[1] - camx + (i % 3) * 7 - 8, p[2] - 4 - (i // 3) * 4, p[1] - camx + (i % 3) * 7 - 1, p[2] - (i // 3) * 4], fill=(140, 132, 124))
        elif k == "well":
            wx, wy = p[1] - camx, p[2]
            d.rectangle([wx - 18, wy - 14, wx + 18, wy], fill=(132, 124, 112)); d.ellipse([wx - 18, wy - 20, wx + 18, wy - 8], fill=(150, 142, 128))
            d.ellipse([wx - 13, wy - 18, wx + 13, wy - 10], fill=(30, 50, 70)); d.line([(wx - 8, wy - 15), (wx - 2, wy - 15)], fill=(140, 190, 230) if int(t * 2) % 2 else (90, 140, 190))
            for yy in range(wy - 12, wy, 4): d.line([(wx - 18, yy), (wx + 18, yy)], fill=(108, 100, 90))
            d.line([(wx - 15, wy - 14), (wx - 15, wy - 38)], fill=(110, 76, 44), width=2); d.line([(wx + 15, wy - 14), (wx + 15, wy - 38)], fill=(110, 76, 44), width=2)
            d.line([(wx - 17, wy - 38), (wx + 17, wy - 38)], fill=(130, 90, 52), width=2); d.line([(wx, wy - 38), (wx, wy - 24)], fill=(200, 180, 130))
            d.rectangle([wx - 3, wy - 26, wx + 3, wy - 21], fill=(120, 84, 50))
        elif k == "pyramids":
            px0 = p[1] - camx * 0.35
            for i, (ox, sz) in enumerate(((0, p[3]), (p[3] * 1.3, p[3] * 0.75), (-p[3] * 1.1, p[3] * 0.55))):
                cx, sz = px0 + ox, int(sz)
                d.polygon([(cx - sz, p[2]), (cx, p[2] - sz * 0.8), (cx + sz, p[2])], fill=(214, 184, 128))
                d.polygon([(cx, p[2] - sz * 0.8), (cx + sz, p[2]), (cx + sz * 0.2, p[2])], fill=(178, 148, 98))
        elif k == "stars_many":
            ta = resolve_t(p[1], beat_start); kk = ease((lt - ta) / 4.0) if lt >= ta else 0.0
            r = random.Random(9)
            for i in range(int(40 + 360 * kk)):
                sx, sy = r.randrange(0, PW), r.randrange(0, HZ - 10); tw = 0.5 + 0.5 * math.sin(t * (1.5 + r.random() * 3) + i)
                c = int(150 + 105 * tw); d.point((sx, sy), fill=(c, c, min(255, c + 20)))
                if r.random() < 0.06: d.point((sx + 1, sy), fill=(c, c, 255)); d.point((sx, sy + 1), fill=(c, c, 255))
        elif k == "fire_rain":
            ta = resolve_t(p[1], beat_start)
            if lt >= ta:
                kk = ease((lt - ta) / 2.0); r = random.Random(4)
                for i in range(int(36 * kk)):
                    sp = 60 + r.random() * 50; ph = r.random() * 10
                    fx = (r.randrange(-40, PW + 40) + (lt * sp * 0.35 + ph * 30)) % (PW + 80) - 40
                    fy = ((lt + ph) * sp) % (PH + 40) - 20
                    d.line([(fx - 7, fy - 14), (fx, fy)], fill=(255, 150, 40), width=2); d.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=(255, 235, 140))
                fx_glow(base, PW * 0.6, HZ - 20, 220, (255, 110, 30), 0.35 * kk); d = ImageDraw.Draw(base)
        elif k == "salt_pillar":
            ta = resolve_t(p[3], beat_start)
            if lt >= ta:
                sx, sy = p[1] - camx, p[2]; a = ease((lt - ta) / 0.8)
                col = lerpc((255, 255, 255), (226, 224, 216), a)
                d.polygon([(sx - 9, sy), (sx - 7, sy - 30), (sx - 5, sy - 44), (sx + 5, sy - 44), (sx + 7, sy - 30), (sx + 9, sy)], fill=col)
                d.ellipse([sx - 6, sy - 56, sx + 6, sy - 42], fill=col); d.line([(sx + 4, sy - 44), (sx + 6, sy - 4)], fill=(190, 188, 180))
                if lt - ta < 0.6: fx_glow(base, sx, sy - 30, 40, (255, 255, 255), 0.8 * (1 - (lt - ta) / 0.6)); d = ImageDraw.Draw(base)
        elif k == "ram":
            rx, ry = p[1] - camx, p[2]
            bush(d, rx, ry, 30, leaf=(70, 110, 50), t=t)
            paste_animal(base, "sheep", rx + 2 * math.sin(t * 6), ry - 2, t, walk=0.0, s=1.0); d = ImageDraw.Draw(base)
            for sgn in (-1, 1): d.arc([rx + sgn * 6 - 5, ry - 24, rx + sgn * 6 + 5, ry - 14], 0, 300, fill=(200, 180, 140), width=2)
            for i in range(5): d.line([(rx - 16 + i * 8, ry - 4), (rx - 10 + i * 6, ry - 20)], fill=(90, 70, 40))
        elif k == "caravan":
            ta = resolve_t(p[1], beat_start); speed = p[2]; x0 = p[3]; y0 = p[4]; kinds = p[5]
            for i, kd in enumerate(kinds):
                xs = x0 - i * 40 + max(0.0, lt - ta) * speed
                paste_animal(base, kd, xs - camx, y0 + (i % 2) * 4, t + i, walk=1.0 if lt >= ta else 0.0, flip=speed < 0, s=0.95)
            d = ImageDraw.Draw(base)
        elif k == "wood":
            wx, wy = p[1] - camx, p[2]
            for i in range(6): d.line([(wx - 14 + i, wy - i * 2), (wx + 14 - i, wy - i * 2 - 1)], fill=(120, 80, 44) if i % 2 else (150, 104, 60), width=2)
        elif k == "flock":
            for i in range(p[1]):
                paste_animal(base, "sheep", p[2] + i * 22 - camx + 2 * math.sin(t * 0.4 + i), p[3] + (i % 2) * 6, t + i, walk=0.0, flip=i % 2);
            d = ImageDraw.Draw(base)
        elif k == "bricks_stack":
            n = int(p[3](lt)) if callable(p[3]) else p[3]
            for i in range(n):
                bx = p[1] - camx + (i % 5) * 8; by = p[2] - (i // 5) * 5
                d.rectangle([bx, by - 4, bx + 6, by], fill=(190, 120, 80)); d.line([(bx, by - 4), (bx + 6, by - 4)], fill=(220, 150, 100))
        elif k == "fog": fx_fog(base, p[1], p[2]); d = ImageDraw.Draw(base)
        elif k == "shafts": fx_shafts(base, t, x0=p[1], n=p[2], a=p[3]); d = ImageDraw.Draw(base)
        elif k == "motes": fx_motes(d, t, p[1], p[2] if len(p) > 2 else (255, 240, 170))
        elif k == "darken": fx_vignette_dark(base, p[1]); d = ImageDraw.Draw(base)
    # --- cast
    cast = sorted(o.get("cast", []), key=lambda c: c["y"])
    for c in cast: cast_member(base, c, t, lt, beat_start, speaker_amp, camx, speaking, ctx)
    d = ImageDraw.Draw(base)
    # --- weather / post
    for p in o.get("post", []):
        k = p[0]
        if k == "rain":
            ta = resolve_t(p[1], beat_start) if len(p) > 1 else 0
            if lt >= ta: fx_rain(d, base, t, p[2] if len(p) > 2 else 1.0)
        elif k == "lightning":
            ta = resolve_t(p[1], beat_start) if len(p) > 1 else 0; period = p[2] if len(p) > 2 else 4.0
            if lt >= ta:
                ph = (lt - ta) % period
                if ph < 0.12:
                    lightning(d, 80 + int(((lt - ta) // period) * 137) % (PW - 160), 0, HZ - 20, seed=int((lt - ta) // period)); fx_flash(base, 0.6 * (1 - ph / 0.12))
        elif k == "fog": fx_fog(base, p[1], p[2])
        elif k == "darken":
            ta = resolve_t(p[1], beat_start) if len(p) > 1 else 0
            if lt >= ta: fx_vignette_dark(base, p[2] * ease((lt - ta) / 1.5))
        elif k == "motes": fx_motes(ImageDraw.Draw(base), t, p[1], p[2] if len(p) > 2 else (255, 240, 170))
        elif k == "flash":
            ta = resolve_t(p[1], beat_start)
            if 0 <= lt - ta < 0.5: fx_flash(base, 1.0 - (lt - ta) / 0.5)
        elif k == "shafts": fx_shafts(base, t, x0=p[1], n=p[2], a=p[3])
        elif k == "quake":
            ta, tb = resolve_t(p[1], beat_start), resolve_t(p[2], beat_start)
            if ta <= lt <= tb:
                sh = int(round(math.sin(t * 60) * 3)); base.paste(Image.fromarray(np.roll(np.asarray(base), sh, axis=1)))
        elif k == "ash":
            r = np.random.RandomState(int(t * 20) % 1000)
            for x, y in zip(r.randint(0, PW, 60), r.randint(0, PH, 60)): d.point((x, y), fill=(120, 110, 110))
        elif k == "glow_pulse":
            fx_glow(base, p[1], p[2], p[3] * (0.9 + 0.1 * math.sin(t * 2)), p[4], p[5])
    zoom = o.get("zoom")
    if zoom:
        z0, z1, zd = zoom[0], zoom[1], (zoom[2] if len(zoom) > 2 else 6.0)
        z = z0 + (z1 - z0) * ease_c(lt / zd)
        if abs(z - 1) > 0.01:
            cw, ch = int(PW / z), int(PH / z); cx = zoom[3] if len(zoom) > 3 else PW / 2; cy = zoom[4] if len(zoom) > 4 else PH * 0.62
            x0 = int(clamp(cx - cw / 2, 0, PW - cw)); y0 = int(clamp(cy - ch / 2, 0, PH - ch))
            base = base.crop((x0, y0, x0 + cw, y0 + ch)).resize((PW, PH), Image.NEAREST)
    return base

def upscale_post(base, bloom=True):
    big = base.resize((W, H), Image.NEAREST)
    if not bloom: return big
    bl = base.resize((120, 68), Image.BILINEAR).point(lambda v: int(max(0, v - 185) * 1.6)).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BICUBIC)
    arr = np.asarray(big).astype(np.float32) + np.asarray(bl).astype(np.float32) * 0.5
    arr = arr * VIG
    arr = (arr - 128) * 1.05 + 128 + 3
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

YY, XX = np.mgrid[0:H, 0:W]
VIG = (1 - 0.40 * np.clip(((XX - W / 2) / (W * 0.72)) ** 2 + ((YY - H / 2) / (H * 0.70)) ** 2, 0, 1)).astype(np.float32)[..., None]
