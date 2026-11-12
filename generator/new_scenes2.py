NEWK2 = {"plague", "palace2", "babel", "joseph"}

def house(d, x, y, w=30, h=26, door_red=False, lit=True, col=(190, 150, 100)):
    d.rectangle([x, y - h, x + w, y], fill=col); d.rectangle([x - 2, y - h - 3, x + w + 2, y - h], fill=tuple(max(0, v - 30) for v in col))
    dw = 8; dx = x + w // 2 - dw // 2
    d.rectangle([dx, y - 14, dx + dw, y], fill=(60, 40, 30))
    if door_red:
        d.rectangle([dx - 2, y - 17, dx + dw + 2, y - 15], fill=(200, 30, 40)); d.rectangle([dx - 2, y - 17, dx - 1, y], fill=(200, 30, 40)); d.rectangle([dx + dw + 1, y - 17, dx + dw + 2, y], fill=(200, 30, 40))
    if lit: d.rectangle([x + 3, y - h + 5, x + 7, y - h + 10], fill=(255, 220, 130))

def frog(d, x, y, ph):
    h = abs(math.sin(ph * math.pi)) * 8
    y = y - h
    d.ellipse([x - 3, y - 3, x + 3, y + 1], fill=(70, 170, 70)); d.point((int(x - 2), int(y - 4)), fill=(250, 250, 200)); d.point((int(x + 2), int(y - 4)), fill=(250, 250, 200))
    d.line([(x - 3, y + 1), (x - 5, y + 3)], fill=(50, 130, 50)); d.line([(x + 3, y + 1), (x + 5, y + 3)], fill=(50, 130, 50))

def locusts(d, t, n=90, y0=20, y1=160):
    rr = random.Random(12)
    for i in range(n):
        x = (rr.uniform(0, PW + 30) + t * (30 + i % 7 * 4)) % (PW + 30) - 15
        y = rr.uniform(y0, y1) + 4 * math.sin(t * 9 + i)
        d.rectangle([x, y, x + 2, y + 1], fill=(120, 96, 40)); d.point((int(x + 1), int(y - 1)), fill=(200, 190, 130))

def nile(d, t, blood=False):
    c0, c1 = ((150, 24, 30), (200, 50, 50)) if blood else ((50, 120, 190), (130, 190, 240))
    d.rectangle([0, 128, PW, PH], fill=c0)
    for k in range(4): waves(d, 128 + k * 9, 140 + k * 9, c1, t + k)

def draw_new2(d, base, kind, o, t, lt):
    st = o.get("stage", "")
    if kind == "plague":
        if st == "blood":
            grad(d, 0, HZ, (120, 60, 60), (230, 170, 120)); hills(d, 150, (110, 70, 50), 12, 1, t, 3); nile(d, t, True)
            d.rectangle([0, 110, PW, 130], fill=(206, 176, 120))
            for x in (10, 40, 150, 170):
                d.line([(x, 130), (x, 70)], fill=(80, 100, 50), width=2); d.polygon([(x, 70), (x - 8, 80), (x + 8, 80)], fill=(70, 130, 60))
            for i in range(4): bird(d, ((t * 8 + i * 50) % 220) - 10, 50 + 5 * math.sin(t + i), t, (90, 40, 40))
            sun(d, 140, 50, 9, t)
        elif st == "seq":
            ph = int(lt / 2.2) % 4
            if ph == 0:
                grad(d, 0, HZ, (120, 190, 240), (210, 232, 245)); ground(d, (110, 160, 80)); nile(d, t, True)
                d.rectangle([0, 100, PW, 128], fill=(206, 176, 120))
            elif ph == 1:
                grad(d, 0, HZ, (130, 200, 245), (215, 236, 246)); ground(d, (90, 150, 70)); d.rectangle([0, 150, PW, PH], fill=(60, 130, 190))
                for i in range(16): frog(d, 10 + i * 11, 168 + (i % 3) * 7, ((t * 1.6 + i * 0.27) % 1))
            elif ph == 2:
                grad(d, 0, HZ, (150, 130, 90), (230, 200, 130)); ground(d, (190, 160, 100)); locusts(d, t, 130)
                for x, h in ((20, 40), (150, 36)): tree(d, x, 164, h, (90, 110, 60), sway=1.0, t=t)
            else:
                grad(d, 0, PH, (4, 4, 10), (8, 8, 18)); stars(d, t, 4, 60, 2)
                house(d, 66, 168, 44, 34, False, True, (60, 50, 44))
                glow(d, 88, 150, 30, (255, 200, 110), (8, 8, 18), 5)
            ov = 0.5 + 0.5 * math.sin(lt * 3)
        elif st == "door":
            grad(d, 0, HZ, (10, 12, 40), (60, 50, 90)); stars(d, t, 50, 110, 5); ground(d, (80, 64, 56))
            house(d, 60, 168, 60, 50, True, True, (196, 156, 106))
            person(base, "Peter", 32, 170, t, 0.5) if lt > 1.5 else None
            if lt > 0.3:
                p = min(1, (lt - 0.3) / 2.5)
                d.line([(86, 130 + 6 * math.sin(t * 8)), (86 + int(2 * p), 130)], fill=(200, 30, 40), width=1)
            sparkles(d, 90, 140, t, 6, 18)
            for i in range(3): d.ellipse([140 + i * 8, 158, 150 + i * 8, 166], fill=(240, 240, 235)) if False else None
            actor(base, "sheep", 150, 168, t * 0.3, 0.5, walk=0.0)
        elif st == "passover":
            grad(d, 0, HZ, (6, 8, 30), (50, 40, 90)); stars(d, t, 60, 110, 8); ground(d, (60, 50, 70))
            for i, x in enumerate((8, 66, 124)): house(d, x, 168, 48, 40, i != 5, True, (150, 120, 90))
            # moving shadow passing over (angel glow)
            ax = -20 + (lt * 26) % 240; ay = 90 + 6 * math.sin(t * 2)
            glow(d, ax, ay, 22, (230, 240, 255), (50, 40, 90), 5)
            d.polygon([(ax - 3, ay - 6), (ax + 3, ay - 6), (ax + 2, ay + 8), (ax - 2, ay + 8)], fill=(250, 250, 255))
            d.polygon([(ax - 3, ay - 4), (ax - 12, ay - 10 + 2 * math.sin(t * 6)), (ax - 4, ay + 2)], fill=(240, 244, 255)); d.polygon([(ax + 3, ay - 4), (ax + 12, ay - 10 + 2 * math.sin(t * 6)), (ax + 4, ay + 2)], fill=(240, 244, 255))
            for i in range(3):
                x = (8, 66, 124)[i]; dx = x + 24 - 4
                d.rectangle([dx - 2, 151, dx + 10, 153], fill=(200, 30, 40)); d.rectangle([dx - 2, 151, dx - 1, 168], fill=(200, 30, 40)); d.rectangle([dx + 9, 151, dx + 10, 168], fill=(200, 30, 40))
            motes(d, t, 12, (200, 220, 255), 40, 180)
        elif st == "freedom":
            grad(d, 0, HZ, (255, 170, 110), (255, 236, 190)); hills(d, 150, (200, 160, 110), 12, 1, t, 4); ground(d, (214, 184, 120), (196, 166, 104))
            sun(d, 90, 108, 14, t)
            n = 26
            for i in range(n):
                x = ((lt * 14 + i * 7) % 220) - 20
                mini(d, x, 164 + (i % 3) * 4, ((220, 220, 230), (200, 90, 70), (80, 130, 200), (230, 190, 80))[i % 4], t, i)
            for i in range(3): actor(base, ("sheep", "deer", "sheep")[i], ((lt * 12 + i * 70) % 230) - 20, 170, t, 0.45, walk=1.0)
    elif kind == "palace2":
        d.rectangle([0, 0, PW, PH], fill=(84, 52, 24)); d.rectangle([0, 0, PW, 36], fill=(60, 36, 20))
        for x in (6, 62, 118, 168):
            d.rectangle([x, 30, x + 10, HZ], fill=(220, 190, 120)); d.rectangle([x - 2, 28, x + 12, 34], fill=(240, 214, 150))
            d.rectangle([x + 3, 40, x + 7, 44], fill=(70, 120, 180)); d.rectangle([x + 3, 60, x + 7, 64], fill=(190, 60, 60))
        d.rectangle([0, HZ, PW, PH], fill=(170, 140, 90))
        for x in range(0, PW, 18): d.line([(x, HZ), (x - 20, PH)], fill=(150, 120, 74))
        d.rectangle([66, 70, 114, 150], fill=(60, 110, 160)); d.rectangle([62, 96, 118, 104], fill=(230, 190, 70)); d.rectangle([66, 150, 114, 166], fill=(170, 130, 50))
        person(base, "Solomon", 90, 168, t, 0.68)
        d.polygon([(80, 86), (100, 86), (96, 76), (84, 76)], fill=(230, 190, 70)) if False else None
        sh = 4 * math.sin(lt * 5) if lt > 3.5 else 0
        person(base, "Peter", 34 + sh, 168, t, 0.55)
        person(base, "David", 150, 168, t, 0.55, flip=True)
        motes(d, t, 8, (255, 230, 160), 60, 170)
    elif kind == "babel":
        if st == "confuse":
            grad(d, 0, HZ, (80, 70, 110), (200, 150, 130))
        elif st == "scatter":
            grad(d, 0, HZ, (255, 170, 110), (255, 232, 190))
        else:
            grad(d, 0, HZ, (120, 190, 240), (230, 220, 190))
        hills(d, 152, (210, 176, 120), 10, 1, t, 3); ground(d, (214, 186, 126), (196, 166, 104))
        for i in range(2): cloud(d, ((t * 4 + i * 100) % 240) - 35, 40 + i * 16, 1.0, (250, 246, 240))
        lev = {"plain": 0.0, "build": ease(lt / 5.0) * 0.8 + 0.1, "confuse": 0.85, "scatter": 0.85}.get(st, 0.5)
        cx = 90 if st != "plain" else 90
        levels = int(8 * lev)
        for i in range(levels):
            w = 76 - i * 8; yy = 166 - i * 14
            d.rectangle([cx - w // 2, yy - 14, cx + w // 2, yy], fill=lerpc((196, 140, 90), (160, 104, 66), i / 8)); d.rectangle([cx - w // 2, yy - 14, cx + w // 2, yy - 12], fill=(226, 176, 120))
            for bx in range(cx - w // 2 + 4, cx + w // 2 - 4, 8): d.line([(bx, yy - 12), (bx, yy - 1)], fill=(120, 80, 50))
        if levels < 8 and st in ("build",):
            yy = 166 - levels * 14
            d.line([(cx + 22, yy), (cx + 22, yy - 30)], fill=(100, 70, 44), width=2); d.line([(cx + 22, yy - 30), (cx + 8, yy - 26)], fill=(100, 70, 44), width=1)
            d.rectangle([cx + 6, yy - 26 + int(3 * math.sin(t * 4)), cx + 10, yy - 22 + int(3 * math.sin(t * 4))], fill=(170, 120, 80))
        if st == "plain":
            for i in range(16): mini(d, 14 + i * 10 + int(4 * math.sin(t + i)), 168 + (i % 3) * 4, ((220, 220, 230), (200, 90, 70), (80, 130, 200), (230, 190, 80))[i % 4], t, i)
        if st == "build":
            for i in range(10):
                mini(d, 14 + i * 16 + int(5 * math.sin(t * 1.3 + i)), 168 + (i % 2) * 4, ((220, 220, 230), (200, 90, 70), (80, 130, 200))[i % 3], t, i)
        if st == "confuse":
            f = ImageFont.load_default()
            marks = ("?", "!", "#", "@", "*", "&")
            for i in range(10):
                px_ = 14 + i * 16; mini(d, px_, 168 + (i % 2) * 4, ((220, 220, 230), (200, 90, 70), (80, 130, 200))[i % 3], t, i)
                if int(t * 2 + i) % 3 == 0:
                    bxx = px_ - 3; byy = 138 - (i % 3) * 8
                    d.rectangle([bxx, byy, bxx + 8, byy + 7], fill=(255, 255, 255)); d.point((bxx + 2, byy + 3), fill=(20, 20, 40)); d.point((bxx + 4, byy + 2), fill=(200, 40, 40)); d.point((bxx + 6, byy + 4), fill=(40, 40, 200))
            glow(d, 90, 44, 26, (255, 255, 230), (80, 70, 110), 5)
        if st == "scatter":
            for i in range(14):
                dirn = -1 if i % 2 else 1
                x = 90 + dirn * (8 + ((lt * 18 + i * 9) % 100)); mini(d, x, 168 + (i % 3) * 4, ((220, 220, 230), (200, 90, 70), (80, 130, 200), (230, 190, 80))[i % 4], t, i)
    elif kind == "joseph":
        if st in ("coat", "forgive"):
            if st == "coat":
                grad(d, 0, HZ, (120, 190, 240), (215, 236, 246)); hills(d, 150, (160, 190, 130), 12, 1, t, 2); ground(d, (110, 160, 80))
                for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 44 + i * 14, 1.0)
                for i, x in enumerate((20, 150, 168)): actor(base, "sheep", x, 168 + (i % 2) * 3, t * 0.3, 0.5, walk=0.3)
                person(base, "David", 80, 168, t, 0.66)
                cols = [(230, 60, 70), (250, 190, 50), (70, 180, 90), (70, 130, 230), (170, 80, 210)]
                for i, c in enumerate(cols):
                    d.rectangle([70 + i * 4, 128 + abs(2 - i), 73 + i * 4, 154 + abs(2 - i)], fill=c)
                for x, nm in ((28, "Peter"), (136, "Peter")): person(base, nm, x, 168, t, 0.55, flip=x > 90)
                sparkles(d, 90, 120, t, 5, 20)
            else:
                d.rectangle([0, 0, PW, PH], fill=(84, 52, 24)); d.rectangle([0, 0, PW, 36], fill=(60, 36, 20))
                for x in (6, 62, 118, 168): d.rectangle([x, 30, x + 10, HZ], fill=(220, 190, 120)); d.rectangle([x - 2, 28, x + 12, 34], fill=(240, 214, 150))
                d.rectangle([0, HZ, PW, PH], fill=(170, 140, 90))
                d.rectangle([66, 70, 114, 150], fill=(60, 110, 160)); d.rectangle([62, 96, 118, 104], fill=(230, 190, 70))
                person(base, "Solomon", 90, 168, t, 0.68)
                person(base, "David", 56, 168, t, 0.58)
                for x in (136, 154): person(base, "Peter", x, 168, t, 0.5, flip=True)
                cols = [(230, 60, 70), (250, 190, 50), (70, 180, 90), (70, 130, 230)]
                for i, c in enumerate(cols): d.rectangle([48 + i * 4, 132 + abs(1 - i), 51 + i * 4, 154], fill=c)
                p = (lt * 0.4) % 1
                sparkles(d, 96, 120, t, 8, 24)
        elif st == "pit":
            grad(d, 0, HZ, (240, 190, 120), (255, 236, 190)); ground(d, (200, 170, 110), (186, 154, 98)); hills(d, 152, (200, 160, 110), 10, 1, t, 3)
            d.ellipse([60, 156, 120, 176], fill=(40, 28, 22)); d.ellipse([64, 158, 116, 172], fill=(20, 14, 12))
            for i, x in enumerate((20, 40, 130, 150)): person(base, "Peter", x, 168, t, 0.5, flip=x > 90)
            if lt > 3.0:
                for i in range(2):
                    cx = ((lt - 3.0) * 20 + i * 44) % 230 - 20
                    d.ellipse([cx - 9, 154, cx + 7, 166], fill=(170, 120, 70)); d.rectangle([cx + 6, 144, cx + 9, 156], fill=(170, 120, 70)); d.ellipse([cx + 6, 140, cx + 14, 148], fill=(150, 104, 60))
                    for lx in (cx - 6, cx + 3): d.line([(lx, 165), (lx, 171 + int(math.sin(t * 7 + lx)))], fill=(120, 80, 50))
            else:
                person(base, "David", 90, 150 + int(2 * math.sin(t * 3)), t, 0.4)
        elif st == "prison":
            d.rectangle([0, 0, PW, PH], fill=(34, 32, 40)); d.rectangle([0, HZ, PW, PH], fill=(60, 56, 64))
            for y in range(0, HZ, 14):
                for x in range(0, PW, 26): d.rectangle([x + (7 if (y // 14) % 2 else 0), y, x + 24 + (7 if (y // 14) % 2 else 0), y + 12], outline=(54, 50, 60))
            d.polygon([(70, 0), (110, 0), (140, HZ), (40, HZ)], fill=(50, 56, 90)) if False else None
            shafts(base, t, 40, 60, 2)
            person(base, "David", 90, 168, t, 0.66)
            for x in range(20, 161, 14): d.rectangle([x, 20, x + 2, 168], fill=(120, 124, 136)); d.point((x, 22), fill=(200, 204, 214))
            d.rectangle([20, 20, 162, 24], fill=(100, 104, 116)); d.rectangle([20, 160, 162, 168], fill=(100, 104, 116))
            if int(lt * 1.2) % 2:
                d.ellipse([110, 70, 130, 82], fill=(255, 255, 255)); d.ellipse([124, 84, 128, 88], fill=(255, 255, 255))
                d.ellipse([112, 72, 126, 78], fill=(255, 240, 160)) if False else None
            sparkles(d, 100, 100, t, 6, 18)
        elif st == "cows":
            grad(d, 0, HZ, (140, 200, 240), (220, 236, 246)); hills(d, 150, (150, 196, 140), 12, 1, t, 2); ground(d, (110, 166, 80))
            d.rectangle([0, 150, PW, 156], fill=(60, 130, 190))
            for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 44 + i * 14, 1.0)
            for i in range(4):
                x = 22 + i * 18
                im = actor(base, "sheep", x, 172, t * 0.2, 0.62, walk=0.0)
            for i in range(4):
                x = 110 + i * 16
                d.ellipse([x - 5, 156, x + 5, 164], fill=(150, 130, 100)); d.line([(x - 4, 164), (x - 4, 170)], fill=(120, 100, 76)); d.line([(x + 4, 164), (x + 4, 170)], fill=(120, 100, 76)); d.ellipse([x + 4, 154, x + 9, 159], fill=(130, 110, 84))
            for i in range(7):
                x = 16 + i * 22; ph = (lt * 0.5 + i * 0.1) % 1
                d.rectangle([x, 120 - int(4 * math.sin(t * 2 + i)), x + 2, 128], fill=(230, 190, 60)); d.rectangle([x - 1, 114 - int(4 * math.sin(t * 2 + i)), x + 3, 120], fill=(250, 220, 90)) if False else None
            person(base, "David", 150, 168, t, 0.55, flip=True)
