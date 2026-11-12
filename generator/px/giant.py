import math, sys
import numpy as np
from PIL import Image

W, H = 100, 120
canvas = np.zeros((H, W, 4), dtype=np.uint8)
OUT = (22, 12, 18)
R = dict(
    skin=[(105,58,44),(158,94,68),(204,134,98),(236,176,136)],
    bronze=[(66,42,20),(122,82,34),(184,134,54),(238,198,104)],
    red=[(66,22,30),(118,38,40),(170,64,54),(212,102,80)],
    wood=[(48,30,24),(88,58,38),(130,90,54),(168,122,76)],
    hair=[(26,18,18),(52,34,30),(82,56,44),(110,78,60)],
    steel=[(50,60,80),(100,115,140),(160,175,200),(224,234,248)],
    shadow=[(30,24,44)]*4,
)
L = np.array([-0.55, -0.65, 0.52]); L /= np.linalg.norm(L)
B = [[0, 8], [12, 4]]
def pick(d, x, y, ramp):
    d = d + (B[y % 2][x % 2] / 16.0 - 0.25) * 0.10
    i = 0 if d < 0.12 else 1 if d < 0.48 else 2 if d < 0.80 else 3
    return ramp[i]
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: canvas[y, x] = (*c, 255)

def ell(cx, cy, rx, ry, ramp, clip=None):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            nx, ny = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            r2 = nx * nx + ny * ny
            if r2 <= 1:
                if clip and not clip(x, y): continue
                nz = math.sqrt(1 - r2)
                put(x, y, pick(nx * L[0] + ny * L[1] + nz * L[2], x, y, ramp))

def cap(p0, p1, r0, r1, ramp, clip=None):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0; ll = dx * dx + dy * dy or 1
    m = max(r0, r1) + 1
    for y in range(int(min(y0, y1) - m), int(max(y0, y1) + m) + 1):
        for x in range(int(min(x0, x1) - m), int(max(x0, x1) + m) + 1):
            px, py = x + .5, y + .5
            u = min(1, max(0, ((px - x0) * dx + (py - y0) * dy) / ll))
            cx, cy = x0 + u * dx, y0 + u * dy
            r = r0 + (r1 - r0) * u
            ddx, ddy = px - cx, py - cy
            dd = math.hypot(ddx, ddy)
            if dd <= r:
                if clip and not clip(x, y): continue
                nx, ny = ddx / r, ddy / r
                nz = math.sqrt(max(0, 1 - nx * nx - ny * ny))
                put(x, y, pick(nx * L[0] + ny * L[1] + nz * L[2], x, y, ramp))

def draw(t=0.0):
    canvas[:] = 0
    bob = round(math.sin(t * 2.2) * 1.0)
    sw = math.sin(t * 2.2)
    # shadow
    for y in range(111, 119):
        for x in range(20, 82):
            nx, ny = (x - 50) / 31, (y - 115) / 4
            if nx * nx + ny * ny <= 1 and (x + y) % 2 == 0: put(x, y, R["shadow"][0])
    # spear (behind)
    sx = 86
    cap((sx, 12 + bob), (sx, 114), 1.8, 1.8, R["wood"])
    cap((sx, 3 + bob), (sx, 15 + bob), 2.6, 0.8, R["steel"])
    # legs
    for s in (-1, 1):
        hx = 50 + s * 10
        cap((hx, 78 + bob), (50 + s * 12, 96), 8, 7, R["skin"])
        cap((50 + s * 12, 96), (50 + s * 13, 109), 7.2, 5.2, R["bronze"])
        ell(50 + s * 13, 111, 8.5, 4, R["wood"], clip=lambda x, y: y >= 108)
    # tunic
    ell(50, 80 + bob, 22, 12, R["red"], clip=lambda x, y: y >= 72)
    for i in range(3):
        cap((34 + i * 16, 86 + bob), (34 + i * 16 + (i - 1) * 2, 93), 1.0, 1.0, R["red"][:1] * 4)
    # torso
    ell(50, 54 + bob, 23, 23, R["bronze"], clip=lambda x, y: y <= 74)
    # belt
    cap((30, 72 + bob), (70, 72 + bob), 3, 3, R["wood"])
    ell(50, 72 + bob, 4, 3.4, R["bronze"])
    # chest lines
    cap((50, 40 + bob), (50, 66 + bob), 0.9, 0.9, R["bronze"][:1] * 4)
    cap((36, 52 + bob), (46, 56 + bob), 0.8, 0.8, R["bronze"][:1] * 4)
    cap((64, 52 + bob), (54, 56 + bob), 0.8, 0.8, R["bronze"][:1] * 4)
    # arms
    ell(27, 43 + bob, 9.5, 8.5, R["bronze"]); ell(73, 43 + bob, 9.5, 8.5, R["bronze"])
    cap((26, 47 + bob), (19, 62 + bob), 6, 5.2, R["skin"]); cap((19, 62 + bob), (21, 76 + bob), 5.6, 4.8, R["bronze"])
    cap((74, 47 + bob), (81, 61 + bob), 6, 5.2, R["skin"]); cap((81, 61 + bob), (84, 73 + bob), 5.6, 4.8, R["bronze"])
    ell(85, 74 + bob, 5.2, 5, R["skin"])
    # shield
    ell(13, 72 + bob, 13.5, 18, R["bronze"]); ell(13, 72 + bob, 10.5, 15, R["wood"]); ell(13, 72 + bob, 4, 4.6, R["bronze"])
    cap((13, 60 + bob), (13, 84 + bob), 0.8, 0.8, R["wood"][:1] * 4)
    # head
    hy = 25 + bob
    ell(50, hy, 12, 13, R["skin"])
    ell(50, hy + 9, 10.5, 8.5, R["hair"], clip=lambda x, y: y >= hy + 3)
    # helmet
    ell(50, hy - 4, 14.5, 12.5, R["bronze"], clip=lambda x, y: y <= hy - 1)
    cap((35, hy - 1), (65, hy - 1), 2.2, 2.2, R["bronze"])
    cap((50, hy - 1), (50, hy + 9), 1.7, 1.7, R["bronze"])
    cap((37, hy), (39, hy + 10), 3.2, 2.6, R["bronze"]); cap((63, hy), (61, hy + 10), 3.2, 2.6, R["bronze"])
    # crest
    cap((36, hy - 10), (43, hy - 16), 3, 3.4, R["red"]); cap((43, hy - 16), (57, hy - 16), 3.4, 3.4, R["red"]); cap((57, hy - 16), (64, hy - 10), 3.4, 3, R["red"])
    # eyes
    for ex in (44, 56):
        for dx in range(3):
            put(ex + dx - 1, hy + 2, (238, 232, 222))
        put(ex, hy + 2, (30, 20, 28)); put(ex + (1 if ex < 50 else -1), hy + 2, (30, 20, 28))
        for dx in range(-2, 3): put(ex + dx, hy, R["hair"][0])
    # outline
    a = canvas[:, :, 3] > 0
    ol = np.zeros_like(a)
    ol[1:, :] |= a[:-1, :]; ol[:-1, :] |= a[1:, :]; ol[:, 1:] |= a[:, :-1]; ol[:, :-1] |= a[:, 1:]
    ol &= ~a
    out = canvas.copy()
    out[ol] = (*OUT, 255)
    return out

if __name__ == "__main__":
    img = Image.fromarray(draw(0.0), "RGBA")
    bg = Image.new("RGBA", img.size, (40, 36, 80, 255)); bg.alpha_composite(img)
    bg.save(f"{sys.argv[1]}/giant_1x.png")
    bg.resize((W * 8, H * 8), Image.NEAREST).save(f"{sys.argv[1]}/giant_8x.png")
    print("ok")
