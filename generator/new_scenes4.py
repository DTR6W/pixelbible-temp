NEWK4 = {"bush", "tomb", "wisdom"}

def baby(d, x, y):
    d.ellipse([x - 5, y - 7, x + 5, y + 1], fill=(240, 230, 210)); d.ellipse([x - 3, y - 12, x + 3, y - 6], fill=(235, 190, 150))

def throne(d, x, y):
    d.rectangle([x - 14, y - 34, x + 14, y], fill=(150, 100, 40)); d.rectangle([x - 10, y - 30, x + 10, y - 10], fill=(150, 30, 40))
    d.rectangle([x - 16, y - 12, x + 16, y - 8], fill=(200, 150, 50)); d.rectangle([x - 18, y - 36, x + 18, y - 33], fill=(220, 170, 60))

def draw_new4(d, base, kind, o, t, lt):
    st = o.get("stage", "")
    if kind == "bush":
        if st == "go":
            grad(d, 0, HZ, (250, 170, 100), (255, 226, 170)); hills(d, 150, (190, 130, 90), 12, 1, t, 2); ground(d, (206, 170, 110), (190, 150, 96))
            for x in (120, 150): d.polygon([(x - 18, 168), (x, 136), (x + 18, 168)], fill=(224, 190, 120)); d.polygon([(x, 136), (x + 18, 168), (x + 5, 168)], fill=(190, 156, 96))
            person(base, "Moses", 40 + int(40 * ease(lt / 5.0)), 170, t, 0.55)
            for i in range(3): actor(base, "sheep", 22 + i * 20, 172 + (i % 2) * 3, t * 0.3, 0.4, walk=0.3)
        else:
            desert(d, t, (90, 150, 215), (250, 220, 170))
            mountain(d, 150, 60, 160, 50, (130, 100, 90))
            near = st in ("voice", "send")
            bx = 118 if near else 112; by = 170
            r = 1.6 if near else 1.0
            glow(d, bx, by - int(26 * r), int(34 * r), (255, 200, 90), (230, 196, 140), 6)
            d.ellipse([bx - 22 * r, by - 30 * r, bx + 22 * r, by + 2], fill=(60, 120, 60))
            for i in range(7): flame(d, bx - 16 * r + i * 5.5 * r, by - 8 - (i % 3) * 6 * r, t + i * 0.3, 0.9 * r)
            if st == "bush":
                person(base, "Moses", 40 + int(14 * ease(lt / 4.0)), 170, t, 0.5)
                for i in range(3): actor(base, "sheep", 12 + i * 12, 175 + (i % 2) * 3, t * 0.3, 0.35, walk=0.2)
            else:
                person(base, "Moses", 50, 172, t, 0.62)
                sparkles(d, bx, by - 30, t, 10, 40)
    elif kind == "tomb":
        if st == "cross":
            grad(d, 0, HZ, (50, 30, 50), (190, 100, 80)); hills(d, 150, (50, 34, 40), 12, 1, t, 3); ground(d, (60, 46, 44))
            for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 30 + i * 12, 1.6, (90, 56, 70))
            for x, h in ((50, 70), (90, 84), (130, 70)):
                d.rectangle([x - 2, 168 - h, x + 2, 168], fill=(60, 36, 26)); d.rectangle([x - 14, 168 - h + 16, x + 14, 168 - h + 20], fill=(60, 36, 26))
        else:
            if st == "sealed":
                grad(d, 0, HZ, (6, 8, 30), (50, 44, 90)); stars(d, t, 60, 110, 5)
            elif st == "open":
                grad(d, 0, HZ, (250, 170, 120), (255, 232, 180))
            else:
                grad(d, 0, HZ, (255, 196, 120), (255, 244, 210))
            hills(d, 150, (110, 120, 90) if st != "sealed" else (24, 30, 60), 12, 1, t, 4); ground(d, (120, 150, 90) if st != "sealed" else (30, 44, 50))
            d.polygon([(70, 168), (76, 100), (140, 100), (150, 168)], fill=(150, 140, 130))
            d.polygon([(76, 100), (140, 100), (130, 90), (88, 90)], fill=(176, 166, 156))
            d.ellipse([88, 126, 126, 172], fill=(20, 16, 20))
            if st == "sealed":
                d.ellipse([84, 122, 130, 172], fill=(120, 112, 106)); d.arc([84, 122, 130, 172], 200, 330, fill=(160, 152, 146))
            else:
                d.ellipse([128, 138, 160, 172], fill=(120, 112, 106)); d.arc([128, 138, 160, 172], 200, 330, fill=(160, 152, 146))
            if st == "open":
                person(base, "Mary", 30 + int(30 * ease(lt / 4.0)), 172, t, 0.55)
                glow(d, 107, 150, 20, (255, 250, 200), (20, 16, 20), 5)
            if st == "alive":
                glow(d, 107, 148, 36, (255, 250, 210), (255, 232, 180), 6)
                person(base, "Jesus", 107, 172, t, 0.62)
                person(base, "Mary", 40, 172, t, 0.55)
                sparkles(d, 107, 140, t, 10, 36)
    elif kind == "wisdom":
        grad(d, 0, HZ, (70, 34, 52), (140, 84, 76)); d.rectangle([0, HZ - 6, PW, PH], fill=(150, 110, 80))
        for x in (14, 166): d.rectangle([x - 6, 40, x + 6, 168], fill=(220, 206, 180)); d.rectangle([x - 8, 36, x + 8, 42], fill=(240, 226, 196))
        d.rectangle([60, 168, 120, 172], fill=(150, 30, 40))
        throne(d, 90, 168)
        if st == "throne":
            person(base, "Solomon", 90, 170, t, 0.55)
        elif st == "two":
            person(base, "Solomon", 90, 150, t, 0.4)
            person(base, "Mary", 40, 176, t, 0.5); person(base, "Mary", 140, 176, t, 0.5, flip=True)
            baby(d, 90, 182)
        elif st == "sword":
            person(base, "Solomon", 90, 150, t, 0.4)
            person(base, "Mary", 40, 176, t, 0.5); person(base, "Mary", 140, 176, t, 0.5, flip=True)
            baby(d, 90, 182)
            sx = 90; d.line([(sx, 196), (sx, 170)], fill=(220, 224, 235), width=2); d.rectangle([sx - 3, 196, sx + 3, 198], fill=(150, 100, 40))
            if int(t * 3) % 2: d.point((sx, 168), fill=(255, 255, 255))
        else:
            person(base, "Solomon", 90, 150, t, 0.4)
            person(base, "Mary", 70, 178, t, 0.55)
            baby(d, 82, 176)
            sparkles(d, 90, 120, t, 10, 40)
