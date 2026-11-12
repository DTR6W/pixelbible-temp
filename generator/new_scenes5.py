NEWK5 = {"gen", "lesson"}
_SETS = {
 "day": ((130, 200, 245), (220, 238, 246), (150, 196, 140), (100, 160, 76), (84, 140, 62)),
 "dawn": ((250, 170, 120), (255, 232, 180), (190, 140, 100), (130, 150, 90), (110, 130, 76)),
 "dusk": ((60, 34, 64), (200, 110, 80), (60, 40, 50), (70, 56, 54), (56, 44, 44)),
 "night": ((6, 8, 30), (50, 44, 90), (24, 30, 60), (36, 54, 56), (30, 44, 46)),
 "storm": ((40, 50, 80), (96, 106, 136), (50, 60, 84), (50, 66, 70), (40, 54, 58)),
 "fire": ((70, 20, 20), (210, 100, 40), (80, 30, 24), (90, 56, 40), (70, 44, 32)),
 "dark": ((20, 16, 28), (50, 40, 60), (30, 24, 36), (40, 34, 40), (30, 26, 32)),
}

def draw_new5(d, base, kind, o, t, lt):
    if kind == "lesson":
        grad(d, 0, HZ, (30, 20, 70), (210, 150, 100)); hills(d, 150, (60, 44, 90), 12, 1, t, 6); ground(d, (60, 50, 90), (50, 42, 80))
        glow(d, 90, 96, 44, (255, 238, 180), (60, 40, 90), 7); star8(d, 90, 96, 10 + int(2 * math.sin(t * 3)))
        motes(d, t, 24, (255, 230, 150)); return
    st = o.get("set", "day"); cast = o.get("cast", []); props = o.get("props", [])
    if st == "desert":
        desert(d, t)
    elif st == "palace":
        grad(d, 0, HZ, (70, 34, 52), (140, 84, 76)); d.rectangle([0, HZ - 6, PW, PH], fill=(150, 110, 80))
        for x in (14, 166): d.rectangle([x - 6, 40, x + 6, 168], fill=(220, 206, 180)); d.rectangle([x - 8, 36, x + 8, 42], fill=(240, 226, 196))
        d.rectangle([60, 168, 120, 172], fill=(150, 30, 40))
    elif st == "sea":
        daysky(d, t); d.rectangle([0, 120, PW, PH], fill=(50, 120, 190))
        for k in range(4): waves(d, 120 + k * 9, 140 + k * 9, (130, 190, 240), t + k)
    elif st == "river":
        daysky(d, t); hills(d, 130, (150, 196, 140), 10, 1, t, 2); d.rectangle([0, 140, PW, PH], fill=(60, 130, 190))
        for k in range(4): waves(d, 142 + k * 8, 160 + k * 8, (140, 196, 240), t + k)
        d.rectangle([0, 130, PW, 142], fill=(110, 160, 80))
    else:
        c = _SETS.get(st, _SETS["day"])
        grad(d, 0, HZ, c[0], c[1]); hills(d, 150, c[2], 12, 1, t, 3); ground(d, c[3], c[4])
        if st in ("night",): stars(d, t, 60, 110, 5)
        if st in ("day", "dawn"):
            for i in range(3): cloud(d, ((t * 5 + i * 80) % 240) - 35, 40 + i * 14, 1.0)
        if st in ("storm", "dusk", "dark", "fire"):
            for i in range(4): cloud(d, ((t * 8 + i * 70) % 250) - 40, 28 + i * 12, 1.7, tuple(max(0, v - 10) for v in c[2]))
    if st == "storm": rain(d, t, 80, (170, 190, 230), 0, PH)
    for p in props:
        k = p[0]
        if k == "tree": tree(d, p[1], 166, p[2], (50, 130, 60), sway=1.0, t=t)
        elif k == "house": house(d, p[1], 168, p[2], p[3])
        elif k == "altar": altar_stones(d, p[1], 168)
        elif k == "flame": flame(d, p[1], p[2], t, p[3])
        elif k == "boat": boat(d, p[1], p[2], t, math.sin(t * 2) * (2 if st == "storm" else 0.5))
        elif k == "sheep": actor(base, "sheep", p[1], p[2], t * 0.3, 0.4, walk=0.2)
        elif k == "lion": actor(base, "lion", p[1], p[2], t * 0.3, 0.45, walk=0.0)
        elif k == "baby": baby(d, p[1], p[2])
        elif k == "throne": throne(d, p[1], 168)
        elif k == "star": star8(d, p[1], p[2], 6 + int(1.5 * math.sin(t * 3)))
        elif k == "cross":
            d.rectangle([p[1] - 2, 168 - p[2], p[1] + 2, 168], fill=(70, 44, 30)); d.rectangle([p[1] - 12, 168 - p[2] + 14, p[1] + 12, 168 - p[2] + 18], fill=(70, 44, 30))
        elif k == "crowd":
            for i in range(p[3]): mini(d, p[1] + i * (p[2] - p[1]) // max(1, p[3] - 1) + int(2 * math.sin(t + i)), p[4] + (i % 2) * 3, CROWDC[i % 5], t, i)
        elif k == "pyramid":
            d.polygon([(p[1] - 22, 168), (p[1], 130), (p[1] + 22, 168)], fill=(224, 190, 120)); d.polygon([(p[1], 130), (p[1] + 22, 168), (p[1] + 6, 168)], fill=(190, 156, 96))
        elif k == "well":
            d.rectangle([p[1] - 12, 154, p[1] + 12, 168], fill=(130, 124, 118)); d.rectangle([p[1] - 12, 154, p[1] + 12, 157], fill=(170, 164, 156))
            d.line([(p[1] - 10, 140), (p[1] - 10, 154)], fill=(90, 60, 36)); d.line([(p[1] + 10, 140), (p[1] + 10, 154)], fill=(90, 60, 36)); d.rectangle([p[1] - 12, 138, p[1] + 12, 141], fill=(110, 76, 44))
        elif k == "basket":
            by = p[2] + 1.5 * math.sin(t * 2); d.ellipse([p[1] - 9, by - 5, p[1] + 9, by + 3], fill=(190, 150, 80)); d.arc([p[1] - 9, by - 5, p[1] + 9, by + 3], 0, 180, fill=(140, 100, 50)); baby(d, p[1], by - 3)
        elif k == "ladder":
            glow(d, p[1], 70, 40, (255, 250, 210), (6, 8, 30), 6)
            for i in range(10): d.line([(p[1] - 6 + i * 3 // 2, 168 - i * 11), (p[1] + 6 + i * 3 // 2, 168 - i * 11)], fill=(255, 240, 180))
            d.line([(p[1] - 6, 168), (p[1] + 8, 58)], fill=(255, 240, 180)); d.line([(p[1] + 6, 168), (p[1] + 20, 58)], fill=(255, 240, 180))
            sparkles(d, p[1] + 10, 120, t, 12, 50)
        elif k == "furnace":
            d.rectangle([p[1] - 24, 120, p[1] + 24, 168], fill=(70, 50, 44)); d.rectangle([p[1] - 16, 132, p[1] + 16, 168], fill=(255, 150, 40))
            for i in range(6): flame(d, p[1] - 14 + i * 5.5, 166, t + i * 0.2, 1.1)
        elif k == "statue":
            d.rectangle([p[1] - 8, 70, p[1] + 8, 150], fill=(230, 190, 60)); d.ellipse([p[1] - 8, 56, p[1] + 8, 74], fill=(240, 200, 70)); d.rectangle([p[1] - 14, 150, p[1] + 14, 168], fill=(200, 160, 50))
        elif k == "script":
            glow(d, p[1], p[2], 28, (255, 240, 200), (140, 84, 76), 5)
            for i, w in enumerate(("MENE", "TEKEL", "PARSIN")): d.text((p[1] - 13, p[2] - 14 + i * 10), w, fill=(120, 20, 20), font=ImageFont.load_default())
        elif k == "bread":
            for i in range(14): d.ellipse([(i * 37 + int(t * 20)) % PW, (i * 23 + int(t * 30)) % 150 + 10, (i * 37 + int(t * 20)) % PW + 3, (i * 23 + int(t * 30)) % 150 + 13], fill=(250, 244, 220))
        elif k == "table":
            d.rectangle([p[1] - 36, 164, p[1] + 36, 168], fill=(130, 86, 50)); d.rectangle([p[1] - 36, 168, p[1] + 36, 172], fill=(96, 62, 38))
            d.ellipse([p[1] - 4, 160, p[1] + 4, 164], fill=(240, 220, 170)); d.rectangle([p[1] + 10, 158, p[1] + 14, 164], fill=(210, 190, 90))
        elif k == "dove":
            x = p[1]; y = p[2] + 3 * math.sin(t * 4); d.ellipse([x - 4, y - 2, x + 4, y + 2], fill=(250, 250, 255)); d.polygon([(x - 2, y), (x - 8, y - 5 - int(2 * math.sin(t * 8))), (x + 1, y - 1)], fill=(235, 235, 245))
        elif k == "glow": glow(d, p[1], p[2], p[3], (255, 250, 215), (255, 230, 170) if st in ("day", "dawn") else (60, 50, 80), 6)
        elif k == "sparks": sparkles(d, p[1], p[2], t, 10, p[3])
        elif k == "light":
            glow(d, p[1], 40, 50, (255, 255, 245), (200, 230, 255) if st == "day" else (60, 60, 100), 6)
        elif k == "mount": mountain(d, p[1], p[2], 168, p[3], (130, 110, 100))
        elif k == "sun": d.ellipse([p[1] - 9, p[2] - 9, p[1] + 9, p[2] + 9], fill=(255, 220, 90))
        elif k == "moon": d.ellipse([p[1] - 7, p[2] - 7, p[1] + 7, p[2] + 7], fill=(235, 235, 220))
        elif k == "wall": d.rectangle([p[1], 110, p[2], 168], fill=(190, 160, 120)); [d.line([(p[1], y), (p[2], y)], fill=(150, 124, 92)) for y in range(116, 168, 8)]
        elif k == "lightning": lightning(base, t, lt)
    for c in cast:
        name, x, y, s, fl = c[0], c[1], c[2], c[3], c[4]
        dx = c[5] if len(c) > 5 else 0
        person(base, name, x + int(dx * ease(lt / 4.0)), y, t, s, flip=bool(fl))
