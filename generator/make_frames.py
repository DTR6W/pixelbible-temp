import random, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = sys.argv[1]
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

scenes = [
    ("intro", None, "3 FATOS\nCURIOSOS\nSOBRE O\nESPAÇO", "Fique até o final", (255, 210, 90)),
    ("f1", "FATO 1", "Em Vênus, um dia dura mais que um ano", "Vênus leva cerca de 243 dias terrestres para girar uma vez, mas só 225 para dar a volta no Sol.", (120, 200, 255)),
    ("f2", "FATO 2", "O Sol tem quase toda a massa do Sistema Solar", "Ele concentra cerca de 99,86% da massa. Todos os planetas juntos ficam com o resto.", (255, 150, 110)),
    ("f3", "FATO 3", "A luz do Sol leva 8 minutos para chegar aqui", "Cerca de 8 minutos e 20 segundos. Se o Sol sumisse agora, só perceberíamos depois disso.", (160, 255, 190)),
    ("outro", None, "GOSTOU?", "Siga o canal para mais curiosidades", (255, 210, 90)),
]

def bg(seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H))
    px = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        px.line([(0, y), (W, y)], fill=(int(8 + 14 * t), int(10 + 8 * t), int(32 + 40 * t)))
    d = ImageDraw.Draw(img)
    for _ in range(220):
        x, y = rnd.randrange(W), rnd.randrange(H)
        r = rnd.choice([1, 1, 2, 2, 3])
        c = rnd.randint(150, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, c))
    return img

def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            test = (line + " " + w).strip()
            if d.textlength(test, font=font) <= maxw:
                line = test
            else:
                out.append(line)
                line = w
        out.append(line)
    return out

def centered(d, lines, font, y, fill, gap):
    for ln in lines:
        w = d.textlength(ln, font=font)
        d.text(((W - w) / 2, y), ln, font=font, fill=fill)
        y += font.size + gap
    return y

for i, (name, tag, title, sub, color) in enumerate(scenes):
    img = bg(i + 1)
    d = ImageDraw.Draw(img)
    MAXW = W - 160
    if tag is None:
        tfont = ImageFont.truetype(BOLD, 150 if name == "intro" else 170)
        lines = wrap(d, title, tfont, MAXW)
        block = len(lines) * (tfont.size + 20)
        y = (H - block) // 2 - 120
        y = centered(d, lines, tfont, y, color, 20)
        sfont = ImageFont.truetype(REG, 56)
        sl = wrap(d, sub, sfont, MAXW)
        centered(d, sl, sfont, y + 80, (230, 235, 255), 16)
    else:
        gfont = ImageFont.truetype(BOLD, 72)
        w = d.textlength(tag, font=gfont)
        d.rounded_rectangle([(W - w) / 2 - 50, 330, (W + w) / 2 + 50, 330 + 120], 60, fill=color)
        d.text(((W - w) / 2, 330 + 14), tag, font=gfont, fill=(10, 12, 35))
        tfont = ImageFont.truetype(BOLD, 96)
        lines = wrap(d, title, tfont, MAXW)
        y = centered(d, lines, tfont, 560, (255, 255, 255), 20)
        d.rectangle([W / 2 - 90, y + 40, W / 2 + 90, y + 52], fill=color)
        sfont = ImageFont.truetype(REG, 56)
        sl = wrap(d, sub, sfont, MAXW)
        centered(d, sl, sfont, y + 130, (205, 215, 245), 18)
    img.save(f"{OUT}/{name}.png")
print("ok")
