import sys, math, os, subprocess, random
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

S = sys.argv[1]; PART = int(sys.argv[2]); MODE = sys.argv[3]
sys.path.insert(0, f"{S}/px")
import chars
W, H, FPS = 1080, 1920, 30
PW, PH, K = 180, 320, 6
HZ = 165
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VSR = 24000
OUTD = f"{S}/gen{PART}"; os.makedirs(OUTD, exist_ok=True)

P1 = [
 dict(s=["What does the Bible say about the very beginning?"], t=("THE VERY", "BEGINNING?"), draw="void"),
 dict(s=["Genesis says God created the heavens and the earth, and at first it was dark and empty."], t=("GENESIS 1", "DARK + EMPTY"), draw="void"),
 dict(s=["Day one: God said, let there be light. And there was light."], t=("DAY 1", "LIGHT"), draw="light"),
 dict(s=["Day two: God made the sky."], t=("DAY 2", "SKY"), draw="sky"),
 dict(s=["Day three: dry land, seas, and plants and trees."], t=("DAY 3", "LAND + PLANTS"), draw="land"),
 dict(s=["Day four: the sun, the moon, and the stars."], t=("DAY 4", "SUN, MOON, STARS"), draw="sunmoon"),
 dict(s=["Day five: fish in the sea, and birds in the sky."], t=("DAY 5", "FISH + BIRDS"), draw="fishbirds"),
 dict(s=["Day six: animals on the land, and then people."], t=("DAY 6", "ANIMALS + PEOPLE"), draw="animals"),
 dict(s=["On day seven, God rested. This is where the Sabbath comes from."], t=("DAY 7", "REST"), draw="rest"),
 dict(s=["Next: the Garden of Eden.", "Follow for part two."], t=("PART 2", "EDEN"), draw="outro"),
]
P2 = [
 dict(s=["Was the forbidden fruit really an apple?"], t=("THE FORBIDDEN", "FRUIT?"), draw="eden", o=dict(tree="fruit")),
 dict(s=["After creation, God placed the first man, Adam, in a garden called Eden."], t=("ADAM", "IN EDEN"), draw="eden", o=dict(adam=0.6)),
 dict(s=["Adam named the animals. But none was a partner for him, so God made Eve."], t=("NAMING", "+ EVE"), draw="eden", o=dict(adam=0, naming=True, eve=3.2)),
 dict(s=["They could eat from any tree, except one: the tree of the knowledge of good and evil."], t=("THE ONE", "RULE"), draw="eden", o=dict(adam=0, eve=0, tree="fruit", pair=True)),
 dict(s=["A serpent told Eve she would not die. She ate the fruit, and Adam ate too."], t=("THE", "SERPENT"), draw="eden", o=dict(adam=0, eve=0, tree="fruit", snake=True, pair=True)),
 dict(s=["And no, the text never says it was an apple. It only says fruit."], t=("JUST", "FRUIT"), draw="fruits"),
 dict(s=["They hid, and then they had to leave Eden. But God made clothes for them first."], t=("LEAVING", "EDEN"), draw="gate"),
 dict(s=["That is Genesis, the first book of the Bible.", "Follow for more."], t=("GENESIS", "THE BEGINNING"), draw="outro2"),
]
SCENES = P1 if PART == 1 else P2
FLAT = [(si, x) for si, sc in enumerate(SCENES) for x in sc["s"]]

if MODE == "tts":
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
    for i, (si, txt) in enumerate(FLAT):
        x, sr = k.create(txt, voice="am_michael", speed=1.0, lang="en-us")
        sf.write(f"{OUTD}/s{i}.wav", x, sr); print(i, round(len(x) / sr, 2))
    sys.exit()

def load_trim(i):
    x, sr = sf.read(f"{OUTD}/s{i}.wav")
    x = x / np.abs(x).max() * 0.9
    idx = np.where(np.abs(x) > 0.02)[0]
    return x[max(0, idx[0] - int(0.03 * sr)): min(len(x), idx[-1] + int(0.06 * sr))]
sent = []; scene_start = []; pos = 0.10
for si, sc in enumerate(SCENES):
    scene_start.append(pos)
    for txt in sc["s"]:
        au = load_trim(len(sent)); sent.append(dict(text=txt, scene=si, start=pos, dur=len(au) / VSR, audio=au))
        pos += len(au) / VSR + 0.2
    pos += 0.25
TOTAL = sent[-1]["start"] + sent[-1]["dur"] + 1.2
words = []
for j, s in enumerate(sent):
    toks = s["text"].split()
    ws = [len(t.strip(",.:?!")) + 1 + (4 if t[-1] in ",.:?!" else 0) for t in toks]
    tot = sum(ws); cum = 0
    for t, w in zip(toks, ws):
        t0 = s["start"] + s["dur"] * cum / tot; cum += w
        words.append(dict(w=t, t0=t0, t1=s["start"] + s["dur"] * cum / tot, scene=s["scene"], sent=j))
voice = np.zeros(int(TOTAL * VSR) + VSR)
for s in sent:
    a = int(s["start"] * VSR); voice[a:a + len(s["audio"])] += s["audio"]
nfr = int(TOTAL * FPS) + 3; spf = VSR // FPS
rms = np.array([np.sqrt(np.mean(voice[i * spf:(i + 1) * spf] ** 2)) if (i + 1) * spf <= len(voice) else 0 for i in range(nfr)])
amp = np.convolve(np.clip(rms / np.percentile(rms[rms > 0.01], 90), 0, 1), [0.25, 0.5, 0.25], mode="same")
chunks = []
for j, s in enumerate(sent):
    cur = []
    for i in [i for i, x in enumerate(words) if x["sent"] == j]:
        cur.append(i)
        if len(cur) >= 3 or words[i]["w"][-1] in ",.:?!" or len(" ".join(words[q]["w"] for q in cur)) > 17:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
chunk_t = []
for ci, c in enumerate(chunks):
    j = words[c[0]]["sent"]
    nxt = words[chunks[ci + 1][0]]["t0"] if ci + 1 < len(chunks) and words[chunks[ci + 1][0]]["sent"] == j else sent[j]["start"] + sent[j]["dur"] + 0.1
    chunk_t.append((words[c[0]]["t0"], nxt))

def scene_at(t):
    idx = 0
    for i in range(len(SCENES)):
        if scene_start[i] - 0.1 <= t: idx = i
    return idx
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_c(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3
def lerpc(a, b, f): return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))
ACC = (255, 210, 90); WHITE = (255, 255, 255)

# ---------- pixel scenery ----------
def grad(d, y0, y1, c0, c1, x0=0, x1=PW):
    for y in range(y0, y1, 3):
        d.rectangle([x0, y, x1, y + 2], fill=lerpc(c0, c1, (y - y0) / max(1, y1 - y0)))
def ground(d, c, c2=None):
    d.rectangle([0, HZ, PW, PH], fill=c)
    rr = random.Random(3)
    for _ in range(90): d.point((rr.randrange(PW), rr.randrange(HZ + 2, PH)), fill=c2 or tuple(max(0, v - 18) for v in c))
def tree(d, x, y, h, leaf=(50, 130, 60), fruit=None, glow=False):
    if h < 3: return
    tw = max(2, h // 8)
    d.rectangle([x - tw // 2, y - h, x + tw // 2, y], fill=(96, 62, 38))
    r = max(4, int(h * 0.42)); cy = y - h
    for dx, dy, rr_, col in ((0, -r // 3, r, leaf), (-r // 2, 0, r * 0.75, tuple(max(0, v - 14) for v in leaf)), (r // 2, 0, r * 0.75, tuple(max(0, v - 14) for v in leaf)), (-r // 4, -r // 2, r * 0.5, tuple(min(255, v + 25) for v in leaf))):
        d.ellipse([x + dx - rr_, cy + dy - rr_, x + dx + rr_, cy + dy + rr_], fill=col)
    if fruit:
        for fx, fy in ((-r * 0.6, 0), (r * 0.5, -r * 0.2), (0, r * 0.3), (r * 0.2, -r * 0.7)):
            d.ellipse([x + fx - 2, cy + fy - 2, x + fx + 2, cy + fy + 2], fill=fruit)
def flower(d, x, y, col, h=6):
    d.line([(x, y), (x, y - h)], fill=(40, 120, 50)); d.rectangle([x - 1, y - h - 1, x + 1, y - h + 1], fill=col); d.point((x, y - h), fill=(255, 240, 150))
def bird(d, x, y, t, col=(40, 40, 60)):
    w = int(2 + 2 * math.sin(t * 9 + x))
    d.line([(x - 5, y - w), (x, y)], fill=col); d.line([(x, y), (x + 5, y - w)], fill=col); d.point((x, y - 1), fill=col)
def fish(d, x, y, flip, col=(255, 150, 60)):
    s = -1 if flip else 1
    d.ellipse([x - 5, y - 3, x + 5, y + 3], fill=col); d.polygon([(x - 5 * s, y), (x - 9 * s, y - 3), (x - 9 * s, y + 3)], fill=col); d.point((x + 3 * s, y - 1), fill=(20, 20, 30))
def sheep(d, x, y, t, f=1):
    d.ellipse([x - 7, y - 11, x + 7, y - 2], fill=(240, 240, 235)); d.ellipse([x + 5 * f - 3, y - 10, x + 5 * f + 3, y - 4], fill=(50, 50, 55))
    for lx in (-4, 3): d.line([(x + lx, y - 3), (x + lx, y + (1 if int(t * 3 + lx) % 2 else 0))], fill=(50, 50, 55))
def lion(d, x, y, t, f=1):
    d.ellipse([x - 9, y - 11, x + 7, y - 3], fill=(214, 160, 70)); d.ellipse([x + 6 * f - 5, y - 14, x + 6 * f + 5, y - 4], fill=(130, 80, 36)); d.ellipse([x + 6 * f - 3, y - 12, x + 6 * f + 3, y - 6], fill=(228, 180, 90))
    d.line([(x - 9 * f, y - 8), (x - 13 * f, y - 12 + int(math.sin(t * 4) * 2))], fill=(130, 80, 36))
    for lx in (-6, 4): d.line([(x + lx, y - 3), (x + lx, y + (1 if int(t * 3 + lx) % 2 else 0))], fill=(180, 130, 56))
def deer(d, x, y, t, f=1):
    d.ellipse([x - 8, y - 14, x + 6, y - 6], fill=(176, 120, 70)); d.line([(x + 5 * f, y - 11), (x + 8 * f, y - 19)], fill=(176, 120, 70), width=2)
    d.ellipse([min(x + 6 * f, x + 11 * f), y - 22, max(x + 6 * f, x + 11 * f), y - 17], fill=(190, 134, 82)); d.line([(x + 8 * f, y - 22), (x + 6 * f, y - 27)], fill=(110, 80, 50)); d.line([(x + 10 * f, y - 22), (x + 12 * f, y - 27)], fill=(110, 80, 50))
    for lx in (-6, 3): d.line([(x + lx, y - 6), (x + lx, y + 1 + (1 if int(t * 3 + lx) % 2 else 0))], fill=(150, 100, 60))
def serpent(d, x, y, t, n=14):
    for i in range(n):
        px = x + 3 * math.sin(i * 0.9 + t * 5) ; py = y - i * 3
        d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2], fill=(70, 150, 70) if i % 2 else (50, 120, 56))
    d.ellipse([x + 3 * math.sin(t * 5 + n * 0.9) - 3, y - n * 3 - 3, x + 3 * math.sin(t * 5 + n * 0.9) + 3, y - n * 3 + 3], fill=(80, 165, 80)); d.point((int(x + 3 * math.sin(t * 5 + n * 0.9) + 1), y - n * 3 - 1), fill=(230, 40, 40))
def sun(d, x, y, r, t):
    for a in range(0, 360, 30):
        aa = math.radians(a + t * 20); d.line([(x + (r + 2) * math.cos(aa), y + (r + 2) * math.sin(aa)), (x + (r + 7) * math.cos(aa), y + (r + 7) * math.sin(aa))], fill=(255, 220, 110))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 205, 90)); d.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], fill=(255, 235, 150))
def cloud(d, x, y, s=1.0, col=(250, 250, 255)):
    for dx, dy, r in ((0, 0, 7), (8, -2, 8), (17, 0, 6), (5, 3, 6), (13, 3, 6)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s * 0.7, x + dx * s + r * s, y + dy * s + r * s * 0.7], fill=col)
def person(base, name, x, y, t, scale=0.5, flip=False, glow=0.0):
    arr = chars.draw(name, t, 0.0, False, None)
    im = Image.fromarray(arr, "RGBA")
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.NEAREST)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    base.paste(im, (int(x - im.width / 2), int(y - im.height + 3)), im)
def sparkles(d, x, y, t, n=8, rad=14):
    for i in range(n):
        a = i * 2.4 + t * 3; r = rad * ((t * 1.4 + i * 0.13) % 1)
        px, py = x + r * math.cos(a), y - r * 0.8 * abs(math.sin(a)) - r * 0.3
        d.point((int(px), int(py)), fill=(255, 240, 160)); d.point((int(px) + 1, int(py)), fill=(255, 215, 110))
def waves(d, y0, y1, c, t):
    for y in range(y0, y1, 6):
        for x in range(0, PW, 2):
            if int(y + 3 * math.sin(x * 0.12 + t * 2 + y)) % 6 == 0: d.point((x, y), fill=c)

def ground_fill(d, c): ground(d, c)

# ---------- scene drawers ----------
def draw_scene(d, base, kind, o, t, lt):
    o = o or {}
    if kind == "void":
        grad(d, 0, HZ, (4, 5, 18), (14, 20, 54)); d.rectangle([0, HZ, PW, PH], fill=(10, 16, 46)); waves(d, HZ + 4, 300, (30, 44, 100), t)
        rr = random.Random(9)
        for i in range(30):
            if (int(t * 2) + i) % 6 == 0: d.point((rr.randrange(PW), rr.randrange(HZ)), fill=(80, 90, 150))
    elif kind == "light":
        grad(d, 0, HZ, (4, 5, 18), (14, 20, 54)); d.rectangle([0, HZ, PW, PH], fill=(10, 16, 46)); waves(d, HZ + 4, 300, (30, 44, 100), t)
        r = ease(lt / 1.4) * 150
        for i in range(12, 0, -1):
            f = i / 12; d.ellipse([90 - r * f, 118 - r * f, 90 + r * f, 118 + r * f], fill=lerpc((255, 250, 225), (60, 80, 150), f ** 1.4) if r > 3 else None)
        for a in range(0, 360, 20):
            aa = math.radians(a + t * 8); d.line([(90, 118), (90 + 200 * math.cos(aa), 118 + 200 * math.sin(aa))], fill=(255, 245, 190))
        d.ellipse([90 - r * 0.2, 118 - r * 0.2, 90 + r * 0.2, 118 + r * 0.2], fill=(255, 255, 245))
    elif kind == "sky":
        grad(d, 0, HZ, (70, 120, 200), (170, 210, 245)); grad(d, 0, 22, (60, 70, 120), (100, 120, 170)); d.rectangle([0, HZ, PW, PH], fill=(36, 84, 160)); waves(d, HZ + 4, 300, (80, 140, 220), t)
        for i in range(4): cloud(d, ((t * 8 + i * 55) % 230) - 30, 70 + (i % 2) * 28, 1 + 0.25 * (i % 3))
        d.line([(0, 22), (PW, 22)], fill=(130, 160, 210))
    elif kind == "land":
        grad(d, 0, HZ, (120, 190, 240), (210, 232, 245)); ground(d, (76, 150, 70)); d.ellipse([-20, 150, 70, 180], fill=(40, 110, 190)); waves(d, 154, 176, (110, 170, 240), t)
        g_ = ease(lt / 3.0)
        for (x, y, h, c) in ((92, 165, 40, (50, 130, 60)), (132, 163, 52, (60, 145, 66)), (165, 166, 34, (46, 120, 56))): tree(d, x, y, int(h * g_), c)
        for i, x in enumerate((84, 105, 120, 145, 155, 172)): flower(d, x, 170 + (i % 2) * 4, ((240, 90, 120), (255, 220, 90), (200, 120, 230))[i % 3], int(7 * ease((lt - 0.6) / 2)))
    elif kind == "sunmoon":
        grad(d, 0, HZ, (6, 14, 50), (60, 100, 160)); ground(d, (44, 100, 60))
        rr = random.Random(4)
        for i in range(36):
            if (int(t * 2) + i) % 5: d.point((rr.randrange(PW), rr.randrange(HZ - 20)), fill=(230, 235, 255))
        sun(d, 46, 96, 12, t); d.ellipse([122, 80, 148, 106], fill=(240, 240, 220)); d.ellipse([130, 76, 156, 102], fill=(26, 56, 110))
    elif kind == "fishbirds":
        grad(d, 0, HZ, (100, 170, 240), (200, 228, 248)); ground(d, (36, 92, 170)); waves(d, HZ + 4, 300, (90, 150, 230), t)
        d.rectangle([0, 135, PW, HZ + 2], fill=(44, 110, 190)); waves(d, 135, HZ, (120, 180, 240), t)
        for i in range(6): bird(d, ((t * 26 + i * 40) % 230) - 25, 88 + 10 * math.sin(t * 1.5 + i) + (i % 3) * 8, t)
        for i in range(4):
            ph = (t * 0.7 + i * 0.27) % 1; x = 30 + i * 38 + int(12 * ph); y = 140 - 28 * 4 * ph * (1 - ph)
            fish(d, x, int(y), False, ((255, 150, 60), (120, 200, 255), (255, 210, 90), (200, 120, 230))[i])
    elif kind == "animals":
        grad(d, 0, HZ, (130, 200, 245), (215, 236, 246)); ground(d, (84, 156, 72))
        lion(d, 26 + int(2 * math.sin(t)), 168, t); sheep(d, 56, 170, t); sheep(d, 76, 166, t + 1); deer(d, 100, 168, t)
        if lt > 2.2:
            person(base, "Adam", 124, 176, t, 0.5); person(base, "Eve", 152, 177, t, 0.5); sparkles(d, 138, 150, lt - 2.2, 10, 18)
        for x in (10, 172): tree(d, x, 160, 30, (56, 140, 64))
    elif kind == "rest":
        grad(d, 0, HZ, (80, 60, 130), (250, 190, 110)); ground(d, (110, 110, 80), (96, 94, 70))
        r = 26
        for i in range(10, 0, -1): d.ellipse([90 - r * i / 5 * 1.2, HZ - r * i / 5 * 1.2, 90 + r * i / 5 * 1.2, HZ + r * i / 5 * 1.2], fill=lerpc((255, 240, 190), (250, 190, 110), i / 10))
        for a in range(200, 341, 10):
            aa = math.radians(a + math.sin(t) * 2); d.line([(90, HZ), (90 + 180 * math.cos(aa), HZ + 180 * math.sin(aa))], fill=(255, 215, 130))
        for x, h in ((20, 36), (50, 28), (140, 32), (166, 40)): tree(d, x, 166, h, (40, 70, 60))
    elif kind in ("outro", "outro2"):
        grad(d, 0, HZ, (8, 8, 34), (50, 40, 100)); ground(d, (44, 40, 80))
        rr = random.Random(11)
        for i in range(60):
            if (int(t * 2) + i) % 5: d.point((rr.randrange(PW), rr.randrange(HZ)), fill=(230, 235, 255))
        pr = 8 + int(1.2 * math.sin(t * 2.2)); d.polygon([(135, 90 - pr), (139, 86), (135 + pr, 90), (139, 94), (135, 90 + pr), (131, 94), (135 - pr, 90), (131, 86)], fill=(255, 225, 140))
    elif kind == "eden":
        grad(d, 0, HZ, (120, 200, 230), (210, 240, 235)); ground(d, (70, 160, 80), (56, 138, 66))
        rr = random.Random(21)
        for x, h in ((12, 52), (40, 40), (150, 56), (172, 40), (118, 34)): tree(d, x, 162, h, (46, 140, 70))
        for i in range(16): flower(d, rr.randrange(4, 176), rr.randrange(168, 178), ((240, 90, 120), (255, 220, 90), (200, 130, 240), (255, 255, 255))[i % 4], 5)
        # river
        for x in range(0, PW, 2): d.line([(x, 172 + int(3 * math.sin(x * 0.08 + t))), (x, 176 + int(3 * math.sin(x * 0.08 + t)))], fill=(90, 170, 230))
        if o.get("tree"):
            tree(d, 90, 166, 66, (36, 120, 60), fruit=(220, 50, 60))
            if o.get("pair") or lt < 99:
                gl = 1 + 0.5 * math.sin(t * 4)
                if o.get("pair"): d.ellipse([90 - 3 * gl, 100, 90 + 3 * gl, 104], fill=(255, 240, 160))
        if o.get("snake"): serpent(d, 90, 160, t)
        if o.get("naming"):
            an = (lion, sheep, deer)
            for i, fn in enumerate(an):
                ph = ((lt - 0.2 - i * 1.0) / 1.2)
                if 0 <= ph <= 1: fn(d, int(170 - 120 * ph), 170, t, -1)
        # humans
        if "adam" in o and lt >= o["adam"]:
            a_t = lt - o["adam"]
            xa = 60 if not o.get("pair") else 56
            if o.get("naming"): xa = 52
            if a_t < 0.8: sparkles(d, xa, 150, a_t, 12, 22)
            if a_t > 0.3: person(base, "Adam", xa, 176, t, 0.5)
        if "eve" in o and lt >= o["eve"]:
            e_t = lt - o["eve"]
            xe = 124 if o.get("pair") else 80
            if e_t < 0.8: sparkles(d, xe, 150, e_t, 12, 22)
            if e_t > 0.3: person(base, "Eve", xe, 177, t, 0.5, flip=True)
        if o.get("naming") and lt < o.get("eve", 99) and False: pass
    elif kind == "fruits":
        grad(d, 0, HZ, (40, 90, 130), (150, 200, 200)); ground(d, (60, 130, 70))
        tree(d, 90, 168, 66, (36, 120, 60), fruit=(220, 50, 60))
        cols = [(220, 40, 50), (120, 60, 160), (245, 150, 40), (130, 200, 60)]
        i = int(lt / 0.8) % 4; r = 11
        cx, cy = 90, 112 + int(2 * math.sin(t * 4))
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 245, 200)); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cols[i]); d.line([(cx, cy - r), (cx + 2, cy - r - 4)], fill=(70, 50, 30))
        d.rectangle([cx - 4, cy - 6, cx - 2, cy - 4], fill=tuple(min(255, v + 70) for v in cols[i]))
    elif kind == "gate":
        grad(d, 0, HZ, (50, 40, 100), (240, 160, 110)); ground(d, (110, 90, 70), (96, 78, 60))
        for i in range(8, 0, -1): d.ellipse([34 - i * 5, 130 - i * 6, 34 + i * 5, 130 + i * 6], fill=lerpc((255, 230, 150), (150, 100, 120), i / 8))
        d.rectangle([14, 110, 22, 166], fill=(210, 170, 70)); d.rectangle([46, 110, 54, 166], fill=(210, 170, 70)); d.pieslice([14, 96, 54, 126], 180, 360, fill=(210, 170, 70)); d.pieslice([20, 102, 48, 126], 180, 360, fill=(255, 235, 170))
        d.rectangle([22, 118, 46, 166], fill=(255, 235, 170))
        for x, h in ((100, 22), (160, 30)): tree(d, x, 164, h, (90, 110, 60))
        px = 70 + 30 * ease(lt / 5.0)
        person(base, "Adam", px + 14, 176, t, 0.5); person(base, "Eve", px - 8, 177, t, 0.5)

def draw_text(d, t):
    si = scene_at(t); sc = SCENES[si]; lt = t - scene_start[si]
    out = 1.0
    if si + 1 < len(SCENES): out = min(1, max(0, ((scene_start[si + 1] - 0.1) - t) / 0.2))
    def T(txt, y, size, color, a):
        if a <= 0: return
        f = ImageFont.truetype(BOLD, size)
        while d.textlength(txt, font=f) > (W - 90) and size > 20:
            size -= 4; f = ImageFont.truetype(BOLD, size)
        tw = d.textlength(txt, font=f); x = (W - tw) / 2; yy = y + (1 - a) * 30
        d.text((x + 5, yy + 5), txt, font=f, fill=(10, 10, 30)); d.text((x, yy), txt, font=f, fill=color if a >= 1 else lerpc((10, 10, 30), color, a))
    pop = 1 + 0.25 * (1 - ease(lt / 0.35))
    T(sc["t"][0], 130, 84, WHITE, ease(lt / 0.3) * out)
    T(sc["t"][1], 235, int(120 * pop), ACC, ease((lt - 0.15) / 0.3) * out)

def draw_caption(d, t):
    si = scene_at(t)
    if si == 0: return
    for ci, (a, b) in enumerate(chunk_t):
        if a - 0.02 <= t < b:
            c = chunks[ci]; f = ImageFont.truetype(BOLD, 76)
            sp = d.textlength(" ", font=f); ws = [words[i]["w"] for i in c]; widths = [d.textlength(w, font=f) for w in ws]
            x = (W - (sum(widths) + sp * (len(ws) - 1))) / 2; y = 1030
            for i, w, wd in zip(c, ws, widths):
                col = ACC if (words[i]["t0"] <= t < words[i]["t1"]) else (WHITE if words[i]["t0"] <= t else (150, 150, 190))
                d.text((x + 5, y + 5), w, font=f, fill=(8, 6, 24)); d.text((x, y), w, font=f, fill=col); x += wd + sp
            break

SPRITES = {}
def pose_L(t):
    j = 0
    for i, st in enumerate(sent):
        if st["start"] - 0.15 <= t: j = i
    pj = max(j - 1, 0); b = ease_c((t - (sent[j]["start"] - 0.15)) / 0.3)
    P = [20, 150, 95, 135, 60, 125, 30, 150]
    ang = lambda i: P[i % 8] + 12 * math.sin(t * 4.5 + i) + 6 * math.sin(t * 9)
    return (ang(pj) * (1 - b) + ang(j) * b, 14 * math.sin(t * 3.2))

def frame(t):
    si = scene_at(t); sc = SCENES[si]; lt = t - scene_start[si]
    base = Image.new("RGB", (PW, PH)); d = ImageDraw.Draw(base)
    draw_scene(d, base, sc["draw"], sc.get("o"), t, lt)
    d = ImageDraw.Draw(base)
    fi = min(int(t * FPS), nfr - 1)
    walk = 1 - ease(t / 1.3)
    cx_ = 40 - int(95 * walk) + int(round(3 * math.sin(t * 1.4)))
    bob = int(round(1.6 * abs(math.sin(t * (9 if walk > 0.02 else 3.2)))))
    hop = 0
    for st in sent:
        if 0 <= t - st["start"] < 0.25: hop = max(hop, int(round(3 * math.sin(math.pi * (t - st["start"]) / 0.25))))
    spr = Image.fromarray(chars.draw("Moses", t, float(amp[fi]), (t % 3.3) < 0.12, pose_L(t)), "RGBA")
    base.paste(spr, (cx_, 180 - bob - hop), spr)
    big = base.resize((W, H), Image.NEAREST)
    d2 = ImageDraw.Draw(big)
    draw_text(d2, t); draw_caption(d2, t)
    return big

def build_audio():
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr
    mix = np.interp(np.arange(n) / sr * VSR, np.arange(len(voice)), voice)
    pad = sum(np.sin(2 * np.pi * f * tt + p) for f, p in ((98, 0), (146.83, 1), (196, 2), (246.94, 3)))
    mix += pad * 0.010 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * tt))
    notes = [392, 440, 494, 523, 587, 659, 698, 784, 880, 988]
    for i, st in enumerate(scene_start):
        a = int(st * sr); m = int(0.12 * sr); x = np.arange(m) / sr
        mix[a:a + m] += np.sin(2 * np.pi * notes[i % 10] * x) * np.exp(-x * 24) * 0.07
    return np.clip(mix, -1, 1), sr

def render():
    out = f"{OUTD}/part{PART}"
    n = int(TOTAL * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", f"fade=t=in:d=0.3,fade=t=out:st={TOTAL-0.8:.2f}:d=0.8", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"{out}.v.tmp.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    mix, sr = build_audio(); sf.write(f"{out}.wav", mix, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}.v.tmp.mp4", "-i", f"{out}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}.tmp.mp4"], check=True)
    os.replace(f"{out}.tmp.mp4", f"{out}.mp4")

if MODE == "preview":
    os.makedirs(f"{OUTD}/prev", exist_ok=True)
    cols = 5; rows = (len(SCENES) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 270, rows * 480))
    for i in range(len(SCENES)):
        t = scene_start[i] + min(3.0, sent[[j for j, s in enumerate(sent) if s["scene"] == i][-1]]["dur"] * 0.8)
        sh.paste(frame(t).resize((270, 480)), ((i % cols) * 270, (i // cols) * 480))
    sh.save(f"{OUTD}/prev/sheet.png"); print("starts", [round(x, 1) for x in scene_start], "total", round(TOTAL, 1))
elif MODE == "full":
    render(); print("done", round(TOTAL, 1))
