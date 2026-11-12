"""Thumbnail for the Genesis long-form video: Eden | Ark + rainbow | Babel, big title."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import engine5 as E, cast5

PW, PH, HZ = 480, 270, 196
# sky: warm sunset at horizon, deep purple top
sky = Image.new("RGBA", (PW, PH))
sd = ImageDraw.Draw(sky)
for y in range(PH):
    f = y / HZ
    c = E.lerpc((46, 30, 92), (255, 150, 80), f ** 1.4) if y < HZ else (0, 0, 0)
    sd.line([(0, y), (PW, y)], fill=c + (255,))
base = sky
d = ImageDraw.Draw(base)
E.stars(d, 0.0, n=40, seed=3, w=PW, ymax=70)
E.sun(d, 240, HZ - 18, 26, 0.0, col=(255, 214, 120), rays=False)
E.cloud(d, 60, 70, 1.2, col=(255, 200, 170), shade=(220, 140, 130))
E.cloud(d, 400, 60, 1.0, col=(255, 200, 170), shade=(220, 140, 130))
E.mountains(d, 7, HZ - 30, 40, (92, 60, 110), (120, 84, 130), w=PW)
E.hills(d, 9, HZ - 8, 14, (60, 110, 70), (80, 140, 80), w=PW)
# ground
d.rectangle([0, HZ, PW, PH], fill=(70, 140, 70))
for x in range(0, PW, 3):
    if random.Random(x).random() < 0.5: d.point((x, HZ + random.Random(x * 7).randint(2, 70)), fill=(96, 170, 90))
# --- right: Babel tower + small city
E.city(d, 360, 480, HZ, seed=4, h0=12, h1=30)
E.tower(d, 418, HZ, 1.0, maxh=150)
# --- center: ark on a mound with rainbow
d.ellipse([150, HZ - 26, 330, HZ + 30], fill=(110, 100, 90))
d.ellipse([160, HZ - 30, 320, HZ + 10], fill=(130, 120, 106))
E.rainbow(d, 240, HZ - 20, 120, base, a=1.0)
d = ImageDraw.Draw(base)
E.ark(d, 240, HZ - 22, 0.0, 1.0, w=150, h=46, doors_open=False)
E.dove_sprite(base, 300, 92, 0.3, "dove")
# --- left: Eden tree, serpent, Adam and Eve
E.tree(d, 70, HZ + 4, 92, leaf=(40, 120, 56), style="round", fruit=(220, 50, 60), seed=2)
E.serpent(d, 92, HZ - 6, 1.1, n=18)
def put(name, x, yb, s, flip=False, pose=None):
    im = Image.fromarray(cast5.sprite(name, 0.4, 0.0, False, pose), "RGBA")
    im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    base.paste(im, (int(x - im.width / 2), int(yb - im.height)), im)
put("Adam", 30, PH - 6, 0.9)
put("Eve", 128, PH - 6, 0.9, flip=True, pose={"ra": (70, -40)})
d = ImageDraw.Draw(base)
E.apple(d, 112, PH - 66)
put("Noah", 300, PH - 4, 0.8, flip=True, pose={"la": (120, -110), "ra": (120, -110)})

# upscale + glow
big = E.upscale_post(base.convert("RGB"))
W, H = big.size
# darken top for the title
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for y in range(0, 380):
    od.line([(0, y), (W, y)], fill=(10, 6, 30, int(170 * (1 - y / 380))))
big = Image.alpha_composite(big.convert("RGBA"), ov)
dd = ImageDraw.Draw(big)
F = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
def text_c(txt, y, size, fill, stroke=14, sc=(20, 10, 30)):
    f = ImageFont.truetype(F, size); w = dd.textlength(txt, font=f)
    dd.text(((W - w) / 2 + 8, y + 10), txt, font=f, fill=(0, 0, 0, 160), stroke_width=stroke, stroke_fill=(0, 0, 0, 160))
    dd.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)
text_c("GENESIS", 20, 230, (255, 214, 90))
text_c("THE FULL STORY", 270, 92, (255, 255, 255), stroke=10)
out = big.convert("RGB").resize((1280, 720), Image.LANCZOS)
out.save("thumb_genesis.jpg", quality=92)
print(out.size)
