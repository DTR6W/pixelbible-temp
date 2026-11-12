NEWK3 = {"cain", "abraham", "samson", "jericho", "elijah", "prodigal", "samaritan", "waterwalk", "loaves", "sinai"}
CROWDC = ((220, 220, 230), (200, 90, 70), (80, 130, 200), (230, 190, 80), (110, 170, 110))

def lying(base, name, x, y, t, sc=0.6):
    im = Image.fromarray(chars.draw(name, t, 0.0, False, None), "RGBA").resize((int(100 * sc), int(120 * sc)), Image.NEAREST).rotate(90, expand=True)
    base.paste(im, (int(x - im.width / 2), int(y - im.height + 3)), im)

def mountain(d, cx, top, base_y, w, col=(130, 110, 100), snow=False):
    d.polygon([(cx - w, base_y), (cx, top), (cx + w, base_y)], fill=col)
    d.polygon([(cx, top), (cx + w, base_y), (cx + w // 3, base_y)], fill=tuple(max(0, v - 28) for v in col))
    if snow: d.polygon([(cx, top), (cx - 8, top + 12), (cx + 8, top + 12)], fill=(245, 245, 250))

def flame(d, x, y, t, s=1.0):
    for (col, r, h) in (((255, 90, 30), 8, 22), ((255, 170, 40), 6, 17), ((255, 236, 150), 3, 11)):
        r2 = r * s; h2 = h * s + 2 * math.sin(t * 12 + x)
        d.polygon([(x - r2, y), (x - r2 * 0.5, y - h2 * 0.6), (x + 1.5 * math.sin(t * 9 + r), y - h2), (x + r2 * 0.5, y - h2 * 0.6), (x + r2, y)], fill=col)

def altar_stones(d, x, y, w=30, h=12):
    d.rectangle([x - w // 2, y - h, x + w // 2, y], fill=(130, 124, 118)); d.rectangle([x - w // 2, y - h, x + w // 2, y - h + 2], fill=(170, 164, 156))
    for i in range(3): d.line([(x - w // 2 + i * (w // 3), y - h), (x - w // 2 + i * (w // 3), y)], fill=(96, 90, 86))

def pig(d, x, y, t):
    d.ellipse([x - 7, y - 8, x + 7, y], fill=(240, 170, 170)); d.ellipse([x + 5, y - 8, x + 11, y - 2], fill=(250, 190, 190)); d.point((x + 9, y - 6), fill=(60, 30, 30))
    d.line([(x - 4, y), (x - 4, y + 3)], fill=(220, 150, 150)); d.line([(x + 3, y), (x + 3, y + 3)], fill=(220, 150, 150))

def draw_new3(d, base, kind, o, t, lt):
    st = o.get("stage", "")
    if kind == "cain":
        if st in ("altar", "field"):
            grad(d, 0, HZ, (130, 200, 245), (220, 238, 246)); hills(d, 150, (150, 196, 140), 12, 1, t, 2); ground(d, (100, 160, 76))
            for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 44 + i * 14, 1.0)
        if st == "altar":
            altar_stones(d, 46, 168); altar_stones(d, 134, 168)
            flame(d, 46, 156, t, 0.7)
            for i in range(10): d.point((int(46 + 3 * math.sin(t * 2 + i) * (i / 10)), 140 - i * 4), fill=(235, 235, 235))
            for i in range(10): d.point((int(134 + i * 1.8 + 2 * math.sin(t * 2 + i)), 140 - i * 2 + (i // 2)), fill=(90, 84, 80))
            person(base, "David", 22, 170, t, 0.55); person(base, "Peter", 158, 170, t, 0.55, flip=True)
            for i in range(4): d.rectangle([128 + i * 3, 150, 129 + i * 3, 156], fill=(230, 190, 70))
            actor(base, "sheep", 66, 170, t * 0.3, 0.4, walk=0.0)
            shafts(base, t, 26, 20, 2)
        elif st == "field":
            d.rectangle([100, 150, PW, PH], fill=(214, 184, 80))
            for x in range(104, 178, 4):
                for y in range(150, 190, 8): d.line([(x, y), (x + int(math.sin(t * 2 + x) * 1.5), y - 7)], fill=(190, 150, 40))
            for i, x in enumerate((14, 34, 54)): actor(base, "sheep", x, 168 + (i % 2) * 3, t * 0.3, 0.5, walk=0.3)
            person(base, "David", 80, 168, t, 0.6); person(base, "Peter", 128, 166, t, 0.6, flip=True)
        elif st == "dark":
            grad(d, 0, HZ, (90, 30, 30), (200, 100, 70)); hills(d, 150, (60, 36, 36), 12, 1, t, 4); ground(d, (70, 56, 48))
            for i in range(4): cloud(d, ((t * 8 + i * 70) % 250) - 40, 30 + i * 12, 1.7, (70, 40, 46))
            person(base, "Peter", 90, 170, t, 0.7)
            glow(d, 90, 100, 30, (120, 30, 30), (90, 40, 40), 4) if False else None
            for i in range(8):
                x = 60 + 7 * i; d.line([(x, 120 + 3 * math.sin(t * 4 + i)), (x + 3, 108)], fill=(40, 10, 10))
        elif st == "night":
            grad(d, 0, HZ, (6, 8, 30), (50, 44, 90)); stars(d, t, 70, 120, 4); hills(d, 152, (24, 30, 60), 14, 1, t, 3); ground(d, (36, 54, 56))
            for i, x in enumerate((20, 46, 70)): actor(base, "sheep", x, 168 + (i % 2) * 3, t * 0.2, 0.5, walk=0.0)
            glow(d, 100, 150, 34, (230, 235, 255), (36, 54, 56), 6)
            sparkles(d, 100, 150, t, 8, 24)
            person(base, "Peter", 160 + int(8 * ease(lt / 5)), 170, t, 0.42, flip=False)
        elif st == "mark":
            grad(d, 0, HZ, (60, 40, 90), (255, 160, 110)); hills(d, 150, (120, 90, 90), 12, 1, t, 5); ground(d, (170, 140, 110), (150, 120, 96))
            sun(d, 140, 96, 11, t)
            x = 140 - 80 * ease_c(lt / 6.0)
            person(base, "Peter", x, 170, t, 0.64)
            star8(d, int(x + 1), 118, 4 + int(math.sin(t * 5)))
            sparkles(d, x, 120, t, 5, 12)
    elif kind == "abraham":
        if st in ("stars", "tent"):
            grad(d, 0, HZ, (4, 6, 26), (50, 44, 96)); stars(d, t, 110 if st == "stars" else 70, 130, 6); hills(d, 152, (50, 40, 70), 12, 1, t, 3); ground(d, (86, 70, 66))
            d.polygon([(108, 168), (134, 120), (160, 168)], fill=(200, 170, 120)); d.polygon([(134, 120), (134, 168), (160, 168)], fill=(176, 146, 100)); d.polygon([(128, 168), (134, 146), (140, 168)], fill=(60, 40, 30))
            if st == "stars":
                for i in range(14):
                    sx = 14 + (i * 37) % 160; sy = 14 + (i * 53) % 90
                    if int(t * 2 + i) % 3: star8(d, sx, sy, 2, (255, 240, 170))
                person(base, "Peter", 70, 170, t, 0.68)
                if lt > 3.0: person(base, "David", 94, 170, t, 0.4)
            else:
                person(base, "Peter", 70, 170, t, 0.68)
                glow(d, 90, 36, 34, (255, 245, 210), (50, 44, 96), 6); shafts(base, t, 40, 60, 2)
        elif st == "mount":
            grad(d, 0, HZ, (120, 190, 240), (230, 226, 200)); ground(d, (180, 160, 110), (160, 140, 96))
            mountain(d, 120, 40, 168, 80, (150, 122, 100)); mountain(d, 30, 90, 168, 60, (176, 150, 120))
            for i in range(4): cloud(d, ((t * 4 + i * 80) % 240) - 35, 40 + i * 12, 1.0)
            p = ease_c(lt / 5.0); x = 14 + 70 * p; y = 168 - 70 * p
            person(base, "Peter", x + 12, y, t, 0.38); person(base, "David", x, y + 2, t, 0.32)
            d.rectangle([x - 6, y - 24, x - 2, y - 22], fill=(120, 80, 50)) if False else None
        elif st == "angel":
            grad(d, 0, HZ, (255, 190, 130), (255, 236, 196)); ground(d, (180, 160, 110)); mountain(d, 150, 80, 168, 70, (150, 122, 100))
            altar_stones(d, 90, 168, 34, 12)
            person(base, "Peter", 60, 170, t, 0.62); person(base, "David", 120, 170, t, 0.45, flip=True)
            glow(d, 90, 44, 40, (255, 252, 230), (255, 214, 160), 7)
            d.polygon([(80, 34), (100, 34), (96, 62), (84, 62)], fill=(255, 255, 250))
            w = int(3 * math.sin(t * 3))
            d.polygon([(80, 38), (58, 28 - w), (62, 56), (82, 54)], fill=(250, 250, 255)); d.polygon([(100, 38), (122, 28 - w), (118, 56), (98, 54)], fill=(250, 250, 255))
            d.ellipse([84, 24, 96, 36], fill=(255, 226, 190)); d.ellipse([83, 19, 97, 24], fill=(255, 236, 140)); sparkles(d, 90, 50, t, 10, 36)
        elif st == "ram":
            grad(d, 0, HZ, (255, 170, 110), (255, 236, 190)); sun(d, 140, 90, 12, t); ground(d, (170, 150, 100))
            for x, y, r in ((50, 160, 14), (70, 164, 12), (40, 168, 10), (84, 168, 11)): d.ellipse([x - r, y - r, x + r, y + r // 2], fill=(76, 110, 60)); d.ellipse([x - r + 3, y - r + 2, x + r - 3, y], fill=(96, 140, 76))
            actor(base, "sheep", 66, 168, t * 0.4, 0.62, walk=0.0)
            d.arc([60, 142, 70, 152], 90, 300, fill=(150, 110, 60), width=2); d.arc([62, 142, 72, 152], 240, 450, fill=(150, 110, 60), width=2)
            person(base, "Peter", 112, 170, t, 0.64, flip=True); person(base, "David", 140, 170, t, 0.46, flip=True)
            sparkles(d, 66, 148, t, 10, 22)
    elif kind == "samson":
        if st == "temple":
            d.rectangle([0, 0, PW, PH], fill=(70, 54, 44)); d.rectangle([0, 0, PW, 36], fill=(46, 34, 30)); d.rectangle([0, HZ, PW, PH], fill=(130, 106, 80))
            for x in range(0, PW, 20): d.line([(x, HZ), (x - 24, PH)], fill=(110, 88, 64))
            p = ease_c((lt - 2.2) / 3.0) if scene_dur[scene_at(t)] > 5 else 0
            for sgn in (-1, 1):
                x = 90 + sgn * (26 + 36 * p)
                ang = sgn * 14 * p
                d.polygon([(x - 7 + ang, 30), (x + 7 + ang, 30), (x + 7, HZ), (x - 7, HZ)], fill=(196, 170, 120)); d.rectangle([x - 11 + ang, 26, x + 11 + ang, 34], fill=(220, 196, 140))
            d.rectangle([34, 26, 146, 34], fill=(220, 196, 140)) if p < 0.02 else None
            for i in range(26):
                dx = 70 + (i * 17) % 90; dy = 40 + ((lt * 40 + i * 11) % 120)
                if p > 0.05: d.rectangle([dx, dy, dx + 2, dy + 2], fill=(190, 170, 140))
            person(base, "David", 90, 168, t, 0.7)
            if lt < 2.2: glow(d, 90, 120, 28, (255, 240, 200), (70, 54, 44), 5)
        elif st == "lion":
            grad(d, 0, HZ, (130, 200, 245), (230, 232, 210)); hills(d, 150, (200, 180, 120), 12, 1, t, 3); ground(d, (200, 176, 120), (184, 158, 104))
            person(base, "David", 66, 168, t, 0.66)
            actor(base, "lion", 112, 170, t, 0.7, flip=True, walk=0.6)
            sparkles(d, 90, 140, t, 10, 30)
            if int(t * 3) % 2: d.line([(86, 126), (96, 130)], fill=(255, 240, 160))
        elif st == "delilah":
            d.rectangle([0, 0, PW, PH], fill=(60, 36, 48)); d.rectangle([0, HZ, PW, PH], fill=(120, 86, 70))
            d.rectangle([20, 138, 130, 166], fill=(190, 80, 90)); d.rectangle([20, 128, 130, 140], fill=(230, 210, 190))
            glow(d, 150, 80, 24, (255, 220, 130), (60, 36, 48), 5); d.rectangle([146, 40, 154, 90], fill=(110, 80, 50)) if False else None
            lying(base, "David", 76, 140, t, 0.5)
            person(base, "Mary", 146, 170, t, 0.66, flip=True)
            if int(t * 4) % 2: d.line([(130, 122), (122, 128)], fill=(240, 240, 250)); d.line([(130, 128), (122, 122)], fill=(240, 240, 250))
        elif st == "captured":
            d.rectangle([0, 0, PW, PH], fill=(30, 28, 36)); d.rectangle([0, HZ, PW, PH], fill=(56, 52, 60))
            for y in range(0, HZ, 14):
                for x in range(0, PW, 26): d.rectangle([x + (7 if (y // 14) % 2 else 0), y, x + 24 + (7 if (y // 14) % 2 else 0), y + 12], outline=(50, 46, 56))
            person(base, "David", 90, 170, t, 0.66)
            d.line([(78, 140), (60, 120)], fill=(150, 150, 160), width=2); d.line([(102, 140), (120, 120)], fill=(150, 150, 160), width=2)
            for x in (30, 150): person(base, "Solomon", x, 170, t, 0.55, flip=x > 90)
    elif kind == "jericho":
        grad(d, 0, HZ, (130, 200, 245), (230, 226, 200)); hills(d, 150, (200, 180, 120), 10, 1, t, 3); ground(d, (200, 176, 120), (184, 158, 104))
        fall = ease_c((lt - 1.2) / 2.0) if st == "fall" else 0
        if st != "rahab":
            for i in range(9):
                x = 8 + i * 20; hh = 66 - (i % 2) * 8
                off = fall * (30 + 14 * (i % 3)) * (1 if i % 2 else 0.7)
                y0 = HZ - hh + off
                d.rectangle([x, y0, x + 19, HZ + 2 - 0], fill=lerpc((190, 160, 120), (150, 120, 90), (i % 3) / 3))
                for by in range(int(y0) + 4, HZ, 8): d.line([(x, by), (x + 19, by)], fill=(130, 104, 80))
                d.rectangle([x, y0 - 4, x + 4, y0], fill=(190, 160, 120)); d.rectangle([x + 10, y0 - 4, x + 14, y0], fill=(190, 160, 120))
            if st == "fall":
                for i in range(40):
                    dx = (i * 23) % 180; dy = 100 + ((lt * 30 + i * 9) % 70)
                    if fall > 0.05: d.ellipse([dx - 3, dy - 3, dx + 3, dy + 2], fill=(220, 204, 170))
            if st in ("march", "wall", "fall"):
                n = 12 if st != "wall" else 6
                for i in range(n):
                    ang = (lt * 0.4 + i / n) * 2 * math.pi
                    x = 90 + 78 * math.cos(ang); y = 176 + 8 * math.sin(ang)
                    mini(d, x, y, (240, 240, 245) if i < 4 else CROWDC[i % 5], t, i, 2)
                    if i < 4 and st != "wall": d.rectangle([x + 1, y - 10, x + 4, y - 9], fill=(250, 210, 70))
            if st == "fall":
                glow(d, 90, 40, 20 * min(1, fall * 3), (255, 255, 255), (130, 200, 245), 4)
        else:
            d.rectangle([40, 40, 140, HZ], fill=(176, 146, 110)); d.rectangle([40, 40, 140, 46], fill=(200, 170, 130))
            for by in range(52, HZ, 8): d.line([(40, by), (140, by)], fill=(130, 104, 80))
            d.rectangle([76, 76, 104, 112], fill=(40, 28, 24)); d.line([(90, 100), (90, 160)], fill=(210, 30, 40), width=2)
            person(base, "Mary", 90, 112, t, 0.4)
            sparkles(d, 90, 80, t, 8, 20)
            for x in (20, 160): person(base, "Peter", x, 170, t, 0.5, flip=x > 90)
    elif kind == "elijah":
        if st in ("drought", "altars", "silent", "fire", "rain"):
            if st == "rain":
                grad(d, 0, HZ, (50, 60, 90), (150, 160, 190)); ground(d, (110, 130, 80))
                for i in range(5): cloud(d, ((t * 8 + i * 55) % 250) - 40, 24 + (i % 3) * 14, 1.7, (80, 90, 120))
                rain(d, t, 80, (170, 190, 230), 0, 180)
                for i in range(12): mini(d, 14 + i * 14, 170 + (i % 2) * 4, CROWDC[i % 5], t, i)
                person(base, "Peter", 90, 168, t, 0.66)
            else:
                dry = st == "drought"
                grad(d, 0, HZ, (255, 190, 110), (255, 236, 190)) if dry else grad(d, 0, HZ, (130, 200, 245), (230, 226, 200))
                if dry: sun(d, 140, 50, 14, t)
                hills(d, 150, (160, 130, 90), 12, 1, t, 2); ground(d, (196, 168, 110), (170, 140, 90))
                rr = random.Random(7)
                for _ in range(22):
                    x = rr.randrange(180); y = rr.randrange(HZ + 6, 230); d.line([(x, y), (x + 5, y + 2)], fill=(150, 120, 80)); d.line([(x + 3, y), (x + 4, y + 5)], fill=(150, 120, 80))
                if dry:
                    for x in (20, 150): d.line([(x, 166), (x, 120)], fill=(90, 66, 44), width=2); d.line([(x, 130), (x - 8, 118)], fill=(90, 66, 44)); d.line([(x, 138), (x + 9, 126)], fill=(90, 66, 44))
                    for i in range(8): mini(d, 100 + i * 9, 170 + (i % 2) * 3, (200, 40, 50), t, i)
                    person(base, "Peter", 50, 170, t, 0.66)
                if st == "altars":
                    altar_stones(d, 50, 168, 36, 14); altar_stones(d, 134, 168, 36, 14)
                    for x in (50, 134): d.rectangle([x - 5, 150, x + 5, 154], fill=(120, 70, 44))
                    person(base, "Peter", 20, 170, t, 0.55)
                    for i in range(5): mini(d, 160 + (i % 3) * 5, 170 + (i // 3) * 5, (200, 40, 50), t, i)
                if st == "silent":
                    altar_stones(d, 90, 168, 36, 14); d.rectangle([85, 150, 95, 154], fill=(120, 70, 44))
                    for i in range(8):
                        ang = i / 8 * 2 * math.pi + t * 0.8; x = 90 + 44 * math.cos(ang); y = 172 + 6 * math.sin(ang)
                        mini(d, x, y - int(abs(math.sin(t * 5 + i)) * 4), (200, 40, 50), t, i)
                    sun(d, 90, 60, 12, t)
                    d.text((82, 24), "...", fill=(120, 90, 60)) if False else None
                if st == "fire":
                    altar_stones(d, 90, 168, 40, 16)
                    for x in (40, 60, 120, 140): d.ellipse([x - 7, 170, x + 7, 176], fill=(60, 120, 200))
                    p = ease((lt - 2.0) / 0.6)
                    if lt > 2.0:
                        d.polygon([(90, 0), (86 + 3 * math.sin(t * 20), 60), (94, 60)], fill=(255, 240, 160)) if lt < 2.8 else None
                        glow(d, 90, 140, 40 * p, (255, 240, 180), (196, 168, 110), 6)
                        for i, x in enumerate((72, 82, 90, 98, 108)): flame(d, x, 150, t + i, 1.1 * p)
                    person(base, "Peter", 30, 170, t, 0.62)
                    for i in range(6): mini(d, 140 + (i % 3) * 6, 170 + (i // 3) * 5, (200, 40, 50), t, i)
    elif kind == "prodigal":
        if st in ("home", "leave", "hug", "feast"):
            grad(d, 0, HZ, (130, 200, 245), (230, 238, 226)); hills(d, 150, (140, 190, 130), 14, 1, t, 2); ground(d, (110, 162, 80))
            for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 44 + i * 14, 1.0)
        if st == "home":
            house(d, 100, 160, 56, 44, False, True, (210, 180, 130))
            person(base, "Peter", 50, 170, t, 0.66); person(base, "David", 78, 170, t, 0.56); person(base, "Peter", 22, 170, t, 0.5, flip=False)
            for x in (10, 170): tree(d, x, 166, 38, (60, 140, 70), sway=1.0, t=t)
        elif st == "leave":
            d.polygon([(0, 170), (180, 150), (180, 160), (0, 190)], fill=(196, 170, 120))
            house(d, 6, 160, 40, 32, False, True, (210, 180, 130))
            person(base, "Peter", 34, 172, t, 0.6)
            sx = 60 + 80 * ease_c(lt / 5.0); person(base, "David", sx, 170 - int((sx - 60) * 0.1), t, 0.5, flip=True)
            for i in range(5): d.rectangle([sx + 8 + i, 138 + (i % 2), sx + 10 + i, 140 + (i % 2)], fill=(255, 220, 90)) if int(t * 4 + i) % 2 else None
        elif st == "pigs":
            grad(d, 0, HZ, (80, 70, 80), (180, 160, 140)); ground(d, (100, 76, 56), (84, 62, 46))
            d.rectangle([0, 150, PW, 175], fill=(80, 60, 44))
            for i, x in enumerate((30, 62, 120, 150)): pig(d, x, 168 + (i % 2) * 4, t)
            person(base, "David", 90, 172, t, 0.6)
            for x in range(10, 170, 20): d.rectangle([x, 128, x + 3, 160], fill=(110, 80, 50))
            d.line([(8, 136), (172, 136)], fill=(110, 80, 50), width=2); d.line([(8, 148), (172, 148)], fill=(110, 80, 50), width=2)
        elif st == "hug":
            d.polygon([(0, 170), (180, 150), (180, 160), (0, 190)], fill=(196, 170, 120))
            house(d, 130, 160, 44, 36, False, True, (210, 180, 130))
            q = ease_c(lt / 3.5)
            person(base, "David", 20 + 56 * q, 172, t, 0.56); person(base, "Peter", 120 - 40 * q, 172, t, 0.62, flip=True)
            if q > 0.95:
                for i in range(6): d.polygon([(90 + i * 3 - 8, 120 - (t * 14 + i * 6) % 24), (92 + i * 3 - 8, 118 - (t * 14 + i * 6) % 24), (94 + i * 3 - 8, 120 - (t * 14 + i * 6) % 24)], fill=(255, 90, 120))
                sparkles(d, 90, 150, t, 10, 30)
        elif st == "feast":
            d.rectangle([0, 0, PW, PH], fill=(120, 70, 40)); d.rectangle([0, 0, PW, 44], fill=(90, 50, 30)); d.rectangle([0, HZ, PW, PH], fill=(170, 130, 90))
            for x in range(14, 180, 32): d.line([(x, 0), (x + 8, 36)], fill=(240, 200, 90)); d.ellipse([x + 6, 34, x + 11, 40], fill=(255, 230, 130))
            d.rectangle([30, 140, 150, 168], fill=(140, 90, 56)); d.rectangle([30, 140, 150, 144], fill=(230, 200, 150))
            for i in range(6): d.ellipse([40 + i * 18, 132, 50 + i * 18, 140], fill=((230, 70, 70), (250, 200, 70), (150, 200, 90))[i % 3])
            person(base, "Peter", 20, 170, t, 0.55); person(base, "David", 90, 138, t, 0.5); person(base, "Peter", 162, 170, t, 0.55, flip=True)
            for i in range(6): mini(d, 30 + i * 24 + int(3 * math.sin(t * 4 + i)), 176 + (i % 2) * 4, CROWDC[i % 5], t, i)
            sparkles(d, 90, 120, t, 10, 40)
    elif kind == "samaritan":
        grad(d, 0, HZ, (255, 200, 140), (255, 240, 200)) if st != "hurt" else grad(d, 0, HZ, (150, 130, 130), (230, 200, 170))
        hills(d, 150, (200, 160, 110), 12, 1, t, 3); ground(d, (206, 178, 120), (186, 158, 104)); sun(d, 150, 50, 10, t)
        if st != "inn":
            d.polygon([(0, 176), (180, 156), (180, 168), (0, 200)], fill=(176, 146, 100))
        if st == "hurt":
            lying(base, "Peter", 90, 180, t, 0.5)
            for i in range(3): mini(d, 20 + int(((lt * 14) + i * 10) % 60), 164 + (i % 2) * 4, (40, 30, 30), t, i)
        elif st == "pass":
            lying(base, "Peter", 90, 182, t, 0.46)
            p1 = ease_c(lt / 3.4); person(base, "Solomon", -10 + 200 * p1, 164, t, 0.5)
            if lt > 3.2: person(base, "Peter", 190 - 200 * ease_c((lt - 3.2) / 3.0), 166, t, 0.5, flip=True)
        elif st == "help":
            lying(base, "Peter", 78, 182, t, 0.46)
            person(base, "David", 112, 172, t, 0.6, flip=True)
            glow(d, 80, 160, 14, (255, 240, 200), (206, 178, 120), 4); sparkles(d, 80, 162, t, 8, 18)
            d.ellipse([140, 150, 164, 164], fill=(150, 144, 140)); d.rectangle([158, 140, 162, 152], fill=(150, 144, 140))
        elif st == "inn":
            d.rectangle([0, HZ, PW, PH], fill=(196, 168, 112))
            house(d, 70, 164, 90, 60, False, True, (214, 182, 130))
            d.rectangle([108, 112, 124, 164], fill=(70, 46, 34))
            person(base, "Peter", 50, 172, t, 0.58); person(base, "David", 24, 172, t, 0.58)
            for i in range(4): d.ellipse([34 + i * 3, 144 - (t * 10 + i * 6) % 14, 38 + i * 3, 148 - (t * 10 + i * 6) % 14], fill=(255, 220, 90))
    elif kind == "waterwalk":
        calm = st == "calm"
        if calm: grad(d, 0, HZ, (255, 170, 120), (255, 236, 190)); sun(d, 140, 100, 12, t)
        else: grad(d, 0, HZ, (10, 14, 40), (60, 64, 100)); stars(d, t, 30, 100, 9); d.ellipse([20, 28, 40, 48], fill=(240, 240, 220))
        d.rectangle([0, 126, PW, PH], fill=(60, 120, 190) if calm else (20, 40, 90))
        for k in range(5): waves(d, 126 + k * 9, 140 + k * 9, (150, 200, 240) if calm else (70, 110, 170), t * (1 if calm else 2.2) + k)
        if not calm: rain(d, t, 60, (150, 170, 210), 0, 160)
        bx = 130 if st != "calm" else 90
        boat(d, bx, 134, t, 0 if calm else 6 * math.sin(t * 2.5))
        for i in range(3): person(base, "Peter", bx - 10 + i * 8, 130 + int(1.5 * math.sin(t * 2.1)), t, 0.3)
        if st == "far":
            glow(d, 40, 126, 16, (255, 250, 220), (20, 40, 90), 4); person(base, "Jesus", 40, 138 + int(math.sin(t * 2)), t, 0.5)
        if st == "near":
            glow(d, 80, 120, 22, (255, 250, 220), (20, 40, 90), 5); person(base, "Jesus", 80 + 6 * math.sin(t), 142, t, 0.62); sparkles(d, 80, 124, t, 8, 20)
        if st == "sink":
            glow(d, 56, 120, 20, (255, 250, 220), (20, 40, 90), 5); person(base, "Jesus", 56, 142, t, 0.62)
            person(base, "Peter", 96, 150 + int(8 * ease(lt / 4)), t, 0.4)
            for i in range(6): d.ellipse([88 + i * 3, 148 - (t * 12 + i * 5) % 12, 91 + i * 3, 151 - (t * 12 + i * 5) % 12], outline=(200, 230, 250))
            d.rectangle([0, 152 + int(8 * ease(lt / 4)), PW, PH], fill=(20, 40, 90))
            for k in range(3): waves(d, 156 + k * 9, 166 + k * 9, (70, 110, 170), t * 2 + k)
        if calm:
            person(base, "Jesus", bx + 18, 130, t, 0.34); sparkles(d, bx, 110, t, 8, 24)
    elif kind == "loaves":
        grad(d, 0, HZ, (130, 200, 245), (225, 238, 226)); hills(d, 150, (140, 190, 130), 14, 1, t, 2); ground(d, (110, 162, 80))
        for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 44 + i * 14, 1.0)
        if st in ("crowd", "feast", "baskets", "boy"):
            rows = 4 if st != "boy" else 2
            for r_ in range(rows):
                for i in range(17 if st != "boy" else 9):
                    x = 6 + i * (10 if st != "boy" else 20) + (r_ % 2) * 4; y = 148 + r_ * 9
                    mini(d, x, y, CROWDC[(i + r_) % 5], t, i + r_)
        if st == "crowd":
            person(base, "Jesus", 90, 150, t, 0.5); person(base, "Peter", 120, 152, t, 0.38)
        if st == "boy":
            person(base, "Jesus", 70, 160, t, 0.58); person(base, "David", 110, 164, t, 0.4, flip=True)
            d.rectangle([116, 146, 126, 152], fill=(150, 104, 60))
            for i in range(5): d.ellipse([117 + i * 2, 143, 121 + i * 2, 147], fill=(220, 170, 90))
            for i in range(2): d.ellipse([117 + i * 4, 148, 124 + i * 4, 151], fill=(130, 170, 200))
            glow(d, 120, 144, 14, (255, 250, 200), (110, 162, 80), 4)
        if st == "feast":
            for i in range(12):
                x = 50 + (i * 11) % 80; y = 128 + ((t * 18 + i * 13) % 26)
                d.ellipse([x, 120 + (i * 7) % 20 - int((t * 8 + i) % 10), x + 4, 124 + (i * 7) % 20 - int((t * 8 + i) % 10)], fill=(224, 176, 96))
            glow(d, 90, 128, 22, (255, 250, 210), (140, 190, 110), 5); person(base, "Jesus", 90, 164, t, 0.62); sparkles(d, 90, 140, t, 12, 36)
        if st == "baskets":
            for i in range(12):
                x = 10 + (i % 6) * 28; y = 132 + (i // 6) * 18
                p = ease((lt - i * 0.18) / 0.4)
                if p > 0:
                    d.rectangle([x, y, x + 16, y + 10], fill=(150, 104, 60)); d.rectangle([x, y, x + 16, y + 2], fill=(190, 140, 80))
                    for j in range(3): d.ellipse([x + 2 + j * 4, y - 3, x + 6 + j * 4, y + 1], fill=(224, 176, 96))
    elif kind == "sinai":
        if st == "people":
            grad(d, 0, HZ, (130, 200, 245), (230, 226, 200)); ground(d, (200, 176, 120), (184, 158, 104)); mountain(d, 140, 40, 168, 60, (120, 96, 84))
            for i, x in enumerate((20, 50, 80, 110)):
                d.polygon([(x - 12, 170), (x, 146), (x + 12, 170)], fill=(214, 190, 150)); d.polygon([(x, 146), (x + 12, 170), (x + 3, 170)], fill=(184, 160, 120))
            for i in range(10): mini(d, 14 + i * 16 + int(3 * math.sin(t + i)), 174 + (i % 2) * 4, CROWDC[i % 5], t, i)
        else:
            grad(d, 0, HZ, (40, 40, 70), (150, 130, 130)); ground(d, (110, 90, 80)); mountain(d, 100, 30, 168, 90, (96, 80, 76))
            for i in range(4): cloud(d, ((t * 6 + i * 70) % 250) - 40, 24 + (i % 3) * 10, 1.8, (110, 110, 130))
            if int(t * 1.7) % 3 == 0: d.line([(100, 30), (92, 52), (102, 52), (94, 78)], fill=(255, 250, 200), width=2)
            if st == "mount":
                p = ease_c(lt / 5.0); person(base, "Moses", 50 + 36 * p, 168 - 66 * p, t, 0.42)
            else:
                glow(d, 90, 112, 40, (255, 250, 220), (110, 90, 80), 6)
                person(base, "Moses", 90, 170, t, 0.7)
                for sgn in (-1, 1):
                    x = 90 + sgn * 16; d.rectangle([x - 9, 96, x + 9, 134], fill=(190, 186, 182)); d.pieslice([x - 9, 88, x + 9, 106], 180, 360, fill=(190, 186, 182))
                    for j in range(5): d.line([(x - 5, 104 + j * 6), (x + 5, 104 + j * 6)], fill=(110, 106, 100))
                sparkles(d, 90, 112, t, 10, 34)
