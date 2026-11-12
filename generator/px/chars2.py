import math, sys
import numpy as np
from PIL import Image
import giant as g
from giant import ell, cap, put, R, OUT, W, H
from elder import body

def _r(*c): return [tuple(x) for x in c]
R["tan"] = _r((96,56,40),(146,92,62),(190,130,92),(224,170,128))
R["fair"] = _r((120,70,54),(176,112,80),(222,160,120),(246,198,160))
R["dark"] = _r((60,34,28),(100,60,44),(140,88,62),(178,120,88))
R["white"] = _r((120,120,136),(176,178,194),(226,228,238),(252,252,255))
R["sky"] = _r((40,60,84),(76,104,136),(120,150,182),(168,194,220))
R["ochre"] = _r((96,60,20),(150,100,34),(200,146,58),(240,194,104))
R["terra"] = _r((70,32,24),(120,60,40),(166,92,58),(206,128,84))
R["azure"] = _r((20,44,90),(34,76,150),(62,112,196),(120,164,230))
R["rose"] = _r((120,60,80),(176,98,118),(218,140,156),(246,186,196))
R["cream"] = _r((130,114,98),(196,180,156),(238,226,200),(255,250,236))
R["purple"] = _r((40,20,70),(80,42,128),(120,76,170),(166,120,214))
R["crimson"] = _r((80,16,28),(140,28,40),(190,52,56),(226,96,86))
R["sea"] = _r((30,60,64),(54,100,104),(90,140,140),(136,184,176))
R["salt"] = _r((70,64,62),(114,104,98),(160,148,138),(204,192,180))
R["stone"] = _r((70,72,82),(110,114,126),(156,160,172),(204,208,218))
R["auburn"] = _r((44,22,16),(92,48,30),(140,78,44),(180,110,64))
R["leaf"] = _r((24,70,34),(40,110,52),(66,150,70),(110,190,100))
R["linen"] = _r((104,86,66),(156,132,98),(204,178,138),(238,218,176))
R["gray"] = _r((66,62,70),(108,104,112),(156,152,160),(204,200,208))
R["brown"] = _r((50,30,22),(96,62,42),(142,98,64),(184,138,96))
R["gold"] = _r((120,76,16),(190,134,30),(240,190,60),(255,232,130))
R["lapis"] = _r((16,30,90),(30,56,160),(52,96,214),(110,150,250))
R["ivory"] = _r((150,140,126),(210,200,184),(244,238,224),(255,255,250))
R["scarlet"] = _r((90,10,16),(160,22,28),(210,44,40),(244,94,76))
R["plate"] = _r((60,66,86),(112,122,148),(170,182,204),(228,238,252))
R["black"] = _r((10,10,14),(24,22,30),(44,40,52),(70,66,80))
R["wing"] = _r((170,186,226),(214,224,246),(244,248,255),(255,255,255))

SPECS = {
 "Jesus": dict(robe="ivory", w=(12, 18), hem=109, sash="scarlet", skin="fair", hair="auburn", style="long", beard=("auburn", 6, 7), prop="none", brow="auburn", eyes=(70,44,28), sleeve="long", trim="gold", aura=True, kind=True),
 "Moses": dict(robe="sky", w=(13, 19), hem=109, mantle="ochre", sash="brown", skin="tan", hair="white", style="long", beard=("white", 8, 13), prop="tablets", brow="gray", eyes=(50,40,34), sleeve="long", trim="ochre"),
 "David": dict(robe="terra", w=(11, 14), hem=99, sash="brown", skin="tan", hair="hair", style="curly", beard=None, prop="sling", brow="hair", eyes=(36,24,20), sleeve="short", trim="ochre", young=True),
 "Mary": dict(robe="rose", w=(11, 17), hem=109, skin="tan", hair="hair", style="veil", beard=None, prop="none", veil="azure", inner="cream", brow="hair", eyes=(50,32,26), sleeve="long", trim="cream", kind=True),
 "Solomon": dict(robe="purple", w=(13, 19), hem=109, mantle="crimson", sash="gold", skin="tan", hair="hair", style="crown", beard=("hair", 7, 8), prop="scepter", brow="hair", eyes=(36,24,20), sleeve="long", trim="gold"),
 "Peter": dict(robe="sea", w=(13, 16), hem=102, sash="brown", skin="tan", hair="salt", style="sides", beard=("salt", 8, 9), prop="rod", brow="salt", eyes=(50,40,34), sleeve="short", trim="linen"),
 "Angel": dict(robe="white", w=(12, 17), hem=109, sash="gold", skin="fair", hair="gold", style="long", beard=None, prop="none", brow="gold", eyes=(60,110,170), sleeve="long", trim="gold", wings=True, halo=True, aura=True, kind=True, float=True),
 "King": dict(robe="lapis", w=(13, 19), hem=109, mantle="gold", sash="scarlet", skin="dark", hair="black", style="nemes", beard=("black", 3, 9), prop="crook", brow="black", eyes=(20,14,14), sleeve="short", trim="gold", collar=True),
 "Boy": dict(robe="linen", w=(9, 12), hem=100, sash="brown", skin="tan", hair="hair", style="curly", beard=None, prop="none", brow="hair", eyes=(36,24,20), sleeve="short", trim="linen", kid=True),
 "Elder": dict(robe="brown", w=(13, 17), hem=109, mantle="salt", sash="rope", skin="fair", hair="white", style="bald", beard=("white", 9, 15), prop="staff", brow="white", eyes=(50,44,40), sleeve="long", trim="linen", old=True),
 "Soldier": dict(robe="scarlet", w=(11, 15), hem=92, mantle="scarlet", sash="brown", skin="tan", hair="hair", style="helmet", beard=None, prop="spear", brow="hair", eyes=(36,24,20), sleeve="armor", trim="plate", armor=True),
}
SPECS.update({
 "Paul": dict(robe="plum", w=(12, 16), hem=109, mantle="gray", sash="brown", skin="tan", hair="gray", style="bald", beard=("gray", 6, 9), prop="scroll", brow="gray", eyes=(30,24,20), sleeve="long", trim="linen", old=False),
 "Queen": dict(robe="scarlet", w=(11, 16), hem=109, sash="gold", skin="tan", hair="black", style="longcrown", beard=None, prop="none", brow="black", eyes=(30,20,18), sleeve="long", trim="gold", kind=True),
 "Shepherd": dict(robe="linen", w=(11, 14), hem=102, mantle="ivory", sash="brown", skin="tan", hair="brown", style="curly", beard=("brown", 5, 5), prop="crook", brow="brown", eyes=(36,24,20), sleeve="short", trim="linen"),
 "John": dict(robe="camel", w=(12, 15), hem=102, sash="brown", skin="tan", hair="auburn", style="wild", beard=("auburn", 8, 12), prop="staff", brow="auburn", eyes=(30,24,20), sleeve="short", trim="brown"),
 "Priest": dict(robe="white", w=(13, 18), hem=109, mantle="lapis", sash="gold", skin="fair", hair="white", style="turban", beard=("white", 7, 11), prop="none", brow="white", eyes=(50,44,40), sleeve="long", trim="gold", collar=True),
 "Woman": dict(robe="teal", w=(11, 16), hem=109, sash="brown", skin="tan", hair="brown", style="veil", veil="ochre", inner="cream", beard=None, prop="jar", brow="brown", eyes=(50,32,26), sleeve="long", trim="cream", kind=True),
 "Fisherman": dict(robe="sky", w=(12, 15), hem=100, sash="brown", skin="tan", hair="brown", style="cap", beard=("brown", 6, 6), prop="net", brow="brown", eyes=(36,24,20), sleeve="short", trim="linen"),
 "Pharisee": dict(robe="blackhat", w=(12, 17), hem=109, mantle="white", sash="gold", skin="fair", hair="gray", style="hat", beard=("gray", 7, 10), prop="scroll", brow="gray", eyes=(40,34,30), sleeve="long", trim="gold"),
 "Governor": dict(robe="toga", w=(13, 18), hem=109, mantle="scarlet", sash="gold", skin="fair", hair="gray", style="laurel", beard=None, prop="none", brow="gray", eyes=(50,44,40), sleeve="long", trim="scarlet"),
 "Samson": dict(robe="brown", w=(14, 17), hem=90, sash="camel", skin="tan", hair="auburn", style="long", beard=("auburn", 6, 8), prop="none", brow="auburn", eyes=(36,24,20), sleeve="bare", trim="brown", big=True),
})
R["plum"] = _r((44,24,52),(84,48,96),(122,80,136),(164,120,176))
R["camel"] = _r((90,64,34),(140,100,56),(184,142,84),(222,184,124))
R["teal"] = _r((20,64,70),(36,104,110),(64,148,150),(110,192,188))
R["blackhat"] = _r((12,12,18),(30,30,40),(52,52,66),(80,80,96))
R["toga"] = _r((150,144,136),(206,200,190),(240,236,228),(255,255,250))
R["leafg"] = _r((40,90,36),(70,140,56),(110,184,84),(160,220,120))
R["rope"] = _r((70,28,26),(120,50,40),(160,78,56),(196,110,80))

def DK(r): return r[:1] * 4
def _shadow():
    for y in range(111, 119):
        for x in range(26, 76):
            nx, ny = (x - 50) / 25, (y - 115) / 4
            if nx * nx + ny * ny <= 1 and (x + y) % 2 == 0: put(x, y, R["shadow"][0])

def _face(sp, hy, sk, lk, blink, amp, look_y=0):
    old = sp.get("old"); kid = sp.get("kid")
    ec = sp["eyes"]; bc = R[sp["brow"]]
    for ex in (45, 55):
        e = ex + lk
        if blink:
            for dx in range(-1, 2): put(e + dx, hy + 3, DK(sk)[0] if old is None else sk[0])
            continue
        w = 2 if kid else 1
        for dx in range(-2, 3): put(ex + dx, hy + 2, (246, 242, 236)); put(ex + dx, hy + 3, (246, 242, 236))
        ix = max(-1, min(0, round(lk * 0.7)))
        for dy in (2, 3):
            put(e + ix, hy + dy, ec); put(e + ix + 1, hy + dy, ec)
        put(e + ix, hy + 2, (255, 255, 255))
        put(ex - 2, hy + 3, sk[1]); put(ex + 2, hy + 3, sk[1])
    # brows
    kind = sp.get("kind")
    for ex, s in ((45, -1), (55, 1)):
        for dx in range(-2, 3):
            tilt = (1 if (dx * s > 0 and kind) else 0)
            put(ex + dx, hy - 1 - tilt if not old else hy - 1, bc[1]); 
            if old and dx * s > 0: put(ex + dx, hy - 2, bc[2])
    # nose
    put(50, hy + 4, sk[1]); put(50, hy + 5, sk[0]); put(49, hy + 5, sk[1]); put(51, hy + 5, sk[1]); put(49, hy + 3, sk[3])
    # cheeks
    if not sp.get("beard") or kid:
        for cx_ in (41, 59): put(cx_, hy + 5, (236, 140, 130)); put(cx_ + (1 if cx_ < 50 else -1), hy + 5, (236, 140, 130))
    # mouth
    mh = int(amp * 3.2)
    my = hy + 8 if not sp.get("beard") else hy + 8
    if mh > 0:
        for yy in range(my, my + mh + 1):
            for xx in range(48, 53): put(xx, yy, (96, 28, 40))
        for xx in range(49, 52): put(xx, my + mh, (214, 96, 104))
        for xx in range(48, 53): put(xx, my - 1, (170, 70, 74))
    else:
        for xx, yy in ((47, my - 1), (48, my), (49, my), (50, my), (51, my), (52, my), (53, my - 1)): put(xx, yy, (150, 54, 60) if not sp.get("beard") else (90, 40, 44))

def draw(name, t=0.0, amp=0.0, blink=False, pose=None, walk=0.0, look=0.0):
    sp = SPECS[name]; c = g.canvas; c[:] = 0
    pose = pose or {}
    ph = t * 5.0
    bob = round(math.sin(t * 2.2) * 0.8 - abs(math.sin(ph)) * walk * 1.6)
    if sp.get("float"): bob += round(math.sin(t * 1.8) * 1.5) - 3
    skin = R[sp["skin"]]; robe = R[sp["robe"]]; hem = sp["hem"]
    kid = sp.get("kid")
    sh = 0 if not kid else 6
    _shadow()
    lk = int(round(look * 1.6))
    # --- back layers
    if sp.get("wings"):
        fl = math.sin(t * 2.6) * 3
        for s_ in (-1, 1):
            for i, (dx, dy, L, r0) in enumerate(((10, 46, 40, 6), (12, 52, 34, 5.5), (14, 58, 27, 5))):
                a = math.radians(-62 + i * 22 + fl * 2)
                p0 = (50 + s_ * dx, dy + bob - 4)
                p1 = (p0[0] + s_ * L * math.cos(a) * 0.9, p0[1] + L * math.sin(a) * -0.5 - 6 + i * 4)
                cap(p0, p1, r0, 1.2, R["wing"])
    if sp.get("mantle") and name in ("King", "Soldier"):
        body(48 + bob, 100, 15, 19, R[sp["mantle"]] if name == "Soldier" else R["gold"])
    if sp["prop"] in ("spear",):
        cap((84, 4 + bob), (84, 114), 1.6, 1.6, R["wood"]); cap((84, 0 + bob), (84, 14 + bob), 2.4, 0.6, R["steel"])
    # --- legs/feet
    if hem < 105:
        for s in (-1, 1):
            sw = math.sin(ph + (0 if s < 0 else math.pi)) * walk * 4
            cap((50 + s * 5, hem), (50 + s * 5 + sw, 107), 3.2, 2.8, skin)
    for s in (-1, 1):
        sw = math.sin(ph + (0 if s < 0 else math.pi)); lift = max(0, sw) * walk * 3
        fx = 50 + s * 7 + sw * walk * 3
        ell(fx, 110 - lift, 6.0, 3.0, R["wood"], clip=lambda x, y: y >= 107 - lift)
    # --- robe
    body(46 + bob + sh, hem + (0 if hem < 105 else 0), sp["w"][0], sp["w"][1], robe, clip=lambda x, y: y <= hem + int(math.sin(x * 0.55 + ph) * walk * 1.5))
    for xx, dxx in ((42, -1), (50, 0), (58, 1)):
        cap((xx, 82 + bob), (xx + dxx * 2, hem - 2), 0.7, 0.7, DK(robe))
    for xx in (38, 62): cap((xx, 90 + bob), (xx + (1 if xx > 50 else -1), hem - 1), 0.5, 0.5, robe[3:] * 4)
    if sp.get("trim"):
        tr = R[sp["trim"]]
        for x in range(50 - sp["w"][1] - 1, 50 + sp["w"][1] + 2):
            put(x, hem - 2 + int(math.sin(x * 0.55 + ph) * walk * 1.5), tr[2]); put(x, hem - 3 + int(math.sin(x * 0.55 + ph) * walk * 1.5), tr[1])
    # --- neckline
    for x in range(44, 57): put(x, 47 + bob + sh + (1 if 46 < x < 54 else 0), skin[1])
    # --- armor / mantle / sash
    if sp.get("armor"):
        body(46 + bob, 72 + bob, 15, 13, R["plate"])
        for yy in (54, 60, 66): cap((37, yy + bob), (63, yy + bob), 0.6, 0.6, DK(R["plate"]))
        cap((37, 74 + bob), (63, 74 + bob), 2.2, 2.2, R["brown"]); ell(50, 74 + bob, 3, 3, R["gold"])
        for i in range(5): cap((40 + i * 5, 76 + bob), (40 + i * 5, 84 + bob), 1.6, 1.4, R["brown"])
    elif sp.get("mantle") and name != "King":
        m = R[sp["mantle"]]
        ell(50, 46 + bob, 19, 8, m, clip=lambda x, y: y <= 52 + bob)
        cap((35, 48 + bob), (60, 80 + bob), 5.5, 6.5, m)
        if name == "Solomon":
            for yy in range(48, 80, 4): put(36 + (yy - 48) * 24 // 32, yy + bob, R["gold"][3])
    elif sp.get("mantle") and name == "King":
        ell(50, 48 + bob, 17, 9, R["gold"], clip=lambda x, y: y <= 56 + bob)
        for i in range(-3, 4): ell(50 + i * 4.5, 50 + bob + abs(i), 2.2, 3, R["lapis"] if i % 2 else R["scarlet"])
    if sp.get("sash") and not sp.get("armor"):
        b = R[sp["sash"]]
        if name == "Jesus":
            cap((36, 49 + bob), (60, 84 + bob), 3.2, 3.4, b)
        else:
            cap((37, 73 + bob), (63, 73 + bob), 1.9, 1.9, b)
            cap((54, 74 + bob), (56, 87 + bob), 1.2, 1.0, b)
    # --- arms
    sleeve_t = sp.get("sleeve", "long")
    upper = skin if sleeve_t in ("bare", "armor") else robe
    lowr = skin if sleeve_t in ("bare", "short", "armor") else robe
    if sp.get("armor"): upper = R["scarlet"]
    hands = {}
    for s_, key in ((-1, "la"), (1, "ra")):
        sway = math.sin(ph + (math.pi if s_ < 0 else 0)) * walk * 14
        base_a = (10 + 2 * math.sin(t * 1.7 + s_) + sway, 12)
        a1, f = pose.get(key, base_a)
        if sp["prop"] == "tablets" and s_ == 1 and key not in pose: a1, f = 34, -52
        if sp["prop"] in ("scepter", "rod", "spear", "staff", "crook") and s_ == 1 and key not in pose: a1, f = 22, -6
        shx, shy = 50 + s_ * 14.5, 48 + bob + sh
        el = (shx + s_ * 16 * math.sin(math.radians(a1)), shy + 16 * math.cos(math.radians(a1)))
        a2 = a1 + f
        hd = (el[0] + s_ * 14 * math.sin(math.radians(a2)), el[1] + 14 * math.cos(math.radians(a2)))
        cap((shx, shy), el, 4.8, 4.2, upper); cap(el, hd, 4.2, 3.4, lowr)
        if sleeve_t == "long": cap((el[0] + (hd[0] - el[0]) * 0.7, el[1] + (hd[1] - el[1]) * 0.7), hd, 3.8, 3.5, R[sp["trim"]] if sp.get("trim") else robe)
        hands[s_] = hd
    # props held
    hr = hands[1]
    pr = sp["prop"]
    if pr in ("scepter", "rod", "staff", "crook"):
        px = hr[0]
        top = 18 if pr != "rod" else 10
        cap((px, top), (px, 114), 1.5, 1.5, R["wood"] if pr not in ("scepter",) else R["gold"])
        if pr == "scepter": ell(px, top - 3, 3.6, 3.6, R["gold"]); put(int(px), top - 3, R["crimson"][2])
        if pr == "crook":
            cap((px, top), (px + 4, top - 5), 1.5, 1.5, R["gold"]); cap((px + 4, top - 5), (px + 9, top - 3), 1.5, 1.5, R["gold"])
        if pr == "staff":
            cap((px, top), (px - 3, top - 6), 1.6, 1.6, R["wood"]); cap((px - 3, top - 6), (px - 8, top - 8), 1.6, 1.6, R["wood"]); cap((px - 8, top - 8), (px - 11, top - 3), 1.6, 1.6, R["wood"])
        if pr == "rod":
            for yy in range(8, 52): put(int(px) + (yy - 8) // 14, yy, (200, 200, 210))
            ell(px + 3, 55, 4, 2.2, R["steel"])
    if pr == "spear" and True:
        px = 84
    ell(hr[0], hr[1] + 1.5, 3.5, 3.8, skin)
    hl = hands[-1]; ell(hl[0], hl[1] + 1.5, 3.5, 3.8, skin)
    if pr == "tablets":
        cx, cy = hr[0] + 1, hr[1] - 12
        ell(cx, cy + bob * 0, 7, 10, R["stone"]); cap((cx, cy - 6), (cx, cy + 8), 0.5, 0.5, [R["stone"][1]] * 4)
        for i in range(3):
            cap((cx - 4, cy - 5 + i * 4), (cx - 2, cy - 5 + i * 4), 0.5, 0.5, [R["stone"][0]] * 4); cap((cx + 2, cy - 5 + i * 4), (cx + 4, cy - 5 + i * 4), 0.5, 0.5, [R["stone"][0]] * 4)
        ell(hr[0], hr[1] + 1.5, 3.5, 3.8, skin)
    if pr == "scroll":
        cap((hr[0] - 1, hr[1] - 8), (hr[0] + 1, hr[1] + 6), 3.2, 3.2, R["ivory"]); ell(hr[0] - 1, hr[1] - 8, 3.2, 1.6, R["ivory"]); ell(hr[0] + 1, hr[1] + 6, 3.2, 1.6, R["linen"])
        cap((hr[0] - 2, hr[1] - 5), (hr[0] + 2, hr[1] - 5), 0.6, 0.6, R["scarlet"]); ell(hr[0], hr[1] + 1.5, 3.5, 3.8, skin)
    if pr == "jar":
        ell(hl[0] + 1, hl[1] - 4, 6, 8, R["terra"]); ell(hl[0] + 1, hl[1] - 12, 3, 2, R["terra"]); cap((hl[0] - 4, hl[1] - 5), (hl[0] + 6, hl[1] - 5), 0.6, 0.6, R["gold"]); ell(hl[0], hl[1] + 1.5, 3.5, 3.8, skin)
    if pr == "net":
        for i in range(8):
            cap((hl[0] - 4 + i * 1.2, hl[1] - 4), (hl[0] - 9 + i * 1.6, hl[1] + 16), 0.5, 0.5, R["linen"])
        for j in range(5): cap((hl[0] - 8 + j * 0.4, hl[1] + j * 4), (hl[0] + 6, hl[1] + j * 4), 0.5, 0.5, R["linen"])
        ell(hl[0], hl[1] + 1.5, 3.5, 3.8, skin)
    if pr == "sling":
        cap((hl[0], hl[1] + 3), (hl[0] - 3, hl[1] + 20), 0.7, 0.7, R["wood"]); ell(hl[0] - 4, hl[1] + 22, 3, 2.6, R["gray"])
    if sp.get("armor"):
        # shield on left
        sx0, sy0 = hl[0] - 3, hl[1] - 6
        ell(sx0, sy0, 9, 13, R["scarlet"]); ell(sx0, sy0, 4, 4, R["gold"]); 
        for yy in range(int(sy0) - 12, int(sy0) + 13): put(int(sx0), yy, R["gold"][2])
        ell(hl[0], hl[1] + 1.5, 3.5, 3.8, skin)
    # --- head
    cap((50, 32 + bob + sh), (50, 40 + bob + sh), 3.8, 3.8, skin)
    hy = 26 + bob + sh
    st = sp["style"]; hair = R[sp["hair"]]
    hdx = round(math.sin(t * 0.9) * 0.6)
    if st in ("long", "longcrown"): ell(50, hy + 4, 13, 14, hair, clip=lambda x, y: y <= hy + 20)
    if st == "veil": ell(50, hy + 3, 14, 15, R[sp["veil"]], clip=lambda x, y: y <= hy + 20)
    if st == "nemes":
        ell(50, hy + 5, 15, 16, R["lapis"], clip=lambda x, y: y <= hy + 22)
        for i in range(-3, 4): put(50 + i * 4, hy + 18, R["gold"][2]); put(50 + i * 4, hy + 12, R["gold"][1])
    if st == "helmet": pass
    ell(50, hy + 13, 5, 4.5, skin)
    hrx = 10.5 if not kid else 11.5; hry = 11.5 if not kid else 11.0
    ell(40.3, hy + 1, 2, 2.8, skin); ell(59.7, hy + 1, 2, 2.8, skin)
    ell(50, hy, hrx, hry, skin)
    ell(50, hy + 4, 2.0, 2.6, skin)
    if sp.get("old"):
        for x in range(42, 49): put(x, hy + 7 - (x % 2), skin[1])
        for yy, xx in ((hy - 4, 43), (hy - 3, 47), (hy - 4, 52), (hy - 3, 57)): put(xx, yy, skin[1])
    if sp["beard"]:
        bc, bw, bh = sp["beard"]
        ell(50, hy + 8 + bh // 2, bw, bh, R[bc], clip=lambda x, y: y >= hy + 6)
        cap((43, hy + 6), (57, hy + 6), 1.7, 1.7, R[bc])
    _face(sp, hy, skin, lk, blink, amp)
    if st in ("long", "longcrown"):
        ell(50, hy - 6, 12, 8, hair, clip=lambda x, y: y <= hy - 3)
        cap((39, hy - 4), (37, hy + 14), 2.2, 2.8, hair); cap((61, hy - 4), (63, hy + 14), 2.2, 2.8, hair)
        for x in range(42, 50): put(x, hy - 4 + (x % 2), hair[2])
    elif st == "curly":
        ell(50, hy - 4, 12, 8.5, hair, clip=lambda x, y: y <= hy - 1)
        for cx_, cy_ in ((39, hy - 1), (61, hy - 1), (41, hy - 7), (59, hy - 7), (50, hy - 11), (36, hy + 3), (64, hy + 3)): ell(cx_, cy_, 3.6, 3.6, hair)
    elif st == "veil":
        v = R[sp["veil"]]; inn = R[sp["inner"]]
        ell(50, hy - 4, 13.5, 10.5, v, clip=lambda x, y: y <= hy - 1)
        ell(50, hy - 3, 10.5, 6.5, inn, clip=lambda x, y: y <= hy - 2)
        ell(50, hy - 6, 12.5, 7, v, clip=lambda x, y: y <= hy - 4)
        cap((37, hy - 1), (35, hy + 18), 2.6, 3.4, v); cap((63, hy - 1), (65, hy + 18), 2.6, 3.4, v)
    elif st == "crown":
        ell(50, hy - 4, 12, 8.5, hair, clip=lambda x, y: y <= hy - 1)
        cap((38, hy), (37, hy + 7), 2.4, 2.8, hair); cap((62, hy), (63, hy + 7), 2.4, 2.8, hair)
        cap((39, hy - 7), (61, hy - 7), 1.7, 1.7, R["gold"])
        for i in (-9, -4.5, 0, 4.5, 9): cap((50 + i, hy - 8), (50 + i, hy - 12 + abs(i) // 5), 1.4, 0.8, R["gold"])
        put(50, hy - 7, R["crimson"][3]); put(45, hy - 7, R["azure"][3]); put(55, hy - 7, R["azure"][3])
    elif st == "sides":
        ell(50, hy - 5, 11, 7, hair, clip=lambda x, y: y <= hy - 7)
        cap((39, hy - 4), (38, hy + 5), 2.6, 3.0, hair); cap((61, hy - 4), (62, hy + 5), 2.6, 3.0, hair)
        for x in range(44, 57): put(x, hy - 6 + (x % 2), skin[2])
    elif st == "bald":
        cap((39, hy - 3), (38, hy + 6), 2.6, 3.0, hair); cap((61, hy - 3), (62, hy + 6), 2.6, 3.0, hair)
        ell(50, hy - 9, 8, 3, skin, clip=lambda x, y: y <= hy - 8)
    elif st == "nemes":
        ell(50, hy - 6, 12, 7.5, R["lapis"], clip=lambda x, y: y <= hy - 3)
        cap((38, hy - 4), (36, hy + 16), 3.2, 4.0, R["lapis"]); cap((62, hy - 4), (64, hy + 16), 3.2, 4.0, R["lapis"])
        for yy in range(hy - 6, hy + 14, 3): put(37, yy, R["gold"][2]); put(63, yy, R["gold"][2])
        cap((38, hy - 7), (62, hy - 7), 1.5, 1.5, R["gold"]); ell(50, hy - 10, 2.2, 3.2, R["gold"]); put(50, hy - 9, R["scarlet"][3])
    elif st == "helmet":
        ell(50, hy - 5, 12.5, 9, R["steel"], clip=lambda x, y: y <= hy - 1)
        cap((38, hy - 3), (38, hy + 5), 2.4, 2.4, R["steel"]); cap((62, hy - 3), (62, hy + 5), 2.4, 2.4, R["steel"])
        cap((39, hy - 1), (61, hy - 1), 1.3, 1.3, R["gold"])
        for i in range(-5, 6): cap((50 + i * 1.4, hy - 13), (50 + i * 1.4, hy - 18 + abs(i) // 2), 1.3, 1.0, R["scarlet"])
        cap((50, hy - 13), (50, hy - 15), 1.5, 1.5, R["scarlet"])
    if st == "longcrown":
        cap((39, hy - 7), (61, hy - 7), 1.7, 1.7, R["gold"])
        for i in (-9, -4.5, 0, 4.5, 9): cap((50 + i, hy - 8), (50 + i, hy - 12 + abs(i) // 5), 1.4, 0.8, R["gold"])
        put(50, hy - 7, R["scarlet"][3]); put(45, hy - 7, R["lapis"][3]); put(55, hy - 7, R["lapis"][3])
    elif st == "turban":
        ell(50, hy - 6, 13.5, 8.5, R["lapis"], clip=lambda x, y: y <= hy - 2)
        for i in range(-6, 7): put(50 + i * 2, hy - 8 + (i % 2), R["lapis"][3]); put(50 + i * 2, hy - 4 + (i % 2), R["lapis"][0])
        cap((38, hy - 3), (62, hy - 3), 1.6, 1.6, R["gold"]); ell(50, hy - 3, 2.4, 2.4, R["scarlet"])
    elif st == "hat":
        cap((38, hy - 3), (38, hy + 4), 2.2, 2.6, hair); cap((62, hy - 3), (62, hy + 4), 2.2, 2.6, hair)
        cap((50, hy - 8), (50, hy - 19), 8.5, 8.0, R["blackhat"]); cap((38, hy - 7), (62, hy - 7), 1.8, 1.8, R["blackhat"])
        cap((42, hy - 12), (58, hy - 12), 1.0, 1.0, R["gold"])
    elif st == "laurel":
        ell(50, hy - 5, 11.5, 7, hair, clip=lambda x, y: y <= hy - 4)
        for a in range(200, 345, 14):
            ax = 50 + 11 * math.cos(math.radians(a)); ay = hy - 3 + 9 * math.sin(math.radians(a))
            ell(ax, ay, 2.2, 1.6, R["leafg"])
    elif st == "wild":
        ell(50, hy - 5, 12.5, 8.5, hair, clip=lambda x, y: y <= hy - 2)
        for i in range(-6, 7): cap((50 + i * 2, hy - 8), (50 + i * 2.6, hy - 13 + abs(i) // 2), 1.6, 0.6, hair)
        cap((38, hy - 3), (35, hy + 12), 3.0, 3.4, hair); cap((62, hy - 3), (65, hy + 12), 3.0, 3.4, hair)
    elif st == "cap":
        ell(50, hy - 5, 11.5, 7, R["brown"], clip=lambda x, y: y <= hy - 3)
        cap((36, hy - 3), (66, hy - 3), 1.6, 1.6, R["brown"])
    if sp.get("halo"):
        for a in range(0, 360, 12):
            put(50 + int(13 * math.cos(math.radians(a))), hy - 15 + int(3.5 * math.sin(math.radians(a))), (255, 238, 150))
    a = c[:, :, 3] > 0
    ol = np.zeros_like(a)
    ol[1:, :] |= a[:-1, :]; ol[:-1, :] |= a[1:, :]; ol[:, 1:] |= a[:, :-1]; ol[:, :-1] |= a[:, 1:]
    ol &= ~a
    out = c.copy(); out[ol] = (*OUT, 255)
    if kid:
        im = Image.fromarray(out, "RGBA").resize((86, 103), Image.NEAREST)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o.alpha_composite(im, (7, H - 103 - 1)); out = np.array(o)
    return out

def sheet(path, names, t=0.0, Z=3, **kw):
    sh = Image.new("RGBA", (len(names) * W * Z, H * Z), (120, 170, 120, 255))
    for i, n in enumerate(names):
        im = Image.fromarray(draw(n, t, **kw), "RGBA").resize((W * Z, H * Z), Image.NEAREST)
        sh.alpha_composite(im, (i * W * Z, 0))
    sh.convert("RGB").save(path)

if __name__ == "__main__":
    S = sys.argv[1]
    names = list(SPECS)
    sheet(f"{S}/new_a.png", names[:6]); sheet(f"{S}/new_b.png", names[6:])

def strip(path, name, ts, Z=2, **kw):
    sh = Image.new("RGBA", (len(ts) * W * Z, H * Z), (120, 170, 120, 255))
    for i, (t, k) in enumerate(ts):
        im = Image.fromarray(draw(name, t, **{**kw, **k}), "RGBA").resize((W * Z, H * Z), Image.NEAREST)
        sh.alpha_composite(im, (i * W * Z, 0))
    sh.convert("RGB").save(path)
