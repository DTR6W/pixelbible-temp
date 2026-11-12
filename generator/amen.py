import sys, math, os, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

S = sys.argv[1]; MODE = sys.argv[2]
W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VOICE_SR = 24000

SEGS = [
    "What does Amen mean?",
    "The word comes from Hebrew, and it means something like: truly, or so be it.",
    "In the Old Testament, people said it to agree with what had just been said. Later, Christians made it the way to close a prayer. It is also used in Judaism and Islam.",
    "So when you say Amen, you are saying: I agree. Let it be so.",
]
LEAD, GAP, TAIL = 0.6, 0.6, 1.4
os.makedirs(f"{S}/amen", exist_ok=True)

if MODE == "tts":
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
    for i, t in enumerate(SEGS):
        x, sr = k.create(t, voice="am_michael", speed=0.95, lang="en-us")
        sf.write(f"{S}/amen/seg{i}.wav", x, sr); print(i, round(len(x) / sr, 2))
    sys.exit()

# ---------- timeline ----------
seg_len, seg_start = [], []
t0 = LEAD
for i in range(len(SEGS)):
    info = sf.info(f"{S}/amen/seg{i}.wav")
    seg_len.append(info.frames / info.samplerate); seg_start.append(t0)
    t0 += seg_len[-1] + GAP
TOTAL = t0 - GAP + TAIL
voice = np.zeros(int(TOTAL * VOICE_SR) + VOICE_SR)
for i in range(len(SEGS)):
    x, sr = sf.read(f"{S}/amen/seg{i}.wav")
    x = x / np.abs(x).max() * 0.9
    a = int(seg_start[i] * VOICE_SR); voice[a:a + len(x)] += x
voice = voice[:int(TOTAL * VOICE_SR)]
nfr = int(TOTAL * FPS) + 2
spf = VOICE_SR // FPS
rms = np.array([np.sqrt(np.mean(voice[i * spf:(i + 1) * spf] ** 2)) if (i + 1) * spf <= len(voice) else 0 for i in range(nfr)])
p90 = np.percentile(rms[rms > 0.01], 90)
amp = np.clip(rms / p90, 0, 1)
amp = np.convolve(amp, [0.25, 0.5, 0.25], mode="same")

BGC = (10, 12, 38)
ACC = (255, 210, 90)
WHITE = (255, 255, 255)
GREY = (170, 180, 215)

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(c, a, bg=BGC): return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

def content_state(t):
    idx = -1
    for i in range(len(SEGS)):
        if seg_start[i] - 0.2 <= t: idx = i
    if idx < 0: idx = 0
    t_in = seg_start[idx] - 0.2
    rel = t - t_in
    out = 1.0
    if idx + 1 < len(SEGS):
        end = seg_start[idx + 1] - 0.2
        out = min(1, max(0, (end - t) / 0.25))
    return idx, rel, out

# ---------- shared content (1080x1920 coordinates, scale k) ----------
def draw_content(d, k, pix, t):
    idx, rel, out = content_state(t)
    def font(bold, size):
        return ImageFont.truetype(BOLD if bold else REG, max(6, int(size * k)))
    def A(start, dur=0.45): return ease((rel - start) / dur) * out
    def T(txt, y, size, color, a, bold=True, maxw=W - 90):
        if a <= 0: return
        f = font(bold, size)
        while d.textlength(txt, font=f) > maxw * k and size > 20:
            size -= 4; f = font(bold, size)
        tw = d.textlength(txt, font=f)
        dy = (1 - a) * 40
        d.text(((W * k - tw) / 2, (y + dy) * k), txt, font=f, fill=lerp(color, a))
    if idx == 0:
        T("WHAT DOES", 300, 120, WHITE, A(0.1)); T("AMEN", 460, 270, ACC, A(0.4)); T("MEAN?", 800, 120, WHITE, A(0.8))
    elif idx == 1:
        T("HEBREW", 260, 64, GREY, A(0.1)); T("אמן", 330, 340, WHITE, A(0.4))
        T("āmēn", 740, 100, (190, 200, 235), A(1.2)); T("= truly, so be it", 890, 84, ACC, A(2.6))
    elif idx == 2:
        L = seg_len[2]
        cards = [("OLD TESTAMENT", "Agreeing with the speaker", 0.0), ("CHRISTIAN PRAYER", "The word ending a prayer", 0.45 * L), ("ALSO USED IN", "Judaism and Islam", 0.78 * L)]
        for j, (h, b, ts) in enumerate(cards):
            a = A(ts)
            if a <= 0: continue
            y = 290 + j * 250 + (1 - a) * 40
            d.rounded_rectangle([90 * k, y * k, 990 * k, (y + 210) * k], int(36 * k), fill=lerp((40, 46, 100), a), outline=lerp(ACC, a), width=max(1, int(5 * k)))
            for txt, yy, sz, col, bold in ((h, y + 26, 60, ACC, True), (b, y + 104, 56, WHITE, False)):
                f = font(bold, sz); tw = d.textlength(txt, font=f)
                d.text(((W * k - tw) / 2, yy * k), txt, font=f, fill=lerp(col, a))
    else:
        T("I AGREE.", 420, 200, ACC, A(0.2)); T("LET IT BE SO.", 700, 120, WHITE, A(2.0))

# ---------- poses ----------
def pose_for(i, t):
    s = math.sin
    if i == 0: return dict(L=(15 + 3 * s(2 * t), 5), R=(145, 35 * s(9 * t)))
    if i == 1: return dict(L=(150 + 4 * s(3 * t), 12 * s(2 * t)), R=(18 + 3 * s(2.5 * t), 8))
    if i == 2: return dict(L=(20 + 2 * s(2 * t), 6), R=(135 + 3 * s(3 * t), 10 * s(2 * t)))
    if i == 3: return dict(L=(105 + 5 * s(3 * t), -8), R=(105 + 5 * s(3 * t + 1), -8))
    return dict(L=(14, 6), R=(14, 6))

def pose(t):
    cur = 0
    for i in range(len(SEGS)):
        if seg_start[i] - 0.2 <= t: cur = i
    if t > seg_start[-1] + seg_len[-1] + 0.2: cur = 9
    prev = max(cur - 1, 0) if cur != 9 else 3
    b = ease((t - (seg_start[cur] - 0.2 if cur != 9 else seg_start[-1] + seg_len[-1] + 0.2)) / 0.5)
    pc, pp = pose_for(cur, t), pose_for(prev, t)
    return {k: tuple(pp[k][j] * (1 - b) + pc[k][j] * b for j in range(2)) for k in ("L", "R")}

def arm(S0, sg, a1, a2, L):
    r1, r2 = math.radians(a1), math.radians(a1 + a2)
    el = (S0[0] + sg * L * math.sin(r1), S0[1] + L * math.cos(r1))
    hd = (el[0] + sg * L * math.sin(r2), el[1] + L * math.cos(r2))
    return el, hd

# ---------- 2D renderer ----------
BGIMG = None; ST = None
def init2d():
    global BGIMG, ST
    ys = np.linspace(0, 1, H)[:, None]
    BGIMG = Image.fromarray(np.dstack([(8 + 14 * ys) * np.ones((H, W)), (10 + 8 * ys) * np.ones((H, W)), (32 + 40 * ys) * np.ones((H, W))]).astype("uint8"), "RGB")
    import random
    rnd = random.Random(5)
    ST = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(ST)
    for _ in range(80):
        x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.randint(1, 3); c = rnd.randint(140, 255)
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, c, 255))

def frame_2d(t):
    base = BGIMG.copy()
    off = int((t * 14) % H)
    base.paste(ST, (0, off), ST); base.paste(ST, (0, off - H), ST)
    d = ImageDraw.Draw(base)
    draw_content(d, 1.0, False, t)
    # character on 2x patch
    Y0 = 1100; PH = 760
    patch = Image.new("RGBA", (W * 2, PH * 2), (0, 0, 0, 0)); pd = ImageDraw.Draw(patch)
    def P(x, y): return (x * 2, (y - Y0) * 2)
    fi = min(int(t * FPS), nfr - 1)
    a_m = float(amp[fi]); by = 6 * math.sin(t * 2.2)
    pd.ellipse([*P(400, 1778), *P(680, 1818)], fill=(0, 0, 0, 90))
    col = (255, 255, 255, 255); lw = 20
    def line(p, q):
        pd.line([P(*p), P(*q)], fill=col, width=lw * 2)
        for z in (p, q):
            x, y = P(*z); pd.ellipse([x - lw, y - lw, x + lw, y + lw], fill=col)
    hc = (540, 1290 + by); hip = (540, 1610 + by * 0.5); sh = (540, 1405 + by)
    line(sh, hip)
    line(hip, (480, 1790)); line(hip, (600, 1790))
    pz = pose(t)
    for sg, key in ((-1, "L"), (1, "R")):
        el, hd = arm(sh, sg, pz[key][0], pz[key][1], 125)
        line(sh, el); line(el, hd)
    r = 88
    pd.ellipse([*P(hc[0] - r, hc[1] - r), *P(hc[0] + r, hc[1] + r)], fill=(10, 12, 38, 255), outline=col, width=lw * 2 // 1)
    blink = (t % 3.3) < 0.12
    for ex in (-30, 30):
        x, y = P(hc[0] + ex, hc[1] - 14)
        hh = 3 if blink else 12
        pd.ellipse([x - 9 * 2 // 1, y - hh, x + 9 * 2 // 1, y + hh], fill=col)
    mx, my = P(hc[0], hc[1] + 38)
    mh = 4 + a_m * 26
    pd.ellipse([mx - 24, my - mh / 2 * 1.0, mx + 24, my + mh / 2 * 1.0 + 4], fill=(255, 255, 255, 255))
    small = patch.resize((W, PH), Image.LANCZOS)
    base.paste(small, (0, Y0), small)
    return base

# ---------- pixel renderer ----------
PW, PHH, K = 180, 320, 6
def frame_px(t):
    im = Image.new("RGB", (PW, PHH), (14, 12, 40)); d = ImageDraw.Draw(im); d.fontmode = "1"
    for b in range(0, PHH, 10):
        c = int(b / PHH * 5)
        d.rectangle([0, b, PW, b + 9], fill=(14 + c * 3, 12 + c * 2, 40 + c * 6))
    import random
    rnd = random.Random(9)
    for n in range(50):
        x = rnd.randrange(PW); y = (rnd.randrange(PHH) + int(t * 2)) % PHH
        if (int(t * 2) + n) % 5 != 0:
            d.point((x, y), fill=(220, 220, 255))
    draw_content(d, 1 / K, True, t)
    fi = min(int(t * FPS), nfr - 1); a_m = float(amp[fi])
    by = int(round(1.2 * math.sin(t * 2.2)))
    skin = (255, 205, 160); hair = (70, 40, 30); tun = (70, 110, 220); dk = (50, 50, 90)
    hc = 222 + by
    d.rectangle([60, 297, 120, 298], fill=(30, 28, 70))
    d.rectangle([84, hc + 22, 89, hc + 44], fill=dk); d.rectangle([91, hc + 22, 96, hc + 44], fill=dk)
    d.rectangle([83, hc + 44, 89, hc + 46], fill=(40, 30, 30)); d.rectangle([91, hc + 44, 97, hc + 46], fill=(40, 30, 30))
    d.rectangle([83, hc + 11, 97, hc + 36], fill=tun)
    pz = pose(t)
    shs = {-1: (84, hc + 14), 1: (96, hc + 14)}
    for sg, key in ((-1, "L"), (1, "R")):
        el, hd = arm(shs[sg], sg, pz[key][0], pz[key][1], 17)
        d.line([shs[sg], el], fill=tun, width=4); d.line([el, hd], fill=skin, width=3)
        d.rectangle([hd[0] - 2, hd[1] - 2, hd[0] + 2, hd[1] + 2], fill=skin)
    d.rectangle([79, hc - 11, 101, hc + 10], fill=skin)
    d.rectangle([79, hc - 11, 101, hc - 6], fill=hair); d.rectangle([77, hc - 9, 78, hc - 2], fill=hair); d.rectangle([102, hc - 9, 103, hc - 2], fill=hair)
    blink = (t % 3.3) < 0.12
    for ex in (84, 94):
        d.rectangle([ex, hc - 1, ex + 1, hc - (1 if blink else 0) + (0 if blink else 1)], fill=(25, 25, 50))
    mh = 1 + int(a_m * 3.2)
    d.rectangle([87, hc + 5, 92, hc + 4 + mh], fill=(130, 40, 50))
    return im.resize((W, H), Image.NEAREST)

# ---------- audio ----------
def build_audio(style):
    sr = 44100
    n = int(TOTAL * sr)
    tt = np.arange(n) / sr
    v = np.interp(np.arange(n) / sr * VOICE_SR, np.arange(len(voice)), voice)
    mix = v.copy()
    if style == "2d":
        pad = sum(np.sin(2 * np.pi * f * tt + p) for f, p in ((110, 0), (164.81, 1), (220, 2), (261.63, 3)))
        mix += pad * 0.011 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * tt)) * np.minimum(1, tt / 2) * np.minimum(1, (TOTAL - tt) / 1.5)
    else:
        notes = [220, 261.63, 329.63, 392, 329.63, 261.63, 196, 246.94]
        step = 0.22
        idx = (tt / step).astype(int) % len(notes)
        fr = np.array(notes)[idx]
        ph = np.cumsum(fr) / sr
        sq = np.sign(np.sin(2 * np.pi * ph))
        env = np.exp(-((tt % step) / step) * 3)
        mix += sq * env * 0.012 * np.minimum(1, tt / 1.0) * np.minimum(1, (TOTAL - tt) / 1.5)
    return np.clip(mix, -1, 1), sr

def render(style):
    if style == "2d": init2d(); fr = frame_2d
    else: fr = frame_px
    out = f"{S}/amen/amen_{style}"
    n = int(TOTAL * FPS)
    fo = TOTAL - 0.4
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", f"fade=t=in:d=0.3,fade=t=out:st={fo:.2f}:d=0.4", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"{out}.v.tmp.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(fr(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    mix, sr = build_audio(style); sf.write(f"{out}.wav", mix, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}.v.tmp.mp4", "-i", f"{out}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}.tmp.mp4"], check=True)
    os.replace(f"{out}.tmp.mp4", f"{out}.mp4")
    return style

if MODE == "preview":
    init2d(); os.makedirs(f"{S}/amen/prev", exist_ok=True)
    for name, t in (("a", seg_start[0] + 1.2), ("b", seg_start[1] + 3.5), ("c", seg_start[2] + seg_len[2] * 0.9), ("d", seg_start[3] + 3.0)):
        frame_2d(t).save(f"{S}/amen/prev/2d_{name}.png"); frame_px(t).save(f"{S}/amen/prev/px_{name}.png")
    print("seg_start", [round(x, 2) for x in seg_start], "len", [round(x, 2) for x in seg_len], "total", round(TOTAL, 2))
elif MODE == "full":
    from multiprocessing import Pool
    with Pool(2) as pool:
        for r in pool.imap_unordered(render, ["2d", "px"]): print("done", r, flush=True)
