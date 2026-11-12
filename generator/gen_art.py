import sys, math, random
S = sys.argv[1]
sys.path.insert(0, S + "/px")
import chars, eden_sprites as es
chars.BIG_EYES = True
from PIL import Image, ImageDraw, ImageFont
def lerp(a, b, f): return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))
def star(d, cx, cy, pr, col):
    d.polygon([(cx, cy - pr), (cx + pr // 3, cy - pr // 3), (cx + pr, cy), (cx + pr // 3, cy + pr // 3), (cx, cy + pr), (cx - pr // 3, cy + pr // 3), (cx - pr, cy), (cx - pr // 3, cy - pr // 3)], fill=col)
def put(im, arr, x, base, sc, flip=False):
    a = Image.fromarray(arr, "RGBA"); a = a.resize((int(a.width * sc), int(a.height * sc)), Image.NEAREST)
    if flip: a = a.transpose(Image.FLIP_LEFT_RIGHT)
    im.paste(a, (int(x - a.width / 2), int(base - 111 * sc)), a)
ch = lambda n: chars.draw(n, 0.0, 0.0, False, None)
W, H = 256, 144
im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); d.fontmode = "1"
for y in range(0, H, 2):
    f = y / 108
    c = lerp((8, 8, 34), (60, 40, 100), min(1, f / 0.7)) if f < 0.7 else lerp((60, 40, 100), (240, 150, 110), min(1, (f - 0.7) / 0.3))
    d.rectangle([0, y, W, y + 1], fill=c)
rr = random.Random(8)
for _ in range(150): d.point((rr.randrange(W), rr.randrange(95)), fill=(230, 235, 255) if rr.random() < 0.8 else (255, 232, 160))
for r in range(80, 0, -4): d.ellipse([128 - r * 1.5, 60 - r * 0.7, 128 + r * 1.5, 60 + r * 0.7], fill=lerp((40, 30, 90), (120, 80, 140), (1 - r / 80) ** 1.8))
def cloud(x, y, s, col):
    for dx, dy, r in ((0, 0, 7), (8, -2, 8), (17, 0, 6), (5, 3, 6), (13, 3, 6)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s * 0.6, x + dx * s + r * s, y + dy * s + r * s * 0.6], fill=col)
cloud(14, 22, 1.1, (70, 56, 120)); cloud(196, 16, 1.2, (74, 58, 124)); cloud(150, 32, 0.8, (66, 52, 114)); cloud(52, 40, 0.8, (66, 52, 114))
for r_ in (22, 16): d.ellipse([128 - r_, 24 - r_, 128 + r_, 24 + r_], outline=(92, 80, 150))
star(d, 128, 24, 11, (255, 228, 150)); star(d, 128, 24, 5, (255, 250, 220))
for sx, sy, p in ((70, 18, 3), (190, 40, 3), (40, 50, 2), (220, 60, 2)): star(d, sx, sy, p, (255, 232, 170))
for x in range(W):
    y1 = int(106 + 7 * math.sin(x * 0.035) + 3 * math.sin(x * 0.11)); d.line([(x, y1), (x, H)], fill=(100, 62, 96))
    y2 = int(120 + 5 * math.sin(x * 0.05 + 1.2) + 2 * math.sin(x * 0.13)); d.line([(x, y2), (x, H)], fill=(160, 100, 96))
    y3 = int(134 + 3 * math.sin(x * 0.07 + 2)); d.line([(x, y3), (x, H)], fill=(200, 130, 100))
put(im, ch("Moses"), 30, 140, 0.7); put(im, ch("David"), 64, 141, 0.5)
put(im, es.SP["lion"](0.4, 0.0), 97, 142, 0.36); put(im, es.SP["sheep"](0.4, 0.0), 118, 141, 0.34); put(im, es.SP["bunny"](0.2, 0.0), 136, 142, 0.32); put(im, es.SP["deer"](0.4, 0.0), 155, 141, 0.36, True)
put(im, ch("Mary"), 190, 141, 0.5); put(im, ch("Jesus"), 226, 140, 0.7)
def text(txt, cy, size, col, sh=(10, 8, 30)):
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    tw = d.textlength(txt, font=f); x = (W - tw) / 2
    for dx, dy in ((1, 1), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)): d.text((x + dx, cy + dy), txt, font=f, fill=sh)
    d.text((x, cy), txt, font=f, fill=col)
text("PIXEL BIBLE", 51, 19, (255, 214, 100)); text("BIBLE, EXPLAINED", 77, 10, (255, 255, 255))
big = im.resize((2048, 1152), Image.NEAREST); big.save(S + "/banner_2048x1152.png")
N = 200; p = Image.new("RGB", (N, N)); d = ImageDraw.Draw(p)
for y in range(0, N, 2):
    f = y / N
    c = lerp((10, 10, 40), (60, 40, 100), f / 0.65) if f < 0.65 else lerp((60, 40, 100), (240, 160, 110), (f - 0.65) / 0.35)
    d.rectangle([0, y, N, y + 1], fill=c)
for _ in range(70): d.point((rr.randrange(N), rr.randrange(100)), fill=(230, 235, 255))
for r in range(78, 0, -4): d.ellipse([100 - r, 98 - r, 100 + r, 98 + r], fill=lerp((60, 40, 100), (255, 230, 160), (1 - r / 78) ** 1.5))
for r_ in (16, 11): d.ellipse([100 - r_, 22 - r_, 100 + r_, 22 + r_], outline=(90, 80, 150))
star(d, 100, 22, 9, (255, 228, 150))
for x in range(N):
    y1 = int(138 + 8 * math.sin(x * 0.05) + 4 * math.sin(x * 0.13)); d.line([(x, y1), (x, N)], fill=(120, 72, 100))
    y2 = int(158 + 6 * math.sin(x * 0.06 + 1.2)); d.line([(x, y2), (x, N)], fill=(176, 110, 98))
put(p, ch("Moses"), 50, 150, 0.6); put(p, ch("Peter"), 150, 150, 0.6); put(p, ch("Jesus"), 100, 150, 0.86)
put(p, ch("David"), 66, 186, 0.64); put(p, ch("Mary"), 134, 186, 0.64)
pb = p.resize((800, 800), Image.NEAREST); pb.save(S + "/perfil_jesus.png")
mask = Image.new("L", (800, 800), 0); ImageDraw.Draw(mask).ellipse([0, 0, 799, 799], fill=255)
bg = Image.new("RGB", (800, 800), (30, 30, 30)); bg.paste(pb, (0, 0), mask); bg.resize((400, 400)).save(S + "/perfil_jesus_circulo.png")
a = big.crop((0, 500, 2048, 1152)).resize((1024, 326)); b = Image.open(S + "/perfil_jesus_circulo.png")
m = Image.new("RGB", (1024, 326 + 400), (30, 30, 30)); m.paste(a, (0, 0)); m.paste(b, (300, 326)); m.save(S + "/chk5.png")
