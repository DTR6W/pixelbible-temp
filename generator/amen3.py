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
os.makedirs(f"{S}/v3", exist_ok=True)

SCENES = [
    ["Why do we say Amen after every prayer?"],
    ["Amen is a Hebrew word.", "It means truly, or so be it."],
    ["In the Old Testament, people said it to agree.", "Today it ends Christian prayers, and it is used in Judaism and Islam too."],
    ["So saying Amen means: I agree. Let it be so.", "That is why we say it after every prayer."],
]
FLAT = [(si, s) for si, sc in enumerate(SCENES) for s in sc]

if MODE == "tts":
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
    for i, (si, txt) in enumerate(FLAT):
        x, sr = k.create(txt, voice="am_michael", speed=1.0, lang="en-us")
        sf.write(f"{S}/v3/s{i}.wav", x, sr); print(i, round(len(x) / sr, 2))
    sys.exit()

# ---------- timeline ----------
def load_trim(i):
    x, sr = sf.read(f"{S}/v3/s{i}.wav")
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

# ---------- content ----------
def draw_content(d, k, t):
    idx, out = cur_scene(t)
    base = scene_start[idx] - 0.15
    def font(bold, size): return ImageFont.truetype(BOLD if bold else REG, max(6, int(size * k)))
    def Aabs(ta, dur=0.4): return ease((t - ta) / dur) * out
    def T(txt, y, size, color, a, bold=True, maxw=W - 90):
        if a <= 0: return
        f = font(bold, size)
        while d.textlength(txt, font=f) > maxw * k and size > 20:
            size -= 4; f = font(bold, size)
        tw = d.textlength(txt, font=f)
        d.text(((W * k - tw) / 2, (y + (1 - a) * 40) * k), txt, font=f, fill=lerp(color, a))
    if idx == 0:
        pop = 1 + 0.30 * (1 - ease(t / 0.35))
        T("WHY DO WE SAY", 330, 112, WHITE, 1.0 * out)
        T("AMEN", 470, int(270 * pop), ACC, 1.0 * out)
        T("AFTER EVERY", 800, 104, WHITE, Aabs(0.35, 0.3))
        T("PRAYER?", 925, 120, WHITE, Aabs(0.55, 0.3))
    elif idx == 1:
        T("HEBREW", 260, 64, GREY, Aabs(scene_start[1]))
        T("אמן", 330, 340, WHITE, Aabs(scene_start[1] + 0.1))
        T("āmēn", 740, 100, (190, 200, 235), Aabs(wt(1, "hebrew", 0)))
        T("= truly, so be it", 890, 84, ACC, Aabs(wt(1, "truly") - 0.1))
    elif idx == 2:
        cards = [("OLD TESTAMENT", "Agreeing with the speaker", scene_start[2]),
                 ("CHRISTIAN PRAYER", "The word ending a prayer", wt(2, "christian") - 0.15),
                 ("ALSO USED IN", "Judaism and Islam", wt(2, "judaism") - 0.15)]
        for j, (h, b, ts) in enumerate(cards):
            a = Aabs(ts)
            if a <= 0: continue
            y = 290 + j * 250 + (1 - a) * 40
            d.rounded_rectangle([90 * k, y * k, 990 * k, (y + 210) * k], int(36 * k), fill=lerp((40, 46, 100), a), outline=lerp(ACC, a), width=max(1, int(5 * k)))
            for txt, yy, sz, col, bold in ((h, y + 26, 60, ACC, True), (b, y + 104, 56, WHITE, False)):
                f = font(bold, sz); tw = d.textlength(txt, font=f)
                d.text(((W * k - tw) / 2, yy * k), txt, font=f, fill=lerp(col, a))
    else:
        T("I AGREE.", 420, 200, ACC, Aabs(wt(3, "agree") - 0.2))
        T("LET IT BE SO.", 700, 120, WHITE, Aabs(wt(3, "let") - 0.1))
        fa = Aabs(sent[-1]["start"], 0.3)
        if fa > 0:
            pop = 1 + 0.3 * (1 - ease((t - sent[-1]["start"]) / 0.3))
            d.rectangle([0, 380 * k, W * k, 1000 * k], fill=lerp(BGC, 1.0) if False else BGC) if False else None

def draw_caption(d, k, t):
    idx, out = cur_scene(t)
    if idx == 0: return
    for ci, (a, b) in enumerate(chunk_t):
        if a - 0.02 <= t < b:
            c = chunks[ci]
            f = ImageFont.truetype(BOLD, max(6, int(76 * k)))
            sp = d.textlength(" ", font=f)
            ws = [words[i]["w"].strip(",.:?!") if False else words[i]["w"] for i in c]
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

# ---------- poses ----------
def pose_for(i, t):
    s = math.sin
    if i == 0: return dict(L=(15 + 3 * s(2 * t), 5), R=(145, 35 * s(9 * t)))
    if i == 1: return dict(L=(150 + 4 * s(3 * t), 12 * s(2 * t)), R=(18 + 3 * s(2.5 * t), 8))
    if i == 2: return dict(L=(20 + 2 * s(2 * t), 6), R=(135 + 3 * s(3 * t), 10 * s(2 * t)))
    if i == 3: return dict(L=(105 + 5 * s(3 * t), -8), R=(105 + 5 * s(3 * t + 1), -8))
    return dict(L=(14, 6), R=(14, 6))
def ease_c(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3
def pose_L(t):
    cur = 0
    for i in range(len(SCENES)):
        if scene_start[i] - 0.2 <= t: cur = i
    prev = max(cur - 1, 0)
    b = ease_c((t - (scene_start[cur] - 0.2)) / 0.4)
    pc, pp = pose_for(cur, t)["L"], pose_for(prev, t)["L"]
    return tuple(pp[j] * (1 - b) + pc[j] * b for j in range(2))

# ---------- frame ----------
sys.path.insert(0, f"{S}/px")
import elder
SKY = None; STARS = None
def make_sky():
    stops = [(0, (18, 14, 48)), (110, (64, 32, 90)), (180, (186, 84, 98)), (235, (240, 160, 100)), (320, (240, 160, 100))]
    im = Image.new("RGB", (PW, PHH)); d = ImageDraw.Draw(im)
    for y0 in range(0, PHH, 8):
        for i in range(len(stops) - 1):
            (ya, ca), (yb, cb) = stops[i], stops[i + 1]
            if ya <= y0 <= yb:
                f = (y0 - ya) / (yb - ya)
                d.rectangle([0, y0, PW, y0 + 7], fill=tuple(int(ca[j] + (cb[j] - ca[j]) * f) for j in range(3))); break
    return im

amen_times = [x["t0"] for x in words if x["w"].strip(",.:?!").lower() == "amen"]
shake_times = [scene_start[1], wt(3, "agree"), sent[-1]["start"]]

def frame(t):
    global SKY, STARS
    if SKY is None:
        SKY = make_sky(); rnd = random.Random(4); STARS = [(rnd.randrange(PW), rnd.randrange(150)) for _ in range(45)]
    base = SKY.copy(); d = ImageDraw.Draw(base); d.fontmode = "1"
    for n, (x, y) in enumerate(STARS):
        if (int(t * 2) + n) % 4 != 0: d.point((x, y), fill=(235, 235, 255))
    sy = 216 - int(t * 0.25)
    d.ellipse([30, sy - 16, 62, sy + 16], fill=(255, 205, 110)); d.ellipse([34, sy - 12, 58, sy + 12], fill=(255, 232, 150))
    for x in range(PW):
        y1 = int(248 + 7 * math.sin((x + t * 2) * 0.045) + 3 * math.sin((x + t * 2) * 0.11)); d.line([(x, y1), (x, PHH)], fill=(150, 72, 96))
        y2 = int(270 + 5 * math.sin((x + t * 5) * 0.06 + 1.3) + 2 * math.sin((x + t * 5) * 0.15)); d.line([(x, y2), (x, PHH)], fill=(200, 122, 98))
    d.rectangle([0, 289, PW, PHH], fill=(224, 176, 114))
    rr = random.Random(2)
    for _ in range(40): d.point((rr.randrange(PW), rr.randrange(292, PHH)), fill=(200, 150, 96))
    draw_content(d, 1 / K, t)
    draw_caption(d, 1 / K, t)
    idx, _ = cur_scene(t)
    if idx == 3:
        for i in range(16):
            x = 20 + (i * 37) % 140 + 4 * math.sin(t * 2 + i); y = 290 - ((t * 16 + i * 19) % 130)
            if int(t * 5 + i) % 3 != 0:
                d.point((int(x), int(y)), fill=(255, 235, 150)); d.point((int(x) - 1, int(y)), fill=(255, 215, 110)); d.point((int(x) + 1, int(y)), fill=(255, 215, 110)); d.point((int(x), int(y) - 1), fill=(255, 215, 110)); d.point((int(x), int(y) + 1), fill=(255, 215, 110))
    d.rectangle([0, 0, int(PW * t / TOTAL), 1], fill=ACC)
    fi = min(int(t * FPS), nfr - 1)
    jump = 0
    for te in amen_times:
        if 0 <= t - te < 0.35: jump = max(jump, int(round(6 * math.sin(math.pi * (t - te) / 0.35))))
    spr = Image.fromarray(elder.draw(t, float(amp[fi]), (t % 3.3) < 0.12, pose_L(t)), "RGBA")
    base.paste(spr, (40, 180 - jump), spr)
    for te in shake_times:
        if 0 <= t - te < 0.22:
            base = ImageChops.offset(base, int(round(math.sin(t * 90) * 1.2)), int(round(math.cos(t * 70) * 1.2)))
    return base.resize((W, H), Image.NEAREST)

def build_audio():
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr
    mix = np.interp(np.arange(n) / sr * VSR, np.arange(len(voice)), voice)
    pad = sum(np.sin(2 * np.pi * f * tt + p) for f, p in ((110, 0), (164.81, 1), (220, 2), (261.63, 3)))
    mix += pad * 0.010 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * tt))
    ev = [(0.05, 330), (scene_start[1] + 0.1, 660), (wt(1, "truly") - 0.1, 880), (scene_start[2], 740), (wt(2, "christian") - 0.15, 740), (wt(2, "judaism") - 0.15, 740), (wt(3, "agree") - 0.2, 880), (wt(3, "let") - 0.1, 660), (sent[-1]["start"], 523)]
    for te, fr in ev:
        a = int(max(0, te) * sr); m = int(0.07 * sr)
        x = np.arange(m) / sr
        mix[a:a + m] += np.sign(np.sin(2 * np.pi * fr * x)) * np.exp(-x * 40) * 0.05
    return np.clip(mix, -1, 1), sr

def render():
    out = f"{S}/v3/amen_v3"
    n = int(TOTAL * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"{out}.v.tmp.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    mix, sr = build_audio(); sf.write(f"{out}.wav", mix, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}.v.tmp.mp4", "-i", f"{out}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}.tmp.mp4"], check=True)
    os.replace(f"{out}.tmp.mp4", f"{out}.mp4")

if __name__ == "__main__":
    sys.path.insert(0, f"{S}/px")
    if MODE == "preview":
        os.makedirs(f"{S}/v3/prev", exist_ok=True)
        pts = {"a": 0.0, "b": 0.4, "c": wt(1, "truly") + 0.3, "d": wt(2, "judaism") + 0.5, "e": wt(3, "agree") + 0.6, "f": sent[-1]["start"] + 1.0}
        for n_, t in pts.items(): frame(t).save(f"{S}/v3/prev/{n_}.png")
        print("scene_start", [round(x, 2) for x in scene_start], "total", round(TOTAL, 2))
    elif MODE == "full":
        render(); print("done", round(TOTAL, 2))
