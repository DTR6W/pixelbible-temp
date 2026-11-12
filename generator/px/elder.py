import math, sys
import numpy as np
from PIL import Image
import giant as g
from giant import ell, cap, put, R, OUT, W, H

R["linen"] = [(104,86,66),(156,132,98),(204,178,138),(238,218,176)]
R["indigo"] = [(26,32,64),(48,60,106),(78,96,148),(118,138,190)]
R["gray"] = [(66,62,70),(108,104,112),(156,152,160),(204,200,208)]
R["rope"] = [(70,28,26),(120,50,40),(160,78,56),(196,110,80)]

def body(y0, y1, w0, w1, ramp, cx=50, clip=None):
    for y in range(y0, y1 + 1):
        w = w0 + (w1 - w0) * (y - y0) / max(1, y1 - y0)
        for x in range(int(cx - w) - 1, int(cx + w) + 2):
            nx = (x + .5 - cx) / w
            if abs(nx) <= 1:
                if clip and not clip(x, y): continue
                nz = math.sqrt(1 - nx * nx)
                put(x, y, g.pick(nx * g.L[0] + 0.15 * g.L[1] + nz * g.L[2], x, y, ramp))

def draw(t=0.0, amp=0.0, blink=False, pose=None):
    c = g.canvas; c[:] = 0
    bob = round(math.sin(t * 2.2) * 0.8)
    DK = lambda ramp: ramp[:1] * 4
    for y in range(111, 119):
        for x in range(26, 76):
            nx, ny = (x - 50) / 25, (y - 115) / 4
            if nx * nx + ny * ny <= 1 and (x + y) % 2 == 0: put(x, y, R["shadow"][0])
    sx = 86
    cap((sx, 14), (sx, 114), 1.8, 1.8, R["wood"])
    cap((sx, 14), (sx - 3, 8), 1.8, 1.8, R["wood"]); cap((sx - 3, 8), (sx - 9, 6), 1.8, 1.8, R["wood"]); cap((sx - 9, 6), (sx - 13, 10), 1.8, 1.8, R["wood"])
    # robe: tapered, long
    body(46 + bob, 109, 13, 19, R["linen"])
    for xx, dxx in ((42, -1), (50, 0), (58, 1)):
        cap((xx, 84 + bob), (xx + dxx * 3, 107), 0.8, 0.8, DK(R["linen"]))
    for s_ in (-1, 1):
        ell(50 + s_ * 8, 111, 7, 3.4, R["wood"], clip=lambda x, y: y >= 109)
    # mantle: shoulders + diagonal drape
    ell(50, 46 + bob, 19, 8, R["indigo"], clip=lambda x, y: y <= 52 + bob)
    cap((34, 48 + bob), (60, 80 + bob), 5.5, 6.5, R["indigo"])
    cap((37, 58 + bob), (41, 58 + bob), 0.8, 0.8, R["linen"]); cap((43, 66 + bob), (47, 66 + bob), 0.8, 0.8, R["linen"])
    # rope belt + tail
    cap((37, 74 + bob), (63, 74 + bob), 2.0, 2.0, R["rope"])
    cap((54, 75 + bob), (56, 88 + bob), 1.3, 1.1, R["rope"])
    # arms
    if pose:
        S0 = (33, 47 + bob); r1 = math.radians(pose[0]); r2 = math.radians(pose[0] + pose[1])
        el = (S0[0] - 13 * math.sin(r1), S0[1] + 13 * math.cos(r1)); hd = (el[0] - 12 * math.sin(r2), el[1] + 12 * math.cos(r2))
        cap(S0, el, 4.8, 4.6, R["linen"]); cap(el, hd, 4.6, 4.0, R["linen"]); ell(hd[0], hd[1] + 1.5, 3.8, 4.0, R["skin"])
    else:
        cap((33, 47 + bob), (25, 60 + bob), 4.8, 4.6, R["linen"]); cap((25, 60 + bob), (23, 71 + bob), 4.6, 4.0, R["linen"])
        ell(22, 74 + bob, 3.8, 4.0, R["skin"])
    cap((67, 47 + bob), (75, 59 + bob), 4.8, 4.6, R["linen"]); cap((75, 59 + bob), (83, 68 + bob), 4.6, 4.0, R["linen"])
    ell(85, 70 + bob, 3.9, 4.0, R["skin"])
    # head
    hy = 26 + bob
    ell(50, hy + 13, 5, 4.5, R["skin"])
    ell(50, hy, 10.5, 11.5, R["skin"])
    ell(50, hy + 4, 2.0, 2.6, R["skin"])
    # beard (pointed) + mustache
    ell(50, hy + 11, 8, 9, R["gray"], clip=lambda x, y: y >= hy + 6)
    cap((44, hy + 6), (56, hy + 6), 1.7, 1.7, R["gray"])
    mh = 1 + int(amp * 3.2)
    for yy in range(hy + 8, hy + 8 + mh):
        for xx in range(47, 54): put(xx, yy, (62, 30, 40))
    # headcloth
    ell(50, hy - 4, 12.5, 10.5, R["linen"], clip=lambda x, y: y <= hy - 1)
    cap((38, hy - 2), (62, hy - 2), 1.8, 1.8, R["rope"])
    cap((39, hy - 2), (38, hy + 10), 3.0, 3.8, R["linen"]); cap((61, hy - 2), (62, hy + 10), 3.0, 3.8, R["linen"])
    cap((37, hy + 3), (37, hy + 10), 0.8, 0.8, R["indigo"]); cap((63, hy + 3), (63, hy + 10), 0.8, 0.8, R["indigo"])
    # eyes + brows
    for ex in (45, 55):
        if blink:
            for dx in range(-1, 2): put(ex + dx, hy + 3, (60, 36, 36))
        else:
            for dx in range(-1, 2):
                put(ex + dx, hy + 2, (240, 234, 224)); put(ex + dx, hy + 3, (240, 234, 224))
            put(ex, hy + 2, (30, 20, 28)); put(ex, hy + 3, (30, 20, 28))
        for dx in range(-2, 3): put(ex + dx, hy, R["gray"][1])
    a = c[:, :, 3] > 0
    ol = np.zeros_like(a)
    ol[1:, :] |= a[:-1, :]; ol[:-1, :] |= a[1:, :]; ol[:, 1:] |= a[:, :-1]; ol[:, :-1] |= a[:, 1:]
    ol &= ~a
    out = c.copy(); out[ol] = (*OUT, 255)
    return out

if __name__ == "__main__":
    img = Image.fromarray(draw(0.0), "RGBA")
    bg = Image.new("RGBA", img.size, (40, 36, 80, 255)); bg.alpha_composite(img)
    bg.resize((W * 8, H * 8), Image.NEAREST).save(f"{sys.argv[1]}/elder_8x.png")
    img.save(f"{sys.argv[1]}/elder_sprite.png")
    print("ok")
