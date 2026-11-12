import re as _re
_YD = {"palace": 176, "palace_dusk": 176, "ship": 185, "ship_storm": 185, "ship_night": 185, "house": 170, "den": 168}
def _cast(env, specs):
    out = []
    for sp in specs:
        tk = sp.split(); d = dict(n=tk[0], x=int(tk[1]), y=_YD.get(env, 172), s=.55, acts=[(0, "idle")], bubbles=[])
        if d["n"] in ("sheep", "lion", "deer"): d["s"] = .42
        for t in tk[2:]:
            if t == "f": d["flip"] = 1
            elif t == "v": d["speaks"] = True
            elif t[0] == "s" and t[1:].isdigit(): d["s"] = int(t[1:]) / 100.0
            elif t[0] == "y" and t[1:].isdigit(): d["y"] = int(t[1:])
            elif t[0] == "t": a, b = t[1:].split(":"); d["acts"].append((float(a), b))
            elif t[0] == "w": b, c = t[1:].split("@"); a1, a2 = c.split("-"); d["walk"] = (float(a1), float(a2), int(b))
            elif t[0] == "b": b, c = t[1:].split("@"); a1, a2 = c.split("-"); d["bubbles"].append((float(a1), float(a2), b.replace("_", " ")))
            elif t[0] == "g": b, c = t[1:].split("@"); a1, a2 = c.split("-"); d["glide"] = (float(a1), float(a2), int(b.split(",")[0]), int(b.split(",")[1]))
            elif t[0] == "z": d["salt"] = float(t[1:])
        d["acts"].sort(key=lambda a: a[0])
        out.append(d)
    return out
def N(old, idx, env, specs, props=(), **kw):
    s = STORIES[old][idx]
    return sc(s["t"], "g6", s["text"], env=env, cast=_cast(env, specs), props=list(props), voice=kw.get("voice"), echo=kw.get("echo"), sfx=kw.get("sfx", []), sfx_echo=kw.get("sfx_echo"), quake=kw.get("quake"))
def NE(old): return STORIES[old][-1]
def reg(old, scenes): STORIES["n_" + old] = scenes + [NE(old)]
HL = ["throne"]; TW2 = [("town", 0, 180, 152, (196, 150, 110))]; TR = [("tree", 28, 150, 32)]; TR2 = [("tree", 28, 150, 32), ("tree", 154, 150, 28)]

reg("waterwalk23", [
 N("waterwalk23", 0, "sea_night", ["Jesus 90 y160 s45 w120@0.5-5"]),
 N("waterwalk23", 1, "ship_storm", ["Peter 60 t2:cower", "Fisherman 110 f t2:cower", "Boy 150 f t2:cower"], quake=(0, 6)),
 N("waterwalk23", 2, "ship_storm", ["Peter 60 t0:cower bAAAH!@3-5", "Fisherman 110 f t0:cower", "Boy 150 f t0:cower"], quake=(0, 6), sfx=[(3.0, "Peter", "A ghost! It's a ghost!", 1.15)]),
 N("waterwalk23", 3, "sea_night", ["Jesus 90 y160 s45 t0:welcome"]),
 N("waterwalk23", 4, "sea_night", ["Peter 60 y160 s45 t3:cower bHELP!@4-6", "Jesus 120 y160 s45 f t0:welcome"], sfx=[(4.2, "Peter", "Lord, save me!", 1.1)]),
 N("waterwalk23", 5, "ship", ["Peter 60 t0:cheer", "Jesus 100 f t0:welcome", "Fisherman 144 f t0:cheer"])])
reg("loaves23", [
 N("loaves23", 0, "day", ["Jesus 90 t2:welcome", "Boy 50 t3:cheer", "Woman 140 f t3:cheer"], TR),
 N("loaves23", 1, "day", ["Jesus 120 f t2:hands", "Fisherman 30 t0:hands", "Woman 60 t0:hands", "Boy 160 f t1:hands"], TR),
 N("loaves23", 2, "day", ["Boy 60 t1:welcome", "Jesus 110 f t3:raise", "Peter 150 f t0:hands"], TR),
 N("loaves23", 3, "day", ["Jesus 90 t1:welcome", "Woman 40 t2:cheer", "Fisherman 140 f t2:cheer", "Boy 160 f t2:cheer"], TR),
 N("loaves23", 4, "day", ["Peter 60 t1:cheer", "Fisherman 110 f t1:cheer", "Jesus 150 f t0:welcome"], TR)])
reg("abraham23", [
 N("abraham23", 0, "dawn", ["Elder 90 t2:hands"], [("tree", 28, 150, 30)]),
 N("abraham23", 1, "dawn", ["Elder 70 t0:talk", "Boy 112 f", "Angel 150 y60 g150,60@0-0.1"] if False else ["Elder 70 t3:point", "Boy 112 f"], [("tree", 154, 150, 30)]),
 N("abraham23", 2, "golden", ["Boy 50 w100@0-4 t4:talk", "Elder 20 w70@0-4"], [("tree", 154, 150, 30)]),
 N("abraham23", 3, "golden", ["Elder 70 t0:raise", "Boy 110 f t2:kneel", "Angel 150 f y40 g150,160@0.5-2.5 t0:raise"], [("altar", 90, 168)], sfx=[(2.6, "Angel", "Abraham! Stop! Do not harm the boy!", 1.0)]),
 N("abraham23", 4, "golden", ["Elder 60 t1:cheer", "Boy 100 t1:cheer", "sheep 144 f"], [("altar", 20, 168), ("tree", 154, 150, 30)])])
reg("basket3", [
 N("basket3", 0, "shore", ["Woman 140 f t2:hands"], []),
 N("basket3", 1, "palace_dusk", ["King 90 y150 s50 t3:point", "Soldier 140 f", "Woman 40 t3:cower"], HL),
 N("basket3", 2, "dawn", ["Woman 70 t2:hands", "Woman 120 f t0:hands"], [("tree", 28, 150, 30)]),
 N("basket3", 3, "shore", ["Queen 80 t1:welcome", "Woman 130 f t3:cheer"]),
 N("basket3", 4, "palace_dusk", ["Moses 70 t2:cheer", "King 100 y150 s50 f", "Queen 140 f t3:welcome"], HL)])
reg("zacchaeus3", [
 N("zacchaeus3", 0, "day", ["Boy 60 t2:cheer", "Fisherman 120 f t1:talk"], TW2),
 N("zacchaeus3", 1, "day", ["Fisherman 40 t0:raise", "Woman 100 t0:hands", "Boy 150 f w100@0-3 t3:cheer"], [("tree", 20, 152, 38), ("tree", 160, 152, 34)]),
 N("zacchaeus3", 2, "day", ["Jesus 70 t1:point", "Boy 130 f y150 s45 t3:cheer"], [("tree", 132, 152, 40)]),
 N("zacchaeus3", 3, "house", ["Boy 70 t2:cheer", "Jesus 130 f t1:welcome", "Woman 160 f t3:cheer"], ["table"])])
reg("ruth3", [
 N("ruth3", 0, "golden", ["Woman 70 w110@0-4", "Mary 40 w80@0-4"]),
 N("ruth3", 1, "dusk", ["Mary 70 t1:hands", "Woman 120 f t3:hands"], TR),
 N("ruth3", 2, "golden", ["Woman 70 t2:welcome", "Mary 120 f t3:hands"], TR2),
 N("ruth3", 3, "golden", ["Woman 60 t1:talk", "Shepherd 120 f t3:welcome"], [("tree", 154, 150, 30)]),
 N("ruth3", 4, "golden", ["Woman 60 t2:cheer", "Shepherd 100 f t2:cheer", "Mary 140 f t3:cheer"], [("tree", 28, 150, 30)])])
reg("gideon3", [
 N("gideon3", 0, "dawn", ["Soldier 90 t2:raise"], [("tree", 28, 150, 30)]),
 N("gideon3", 1, "day", ["Soldier 50 t0:cower", "Angel 120 f t1:welcome"], [("altar", 154, 168)]),
 N("gideon3", 2, "day", ["Soldier 80 t0:raise", "Fisherman 120 f w170@3-6", "Samson 150 f w170@3-6", "Boy 30 w-20@3-6"], TR),
 N("gideon3", 3, "night", ["Soldier 60 t2:raise", "Fisherman 100 t2:raise", "Boy 140 f t2:raise"], [("town", 100, 180, 152, (110, 90, 80))]),
 N("gideon3", 4, "night", ["Soldier 60 t0:raise bCHARGE!@1-3", "Fisherman 100 t0:raise", "Samson 150 f t1:cower w190@2-5 bRUN!@2.5-4.5"], [("town", 100, 180, 152, (110, 90, 80))], sfx=[(1.2, "Soldier", "For the Lord and for Gideon!", 1.1)])])
reg("esther3", [
 N("esther3", 0, "palace_dusk", ["Queen 90 y150 s50 t2:hands"], HL),
 N("esther3", 1, "palace_dusk", ["Queen 60 t1:welcome", "King 120 y150 s50 f"], HL),
 N("esther3", 2, "palace_dusk", ["Pharisee 60 t1:talk", "King 130 y150 s50 f t3:raise bSIGN_IT!@1-3", "Queen 164 f"], HL),
 N("esther3", 3, "palace_dusk", ["Queen 40 w84@0-4 t4:welcome", "King 120 y150 s50 f"], HL),
 N("esther3", 4, "palace_dusk", ["King 100 y150 s50 t0:welcome", "Queen 60 t2:cheer", "Pharisee 150 f t0:cower"], HL)])
reg("lastsupper3", [
 N("lastsupper3", 0, "house", ["Jesus 90 y165 t2:welcome", "Peter 40 y168", "Fisherman 140 y168 f"], ["table"]),
 N("lastsupper3", 1, "house", ["Jesus 90 y165 t1:raise", "Peter 40 y168 t3:hands", "Fisherman 140 y168 f t3:hands"], ["table"]),
 N("lastsupper3", 2, "house", ["Jesus 90 y165 t0:hands", "Peter 40 y168 t2:cower bME?@2.5-4.5", "Fisherman 140 y168 f t2:cower"], ["table"]),
 N("lastsupper3", 3, "house", ["Jesus 90 y170 t1:kneel", "Peter 50 y170 t3:hands", "Fisherman 140 y170 f t3:hands"], [])])
reg("job3", [
 N("job3", 0, "dusk", ["Elder 90 t2:cower"], [("ruin", 100, 152, 60, (110, 96, 88))]),
 N("job3", 1, "golden", ["Elder 80 t2:cheer", "sheep 30 f", "sheep 150", "Woman 120 f t2:welcome"], TR2),
 N("job3", 2, "burn", ["Elder 90 t2:cower bNO!@3-5"], [("ruin", 100, 152, 60, (80, 60, 56))], sfx=[(3.0, "Elder", "No! No! Not my children!", 1.1)]),
 N("job3", 3, "dusk", ["Elder 60 t3:hands", "Pharisee 130 f t1:point", "Priest 160 f t2:point"], []),
 N("job3", 4, "golden", ["Elder 80 t1:cheer", "Woman 120 f t2:cheer", "Boy 150 f t2:cheer", "sheep 30 f"], TR2)])
reg("jacobladder3", [
 N("jacobladder3", 0, "night", ["Fisherman 90 t3:kneel"], [("olive", 28, 152, 30)]),
 N("jacobladder3", 1, "dusk", ["Fisherman 60 w120@0-4", "Boy 30 w100@0-4"][:1], TR),
 N("jacobladder3", 2, "night", ["Fisherman 90 t2:kneel"], [("olive", 154, 150, 34)]),
 N("jacobladder3", 3, "night", ["Fisherman 90 t0:kneel", "Angel 60 y60 s50 g60,100@0-4", "Angel 130 y110 s50 g130,60@0-4"], []),
 N("jacobladder3", 4, "dawn", ["Fisherman 90 t0:raise", "Angel 140 y60 s50 t0:raise"], TR, voice=None)])
reg("storm3", [
 N("storm3", 0, "ship_storm", ["Jesus 90 t0:bow", "Peter 40 t1:cower", "Fisherman 144 f t1:cower"], quake=(0, 6)),
 N("storm3", 1, "ship_storm", ["Peter 50 t0:cower", "Fisherman 100 f t0:cower", "Boy 150 f t0:cower bAAAH!@3-5", "Jesus 90 y185 s30 t0:bow"][:3], quake=(0, 7), sfx=[(3.0, "Boy", "We're going to sink!", 1.2)]),
 N("storm3", 2, "ship_storm", ["Peter 50 t0:raise bWAKE_UP!@1-3", "Jesus 100 f t0:bow", "Fisherman 150 f t0:raise"], quake=(0, 6), sfx=[(1.0, "Peter", "Teacher, don't you care that we are about to die?", 1.05)]),
 N("storm3", 3, "ship_storm", ["Jesus 90 t0:raise", "Peter 40 t1:cower", "Fisherman 144 f t1:cower"], quake=(0, 2.5)),
 N("storm3", 4, "ship", ["Jesus 90 t0:welcome", "Peter 50 t2:cheer", "Fisherman 144 f t2:cheer"])])
reg("lazarus3", [
 N("lazarus3", 0, "dawn", ["Jesus 70 t2:point", "Elder 130 f t4:raise"], [("ruin", 120, 152, 48, (150, 136, 120))]),
 N("lazarus3", 1, "dusk", ["Woman 60 t1:hands", "Mary 110 f t1:hands", "Elder 150 f s30 y160 t0:cower"][:2], [("ruin", 120, 152, 40, (130, 118, 108))]),
 N("lazarus3", 2, "dusk", ["Jesus 60 t2:hands", "Woman 110 f t0:hands", "Mary 150 f t0:hands"], []),
 N("lazarus3", 3, "dawn", ["Jesus 70 t1:point", "Peter 120 f t2:hands", "Woman 150 f t0:hands"], [("ruin", 150, 152, 40, (150, 136, 120))]),
 N("lazarus3", 4, "dawn", ["Jesus 60 t0:raise bCOME_OUT!@0.5-3", "Elder 130 f t4:cheer", "Woman 160 f t4:cheer", "Mary 20 t4:cheer"], [("ruin", 150, 152, 40, (150, 136, 120))], sfx=[(0.5, "Jesus", "Lazarus, come out!", 1.0)])])
reg("naaman3", [
 N("naaman3", 0, "palace_dusk", ["Soldier 90 y150 s50 t2:hands", "Woman 140 f t3:hands"], HL),
 N("naaman3", 1, "palace_dusk", ["Woman 60 t1:point", "Soldier 120 f t3:hands"], HL),
 N("naaman3", 2, "day", ["Elder 130 f t0:point", "Soldier 60 t3:cower bWHAT?!@4-6"], TR),
 N("naaman3", 3, "day", ["Soldier 60 t0:raise bNO!@0.5-3", "Fisherman 120 f t3:talk", "Woman 160 f t3:point"], TR),
 N("naaman3", 4, "river" if False else "sea", ["Soldier 90 y160 s45 t3:cheer"], [])])
reg("hannah3", [
 N("hannah3", 0, "dawn", ["Woman 90 t1:kneel"], [("altar", 130, 168)]),
 N("hannah3", 1, "golden", ["Woman 70 t0:kneel", "Priest 130 f t3:welcome"], [("altar", 154, 168), ("tree", 20, 150, 28)]),
 N("hannah3", 2, "golden", ["Woman 70 t2:cheer", "Boy 110 f t2:cheer"], TR2),
 N("hannah3", 3, "palace_dusk", ["Woman 50 t1:welcome", "Boy 80 s40 t1:bow", "Priest 130 y150 s50 f t2:welcome"], []),
 N("hannah3", 4, "night", ["Boy 70 t0:kneel bSPEAK_LORD@4-6", "Angel 130 y60 s50 g130,130@0-1 t3:raise"], [], sfx=[(4.3, "Boy", "Speak, Lord, your servant is listening!", 1.1)])])
reg("jacobesau3", [
 N("jacobesau3", 0, "dusk", ["Fisherman 60 t2:talk", "Samson 120 f t3:hands"], TR),
 N("jacobesau3", 1, "dusk", ["Samson 60 t0:cower bSO_HUNGRY!@0.5-2.5", "Fisherman 120 f t2:welcome"], [("hut", 150, 152, 34, 24, (200, 170, 120), (120, 70, 50))], sfx=[(0.8, "Samson", "I am starving! Give me some stew!", 1.0)]),
 N("jacobesau3", 2, "house", ["Elder 60 t2:welcome", "Fisherman 120 f t3:hands"], []),
 N("jacobesau3", 3, "dusk", ["Samson 60 t0:raise bFURIOUS!@1-3", "Fisherman 130 f w180@3-6"], TR),
 N("jacobesau3", 4, "golden", ["Samson 20 w80@0-3 t3:welcome", "Fisherman 130 f t3:cheer"], TR2)])
reg("furnace3", [
 N("furnace3", 0, "burn", ["Fisherman 50 t2:raise", "Boy 90 t2:raise", "Peter 130 f t2:raise", "King 160 f t3:point"], [("furnace", 120, 152)]),
 N("furnace3", 1, "palace_dusk", ["King 70 t1:raise", "Pharisee 140 f t3:hands"], [("throne",), ("statue", 130, 152)] if False else [("statue", 130, 152)]),
 N("furnace3", 2, "palace_dusk", ["Fisherman 40 t2:welcome", "Boy 76 t2:welcome", "Peter 110 t2:welcome", "King 150 f t0:point bBOW_DOWN!@0.5-2.5"], [("statue", 130, 152)]),
 N("furnace3", 3, "burn", ["King 40 t0:point", "Soldier 100 f t2:raise", "Fisherman 150 f t3:cower bAAAH!@4-6"], [("furnace", 110, 152)], sfx=[(4.2, "Fisherman", "Aaaah!", 1.2)]),
 N("furnace3", 4, "burn", ["King 40 t0:hands", "Angel 118 y160 s48 t0:raise"], [("furnace", 120, 152)]),
 N("furnace3", 5, "day", ["Fisherman 50 t1:cheer", "Boy 90 t1:cheer", "Peter 130 f t1:cheer", "King 160 f t0:raise"], TR)])
reg("handwriting3", [
 N("handwriting3", 0, "palace_dusk", ["King 90 y150 s50 t2:raise", "Queen 40 t2:cheer", "Pharisee 150 f t2:cheer"], HL),
 N("handwriting3", 1, "palace_dusk", ["King 90 y150 s50 t0:raise", "Queen 40 t0:cheer", "Pharisee 150 f t0:cheer"], HL),
 N("handwriting3", 2, "palace_dusk", ["King 90 y150 s50 t2:cower bWHAT_IS_THAT?@3-5", "Queen 40 t2:cower", "Pharisee 150 f t2:cower"], HL, sfx=[(3.0, "King", "What does that mean?!", 1.1)]),
 N("handwriting3", 3, "palace_dusk", ["Paul 50 t1:point", "King 110 y150 s50 f t0:cower"], HL),
 N("handwriting3", 4, "night", ["Soldier 40 w150@0-4", "Soldier 10 w120@0-4", "King 130 f t0:cower"], [("town", 0, 180, 152, (110, 90, 80))])])
reg("bartimaeus3", [
 N("bartimaeus3", 0, "day", ["Elder 70 t0:raise bJESUS!@0.5-3", "Fisherman 130 f t1:point"], TW2, sfx=[(0.5, "Elder", "Jesus! Have mercy on me!", 1.2)]),
 N("bartimaeus3", 1, "day", ["Elder 60 t1:raise", "Fisherman 120 f t2:point", "Woman 160 f t2:point"], TW2),
 N("bartimaeus3", 2, "day", ["Jesus 120 f t0:welcome", "Elder 60 t1:hands"], TR),
 N("bartimaeus3", 3, "day", ["Jesus 120 f t0:welcome", "Elder 60 t3:cheer bI_CAN_SEE!@3.5-6", "Fisherman 160 f t4:cheer"], TR, sfx=[(3.5, "Elder", "I can see! I can see!", 1.15)])])
reg("damascus3", [
 N("damascus3", 0, "desert", ["Paul 70 t1:point", "Soldier 120 f t1:point"]),
 N("damascus3", 1, "desert", ["Paul 40 w110@0-5", "Soldier 10 w80@0-5"]),
 N("damascus3", 2, "desert", ["Paul 80 t1:cower bAAAH!@1-3", "Jesus 140 f y90 s45 t0:raise"][:1], [], sfx=[(1.0, "Paul", "Aaaah! Who are you, Lord?", 1.1)], quake=(0.5, 3)),
 N("damascus3", 3, "house", ["Paul 80 t0:hands", "Soldier 140 f"], []),
 N("damascus3", 4, "house", ["Paul 70 t2:cheer", "Elder 120 f t0:welcome"], [])])
reg("denial3", [
 N("denial3", 0, "night", ["Peter 90 t2:cower"], TR),
 N("denial3", 1, "night", ["Peter 60 t1:raise", "Jesus 120 f t2:hands"], OLV),
 N("denial3", 2, "night", ["Peter 70 t1:hands", "Woman 120 f t3:point", "Soldier 160 f t3:point"], [("town", 0, 180, 152, (110, 90, 80))]),
 N("denial3", 3, "night", ["Peter 60 t0:cower bI_DON'T_KNOW_HIM!@1-3", "Woman 120 f t1:point", "Soldier 160 f t1:point"], [("town", 0, 180, 152, (110, 90, 80))], sfx=[(1.0, "Peter", "I do not know him!", 1.15)]),
 N("denial3", 4, "dawn", ["Peter 80 t0:kneel", "Jesus 130 f t3:welcome"], TR)])
reg("baptism3", [
 N("baptism3", 0, "sea", ["Jesus 90 y160 s45 t2:welcome"]),
 N("baptism3", 1, "sea", ["John 60 y165 s48 t0:talk", "Woman 130 f y172 t2:hands", "Fisherman 160 f y172"]),
 N("baptism3", 2, "sea", ["John 70 y165 s48 t0:hands", "Jesus 120 f y165 s48 t2:welcome"]),
 N("baptism3", 3, "sea", ["Jesus 90 y165 s48 t0:raise", "John 50 y165 s48 t3:cheer", "Angel 130 y40 s40 g130,60@0-2 t0:raise"]),
 N("baptism3", 4, "sea", ["Jesus 90 y165 s48 t0:raise", "John 50 y165 s48 t0:raise", "Angel 130 y60 s45 t0:raise"])])
reg("temptation3", [
 N("temptation3", 0, "desert", ["Jesus 90 t2:hands"]),
 N("temptation3", 1, "desert", ["Jesus 60 t2:welcome", "Pharisee 130 f t0:point"]),
 N("temptation3", 2, "desert", ["Jesus 60 t2:welcome", "Pharisee 130 f t0:point"], [("ruin", 140, 152, 40, (190, 160, 110))]),
 N("temptation3", 3, "desert", ["Jesus 60 t2:raise", "Pharisee 130 f t0:point t5:cower bGO!@4-6"], [])])
reg("manna3", [
 N("manna3", 0, "desert", ["Fisherman 40 t2:hands", "Woman 90 t2:hands", "Boy 140 f t2:hands", "Moses 160 f"] if False else ["Fisherman 40 t2:hands", "Woman 90 t2:hands", "Boy 140 f t2:hands"], [("bones", 0, 0, 152)] if False else []),
 N("manna3", 1, "desert", ["Moses 60 t3:hands", "Fisherman 110 f t0:raise bWE'RE_HUNGRY!@0.5-3", "Woman 150 f t0:raise"], [], sfx=[(0.6, "Fisherman", "We are starving, Moses!", 1.0)]),
 N("manna3", 2, "dawn", ["Moses 60 t1:raise", "Woman 110 f t3:cheer", "Boy 150 f t3:cheer"], []),
 N("manna3", 3, "dawn", ["Woman 50 t1:welcome", "Fisherman 100 t1:welcome", "Boy 150 f t1:welcome", "Moses 20"][:3], []),
 N("manna3", 4, "golden", ["Moses 70 t1:point", "Woman 110 f t2:cheer", "Fisherman 150 f t2:cheer"], [("tree", 28, 150, 30)])])
reg("sunstill3", [
 N("sunstill3", 0, "golden", ["Soldier 90 t2:raise"], []),
 N("sunstill3", 1, "dusk", ["Soldier 60 t1:point", "King 120 f t2:raise"], TW2),
 N("sunstill3", 2, "night", ["Soldier 40 w140@0-6", "Fisherman 10 w110@0-6"], []),
 N("sunstill3", 3, "storm", ["Fisherman 130 f t1:cower bAAAH!@1.5-3.5", "King 160 f t1:cower"], [], quake=(1, 5), sfx=[(1.5, "Fisherman", "Run! Run away!", 1.15)]),
 N("sunstill3", 4, "golden", ["Soldier 80 t0:raise", "Fisherman 120 f t3:cheer"], [])])
reg("well3", [
 N("well3", 0, "golden", ["Jesus 60 t2:welcome", "Woman 130 f t1:hands"], [("well", 95, 156)]),
 N("well3", 1, "golden", ["Woman 120 f t0:hands", "Jesus 50 t3:point"], [("well", 85, 156)]),
 N("well3", 2, "golden", ["Jesus 50 t1:welcome", "Woman 120 f t3:cower"], [("well", 85, 156)]),
 N("well3", 3, "day", ["Woman 70 w140@0-3 t3:cheer bCOME_SEE!@3.5-6", "Fisherman 160 f t4:cheer"], TW2, sfx=[(3.5, "Woman", "Come and see a man who told me everything I ever did!", 1.1)])])
reg("temple3", [
 N("temple3", 0, "palace", ["Jesus 90 t2:raise", "Fisherman 40 t0:cower", "Pharisee 150 f t0:hands"], []),
 N("temple3", 1, "palace", ["Fisherman 40 t1:talk", "Pharisee 140 f t2:welcome", "sheep 100 y176"], []),
 N("temple3", 2, "palace", ["Jesus 90 t0:raise bGET_OUT!@2-4", "Fisherman 40 t2:cower w10@2-4", "Pharisee 150 f t2:cower"], [], sfx=[(2.0, "Jesus", "Stop turning my Father's house into a marketplace!", 1.0)], sfx_echo="hall"),
 N("temple3", 3, "palace", ["Pharisee 50 t0:point", "Priest 90 y176 t0:raise", "Jesus 150 f t2:hands"], [])])
reg("catch", [
 N("catch", 0, "ship", ["Peter 60 t2:hands", "Fisherman 120 f t2:hands"]),
 N("catch", 1, "ship", ["Peter 60 t0:cower", "Fisherman 120 f t1:cower"]),
 N("catch", 2, "ship", ["Jesus 120 f t0:point", "Peter 60 t2:welcome"]),
 N("catch", 3, "ship", ["Peter 60 t0:cheer", "Fisherman 120 f t1:cheer", "Jesus 150 f t2:welcome"]),
 N("catch", 4, "ship", ["Peter 60 t0:kneel", "Jesus 120 f t0:welcome", "Fisherman 150 f t3:cheer"])])
reg("paralytic", [
 N("paralytic", 0, "house", ["Fisherman 40 t2:hands", "Boy 90 y170", "Peter 140 f t2:hands"], []),
 N("paralytic", 1, "day", ["Fisherman 50 t1:point", "Peter 90 t1:point", "Woman 130 f t0:raise", "Pharisee 160 f t0:hands"], [("hut", 100, 152, 40, 30, (200, 170, 120), (120, 70, 50))]),
 N("paralytic", 2, "day", ["Fisherman 50 t2:raise", "Peter 90 t2:raise", "Boy 70 y120 s35 g70,150@3-5 t0:kneel"], [("hut", 100, 152, 40, 30, (200, 170, 120), (120, 70, 50))]),
 N("paralytic", 3, "house", ["Jesus 90 t1:welcome", "Boy 140 f y172 t0:kneel", "Pharisee 40 t3:point"], []),
 N("paralytic", 4, "house", ["Jesus 90 t0:raise", "Boy 140 f t2:cheer w40@4-6", "Pharisee 20 t3:cower"], [])])
reg("sower", [
 N("sower", 0, "golden", ["Shepherd 70 t2:welcome"], [("tree", 154, 150, 30)]),
 N("sower", 1, "golden", ["Shepherd 70 t0:welcome", "Boy 130 f t3:point"], []),
 N("sower", 2, "golden", ["Shepherd 70 t0:welcome"], [("tree", 120, 150, 34), ("tree", 150, 150, 30)]),
 N("sower", 3, "golden", ["Shepherd 70 t2:cheer", "Woman 130 f t2:cheer"], [("tree", 28, 150, 30)]),
 N("sower", 4, "golden", ["Jesus 60 t1:talk", "Woman 110 f t3:hands", "Fisherman 150 f t3:hands"], [])])
reg("lostsheep", [
 N("lostsheep", 0, "golden", ["Shepherd 80 t2:hands", "sheep 30", "sheep 130 f", "sheep 160 f"], []),
 N("lostsheep", 1, "dusk", ["Shepherd 80 t1:hands", "sheep 30", "sheep 140 f"], []),
 N("lostsheep", 2, "night", ["Shepherd 40 w130@0-6", "sheep 150 f s38"], []),
 N("lostsheep", 3, "dawn", ["Shepherd 90 t0:cheer", "sheep 50", "sheep 130 f"], [("hut", 150, 152, 34, 24, (200, 170, 120), (120, 70, 50))]),
 N("lostsheep", 4, "golden", ["Jesus 70 t1:talk", "Woman 120 f t3:cheer", "Fisherman 150 f t3:cheer"], [])])
reg("tenlepers", [
 N("tenlepers", 0, "day", ["Fisherman 40 t0:raise bHELP_US!@1-3", "Samson 80 t0:raise", "Boy 120 t0:raise", "Jesus 160 f t3:welcome"], [], sfx=[(1.0, "Fisherman", "Jesus, have mercy on us!", 1.1)]),
 N("tenlepers", 1, "dusk", ["Fisherman 40 t2:hands", "Samson 80 t2:hands", "Boy 120 t2:hands"], [("town", 100, 180, 152, (150, 120, 96))]),
 N("tenlepers", 2, "day", ["Fisherman 40 t0:raise", "Samson 80 t0:raise", "Jesus 130 f t3:point"], TR),
 N("tenlepers", 3, "day", ["Fisherman 40 t1:cheer", "Samson 80 t1:cheer", "Boy 120 t1:cheer", "Woman 160 f t1:cheer"], TR),
 N("tenlepers", 4, "day", ["Fisherman 60 t0:kneel", "Jesus 120 f t2:point", "Samson 160 f s30 y166"][:2], TR)])
reg("balaam", [
 N("balaam", 0, "desert", ["Elder 90 t2:cower"], [("ruin", 140, 152, 40, (190, 160, 110))]),
 N("balaam", 1, "palace_dusk", ["King 90 y150 s50 t1:point", "Elder 50 t3:hands"], HL),
 N("balaam", 2, "desert", ["Elder 50 t0:point", "deer 100 f", "Angel 140 f t1:raise"][:1] + ["Angel 140 f t1:raise"], []),
 N("balaam", 3, "desert", ["Elder 50 t0:raise bHIT!@1-3", "deer 100 f bWHY_DID_YOU_HIT_ME?@3-6"], [], sfx=[(3.2, "Woman", "Why did you hit me?", 1.2)]),
 N("balaam", 4, "desert", ["Elder 70 t0:kneel", "Angel 130 f t0:raise"], [])])
reg("widowoil", [
 N("widowoil", 0, "house", ["Woman 90 t2:hands"], []),
 N("widowoil", 1, "house", ["Woman 50 t1:cower", "Pharisee 130 f t1:point bPAY_ME!@1-3", "Boy 90 s40 t3:hands"], [], sfx=[(1.0, "Pharisee", "Pay me what you owe!", 1.0)]),
 N("widowoil", 2, "house", ["Woman 50 t3:welcome", "Elder 120 f t1:talk"], []),
 N("widowoil", 3, "house", ["Woman 90 t0:cheer", "Boy 40 s40 t1:cheer", "Boy 140 s40 f t1:cheer"], []),
 N("widowoil", 4, "house", ["Elder 60 t0:point", "Woman 120 f t2:cheer"], [])])
reg("pentecost", [
 N("pentecost", 0, "house", ["Peter 40 t1:raise", "Mary 90 t1:raise", "Fisherman 140 f t1:raise"], [], quake=(1, 6)),
 N("pentecost", 1, "house", ["Peter 40 t2:hands", "Mary 90 t0:hands", "Fisherman 140 f t0:hands"], []),
 N("pentecost", 2, "house", ["Peter 40 t0:raise", "Mary 90 t0:raise", "Fisherman 140 f t0:raise"], [], quake=(0, 5)),
 N("pentecost", 3, "day", ["Peter 40 t0:talk", "Woman 90 t2:cheer", "Soldier 130 f t2:cheer", "Pharisee 160 f t2:cheer"], TW2),
 N("pentecost", 4, "day", ["Peter 60 t0:raise", "Woman 110 f t2:cheer", "Soldier 140 f t2:cheer", "Boy 30 t2:cheer"], TW2)])
reg("tenvirgins", [
 N("tenvirgins", 0, "night", ["Woman 30 t2:cheer", "Mary 70 t2:cheer", "Queen 110 f t2:hands", "Woman 150 f t2:hands"], [("hut", 150, 152, 34, 24, (200, 170, 120), (120, 70, 50))]),
 N("tenvirgins", 1, "night", ["Woman 30 t3:bow", "Mary 70 t3:bow", "Queen 110 f t3:bow", "Woman 150 f t3:bow"], []),
 N("tenvirgins", 2, "night", ["Woman 30 t0:raise bHE'S_HERE!@0.5-2.5", "Mary 70 t0:raise", "Queen 110 f t3:cower", "Woman 150 f t3:cower"], [], sfx=[(0.6, "Woman", "The groom is here!", 1.15)]),
 N("tenvirgins", 3, "night", ["Queen 40 w-20@1-4", "Woman 20 w-20@1-4", "Mary 100 t4:cheer", "Woman 150 f t4:cheer"], [("hut", 150, 152, 34, 24, (200, 170, 120), (120, 70, 50))]),
 N("tenvirgins", 4, "dawn", ["Jesus 90 t1:talk", "Woman 40 t3:hands", "Mary 140 f t3:hands"], [])])
