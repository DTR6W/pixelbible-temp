"""build5: timeline + audio + render for 16:9 long-form Pixel Bible videos.
usage: python3 build5.py SCRIPT MODE STAGE [part/total]
  SCRIPT: python module in g5/ (e.g. genesis)   MODE: nar | drama   STAGE: tts | preview | render | mix | concat
"""
import sys, os, math, json, hashlib, subprocess, random
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
G5 = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(G5)
sys.path.insert(0, G5); sys.path.insert(0, S)
import engine5 as E, sfx as SFX, cast5
import voices as VZ

SCRIPT, MODE, STAGE = sys.argv[1], sys.argv[2], sys.argv[3]
PART = sys.argv[4] if len(sys.argv) > 4 else "0/1"
OUTD = f"{G5}/out_{SCRIPT}_{MODE}"; os.makedirs(OUTD, exist_ok=True)
CACHE = f"{G5}/tts_cache"; os.makedirs(CACHE, exist_ok=True)
VSR = 24000; SR = 44100; FPS = E.FPS; W, H = E.W, E.H
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
mod = __import__(SCRIPT); SCENES = mod.SCENES
NAR = (MODE == "nar")

VOICES = dict(VZ.VOICES)
VOICES.update({"God": ("am_onyx", 0.80), "Noah": ("bm_george", 0.9), "Naamah": ("bf_emma", 0.95), "Cain": ("am_fenrir", 1.0), "Abel": ("am_liam", 1.0),
               "Shem": ("am_puck", 1.0), "Ham": ("am_eric", 1.0), "Japheth": ("am_echo", 1.0), "Nimrod": ("bm_daniel", 0.9), "Worker": ("am_adam", 1.05), "Worker2": ("am_santa", 1.0), "Worker3": ("bm_lewis", 1.05),
               "Serpent": ("af_nicole", 0.85), "Cherub": ("af_aoede", 0.9), "Mocker": ("bm_daniel", 1.05), "Mocker2": ("am_puck", 1.1), "Seth": ("am_liam", 1.0), "Enoch": ("bm_lewis", 0.92),
               "Lamech": ("am_onyx", 0.95), "Terah": ("bm_george", 0.88), "Abram": ("am_adam", 0.95), "Crowd": ("am_michael", 1.0)})
VOICES.update(getattr(mod, 'VOICES', {}))
SPEAKER_COL = {"God": (255, 236, 160), "Moses": (255, 210, 90), "Serpent": (150, 230, 120), "Cherub": (200, 220, 255), "Eve": (255, 170, 190), "Naamah": (255, 190, 210)}
SPEAKER_COL.update(getattr(mod, "COLORS", {}))

# ------------------------------------------------------------------ timeline items
def beat_items(sc, bi, b):
    items = []
    if NAR and b.get("nar"): items.append(("Moses", b["nar"], b.get("echo")))
    for ln in b.get("lines", []):
        if len(ln) == 2 or not ln[2] or ln[2] == MODE or ln[2] == "both":
            items.append((ln[0], ln[1], b.get("echo")))
    return items

def tts_key(spk, text):
    v, s = VOICES.get(spk, ("am_michael", 1.0)); return hashlib.md5(f"{v}|{s}|{text}".encode()).hexdigest()[:16]

if STAGE == "tts":
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
    n = 0
    for si, sc in enumerate(SCENES):
        for bi, b in enumerate(sc["beats"]):
            for spk, text, _ in beat_items(sc, bi, b):
                f = f"{CACHE}/{tts_key(spk, text)}.wav"
                if os.path.exists(f): continue
                v, s = VOICES.get(spk, ("am_michael", 1.0))
                x, sr = k.create(text, voice=v, speed=s, lang="en-us", sentence_pause=0.3 if spk == "Moses" else 0.22, clause_pause=0.14)
                sf.write(f, x, sr); n += 1; print(si, bi, spk, round(len(x) / sr, 1), text[:50], flush=True)
    print("tts done", n); sys.exit()

# ------------------------------------------------------------------ voice processing
from pedalboard import Delay, Pedalboard, HighpassFilter, LowShelfFilter, PeakFilter, Compressor, Reverb, Limiter, LowpassFilter, Gain, PitchShift, Chorus
def voice_fx(x, sr, spk, echo=None):
    pb = [HighpassFilter(75), LowShelfFilter(200, 2.5), PeakFilter(3200, 1.8, 0.9), PeakFilter(7500, -2.0, 1.0),
          Compressor(threshold_db=-21, ratio=3.0, attack_ms=8, release_ms=140)]
    if spk == "God":
        pb = [HighpassFilter(60), PitchShift(-3.5), LowShelfFilter(180, 6.0), PeakFilter(2500, 2.0, 1.0), Chorus(rate_hz=0.4, depth=0.35, mix=0.35, centre_delay_ms=12),
              Compressor(threshold_db=-20, ratio=3.5, attack_ms=10, release_ms=200), Delay(delay_seconds=0.17, feedback=0.35, mix=0.25), Reverb(room_size=0.92, damping=0.3, wet_level=0.45, dry_level=0.7, width=1.0)]
    elif spk == "Serpent":
        pb += [PitchShift(1.5), Chorus(rate_hz=1.5, depth=0.5, mix=0.4), Reverb(room_size=0.5, damping=0.4, wet_level=0.25, dry_level=0.85)]
    elif spk == "Cherub":
        pb += [Chorus(rate_hz=0.6, depth=0.3, mix=0.3), Reverb(room_size=0.8, damping=0.3, wet_level=0.35, dry_level=0.8)]
    elif spk == "Crowd":
        pb += [Chorus(rate_hz=0.9, depth=0.6, mix=0.6), Delay(delay_seconds=0.07, feedback=0.4, mix=0.4), Reverb(room_size=0.6, wet_level=0.3, dry_level=0.8)]
    else:
        pb += [Reverb(room_size=0.22, damping=0.55, wet_level=0.11, dry_level=0.92, width=0.8)]
    if echo:
        pb += [Delay(delay_seconds=0.12, feedback=0.3, mix=0.22), Reverb(room_size=0.85, damping=0.3, wet_level=0.35, dry_level=0.8)]
    pb.append(Limiter(-1.0))
    y = Pedalboard(pb)(x.astype(np.float32).reshape(1, -1), sr).reshape(-1)
    if spk == "God":  # sub layer following envelope
        env = np.sqrt(np.convolve(y ** 2, np.ones(int(0.02 * sr)) / (0.02 * sr), mode="same"))
        sub = np.sin(2 * np.pi * 55 * np.arange(len(y)) / sr) * env * 0.9
        y = np.clip(y + sub, -1, 1)
    return y

_AU = {}
def load_item(spk, text, echo):
    key = (spk, text, echo)
    if key in _AU: return _AU[key]
    x, sr = sf.read(f"{CACHE}/{tts_key(spk, text)}.wav")
    x = x / max(1e-6, np.abs(x).max()) * 0.85
    idx = np.where(np.abs(x) > 0.015)[0]
    x = x[max(0, idx[0] - int(0.04 * sr)): min(len(x), idx[-1] + int(0.12 * sr))]
    tail = 1.6 if spk == "God" else (1.0 if echo else 0.45)
    y = voice_fx(np.concatenate([x, np.zeros(int(tail * sr))]), sr, spk, echo)
    _AU[key] = (y.astype(np.float32), sr)
    return _AU[key]

# ------------------------------------------------------------------ build timeline
ITEMS = []          # dict(spk, text, t0, dur, si, bi, audio)
scene_start = []; scene_dur = []; beat_starts = []
pos = 0.6
for si, sc in enumerate(SCENES):
    scene_start.append(pos); bs = []
    for bi, b in enumerate(sc["beats"]):
        bs.append(pos - scene_start[si]); bpos = pos; line_starts = []
        for spk, text, echo in beat_items(sc, bi, b):
            au, sr = load_item(spk, text, echo)
            dur = len(au) / sr
            ITEMS.append(dict(spk=spk, text=text, t0=bpos, dur=dur, si=si, bi=bi, audio=au))
            line_starts.append(bpos - scene_start[si]); bpos += dur + (0.35 if spk == "Moses" else 0.5)
        b["_lines"] = line_starts
        pos = max(bpos, pos + b.get("dur", 0.0)) + b.get("pad", 0.0)
    pos += sc.get("pad", 0.8)
    beat_starts.append(bs); scene_dur.append(pos - scene_start[si])
TOTAL = pos + 1.5

# resolve ("L", beat, line, off) time specs inside scenes
def _res(spec, si):
    if isinstance(spec, (list, tuple)) and len(spec) == 4 and spec[0] == "L":
        _, b, li, off = spec; ls = SCENES[si]["beats"][b].get("_lines", [])
        base = ls[min(li, len(ls) - 1)] if ls else beat_starts[si][b]
        return base + off
    return spec
def _walk_specs(obj, si):
    if isinstance(obj, dict): return {k: _walk_specs(v, si) for k, v in obj.items()}
    if isinstance(obj, list): return [_walk_specs(v, si) for v in obj]
    if isinstance(obj, tuple):
        if len(obj) == 4 and obj[0] == "L": return _res(obj, si)
        return tuple(_walk_specs(v, si) for v in obj)
    return obj
for si, sc in enumerate(SCENES):
    for k in ("cast", "dyn", "post", "sfx", "amb"):
        if k in sc: sc[k] = _walk_specs(sc[k], si)

# word timing per item (speech energy mapping)
def word_times(it):
    au = it["audio"]; sr = VSR; win = int(0.01 * sr); n = len(au) // win
    env = np.array([np.sqrt(np.mean(au[i * win:(i + 1) * win] ** 2)) for i in range(n)])
    sp = env > max(0.012, env.max() * 0.06)
    cum = np.concatenate([[0], np.cumsum(sp)]) / 100.0; tot = cum[-1]
    toks = it["text"].split(); ws = [len(t.strip(",.:?!\"")) + 1.2 for t in toks]; totw = sum(ws); c = 0; out = []
    def t_of(st): j = int(np.searchsorted(cum, st)); return min(j, n) * 0.01
    for tk, w in zip(toks, ws):
        a = t_of(tot * c / totw); c += w; b = t_of(tot * c / totw); out.append((tk, it["t0"] + a, it["t0"] + b))
    return out
for it in ITEMS: it["words"] = word_times(it)

def scene_at(t):
    idx = 0
    for i in range(len(SCENES)):
        if scene_start[i] - 0.3 <= t: idx = i
    return idx
def speaking_at(t):
    for it in ITEMS:
        if it["t0"] <= t < it["t0"] + it["dur"]: return it
    return None

# ------------------------------------------------------------------ audio
nfr = int(TOTAL * FPS) + 3
def build_voice():
    v = np.zeros(int(TOTAL * VSR) + VSR, np.float32)
    for it in ITEMS:
        a = int(it["t0"] * VSR); v[a:a + len(it["audio"])] += it["audio"][:len(v) - a]
    return v
VOICE = build_voice()
spf = VSR // FPS
RMS = np.array([np.sqrt(np.mean(VOICE[i * spf:(i + 1) * spf] ** 2)) if (i + 1) * spf <= len(VOICE) else 0 for i in range(nfr)])
AMP = np.convolve(np.clip(RMS / max(1e-6, np.percentile(RMS[RMS > 0.01], 90) if (RMS > 0.01).any() else 1), 0, 1), [0.25, 0.5, 0.25], mode="same")

MOODS = {
 "holy": [(110.00, 164.81, 220.00, 329.63), (130.81, 196.00, 261.63, 392.00), (98.00, 146.83, 196.00, 293.66), (87.31, 130.81, 174.61, 261.63)],
 "calm": [(110.00, 164.81, 220.00, 261.63), (87.31, 130.81, 174.61, 220.00), (130.81, 196.00, 261.63, 329.63), (98.00, 146.83, 196.00, 246.94)],
 "sad": [(110.00, 130.81, 164.81, 220.00), (87.31, 103.83, 130.81, 174.61), (98.00, 116.54, 146.83, 196.00), (82.41, 98.00, 123.47, 164.81)],
 "tense": [(82.41, 98.00, 123.47, 164.81), (87.31, 103.83, 130.81, 174.61), (82.41, 98.00, 116.54, 164.81), (77.78, 92.50, 116.54, 155.56)],
 "epic": [(73.42, 110.00, 146.83, 220.00), (98.00, 146.83, 196.00, 293.66), (87.31, 130.81, 174.61, 261.63), (65.41, 98.00, 130.81, 196.00)],
 "none": None,
}
def build_music(n, tt):
    music = np.zeros(n, np.float32); seg = 6.0
    for si, sc in enumerate(SCENES):
        mood = MOODS.get(sc.get("mood", "calm"))
        if not mood: continue
        s0, s1 = scene_start[si] - 0.5, scene_start[si] + scene_dur[si] + 0.5
        ci = 0; st = s0
        while st < s1:
            a = int(max(0, st) * SR); b = min(n, int((st + seg + 1.5) * SR))
            if a >= n: break
            x = tt[a:b] - st; env = np.clip(x / 1.5, 0, 1) * np.clip((seg + 1.5 - x) / 1.5, 0, 1)
            ch = mood[ci % 4]
            for f in ch:
                for det in (-0.4, 0.0, 0.4):
                    music[a:b] += (np.sin(2 * np.pi * (f + det) * x) * 0.05 + np.sin(2 * np.pi * (f * 2 + det) * x) * 0.012) * env
            if sc.get("mood") in ("epic", "tense"):
                step = 60 / 96 / 2
                for k_, s_ in enumerate(np.arange(0, seg, step)):
                    aa = a + int(s_ * SR); m = int(0.5 * SR); xx = np.arange(m) / SR
                    if aa + m < n: music[aa:aa + m] += np.sin(2 * np.pi * ch[0] * xx) * np.exp(-xx * 9) * 0.05 * (1.0 if k_ % 4 == 0 else 0.5)
            elif sc.get("mood") != "sad":
                step = 60 / 84 / 2
                for k_, s_ in enumerate(np.arange(0, seg, step)):
                    note = ch[[1, 2, 3, 2][k_ % 4]] * 2; aa = a + int(s_ * SR); m = int(0.9 * SR); xx = np.arange(m) / SR
                    if aa + m < n: music[aa:aa + m] += np.sin(2 * np.pi * note * xx) * np.exp(-xx * 5.5) * 0.022
            st += seg; ci += 1
    return Pedalboard([LowpassFilter(2600), Reverb(room_size=0.7, damping=0.5, wet_level=0.35, dry_level=0.7)])(music.reshape(1, -1), SR).reshape(-1)

def build_sfx(n):
    out = np.zeros(n, np.float32)
    def add(x, t, vol=1.0):
        a = int(t * SR)
        if a < 0 or a >= n: return
        out[a:a + len(x)] += x[:n - a] * vol
    for si, sc in enumerate(SCENES):
        s0 = scene_start[si]; bs = beat_starts[si]
        for ev in sc.get("sfx", []):
            t = s0 + E.resolve_t(ev[0], bs); name = ev[1]; kw = {}; vol = 1.0
            for extra in ev[2:]:
                if isinstance(extra, dict): kw = extra
                else: vol = extra
            if name == "steps": x = SFX.footsteps(kw.get("dur", 2.0), kw.get("rate", 2.2), kw.get("surface", "dirt"), seed=si * 10 + int(t))
            elif name == "hammering": x = SFX.hammering(kw.get("dur", 3.0), kw.get("rate", 1.6), seed=si, n_workers=kw.get("n", 1), wood=kw.get("wood", True))
            elif name in SFX.AMBIENT: x = SFX.get(name, dur=kw.get("dur", 6.0))
            else: x = SFX.get(name, **kw)
            add(x, t, vol)
        for bi, b in enumerate(sc["beats"]):
            for ev in b.get("sfx", []):
                t = s0 + bs[bi] + ev[0]; name = ev[1]; kw = {}; vol = 1.0
                for extra in ev[2:]:
                    if isinstance(extra, dict): kw = extra
                    else: vol = extra
                if name == "steps": x = SFX.footsteps(kw.get("dur", 2.0), kw.get("rate", 2.2), kw.get("surface", "dirt"), seed=si * 10 + bi)
                elif name == "hammering": x = SFX.hammering(kw.get("dur", 3.0), kw.get("rate", 1.6), seed=si + bi, n_workers=kw.get("n", 1), wood=kw.get("wood", True))
                elif name in SFX.AMBIENT: x = SFX.get(name, dur=kw.get("dur", 6.0))
                else: x = SFX.get(name, **kw)
                add(x, t, vol)
    return out

def build_ambient(n, tt):
    out = np.zeros(n, np.float32)
    for si, sc in enumerate(SCENES):
        amb = sc.get("amb")
        if not amb: continue
        if isinstance(amb, str): amb = [(amb, 1.0)]
        s0 = scene_start[si] - 0.8; s1 = scene_start[si] + scene_dur[si] + 0.8; dur = s1 - s0
        for name, vol in amb:
            x = SFX.loop(name, dur + 2); fade = np.ones(len(x), np.float32); f = int(1.2 * SR)
            fade[:f] = np.linspace(0, 1, f); fade[-f:] = np.linspace(1, 0, f)
            a = int(max(0, s0) * SR); x = x * fade * vol; out[a:a + len(x)] += x[:n - a]
    return out

def mix_audio():
    n = int(TOTAL * SR); tt = np.arange(n) / SR
    v = np.interp(np.arange(n) / SR * VSR, np.arange(len(VOICE)), VOICE).astype(np.float32)
    music = build_music(n, tt); sfx_ = build_sfx(n); amb = build_ambient(n, tt)
    envv = np.sqrt(np.convolve(v ** 2, np.ones(int(0.12 * SR)) / (0.12 * SR), mode="same")); envv = np.convolve(envv, np.ones(int(0.3 * SR)) / (0.3 * SR), mode="same")
    duck = 1 - 0.6 * np.clip(envv / 0.12, 0, 1)
    fade = np.clip(tt / 1.0, 0, 1) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    mix = v * 1.0 + music * 0.9 * duck * fade + amb * 0.9 * (0.55 + 0.45 * duck) * fade + sfx_ * 0.85 * (0.7 + 0.3 * duck)
    mix = Pedalboard([Compressor(threshold_db=-12, ratio=2.5, attack_ms=10, release_ms=200), Limiter(-1.0)])(mix.reshape(1, -1), SR).reshape(-1)
    return np.clip(mix * 0.95, -1, 1), SR

# ------------------------------------------------------------------ narrator Moses (video 1)
def _moses_series():
    beats = [it["t0"] for it in ITEMS if it["spk"] == "Moses"]
    G = [(25, 10), (100, -20), (70, 15), (120, -10), (50, 25), (95, 0)]
    out = np.zeros((nfr, 2)); x = np.array([20.0, 8.0]); v = np.zeros(2); kk = 70.0; cc = 2 * math.sqrt(kk) * 0.85
    for i in range(nfr):
        t = i / FPS; j = 0
        for q, b in enumerate(beats):
            if b - 0.05 <= t: j = q
        tg = np.array(G[j % len(G)], dtype=float) + np.array([6 * math.sin(t * 2.6 + j), 8 * math.sin(t * 2.0)])
        it = speaking_at(t)
        if not it or it["spk"] != "Moses": tg = np.array([14.0, 10.0])
        for _ in range(3):
            acc = kk * (tg - x) - cc * v; v += acc / FPS / 3; x += v / FPS / 3
        out[i] = x
    return out
MOSES = _moses_series() if NAR else None
MS = 1.15
def draw_moses(base, t, fi):
    it = speaking_at(t); amp = float(AMP[fi]) if (it and it["spk"] == "Moses") else 0.0
    pl = MOSES[fi]
    spr = Image.fromarray(cast5.sprite("Moses", t, amp, (t % 3.3) < 0.12, {"la": (float(pl[0]), float(pl[1]))}, look=0.3), "RGBA")
    spr = spr.resize((int(100 * MS), int(120 * MS)), Image.NEAREST)
    base.paste(spr, (6, E.PH - spr.height + 10), spr)

# ------------------------------------------------------------------ text overlays (full-res)
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(BOLD, sz)
    return _F[sz]
def draw_title(d, t, si, lt):
    sc = SCENES[si]; ti = sc.get("title")
    if not ti: return
    a = E.ease(lt / 0.5) * (1 - E.ease((lt - 4.0) / 0.8))
    if a <= 0: return
    if isinstance(ti, str): ti = (ti,)
    main = ti[0]; sub = ti[1] if len(ti) > 1 else None
    f = font(84); tw = d.textlength(main, font=f); x = (W - tw) / 2; y = 70 + (1 - a) * 30
    col = E.lerpc((10, 10, 30), (255, 230, 140), a)
    d.text((x, y), main, font=f, fill=col, stroke_width=8, stroke_fill=(10, 10, 32))
    if sub:
        f2 = font(44); tw2 = d.textlength(sub, font=f2)
        d.text(((W - tw2) / 2, y + 100), sub, font=f2, fill=E.lerpc((10, 10, 30), (255, 255, 255), a), stroke_width=6, stroke_fill=(10, 10, 32))

def draw_caption(d, t):
    it = speaking_at(t)
    if not it:
        return
    words = it["words"]; col_sp = SPEAKER_COL.get(it["spk"], (255, 255, 255))
    # chunk words into lines of <= 7 words / ~42 chars
    chunks = []; cur = []
    for i, (w, a, b) in enumerate(words):
        cur.append(i)
        if len(cur) >= 7 or len(" ".join(words[q][0] for q in cur)) > 40 or w[-1] in ".?!":
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for ci, c in enumerate(chunks):
        a = words[c[0]][1] - 0.02; b = (words[chunks[ci + 1][0]][1] if ci + 1 < len(chunks) else words[c[-1]][2] + 0.3)
        if a <= t < b:
            f = font(52); fb = font(58); sp = d.textlength(" ", font=f)
            ws = [words[i][0] for i in c]
            widths = [d.textlength(w, font=(fb if words[i][1] <= t < words[i][2] else f)) for i, w in zip(c, ws)]
            total = sum(widths) + sp * (len(ws) - 1)
            x0 = (W - total) / 2 + (90 if NAR else 0); y = H - 150
            if it["spk"] != "Moses":
                lab = it["spk"].upper() + ":"; fl = font(36); lw = d.textlength(lab, font=fl)
                d.text((x0 - lw - 18, y + 14), lab, font=fl, fill=col_sp, stroke_width=5, stroke_fill=(8, 6, 24))
            x = x0
            for i, w, wd in zip(c, ws, widths):
                act = words[i][1] <= t < words[i][2]
                col = (255, 210, 90) if act else ((255, 255, 255) if words[i][1] <= t else (175, 175, 205))
                if it["spk"] != "Moses" and not act: col = col_sp if words[i][1] <= t else (175, 175, 205)
                d.text((x, y - (5 if act else 0)), w, font=(fb if act else f), fill=col, stroke_width=6, stroke_fill=(8, 6, 24)); x += wd + sp
            break

def frame(t):
    si = scene_at(t); lt = t - scene_start[si]; fi = min(int(t * FPS), nfr - 1)
    it = speaking_at(t); spk = it["spk"] if it else None
    ctx = dict(scene_dur=scene_dur[si])
    base = E.compose(SCENES[si], t, lt, beat_starts[si], float(AMP[fi]), spk, ctx)
    if si > 0 and lt < 0.6:
        prev = E.compose(SCENES[si - 1], t, t - scene_start[si - 1], beat_starts[si - 1], 0.0, None, dict(scene_dur=scene_dur[si - 1]))
        base = Image.blend(prev, base, E.ease((lt + 0.1) / 0.7))
    if NAR: draw_moses(base, t, fi)
    out = E.upscale_post(base)
    d = ImageDraw.Draw(out)
    draw_title(d, t, si, lt); draw_caption(d, t)
    return out

if STAGE == "preview":
    os.makedirs(f"{OUTD}/prev", exist_ok=True)
    cols = 4; rows = (len(SCENES) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 480, rows * 270))
    for i in range(len(SCENES)):
        t = scene_start[i] + scene_dur[i] * 0.6
        sh.paste(frame(t).resize((480, 270), Image.BILINEAR), ((i % cols) * 480, (i // cols) * 270))
    sh.save(f"{OUTD}/prev/sheet.png")
    print("scenes", len(SCENES), "total", round(TOTAL, 1), "s =", round(TOTAL / 60, 1), "min")
    for i, sc in enumerate(SCENES): print(i, sc.get("title") or sc.get("env"), round(scene_start[i], 1), round(scene_dur[i], 1))
    if len(sys.argv) > 4:  # specific times: preview SCRIPT MODE preview t1,t2,...
        for k, ts in enumerate(sys.argv[4].split(",")): frame(float(ts)).save(f"{OUTD}/prev/f{k}.png")
elif STAGE == "render":
    p_, n_ = map(int, PART.split("/")); n = int(TOTAL * FPS)
    f0, f1 = n * p_ // n_, n * (p_ + 1) // n_
    out = f"{OUTD}/seg{p_}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", out + ".tmp.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(f0, f1):
        p.stdin.write(frame(i / FPS).tobytes())
        if (i - f0) % 300 == 0: print(f"part {p_}: {i - f0}/{f1 - f0}", flush=True)
    p.stdin.close(); p.wait(); os.replace(out + ".tmp.mp4", out); print("seg done", p_)
elif STAGE == "mix":
    mix, sr = mix_audio(); sf.write(f"{OUTD}/mix.wav", mix, sr); print("mix", round(TOTAL, 1))
elif STAGE == "concat":
    n_ = int(PART.split("/")[1]); lst = f"{OUTD}/segs.txt"
    open(lst, "w").write("".join(f"file 'seg{i}.mp4'\n" for i in range(n_)))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{OUTD}/video.mp4"], check=True)
    final = f"{OUTD}/{SCRIPT}_{MODE}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUTD}/video.mp4", "-i", f"{OUTD}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-vf" if False else "-movflags", "+faststart", final], check=True)
    print("final", final, round(TOTAL / 60, 1), "min")
