import sys, math, os, subprocess, random
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = sys.argv[1]; PART = int(sys.argv[2]); MODE = sys.argv[3]
sys.path.insert(0, f"{S}/px")
import chars
import eden_sprites as es
W, H, FPS = 1080, 1920, 30
PW, PH = 180, 320
HZ = 165
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VSR = 24000
OUTD = f"{S}/g3_{PART}"; os.makedirs(OUTD, exist_ok=True)

P1 = [
 dict(t=("THE VERY", "BEGINNING?"), draw="void", text="What does the Bible say about the very beginning?"),
 dict(t=("GENESIS 1", "DARK + EMPTY"), draw="void", text="In the beginning, God created the heavens and the earth. It was dark and empty."),
 dict(t=("DAY 1", "LIGHT"), draw="light", text="On day one, God said, let there be light, and there was light."),
 dict(t=("DAY 2", "SKY"), draw="sky", text="On day two, God made the sky, and separated the waters above from the waters below."),
 dict(t=("DAY 3", "LAND + PLANTS"), draw="land", text="On day three, dry land appeared. Then the land filled with plants and trees."),
 dict(t=("DAY 4", "SUN, MOON, STARS"), draw="sunmoon", text="On day four, God made the sun, the moon, and the stars."),
 dict(t=("DAY 5", "FISH + BIRDS"), draw="fishbirds", text="On day five, the seas filled with fish, and the sky with birds."),
 dict(t=("DAY 6", "ANIMALS + PEOPLE"), draw="animals", text="On day six, God made the animals of the land. And finally, people, made in God's image."),
 dict(t=("DAY 7", "REST"), draw="rest", text="On day seven, God rested. That is where the idea of the Sabbath comes from."),
 dict(t=("PART 2", "EDEN"), draw="outro", text="Next, the Garden of Eden. Follow for part two."),
]
P2 = [
 dict(t=("THE FORBIDDEN", "FRUIT?"), draw="eden", o=dict(tree="fruit"), text="Was the forbidden fruit really an apple? The answer might surprise you."),
 dict(t=("ADAM", "IN EDEN"), draw="eden", o=dict(adam=0.8), text="After creation, God placed the first man, Adam, in a garden called Eden."),
 dict(t=("NAMING", "+ EVE"), draw="eden", o=dict(adam=0, naming=True, eve=4.2), text="Adam gave names to the animals. But none was a true partner for him, so God made Eve."),
 dict(t=("THE ONE", "RULE"), draw="eden", o=dict(adam=0, eve=0, tree="fruit", pair=True), text="God told them they could eat from any tree in the garden, except one: the tree of the knowledge of good and evil."),
 dict(t=("THE", "SERPENT"), draw="eden", o=dict(adam=0, eve=0, tree="fruit", snake=True, pair=True), text="Then a serpent told Eve she would not die if she ate its fruit. She ate, and Adam ate too."),
 dict(t=("JUST", "FRUIT"), draw="fruits", text="And here is the surprise. The Bible never says it was an apple. It only says fruit."),
 dict(t=("LEAVING", "EDEN"), draw="gate", text="Afterward, they hid, and had to leave the garden. But before they left, God made clothes for them."),
 dict(t=("GENESIS", "THE BEGINNING"), draw="outro2", text="That is the story of Eden, from Genesis. Follow for more Bible explained."),
]
SCENES = P1 if PART == 1 else P2

if MODE == "tts":
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
    for i, sc in enumerate(SCENES):
        x, sr = k.create(sc["text"], voice="am_michael", speed=1.0, lang="en-us", sentence_pause=0.28, clause_pause=0.14)
        sf.write(f"{OUTD}/s{i}.wav", x, sr); print(i, round(len(x) / sr, 2))
    sys.exit()

# ---------- voice FX ----------
from pedalboard import Pedalboard, HighpassFilter, LowShelfFilter, PeakFilter, Compressor, Reverb, Limiter, LowpassFilter, Gain
def voice_fx(x, sr):
    pb = Pedalboard([HighpassFilter(75), LowShelfFilter(200, 2.5), PeakFilter(3200, 1.8, 0.9), PeakFilter(7500, -2.0, 1.0),
                     Compressor(threshold_db=-21, ratio=3.0, attack_ms=8, release_ms=140), Reverb(room_size=0.22, damping=0.55, wet_level=0.11, dry_level=0.92, width=0.8), Limiter(-1.0)])
    return pb(x.astype(np.float32).reshape(1, -1), sr).reshape(-1)

def load_scene(i):
    x, sr = sf.read(f"{OUTD}/s{i}.wav")
    x = x / np.abs(x).max() * 0.85
    idx = np.where(np.abs(x) > 0.015)[0]
    x = x[max(0, idx[0] - int(0.04 * sr)): min(len(x), idx[-1] + int(0.10 * sr))]
    x = voice_fx(np.concatenate([x, np.zeros(int(0.5 * sr))]), sr)
    return x[:len(x) - int(0.3 * sr)]

aud = []; scene_start = []; scene_dur = []; pos = 0.15
for i, sc in enumerate(SCENES):
    au = load_scene(i); aud.append(au)
    scene_start.append(pos); scene_dur.append(len(au) / VSR)
    pos += len(au) / VSR + 0.3
TOTAL = scene_start[-1] + scene_dur[-1] + 1.3

voice = np.zeros(int(TOTAL * VSR) + VSR)
for st, au in zip(scene_start, aud):
    a = int(st * VSR); voice[a:a + len(au)] += au

# word timing from speech mask
words = []; beats = []
for si, sc in enumerate(SCENES):
    au = aud[si]; win = int(0.01 * VSR); n = len(au) // win
    env = np.array([np.sqrt(np.mean(au[i * win:(i + 1) * win] ** 2)) for i in range(n)])
    sp = env > max(0.012, env.max() * 0.06)
    cum = np.concatenate([[0], np.cumsum(sp)]) / 100.0
    tot_sp = cum[-1]
    toks = sc["text"].split()
    ws = [len(t.strip(",.:?!")) + 1.2 for t in toks]
    totw = sum(ws); c = 0
    def t_of(speech_t):
        j = int(np.searchsorted(cum, speech_t)); return min(j, n) * 0.01
    for ti, (tk, w) in enumerate(zip(toks, ws)):
        a = t_of(tot_sp * c / totw); c += w; b = t_of(tot_sp * c / totw)
        words.append(dict(w=tk, t0=scene_start[si] + a, t1=scene_start[si] + b, scene=si, idx=ti))
        if ti == 0 or toks[ti - 1][-1] in ".?!:": beats.append(scene_start[si] + a)
nfr = int(TOTAL * FPS) + 3; spf = VSR // FPS
rms = np.array([np.sqrt(np.mean(voice[i * spf:(i + 1) * spf] ** 2)) if (i + 1) * spf <= len(voice) else 0 for i in range(nfr)])
amp = np.convolve(np.clip(rms / np.percentile(rms[rms > 0.01], 90), 0, 1), [0.25, 0.5, 0.25], mode="same")
chunks = []
for si in range(len(SCENES)):
    cur = []
    for i in [i for i, x in enumerate(words) if x["scene"] == si]:
        cur.append(i)
        if len(cur) >= 3 or words[i]["w"][-1] in ",.:?!" or len(" ".join(words[q]["w"] for q in cur)) > 16:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
chunk_t = []
for ci, c in enumerate(chunks):
    nxt = words[chunks[ci + 1][0]]["t0"] if ci + 1 < len(chunks) and words[chunks[ci + 1][0]]["scene"] == words[c[0]]["scene"] else words[c[-1]]["t1"] + 0.15
    chunk_t.append((words[c[0]]["t0"], max(nxt, words[c[-1]]["t1"] + 0.05) if words[c[-1]]["w"][-1] not in ".?!" else words[c[-1]]["t1"] + 0.25))

def scene_at(t):
    idx = 0
    for i in range(len(SCENES)):
        if scene_start[i] - 0.15 <= t: idx = i
    return idx
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_c(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3
def lerpc(a, b, f): return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))
ACC = (255, 210, 90); WHITE = (255, 255, 255)

# ---------- scaled draw wrapper ----------
class SD:
    def __init__(s, d, ax, ay, k): s.d, s.ax, s.ay, s.k = d, ax, ay, k
    def m(s, p): return (s.ax + (p[0] - s.ax) * s.k, s.ay + (p[1] - s.ay) * s.k)
    def ellipse(s, xy, fill=None):
        a = s.m((xy[0], xy[1])); b = s.m((xy[2], xy[3])); s.d.ellipse([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=fill)
    def rectangle(s, xy, fill=None):
        a = s.m((xy[0], xy[1])); b = s.m((xy[2], xy[3])); s.d.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=fill)
    def line(s, pts, fill=None, width=1): s.d.line([s.m(p) for p in pts], fill=fill, width=max(1, int(round(width * s.k))))
    def polygon(s, pts, fill=None): s.d.polygon([s.m(p) for p in pts], fill=fill)
    def point(s, xy, fill=None):
        a = s.m(xy); s.d.rectangle([a[0], a[1], a[0] + max(0, s.k - 1), a[1] + max(0, s.k - 1)], fill=fill)

# ---------- pixel scenery ----------
def grad(d, y0, y1, c0, c1):
    for y in range(y0, y1, 2): d.rectangle([0, y, PW, y + 1], fill=lerpc(c0, c1, (y - y0) / max(1, y1 - y0)))
def ground(d, c, c2=None):
    d.rectangle([0, HZ, PW, PH], fill=c)
    rr = random.Random(3)
    for _ in range(110): d.point((rr.randrange(PW), rr.randrange(HZ + 2, PH)), fill=c2 or tuple(max(0, v - 18) for v in c))
def hills(d, base, col, amp, drift, t, seed=0):
    for x in range(PW):
        y = base - amp * (0.6 + 0.4 * math.sin((x + drift * t) * 0.03 + seed)) - amp * 0.5 * math.sin((x + drift * t) * 0.011 + seed * 2)
        d.line([(x, int(y)), (x, HZ + 1)], fill=col)
def tree(d, x, y, h, leaf=(50, 130, 60), fruit=None, sway=0.0, t=0):
    if h < 3: return
    tw = max(2, h // 8)
    d.rectangle([x - tw // 2, y - h, x + tw // 2, y], fill=(96, 62, 38)); d.line([(x - tw // 2, y - h), (x - tw // 2, y)], fill=(130, 90, 56))
    r = max(4, int(h * 0.42)); cy = y - h; sw = int(round(math.sin(t * 1.3 + x) * sway))
    dk = tuple(max(0, v - 16) for v in leaf); lt_ = tuple(min(255, v + 28) for v in leaf)
    for dx, dy, rr_, col in ((0, -r // 3, r, leaf), (-r // 2, 0, r * 0.75, dk), (r // 2, 0, r * 0.75, dk), (-r // 4, -r // 2, r * 0.5, lt_)):
        d.ellipse([x + dx + sw - rr_, cy + dy - rr_, x + dx + sw + rr_, cy + dy + rr_], fill=col)
    if fruit:
        for fx, fy in ((-r * 0.6, 0), (r * 0.5, -r * 0.2), (0, r * 0.3), (r * 0.2, -r * 0.7), (-r * 0.3, -r * 0.5)):
            d.ellipse([x + fx + sw - 2, cy + fy - 2, x + fx + sw + 2, cy + fy + 2], fill=fruit); d.point((int(x + fx + sw - 1), int(cy + fy - 1)), fill=(255, 170, 170))
def flower(d, x, y, col, h=6, t=0):
    sw = int(round(math.sin(t * 2 + x) * 1))
    d.line([(x, y), (x + sw, y - h)], fill=(40, 120, 50)); d.rectangle([x + sw - 1, y - h - 1, x + sw + 1, y - h + 1], fill=col); d.point((x + sw, y - h), fill=(255, 240, 150))
def bird(d, x, y, t, col=(40, 40, 60), s=1):
    w = int((2 + 2.5 * math.sin(t * 9 + x)) * s)
    d.line([(x - 5 * s, y - w), (x, y)], fill=col, width=max(1, int(s))); d.line([(x, y), (x + 5 * s, y - w)], fill=col, width=max(1, int(s)))
def fish(d, x, y, flip, col=(255, 150, 60), s=1):
    k = -1 if flip else 1; sd = SD(d, x, y, s)
    sd.ellipse([x - 5, y - 3, x + 5, y + 3], fill=col); sd.polygon([(x - 5 * k, y), (x - 9 * k, y - 3), (x - 9 * k, y + 3)], fill=col); sd.point((x + 3 * k, y - 1), fill=(20, 20, 30))
def sheep(d, x, y, t, f=1):
    d.ellipse([x - 7, y - 11, x + 7, y - 2], fill=(240, 240, 235)); d.ellipse([x - 6, y - 12, x, y - 6], fill=(250, 250, 245)); d.ellipse([x + 5 * f - 3, y - 10, x + 5 * f + 3, y - 4], fill=(50, 50, 55))
    for lx in (-4, 3): d.line([(x + lx, y - 3), (x + lx, y + (1 if int(t * 3 + lx) % 2 else 0))], fill=(50, 50, 55))
def lion(d, x, y, t, f=1):
    d.ellipse([x - 9, y - 11, x + 7, y - 3], fill=(214, 160, 70)); d.ellipse([x + 6 * f - 5, y - 14, x + 6 * f + 5, y - 4], fill=(130, 80, 36)); d.ellipse([x + 6 * f - 3, y - 12, x + 6 * f + 3, y - 6], fill=(228, 180, 90))
    d.line([(x - 9 * f, y - 8), (x - 13 * f, y - 12 + int(math.sin(t * 4) * 2))], fill=(130, 80, 36))
    for lx in (-6, 4): d.line([(x + lx, y - 3), (x + lx, y + (1 if int(t * 3 + lx) % 2 else 0))], fill=(180, 130, 56))
def deer(d, x, y, t, f=1):
    d.ellipse([x - 8, y - 14, x + 6, y - 6], fill=(176, 120, 70)); d.line([(x + 5 * f, y - 11), (x + 8 * f, y - 19)], fill=(176, 120, 70), width=2)
    d.ellipse([x + 6 * f, y - 22, x + 11 * f, y - 17], fill=(190, 134, 82)); d.line([(x + 8 * f, y - 22), (x + 6 * f, y - 27)], fill=(110, 80, 50)); d.line([(x + 10 * f, y - 22), (x + 12 * f, y - 27)], fill=(110, 80, 50))
    for lx in (-6, 3): d.line([(x + lx, y - 6), (x + lx, y + 1 + (1 if int(t * 3 + lx) % 2 else 0))], fill=(150, 100, 60))
def butterfly(d, x, y, t, col):
    w = int(1 + 2 * abs(math.sin(t * 12 + x)))
    d.ellipse([x - w - 1, y - 2, x, y + 1], fill=col); d.ellipse([x, y - 2, x + w + 1, y + 1], fill=col)
def serpent(d, x, y, t, n=14):
    for i in range(n):
        px = x + 3 * math.sin(i * 0.9 + t * 5); py = y - i * 3
        d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2], fill=(70, 150, 70) if i % 2 else (50, 120, 56))
    hx = x + 3 * math.sin(t * 5 + n * 0.9)
    d.ellipse([hx - 3, y - n * 3 - 3, hx + 3, y - n * 3 + 3], fill=(80, 165, 80)); d.point((int(hx + 1), y - n * 3 - 1), fill=(230, 40, 40))
def sun(d, x, y, r, t):
    for a in range(0, 360, 30):
        aa = math.radians(a + t * 20); d.line([(x + (r + 2) * math.cos(aa), y + (r + 2) * math.sin(aa)), (x + (r + 7 + 2 * math.sin(t * 3 + a)) * math.cos(aa), y + (r + 7 + 2 * math.sin(t * 3 + a)) * math.sin(aa))], fill=(255, 220, 110))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 205, 90)); d.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], fill=(255, 235, 150))
def cloud(d, x, y, s=1.0, col=(250, 250, 255)):
    for dx, dy, r in ((0, 0, 7), (8, -2, 8), (17, 0, 6), (5, 3, 6), (13, 3, 6)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s * 0.7, x + dx * s + r * s, y + dy * s + r * s * 0.7], fill=col)
def person(base, name, x, y, t, scale=0.5, flip=False):
    im = Image.fromarray(chars.draw(name, t, 0.0, False, None), "RGBA")
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.NEAREST)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    base.paste(im, (int(x - im.width / 2), int(y - im.height + 3)), im)
_AC = {}
def actor(base, name, x, y, t, scale=0.6, flip=False, walk=0.0):
    key = (name, int(t * 10) % 40, walk > 0, flip, scale)
    if key not in _AC:
        arr = es.SP[name](int(t * 10) / 10.0, walk)
        im = Image.fromarray(arr, "RGBA"); im = im.resize((int(im.width * scale), int(im.height * scale)), Image.NEAREST)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        _AC[key] = im
    im = _AC[key]
    base.paste(im, (int(x - im.width / 2), int(y - 110 * scale)), im)
def sparkles(d, x, y, t, n=8, rad=14):
    for i in range(n):
        a = i * 2.4 + t * 3; r = rad * ((t * 1.4 + i * 0.13) % 1)
        px, py = x + r * math.cos(a), y - r * 0.8 * abs(math.sin(a)) - r * 0.3
        d.point((int(px), int(py)), fill=(255, 240, 160)); d.point((int(px) + 1, int(py)), fill=(255, 215, 110))
def waves(d, y0, y1, c, t):
    for y in range(y0, y1, 6):
        for x in range(0, PW, 2):
            if int(y + 3 * math.sin(x * 0.12 + t * 2 + y)) % 6 == 0: d.point((x, y), fill=c)
def motes(d, t, n=22, col=(255, 240, 170), y0=20, y1=300):
    rr = random.Random(77)
    for i in range(n):
        x = rr.uniform(0, PW) + 6 * math.sin(t * 0.8 + i); y = y1 - ((t * (6 + i % 5) + rr.uniform(0, y1 - y0)) % (y1 - y0))
        if int(t * 3 + i) % 4: d.point((int(x), int(y)), fill=col)
def shafts(base, t, a=34, x0=40, n=4):
    ov = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(n):
        sx = x0 + i * 38 + 6 * math.sin(t * 0.6 + i)
        od.polygon([(sx, 0), (sx + 14, 0), (sx + 50 + i * 6, HZ + 10), (sx + 18, HZ + 10)], fill=(255, 245, 200, a))
    base.paste(ov, (0, 0), ov)
def ripple(d, x, y, ph):
    r = 2 + ph * 9
    d.ellipse([x - r, y - r * 0.35, x + r, y + r * 0.35], outline=(200, 230, 255))

def draw_scene(d, base, kind, o, t, lt):
    o = o or {}
    if kind == "void":
        grad(d, 0, HZ, (4, 5, 18), (16, 22, 60)); d.rectangle([0, HZ, PW, PH], fill=(10, 16, 46)); waves(d, HZ + 4, 300, (34, 50, 110), t)
        rr = random.Random(9)
        for i in range(34):
            if (int(t * 2) + i) % 6 == 0: d.point((rr.randrange(PW), rr.randrange(HZ)), fill=(90, 100, 160))
        glow = 0.5 + 0.5 * math.sin(t * 0.8)
        for r_ in range(30, 0, -3): d.ellipse([90 - r_ * 2, 120 - r_, 90 + r_ * 2, 120 + r_], fill=lerpc((16, 22, 60), (30, 40, 100), (1 - r_ / 30) * glow))
        motes(d, t, 14, (110, 130, 200))
    elif kind == "light":
        grad(d, 0, HZ, (4, 5, 18), (14, 20, 54)); d.rectangle([0, HZ, PW, PH], fill=(10, 16, 46)); waves(d, HZ + 4, 300, (30, 44, 100), t)
        r = ease(lt / 1.6) * 150
        if r > 3:
            for i in range(12, 0, -1):
                f = i / 12; d.ellipse([90 - r * f, 118 - r * f, 90 + r * f, 118 + r * f], fill=lerpc((255, 250, 225), (60, 80, 150), f ** 1.4))
        for a in range(0, 360, 20):
            aa = math.radians(a + t * 8); d.line([(90, 118), (90 + 200 * math.cos(aa), 118 + 200 * math.sin(aa))], fill=(255, 245, 190))
        d.ellipse([90 - r * 0.2, 118 - r * 0.2, 90 + r * 0.2, 118 + r * 0.2], fill=(255, 255, 245))
        motes(d, t, 26, (255, 250, 210))
    elif kind == "sky":
        grad(d, 0, HZ, (70, 120, 200), (170, 210, 245)); grad(d, 0, 24, (60, 70, 120), (100, 120, 170)); d.rectangle([0, HZ, PW, PH], fill=(36, 84, 160)); waves(d, HZ + 4, 300, (80, 140, 220), t)
        d.line([(0, 24), (PW, 24)], fill=(130, 160, 210))
        for i in range(5): cloud(d, ((t * (6 + i * 2) + i * 55) % 240) - 35, 66 + (i % 3) * 22, 1.1 + 0.3 * (i % 3), (250, 250, 255) if i % 2 else (232, 240, 252))
        motes(d, t, 10, (255, 255, 255))
    elif kind == "land":
        grad(d, 0, HZ, (120, 190, 240), (210, 232, 245)); hills(d, 150, (150, 190, 170), 14, 2, t, 1)
        for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 70 + i * 14, 1.0)
        ground(d, (76, 150, 70)); d.ellipse([-30, 150, 74, 184], fill=(40, 110, 190)); waves(d, 154, 178, (110, 170, 240), t)
        g_ = ease(lt / 3.2)
        for (x, y, h, c) in ((92, 165, 46, (50, 130, 60)), (132, 163, 62, (60, 145, 66)), (167, 166, 40, (46, 120, 56)), (108, 170, 30, (70, 156, 72))): tree(d, x, y, int(h * g_), c, sway=1.2, t=t)
        for i, x in enumerate((84, 105, 120, 145, 155, 172, 100, 130)): flower(d, x, 172 + (i % 3) * 4, ((240, 90, 120), (255, 220, 90), (200, 120, 230))[i % 3], int(8 * ease((lt - 0.8) / 2.4)), t)
        motes(d, t, 12, (255, 250, 200), 100, 300)
    elif kind == "sunmoon":
        grad(d, 0, HZ, (6, 14, 50), (60, 100, 160)); hills(d, 152, (22, 56, 70), 16, 3, t, 2); ground(d, (44, 100, 60))
        rr = random.Random(4)
        for i in range(46):
            if (int(t * 2) + i) % 5: d.point((rr.randrange(PW), rr.randrange(HZ - 30)), fill=(230, 235, 255))
        sun(d, 46, 100 - int(4 * ease(lt / 2)), 12, t); d.ellipse([122, 84, 148, 110], fill=(240, 240, 220)); d.ellipse([130, 80, 156, 106], fill=(26, 56, 110))
        d.point((128, 96), fill=(200, 200, 180)); d.point((134, 102), fill=(200, 200, 180))
        if int(t * 1.5) % 6 == 0:
            sx = 100 + (t * 30) % 60; d.line([(sx, 40), (sx + 10, 46)], fill=(255, 255, 255))
        motes(d, t, 14, (200, 230, 255), 160, 300)
    elif kind == "fishbirds":
        grad(d, 0, HZ, (100, 170, 240), (200, 228, 248)); ground(d, (36, 92, 170)); waves(d, HZ + 4, 300, (90, 150, 230), t)
        for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 56 + i * 10, 0.9)
        d.rectangle([0, 135, PW, HZ + 2], fill=(44, 110, 190)); waves(d, 135, HZ, (120, 180, 240), t)
        for i in range(7): bird(d, ((t * (22 + i * 2) + i * 36) % 240) - 25, 84 + 12 * math.sin(t * 1.3 + i) + (i % 3) * 9, t, s=1.4)
        for i in range(4):
            ph = (t * 0.55 + i * 0.27) % 1; x = 26 + i * 40 + int(14 * ph); y = 140 - 34 * 4 * ph * (1 - ph)
            fish(d, x, int(y), False, ((255, 150, 60), (120, 255, 255), (255, 210, 90), (200, 120, 230))[i], 1.5)
            if ph < 0.12 or ph > 0.9: ripple(d, x, 140, (ph if ph < 0.5 else 1 - ph) * 8)
    elif kind == "animals":
        grad(d, 0, HZ, (130, 200, 245), (215, 236, 246)); hills(d, 150, (150, 200, 150), 12, 2, t, 3)
        for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 60 + i * 12, 1.0)
        ground(d, (84, 156, 72))
        for x in (8, 174): tree(d, x, 162, 40, (56, 140, 64), sway=1.0, t=t)
        gy = 166
        actor(base, "lion", 36 + int(4 * math.sin(t * 0.5)), gy, t, 0.58, walk=0.5)
        actor(base, "sheep", 70, gy, t, 0.55, walk=0.5); actor(base, "bunny", 94, gy + 4, t, 0.5, walk=1.0); actor(base, "deer", 118, gy, t, 0.58, walk=0.5)
        if lt > 3.0:
            actor(base, "Adam", 148, gy, t, 0.6); actor(base, "Eve", 169, gy + 1, t, 0.6); sparkles(d, 160, 140, lt - 3.0, 12, 22)
        for i in range(3): butterfly(d, 20 + (t * 8 + i * 60) % 150, 150 + 10 * math.sin(t + i), t, ((255, 160, 80), (255, 255, 255), (170, 130, 240))[i])
    elif kind == "rest":
        grad(d, 0, HZ, (80, 60, 130), (250, 190, 110)); ground(d, (110, 110, 80), (96, 94, 70))
        r = 26
        for i in range(10, 0, -1): d.ellipse([90 - r * i / 5 * 1.2, HZ - r * i / 5 * 1.2, 90 + r * i / 5 * 1.2, HZ + r * i / 5 * 1.2], fill=lerpc((255, 240, 190), (250, 190, 110), i / 10))
        for a in range(200, 341, 10):
            aa = math.radians(a + math.sin(t) * 2); d.line([(90, HZ), (90 + 180 * math.cos(aa), HZ + 180 * math.sin(aa))], fill=(255, 215, 130))
        for x, h in ((20, 44), (52, 32), (140, 38), (166, 48)): tree(d, x, 166, h, (40, 70, 60), sway=0.8, t=t)
        for i in range(5): bird(d, 20 + (t * 10 + i * 36) % 150, 70 + 8 * math.sin(t + i) + i * 4, t, (60, 40, 70))
        motes(d, t, 18, (255, 220, 140))
    elif kind in ("outro", "outro2"):
        grad(d, 0, HZ, (8, 8, 34), (50, 40, 100)); hills(d, 150, (30, 26, 70), 14, 2, t, 4); ground(d, (44, 40, 80))
        rr = random.Random(11)
        for i in range(70):
            if (int(t * 2) + i) % 5: d.point((rr.randrange(PW), rr.randrange(HZ)), fill=(230, 235, 255))
        pr = 8 + int(1.4 * math.sin(t * 2.2)); cx_, cy_ = 135, 92
        for r_ in (18, 12): d.ellipse([cx_ - r_, cy_ - r_, cx_ + r_, cy_ + r_], outline=(70, 66, 130))
        d.polygon([(cx_, cy_ - pr), (cx_ + 3, cy_ - 3), (cx_ + pr, cy_), (cx_ + 3, cy_ + 3), (cx_, cy_ + pr), (cx_ - 3, cy_ + 3), (cx_ - pr, cy_), (cx_ - 3, cy_ - 3)], fill=(255, 225, 140))
        motes(d, t, 20, (255, 230, 150))
    elif kind == "eden":
        grad(d, 0, HZ, (120, 200, 230), (210, 240, 235)); hills(d, 148, (130, 190, 150), 12, 2, t, 5); ground(d, (70, 160, 80), (56, 138, 66))
        rr = random.Random(21)
        for x, h in ((10, 56), (36, 44), (150, 60), (174, 44), (122, 36), (68, 38)): tree(d, x, 162, h, (46, 140, 70), sway=1.3, t=t)
        for i in range(18): flower(d, rr.randrange(4, 176), rr.randrange(168, 180), ((240, 90, 120), (255, 220, 90), (200, 130, 240), (255, 255, 255))[i % 4], 5, t)
        for x in range(0, PW, 2): d.line([(x, 172 + int(3 * math.sin(x * 0.08 + t))), (x, 176 + int(3 * math.sin(x * 0.08 + t)))], fill=(90, 170, 230))
        if o.get("tree"):
            tree(d, 90, 168, 70, (36, 120, 60), fruit=(220, 50, 60), sway=1.0, t=t)
            if o.get("pair"):
                gl = 1 + 0.5 * math.sin(t * 4); d.ellipse([90 - 3 * gl, 98, 90 + 3 * gl, 104], fill=(255, 240, 160))
        if o.get("snake"): serpent(d, 90, 160, t)
        if o.get("naming"):
            for i, nm in enumerate(("lion", "sheep", "deer", "bunny")):
                ph = (lt - 0.3 - i * 1.0) / 1.5
                if 0 <= ph <= 1: actor(base, nm, int(180 - 124 * ph), 168, t, 0.58, flip=True, walk=1.0)
        for i in range(3): butterfly(d, 20 + (t * 7 + i * 60) % 150, 140 + 10 * math.sin(t + i), t, ((255, 160, 80), (255, 255, 255), (170, 130, 240))[i])
        if "adam" in o and lt >= o["adam"]:
            a_t = lt - o["adam"]; xa = 54 if (o.get("pair") or o.get("naming")) else 62
            if a_t < 0.9: sparkles(d, xa, 150, a_t, 14, 24)
            if a_t > 0.3: actor(base, "Adam", xa, 166, t, 0.64)
        if "eve" in o and lt >= o["eve"]:
            e_t = lt - o["eve"]; xe = 126 if o.get("pair") else 84
            if e_t < 0.9: sparkles(d, xe, 150, e_t, 14, 24)
            if e_t > 0.3: actor(base, "Eve", xe, 167, t, 0.64, flip=True)
        shafts(base, t, 30)
    elif kind == "fruits":
        grad(d, 0, HZ, (40, 90, 130), (150, 200, 200)); hills(d, 150, (60, 120, 110), 14, 2, t, 6); ground(d, (60, 130, 70))
        tree(d, 90, 168, 70, (36, 120, 60), fruit=(220, 50, 60), sway=1.0, t=t)
        cols = [(220, 40, 50), (120, 60, 160), (245, 150, 40), (130, 200, 60)]
        i = int(lt / 0.9) % 4; ph = (lt / 0.9) % 1; r = 11 + int(2 * math.sin(ph * math.pi))
        cx, cy = 90, 112 + int(2 * math.sin(t * 4))
        for rr_ in (26, 22, 18): d.ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], fill=lerpc((255, 245, 200), (130, 170, 160), (rr_ - 18) / 12))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cols[i]); d.line([(cx, cy - r), (cx + 2, cy - r - 4)], fill=(70, 50, 30)); d.rectangle([cx - 4, cy - 6, cx - 2, cy - 4], fill=tuple(min(255, v + 70) for v in cols[i]))
        motes(d, t, 14, (255, 250, 200), 60, 200)
    elif kind == "gate":
        grad(d, 0, HZ, (50, 40, 100), (240, 160, 110)); hills(d, 152, (90, 70, 100), 16, 2, t, 7); ground(d, (110, 90, 70), (96, 78, 60))
        for i in range(8, 0, -1): d.ellipse([34 - i * 5, 130 - i * 6, 34 + i * 5, 130 + i * 6], fill=lerpc((255, 230, 150), (150, 100, 120), i / 8))
        d.rectangle([14, 110, 22, 166], fill=(210, 170, 70)); d.rectangle([46, 110, 54, 166], fill=(210, 170, 70)); d.pieslice([14, 96, 54, 126], 180, 360, fill=(210, 170, 70)); d.pieslice([20, 102, 48, 126], 180, 360, fill=(255, 235, 170))
        d.rectangle([22, 118, 46, 166], fill=(255, 235, 170))
        for x, h in ((100, 26), (160, 34)): tree(d, x, 164, h, (90, 110, 60), sway=0.8, t=t)
        px = 76 + 34 * ease(lt / (scene_dur[scene_at(t)] + 0.5))
        actor(base, "Adam", px + 16, 168, t, 0.62, walk=1.0); actor(base, "Eve", px - 8, 169, t, 0.62, walk=1.0)
        motes(d, t, 16, (255, 220, 150))

def draw_text(d, t):
    si = scene_at(t); sc = SCENES[si]; lt = t - scene_start[si]
    out = 1.0
    if si + 1 < len(SCENES): out = min(1, max(0, ((scene_start[si + 1] - 0.15) - t) / 0.25))
    def T(txt, y, size, color, a, dx=0):
        if a <= 0: return
        f = ImageFont.truetype(BOLD, size)
        while d.textlength(txt, font=f) > (W - 90) and size > 20:
            size -= 4; f = ImageFont.truetype(BOLD, size)
        tw = d.textlength(txt, font=f); x = (W - tw) / 2 + dx; yy = y + (1 - a) * 40
        col = color if a >= 1 else lerpc((10, 10, 30), color, a)
        d.text((x, yy), txt, font=f, fill=col, stroke_width=7, stroke_fill=(10, 10, 32))
    pop = 1 + 0.22 * (1 - ease(lt / 0.4))
    T(sc["t"][0], 120, 84, WHITE, ease(lt / 0.35) * out, dx=int(60 * (1 - ease(lt / 0.5))))
    T(sc["t"][1], 225, int(118 * pop), ACC, ease((lt - 0.15) / 0.35) * out, dx=int(-60 * (1 - ease((lt - 0.1) / 0.5))))

def draw_caption(d, t):
    si = scene_at(t)
    if si == 0: return
    for ci, (a, b) in enumerate(chunk_t):
        if a - 0.02 <= t < b:
            c = chunks[ci]; f = ImageFont.truetype(BOLD, 74); fb = ImageFont.truetype(BOLD, 84)
            sp = d.textlength(" ", font=f)
            ws = [words[i]["w"] for i in c]
            widths = [d.textlength(w, font=(fb if words[i]["t0"] <= t < words[i]["t1"] else f)) for i, w in zip(c, ws)]
            x = (W - (sum(widths) + sp * (len(ws) - 1))) / 2; y = 1018
            for i, w, wd in zip(c, ws, widths):
                act = words[i]["t0"] <= t < words[i]["t1"]
                col = ACC if act else (WHITE if words[i]["t0"] <= t else (170, 170, 205))
                d.text((x, y - (6 if act else 0)), w, font=(fb if act else f), fill=col, stroke_width=7, stroke_fill=(8, 6, 24)); x += wd + sp
            break

def pose_L(t):
    j = 0
    for i, b in enumerate(beats):
        if b - 0.1 <= t: j = i
    pj = max(j - 1, 0); b_ = ease_c((t - (beats[j] - 0.1)) / 0.45)
    P = [20, 150, 95, 135, 60, 125, 30, 150, 80, 140]
    ang = lambda i: P[i % 10] + 10 * math.sin(t * 3.2 + i) + 5 * math.sin(t * 7)
    return (ang(pj) * (1 - b_) + ang(j) * b_, 14 * math.sin(t * 3.2))

YY, XX = np.mgrid[0:H, 0:W]
VIG = (1 - 0.42 * np.clip(((XX - W / 2) / (W * 0.72)) ** 2 + ((YY - H / 2) / (H * 0.68)) ** 2, 0, 1)).astype(np.float32)[..., None]

def scene_layer(t, si):
    sc = SCENES[si]; lt = t - scene_start[si]
    base = Image.new("RGB", (PW, PH)); d = ImageDraw.Draw(base)
    draw_scene(d, base, sc["draw"], sc.get("o"), t, lt)
    return base

def frame(t):
    si = scene_at(t); lt = t - scene_start[si]
    base = scene_layer(t, si)
    if si > 0 and lt < 0.5:
        prev = scene_layer(t, si - 1)
        base = Image.blend(prev, base, ease((lt + 0.15) / 0.65))
    d = ImageDraw.Draw(base)
    fi = min(int(t * FPS), nfr - 1)
    walk = 1 - ease(t / 1.4)
    cx_ = 40 - int(95 * walk) + int(round(3 * math.sin(t * 1.3)))
    bob = int(round(1.6 * abs(math.sin(t * (9 if walk > 0.02 else 3.0)))))
    hop = 0
    for b in beats:
        if 0 <= t - b < 0.28: hop = max(hop, int(round(3 * math.sin(math.pi * (t - b) / 0.28))))
    spr = Image.fromarray(chars.draw("Moses", t, float(amp[fi]), (t % 3.3) < 0.12, pose_L(t)), "RGBA")
    base.paste(spr, (cx_, 180 - bob - hop), spr)
    big = base.resize((W, H), Image.NEAREST)
    # bloom
    bl = base.resize((90, 160), Image.BILINEAR).point(lambda v: int(max(0, v - 185) * 1.6)).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BICUBIC)
    arr = np.asarray(big).astype(np.float32); arr = arr + np.asarray(bl).astype(np.float32) * 0.55
    arr = arr * VIG
    # gentle grade
    arr = (arr - 128) * 1.06 + 128 + 4
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d2 = ImageDraw.Draw(out)
    draw_text(d2, t); draw_caption(d2, t)
    return out

def build_audio():
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr
    v = np.interp(np.arange(n) / sr * VSR, np.arange(len(voice)), voice)
    chords = [(110.00, 164.81, 220.00, 261.63), (87.31, 130.81, 174.61, 220.00), (130.81, 196.00, 261.63, 329.63), (98.00, 146.83, 196.00, 246.94)]
    seg = 6.0
    music = np.zeros(n)
    for ci in range(int(TOTAL / seg) + 2):
        a = int(ci * seg * sr); b = min(n, int((ci + 1) * seg * sr + 1.5 * sr))
        if a >= n: break
        x = tt[a:b] - ci * seg; env = np.clip(x / 1.5, 0, 1) * np.clip((seg + 1.5 - x) / 1.5, 0, 1)
        ch = chords[ci % 4]
        for f in ch:
            for det in (-0.4, 0.0, 0.4):
                music[a:b] += np.sin(2 * np.pi * (f + det) * x) * env * 0.05 + np.sin(2 * np.pi * (f * 2 + det) * x) * env * 0.012
        step = 60 / 84 / 2
        for k_, st in enumerate(np.arange(0, seg, step)):
            note = ch[[1, 2, 3, 2][k_ % 4]] * 2
            aa = a + int(st * sr); m = int(0.9 * sr); xx = np.arange(m) / sr
            if aa + m < n: music[aa:aa + m] += np.sin(2 * np.pi * note * xx) * np.exp(-xx * 5.5) * 0.028
    music = Pedalboard([LowpassFilter(2600), Reverb(room_size=0.7, damping=0.5, wet_level=0.35, dry_level=0.7)])(music.astype(np.float32).reshape(1, -1), sr).reshape(-1)
    envv = np.sqrt(np.convolve(v ** 2, np.ones(int(0.12 * sr)) / (0.12 * sr), mode="same")); envv = np.convolve(envv, np.ones(int(0.3 * sr)) / (0.3 * sr), mode="same")
    duck = 1 - 0.62 * np.clip(envv / 0.12, 0, 1)
    fade = np.clip(tt / 1.0, 0, 1) * np.clip((TOTAL - tt) / 1.2, 0, 1)
    notes = [392, 440, 494, 523, 587, 659, 698, 784, 880, 988]
    chime = np.zeros(n)
    for i, st in enumerate(scene_start):
        a = int(st * sr); m = int(0.6 * sr); x = np.arange(m) / sr
        chime[a:a + m] += (np.sin(2 * np.pi * notes[i % 10] * x) + 0.3 * np.sin(2 * np.pi * notes[i % 10] * 2 * x)) * np.exp(-x * 7) * 0.05
    mix = v * 1.0 + music * 1.0 * duck * fade + chime * duck
    return np.clip(mix * 0.95, -1, 1), sr

def render():
    out = f"{OUTD}/part{PART}"
    n = int(TOTAL * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.9:.2f}:d=0.9", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"{out}.v.tmp.mp4"]
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
        t = scene_start[i] + scene_dur[i] * 0.85
        sh.paste(frame(t).resize((270, 480)), ((i % cols) * 270, (i // cols) * 480))
    sh.save(f"{OUTD}/prev/sheet.png"); print("starts", [round(x, 1) for x in scene_start], "total", round(TOTAL, 1))
    import json; print(json.dumps([[w["w"], round(w["t0"], 2)] for w in words[:14]]))
elif MODE == "full":
    render(); print("done", round(TOTAL, 1))
