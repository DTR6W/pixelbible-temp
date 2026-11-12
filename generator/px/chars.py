import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import giant as g
from giant import ell, cap, put, R, OUT, W, H
from elder import body

R["tan"] = [(96,56,40),(146,92,62),(190,130,92),(224,170,128)]
R["white"] = [(110,110,126),(170,172,188),(222,224,236),(250,250,255)]
R["sky"] = [(40,60,84),(76,104,136),(120,150,182),(168,194,220)]
R["ochre"] = [(96,60,20),(150,100,34),(200,146,58),(240,194,104)]
R["terra"] = [(70,32,24),(120,60,40),(166,92,58),(206,128,84)]
R["azure"] = [(20,44,90),(34,76,150),(62,112,196),(120,164,230)]
R["rose"] = [(120,60,80),(176,98,118),(218,140,156),(246,186,196)]
R["cream"] = [(120,106,92),(184,168,146),(226,212,186),(248,238,214)]
R["purple"] = [(40,20,70),(80,42,128),(120,76,170),(166,120,214)]
R["crimson"] = [(80,16,28),(140,28,40),(190,52,56),(226,96,86)]
R["sea"] = [(30,60,64),(54,100,104),(90,140,140),(136,184,176)]
R["salt"] = [(60,54,52),(104,94,88),(150,138,128),(196,184,172)]
R["stone"] = [(70,72,82),(110,114,126),(156,160,172),(204,208,218)]
R["auburn"] = [(52,24,16),(104,52,32),(150,82,46),(192,116,66)]
R["leaf"] = [(24,70,34),(40,110,52),(66,150,70),(110,190,100)]
R["auburn"] = [(40,20,16),(84,42,28),(130,70,40),(170,100,58)]
R["rope"] = [(70,28,26),(120,50,40),(160,78,56),(196,110,80)]
R["linen"] = [(104,86,66),(156,132,98),(204,178,138),(238,218,176)]
R["gray"] = [(66,62,70),(108,104,112),(156,152,160),(204,200,208)]

BIG_EYES = False
SPECS = {
 "Jesus": dict(robe="cream", w=(13, 19), hem=109, mantle="crimson", belt=None, skin="tan", hair="auburn", style="long",
               beard=("auburn", 6, 6), prop="none", brow="auburn"),
 "Adam": dict(robe="leaf", w=(9, 12), hem=88, mantle=None, belt=None, skin="tan", hair="hair", style="curly", beard=None, prop="none", bare=True, brow="hair"),
 "Eve": dict(robe="leaf", w=(9, 12), hem=90, mantle=None, belt=None, skin="skin", hair="auburn", style="long", beard=None, prop="none", bare=True, brow="auburn"),
 "Moses": dict(robe="sky", w=(13, 19), hem=109, mantle="ochre", belt="rope", skin="skin", hair="white", style="long",
               beard=("white", 8, 12), prop="tablets", brow="gray"),
 "David": dict(robe="terra", w=(11, 14), hem=97, mantle=None, belt="wood", skin="skin", hair="hair", style="curly",
               beard=None, prop="sling", bare=True, brow="hair"),
 "Mary": dict(robe="rose", w=(11, 18), hem=109, mantle="azure", belt=None, skin="tan", hair="hair", style="veil",
              beard=None, prop="none", veil="azure", inner="cream", brow="hair"),
 "Solomon": dict(robe="purple", w=(13, 19), hem=109, mantle="crimson", belt="bronze", skin="tan", hair="hair", style="crown",
                 beard=("hair", 7, 7), prop="scepter", brow="hair"),
 "Peter": dict(robe="sea", w=(13, 16), hem=100, mantle=None, belt="rope", skin="tan", hair="salt", style="sides",
               beard=("salt", 8, 9), prop="rod", bare=True, brow="salt"),
}

def draw(name, t=0.0, amp=0.0, blink=False, pose=None):
    sp = SPECS[name]
    c = g.canvas; c[:] = 0
    bob = round(math.sin(t * 2.2) * 0.8)
    skin = R[sp["skin"]]; robe = R[sp["robe"]]; hem = sp["hem"]
    DK = lambda ramp: ramp[:1] * 4
    for y in range(111, 119):
        for x in range(26, 76):
            nx, ny = (x - 50) / 25, (y - 115) / 4
            if nx * nx + ny * ny <= 1 and (x + y) % 2 == 0: put(x, y, R["shadow"][0])
    sx = 86
    pr = sp["prop"]
    if pr == "scepter":
        cap((sx, 24), (sx, 114), 1.5, 1.5, R["bronze"]); ell(sx, 20, 3.6, 3.6, R["bronze"]); put(sx, 20, R["crimson"][2]); put(sx - 1, 19, R["crimson"][3])
    elif pr == "rod":
        cap((sx - 2, 72), (sx + 8, 8), 0.8, 0.5, R["wood"])
        for yy in range(8, 52): put(sx + 8 + (yy - 8) // 14, yy, (200, 200, 210))
        ell(sx + 11, 55, 4, 2.2, R["steel"]); put(sx + 9, 54, (20, 20, 30))
    # body
    body(46 + bob, hem + bob if False else hem, sp["w"][0], sp["w"][1], robe)
    for xx, dxx in ((42, -1), (50, 0), (58, 1)):
        cap((xx, 84 + bob), (xx + dxx * 2, hem - 2), 0.8, 0.8, DK(robe))
    if hem < 105:
        for s_ in (-1, 1):
            cap((50 + s_ * 5, hem), (50 + s_ * 5, 109), 2.8, 2.6, skin)
    for s_ in (-1, 1):
        ell(50 + s_ * 7, 111, 6.5, 3.2, R["wood"], clip=lambda x, y: y >= 109)
    # mantle
    if sp["mantle"]:
        m = R[sp["mantle"]]
        ell(50, 46 + bob, 19, 8, m, clip=lambda x, y: y <= 52 + bob)
        if name == "Mary":
            cap((33, 48 + bob), (30, hem - 4), 5, 7, m); cap((67, 48 + bob), (70, hem - 4), 5, 7, m)
        else:
            cap((34, 48 + bob), (60, 80 + bob), 5.5, 6.5, m)
        if name == "Solomon":
            for yy in range(48, 80, 4): put(36 + (yy - 48) * 24 // 32, yy + bob, R["bronze"][3])
    if sp.get("belt"):
        b = R[sp["belt"]]
        cap((37, 74 + bob), (63, 74 + bob), 2.0, 2.0, b)
        if name != "Solomon": cap((54, 75 + bob), (56, 88 + bob), 1.3, 1.1, b)
        else: ell(50, 74 + bob, 2.4, 2.4, R["red"])
    # arms
    sleeve = skin if sp.get("bare") else (R["rose"] if name == "Mary" else robe)
    upper = robe if sp.get("bare") else sleeve
    if pose:
        S0 = (33, 47 + bob); r1 = math.radians(pose[0]); r2 = math.radians(pose[0] + pose[1])
        el = (S0[0] - 13 * math.sin(r1), S0[1] + 13 * math.cos(r1)); hd = (el[0] - 12 * math.sin(r2), el[1] + 12 * math.cos(r2))
        cap(S0, el, 4.8, 4.6, upper); cap(el, hd, 4.6, 4.0, sleeve); ell(hd[0], hd[1] + 1.5, 3.8, 4.0, skin)
    else:
        cap((33, 47 + bob), (25, 60 + bob), 4.8, 4.6, upper); cap((25, 60 + bob), (23, 71 + bob), 4.6, 4.0, sleeve)
        ell(22, 74 + bob, 3.8, 4.0, skin)
    cap((67, 47 + bob), (75, 59 + bob), 4.8, 4.6, upper); cap((75, 59 + bob), (83, 68 + bob), 4.6, 4.0, sleeve)
    ell(85, 70 + bob, 3.9, 4.0, skin)
    if pr == "tablets":
        ell(88, 60 + bob, 7, 10, R["stone"]); cap((88, 54 + bob), (88, 70 + bob), 0.5, 0.5, [R["stone"][1]]*4)
        for i in range(3):
            cap((84, 55 + i * 4 + bob), (86, 55 + i * 4 + bob), 0.5, 0.5, [R["stone"][0]]*4); cap((90, 55 + i * 4 + bob), (92, 55 + i * 4 + bob), 0.5, 0.5, [R["stone"][0]]*4)
        ell(85, 71 + bob, 3.9, 4.0, skin)
    elif pr == "sling":
        cap((85, 72 + bob), (89, 90 + bob), 0.7, 0.7, R["wood"]); ell(90, 93 + bob, 3, 2.6, R["gray"])
    # head
    hy = 26 + bob
    st = sp["style"]; hair = R[sp["hair"]]
    if st == "long":
        ell(50, hy + 4, 13, 14, hair, clip=lambda x, y: y <= hy + 20)
    if st == "veil":
        v = R[sp["veil"]]
        ell(50, hy + 3, 14, 15, v, clip=lambda x, y: y <= hy + 20)
    if st != "veil": ell(50, hy + 13, 5, 4.5, skin)
    ell(50, hy, 10.5, 11.5, skin)
    ell(50, hy + 4, 2.0, 2.6, skin)
    if sp["beard"]:
        bc, bw, bh = sp["beard"]
        ell(50, hy + 8 + bh // 2, bw, bh, R[bc], clip=lambda x, y: y >= hy + 6)
        cap((44, hy + 6), (56, hy + 6), 1.7, 1.7, R[bc])
    mh = 1 + int(amp * 3.2)
    for yy in range(hy + 8, hy + 8 + mh):
        for xx in range(47, 54): put(xx, yy, (62, 30, 40))
    if st == "long":
        ell(50, hy - 6, 12, 8, hair, clip=lambda x, y: y <= hy - 3)
        cap((39, hy - 4), (37, hy + 14), 2.2, 2.8, hair); cap((61, hy - 4), (63, hy + 14), 2.2, 2.8, hair)
    elif st == "curly":
        ell(50, hy - 4, 12, 8.5, hair, clip=lambda x, y: y <= hy - 1)
        for cx_, cy_ in ((39, hy - 1), (61, hy - 1), (41, hy - 7), (59, hy - 7), (50, hy - 11), (36, hy + 3), (64, hy + 3)):
            ell(cx_, cy_, 3.6, 3.6, hair)
    elif st == "veil":
        v = R[sp["veil"]]; inn = R[sp["inner"]]
        ell(50, hy - 4, 13.5, 10.5, v, clip=lambda x, y: y <= hy - 1)
        ell(50, hy - 3, 10.5, 6.5, inn, clip=lambda x, y: y <= hy - 2)
        ell(50, hy - 6, 12.5, 7, v, clip=lambda x, y: y <= hy - 4)
        cap((37, hy - 1), (35, hy + 18), 2.6, 3.4, v); cap((63, hy - 1), (65, hy + 18), 2.6, 3.4, v)
    elif st == "crown":
        ell(50, hy - 4, 12, 8.5, hair, clip=lambda x, y: y <= hy - 1)
        cap((38, hy), (37, hy + 7), 2.4, 2.8, hair); cap((62, hy), (63, hy + 7), 2.4, 2.8, hair)
        cap((39, hy - 7), (61, hy - 7), 1.7, 1.7, R["bronze"])
        for i in (-9, -4.5, 0, 4.5, 9):
            cap((50 + i, hy - 8), (50 + i, hy - 12 + abs(i) // 5), 1.4, 0.8, R["bronze"])
        put(50, hy - 7, R["crimson"][3]); put(45, hy - 7, R["azure"][3]); put(55, hy - 7, R["azure"][3])
    elif st == "sides":
        ell(50, hy - 5, 11, 7, hair, clip=lambda x, y: y <= hy - 7)
        cap((39, hy - 4), (38, hy + 5), 2.6, 3.0, hair); cap((61, hy - 4), (62, hy + 5), 2.6, 3.0, hair)
        for x in range(44, 57): put(x, hy - 6 + (x % 2), skin[2])
    if not sp["beard"] or name == "Solomon":
        for cx_ in (42, 58): put(cx_, hy + 6, skin[3]); put(cx_ + (1 if cx_ < 50 else -1), hy + 6, skin[3])
    bc_ = R[sp["brow"]]
    for ex in (45, 55):
        if blink:
            for dx in range(-1, 2): put(ex + dx, hy + 3, (60, 36, 36))
        elif BIG_EYES:
            for dx in range(-2, 3):
                for dy in range(2, 4): put(ex + dx, hy + dy, (250, 246, 240))
            for dx in range(-1, 2):
                for dy in range(2, 4): put(ex + dx, hy + dy, (28, 16, 24))
            put(ex - 1, hy + 2, (255, 255, 255))
        else:
            for dx in range(-1, 2):
                put(ex + dx, hy + 2, (240, 234, 224)); put(ex + dx, hy + 3, (240, 234, 224))
            put(ex, hy + 2, (30, 20, 28)); put(ex, hy + 3, (30, 20, 28))
        for dx in range(-2, 3): put(ex + dx, hy, bc_[1] if not BIG_EYES else bc_[0])
    if name == "Mary" and not BIG_EYES:
        for ex in (45, 55): put(ex - 1, hy + 2, (30, 20, 28)); put(ex + 1, hy + 2, (30, 20, 28))
    a = c[:, :, 3] > 0
    ol = np.zeros_like(a)
    ol[1:, :] |= a[:-1, :]; ol[:-1, :] |= a[1:, :]; ol[:, 1:] |= a[:, :-1]; ol[:, :-1] |= a[:, 1:]
    ol &= ~a
    out = c.copy(); out[ol] = (*OUT, 255)
    return out

if __name__ == "__main__":
    S = sys.argv[1]
    names = [n for n in SPECS if n not in ('Adam','Eve','Jesus')]
    Z = 4
    sheet = Image.new("RGBA", (3 * W * Z, 2 * (H * Z + 40)), (26, 22, 56, 255))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    for i, n in enumerate(names):
        im = Image.fromarray(draw(n, 0.0), "RGBA").resize((W * Z, H * Z), Image.NEAREST)
        ox, oy = (i % 3) * W * Z, (i // 3) * (H * Z + 40)
        sheet.alpha_composite(im, (ox, oy + 40))
        tw = d.textlength(n.upper(), font=f); d.text((ox + (W * Z - tw) / 2, oy + 4), n.upper(), font=f, fill=(255, 210, 90))
    sheet.convert("RGB").save(f"{S}/v6_chars.png"); print("ok")
