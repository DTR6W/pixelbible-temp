"""Genesis cast: extra character specs on top of px/chars2 + simple pixel animals for the ark."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "px"))
import chars2
import eden_sprites as es
from chars2 import R, _r, SPECS

R["fig"] = _r((40, 80, 30), (70, 120, 46), (104, 160, 66), (150, 200, 100))
R["hide"] = _r((70, 44, 30), (110, 72, 46), (150, 104, 68), (190, 140, 96))
R["olive"] = _r((60, 70, 40), (96, 110, 60), (136, 150, 86), (176, 190, 120))
R["rust"] = _r((90, 40, 24), (140, 66, 36), (186, 100, 54), (220, 140, 84))
R["slate"] = _r((40, 46, 60), (70, 80, 100), (110, 122, 146), (156, 170, 192))
R["sand"] = _r((130, 106, 70), (184, 154, 104), (222, 194, 140), (246, 228, 184))
R["mud"] = _r((60, 44, 30), (96, 72, 48), (130, 100, 66), (160, 128, 90))
R["pine"] = _r((20, 52, 36), (34, 84, 54), (58, 120, 76), (98, 160, 108))

SPECS.update({
 # after the fall: garments of skin
 "Adam": dict(robe="hide", w=(12, 15), hem=100, sash="brown", skin="tan", hair="hair", style="curly", beard=("hair", 5, 6), prop="none", brow="hair", eyes=(36, 24, 20), sleeve="bare", trim="hide"),
 "Eve": dict(robe="hide", w=(11, 14), hem=104, sash="brown", skin="fair", hair="auburn", style="long", beard=None, prop="none", brow="auburn", eyes=(50, 32, 26), sleeve="bare", trim="hide", kind=True),
 "Cain": dict(robe="rust", w=(12, 15), hem=100, sash="brown", skin="tan", hair="hair", style="wild", beard=("hair", 4, 5), prop="none", brow="hair", eyes=(30, 20, 18), sleeve="short", trim="brown"),
 "Abel": dict(robe="linen", w=(11, 14), hem=100, mantle="cream", sash="brown", skin="tan", hair="brown", style="curly", beard=None, prop="crook", brow="brown", eyes=(36, 24, 20), sleeve="short", trim="linen", kind=True),
 "Seth": dict(robe="olive", w=(11, 14), hem=102, sash="brown", skin="tan", hair="hair", style="curly", beard=None, prop="none", brow="hair", eyes=(36, 24, 20), sleeve="short", trim="linen", kind=True),
 "Enoch": dict(robe="white", w=(12, 16), hem=109, sash="linen", skin="tan", hair="salt", style="long", beard=("salt", 6, 8), prop="staff", brow="salt", eyes=(50, 40, 34), sleeve="long", trim="cream", kind=True),
 "Noah": dict(robe="indigo", w=(13, 18), hem=109, mantle="camel", sash="rope", skin="tan", hair="white", style="long", beard=("white", 9, 14), prop="staff", brow="white", eyes=(50, 44, 40), sleeve="long", trim="linen", old=True, kind=True),
 "Naamah": dict(robe="teal", w=(11, 16), hem=109, skin="tan", hair="gray", style="veil", veil="cream", inner="linen", beard=None, prop="none", brow="gray", eyes=(50, 32, 26), sleeve="long", trim="cream", kind=True),
 "Shem": dict(robe="ochre", w=(12, 15), hem=104, sash="brown", skin="tan", hair="hair", style="sides", beard=("hair", 5, 6), prop="none", brow="hair", eyes=(36, 24, 20), sleeve="short", trim="linen"),
 "Ham": dict(robe="terra", w=(12, 15), hem=104, sash="brown", skin="dark", hair="black", style="curly", beard=("black", 4, 5), prop="none", brow="black", eyes=(20, 14, 14), sleeve="short", trim="linen"),
 "Japheth": dict(robe="sea", w=(12, 15), hem=104, sash="brown", skin="fair", hair="auburn", style="cap", beard=("auburn", 4, 5), prop="none", brow="auburn", eyes=(50, 40, 34), sleeve="short", trim="linen"),
 "Nimrod": dict(robe="crimson", w=(14, 18), hem=100, mantle="gold", sash="gold", skin="tan", hair="black", style="crown", beard=("black", 7, 9), prop="none", brow="black", eyes=(20, 14, 14), sleeve="bare", trim="gold", big=True),
 "Worker": dict(robe="sand", w=(12, 15), hem=98, sash="rope", skin="tan", hair="hair", style="cap", beard=None, prop="none", brow="hair", eyes=(36, 24, 20), sleeve="bare", trim="mud"),
 "Worker2": dict(robe="mud", w=(12, 15), hem=98, sash="rope", skin="dark", hair="black", style="bald", beard=("black", 4, 5), prop="none", brow="black", eyes=(20, 14, 14), sleeve="bare", trim="sand"),
 "Worker3": dict(robe="slate", w=(12, 15), hem=98, sash="rope", skin="fair", hair="brown", style="curly", beard=None, prop="none", brow="brown", eyes=(36, 24, 20), sleeve="bare", trim="sand"),
 "Mocker": dict(robe="plum", w=(12, 16), hem=104, sash="brown", skin="tan", hair="gray", style="hat", beard=("gray", 5, 7), prop="none", brow="gray", eyes=(40, 34, 30), sleeve="long", trim="linen"),
 "Mocker2": dict(robe="teal", w=(12, 16), hem=104, sash="brown", skin="fair", hair="auburn", style="wild", beard=None, prop="none", brow="auburn", eyes=(40, 34, 30), sleeve="short", trim="linen"),
 "Cherub": dict(robe="white", w=(12, 17), hem=109, sash="gold", skin="fair", hair="gold", style="long", beard=None, prop="none", brow="gold", eyes=(60, 110, 170), sleeve="long", trim="gold", wings=True, halo=True, aura=True, float=True),
 "Lamech": dict(robe="black", w=(13, 17), hem=104, mantle="crimson", sash="gold", skin="tan", hair="black", style="wild", beard=("black", 7, 9), prop="none", brow="black", eyes=(20, 14, 14), sleeve="short", trim="gold"),
 "Terah": dict(robe="gray", w=(13, 17), hem=109, mantle="brown", sash="rope", skin="tan", hair="white", style="bald", beard=("white", 8, 12), prop="staff", brow="white", eyes=(50, 44, 40), sleeve="long", trim="linen", old=True),
 "Abram": dict(robe="camel", w=(12, 16), hem=109, mantle="ivory", sash="brown", skin="tan", hair="brown", style="long", beard=("brown", 6, 8), prop="staff", brow="brown", eyes=(36, 24, 20), sleeve="long", trim="linen", kind=True),
})

_CACHE = {}
ALIAS = {}

def sprite(name, t, amp=0.0, blink=False, pose=None, walk=0.0, look=0.0):
    """RGBA numpy 100x120 (or Eden nude-ish variants for Adam0/Eve0)"""
    name = ALIAS.get(name, name)
    if name in ("Adam0", "Eve0"):
        return es.human(name[:-1], t, walk, amp, pose, look, blink)
    if name in ("lion", "sheep", "deer", "bunny"):
        return es.SP[name](t, walk)
    return chars2.draw(name, t, amp, blink, pose, walk=walk, look=look)

# ------------------------------------------------------------------ pixel animals (side view, 2-tone), drawn into a 64x48 RGBA
def _blank(w=64, h=48): return Image.new("RGBA", (w, h), (0, 0, 0, 0))
def _leg(d, x, y0, y1, c, ph, k, sw=3):
    dx = int(round(math.sin(ph + k) * sw)); d.line([(x, y0), (x + dx, y1)], fill=c, width=3)

def animal(kind, t=0.0, walk=1.0):
    key = (kind, int(t * 8) % 16, walk > 0)
    if key in _CACHE: return _CACHE[key]
    im = _blank(); d = ImageDraw.Draw(im); ph = t * 5.0; bob = int(abs(math.sin(ph)) * walk * 1.2)
    o = (22, 12, 18)
    if kind == "ox":
        c, c2 = (120, 70, 40), (170, 110, 70)
        for i, x in enumerate((16, 24, 40, 48)): _leg(d, x, 30 - bob, 44, c, ph, (0, math.pi, math.pi, 0)[i], 3 * walk)
        d.rounded_rectangle([10, 16 - bob, 54, 34 - bob], 8, fill=c, outline=o); d.ellipse([46, 10 - bob, 62, 26 - bob], fill=c2, outline=o)
        d.line([(48, 12 - bob), (44, 6 - bob)], fill=(230, 220, 200), width=2); d.line([(58, 12 - bob), (62, 6 - bob)], fill=(230, 220, 200), width=2)
        d.point((57, 16 - bob), fill=o)
    elif kind == "horse":
        c, c2 = (150, 100, 60), (90, 60, 36)
        for i, x in enumerate((16, 22, 42, 48)): _leg(d, x, 28 - bob, 45, c, ph, (0, math.pi, math.pi, 0)[i], 4 * walk)
        d.rounded_rectangle([10, 14 - bob, 50, 30 - bob], 7, fill=c, outline=o); d.polygon([(46, 16 - bob), (58, 4 - bob), (63, 8 - bob), (56, 22 - bob)], fill=c, outline=o)
        d.line([(48, 14 - bob), (56, 4 - bob)], fill=c2, width=3); d.line([(10, 18 - bob), (4, 30 - bob)], fill=c2, width=2)
        d.point((60, 8 - bob), fill=o)
    elif kind == "camel":
        c = (200, 160, 100)
        for i, x in enumerate((16, 22, 42, 48)): _leg(d, x, 28 - bob, 46, c, ph, (0, math.pi, math.pi, 0)[i], 3 * walk)
        d.rounded_rectangle([10, 16 - bob, 50, 30 - bob], 7, fill=c, outline=o); d.ellipse([24, 6 - bob, 40, 20 - bob], fill=c, outline=o)
        d.line([(48, 18 - bob), (56, 4 - bob)], fill=c, width=5); d.ellipse([53, 1 - bob, 63, 9 - bob], fill=c, outline=o); d.point((60, 4 - bob), fill=o)
    elif kind == "elephant":
        c = (120, 120, 135)
        for i, x in enumerate((14, 24, 40, 50)): _leg(d, x, 32 - bob, 46, c, ph, (0, math.pi, math.pi, 0)[i], 2 * walk)
        d.rounded_rectangle([6, 8 - bob, 54, 36 - bob], 12, fill=c, outline=o); d.ellipse([44, 6 - bob, 64, 28 - bob], fill=c, outline=o)
        d.ellipse([40, 10 - bob, 52, 26 - bob], fill=(150, 150, 165), outline=o)
        sw = int(math.sin(t * 2) * 3); d.line([(60, 20 - bob), (62 + sw, 40 - bob)], fill=c, width=4); d.point((58, 14 - bob), fill=o)
        d.line([(60, 24 - bob), (63, 30 - bob)], fill=(240, 236, 220), width=2)
    elif kind == "giraffe":
        c, c2 = (230, 190, 110), (150, 100, 50)
        for i, x in enumerate((20, 26, 40, 46)): _leg(d, x, 28 - bob, 47, c, ph, (0, math.pi, math.pi, 0)[i], 3 * walk)
        d.rounded_rectangle([16, 18 - bob, 50, 30 - bob], 6, fill=c, outline=o); d.line([(46, 20 - bob), (54, 0 - bob)], fill=c, width=5)
        d.ellipse([50, -4 - bob, 62, 4 - bob], fill=c, outline=o); d.point((59, -1 - bob), fill=o)
        for sx, sy in ((22, 22), (30, 26), (38, 21), (44, 26), (48, 14)): d.rectangle([sx, sy - bob, sx + 2, sy + 2 - bob], fill=c2)
    elif kind == "goat":
        c = (230, 230, 225)
        for i, x in enumerate((22, 28, 40, 46)): _leg(d, x, 32 - bob, 45, (60, 60, 60), ph, (0, math.pi, math.pi, 0)[i], 3 * walk)
        d.rounded_rectangle([18, 22 - bob, 50, 34 - bob], 6, fill=c, outline=o); d.ellipse([46, 16 - bob, 60, 28 - bob], fill=c, outline=o)
        d.line([(54, 16 - bob), (58, 8 - bob)], fill=(120, 100, 80), width=2); d.line([(50, 16 - bob), (48, 9 - bob)], fill=(120, 100, 80), width=2); d.point((57, 21 - bob), fill=o)
    elif kind == "wolf":
        c = (110, 110, 120)
        for i, x in enumerate((18, 24, 40, 46)): _leg(d, x, 30 - bob, 44, c, ph, (0, math.pi, math.pi, 0)[i], 4 * walk)
        d.rounded_rectangle([12, 18 - bob, 50, 32 - bob], 6, fill=c, outline=o); d.polygon([(46, 18 - bob), (62, 20 - bob), (58, 28 - bob), (46, 30 - bob)], fill=c, outline=o)
        d.polygon([(48, 18 - bob), (50, 12 - bob), (53, 18 - bob)], fill=c); d.line([(12, 22 - bob), (4, 16 - bob)], fill=c, width=3); d.point((58, 22 - bob), fill=o)
    elif kind == "pig":
        c = (240, 170, 160)
        for i, x in enumerate((18, 24, 38, 44)): _leg(d, x, 34 - bob, 44, c, ph, (0, math.pi, math.pi, 0)[i], 2 * walk)
        d.rounded_rectangle([12, 22 - bob, 50, 38 - bob], 8, fill=c, outline=o); d.ellipse([44, 22 - bob, 60, 36 - bob], fill=c, outline=o); d.rectangle([57, 28 - bob, 61, 32 - bob], fill=(210, 130, 120)); d.point((54, 27 - bob), fill=o)
    elif kind == "monkey":
        c = (120, 80, 50)
        d.ellipse([20, 24 - bob, 40, 44 - bob], fill=c, outline=o); d.ellipse([30, 12 - bob, 46, 28 - bob], fill=c, outline=o); d.ellipse([34, 16 - bob, 44, 26 - bob], fill=(220, 180, 150))
        d.line([(22, 36 - bob), (14, 16 - bob + int(4 * math.sin(t * 6)))], fill=c, width=3); d.point((40, 20 - bob), fill=o); d.point((37, 20 - bob), fill=o)
        d.line([(26, 42 - bob), (24, 47)], fill=c, width=3); d.line([(34, 42 - bob), (36, 47)], fill=c, width=3)
    elif kind == "bear":
        c = (90, 60, 40)
        for i, x in enumerate((16, 24, 40, 48)): _leg(d, x, 30 - bob, 46, c, ph, (0, math.pi, math.pi, 0)[i], 2 * walk)
        d.rounded_rectangle([8, 12 - bob, 54, 36 - bob], 10, fill=c, outline=o); d.ellipse([46, 10 - bob, 64, 28 - bob], fill=c, outline=o); d.ellipse([48, 6 - bob, 54, 12 - bob], fill=c, outline=o); d.point((59, 18 - bob), fill=o); d.point((62, 22 - bob), fill=(30, 20, 20))
    elif kind == "dove":
        im = _blank(24, 20); d = ImageDraw.Draw(im); w = int(math.sin(t * 14) * 5)
        d.ellipse([6, 8, 18, 16], fill=(250, 250, 255), outline=o); d.ellipse([15, 5, 22, 11], fill=(250, 250, 255), outline=o)
        d.polygon([(10, 10), (4, 6 - w), (14, 10)], fill=(230, 230, 240), outline=o); d.polygon([(2, 12), (8, 12), (6, 15)], fill=(200, 200, 215)); d.point((20, 7), fill=o); d.line([(22, 8), (24, 8)], fill=(240, 160, 60))
    elif kind == "raven":
        im = _blank(24, 20); d = ImageDraw.Draw(im); w = int(math.sin(t * 12) * 6)
        d.ellipse([6, 8, 18, 16], fill=(20, 18, 28), outline=o); d.ellipse([15, 5, 22, 11], fill=(20, 18, 28), outline=o)
        d.polygon([(10, 10), (3, 5 - w), (15, 10)], fill=(40, 36, 50), outline=o); d.polygon([(2, 12), (8, 12), (6, 16)], fill=(30, 28, 40)); d.point((20, 7), fill=(230, 230, 230)); d.line([(22, 8), (24, 8)], fill=(60, 60, 60))
    _CACHE[key] = im
    return im

ARK_ANIMALS = ["elephant", "giraffe", "lion", "horse", "ox", "camel", "bear", "sheep", "goat", "deer", "wolf", "pig", "monkey", "bunny"]
