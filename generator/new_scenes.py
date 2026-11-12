# executed inside gen4 globals
import giant as _giant
NEWK = {"ark_build", "flood", "rainbow", "duel", "palace", "den", "jonah", "redsea", "nativity"}

def spr(base, arr, x, y, sc=1.0, flip=False, ang=0.0):
    im = Image.fromarray(np.array(arr, copy=True), "RGBA")
    if sc != 1.0: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.NEAREST)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if ang:
        pad = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0)); pad.paste(im, (im.width // 2, im.height))
        pad = pad.rotate(ang, resample=Image.NEAREST, center=(im.width, im.height * 2 - 3)); im = pad
        base.paste(im, (int(x - im.width / 2), int(y - im.height + 3)), im); return
    base.paste(im, (int(x - im.width / 2), int(y - im.height + 3)), im)

def mini(d, x, y, col, t, ph=0.0, s=1):
    b = int(abs(math.sin(t * 7 + ph)) * 1.2)
    d.rectangle([x - 1 * s, y - 6 * s - b, x + 1 * s, y - 2 * s - b], fill=col); d.rectangle([x - 1 * s, y - 8 * s - b, x + 1 * s, y - 6 * s - b], fill=(226, 180, 140))
    d.point((x - 1, y - 1 - (b == 0)), fill=(60, 40, 30)); d.point((x + 1, y - 1), fill=(60, 40, 30))

def rain(d, t, n=70, col=(170, 190, 230), y0=0, y1=PH):
    rr = random.Random(5)
    for i in range(n):
        x = rr.uniform(0, PW + 40); sp = 140 + rr.uniform(0, 80); y = (rr.uniform(0, y1) + t * sp) % (y1 - y0) + y0
        xx = (x - t * 40) % (PW + 20)
        d.line([(xx, y), (xx - 2, y + 6)], fill=col)

def lightning(base, t, lt):
    k = (lt * 0.55) % 1
    if k < 0.06:
        ov = Image.new("RGB", (PW, PH), (200, 210, 255)); a = 1 - k / 0.06
        return Image.blend(base, ov, 0.55 * a)
    return base

def boat(d, x, y, t, tilt=0.0, sail=True):
    bob = 1.5 * math.sin(t * 2.1)
    y = y + bob; k = tilt
    d.polygon([(x - 18, y - 4 + k), (x + 18, y - 4 - k), (x + 12, y + 5), (x - 12, y + 5)], fill=(120, 78, 44))
    d.line([(x - 18, y - 4 + k), (x + 18, y - 4 - k)], fill=(170, 118, 70))
    if sail:
        d.line([(x, y - 4), (x, y - 34)], fill=(90, 60, 36))
        d.polygon([(x + 1, y - 33), (x + 1, y - 9), (x + 17, y - 11 - k * 0.4)], fill=(240, 232, 214))
        d.polygon([(x - 1, y - 30), (x - 1, y - 9), (x - 13, y - 10)], fill=(222, 210, 188))

def ark(d, x, y, t, s=1.0, bob=True):
    b = 1.5 * math.sin(t * 1.4) if bob else 0
    y = y + b
    d.polygon([(x - 38, y - 12), (x + 38, y - 12), (x + 28, y + 6), (x - 28, y + 6)], fill=(116, 72, 40))
    for i in range(-3, 4): d.line([(x + i * 10, y - 12), (x + i * 8, y + 5)], fill=(94, 58, 32))
    d.line([(x - 38, y - 12), (x + 38, y - 12)], fill=(160, 108, 62))
    d.rectangle([x - 24, y - 30, x + 24, y - 12], fill=(150, 100, 56))
    for i in range(-2, 3): d.line([(x + i * 10, y - 30), (x + i * 10, y - 13)], fill=(128, 84, 46))
    d.polygon([(x - 28, y - 30), (x, y - 44), (x + 28, y - 30)], fill=(96, 60, 34))
    d.rectangle([x - 4, y - 25, x + 4, y - 18], fill=(255, 224, 140))

def daysky(d, t, c0=(120, 190, 240), c1=(210, 232, 245), nc=3):
    grad(d, 0, HZ, c0, c1)
    for i in range(nc): cloud(d, ((t * 5 + i * 80) % 240) - 35, 56 + i * 14, 1.0)

def star8(d, cx, cy, pr, col=(255, 228, 140)):
    d.polygon([(cx, cy - pr), (cx + 3, cy - 3), (cx + pr, cy), (cx + 3, cy + 3), (cx, cy + pr), (cx - 3, cy + 3), (cx - pr, cy), (cx - 3, cy - 3)], fill=col)

def glow(d, cx, cy, r, c_in, c_out, n=8):
    for i in range(n, 0, -1):
        rr = r * i / n; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=lerpc(c_in, c_out, (i / n) ** 1.3))

def stars(d, t, n=50, ymax=130, seed=3):
    rr = random.Random(seed)
    for i in range(n):
        if (int(t * 2) + i) % 5: d.point((rr.randrange(PW), rr.randrange(ymax)), fill=(230, 235, 255))

def desert(d, t, sky0=(110, 180, 235), sky1=(240, 224, 190), gcol=(214, 184, 120)):
    grad(d, 0, HZ, sky0, sky1); hills(d, 150, (200, 164, 110), 12, 1, t, 2); ground(d, gcol, (196, 166, 104))
    for i in range(2): cloud(d, ((t * 4 + i * 100) % 240) - 35, 50 + i * 16, 1.0)

def whale_draw(d, x, y, t, mouth):
    body = (44, 86, 138); dk = (32, 64, 112); belly = (178, 206, 228)
    sway = 2 * math.sin(t * 1.6)
    # tail stalk and flukes
    d.polygon([(x + 34, y - 8), (x + 56, y - 14 - sway), (x + 56, y + 2 - sway), (x + 34, y + 10)], fill=body)
    d.polygon([(x + 54, y - 8 - sway), (x + 74, y - 34 - sway * 2), (x + 80, y - 24 - sway * 2), (x + 68, y - 8 - sway)], fill=dk)
    d.polygon([(x + 54, y - 4 - sway), (x + 78, y + 10 - sway), (x + 68, y + 12 - sway), (x + 52, y + 2 - sway)], fill=dk)
    # body
    d.ellipse([x - 58, y - 26, x + 42, y + 26], fill=body)
    d.ellipse([x - 58, y - 26, x + 42, y - 2], fill=dk) if False else None
    d.chord([x - 58, y - 26, x + 42, y + 26], 195, 345, fill=dk)
    d.chord([x - 54, y - 2, x + 38, y + 26], 10, 170, fill=belly)
    for i in range(5): d.line([(x - 40 + i * 4, y + 8 + i), (x - 24 + i * 4, y + 8 + i)], fill=(150, 180, 206))
    # flipper
    d.polygon([(x - 6, y + 10), (x + 14, y + 26), (x + 4, y + 28), (x - 14, y + 16)], fill=dk)
    # mouth + eye
    d.line([(x - 56, y + 4), (x - 22, y + 6)], fill=(20, 40, 80), width=2)
    if mouth > 0.02:
        mdrop = 4 + 11 * mouth
        d.polygon([(x - 57, y + 2), (x - 20, y + 5), (x - 28, y + 5 + mdrop), (x - 56, y + 4 + mdrop * 1.1)], fill=(120, 30, 56))
        d.polygon([(x - 54, y + 4 + mdrop * 0.6), (x - 30, y + 6 + mdrop * 0.5), (x - 34, y + 4 + mdrop), (x - 54, y + 3 + mdrop)], fill=(214, 96, 110))
        d.chord([x - 58, y - 2, x - 18, y + 14 + mdrop], 90, 170, fill=body) if False else None
        d.polygon([(x - 56, y + 4 + mdrop * 1.1), (x - 26, y + 6 + mdrop), (x - 30, y + 10 + mdrop), (x - 54, y + 8 + mdrop * 1.1)], fill=body)
    d.ellipse([x - 44, y - 10, x - 38, y - 4], fill=(246, 248, 252)); d.rectangle([x - 43, y - 8, x - 41, y - 6], fill=(12, 14, 30)); d.point((x - 44, y - 12), fill=dk)

def draw_new(d, base, kind, o, t, lt):
    st = o.get("stage", "")
    if kind == "ark_build":
        daysky(d, t); hills(d, 150, (140, 190, 150), 12, 2, t, 1); ground(d, (86, 150, 70))
        for x, h in ((12, 44), (170, 40)): tree(d, x, 164, h, (50, 130, 60), sway=1.0, t=t)
        ark(d, 124, 160, t, bob=False)
        d.polygon([(70, 166), (92, 150), (96, 154), (74, 168)], fill=(150, 104, 60))
        if st == "noah":
            person(base, "Peter", 50, 168, t, 0.62)
            sd = int(t * 4) % 2
            d.rectangle([66 + sd, 146 - sd * 2, 70 + sd, 148 - sd * 2], fill=(150, 150, 160))
            if sd: sparkles(d, 70, 150, t % 0.5, 3, 6)
            for i in range(4): d.rectangle([98 + i * 6, 163, 102 + i * 6, 164], fill=(150, 104, 60))
        else:
            person(base, "Peter", 22, 168, t, 0.55)
            names = ("lion", "sheep", "deer", "bunny")
            for i, nm in enumerate(names):
                for j in range(2):
                    ph = ((lt * 0.2 - i * 0.2 - j * 0.04) % 1.0) if lt > 0.2 else -1
                    if 0 <= ph <= 1:
                        x = -10 + 108 * ph
                        if x > 96: continue
                        actor(base, nm, int(x), 168 - int((x - 70) * 0.6) if x > 74 else 168, t + j * 0.3, 0.5, walk=1.0)
        motes(d, t, 8, (255, 250, 200), 80, 200)
    elif kind == "flood":
        calm = st == "calm"
        if not calm:
            grad(d, 0, HZ, (30, 36, 60), (88, 98, 128))
            for i in range(5): cloud(d, ((t * 8 + i * 55) % 250) - 40, 30 + (i % 3) * 18, 1.6, (70, 76, 100) if i % 2 else (88, 94, 120))
            d.rectangle([0, 128, PW, PH], fill=(24, 54, 100))
            for k in range(4): waves(d, 128 + k * 8, 140 + k * 8, (70, 110, 170), t + k)
            ark(d, 90, 134 + int(3 * math.sin(t * 1.8)), t, bob=False)
            for y in range(124, 190, 4):
                for x in range(0, PW, 3):
                    if int(y + 4 * math.sin(x * 0.08 + t * 3 + y)) % 7 == 0: d.point((x, y + 6), fill=(110, 150, 210))
            rain(d, t, 90, (160, 180, 225), 0, 170)
        else:
            grad(d, 0, HZ, (255, 190, 130), (255, 236, 190)); sun(d, 140, 60, 11, t)
            for i in range(3): cloud(d, ((t * 4 + i * 80) % 240) - 35, 40 + i * 16, 1.0, (255, 235, 215))
            d.rectangle([0, 138, PW, PH], fill=(70, 130, 190)); waves(d, 140, 190, (140, 190, 230), t)
            peak = 0.4 * ease(lt / 5.0)
            d.polygon([(0, 140), (46, 140 - int(30 + 28 * peak)), (96, 140)], fill=(120, 104, 100))
            d.polygon([(46, 140 - int(30 + 28 * peak)), (40, 140 - int(22 + 20 * peak)), (52, 140 - int(22 + 20 * peak))], fill=(240, 240, 245))
            ark(d, 124, 138 + int(2 * math.sin(t * 1.2)), t, bob=False)
            for i in range(5): bird(d, ((t * 8 + i * 50) % 220) - 10, 90 + 6 * math.sin(t + i), t, (90, 60, 50))
        lt_img = None
    elif kind == "rainbow":
        grad(d, 0, HZ, (110, 180, 240), (225, 240, 250)); hills(d, 150, (130, 190, 140), 14, 2, t, 3); ground(d, (80, 156, 72))
        for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 40 + i * 14, 1.0)
        cols = [(230, 50, 60), (250, 140, 40), (250, 220, 60), (70, 190, 90), (60, 140, 230), (110, 80, 200)]
        grow = ease(lt / 2.0)
        for i, c in enumerate(cols):
            r = 84 - i * 4
            d.arc([90 - r, 150 - r, 90 + r, 150 + r], 180, 180 + 180 * grow, fill=c, width=4)
        tree(d, 22, 165, 38, (50, 130, 60), sway=1.0, t=t); tree(d, 160, 166, 30, (60, 145, 66), sway=1.0, t=t)
        ark(d, 120, 160, t, bob=False)
        for i, x in enumerate((60, 80, 100, 140, 40)): flower(d, x, 172 + (i % 3) * 3, ((240, 90, 120), (255, 220, 90), (200, 120, 230))[i % 3], 6, t)
        if st == "dove":
            ph = (lt * 0.3) % 1.0; x = -10 + 200 * ph; y = 90 + 14 * math.sin(ph * 6)
            w = int(3 * math.sin(t * 14))
            d.ellipse([x - 5, y - 3, x + 4, y + 3], fill=(250, 250, 252)); d.ellipse([x + 3, y - 5, x + 8, y - 1], fill=(250, 250, 252))
            d.line([(x - 1, y - 2), (x - 4, y - 8 - w)], fill=(235, 235, 245), width=2); d.line([(x - 1, y - 2), (x + 3, y - 8 + w)], fill=(235, 235, 245), width=2)
            d.point((int(x + 7), int(y - 3)), fill=(250, 190, 60)); d.ellipse([x + 7, y + 1, x + 11, y + 3], fill=(90, 150, 60))
        else:
            sparkles(d, 90, 80, t, 10, 40)
        motes(d, t, 10, (255, 250, 200), 60, 200)
    elif kind == "duel":
        desert(d, t)
        for i in range(8):
            mini(d, 6 + i * 5, 168 + (i % 2), (60, 100, 190), t, i); d.line([(6 + i * 5 + 2, 160), (6 + i * 5 + 2, 168)], fill=(120, 110, 100))
        for i in range(8):
            mini(d, 120 + i * 6, 168 + (i % 2), (190, 70, 60), t, i + 3)
        gx = 138
        if st in ("giant", "boy"):
            gx = 128
        if st in ("giant", "king"):
            spr(base, _giant.draw(t), gx, 170, 1.0, flip=True)
            if st == "giant": sparkles(d, 130, 60, t, 4, 14)
        if st == "boy":
            person(base, "David", 48 + o.get("dx", 0) * ease(lt / 3.0), 169, t, 0.55)
            spr(base, _giant.draw(t), gx, 170, 1.0, flip=True)
            xs = [(34 + 6 * i, 165) for i in range(3)]
            for i in range(3): d.ellipse([24 + i * 5, 168, 28 + i * 5, 172], fill=(230, 224, 214)) if False else None
            for i in range(6): d.ellipse([18 + i * 3, 172 + (i % 2), 21 + i * 3, 175 + (i % 2)], fill=(238, 240, 245))
        if st == "sling":
            gx = 112; hx, hy = 56, 120
            person(base, "David", 40, 169, t, 0.55)
            if lt < 2.0:
                a = lt * 14; r = 9
                sx, sy = hx + r * math.cos(a), hy + r * math.sin(a) * 0.6
                d.line([(hx, hy + 10), (hx, hy)], fill=(120, 80, 50)); d.line([(hx, hy), (sx, sy)], fill=(160, 120, 80))
                d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(240, 240, 245))
            hit = lt - 2.2
            if hit < 0:
                spr(base, _giant.draw(t), gx, 170, 1.0, flip=True)
            else:
                p = min(1, hit / 0.45)
                if p < 1:
                    spr(base, _giant.draw(t), gx, 170, 1.0, flip=True)
                    sx = hx + (gx - 8 - hx) * p; sy = hy + (66 - hy) * p - 12 * math.sin(p * math.pi)
                    d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(250, 250, 255))
                else:
                    f = ease_c((hit - 0.45) / 0.9)
                    spr(base, _giant.draw(0), gx, 170, 1.0, flip=True, ang=-68 * f)
                    sparkles(d, gx - 6, 70, hit - 0.45, 8, 16)
        if st == "king":
            pass
    elif kind == "palace":
        d.rectangle([0, 0, PW, PH], fill=(104, 40, 56)); d.rectangle([0, 0, PW, 40], fill=(80, 28, 44))
        for x in (6, 62, 118, 168):
            d.rectangle([x, 30, x + 10, HZ], fill=(214, 186, 130)); d.rectangle([x - 2, 28, x + 12, 34], fill=(234, 208, 150)); d.rectangle([x + 2, 30, x + 3, HZ], fill=(236, 214, 164))
        d.rectangle([0, HZ, PW, PH], fill=(150, 120, 90))
        for x in range(0, PW, 18): d.line([(x, HZ), (x - 20, PH)], fill=(130, 100, 74))
        d.polygon([(70, 40), (110, 40), (110, 166), (70, 166)], fill=(70, 100, 170)) if False else None
        if st == "window":
            d.rectangle([0, 0, PW, PH], fill=(16, 18, 44)); stars(d, t, 40, 90)
            d.rectangle([56, 40, 124, 146], fill=(30, 36, 80)); d.pieslice([56, 20, 124, 60], 180, 360, fill=(30, 36, 80))
            d.ellipse([84, 56, 100, 72], fill=(250, 244, 210)); d.ellipse([90, 54, 104, 70], fill=(30, 36, 80))
            d.rectangle([0, HZ, PW, PH], fill=(60, 48, 70))
            d.rectangle([52, 140, 128, 150], fill=(120, 96, 80))
            glow(d, 90, 110, 46, (200, 210, 255), (30, 36, 80), 6)
            person(base, "David", 90, 168, t, 0.66)
            sparkles(d, 90, 120, t, 6, 20)
        else:
            d.rectangle([66, 70, 114, 150], fill=(180, 40, 60)); d.rectangle([62, 96, 118, 104], fill=(214, 168, 70))
            d.rectangle([66, 150, 114, 166], fill=(140, 100, 40))
            person(base, "Solomon", 90, 168, t, 0.68)
            if st == "trap":
                person(base, "Peter", 28, 168, t, 0.55); person(base, "Peter", 152, 168, t, 0.55, flip=True)
                d.rectangle([76, 120, 104, 138], fill=(244, 236, 210)); d.line([(80, 126), (100, 126)], fill=(90, 70, 50)); d.line([(80, 131), (98, 131)], fill=(90, 70, 50))
                sparkles(d, 90, 120, t, 5, 12)
            elif st == "court":
                person(base, "David", 28, 168, t, 0.55)
                for x in (140, 158): person(base, "Peter", x, 168, t, 0.5, flip=True)
            elif st == "grief":
                person(base, "David", 30, 168, t, 0.55)
    elif kind == "den":
        night = st != "morning"
        if night:
            grad(d, 0, PH, (14, 10, 18), (44, 32, 38))
            d.pieslice([-20, 10, 200, 210], 180, 360, fill=(24, 18, 26)); d.ellipse([30, 30, 150, 190], fill=(34, 26, 34)) if False else None
            d.rectangle([0, HZ, PW, PH], fill=(78, 62, 54))
            rr = random.Random(8)
            for _ in range(80): d.point((rr.randrange(PW), rr.randrange(HZ, PH)), fill=(62, 48, 42))
            for x in (10, 60, 130, 172): d.polygon([(x, 0), (x + 10, 0), (x + 5, 14 + (x % 7))], fill=(26, 20, 28))
            d.rectangle([154, 20, 178, 24], fill=(24, 20, 26)) if False else None
        else:
            grad(d, 0, HZ, (255, 214, 150), (255, 244, 214)); d.rectangle([0, HZ, PW, PH], fill=(146, 124, 96))
            d.pieslice([-10, 40, 190, 240], 180, 360, fill=(70, 56, 52)) if False else None
            for a in range(0, 180, 12):
                aa = math.radians(200 + a * 0.5); d.line([(40, 0), (40 + 260 * math.cos(aa + 1.1), 260 * math.sin(aa + 1.1) + 0)], fill=(255, 238, 190)) if False else None
            sun(d, 150, 40, 10, t)
        gy = 168
        lions = [(24, True), (150, False), (46, True), (132, False)] if st != "morning" else [(30, True), (150, False)]
        for i, (x, fl) in enumerate(lions):
            actor(base, "lion", x, gy + (i % 2) * 3, t * 0.2, 0.55, flip=fl, walk=0.0)
        if st in ("angel", "morning", "inside"):
            if st == "angel":
                glow(d, 90, 90, 56, (255, 252, 225), (44, 32, 38), 9)
                for i in range(5):
                    ax = 90 + (i - 2) * 9
                    d.polygon([(ax, 20), (ax + 2, 20), (ax + 10 + (i - 2) * 6, 166), (ax - 8 + (i - 2) * 6, 166)], fill=(255, 245, 200)) if False else None
                shafts(base, t, 40, 60, 3)
                d.polygon([(78, 34), (102, 34), (96, 60), (84, 60)], fill=(255, 255, 250))
                wing = int(3 * math.sin(t * 3))
                d.polygon([(78, 38), (56, 28 - wing), (60, 54), (80, 52)], fill=(250, 250, 255)); d.polygon([(102, 38), (124, 28 - wing), (120, 54), (100, 52)], fill=(250, 250, 255))
                d.ellipse([84, 24, 96, 36], fill=(255, 226, 190)); d.ellipse([83, 19, 97, 24], fill=(255, 236, 140))
                sparkles(d, 90, 50, t, 10, 30)
            person(base, "David", 90, 168, t, 0.66)
        else:
            person(base, "David", 90, 168, t, 0.66)
        motes(d, t, 12, (255, 220, 160) if night else (255, 250, 200), 40, 180)
    elif kind == "jonah":
        if st in ("ship", "storm", "whale"):
            if st == "storm":
                grad(d, 0, HZ, (24, 30, 54), (80, 90, 120))
                for i in range(5): cloud(d, ((t * 10 + i * 55) % 250) - 40, 24 + (i % 3) * 16, 1.7, (60, 66, 92) if i % 2 else (82, 88, 116))
                sea = (22, 48, 92); wc = (80, 120, 180)
            elif st == "whale":
                grad(d, 0, HZ, (50, 70, 120), (140, 150, 170)); sea = (24, 60, 110); wc = (90, 140, 200)
                for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 40 + i * 16, 1.0, (190, 196, 214))
            else:
                grad(d, 0, HZ, (120, 190, 240), (215, 234, 246)); sea = (40, 110, 190); wc = (130, 190, 240)
                for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 40 + i * 14, 1.0)
            d.rectangle([0, 126, PW, PH], fill=sea)
            for k in range(5): waves(d, 126 + k * 9, 140 + k * 9, wc, t * (2 if st == "storm" else 1) + k)
            if st == "ship":
                bx = 40 + 70 * ease_c(lt / 7.0); boat(d, bx, 132, t); person(base, "Peter", bx - 4, 130 + int(1.5 * math.sin(t * 2.1)), t, 0.36)
            if st == "storm":
                tilt = 8 * math.sin(t * 2.6); boat(d, 90, 132 - int(6 * abs(math.sin(t * 1.5))), t, tilt)
                rain(d, t, 90, (160, 180, 225), 0, 170)
            if st == "whale":
                rise = ease_c(lt / 1.8)
                bxx = 24
                boat(d, bxx, 132, t, 3 * math.sin(t * 2))
                fy = 176 - 62 * rise
                mo = ease_c((lt - 1.8) / 0.7)
                whale_draw(d, 104, fy, t, mo)
                d.rectangle([0, 146, PW, PH], fill=sea)
                for k in range(4): waves(d, 146 + k * 9, 158 + k * 9, wc, t + k)
                for i in range(14):
                    ph = ((t * 1.3 + i * 0.37) % 1); sx = 50 + 70 * ((i * 0.618) % 1)
                    if rise > 0.3: d.point((int(sx), int(146 - 22 * math.sin(ph * math.pi))), fill=(220, 238, 252))
                if lt > 2.2:
                    pj = min(1, (lt - 2.2) / 1.8)
                    jx = 30 + 24 * pj; jy = 108 - 18 * math.sin(math.pi * pj) + 22 * pj
                    if pj < 1: person(base, "Peter", jx, int(jy + 12), t, 0.3)
        elif st == "inside":
            grad(d, 0, PH, (60, 12, 36), (110, 30, 56))
            for i in range(7):
                x = 8 + i * 28; d.arc([x - 30, 30, x + 30, 260], 200, 340, fill=(220, 176, 170), width=3)
            for y in range(0, PH, 8): d.line([(0, y), (PW, y + 3 * math.sin(t + y))], fill=(130, 40, 70)) if False else None
            d.rectangle([0, 170, PW, PH], fill=(90, 26, 50))
            glow(d, 90, 116, 40, (255, 240, 190), (90, 26, 50), 8)
            person(base, "Peter", 90, 168, t, 0.66)
            for i in range(10):
                bx = 20 + (i * 17) % 150; by = 200 - (t * (10 + i) + i * 20) % 170
                d.ellipse([bx - 2, by - 2, bx + 2, by + 2], outline=(240, 190, 190))
            sparkles(d, 90, 120, t, 6, 24)
        elif st == "shore":
            grad(d, 0, HZ, (250, 170, 120), (255, 236, 190)); sun(d, 130, 90, 12, t)
            d.rectangle([0, 126, PW, 160], fill=(70, 130, 190)); waves(d, 128, 158, (150, 200, 240), t)
            d.rectangle([0, 160, PW, PH], fill=(236, 214, 160))
            rr = random.Random(2)
            for _ in range(60): d.point((rr.randrange(PW), rr.randrange(162, PH)), fill=(214, 190, 136))
            person(base, "Peter", 60, 172, t, 0.66)
            d.ellipse([140, 132, 170, 148], fill=(50, 92, 140)); d.polygon([(168, 138), (180, 128), (180, 150)], fill=(50, 92, 140))
            for i in range(3): bird(d, ((t * 10 + i * 60) % 220) - 10, 70 + i * 8, t, (90, 60, 50))
        elif st == "city":
            grad(d, 0, HZ, (255, 190, 130), (255, 236, 196)); sun(d, 150, 60, 12, t)
            d.rectangle([0, HZ, PW, PH], fill=(204, 172, 120))
            for x, h, w in ((4, 60, 26), (34, 84, 22), (60, 50, 30), (96, 96, 24), (124, 64, 26), (154, 76, 24)):
                d.rectangle([x, HZ - h, x + w, HZ], fill=(196, 150, 104)); d.rectangle([x, HZ - h, x + w, HZ - h + 3], fill=(224, 182, 130))
                for wy in range(HZ - h + 8, HZ - 6, 14): d.rectangle([x + 5, wy, x + 7, wy + 5], fill=(80, 56, 44)); d.rectangle([x + w - 8, wy, x + w - 6, wy + 5], fill=(80, 56, 44))
            for i in range(9): mini(d, 12 + i * 18, 170 + (i % 2) * 3, ((200, 80, 80), (80, 120, 200), (230, 190, 80))[i % 3], t, i)
            person(base, "Peter", 90, 168, t, 0.6)
            sparkles(d, 90, 120, t, 8, 30)
    elif kind == "redsea":
        if st in ("chase", "trap"):
            desert(d, t)
            if st == "trap":
                d.rectangle([110, 120, PW, PH], fill=(40, 110, 190)); waves(d, 124, 170, (130, 190, 240), t)
                for i in range(14): mini(d, 60 + (i % 7) * 6 + (i // 7) * 3, 164 + (i // 7) * 6, ((220, 220, 230), (200, 90, 70), (80, 130, 200))[i % 3], t, i)
                for i in range(3):
                    cx = 8 + i * 16 + 3 * math.sin(t * 5 + i); sparkles(d, cx, 150, t, 2, 3) if False else None
                    d.rectangle([cx - 5, 150, cx + 5, 158], fill=(200, 160, 60)); d.ellipse([cx - 5, 156, cx - 1, 162], fill=(60, 50, 50)); d.ellipse([cx + 1, 156, cx + 5, 162], fill=(60, 50, 50))
                    d.ellipse([cx + 6, 146, cx + 14, 156], fill=(140, 90, 56))
                for i in range(10): d.point(((i * 13 + int(t * 40)) % 60, 160 - (i * 7) % 24), fill=(224, 196, 150))
            else:
                for i in range(3):
                    cx = 30 + ((lt * 26 + i * 52) % 200) - 40
                    d.rectangle([cx - 6, 148, cx + 6, 157], fill=(210, 168, 66)); d.ellipse([cx - 5, 154, cx - 1, 161], fill=(60, 50, 50)); d.ellipse([cx + 1, 154, cx + 5, 161], fill=(60, 50, 50))
                    d.ellipse([cx + 7, 143, cx + 17, 156], fill=(140, 90, 56)); d.line([(cx + 7, 150), (cx - 6, 152)], fill=(90, 60, 40))
                    for j in range(5): d.point((int(cx - 10 - j * 4), 158 + (j * 3) % 8), fill=(224, 196, 150))
                for i in range(8): mini(d, 150 + (i % 4) * 5, 164 + (i // 4) * 5, (200, 200, 220), t, i)
        else:
            grad(d, 0, HZ, (255, 180, 120), (255, 232, 190)) if st == "part" else grad(d, 0, HZ, (120, 190, 240), (214, 232, 246))
            d.rectangle([0, HZ, PW, PH], fill=(214, 184, 126))
            rr = random.Random(5)
            for _ in range(60): d.point((rr.randrange(PW), rr.randrange(HZ, PH)), fill=(196, 166, 108))
            open_ = ease_c(lt / 1.8) if st == "part" else (1 - ease_c(lt / 2.2) if st == "close" else 1.0)
            wl = int(90 - 68 * open_)
            for side in (0, 1):
                x0, x1 = (0, wl + 14) if side == 0 else (PW - wl - 14, PW)
                for y in range(0, 176, 2):
                    sh = 0.5 + 0.5 * math.sin(y * 0.2 + t * 3 + side)
                    d.rectangle([x0, y, x1, y + 1], fill=lerpc((30, 90, 170), (70, 150, 220), sh * 0.7))
                edge = x1 if side == 0 else x0
                for y in range(0, 176, 6): d.point((int(edge + (4 if side == 0 else -4) * math.sin(y + t * 4)), y), fill=(200, 230, 255))
                for k in range(4):
                    fx = x0 + 6 + (k * 11 + 3) % max(6, (x1 - x0 - 10)); fy = 40 + k * 34 + 6 * math.sin(t * 2 + k)
                    fish(d, int(fx), int(fy), side == 1, ((255, 150, 60), (255, 220, 90), (130, 240, 240), (230, 120, 220))[k], 1.0)
                if open_ < 1 or st == "close":
                    pass
            if st in ("part", "cross"):
                for i in range(6): d.line([(20 + i * 30, 6 + (i % 3) * 8), (40 + i * 30, 6 + (i % 3) * 8)], fill=(255, 255, 255)) if st == "part" and int(t * 6 + i) % 3 == 0 else None
            if st == "cross":
                for i in range(18):
                    px_ = ((lt * 8 + i * 6) % 130) + 25
                    if wl < 58: pass
                    mini(d, px_, 166 + (i % 3) * 4, ((220, 220, 230), (200, 90, 70), (80, 130, 200), (230, 190, 80))[i % 4], t, i)
            if st == "close":
                d.rectangle([0, HZ - 6 + int(10 * (1 - open_)), PW, PH], fill=lerpc((214, 184, 126), (40, 110, 190), 1 - open_)) if False else None
                for i in range(3):
                    cx = 70 + i * 22 - int(14 * (1 - open_)); d.rectangle([cx - 5, 150, cx + 5, 158], fill=(200, 160, 60)); d.ellipse([cx - 5, 156, cx - 1, 162], fill=(60, 50, 50)); d.ellipse([cx + 1, 156, cx + 5, 162], fill=(60, 50, 50))
                waves(d, 150, 176, (200, 230, 255), t * 2)
    elif kind == "nativity":
        if st in ("road", "magi", "shepherds"):
            grad(d, 0, HZ, (6, 10, 40), (60, 60, 120)); stars(d, t, 70, 120, 7)
            hills(d, 152, (26, 30, 70), 14, 2, t, 4); ground(d, (40, 44, 76))
        if st == "road":
            glow(d, 150, 140, 26, (255, 214, 130), (26, 30, 70), 5) if False else None
            for x, h, w in ((140, 18, 14), (156, 26, 16), (174, 16, 12)):
                d.rectangle([x, 150 - h, x + w, 152], fill=(58, 50, 90))
                d.rectangle([x + 3, 150 - h + 5, x + 5, 150 - h + 8], fill=(255, 214, 130))
            star8(d, 148, 34, 6 + int(1.2 * math.sin(t * 3)))
            mx = 20 + 60 * ease_c(lt / 7.0)
            person(base, "Mary", mx, 168, t, 0.6); person(base, "Peter", mx - 22, 168, t, 0.6)
            d.ellipse([mx + 6, 150, mx + 28, 164], fill=(150, 144, 140)); d.rectangle([mx + 22, 142, mx + 26, 152], fill=(150, 144, 140))
            for lx in (mx + 10, mx + 24): d.line([(lx, 162), (lx, 169 + int(math.sin(t * 8 + lx)))], fill=(130, 124, 120))
        elif st in ("stable", "find"):
            grad(d, 0, HZ, (10, 14, 50), (70, 60, 110)); stars(d, t, 60, 100, 9)
            ground(d, (60, 56, 74))
            star8(d, 150, 70, 8 + int(1.5 * math.sin(t * 3)))
            for a in range(0, 360, 45): d.line([(150, 70), (150 + 20 * math.cos(math.radians(a + t * 20)), 70 + 20 * math.sin(math.radians(a + t * 20)))], fill=(255, 226, 150))
            d.rectangle([40, 82, 140, 168], fill=(110, 76, 46)); d.polygon([(30, 86), (90, 50), (150, 86)], fill=(140, 96, 56))
            for x in range(40, 140, 8): d.line([(x, 84), (x, 168)], fill=(90, 60, 36))
            glow(d, 90, 142, 40, (255, 232, 170), (110, 76, 46), 7)
            d.rectangle([40, 168, 140, 172], fill=(150, 120, 70))
            d.polygon([(76, 152), (104, 152), (100, 166), (80, 166)], fill=(150, 104, 60)); d.rectangle([78, 148, 102, 154], fill=(238, 214, 120))
            d.ellipse([84, 144, 96, 152], fill=(250, 244, 236)); d.ellipse([88, 141, 94, 147], fill=(250, 206, 170))
            glow(d, 90, 146, 18, (255, 250, 220), (238, 214, 120), 4) if False else None
            sparkles(d, 90, 142, t, 8, 20)
            person(base, "Mary", 56, 168, t, 0.56); person(base, "Peter", 124, 168, t, 0.56, flip=True)
            if st == "find":
                for i, x in enumerate((14, 166)):
                    ph = ease_c((lt - 0.2 - i * 0.5) / 2.0)
                    xx = (-14 if x < 90 else 194) + (x - (-14 if x < 90 else 194)) * ph
                    person(base, "David", xx, 170, t, 0.52, flip=x > 90, )
        elif st == "shepherds":
            for i, x in enumerate((20, 52, 150)): actor(base, "sheep", x, 168 + (i % 2) * 3, t * 0.3, 0.5, walk=0.3)
            person(base, "David", 100, 168, t, 0.6)
            p = ease(lt / 1.2)
            glow(d, 90, 54, 44 * p, (255, 252, 230), (30, 34, 90), 9)
            for a in range(0, 360, 24):
                aa = math.radians(a + t * 10); d.line([(90, 54), (90 + 100 * math.cos(aa), 54 + 100 * math.sin(aa))], fill=(210, 220, 255)) if False else None
            d.polygon([(80, 44), (100, 44), (96, 70), (84, 70)], fill=(255, 255, 250))
            wing = int(3 * math.sin(t * 3))
            d.polygon([(80, 48), (60, 38 - wing), (64, 62), (82, 60)], fill=(250, 250, 255)); d.polygon([(100, 48), (120, 38 - wing), (116, 62), (98, 60)], fill=(250, 250, 255))
            d.ellipse([84, 32, 96, 44], fill=(255, 226, 190)); d.ellipse([83, 28, 97, 33], fill=(255, 236, 140))
            sparkles(d, 90, 60, t, 12, 40)
        elif st == "magi":
            star8(d, 150, 78, 10 + int(1.5 * math.sin(t * 3)))
            for a in range(0, 360, 45): d.line([(150, 78), (150 + 28 * math.cos(math.radians(a + t * 20)), 78 + 28 * math.sin(math.radians(a + t * 20)))], fill=(255, 226, 150))
            d.polygon([(150, 52), (146, 100), (154, 100)], fill=(255, 226, 150)) if False else None
            mx = 10 + 60 * ease_c(lt / 7.0)
            for i, nm in enumerate(("Solomon", "Peter", "David")):
                person(base, nm, mx + i * 26, 168, t + i, 0.56)
                d.rectangle([mx + i * 26 - 5, 118 if False else 123, mx + i * 26 + 5, 125], fill=(70, 70, 120)) if False else None
            d.rectangle([mx + 6, 150, mx + 10, 154], fill=(250, 210, 90)); d.rectangle([mx + 32, 150, mx + 36, 154], fill=(240, 240, 250)); d.rectangle([mx + 58, 150, mx + 62, 154], fill=(210, 120, 90))
