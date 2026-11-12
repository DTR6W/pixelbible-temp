import sys, math, os, subprocess, random
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageChops

S = sys.argv[1]; MODE = sys.argv[2]
W, H, FPS = 1080, 1920, 30
PW, PHH, K = 180, 320, 6
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VSR = 24000
os.makedirs(f"{S}/v4", exist_ok=True)

SCENES = [
    ["Why do Christians light candles before Christmas?"],
    ["It is called Advent.", "The word comes from Latin, and it means coming."],
    ["It starts four Sundays before Christmas.", "Each Sunday, one more candle is lit on a wreath."],
    ["This year, most churches begin Advent on November twenty-ninth.", "It is a time of waiting and hope.", "So why the candles? Because the light is coming."],
    ["Four candles. One light.", "Follow for more Bible explained."],
]
FLAT = [(si, s) for si, sc in enumerate(SCENES) for s in sc]

if MODE == "tts":
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
    for i, (si, txt) in enumerate(FLAT):
        x, sr = k.create(txt, voice="am_michael", speed=1.0, lang="en-us")
        sf.write(f"{S}/v4/s{i}.wav", x, sr); print(i, round(len(x) / sr, 2))
    sys.exit()

# ---------- timeline ----------
def load_trim(i):
    x, sr = sf.read(f"{S}/v4/s{i}.wav")
    x = x / np.abs(x).max() * 0.9
    idx = np.where(np.abs(x) > 0.02)[0]
    a = max(0, idx[0] - int(0.03 * sr)); b = min(len(x), idx[-1] + int(0.06 * sr))
    return x[a:b]
sent = []  # dict(text, scene, start, dur, audio)
pos = 0.10
scene_start = []; scene_end = []
for si in range(len(SCENES)):
    scene_start.append(pos)
    for txt in SCENES[si]:
        i = len(sent); au = load_trim(i)
        sent.append(dict(text=txt, scene=si, start=pos, dur=len(au) / VSR, audio=au))
        pos += len(au) / VSR + 0.2
    pos += 0.15
    scene_end.append(sent[-1]["start"] + sent[-1]["dur"])
TOTAL = sent[-1]["start"] + sent[-1]["dur"] + 0.9

words = []  # dict(w, t0, t1, scene, sent)
for j, s in enumerate(sent):
    toks = s["text"].split()
    ws = [len(t.strip(",.:?!")) + 1 + (4 if t[-1] in ",.:?!" else 0) for t in toks]
    tot = sum(ws); cum = 0
    for t, w in zip(toks, ws):
        t0 = s["start"] + s["dur"] * cum / tot; cum += w
        words.append(dict(w=t, t0=t0, t1=s["start"] + s["dur"] * cum / tot, scene=s["scene"], sent=j))
def wt(scene, word, occ=0):
    m = [x for x in words if x["scene"] == scene and x["w"].strip(",.:?!").lower() == word.lower()]
    return m[occ]["t0"]

voice = np.zeros(int(TOTAL * VSR) + VSR)
for s in sent:
    a = int(s["start"] * VSR); voice[a:a + len(s["audio"])] += s["audio"]
nfr = int(TOTAL * FPS) + 3
spf = VSR // FPS
rms = np.array([np.sqrt(np.mean(voice[i * spf:(i + 1) * spf] ** 2)) if (i + 1) * spf <= len(voice) else 0 for i in range(nfr)])
p90 = np.percentile(rms[rms > 0.01], 90)
amp = np.convolve(np.clip(rms / p90, 0, 1), [0.25, 0.5, 0.25], mode="same")

# chunks for captions
chunks = []
for j, s in enumerate(sent):
    ws = [i for i, x in enumerate(words) if x["sent"] == j]
    cur = []
    for i in ws:
        cur.append(i)
        txt = " ".join(words[q]["w"] for q in cur)
        if len(cur) >= 3 or words[i]["w"][-1] in ",.:?!" or len(txt) > 17:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
chunk_t = []
for ci, c in enumerate(chunks):
    st = words[c[0]]["t0"]
    j = words[c[0]]["sent"]
    nxt = words[chunks[ci + 1][0]]["t0"] if ci + 1 < len(chunks) and words[chunks[ci + 1][0]]["sent"] == j else sent[j]["start"] + sent[j]["dur"] + 0.1
    chunk_t.append((st, nxt))

BGC = (10, 12, 38); ACC = (255, 210, 90); WHITE = (255, 255, 255); GREY = (170, 180, 215)
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(c, a, bg=BGC): return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

def cur_scene(t):
    idx = 0
    for i in range(len(SCENES)):
        if scene_start[i] - 0.15 <= t: idx = i
    out = 1.0
    if idx + 1 < len(SCENES):
        out = min(1, max(0, ((scene_start[idx + 1] - 0.15) - t) / 0.2))
    return idx, out

sys.path.insert(0, f"{S}/px")

# ---------- content ----------
def draw_content(d, k, t):
    idx, out = cur_scene(t)
    def font(bold, size): return ImageFont.truetype(BOLD if bold else REG, max(6, int(size * k)))
    def Aabs(ta, dur=0.4): return ease((t - ta) / dur) * out
    def T(txt, y, size, color, a, bold=True, maxw=W - 90, x=None):
        if a <= 0: return
        f = font(bold, size)
        while d.textlength(txt, font=f) > maxw * k and size > 20:
            size -= 4; f = font(bold, size)
        tw = d.textlength(txt, font=f)
        xx = (W * k - tw) / 2 if x is None else x * k - tw / 2
        d.text((xx, (y + (1 - a) * 40) * k), txt, font=f, fill=lerp(color, a))
    if idx == 0:
        pop = 1 + 0.30 * (1 - ease(t / 0.35))
        T("WHY DO CHRISTIANS", 300, 84, WHITE, out)
        T("LIGHT", 400, int(250 * pop), ACC, out)
        T("CANDLES", 690, 190, ACC, Aabs(0.35, 0.3))
        T("BEFORE CHRISTMAS?", 930, 84, WHITE, Aabs(0.7, 0.3))
    elif idx == 1:
        T("ADVENT", 260, 230, ACC, Aabs(scene_start[1] + 0.05))
        T("LATIN: adventus", 590, 76, GREY, Aabs(wt(1, "latin") - 0.1))
        T("= COMING", 720, 150, WHITE, Aabs(wt(1, "coming") - 0.2))
    elif idx == 2:
        T("4 SUNDAYS", 250, 120, WHITE, Aabs(scene_start[2]))
        T("BEFORE CHRISTMAS", 390, 70, GREY, Aabs(wt(2, "four") + 0.1))
        for n, cx in enumerate(CX):
            if CL[n] is not None and t >= CL[n]:
                T(str(n + 1), 905, 80, ACC, Aabs(CL[n], 0.3), x=cx * 6)
    elif idx == 3:
        T("NOV 29", 290, 250, ACC, Aabs(scene_start[3]))
        T("ADVENT BEGINS", 590, 78, GREY, Aabs(wt(3, "advent") - 0.1))
        T("WAITING + HOPE", 730, 100, WHITE, Aabs(wt(3, "waiting") - 0.15))
        T("THE LIGHT IS COMING", 860, 88, ACC, Aabs(wt(3, "light") - 0.2))
    else:
        T("FOUR CANDLES.", 230, 118, WHITE, Aabs(scene_start[4]))
        T("ONE LIGHT.", 350, 150, ACC, Aabs(wt(4, "light") - 0.25))
        T("FOLLOW FOR MORE", 905, 80, ACC, Aabs(wt(4, "follow") - 0.1))
        T("BIBLE EXPLAINED", 990, 78, WHITE, Aabs(wt(4, "bible") - 0.1))

def draw_caption(d, k, t):
    idx, out = cur_scene(t)
    if idx in (0, 4): return
    for ci, (a, b) in enumerate(chunk_t):
        if a - 0.02 <= t < b:
            c = chunks[ci]
            f = ImageFont.truetype(BOLD, max(6, int(76 * k)))
            sp = d.textlength(" ", font=f)
            ws = [words[i]["w"] for i in c]
            widths = [d.textlength(w, font=f) for w in ws]
            tot = sum(widths) + sp * (len(ws) - 1)
            x = (W * k - tot) / 2; y = 1028 * k
            for i, w, wd in zip(c, ws, widths):
                act = words[i]["t0"] <= t
                col = ACC if (words[i]["t0"] <= t < words[i]["t1"]) else (WHITE if act else (150, 150, 190))
                d.text((x + k * 0.9, y + k * 0.9), w, font=f, fill=(8, 6, 24))
                d.text((x, y), w, font=f, fill=col)
                x += wd + sp
            break

def pose_for(i, t):
    s = math.sin
    if i == 0: return dict(L=(15 + 3 * s(2 * t), 5), R=(145, 35 * s(9 * t)))
    if i == 1: return dict(L=(150 + 4 * s(3 * t), 12 * s(2 * t)), R=(18, 8))
    if i == 2: return dict(L=(135 + 5 * s(3 * t), 8 * s(2 * t)), R=(18, 8))
    return dict(L=(105 + 5 * s(3 * t), -8), R=(105, -8))
def ease_c(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3
PRESETS = [20, 150, 95, 135, 60, 125, 30, 150]
def pose_L(t):
    j = 0
    for i, st in enumerate(sent):
        if st["start"] - 0.15 <= t: j = i
    pj = max(j - 1, 0)
    b = ease_c((t - (sent[j]["start"] - 0.15)) / 0.3)
    def ang(i): return PRESETS[i % len(PRESETS)] + 12 * math.sin(t * 4.5 + i) + 6 * math.sin(t * 9)
    return (ang(pj) * (1 - b) + ang(j) * b, 14 * math.sin(t * 3.2))

# candle times
CX = [48, 74, 106, 132]
s_a = [i for i, s in enumerate(sent) if s["scene"] == 2]
CL = [wt(2, "sundays", 0) + 0.1] + [sent[s_a[1]]["start"] + sent[s_a[1]]["dur"] * f for f in (0.3, 0.55, 0.8)]

import elder
def make_sky():
    stops = [(0, (6, 8, 30)), (120, (16, 24, 70)), (200, (40, 50, 110)), (260, (120, 80, 120)), (320, (200, 120, 100))]
    im = Image.new("RGB", (PW, PHH)); d = ImageDraw.Draw(im)
    for y0 in range(0, PHH, 6):
        for i in range(len(stops) - 1):
            (ya, ca), (yb, cb) = stops[i], stops[i + 1]
            if ya <= y0 <= yb:
                f = (y0 - ya) / (yb - ya)
                d.rectangle([0, y0, PW, y0 + 5], fill=tuple(int(ca[j] + (cb[j] - ca[j]) * f) for j in range(3))); break
    return im

def star4(d, cx, cy, r, col, core):
    q = max(2, r // 4)
    d.polygon([(cx, cy - r), (cx + q, cy - q), (cx + r, cy), (cx + q, cy + q), (cx, cy + r), (cx - q, cy + q), (cx - r, cy), (cx - q, cy - q)], fill=col)
    d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=core)

SKY = None; STARS = None; HOUSES = []
shake_times = [scene_start[1], CL[3], sent[-1]["start"]]
jump_times = [wt(1, "advent", 0), wt(3, "light", 0), wt(4, "light", 0), wt(4, "follow", 0)]

def candle(d, x, lit, t, n):
    by = int(130 - 17 * math.sqrt(max(0, 1 - ((x - 90) / 62) ** 2))) + 3
    col = (236, 130, 190) if n == 2 else (120, 70, 190)
    d.rectangle([x - 3, by - 22, x + 3, by], fill=col); d.rectangle([x - 3, by - 22, x - 2, by], fill=tuple(min(255, c + 50) for c in col))
    d.point((x, by - 23), fill=(60, 40, 30))
    if lit:
        fl = int(t * 8 + n) % 3
        d.rectangle([x - 1, by - 28 - (fl == 0), x + 1, by - 24], fill=(255, 190, 70))
        d.rectangle([x, by - 27, x, by - 25], fill=(255, 245, 190))
        for r_ in (7, 5):
            for a in range(0, 360, 30):
                px_ = int(x + r_ * math.cos(math.radians(a))); py_ = int(by - 26 + r_ * math.sin(math.radians(a)))
                if (a // 30 + int(t * 6)) % 3 == 0: d.point((px_, py_), fill=(255, 215, 120))

def frame(t):
    global SKY, STARS, HOUSES
    rnd = random.Random(7)
    if SKY is None:
        SKY = make_sky(); STARS = [(rnd.randrange(PW), rnd.randrange(230)) for _ in range(70)]
        HOUSES = [(rnd.randrange(4, 160), rnd.randrange(3, 7)) for _ in range(7)]
    base = SKY.copy(); d = ImageDraw.Draw(base); d.fontmode = "1"
    for n, (x, y) in enumerate(STARS):
        if (int(t * 2) + n) % 5 != 0: d.point((x, y), fill=(225, 230, 255) if n % 3 else (255, 235, 170))
    pulse = 5 + int(1.2 * math.sin(t * 2.2)) + (4 if cur_scene(t)[0] == 4 else 0)
    sx, sy = 138, 30
    for r_, a_ in ((16, 25), (11, 50)):
        d.ellipse([sx - r_, sy - r_, sx + r_, sy + r_], outline=(26 + a_, 30 + a_, 80 + a_))
    star4(d, sx, sy, pulse + 6, (255, 225, 140), (255, 252, 220))
    for x in range(PW):
        y1 = int(262 + 8 * math.sin(x * 0.04 + 0.6) + 4 * math.sin(x * 0.12)); d.line([(x, y1), (x, PHH)], fill=(34, 30, 70))
    for hx, hw in HOUSES:
        hy = int(262 + 8 * math.sin(hx * 0.04 + 0.6) + 4 * math.sin(hx * 0.12)) + 2
        d.rectangle([hx, hy - 6, hx + hw + 4, hy], fill=(54, 44, 86)); 
        if (hx + int(t * 1.5)) % 5: d.point((hx + 2, hy - 3), fill=(255, 200, 100))
    for x in range(PW):
        y2 = int(284 + 5 * math.sin(x * 0.05 + 1.3) + 2 * math.sin(x * 0.15)); d.line([(x, y2), (x, PHH)], fill=(70, 50, 84))
    d.rectangle([0, 296, PW, PHH], fill=(92, 66, 80))
    for _ in range(40): d.point((rnd.randrange(PW), rnd.randrange(298, PHH)), fill=(112, 82, 92))
    idx, outa = cur_scene(t)
    if idx in (2, 4):
        rr2 = random.Random(5)
        for a_ in range(0, 360, 3):
            for w_ in range(-4, 5):
                xx = int(90 + (60 + w_) * math.cos(math.radians(a_))); yy = int(130 + (17 + w_ * 0.6) * math.sin(math.radians(a_)))
                d.point((xx, yy), fill=rr2.choice([(28, 100, 56), (40, 140, 70), (60, 165, 90), (24, 80, 48)]))
        for a_ in range(0, 360, 24):
            xx = int(90 + 60 * math.cos(math.radians(a_))); yy = int(130 + 17 * math.sin(math.radians(a_)))
            d.rectangle([xx - 1, yy - 1, xx, yy], fill=(200, 40, 50))
        for n, cx in enumerate(CX): candle(d, cx, idx == 4 or (CL[n] is not None and t >= CL[n]), t, n)
    draw_content(d, 1 / K, t)
    draw_caption(d, 1 / K, t)
    if idx >= 3:
        for i in range(26):
            x = 20 + (i * 37) % 140 + 4 * math.sin(t * 2 + i); y = 290 - ((t * 16 + i * 19) % 140)
            if int(t * 5 + i) % 3 != 0:
                d.point((int(x), int(y)), fill=(255, 235, 150))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.point((int(x) + dx, int(y) + dy), fill=(255, 215, 110))
    fi = min(int(t * FPS), nfr - 1)
    jump = 0
    for te in jump_times:
        if 0 <= t - te < 0.35: jump = max(jump, int(round(6 * math.sin(math.pi * (t - te) / 0.35))))
    spr = Image.fromarray(elder.draw(t, float(amp[fi]), (t % 3.3) < 0.12, pose_L(t)), "RGBA")
    walk = 1 - ease(t / 1.3)
    cx_ = 40 - int(95 * walk) + int(round(3 * math.sin(t * 1.4)))
    bob = int(round(1.6 * abs(math.sin(t * (9 if walk > 0.02 else 3.2)))))
    hop = 0
    for st in sent:
        if 0 <= t - st["start"] < 0.25: hop = max(hop, int(round(3 * math.sin(math.pi * (t - st["start"]) / 0.25))))
    base.paste(spr, (cx_, 180 - jump - bob - hop), spr)
    return base.resize((W, H), Image.NEAREST)

def build_audio():
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr
    mix = np.interp(np.arange(n) / sr * VSR, np.arange(len(voice)), voice)
    pad = sum(np.sin(2 * np.pi * f * tt + p) for f, p in ((98, 0), (146.83, 1), (196, 2), (246.94, 3)))
    mix += pad * 0.010 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * tt))
    ev = [(0.05, 392)] + [(c, 523 + 110 * i) for i, c in enumerate(CL)] + [(scene_start[1] + 0.05, 660), (wt(1, "coming") - 0.2, 880), (scene_start[3], 784), (wt(3, "light") - 0.2, 988), (scene_start[4], 659), (wt(4, "light") - 0.25, 988), (wt(4, "follow"), 1175)]
    for te, fr in ev:
        a = int(max(0, te) * sr); m = int(0.09 * sr)
        x = np.arange(m) / sr
        mix[a:a + m] += np.sin(2 * np.pi * fr * x) * np.exp(-x * 28) * 0.07
    return np.clip(mix, -1, 1), sr

def render():
    out = f"{S}/v4/advent"
    n = int(TOTAL * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", f"fade=t=in:d=0.3,fade=t=out:st={TOTAL-0.8:.2f}:d=0.8",
           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"{out}.v.tmp.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    mix, sr = build_audio(); sf.write(f"{out}.wav", mix, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}.v.tmp.mp4", "-i", f"{out}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}.tmp.mp4"], check=True)
    os.replace(f"{out}.tmp.mp4", f"{out}.mp4")

if __name__ == "__main__":
    if MODE == "preview":
        os.makedirs(f"{S}/v4/prev", exist_ok=True)
        pts = {"a": 0.5, "b": wt(1, "coming") + 0.3, "c": CL[1] + 0.3, "d": CL[3] + 0.8, "e": wt(3, "waiting") + 0.5, "f": wt(3, "light") + 1.0}
        for n_, t in pts.items(): frame(t).save(f"{S}/v4/prev/{n_}.png")
        print("scene_start", [round(x, 2) for x in scene_start], "total", round(TOTAL, 2), [round(c, 2) for c in CL])
    elif MODE == "full":
        render(); print("done", round(TOTAL, 2))
