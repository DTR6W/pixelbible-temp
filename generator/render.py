import sys, math, random, subprocess, os
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool

W, H, FPS = 1080, 1920, 30
S = sys.argv[1]
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
IY, IH = 1150, 700  # illustration area (y, height) at 1x

def F(p, s): return ImageFont.truetype(p, s)
def cl(x): return min(max(x, 0.0), 1.0)
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eob(x):
    x = cl(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eio(x): x = cl(x); return 3 * x * x - 2 * x ** 3

SC = [
    dict(name="intro", kind="intro", tag=None, title="3 FATOS\nCURIOSOS\nSOBRE O\nESPAÇO", sub="Fique até o final", color=(255, 210, 90), lead=0.3, tail=0.7, sub_t=1.0),
    dict(name="f1", kind="f1", tag="FATO 1", title="Em Vênus, um dia dura mais que um ano", sub="Gira uma vez em 243 dias terrestres, mas dá a volta no Sol em só 225.", color=(120, 200, 255), lead=0.5, tail=0.9, sub_t=3.3),
    dict(name="f2", kind="f2", tag="FATO 2", title="O Sol tem quase toda a massa do Sistema Solar", sub="Todos os planetas juntos ficam com o resto.", color=(255, 150, 110), lead=0.5, tail=0.9, sub_t=3.3),
    dict(name="f3", kind="f3", tag="FATO 3", title="A luz do Sol leva 8 minutos para chegar aqui", sub="Se o Sol sumisse agora, só perceberíamos depois disso.", color=(160, 255, 190), lead=0.5, tail=0.9, sub_t=3.8),
    dict(name="outro", kind="outro", tag=None, title="GOSTOU?", sub="Siga o canal para mais curiosidades", color=(255, 210, 90), lead=0.3, tail=1.2, sub_t=1.0),
]
t0 = 0.0
for s in SC:
    info = sf.info(f"{S}/audio/{s['name']}.wav")
    s["alen"] = info.frames / info.samplerate
    s["dur"] = s["lead"] + s["alen"] + s["tail"]
    s["start"] = t0
    t0 += s["dur"]
TOTAL = t0

# ---------- background ----------
def make_bg():
    ys = np.linspace(0, 1, H)[:, None]
    r = (8 + 14 * ys) * np.ones((H, W)); g = (10 + 8 * ys) * np.ones((H, W)); b = (32 + 40 * ys) * np.ones((H, W))
    return Image.fromarray(np.dstack([r, g, b]).astype("uint8"), "RGB")

def make_stars(seed, n, rmax):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = rnd.randrange(W), rnd.randrange(H)
        r = rnd.randint(1, rmax); c = rnd.randint(150, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, c, 255))
    return im

BG = None; ST1 = None; ST2 = None

# ---------- text layers ----------
def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            test = (line + " " + w).strip()
            if d.textlength(test, font=font) <= maxw: line = test
            else: out.append(line); line = w
        out.append(line)
    return out

def line_layer(text, font, fill):
    h = font.size + 30
    im = Image.new("RGBA", (W, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, 6), text, font=font, fill=fill + (255,))
    return im

def build_layout(s):
    """returns list of (layer, y, t_start, kind)"""
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    out = []
    c = s["color"]
    kind = s["kind"]
    if s["tag"]:
        gf = F(BOLD, 68)
        w = tmp.textlength(s["tag"], font=gf)
        im = Image.new("RGBA", (W, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([(W - w) / 2 - 50, 5, (W + w) / 2 + 50, 125], 60, fill=c + (255,))
        d.text(((W - w) / 2, 5 + 16), s["tag"], font=gf, fill=(10, 12, 35, 255))
        out.append((im, 200, 0.15, "tag"))
        y = 390; tf = F(BOLD, 92); gap = 18; tcol = (255, 255, 255)
    elif kind == "intro":
        y = 230; tf = F(BOLD, 112); gap = 14; tcol = c
    else:
        y = 330; tf = F(BOLD, 170); gap = 20; tcol = c
    lines = wrap(tmp, s["title"], tf, W - 150)
    t = 0.4
    for ln in lines:
        out.append((line_layer(ln, tf, tcol), y, t, "line"))
        y += tf.size + gap; t += 0.18
    # accent bar
    if s["tag"]:
        out.append((None, y + 20, t, "bar"))
        y += 80
    else:
        y += 40
    sf_ = F(REG, 52)
    for ln in wrap(tmp, s["sub"], sf_, W - 160):
        out.append((line_layer(ln, sf_, (205, 215, 245)), y, s["sub_t"] + 0.0, "sub"))
        y += sf_.size + 16
    return out

# ---------- illustration helpers (2x canvas) ----------
def planet(ill, cx, cy, R, base, bands, ang=None, spot=(0, 0, 0), light=True):
    size = 2 * R
    patch = Image.new("RGBA", (size, size), base + (255,)); pd = ImageDraw.Draw(patch)
    for yy, hh, col in bands:
        pd.rectangle([0, int(yy * size), size, int((yy + hh) * size)], fill=col + (255,))
    if ang is not None:
        for k in range(3):
            a = ang + k * 2.1; cs = math.cos(a)
            if cs > 0:
                sx = size / 2 + R * 0.82 * math.sin(a); sy = size * (0.32 + 0.18 * k)
                w = R * 0.16 * cs + 4; h = R * 0.10
                pd.ellipse([sx - w, sy - h, sx + w, sy + h], fill=spot + (255,))
    if light:
        shade = Image.new("RGBA", (size, size), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
        sd.ellipse([0, 0, size - 1, size - 1], fill=(0, 0, 30, 140))
        sd.ellipse([-int(.22 * size), -int(.18 * size), int(.86 * size), int(.9 * size)], fill=(0, 0, 0, 0))
        patch.alpha_composite(shade)
    mask = Image.new("L", (size, size), 0); ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    patch.putalpha(mask)
    ill.paste(patch, (cx - R, cy - R), patch)

def glow(ill, cx, cy, R, col, strength=1.0):
    Rg = int(R * 2.1); size = 2 * Rg
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    steps = 22
    for i in range(steps):
        r = Rg * (1 - i / steps)
        a = int(150 * strength * (i / steps) ** 2)
        gd.ellipse([Rg - r, Rg - r, Rg + r, Rg + r], fill=col + (a,))
    ill.paste(g, (cx - Rg, cy - Rg), g)

def sun(ill, cx, cy, R, t):
    pulse = 1 + 0.04 * math.sin(t * 3)
    glow(ill, cx, cy, int(R * pulse), (255, 170, 40), 1.0)
    d = ImageDraw.Draw(ill); r = int(R * pulse)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 205, 70, 255))
    d.ellipse([cx - r * .72, cy - r * .72, cx + r * .72, cy + r * .72], fill=(255, 225, 120, 255))

def f2c(v): return f"{v:.2f}".replace(".", ",")

def draw_ill(s, t):
    ill = Image.new("RGBA", (2160, 1400), (0, 0, 0, 0)); d = ImageDraw.Draw(ill)
    k = s["kind"]
    if k == "intro":
        cx, cy = 1080, 640 + 28 * math.sin(t * 2.2)
        cy = int(cy)
        ring = [cx - 520, cy - 120, cx + 520, cy + 120]
        d.ellipse(ring, outline=(220, 190, 140, 255), width=34)
        planet(ill, cx, cy, 260, (232, 190, 120), [(0.25, 0.08, (214, 165, 96)), (0.45, 0.10, (240, 205, 140)), (0.68, 0.07, (205, 150, 90))])
        d.arc(ring, 0, 180, fill=(235, 205, 155, 255), width=34)
        ang = t * 1.6
        mx = cx + 520 * math.cos(ang); my = cy + 120 * math.sin(ang)
        d.ellipse([mx - 34, my - 34, mx + 34, my + 34], fill=(235, 235, 245, 255))
    elif k == "f1":
        p_in = eob((t - 0.6) / 0.7)
        R = int(250 * p_in)
        if R > 4:
            planet(ill, 1080, 400, R, (232, 176, 92), [(0.2, 0.1, (214, 150, 80)), (0.42, 0.12, (246, 200, 120)), (0.66, 0.1, (210, 140, 76))], ang=t * 0.9, spot=(150, 90, 50))
        lf = F(BOLD, 72); nf = F(BOLD, 78)
        x0, wmax = 200, 1760
        for i, (label, val, a0, col) in enumerate([("1 DIA (rotação)", 243, 5.5, (255, 190, 90)), ("1 ANO (órbita)", 225, 8.9, (120, 200, 255))]):
            yb = 860 + i * 260
            d.text((x0, yb - 96), label, font=lf, fill=(235, 240, 255, 255))
            d.rounded_rectangle([x0, yb, x0 + wmax, yb + 100], 50, fill=(255, 255, 255, 30))
            p = eio((t - a0) / 1.8)
            w = wmax * (val / 243) * p
            if w > 100:
                d.rounded_rectangle([x0, yb, x0 + w, yb + 100], 50, fill=col + (255,))
                txt = f"{int(round(val * p))} dias"
                tw = d.textlength(txt, font=nf)
                d.text((x0 + w - tw - 40, yb + 8), txt, font=nf, fill=(10, 12, 35, 255))
    elif k == "f2":
        cx, cy, R = 1080, 560, 430
        pin = eob((t - 0.6) / 0.7)
        if pin > 0.02:
            bb = [cx - R, cy - R, cx + R, cy + R]
            d.ellipse(bb, outline=(255, 255, 255, 40), width=90)
            p = eio((t - 3.8) / 2.8)
            if p > 0.002:
                d.arc(bb, -90, -90 + 360 * 0.9986 * p, fill=(255, 170, 60, 255), width=90)
            val = 99.86 * p
            big = F(BOLD, max(10, int(135 * pin)))
            txt = f2c(val) + "%"
            tw = d.textlength(txt, font=big)
            d.text((cx - tw / 2, cy - 85 * pin), txt, font=big, fill=(255, 255, 255, 255))
        la = eo((t - 6.3) / 0.6)
        if la > 0:
            lf = F(BOLD, 70); c1 = (255, 170, 60, int(255 * la)); c2 = (255, 255, 255, int(255 * la))
            d.ellipse([260, 1150, 330, 1220], fill=c1)
            d.text((360, 1140), "Sol  99,86%", font=lf, fill=c2)
            d.ellipse([260, 1270, 330, 1340], fill=(120, 200, 255, int(255 * la)))
            d.text((360, 1260), "Planetas  0,14%", font=lf, fill=c2)
    elif k == "f3":
        sx, sy, ex, ey = 330, 760, 1830, 760
        sun(ill, sx, sy, 200, t)
        p = eio((t - 1.8) / 6.2)
        # trail
        d.line([sx + 200, sy, sx + 200 + (ex - 80 - sx - 200) * 1.0, ey], fill=(255, 255, 255, 40), width=6)
        px = sx + 200 + (ex - 80 - sx - 200) * p
        if 0 < p < 1.0:
            for j in range(8):
                tx = px - j * 40; a = int(200 * (1 - j / 8))
                d.ellipse([tx - 26 + j * 2, sy - 26 + j * 2, tx + 26 - j * 2, sy + 26 - j * 2], fill=(255, 245, 190, a))
            d.ellipse([px - 34, sy - 34, px + 34, sy + 34], fill=(255, 255, 230, 255))
        flash = 1 - cl((t - 8.0) / 0.6) if t > 8.0 else 0
        if p >= 1 and flash > 0:
            glow(ill, ex, ey, 90, (255, 245, 190), flash)
        planet(ill, ex, ey, 90, (60, 130, 230), [(0.25, 0.14, (70, 170, 90)), (0.55, 0.12, (60, 160, 90))])
        sec = 500 * p
        txt = f"{int(sec // 60)}:{int(sec % 60):02d}"
        tf = F(BOLD, 250); tw = d.textlength(txt, font=tf)
        d.text((1080 - tw / 2, 160), txt, font=tf, fill=(255, 245, 190, 255))
    elif k == "outro":
        pulse = 1 + 0.06 * math.sin(t * 5)
        pin = eob((t - 0.5) / 0.6)
        bw, bh = 1000 * pulse * pin, 280 * pulse * pin
        cx, cy = 1080, 560
        if pin > 0.02:
            d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], 140 * pulse * pin, fill=(255, 60, 60, 255))
            bf = F(BOLD, int(150 * pulse * pin)); tx = "SEGUIR"
            tw = d.textlength(tx, font=bf)
            d.text((cx - tw / 2, cy - 100 * pulse * pin), tx, font=bf, fill=(255, 255, 255, 255))
    return ill.resize((1080, 700), Image.LANCZOS)

# ---------- frame ----------
def frame(s, t, layout):
    g = s["start"] + t
    base = BG.copy()
    for layer, sp in ((ST1, 14), (ST2, 34)):
        off = int((g * sp) % H)
        base.paste(layer, (0, off), layer); base.paste(layer, (0, off - H), layer)
    c = s["color"]
    for layer, y, ts, kind in layout:
        a = eo((t - ts) / 0.5)
        if a <= 0: continue
        dy = (1 - a) * 50
        if kind == "bar":
            w = 180 * eo((t - ts) / 0.5)
            ImageDraw.Draw(base).rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 12], fill=c)
            continue
        lyr = layer
        if a < 1:
            lyr = layer.copy(); lyr.putalpha(layer.getchannel("A").point(lambda v, a=a: int(v * a)))
        base.paste(lyr, (0, int(y + dy)), lyr)
    ill = draw_ill(s, t)
    base.paste(ill, (0, IY), ill)
    return base

def init():
    global BG, ST1, ST2
    BG = make_bg(); ST1 = make_stars(7, 90, 2); ST2 = make_stars(11, 60, 3)

def render_scene(name):
    init()
    s = next(x for x in SC if x["name"] == name)
    layout = build_layout(s)
    n = int(round(s["dur"] * FPS))
    fo = s["dur"] - 0.35
    tmp = f"{S}/clips2/{name}.tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", f"fade=t=in:d=0.3,fade=t=out:st={fo:.3f}:d=0.35", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(s, i / FPS, layout).tobytes())
    p.stdin.close(); p.wait()
    os.replace(tmp, f"{S}/clips2/{name}.mp4")
    return name

def build_audio():
    sr = 44100
    n = int(TOTAL * sr) + sr
    mix = np.zeros(n)
    tt = np.arange(n) / sr
    pad = sum(np.sin(2 * np.pi * f * tt + ph) for f, ph in ((110, 0), (164.81, 1), (220, 2), (261.63, 3)))
    pad *= 0.012 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.12 * tt))
    env = np.minimum(1, tt / 2.0) * np.minimum(1, np.maximum(0, (TOTAL - tt)) / 1.5)
    mix += pad * env
    rng = np.random.default_rng(3)
    for s in SC:
        x, r = sf.read(f"{S}/audio/{s['name']}.wav")
        if x.ndim > 1: x = x.mean(1)
        x = np.interp(np.arange(int(len(x) * sr / r)) / sr * r, np.arange(len(x)), x)
        x = x / max(1e-6, np.abs(x).max()) * 0.85
        a = int((s["start"] + s["lead"]) * sr)
        mix[a:a + len(x)] += x
        # whoosh at scene start
        m = int(0.55 * sr); nz = rng.normal(0, 1, m)
        nz = np.convolve(nz, np.ones(60) / 60, mode="same")
        e = np.sin(np.pi * np.arange(m) / m) ** 2
        b = int(s["start"] * sr)
        mix[b:b + m] += nz * e * 0.25
    mix = np.clip(mix, -1, 1)
    sf.write(f"{S}/audio/mix.wav", mix[:int(TOTAL * sr)], sr)

if __name__ == "__main__":
    mode = sys.argv[2]
    os.makedirs(f"{S}/clips2", exist_ok=True)
    if mode == "preview":
        init(); os.makedirs(f"{S}/prev", exist_ok=True)
        for name, t in (("intro", 2.0), ("f1", 9.5), ("f2", 6.5), ("f3", 6.0), ("outro", 2.2)):
            s = next(x for x in SC if x["name"] == name)
            frame(s, t, build_layout(s)).save(f"{S}/prev/{name}.png")
        print("preview ok", [round(s["dur"], 2) for s in SC], round(TOTAL, 2))
    elif mode == "full":
        with Pool(min(5, os.cpu_count() or 2)) as pool:
            for r in pool.imap_unordered(render_scene, [s["name"] for s in SC]):
                print("done", r, flush=True)
        build_audio(); print("audio ok")
