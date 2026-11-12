import math, random
from PIL import Image, ImageDraw, ImageFont
import engine5 as E, cast5, abr_cast
PW, PH, HZ = 480, 270, 200
base = Image.new("RGB", (PW, PH)); d = ImageDraw.Draw(base)
for y in range(PH):
    d.line([(0, y), (PW, y)], fill=E.lerpc((6, 8, 34), (70, 50, 120), (y / HZ) ** 1.6))
r = random.Random(9)
for i in range(520):
    x, y = r.randrange(PW), r.randrange(HZ - 6); c = r.randint(150, 255)
    d.point((x, y), fill=(c, c, 255))
    if r.random() < 0.08: d.point((x + 1, y), fill=(c, c, 255)); d.point((x, y + 1), fill=(c, c, 255))
E.fx_glow(base, 330, 70, 120, (180, 170, 255), 0.35); d = ImageDraw.Draw(base)
E.mountains(d, 5, HZ - 20, 30, (30, 26, 64), (46, 40, 86), w=PW)
d.rectangle([0, HZ, PW, PH], fill=(40, 44, 50))
E.tent(d, 410, HZ + 6, 40, 30, col=(150, 120, 90))
def put(name, x, yb, s, flip=False, pose=None):
    im = Image.fromarray(cast5.sprite(name, 0.4, 0.0, False, pose), "RGBA")
    im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    base.paste(im, (int(x - im.width / 2), int(yb - im.height)), im)
put("Abraham", 330, PH + 6, 1.6, pose={"la": (150, -8), "ra": (150, -8)})
put("Isaac", 410, PH + 4, 1.2, flip=True, pose={"ra": (150, -10)})
big = E.upscale_post(base.convert("RGB")); W, H = big.size
dd = ImageDraw.Draw(big)
F = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
def text(txt, x, y, size, fill, stroke=14):
    f = ImageFont.truetype(F, size)
    dd.text((x + 8, y + 10), txt, font=f, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
    dd.text((x, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(20, 10, 40))
text("COUNT", 70, 120, 190, (255, 255, 255))
text("THE STARS", 70, 330, 150, (255, 214, 90))
text("ABRAHAM'S STORY", 76, 540, 70, (200, 220, 255), stroke=8)
big.resize((1280, 720), Image.LANCZOS).save("thumb_abraham.jpg", quality=92)
