import math, sys
import numpy as np
from PIL import Image, ImageDraw
import giant as g
from giant import ell, cap, R, OUT, W, H
def put(x, y, c): g.put(int(round(x)), int(round(y)), c)
from elder import body

R["leaf"] = [(24,70,34),(40,110,52),(70,156,74),(122,200,108)]
R["tan"] = [(96,56,40),(146,92,62),(190,130,92),(224,170,128)]
R["auburn"] = [(52,24,16),(104,52,32),(150,82,46),(192,116,66)]
R["gold"] = [(120,70,20),(186,120,40),(228,168,70),(250,208,120)]
R["mane"] = [(60,32,16),(104,60,26),(146,90,38),(186,124,54)]
R["cream"] = [(150,120,90),(206,176,140),(240,216,184),(255,244,224)]
R["wool"] = [(150,150,168),(198,198,212),(232,232,242),(252,252,255)]
R["dkgray"] = [(30,30,40),(56,56,68),(86,86,100),(120,120,134)]
R["fawn"] = [(110,64,32),(164,100,52),(204,136,76),(232,172,110)]
R["bunny"] = [(150,146,160),(200,196,210),(236,232,242),(255,255,255)]
R["pink"] = [(190,90,110),(228,130,150),(248,170,184),(255,208,216)]

def clear():
    g.canvas[:] = 0
def shadow(cx=50, cy=111, rx=26):
    for y in range(cy - 4, cy + 5):
        for x in range(cx - rx, cx + rx):
            nx, ny = (x - cx) / rx, (y - cy) / 4
            if nx * nx + ny * ny <= 1 and (x + y) % 2 == 0: put(x, y, R["shadow"][0])
def finish():
    c = g.canvas
    a = c[:, :, 3] > 0
    ol = np.zeros_like(a)
    ol[1:, :] |= a[:-1, :]; ol[:-1, :] |= a[1:, :]; ol[:, 1:] |= a[:, :-1]; ol[:, :-1] |= a[:, 1:]
    ol &= ~a
    out = c.copy(); out[ol] = (*OUT, 255)
    return out
def eye(x, y, big=True):
    for dx in range(-1, 2):
        for dy in range(0, 3 if big else 2): put(x + dx, y + dy, (250, 246, 240))
    put(x, y + 1, (40, 24, 30)); put(x, y + 2 if big else y + 1, (40, 24, 30)); put(x - 1, y, (255, 255, 255))

def human(kind, t=0.0, walk=0.0, amp=0.0, pose=None, look=0.0, blink=False):
    clear(); shadow()
    eve = kind == "Eve"
    sk = R["skin"] if eve else R["tan"]; hair = R["auburn"] if eve else R["hair"]
    bob = round(math.sin(t * 2.0) * 0.7)
    ph = t * 4.5
    if eve:
        ell(50, 32 + bob, 15.5, 19, hair, clip=lambda x, y: y <= 60 + bob)
    # legs
    for s in (-1, 1):
        sw = math.sin(ph + (0 if s < 0 else math.pi)) * walk * 5
        top = (50 + s * 5, 78 + bob); bot = (50 + s * 5 + sw, 106)
        cap(top, bot, 4.8, 3.6, sk)
        ell(bot[0] + s * 0.8 + 1.5, 109, 5.6, 3.2, R["wood"])
    # torso
    if eve:
        body(36 + bob, 66 + bob, 12.5, 9.8, sk)
    else:
        body(35 + bob, 66 + bob, 15.5, 10.8, sk)
        for x in range(41, 49): put(x, 49 + bob + (1 if x > 44 else 0), sk[1])
        for x in range(52, 60): put(x, 49 + bob + (1 if x < 55 else 0), sk[1])
        for y in range(53 + bob, 62 + bob): put(50, y, sk[1])
    # arms (angles: 0=down, 90=out, 180=up; fore is relative)
    pose = pose or {}
    for s_, key in ((-1, "la"), (1, "ra")):
        sw = math.sin(ph + (math.pi if s_ < 0 else 0)) * walk * 14
        a1, f = pose.get(key, (9 + 2 * math.sin(t * 1.7 + s_), 7))
        a1 = a1 + sw * (1 if key in pose and False else 1) if key not in pose else a1
        sh = (50 + s_ * 14.5, 40 + bob)
        el = (sh[0] + s_ * 17 * math.sin(math.radians(a1)), sh[1] + 17 * math.cos(math.radians(a1)))
        a2 = a1 + f
        hd = (el[0] + s_ * 15 * math.sin(math.radians(a2)), el[1] + 15 * math.cos(math.radians(a2)))
        cap(sh, el, 4.6, 3.9, sk); cap(el, hd, 3.9, 3.3, sk); ell(hd[0], hd[1] + 1.5, 3.5, 3.8, sk)
    # leaf clothing
    if eve:
        body(45 + bob, 94 + bob, 11.8, 17.5, R["leaf"], clip=lambda x, y: y <= 92 + bob + (3 if (x // 3) % 2 else 0))
        ell(50, 46 + bob, 12.5, 5.5, R["leaf"], clip=lambda x, y: y <= 49 + bob + (2 if (x // 3) % 2 else 0))
        cap((39, 62 + bob), (61, 62 + bob), 1.7, 1.7, R["wood"])
        for x, y in ((43, 70), (50, 76), (57, 71)): cap((x, y + bob), (x, y + 8 + bob), 0.7, 0.7, R["leaf"][:1] * 4)
    else:
        body(62 + bob, 84 + bob, 11.8, 14.8, R["leaf"], clip=lambda x, y: y <= 82 + bob + (3 if (x // 3) % 2 else 0))
        cap((38, 62 + bob), (62, 62 + bob), 1.8, 1.8, R["wood"])
        for x in (44, 50, 56): cap((x, 70 + bob), (x, 78 + bob), 0.7, 0.7, R["leaf"][:1] * 4)
    # head
    cap((50, 30 + bob), (50, 38 + bob), 3.8, 3.8, sk)
    hy = 22 + bob
    ell(40.3, hy + 1, 2, 2.8, sk); ell(59.7, hy + 1, 2, 2.8, sk)
    ell(50, hy, 9.8, 10.8, sk)
    if eve:
        ell(50, hy - 7, 11.2, 8, hair, clip=lambda x, y: y <= hy - 3)
        for xx in range(41, 50): put(xx, hy - 3 + ((xx + 1) % 2), hair[2])
        cap((40, hy - 5), (37, hy + 20), 3.2, 3.8, hair); cap((60, hy - 5), (63, hy + 20), 3.2, 3.8, hair)
        for i, (fx, fy, col) in enumerate(((41, hy - 6, (255, 130, 160)), (45, hy - 9, (255, 255, 255)), (50, hy - 10, (255, 210, 90)), (55, hy - 9, (255, 255, 255)), (59, hy - 6, (255, 130, 160)))):
            put(fx, fy, col); put(fx + 1, fy, col); put(fx, fy + 1, col); put(fx + 1, fy + 1, (255, 210, 90) if i % 2 else (255, 255, 255))
            put(fx - 1, fy + 1, (60, 150, 70))
    else:
        ell(50, hy - 7, 11, 7, hair, clip=lambda x, y: y <= hy - 4)
        for cx_, cy_, r_ in ((41, hy - 3, 3.4), (59, hy - 3, 3.4), (45, hy - 9, 3.8), (55, hy - 9, 3.8), (50, hy - 11, 3.8), (39, hy + 1, 2.6), (61, hy + 1, 2.6)): ell(cx_, cy_, r_, r_, hair)
    lk = int(round(look * 1.6))
    ex = (45 + lk, 55 + lk)
    for e_ in ex:
        if blink:
            for dx in range(-1, 2): put(e_ + dx, hy + 2, (60, 36, 36))
        else: eye(e_, hy + 1)
    for e_ in ex:
        for dx in range(-2, 3): put(e_ + dx, hy - 1 - (1 if eve and dx == 2 else 0), hair[1])
    put(50 + lk, hy + 5, sk[1]); put(49 + lk, hy + 5, sk[1])
    mh = int(amp * 3)
    if mh > 0:
        for yy in range(hy + 7, hy + 7 + mh):
            for xx in range(48, 53): put(xx, yy, (110, 40, 50))
    else:
        for xx, yy in ((47 + lk, hy + 7), (48 + lk, hy + 8), (49 + lk, hy + 8), (50 + lk, hy + 8), (51 + lk, hy + 8), (52 + lk, hy + 8), (53 + lk, hy + 7)): put(xx, yy, (150, 60, 66))
    for cx_ in (42, 58): put(cx_, hy + 5, sk[3]); put(cx_ + 1, hy + 5, (240, 150, 140)); put(cx_ - 1, hy + 5, (240, 150, 140))
    return finish()

def legs4(cx, y0, y1, xs, ph, ramp, r0=4.2, r1=3.0, sw=3.2, offs=(0, math.pi, math.pi, 0)):
    for x0, o in zip(xs, offs):
        s_ = math.sin(ph + o) * sw
        cap((x0, y0), (x0 + s_, y1), r0, r1, ramp)

def lion(t=0.0, walk=1.0):
    clear(); shadow(48, 104, 34)
    ph = t * 5; bob = round(abs(math.sin(ph)) * walk * 0.8)
    legs4(0, 72, 98, (26, 34, 58, 66), ph, R["gold"], 5, 3.6, 3.0 * walk, (0, math.pi, math.pi, 0))
    for x0, o in ((26, 0), (34, math.pi), (58, math.pi), (66, 0)):
        ell(x0 + math.sin(ph + o) * 3.0 * walk, 99, 4.6, 2.8, R["cream"])
    cap((20, 60 - bob), (11, 50 + 3 * math.sin(t * 3)), 1.8, 1.4, R["gold"]); ell(9, 48 + 3 * math.sin(t * 3), 3.4, 4.2, R["mane"])
    ell(44, 66 - bob, 25, 13.5, R["gold"])
    ell(44, 74 - bob, 20, 6, R["cream"], clip=lambda x, y: y >= 74 - bob)
    for cx_, cy_, r_ in ((68, 56, 16), (59, 46, 7.5), (77, 47, 7.5), (60, 67, 7.5), (78, 67, 7), (69, 42, 7)): ell(cx_ - 0, cy_ - bob, r_, r_ * (1 if r_ > 10 else 0.95), R["mane"])
    ell(72, 58 - bob, 10.5, 9.8, R["gold"])
    ell(81, 63 - bob, 6.4, 4.8, R["cream"])
    ell(66, 49 - bob, 3.4, 3.4, R["gold"]); put(66, 49 - bob, R["pink"][1]); put(67, 49 - bob, R["pink"][1])
    put(86, 61 - bob, (30, 16, 20)); put(85, 61 - bob, (30, 16, 20)); put(86, 62 - bob, (30, 16, 20))
    for xx in range(78, 85): put(xx, 66 - bob, (110, 50, 50))
    eye(75, 54 - bob, False); put(73, 52 - bob, R["mane"][0]); put(74, 52 - bob, R["mane"][0]); put(75, 52 - bob, R["mane"][0])
    return finish()

def sheep(t=0.0, walk=1.0):
    clear(); shadow(48, 104, 32)
    ph = t * 4.5; bob = round(abs(math.sin(ph)) * walk * 0.7)
    legs4(0, 78, 98, (36, 46, 58, 68), ph, R["dkgray"], 3.4, 2.6, 2.6 * walk, (0, math.pi, math.pi, 0))
    for x0, o in ((36, 0), (46, math.pi), (58, math.pi), (68, 0)): ell(x0 + math.sin(ph + o) * 2.6 * walk, 99, 3.6, 2.2, (30, 24, 28) and R["dkgray"])
    for cx_, cy_, rx_, ry_ in ((38, 66, 14, 12.5), (54, 62, 14, 13), (30, 74, 11, 10), (48, 74, 14, 11.5), (64, 72, 12, 11), (62, 58, 10, 9)): ell(cx_, cy_ - bob, rx_, ry_, R["wool"])
    ell(76, 66 - bob, 8.4, 9.2, R["dkgray"]); ell(74, 55 - bob, 6.4, 4.4, R["wool"]); ell(70, 56 - bob, 4.4, 3.6, R["wool"])
    cap((69, 62 - bob), (63, 67 - bob), 2.4, 1.8, R["dkgray"])
    for e_ in (77,): eye(e_, 62 - bob, False)
    put(82, 69 - bob, R["pink"][1]); put(82, 70 - bob, R["pink"][1])
    for xx in range(78, 82): put(xx, 73 - bob, R["dkgray"][0])
    return finish()

def deer(t=0.0, walk=1.0):
    clear(); shadow(46, 108, 32)
    ph = t * 4.5; bob = round(abs(math.sin(ph)) * walk * 0.8)
    legs4(0, 66, 104, (28, 36, 54, 62), ph, R["fawn"], 3.0, 2.0, 3.6 * walk, (0, math.pi, math.pi, 0))
    for x0, o in ((28, 0), (36, math.pi), (54, math.pi), (62, 0)): ell(x0 + math.sin(ph + o) * 3.6 * walk, 105, 2.8, 1.8, R["dkgray"])
    ell(22, 58 - bob, 3.6, 3.8, R["cream"])
    ell(42, 62 - bob, 22, 11.5, R["fawn"])
    ell(42, 70 - bob, 17, 5, R["cream"], clip=lambda x, y: y >= 70 - bob)
    for sx, sy in ((30, 56), (38, 54), (46, 56), (54, 58), (34, 62), (44, 60), (52, 63), (26, 62)): put(sx, sy - bob, R["cream"][3]); put(sx + 1, sy - bob, R["cream"][3])
    cap((56, 58 - bob), (66, 40 - bob), 6, 4.2, R["fawn"])
    ell(70, 36 - bob, 7.4, 6.4, R["fawn"]); ell(77, 39 - bob, 4.6, 3.4, R["cream"])
    put(80, 38 - bob, (30, 16, 20)); put(81, 38 - bob, (30, 16, 20))
    cap((65, 31 - bob), (60, 22 - bob), 2.4, 1.8, R["fawn"]); ell(61, 23 - bob, 1.4, 2, R["pink"]); cap((72, 30 - bob), (75, 21 - bob), 2.4, 1.8, R["fawn"]); ell(74.6, 23 - bob, 1.4, 2, R["pink"])
    eye(71, 34 - bob, False)
    return finish()

def bunny(t=0.0, walk=1.0):
    clear(); shadow(44, 108, 22)
    hop = abs(math.sin(t * 5)) * 5 * walk
    ell(26, 86 - hop, 5.2, 5.2, R["bunny"])
    ell(40, 84 - hop, 15, 12, R["bunny"]); ell(46, 98, 6, 3, R["bunny"]); ell(28, 98, 6, 3, R["bunny"])
    ell(58, 74 - hop, 9, 8.4, R["bunny"]); ell(65, 78 - hop, 3.6, 2.8, R["bunny"])
    cap((55, 68 - hop), (51, 44 - hop), 3.4, 2.6, R["bunny"]); cap((61, 68 - hop), (65, 46 - hop), 3.4, 2.6, R["bunny"])
    cap((55, 66 - hop), (52, 48 - hop), 1.6, 1.2, R["pink"]); cap((61, 66 - hop), (64, 50 - hop), 1.6, 1.2, R["pink"])
    eye(60, 72 - hop, False); put(67, 77 - hop, R["pink"][0]); put(67, 78 - hop, R["pink"][0])
    return finish()

SP = dict(Adam=lambda t, w=0.0, a=0.0: human("Adam", t, w, a), Eve=lambda t, w=0.0, a=0.0: human("Eve", t, w, a),
          lion=lambda t, w=1.0, a=0: lion(t, w), sheep=lambda t, w=1.0, a=0: sheep(t, w), deer=lambda t, w=1.0, a=0: deer(t, w), bunny=lambda t, w=1.0, a=0: bunny(t, w))

if __name__ == "__main__":
    S = sys.argv[1]
    names = list(SP); Z = 4
    sheet = Image.new("RGBA", (3 * W * Z, 2 * H * Z), (96, 170, 96, 255))
    for i, n in enumerate(names):
        im = Image.fromarray(SP[n](0.4), "RGBA").resize((W * Z, H * Z), Image.NEAREST)
        sheet.alpha_composite(im, ((i % 3) * W * Z, (i // 3) * H * Z))
    sheet.convert("RGB").save(f"{S}/v7_eden.png"); print("ok")
