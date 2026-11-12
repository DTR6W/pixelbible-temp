"""scene6: rich layered backgrounds + acting cast (uses px/chars2)."""
import math, os, sys, random
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "px"))
import chars2
import eden_sprites as es
from PIL import ImageDraw, ImageFont
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_FONT = ImageFont.truetype(BOLD, 11)

PW, PH = 180, 320
YY, XX = np.mgrid[0:PH, 0:PW]
B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
BAY = B4[YY % 4, XX % 4]
F32 = np.float32

def C(c): return np.array(c, dtype=F32)
def mix(a, b, f): return a + (b - a) * f

def vgrad(arr, y0, y1, c0, c1, bands=10):
    n = y1 - y0
    f = (np.arange(n) / max(1, n - 1))[:, None]
    fq = np.clip(np.floor(f * bands + BAY[y0:y1, :]) / bands, 0, 1)[..., None]
    arr[y0:y1] = C(c0) + (C(c1) - C(c0)) * fq

def ridge(seed, base, amp, scale=1.0):
    r = random.Random(seed)
    ph = [r.random() * 6.28 for _ in range(4)]
    x = np.arange(PW)
    h = (np.sin(x * 0.045 * scale + ph[0]) * 0.5 + np.sin(x * 0.11 * scale + ph[1]) * 0.28 + np.sin(x * 0.23 * scale + ph[2]) * 0.14 + np.sin(x * 0.5 * scale + ph[3]) * 0.06)
    return (base - h * amp).astype(int)

def fill_ridge(arr, h, y_end, col, hi, haze=None, hazef=0.0):
    for x in range(PW):
        y0 = h[x]
        slope = h[min(PW - 1, x + 1)] - h[max(0, x - 1)]
        for y in range(max(0, y0), y_end):
            depth = y - y0
            c = C(col)
            if depth < 2 and slope < 0: c = C(hi)
            elif depth < 3 and (x + y) % 2 == 0 and slope <= 0: c = mix(C(col), C(hi), 0.5)
            if haze is not None: c = mix(c, C(haze), hazef * max(0.0, 1 - depth / 40.0) + hazef * 0.4)
            arr[y, x] = c

def speckle(arr, y0, y1, seed, col, dens=0.05):
    r = np.random.RandomState(seed)
    m = r.rand(y1 - y0, PW) < dens
    sub = arr[y0:y1]
    sub[m] = C(col)

def tree(arr, x, yb, h, leaf, trunk=(70, 44, 30), palm=False):
    r = random.Random(x * 7 + h)
    if palm:
        for i in range(h):
            xx = x + int(math.sin(i * 0.08) * 3)
            for dx in (0, 1): arr[yb - i, xx + dx] = C(trunk) * (0.8 if dx else 1.0)
        top = (x + int(math.sin(h * 0.08) * 3), yb - h)
        for k in range(7):
            a = k / 7 * math.pi - 0.1
            for s in range(1, 15):
                px = top[0] + int(math.cos(a) * s * 1.1) * (1 if True else 1)
                py = top[1] + int(-math.sin(a) * s * 0.5 + (s * s) * 0.02)
                for dy in (0, 1):
                    if 0 <= py + dy < PH and 0 <= px < PW: arr[py + dy, px] = C(leaf) * (1.0 if dy == 0 else 0.7)
        for k in range(7):
            a = math.pi + k / 7 * math.pi - 0.1 - math.pi
        return
    for i in range(h):
        for dx in range(-1, 2 if h > 20 else 1): arr[yb - i, x + dx] = C(trunk) * (0.85 if dx > 0 else 1.0)
    for _ in range(int(h * 1.1)):
        a = r.random() * 6.28; rr = r.random() ** 0.6 * h * 0.55
        cx = x + math.cos(a) * rr; cy = yb - h * 0.95 + math.sin(a) * rr * 0.7
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    px, py = int(cx + dx), int(cy + dy)
                    if 0 <= px < PW and 0 <= py < PH:
                        sh = 1.15 if (dy < -0 and dx < 1) else (0.78 if dy > 1 else 1.0)
                        arr[py, px] = np.clip(C(leaf) * sh, 0, 255)

def rock_wall(arr, x0, x1, y0, y1, col, seed=3, bw=16, bh=8):
    r = random.Random(seed)
    for row, y in enumerate(range(y0, y1, bh)):
        off = (row % 2) * (bw // 2)
        for x in range(x0 - off, x1, bw):
            tone = 0.88 + r.random() * 0.24
            c = np.clip(C(col) * tone, 0, 255)
            for yy in range(y, min(y + bh, y1)):
                for xx in range(max(x, x0), min(x + bw, x1)):
                    k = c
                    if yy == y or xx == x: k = c * 0.62
                    elif yy == y + 1 or xx == x + 1: k = np.clip(c * 1.12, 0, 255)
                    arr[yy, xx] = k

def ruin(arr, x, yb, w, col):
    r = random.Random(x)
    for xx in range(x, min(PW, x + w)):
        h = 18 + int(r.random() * 18) if (xx - x) % 6 == 0 or r.random() < 0.3 else None
        if h is None: h = 14 + int(r.random() * 10)
        for y in range(yb - h, yb):
            bri = 0.84 if (y // 4 + xx // 7) % 2 else 1.0
            arr[y, xx] = np.clip(C(col) * bri * (0.86 if xx > x + w - 4 else 1), 0, 255)
        arr[yb - h, xx] = np.clip(C(col) * 1.25, 0, 255)

def hut(arr, x, yb, w, h, wall, roof, door=(50, 30, 20)):
    x = min(x, PW - w - 3)
    for y in range(yb - h, yb):
        for xx in range(x, x + w):
            arr[y, xx] = C(wall) * (0.82 if xx > x + w - 5 else 1.0)
    for y in range(yb - h - 3, yb - h): arr[y, x - 2:x + w + 2] = C(roof)
    arr[yb - h - 3, x - 2:x + w + 2] = C(roof) * 1.2
    dw = max(6, w // 4)
    arr[yb - h + 8:yb, x + w // 2 - dw // 2:x + w // 2 + dw // 2] = C(door)
    arr[yb - h + 4:yb - h + 8, x + 4:x + 8] = C((250, 220, 130))

def town(arr, x0, x1, yb, col):
    r = random.Random(x0 + x1)
    x = x0
    while x < x1:
        w = r.randint(14, 26); h = r.randint(16, 34)
        for y in range(yb - h, yb):
            for xx in range(x, min(PW, x + w)):
                c = C(col) * (0.8 if xx > x + w - 4 else 1.0) * (0.92 + 0.08 * ((y // 4 + xx // 5) % 2))
                arr[y, xx] = c
        arr[yb - h:yb - h + 2, x:min(PW, x + w)] = C(col) * 1.2
        for wy in range(yb - h + 6, yb - 6, 9):
            for wx in range(x + 4, min(PW - 3, x + w - 4), 8):
                arr[wy:wy + 4, wx:wx + 3] = C((60, 36, 28)) if r.random() < 0.6 else C((255, 210, 120))
        x += w + r.randint(0, 3)
    # tower
    tx = (x0 + x1) // 2
    for y in range(yb - 52, yb): arr[y, tx - 5:tx + 6] = C(col) * (0.9 + 0.1 * ((y // 4) % 2))
    arr[yb - 54:yb - 52, tx - 7:tx + 8] = C(col) * 1.15

def cross(arr, x, yb, h):
    arr[yb - h:yb, x - 1:x + 2] = C((78, 50, 34)); arr[yb - h + 8:yb - h + 11, x - 8:x + 9] = C((78, 50, 34))
    arr[yb - h:yb, x - 1] = C((110, 76, 52))

def bones(arr, x0, x1, yb):
    r = random.Random(x0)
    for _ in range(40):
        bx = r.randint(x0, min(x1, PW - 12)); by = yb + r.randint(0, 130); L = r.randint(4, 8)
        for k in range(L): arr[min(PH - 1, by), min(PW - 1, bx + k)] = C((240, 234, 218))
        arr[by - 1, bx] = C((240, 234, 218)); arr[min(PH - 1, by + 1), min(PW - 1, bx + L)] = C((240, 234, 218))
    for _ in range(6):
        bx = r.randint(x0 + 6, min(x1, PW - 6) - 6); by = yb + r.randint(10, 110)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9: arr[by + dy, bx + dx] = C((232, 226, 208))
        arr[by - 1:by + 1, bx - 2] = C((40, 34, 30)); arr[by - 1:by + 1, bx + 1] = C((40, 34, 30))

# ---------------------------------------------------------------- statics
_ST = {}
SKY = {
 "desert": ((120, 176, 236), (252, 232, 196)),
 "burn": ((50, 8, 12), (246, 108, 40)),
 "cross": ((34, 30, 56), (190, 110, 90)),
 "day": ((96, 170, 236), (222, 238, 250)),
 "dawn": ((120, 110, 190), (255, 196, 140)),
 "dusk": ((52, 36, 96), (240, 130, 86)),
 "golden": ((84, 120, 196), (255, 214, 140)),
 "night": ((6, 8, 32), (44, 52, 110)),
 "storm": ((30, 36, 60), (90, 100, 130)),
}
GROUND = {
 "desert": ((220, 184, 120), (190, 150, 92), (232, 200, 140)),
 "burn": ((70, 40, 36), (40, 24, 24), (110, 70, 56)),
 "cross": ((70, 60, 60), (44, 38, 40), (110, 90, 80)),
 "day": ((104, 168, 72), (70, 120, 56), (200, 166, 110)),
 "dawn": ((120, 128, 80), (84, 92, 60), (190, 140, 100)),
 "dusk": ((112, 84, 84), (70, 54, 66), (170, 124, 104)),
 "golden": ((140, 150, 70), (96, 104, 52), (214, 170, 100)),
 "night": ((26, 44, 56), (16, 28, 40), (60, 66, 84)),
 "storm": ((44, 58, 60), (30, 40, 44), (84, 84, 86)),
}
MTN = {
 "desert": ((226, 190, 130), (246, 214, 160)), "burn": ((60, 20, 24), (150, 60, 40)), "cross": ((50, 40, 70), (110, 70, 90)),
 "day": ((120, 140, 190), (150, 170, 214)), "dawn": ((150, 110, 150), (210, 150, 160)), "dusk": ((86, 56, 100), (150, 86, 100)),
 "golden": ((140, 124, 140), (200, 160, 130)), "night": ((24, 28, 64), (44, 50, 96)), "storm": ((46, 54, 76), (70, 80, 104)),
}

def build_outdoor(env, props):
    arr = np.zeros((PH, PW, 3), F32)
    sk = SKY[env]; vgrad(arr, 0, 140, sk[0], sk[1], bands=12)
    # sun / moon glow
    if env in ("dusk", "dawn", "golden"):
        sx, sy = (130, 112) if env != "dawn" else (50, 112)
        d2 = ((XX - sx) ** 2 + (YY - sy) ** 2).astype(F32)
        gl = np.exp(-d2 / 1400.0)[..., None]
        arr[:140] = np.clip(arr[:140] + gl[:140] * C((255, 190, 110)) * 0.6, 0, 255)
        disc = d2 < 64
        arr[disc] = C((255, 238, 190))
    if env == "day":
        d2 = ((XX - 140) ** 2 + (YY - 34) ** 2).astype(F32)
        arr[:140] = np.clip(arr[:140] + (np.exp(-d2 / 900.0)[..., None] * C((255, 240, 200)) * 0.5)[:140], 0, 255)
        arr[d2 < 49] = C((255, 250, 220))
    if env == "night":
        d2 = ((XX - 140) ** 2 + (YY - 38) ** 2).astype(F32)
        arr[:140] = np.clip(arr[:140] + (np.exp(-d2 / 700.0)[..., None] * C((150, 170, 255)) * 0.35)[:140], 0, 255)
        arr[d2 < 42] = C((240, 240, 226)); arr[((XX - 143) ** 2 + (YY - 36) ** 2) < 30] = C((200, 204, 200))
    m = MTN[env]
    fill_ridge(arr, ridge(11, 112, 20, 0.7), 150, m[0], m[1], sk[1], 0.45)
    fill_ridge(arr, ridge(23, 126, 12, 1.1), 152, tuple(int(v * 0.8) for v in m[0]), m[1], sk[1], 0.25)
    g = GROUND[env]
    h = ridge(37, 140, 6, 1.4)
    for x in range(PW):
        for y in range(h[x], PH):
            f = min(1.0, (y - h[x]) / 160.0)
            arr[y, x] = mix(C(g[0]), C(g[1]), f)
    speckle(arr, 142, PH, 5, g[1], 0.07); speckle(arr, 142, PH, 6, tuple(min(255, int(v * 1.2)) for v in g[0]), 0.05)
    # dirt path (perspective)
    for y in range(150, PH):
        f = (y - 150) / 170.0
        cx = 90 + math.sin(y * 0.03) * 6 * (0.2 + f)
        hw = 4 + f * 30
        for x in range(int(cx - hw), int(cx + hw)):
            if 0 <= x < PW:
                e = abs(x - cx) / hw
                c = mix(C(g[2]), C(g[2]) * 0.82, e ** 2)
                if (x * 7 + y * 13) % 11 == 0: c = c * 0.86
                arr[y, x] = c
    for p in props:
        k = p[0]
        if k == "tree": tree(arr, p[1], p[2], p[3], p[4] if len(p) > 4 else (52, 120, 60))
        elif k == "palm": tree(arr, p[1], p[2], p[3], (64, 140, 70), palm=True)
        elif k == "ruin": ruin(arr, p[1], p[2], p[3], p[4])
        elif k == "hut": hut(arr, *p[1:])
        elif k == "town": town(arr, p[1], p[2], p[3], p[4] if len(p) > 4 else (196, 160, 116))
        elif k == "cross": cross(arr, p[1], p[2], p[3])
        elif k == "bones": bones(arr, p[1], p[2], p[3])
        elif k == "statue":
            x = p[1]; arr[p[2] - 54:p[2], x - 9:x + 10] = C((120, 84, 20)); arr[p[2] - 54:p[2] - 4, x - 7:x + 6] = C((240, 190, 60)); arr[p[2] - 50:p[2] - 4, x - 7:x - 3] = C((255, 232, 130)); arr[p[2] - 66:p[2] - 54, x - 5:x + 5] = C((240, 190, 60)); arr[p[2] - 66:p[2] - 64, x - 5:x + 5] = C((255, 232, 130)); arr[p[2] - 6:p[2], x - 12:x + 13] = C((150, 108, 40))
        elif k == "furnace":
            x = p[1]; arr[p[2] - 44:p[2], x - 24:x + 25] = C((92, 80, 76)); arr[p[2] - 30:p[2] - 4, x - 14:x + 15] = C((255, 150, 40)); arr[p[2] - 20:p[2] - 4, x - 10:x + 11] = C((255, 220, 90)); arr[p[2] - 46:p[2] - 44, x - 26:x + 27] = C((150, 136, 130))
        elif k == "well":
            x = p[1]; arr[p[2] - 16:p[2], x - 13:x + 14] = C((140, 132, 124)); arr[p[2] - 16:p[2] - 13, x - 13:x + 14] = C((190, 182, 170)); arr[p[2] - 36:p[2] - 16, x - 12:x - 10] = C((96, 64, 40)); arr[p[2] - 36:p[2] - 16, x + 11:x + 13] = C((96, 64, 40)); arr[p[2] - 38:p[2] - 35, x - 14:x + 15] = C((120, 84, 50))
        elif k == "altar":
            x = p[1]; arr[p[2] - 12:p[2], x - 16:x + 17] = C((140, 132, 124)); arr[p[2] - 12:p[2] - 10, x - 16:x + 17] = C((196, 188, 176))
        elif k == "olive": tree(arr, p[1], p[2], p[3], (112, 140, 110), trunk=(84, 70, 60))
    return arr

def build_palace(env, props):
    arr = np.zeros((PH, PW, 3), F32)
    rock_wall(arr, 0, PW, 0, 152, (206, 170, 128), seed=4)
    # frieze band
    arr[20:26] = C((140, 40, 48)); arr[26:28] = C((226, 184, 70)); arr[18:20] = C((226, 184, 70))
    for x in range(0, PW, 8): arr[21:25, x:x + 3] = C((226, 184, 70))
    # arched windows with sky
    sk = SKY["dusk" if env == "palace_dusk" else "golden"]
    for wx in (36, 90, 144):
        for y in range(40, 104):
            for x in range(wx - 11, wx + 11):
                inarch = y > 52 or ((x - wx) ** 2 + (y - 52) ** 2) <= 121
                if inarch:
                    f = (y - 40) / 64.0
                    arr[y, x] = mix(C(sk[0]), C(sk[1]), min(1, f * 1.3))
        for y in range(40, 106):
            for x in range(wx - 14, wx + 14):
                inarch = y > 52 or ((x - wx) ** 2 + (y - 52) ** 2) <= 196
                inner = y > 52 and abs(x - wx) < 11 or ((x - wx) ** 2 + (y - 52) ** 2) <= 121
                if inarch and not inner and y < 104: arr[y, x] = C((150, 112, 80)) * (1.15 if x < wx else 0.85)
        arr[104:107, wx - 14:wx + 14] = C((232, 214, 176))
        # distant silhouette in window
        for x in range(wx - 10, wx + 10):
            hh = 92 + int(math.sin(x * 0.7) * 3); arr[hh:104, x] = C((120, 70, 90))
    # columns
    for cx in (9, 171):
        for y in range(28, 152):
            for x in range(cx - 7, cx + 8):
                s = (x - (cx - 7)) / 14.0
                arr[y, x] = C((236, 220, 190)) * (1.08 - 0.45 * s ** 1.5)
                if y % 20 in (0, 1) and 40 < y < 140: arr[y, x] = arr[y, x] * 0.8
        arr[28:36, cx - 10:cx + 11] = C((240, 224, 190)); arr[36:38, cx - 10:cx + 11] = C((150, 120, 90))
        arr[144:152, cx - 10:cx + 11] = C((226, 208, 176))
    # perspective floor
    vpx, vpy = 90.0, 96.0
    for y in range(152, PH):
        d = y - vpy
        v = 2400.0 / d
        for x in range(PW):
            u = (x - vpx) / d * 7.0
            ti, tj = math.floor(u), math.floor(v / 5.0)
            chk = (ti + tj) % 2
            base = C((222, 204, 176)) if chk else C((176, 152, 128))
            fu = u - ti; fv = v / 5.0 - tj
            if fu < 0.06 or fv < 0.06 * (1 + (320 - y) / 80): base = base * 0.62
            fade = min(1.0, (y - 152) / 60.0)
            arr[y, x] = base * (0.82 + 0.18 * fade)
        # carpet
        hw = 6 + (y - 152) * 0.42
        for x in range(int(vpx - hw), int(vpx + hw)):
            if 0 <= x < PW:
                e = abs(x - vpx) / hw
                c = C((152, 28, 40)) * (0.9 + 0.2 * ((x + y // 3) % 2))
                if e > 0.86: c = C((226, 184, 70))
                elif e > 0.80: c = C((100, 16, 26))
                arr[y, x] = c * (0.85 + 0.15 * min(1, (y - 152) / 60))
    # dais + throne
    for i in range(3):
        y0 = 148 - i * 5
        arr[y0:y0 + 5, 66 - i * 4:114 + i * 4] = C((200, 170, 126)) * (1.0 - i * 0.06)
        arr[y0:y0 + 1, 66 - i * 4:114 + i * 4] = C((238, 212, 168))
    # throne (gold, tall back)
    if "throne" in props:
        arr[78:140, 80:100] = C((220, 168, 52)); arr[78:80, 80:100] = C((255, 226, 120))
        arr[96:118, 78:102] = C((140, 30, 44)); arr[118:128, 76:104] = C((232, 180, 60)); arr[128:140, 78:82] = C((190, 140, 40)); arr[128:140, 98:102] = C((190, 140, 40))
        for yy in range(72, 78): arr[yy, 86 + (yy - 72) // 2:94 - (yy - 72) // 2] = C((255, 226, 120))
    return arr

def build_den(env, props):
    arr = np.zeros((PH, PW, 3), F32)
    vgrad(arr, 0, 100, (96, 110, 190), (255, 200, 150), bands=12)       # dawn sky above the pit
    fill_ridge(arr, ridge(5, 92, 10, 0.8), 106, (120, 100, 130), (200, 150, 150), (255, 200, 150), 0.4)
    # pit wall (cutaway)
    rock_wall(arr, 0, PW, 106, 152, (116, 102, 92), seed=9, bw=20, bh=10)
    for y in range(106, 152): arr[y] *= 0.5 + 0.5 * ((y - 106) / 46.0)
    for x in range(PW): arr[106:152, x] *= 0.7 + 0.3 * (1 - abs(x - 90) / 90.0)
    # ground surface (walkway) with a gap above the pit; front edge blocks
    for x in range(PW):
        if 78 <= x < 102: continue
        arr[100:103, x] = C((214, 190, 150)); arr[103:107, x] = C((170, 146, 112)) * (1.0 - 0.15 * (x % 3 == 0))
        arr[107:114, x] = C((140, 118, 92)) * (0.85 if (x // 10) % 2 else 1.0); arr[113, x] = C((80, 66, 52))
    arr[100:114, 76:78] = C((90, 74, 58)); arr[100:114, 102:104] = C((90, 74, 58))
    # sand floor
    for y in range(152, PH):
        f = (y - 152) / 170.0
        arr[y] = mix(C((176, 146, 100)), C((120, 96, 66)), f)
    arr[150:153] = C((96, 78, 56))
    speckle(arr, 152, PH, 12, (206, 176, 128), 0.08); speckle(arr, 152, PH, 13, (90, 70, 50), 0.08)
    r = random.Random(3)
    for _ in range(9):
        bx = r.randint(10, 170); by = r.randint(160, 250)
        for k in range(6): arr[by, min(PW - 1, bx + k)] = C((238, 232, 214))
        arr[by - 1, bx] = C((238, 232, 214)); arr[by + 1, min(PW - 1, bx + 5)] = C((238, 232, 214))
    return arr

def build_sea(env, props):
    arr = np.zeros((PH, PW, 3), F32)
    sk = SKY["storm" if "storm" in env else ("night" if "night" in env else "golden")]
    vgrad(arr, 0, 124, sk[0], sk[1], bands=12)
    wc = ((20, 40, 70), (52, 80, 118)) if ("storm" in env or "night" in env) else ((40, 120, 190), (130, 200, 236))
    vgrad(arr, 124, 320, wc[1], wc[0], bands=14)
    if env == "ship":  # unused
        pass
    if env.startswith("ship"):
        # wooden deck in perspective
        for y in range(160, PH):
            f = (y - 160) / 160.0
            for x in range(PW):
                plank = int((x - 90) / (6 + f * 14))
                c = C((150, 100, 60)) * (0.85 + 0.15 * (plank % 2)); 
                if (x - 90) % int(6 + f * 14) == 0 or (y % 17 == 0): c = c * 0.6
                arr[y, x] = c
        # rail
        arr[150:156, :] = C((112, 76, 44)); arr[148:150, :] = C((176, 128, 80))
        for x in range(4, PW, 18): arr[134:150, x:x + 3] = C((96, 62, 36))
        # mast
        arr[20:152, 84:92] = C((110, 74, 42)); arr[20:152, 84:86] = C((160, 116, 72))
        for y in range(34, 100):
            w = 36 + int(math.sin(y * 0.05) * 4)
            arr[y, 90 - 2:90 + w + 2 if False else 90 + w] = C((230, 220, 196)) * (0.8 + 0.2 * ((y // 6) % 2))
        arr[32:36, 50:130] = C((110, 74, 42))
    if env == "shore":
        for y in range(150, PH):
            f = (y - 150) / 170.0
            arr[y] = mix(C((232, 206, 150)), C((190, 160, 110)), f)
        speckle(arr, 150, PH, 4, (250, 232, 180), 0.06)
        arr[146:152] = C((250, 250, 255)) * 0.0 + arr[146:152]
    return arr

def build_prison(env, props):
    arr = np.zeros((PH, PW, 3), F32)
    rock_wall(arr, 0, PW, 0, 150, (96, 88, 90), seed=11, bw=22, bh=11)
    for y in range(0, 150): arr[y] *= 0.5 + 0.5 * (y / 150.0)
    for x in range(PW): arr[:150, x] *= 0.62 + 0.38 * (1 - abs(x - 90) / 90.0)
    # barred window
    arr[28:78, 66:114] = C((8, 10, 30))
    for y in range(28, 78): arr[y, 66:114] = mix(C((20, 24, 70)), C((70, 80, 140)), (y - 28) / 50.0)
    arr[26:28, 62:118] = C((60, 54, 56)); arr[78:80, 62:118] = C((60, 54, 56)); arr[26:80, 62:66] = C((60, 54, 56)); arr[26:80, 114:118] = C((60, 54, 56))
    for x in range(72, 112, 9): arr[28:78, x:x + 2] = C((26, 24, 28))
    arr[30:34, 92:96] = C((240, 240, 226))
    # stone floor perspective
    vpx, vpy = 90.0, 96.0
    for y in range(150, PH):
        d = y - vpy; v = 2400.0 / d
        for x in range(PW):
            u = (x - vpx) / d * 6.0
            ti, tj = math.floor(u), math.floor(v / 6.0)
            base = C((92, 84, 82)) if (ti + tj) % 2 else C((74, 68, 68))
            if (u - ti) < 0.06 or (v / 6.0 - tj) < 0.06: base = base * 0.6
            arr[y, x] = base * (0.7 + 0.3 * min(1, (y - 150) / 80))
    # hanging chains on wall
    for cx in (20, 160):
        for y in range(60, 110, 4): arr[y:y + 3, cx:cx + 2] = C((120, 120, 132))
    return arr

def build_house(env, props):
    arr = np.zeros((PH, PW, 3), F32)
    rock_wall(arr, 0, PW, 0, 150, (204, 170, 124), seed=14, bw=18, bh=9)
    for x in range(0, PW, 45): arr[0:150, x:x + 6] = C((110, 74, 44)); arr[0:150, x:x + 2] = C((150, 106, 66))
    arr[0:12, :] = C((100, 66, 40))
    arr[40:90, 14:40] = C((20, 24, 60)); arr[40:90, 14:40] = mix(C((40, 50, 110)), C((200, 130, 100)), 0.5); arr[38:40, 12:42] = C((110, 74, 44)); arr[90:92, 12:42] = C((110, 74, 44)); arr[40:90, 26:28] = C((110, 74, 44))
    for y in range(52, 152): arr[y, 130:166] = C((70, 44, 30)) * (1 - 0.15 * ((y - 52) / 100.0))
    for y in range(52, 62):
        for x in range(130, 166):
            if ((x - 148) / 18.0) ** 2 + ((y - 62) / 10.0) ** 2 > 1: arr[y, x] = C((204, 170, 124))
    for y in range(150, PH):
        f = (y - 150) / 170.0
        for x in range(PW):
            plank = (y // 7)
            c = C((150, 104, 64)) * (0.85 + 0.12 * (plank % 2)); 
            if y % 7 == 0 or (x * 3 + plank * 37) % 53 == 0: c = c * 0.62
            arr[y, x] = c * (0.8 + 0.2 * (1 - f))
    return arr

def build_table(arr):
    # long feast table (static foreground behind characters? drawn after back layer)
    arr[164:168, 24:156] = C((150, 96, 56)); arr[168:182, 24:156] = C((110, 68, 40))
    arr[164:165, 24:156] = C((196, 134, 80)); arr[166:172, 20:160] = C((236, 232, 220)) * 0.0 + arr[166:172, 20:160]
    arr[168:172, 24:156] = C((232, 226, 214)) * 0.93
    for x in range(28, 152, 12):
        arr[160:165, x:x + 7] = C((218, 168, 72)); arr[158:160, x + 1:x + 6] = C((250, 214, 110))
    for x in range(40, 150, 26):
        arr[161:165, x:x + 5] = C((200, 60, 56)); arr[160:161, x + 1:x + 4] = C((230, 100, 90))
    for x in (28, 148): arr[182:200, x:x + 4] = C((90, 56, 34))
    return arr

def static(env, props):
    key = (env, tuple(sorted(str(p) for p in props)))
    if key in _ST: return _ST[key]
    if env == "den":
        arr = build_den(env, props)
    elif env.startswith("ship") or env in ("shore", "sea", "sea_storm", "sea_night"):
        arr = build_sea(env, props)
    elif env == "prison":
        arr = build_prison(env, props)
    elif env == "house":
        arr = build_house(env, props)
    elif env.startswith("palace"):
        arr = build_palace(env, [p if isinstance(p, str) else p[0] for p in props])
        if any((p if isinstance(p, str) else p[0]) == "table" for p in props): arr = build_table(arr)
    else:
        arr = build_outdoor(env, [p for p in props if not isinstance(p, str)])
    _ST[key] = arr
    return arr

# ---------------------------------------------------------------- dynamic overlays
def add_glow(arr, cx, cy, r, col, k):
    x0, x1 = max(0, int(cx - r)), min(PW, int(cx + r) + 1); y0, y1 = max(0, int(cy - r)), min(PH, int(cy + r) + 1)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)
    g = np.clip(1 - d2, 0, 1) ** 2
    g = np.floor(g * 5 + BAY[y0:y1, x0:x1]) / 5.0
    arr[y0:y1, x0:x1] = np.clip(arr[y0:y1, x0:x1] + g[..., None] * C(col) * k, 0, 255)

def cloud(arr, x, y, s, col, shade):
    blobs = [(0, 0, 9), (9, 2, 7), (-9, 3, 7), (16, 5, 5), (-16, 5, 5), (4, -4, 6)]
    for bx, by, br in blobs:
        r = br * s
        for dy in range(-int(r), int(r) + 1):
            for dx in range(-int(r * 1.4), int(r * 1.4) + 1):
                if (dx / 1.4) ** 2 + dy ** 2 <= r * r:
                    px, py = int(x + bx * s + dx), int(y + by * s + dy)
                    if 0 <= px < PW and 0 <= py < PH:
                        arr[py, px] = C(shade) if dy > r * 0.35 else C(col)

def dyn_fire(arr, t):
    for fx in (24, 56, 100, 140, 168):
        for k in range(14):
            yy = 150 - k * 3 - int(abs(math.sin(t * 9 + k + fx)) * 3); ww = max(1, 6 - k // 2)
            for dx in range(-ww, ww + 1):
                if 0 <= fx + dx < PW and 0 <= yy < PH: arr[yy, fx + dx] = C((255, 120 + k * 8, 30 + k * 6))
        add_glow(arr, fx, 140, 30, (255, 120, 40), 0.35)
    r = random.Random(2)
    for i in range(40):
        x = (r.random() * PW + math.sin(t + i) * 8) % PW; y = 150 - ((r.random() * 150 + t * (14 + i % 5)) % 150)
        arr[int(y), int(x)] = np.clip(arr[int(y), int(x)] + C((255, 180, 60)) * 0.9, 0, 255)

def dyn_outdoor(arr, env, t, props):
    if env == "burn": dyn_fire(arr, t)
    for i in range(3):
        x = ((t * (2.0 + i) + i * 70) % 260) - 40
        sk = SKY[env][1]
        if env in ("night", "storm", "dusk"): col = tuple(int(v * 0.55) + 20 for v in sk); sh = tuple(int(v * 0.4) + 10 for v in sk)
        else: col, sh = (252, 252, 255), (206, 214, 236)
        cloud(arr, x, 20 + i * 18, 1.0 + 0.2 * i, col, sh)
    if env == "night":
        r = np.random.RandomState(9)
        for i in range(36):
            x, y = r.randint(0, PW), r.randint(0, 110)
            if (math.sin(t * 2 + i) > -0.2): arr[y, x] = C((255, 255, 230))
    # birds
    if env in ("day", "golden", "dawn"):
        for i in range(2):
            bx = (t * 14 + i * 60) % 220 - 20; by = 56 + i * 12 + math.sin(t * 2 + i) * 3
            w = int(math.sin(t * 9 + i) * 2)
            for k in range(-3, 4):
                px = int(bx + k); py = int(by + abs(k) * (0.5) - w * (1 if k else 0))
                if 0 <= px < PW and 0 <= py < PH: arr[py, px] = C((40, 40, 60))
    # sun shafts
    if env in ("golden", "dusk", "dawn", "day"):
        for i in range(4):
            x0 = 120 + i * 18 + math.sin(t * 0.6 + i) * 4
            for y in range(0, 190):
                xs = int(x0 - y * (0.55 + i * 0.05))
                for dx in range(0, 6):
                    px = xs + dx
                    if 0 <= px < PW and (y + px) % 2 == 0: arr[y, px] = np.clip(arr[y, px] + C((255, 220, 150)) * 0.10, 0, 255)
    # motes / fireflies
    r = random.Random(4)
    for i in range(22):
        x = (r.random() * PW + math.sin(t * 0.8 + i) * 6) % PW
        y = (r.random() * 300 - t * (3 + i % 4) * (-1 if env == "night" else 1)) % 280 + 20
        if env == "night": col = (200, 255, 140) if math.sin(t * 2 + i) > 0 else None
        else: col = (255, 240, 190)
        if col and 0 <= int(y) < PH: arr[int(y), int(x)] = np.clip(arr[int(y), int(x)] + C(col) * 0.7, 0, 255)

def dyn_palace(arr, env, t, props):
    # light shafts from windows
    sh = (255, 214, 140) if env != "palace_dusk" else (255, 150, 110)
    for wx in (36, 90, 144):
        for y in range(104, PH):
            f = (y - 104)
            sx = wx - 6 - f * 0.18
            w = 13 + f * 0.1
            for x in range(int(sx), int(sx + w)):
                if 0 <= x < PW and (x + y) % 2 == 0: arr[y, x] = np.clip(arr[y, x] + C(sh) * (0.2 * max(0.15, 1 - f / 220)), 0, 255)
    # banners
    for bx in (62, 118):
        for y in range(30, 76):
            sw = int(math.sin(t * 1.4 + y * 0.08 + bx) * (y - 30) * 0.05)
            for x in range(bx - 6 + sw, bx + 7 + sw):
                if 0 <= x < PW:
                    c = C((150, 30, 44)) * (0.85 + 0.2 * ((x - bx) > 0))
                    if y > 70 and abs(x - (bx + sw)) < 7 - (y - 70): pass
                    if y < 33 or y > 72 - abs(x - bx - sw) // 2 * 0: c = C((226, 184, 70)) if y < 33 else c
                    arr[y, x] = c
        for y in range(46, 56):
            for x in range(bx - 2, bx + 3): arr[y, x + int(math.sin(t * 1.4 + y * 0.08 + bx) * (y - 30) * 0.05)] = C((226, 184, 70))
    # torches
    for tx in (22, 158):
        arr[96:112, tx:tx + 2] = C((90, 60, 36)); arr[92:96, tx - 1:tx + 3] = C((150, 110, 60))
        fl = 0.8 + 0.2 * math.sin(t * 13 + tx) + 0.1 * math.sin(t * 29)
        add_glow(arr, tx + 1, 90, 34 * fl, (255, 160, 60), 0.55)
        for k in range(5):
            yy = 92 - k * 2 - int(abs(math.sin(t * 11 + k + tx)) * 2); ww = max(1, 3 - k // 2)
            arr[yy, tx + 1 - ww // 2: tx + 1 + ww] = C((255, 200 + k * 10, 80 + k * 30))
    # dust
    r = random.Random(8)
    for i in range(26):
        x = (r.random() * PW + math.sin(t * 0.5 + i) * 5) % PW; y = (r.random() * 260 + t * 2.5) % 230 + 50
        arr[int(y), int(x)] = np.clip(arr[int(y), int(x)] + C((255, 230, 180)) * 0.55, 0, 255)

def dyn_sea(arr, env, t):
    storm = "storm" in env
    for y in range(126, 150 if env.startswith("ship") else 190, 3):
        for x in range(0, PW):
            w = math.sin(x * 0.12 + t * (3 if storm else 1.4) + y * 0.4) + math.sin(x * 0.31 - t * 2 + y)
            if w > (1.1 if storm else 1.5): arr[y, x] = np.clip(arr[y, x] + C((220, 236, 255)) * 0.6, 0, 255)
    for i in range(3):
        x = ((t * (3 + i) + i * 80) % 260) - 40
        cloud(arr, x, 18 + i * 14, 1.0 + 0.2 * i, (80, 90, 110) if storm else (250, 250, 255), (50, 60, 80) if storm else (210, 218, 238))
    if storm:
        r = np.random.RandomState(int(t * 20) % 50)
        for _ in range(120):
            x, y = r.randint(0, PW), r.randint(0, PH)
            for k in range(4):
                if y + k < PH and x - k // 2 >= 0: arr[y + k, x - k // 2] = np.clip(arr[y + k, x - k // 2] + C((190, 210, 255)) * 0.5, 0, 255)
        if int(t * 1.3) % 4 == 0 and (t * 1.3) % 1 < 0.12: arr[:] = np.clip(arr + 90, 0, 255)

def dyn_room(arr, env, t):
    if env == "prison":
        for y in range(80, PH):
            f = (y - 80)
            sx = 84 - f * 0.2; w = 16 + f * 0.5
            for x in range(int(sx), int(sx + w)):
                if 0 <= x < PW and (x + y) % 2 == 0: arr[y, x] = np.clip(arr[y, x] + C((160, 180, 255)) * 0.18 * max(0.1, 1 - f / 240), 0, 255)
    else:
        for y in range(90, PH):
            f = y - 90
            for x in range(int(8 - f * 0.1), int(44 + f * 0.1)):
                if 0 <= x < PW and (x + y) % 2 == 0: arr[y, x] = np.clip(arr[y, x] + C((255, 200, 140)) * 0.18 * max(0.1, 1 - f / 200), 0, 255)
    for tx in ((22, 158) if env == "prison" else (100,)):
        arr[96:112, tx:tx + 2] = C((90, 60, 36))
        fl = 0.8 + 0.2 * math.sin(t * 13 + tx)
        add_glow(arr, tx + 1, 90, 30 * fl, (255, 160, 60), 0.5)
        for k in range(5):
            yy = 92 - k * 2 - int(abs(math.sin(t * 11 + k + tx)) * 2); ww = max(1, 3 - k // 2)
            arr[yy, tx + 1 - ww // 2: tx + 1 + ww] = C((255, 200 + k * 10, 80 + k * 30))

def dyn_den(arr, t):
    for y in range(114, 230):
        f = (y - 114) / 116.0
        sx = 78 + f * 10 + math.sin(t * 0.5) * 1.5; w = 24 + f * 40
        for x in range(int(sx), int(sx + w)):
            if 0 <= x < PW and (x + y) % 2 == 0: arr[y, x] = np.clip(arr[y, x] + C((255, 240, 190)) * (0.34 * (1 - f * 0.5)), 0, 255)
    add_glow(arr, 112, 200, 46, (255, 230, 160), 0.3)
    r = random.Random(5)
    for i in range(26):
        x = 84 + r.random() * 30 + math.sin(t + i) * 4; y = (r.random() * 110 + t * 6) % 110 + 114
        arr[int(y), int(x)] = np.clip(arr[int(y), int(x)] + C((255, 244, 200)) * 0.8, 0, 255)

# ---------------------------------------------------------------- acting cast
def _pose(act, t, t0, side=1):
    """returns (pose, extra) ; angles: arm angle from hanging (deg), forearm bend"""
    k = t - t0
    if act == "point":
        return {"ra": (95 + 5 * math.sin(k * 3), -6)}, {}
    if act == "raise":
        return {"la": (150 + 8 * math.sin(k * 4), -8), "ra": (150 + 8 * math.sin(k * 4 + 1), -8)}, {}
    if act == "cower":
        return {"la": (130, -105), "ra": (130, -105)}, {"rot": 7 * side, "sq": 0.95}
    if act == "bow":
        e = min(1.0, max(0.0, k / 0.8))
        return {"la": (20, 30), "ra": (20, 30)}, {"rot": 18 * e * side, "sq": 1 - 0.05 * e}
    if act == "kneel":
        return {"la": (40, 50), "ra": (40, 50)}, {"sq": 0.78, "rot": 6 * side}
    if act == "cheer":
        return {"la": (140 + 15 * math.sin(k * 7), -10), "ra": (140 + 15 * math.sin(k * 7 + 2), -10)}, {"hop": abs(math.sin(k * 7)) * 3}
    if act == "talk":
        return {"ra": (40 + 28 * math.sin(k * 3.1), -34 + 10 * math.sin(k * 5)), "la": (14 + 8 * math.sin(k * 2.3), 10)}, {}
    if act == "cross":
        return {"la": (92, 0), "ra": (92, 0)}, {}
    if act == "welcome":
        return {"la": (75, -8), "ra": (75, -8)}, {}
    if act == "hands":
        return {"la": (60, -85), "ra": (60, -85)}, {}
    return None, {}

def ease_c(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3

def cast_member(base, c, t, lt, speaker_amp):
    name = c["n"]; x = c["x"]; y = c["y"]; s = c.get("s", 0.55); fl = c.get("flip", 0)
    acts = c.get("acts", [])
    act, t0 = "idle", 0.0
    for a in acts:  # (time, act)
        if lt >= a[0]: act, t0 = a[1], a[0]
    walk = 0.0
    if "walk" in c:  # (t_start, t_end, x_to)
        a, b, xt = c["walk"]
        if lt < a: pass
        elif lt < b:
            f = (lt - a) / (b - a); x = x + (xt - x) * f; walk = 1.0
        else: x = xt
    pose, ex = _pose(act, t, t0, side=(-1 if fl else 1))
    amp = speaker_amp if c.get("speaks") else 0.0
    if act == "talk" and not c.get("speaks"): amp = 0.35 * (0.5 + 0.5 * math.sin(t * 9)) if c.get("fake_talk") else 0.0
    blink = (t * 0.9 + c.get("seed", 0) * 0.37) % 3.4 < 0.12
    look = c.get("look", 0.0)
    if "scream" in c and c["scream"][0] <= lt <= c["scream"][1]:
        amp = 0.7 + 0.3 * math.sin(t * 25)
    rotx = 0.0; hopx = 0.0
    if "throw" in c:
        ta, tb, x1, y1, peak = c["throw"]
        if lt < ta: pass
        elif lt < tb:
            f = (lt - ta) / (tb - ta); x = c["x"] + (x1 - c["x"]) * f; y = c["y"] + (y1 - c["y"]) * f; hopx = 4 * peak * f * (1 - f); rotx = 330 * f
            pose = {"la": (150, -10), "ra": (150, -10)}
        else: x, y = x1, y1
    if "glide" in c:
        ga, gb, gx, gy = c["glide"]
        if lt >= gb: x, y = gx, gy
        elif lt >= ga:
            f = ease_c((lt - ga) / (gb - ga)); x = c["x"] + (gx - c["x"]) * f; y = c["y"] + (gy - c["y"]) * f
        else: x, y = c["x"], c["y"]
    if name in ("lion", "sheep", "deer", "bunny"):
        arr = es.SP[name](t + c.get("seed", 0), 0.0 if c.get("calm") else (1.0 if walk else 0.4))
    else:
        arr = chars2.draw(name, t + c.get("seed", 0), amp, blink, pose or None, walk=walk, look=look)
    im = Image.fromarray(arr, "RGBA")
    if c.get("salt") and lt >= c["salt"]:
        a_ = np.asarray(im).astype(F32); lum = a_[..., :3].mean(axis=2, keepdims=True)
        a_[..., :3] = np.clip(lum * 0.55 + 120, 0, 255) * np.array([0.96, 0.97, 1.0], F32); im = Image.fromarray(a_.astype(np.uint8), "RGBA")
    sq = ex.get("sq", 1.0)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s * sq))), Image.NEAREST)
    if ex.get("rot"):
        im = im.rotate(-ex["rot"], resample=Image.NEAREST, expand=True, center=(im.width / 2, im.height))
    if fl: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rotx:
        im = im.rotate(rotx, resample=Image.NEAREST, expand=True, center=(im.width / 2, im.height / 2))
    hop = ex.get("hop", 0) + hopx
    base.paste(im, (int(x - im.width / 2), int(y - im.height + 3 - hop)), im)
    for (ba, bb, txt) in c.get("bubbles", []):
        if ba <= lt <= bb:
            d = ImageDraw.Draw(base); wob = int(math.sin(t * 30) * 1)
            d.text((min(PW - 4 - int(d.textlength(txt, font=_FONT)), max(3, int(x) - int(d.textlength(txt, font=_FONT) / 2))) + wob, int(y - im.height - hop) - 10), txt, font=_FONT, fill=(255, 250, 235), stroke_width=1, stroke_fill=(150, 20, 30))

def draw(base, o, t, lt, speaker_amp=0.0):
    env = o.get("env", "day"); props = o.get("props", [])
    st = static(env, props)
    arr = st.copy()
    if env == "den": dyn_den(arr, t)
    elif env.startswith("ship") or env in ("shore", "sea", "sea_storm", "sea_night"): dyn_sea(arr, env, t)
    elif env in ("prison", "house"): dyn_room(arr, env, t)
    elif env.startswith("palace"): dyn_palace(arr, env, t, props)
    else: dyn_outdoor(arr, env, t, props)
    # slow camera push (parallax-free zoom feel via tiny shift)
    qk = o.get("quake")
    if qk and qk[0] <= lt <= qk[1]:
        sh_ = int(round(math.sin(t * 60) * 2.5)); arr = np.roll(arr, sh_, axis=1)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    base.paste(im, (0, 0))
    # ground shadows for cast
    cast = sorted(o.get("cast", []), key=lambda c: c["y"])
    for c in cast: cast_member(base, c, t, lt, speaker_amp)
    # foreground overlays
    if o.get("fg") == "fog":
        a = np.asarray(base).astype(F32)
        a[200:] = a[200:] * 0.9 + 12
        base.paste(Image.fromarray(a.astype(np.uint8)))
