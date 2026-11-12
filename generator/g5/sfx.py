"""Procedural sound effects + ambient loops (no external samples). All at SR=44100, mono float32."""
import math
import numpy as np
from scipy import signal

SR = 44100
_CACHE = {}


def _t(dur): return np.arange(int(dur * SR)) / SR
def _noise(dur, seed=0): return np.random.RandomState(seed).randn(int(dur * SR)).astype(np.float32)
def _env(n, a, d, s=0.0, r=0.0, sl=1.0):
    e = np.zeros(n, np.float32); i = 0
    for ln, v0, v1 in ((int(a * SR), 0, 1), (int(d * SR), 1, sl), (int(s * SR), sl, sl), (int(r * SR), sl, 0)):
        ln = max(0, min(ln, n - i))
        if ln: e[i:i + ln] = np.linspace(v0, v1, ln); i += ln
    return e
def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], btype="band"); return signal.lfilter(b, a, x).astype(np.float32)
def _lp(x, f, order=2):
    b, a = signal.butter(order, min(f, SR / 2 - 100) / (SR / 2)); return signal.lfilter(b, a, x).astype(np.float32)
def _hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), btype="high"); return signal.lfilter(b, a, x).astype(np.float32)
def _norm(x, g=0.9):
    m = np.abs(x).max()
    return (x / m * g).astype(np.float32) if m > 1e-6 else x.astype(np.float32)
def _fade(x, a=0.01, r=0.05):
    n = len(x); fa, fr = int(a * SR), int(r * SR)
    x = x.copy()
    if fa: x[:fa] *= np.linspace(0, 1, fa)
    if fr: x[-fr:] *= np.linspace(1, 0, fr)
    return x
def _saw(f, dur, vib=0.0, vr=5.0):
    t = _t(dur); ph = 2 * np.pi * f * t + vib * np.sin(2 * np.pi * vr * t)
    return (2 * ((ph / (2 * np.pi)) % 1) - 1).astype(np.float32)
def _sine(f, dur, vib=0.0, vr=5.0):
    t = _t(dur); return np.sin(2 * np.pi * f * t + vib * np.sin(2 * np.pi * vr * t)).astype(np.float32)
def _formant(x, fs, bw=120):
    out = np.zeros_like(x)
    for f, g in fs:
        out += _bp(x, max(40, f - bw), f + bw) * g
    return out
def _rev(x, dur=0.8, mix=0.25, seed=1):
    """cheap reverb: noise tail convolution"""
    ir = _noise(dur, seed) * np.exp(-np.arange(int(dur * SR)) / SR * (4.5 / dur)); ir = _lp(ir, 5000); ir /= np.abs(ir).sum() / 60
    wet = signal.fftconvolve(x, ir)[:len(x) + int(dur * SR)]
    out = np.zeros(len(wet), np.float32); out[:len(x)] += x
    return (out + wet * mix).astype(np.float32)

# --------------------------------------------------------------- one-shots
def thunder(seed=0, dist=1.0):
    dur = 3.5 + 1.5 * dist
    n = _noise(dur, seed)
    x = _lp(n, 180 / dist) * 1.0 + _lp(n, 60) * 1.5
    e = _env(len(x), 0.02 + 0.2 * dist, 0.3, 0.0, dur - 0.6, 0.6)
    rum = _lp(_noise(dur, seed + 1), 90) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * _t(dur) + seed))
    return _norm(_fade(x * e + rum * e * 0.7, 0.005, 0.3), 0.95)

def crack(seed=0):  # lightning crack
    x = _hp(_noise(0.4, seed), 1500) * _env(int(0.4 * SR), 0.001, 0.08, 0, 0.3, 0.3)
    return _norm(x, 0.8)

def rain(dur=10.0, seed=3, heavy=1.0):
    n = _noise(dur, seed)
    x = _bp(n, 1800, 9000) * 0.6 + _bp(n, 300, 1200) * 0.3 * heavy
    drops = (_noise(dur, seed + 5) > 2.6 - 0.4 * heavy).astype(np.float32)
    drops = signal.lfilter([1], [1, -0.985], drops) * 0.08
    x = x + _bp(drops * _noise(dur, seed + 6), 2500, 7000)
    return _norm(_fade(x, 0.3, 0.3), 0.6)

def wind(dur=10.0, seed=2, strength=1.0):
    t = _t(dur); n = _noise(dur, seed)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t + seed) * np.sin(2 * np.pi * 0.21 * t)
    x = np.zeros_like(n)
    for f in (250, 500, 900):
        x += _bp(n, f * (0.8 + 0.4 * lfo.mean()), f * 1.6) * (0.5 + 0.5 * lfo) / 3
    x = _lp(x, 2500 * strength + 500)
    return _norm(_fade(x, 0.5, 0.5), 0.55 * strength)

def waves(dur=10.0, seed=4, calm=1.0):
    t = _t(dur); n = _noise(dur, seed)
    sw = 0.5 + 0.5 * np.sin(2 * np.pi * (0.12 / calm) * t)
    x = _bp(n, 150, 1400) * sw ** 2 + _bp(n, 1500, 5000) * sw ** 3 * 0.4
    return _norm(_fade(x, 0.4, 0.4), 0.5)

def river(dur=10.0, seed=7):
    n = _noise(dur, seed); t = _t(dur)
    x = _bp(n, 600, 4000) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * t)) + _bp(n, 150, 600) * 0.4
    return _norm(_fade(x, 0.3, 0.3), 0.4)

def fire(dur=10.0, seed=8):
    n = _noise(dur, seed); t = _t(dur)
    low = _lp(n, 400) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t))
    pops = (np.random.RandomState(seed + 1).rand(len(n)) < 0.00025).astype(np.float32)
    pops = signal.lfilter([1], [1, -0.9], pops) * _noise(dur, seed + 2) * 3
    x = low + _bp(pops, 1500, 7000)
    return _norm(_fade(x, 0.2, 0.2), 0.5)

def forest(dur=10.0, seed=9):
    """gentle breeze + distant birds"""
    x = wind(dur, seed, 0.4) * 0.5
    r = np.random.RandomState(seed)
    for _ in range(int(dur * 1.2)):
        st = r.uniform(0, dur - 0.5); y = bird_chirp(r.randint(0, 999)) * 0.25
        a = int(st * SR); x[a:a + len(y)] += y[:len(x) - a]
    return _norm(x, 0.45)

def night(dur=10.0, seed=10):
    """crickets"""
    t = _t(dur); x = wind(dur, seed, 0.3) * 0.4
    for k in range(3):
        f = 4200 + k * 600; rate = 28 + k * 7
        g = (np.sin(2 * np.pi * rate * t) > 0.3).astype(np.float32) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t + k))
        x += _sine(f, dur) * g * 0.05
    return _norm(x, 0.35)

def desert(dur=10.0, seed=11): return wind(dur, seed, 1.1)

def crowd(dur=10.0, seed=12, n=24):
    """murmur of many voices (filtered noise through formants)"""
    r = np.random.RandomState(seed); x = np.zeros(int(dur * SR), np.float32)
    for i in range(n):
        f0 = r.uniform(90, 220); t = _t(dur)
        v = _saw(f0, dur, 0.3 + 0.2 * r.rand(), 4 + 2 * r.rand())
        gate = (np.sin(2 * np.pi * r.uniform(0.3, 0.8) * t + r.rand() * 6) > r.uniform(-0.2, 0.5)).astype(np.float32)
        gate = _lp(gate, 20)
        v = _formant(v, [(r.uniform(400, 800), 1.0), (r.uniform(1100, 1800), 0.5), (2500, 0.2)], 150) * gate
        x += v / n
    return _norm(_fade(x, 0.3, 0.3), 0.45)

def footstep(seed=0, surface="dirt"):
    r = np.random.RandomState(seed); dur = 0.14
    n = _noise(dur, seed)
    if surface == "wood": x = _lp(n, 500) * 2 + _bp(n, 800, 2000) * 0.5
    elif surface == "stone": x = _bp(n, 1000, 5000) + _lp(n, 300)
    elif surface == "water": x = _bp(n, 800, 6000) * 1.5; dur = 0.25
    else: x = _bp(n, 150, 900) + _bp(n, 2000, 6000) * 0.3
    x = x * _env(len(x), 0.002, 0.08, 0, 0.05, 0.3)
    return _norm(x, 0.35 + 0.1 * r.rand())

def footsteps(dur, rate=2.2, surface="dirt", seed=0, vol=1.0):
    x = np.zeros(int(dur * SR) + SR, np.float32); r = np.random.RandomState(seed); t = 0.0; i = 0
    while t < dur:
        s = footstep(seed * 100 + i, surface) * vol * (0.8 + 0.4 * r.rand())
        a = int(t * SR); x[a:a + len(s)] += s
        t += 1 / rate * (0.95 + 0.1 * r.rand()); i += 1
    return x[:int(dur * SR)]

def hammer(seed=0, wood=True):
    n = _noise(0.25, seed)
    x = (_bp(n, 1200, 4500) if wood else _bp(n, 2500, 9000)) * _env(int(0.25 * SR), 0.001, 0.05, 0, 0.19, 0.2)
    x += _sine(180 if wood else 900, 0.25) * _env(int(0.25 * SR), 0.001, 0.03, 0, 0.1, 0.1) * 0.5
    return _norm(x, 0.7)

def hammering(dur, rate=1.6, seed=0, n_workers=1, wood=True):
    x = np.zeros(int(dur * SR) + SR, np.float32); r = np.random.RandomState(seed)
    for w in range(n_workers):
        t = r.uniform(0, 0.6)
        while t < dur:
            h = hammer(seed + w * 7 + int(t * 10), wood) * (0.6 + 0.4 * r.rand()) / math.sqrt(n_workers)
            a = int(t * SR); x[a:a + len(h)] += h[:len(x) - a]
            t += 1 / rate * (0.9 + 0.2 * r.rand())
    return x[:int(dur * SR)]

def saw(dur=2.0, seed=0):
    t = _t(dur); n = _noise(dur, seed)
    g = 0.5 + 0.5 * np.sin(2 * np.pi * 1.4 * t)
    return _norm(_bp(n, 800, 3500) * g ** 2, 0.4)

def creak(seed=0):
    dur = 0.9; t = _t(dur)
    x = _saw(90 + 30 * np.sin(2 * np.pi * 3 * t).mean(), dur, 0.6, 7) * _env(int(dur * SR), 0.05, 0.3, 0, 0.5, 0.5)
    return _norm(_bp(x, 100, 1800), 0.35)

def door_shut():
    n = _noise(0.6, 21)
    x = _lp(n, 250) * _env(int(0.6 * SR), 0.002, 0.15, 0, 0.4, 0.2) * 3 + _bp(n, 800, 2500) * _env(int(0.6 * SR), 0.001, 0.05, 0, 0.1, 0.1)
    return _norm(x, 0.85)

def splash(seed=0, big=1.0):
    dur = 0.6 + 0.4 * big; n = _noise(dur, seed)
    x = _bp(n, 400, 5000) * _env(int(dur * SR), 0.003, 0.2 * big, 0, dur - 0.25, 0.4) + _lp(n, 200) * _env(int(dur * SR), 0.002, 0.1, 0, 0.1, 0.1) * big
    return _norm(x, 0.6)

def whoosh(seed=0, dur=0.6):
    n = _noise(dur, seed); t = _t(dur)
    f = 300 + 3000 * np.sin(np.pi * t / dur)
    x = np.zeros_like(n)
    for k in range(int(dur * SR) // 2048):
        s = slice(k * 2048, (k + 1) * 2048); x[s] = _bp(n[s], max(100, f[s].mean() * 0.6), f[s].mean() * 1.5)
    return _norm(x * _env(len(x), 0.05, 0.1, 0, dur - 0.2, 0.9), 0.5)

def shimmer(dur=2.5, seed=0, base=880):
    t = _t(dur); x = np.zeros(int(dur * SR), np.float32); r = np.random.RandomState(seed)
    for k, mul in enumerate((1, 1.5, 2, 3, 4, 5)):
        st = k * 0.12; a = int(st * SR)
        y = _sine(base * mul, dur - st) * np.exp(-_t(dur - st) * (1.2 + k * 0.3)) * (0.5 / (k + 1))
        y *= (0.7 + 0.3 * np.sin(2 * np.pi * 6 * _t(dur - st) + k))
        x[a:a + len(y)] += y
    return _norm(_rev(x, 1.2, 0.35), 0.5)

def holy_pad(dur=10.0, seed=0, root=110.0):
    t = _t(dur); x = np.zeros(int(dur * SR), np.float32)
    for m, g in ((1, 0.5), (1.5, 0.25), (2, 0.35), (3, 0.15), (4, 0.1), (5, 0.06)):
        for det in (-0.6, 0, 0.6):
            x += np.sin(2 * np.pi * (root * m + det) * t + 0.3 * np.sin(2 * np.pi * 0.07 * t * m)) * g / 3
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)
    return _norm(_fade(_lp(x, 3000), 1.0, 1.0), 0.35)

def rumble(dur=3.0, seed=0):
    n = _noise(dur, seed); t = _t(dur)
    x = _lp(n, 70) * 3 * (0.6 + 0.4 * np.sin(2 * np.pi * 2.1 * t)) * _env(len(n), 0.3, 0.5, 0, dur - 1.2, 0.8)
    return _norm(x, 0.8)

def light_burst(dur=3.0):
    t = _t(dur); n = _noise(dur, 33)
    sweep = _bp(n, 200, 8000) * _env(len(n), 0.6, 0.2, 0, dur - 1.0, 0.3)
    x = sweep + shimmer(dur, 2, 660)[:len(n)] * 1.5
    return _norm(x, 0.7)

def bite():
    n = _noise(0.35, 41)
    x = _bp(n, 900, 6000) * _env(int(0.35 * SR), 0.002, 0.06, 0, 0.2, 0.15) + _lp(n, 400) * _env(int(0.35 * SR), 0.001, 0.04, 0, 0.05, 0.05)
    return _norm(x, 0.6)

def hiss(dur=1.4, seed=5):
    n = _noise(dur, seed); t = _t(dur)
    return _norm(_bp(n, 3000, 9000) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * _env(len(n), 0.1, 0.2, 0, dur - 0.5, 0.8), 0.4)

def heartbeat(dur=4.0, bpm=70):
    x = np.zeros(int(dur * SR), np.float32); t = 0.0
    while t < dur - 0.3:
        for off, g in ((0, 1.0), (0.18, 0.7)):
            a = int((t + off) * SR); y = _sine(55, 0.2) * _env(int(0.2 * SR), 0.005, 0.1, 0, 0.09, 0.2) * g
            x[a:a + len(y)] += y
        t += 60 / bpm
    return _norm(x, 0.7)

def strike():
    """blunt hit (Cain) - heavy thud, not gory"""
    n = _noise(0.5, 50)
    x = _lp(n, 300) * _env(int(0.5 * SR), 0.001, 0.12, 0, 0.3, 0.2) * 3 + _bp(n, 1000, 3000) * _env(int(0.5 * SR), 0.001, 0.03, 0, 0.05, 0.05)
    return _norm(x, 0.8)

def stone_drop(seed=0):
    n = _noise(0.4, seed)
    return _norm(_bp(n, 300, 2500) * _env(int(0.4 * SR), 0.001, 0.1, 0, 0.25, 0.2), 0.6)

def wings(dur=1.2, seed=0, rate=7.0):
    t = _t(dur); n = _noise(dur, seed)
    g = np.clip(np.sin(2 * np.pi * rate * t), 0, 1) ** 2
    return _norm(_bp(n, 300, 2500) * g * _env(len(n), 0.05, 0.1, 0, dur - 0.3, 0.9), 0.4)

# animals (stylised, pixel-friendly)
def bird_chirp(seed=0):
    r = np.random.RandomState(seed); dur = 0.12 + 0.1 * r.rand(); t = _t(dur)
    f0 = 2200 + 1800 * r.rand(); f = f0 + 1200 * np.sin(np.pi * t / dur * (1 + r.randint(0, 2)))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.03, 0, dur - 0.05, 0.6)
    y = x.astype(np.float32)
    if r.rand() < 0.6:  # double
        y = np.concatenate([y, np.zeros(int(0.05 * SR), np.float32), y * 0.8])
    return _norm(y, 0.5)

def dove(seed=0):
    dur = 1.2; t = _t(dur)
    f = 520 - 80 * t; g = (np.sin(2 * np.pi * 2.2 * t) > -0.3).astype(np.float32)
    x = _lp(np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * g, 1200) * _env(len(t), 0.05, 0.2, 0, 0.8, 0.8)
    return _norm(x, 0.45)

def raven(seed=0):
    dur = 0.45; t = _t(dur)
    x = _saw(220 - 60 * t.mean(), dur, 1.5, 24) * _env(len(t), 0.02, 0.1, 0, 0.3, 0.6)
    x = _formant(x, [(600, 1.0), (1300, 0.6), (2600, 0.3)], 200)
    y = np.concatenate([x, np.zeros(int(0.12 * SR), np.float32), x * 0.85])
    return _norm(y, 0.5)

def sheep_baa(seed=0):
    dur = 0.8; t = _t(dur)
    x = _saw(300 + 20 * np.sin(2 * np.pi * 1 * t).mean(), dur, 1.2, 9) * _env(len(t), 0.05, 0.3, 0, 0.4, 0.7)
    return _norm(_formant(x, [(650, 1.0), (1200, 0.7), (2400, 0.3)], 180), 0.45)

def goat(seed=0):
    dur = 0.6; t = _t(dur)
    x = _saw(420, dur, 2.0, 14) * _env(len(t), 0.03, 0.2, 0, 0.3, 0.6)
    return _norm(_formant(x, [(800, 1.0), (1600, 0.6)], 200), 0.4)

def cow(seed=0):
    dur = 1.4; t = _t(dur)
    f = 110 + 25 * np.sin(np.pi * t / dur)
    x = (2 * ((np.cumsum(f) / SR) % 1) - 1).astype(np.float32) * _env(len(t), 0.15, 0.4, 0, 0.7, 0.8)
    return _norm(_formant(x, [(300, 1.0), (700, 0.7), (1400, 0.3)], 150), 0.5)

def lion_roar(seed=0):
    dur = 1.8; t = _t(dur); n = _noise(dur, seed)
    f = 70 + 30 * np.sin(np.pi * t / dur)
    x = (2 * ((np.cumsum(f) / SR) % 1) - 1).astype(np.float32) * 0.7 + _bp(n, 150, 900) * 0.8
    x = x * _env(len(t), 0.15, 0.5, 0, 1.0, 0.8)
    return _norm(_formant(x, [(250, 1.0), (600, 0.8), (1200, 0.5)], 180) + _lp(x, 200) * 0.6, 0.7)

def elephant(seed=0):
    dur = 1.5; t = _t(dur)
    f = 300 + 400 * np.sin(np.pi * t / dur) ** 2
    x = (2 * ((np.cumsum(f) / SR) % 1) - 1).astype(np.float32) * _env(len(t), 0.1, 0.4, 0, 0.8, 0.7)
    return _norm(_formant(x, [(500, 1.0), (1100, 0.8), (2200, 0.4)], 220), 0.6)

def horse(seed=0):
    dur = 1.0; t = _t(dur)
    x = _saw(500, dur, 3.0, 11 + 10 * t.mean()) * _env(len(t), 0.03, 0.3, 0, 0.5, 0.7)
    return _norm(_formant(x, [(900, 1.0), (1700, 0.7), (3000, 0.3)], 250), 0.45)

def wolf(seed=0):
    dur = 2.2; t = _t(dur)
    f = 380 + 180 * np.sin(np.pi * t / dur) - 60 * t
    x = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * _env(len(t), 0.3, 0.5, 0, 1.2, 0.8)
    return _norm(_rev(x, 1.0, 0.3), 0.4)

def monkey(seed=0):
    r = np.random.RandomState(seed); x = []
    for i in range(4):
        d = 0.12; t = _t(d); f = 900 + 500 * np.sin(np.pi * t / d)
        x.append(np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * _env(len(t), 0.01, 0.05, 0, 0.05, 0.5)); x.append(np.zeros(int(0.06 * SR), np.float32))
    return _norm(np.concatenate(x), 0.4)

def frog(seed=0):
    dur = 0.3; t = _t(dur)
    x = _saw(140, dur, 1.0, 30) * _env(len(t), 0.02, 0.1, 0, 0.15, 0.6)
    return _norm(_formant(x, [(400, 1.0), (900, 0.5)], 150), 0.35)

def snake_rattle(dur=1.0): return hiss(dur, 7)

def eagle(seed=0):
    dur = 0.7; t = _t(dur); f = 2600 - 900 * t / dur
    x = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * _env(len(t), 0.03, 0.2, 0, 0.4, 0.6)
    return _norm(_rev(x, 0.8, 0.3), 0.4)

ANIMALS = dict(bird=bird_chirp, dove=dove, raven=raven, sheep=sheep_baa, goat=goat, cow=cow, lion=lion_roar, elephant=elephant,
               horse=horse, wolf=wolf, monkey=monkey, frog=frog, eagle=eagle, camel=goat, ox=cow, pig=cow, giraffe=horse, bear=lion_roar)
ONESHOT = dict(thunder=thunder, crack=crack, hammer=hammer, creak=creak, door=door_shut, splash=splash, whoosh=whoosh,
               shimmer=shimmer, rumble=rumble, light=light_burst, bite=bite, hiss=hiss, strike=strike, stone=stone_drop, wings=wings,
               heartbeat=heartbeat, saw=saw)
AMBIENT = dict(rain=rain, wind=wind, waves=waves, river=river, fire=fire, forest=forest, night=night, desert=desert, crowd=crowd, holy=holy_pad)

def get(name, **kw):
    key = (name, tuple(sorted(kw.items())))
    if key in _CACHE: return _CACHE[key]
    if name in ANIMALS: x = ANIMALS[name](**kw)
    elif name in ONESHOT: x = ONESHOT[name](**kw)
    elif name in AMBIENT: x = AMBIENT[name](**kw)
    else: raise KeyError(name)
    _CACHE[key] = x
    return x

def loop(name, dur, **kw):
    """ambient loop of arbitrary length with crossfaded tiles"""
    tile = get(name, dur=12.0, **kw) if "dur" not in kw else get(name, **kw)
    n = int(dur * SR); out = np.zeros(n + len(tile), np.float32); pos = 0; k = 0
    xf = int(1.0 * SR)
    while pos < n:
        t2 = np.roll(tile, k * 7919) if k else tile
        out[pos:pos + len(t2)] += t2
        pos += len(t2) - xf; k += 1
    return out[:n]

if __name__ == "__main__":
    import soundfile as sf, sys
    names = sys.argv[2:] or list(ANIMALS) + list(ONESHOT)
    parts = []
    for nm in names:
        x = get(nm); parts.append(x); parts.append(np.zeros(int(0.4 * SR), np.float32))
    sf.write(sys.argv[1], np.concatenate(parts), SR); print("ok", names)
