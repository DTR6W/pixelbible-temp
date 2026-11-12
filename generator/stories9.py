def cm(n, x, y, s=.55, **k): return dict(n=n, x=x, y=y, s=s, **k)
def g6(title, text, env, cast, props=(), voice=None, echo=None, sfx=(), sfx_echo=None, quake=None):
    return sc(title, "g6", text, env=env, cast=list(cast), props=list(props), voice=voice, echo=echo, sfx=list(sfx), sfx_echo=sfx_echo, quake=quake)
def OP6(ref, line): return sc(ref, "outro2", line + " Like, comment, share, and subscribe!")
HALL = ["throne"]
STORIES.update({
"mephi": [
 g6(("A KING'S","KINDNESS"), "A broken, crippled man was sure the king would kill him. Instead, the king gave him a seat at his own table.", "dusk",
    [cm("Boy", 80, 172, .55, acts=[(0, "idle"), (1.5, "cower")])], [("ruin", 100, 152, 60, (130, 108, 96)), ("palm", 28, 150, 40)]),
 g6(("DAVID'S","QUESTION"), "When David became king, he asked: is anyone left from Saul's family, so I can show them kindness for Jonathan's sake?", "palace",
    [cm("David", 90, 150, .5, acts=[(0, "idle"), (2.5, "talk")]), cm("Elder", 40, 172, .55, acts=[(0, "bow")]), cm("Soldier", 140, 172, .55, flip=1)], HALL),
 g6(("A HIDDEN","HEIR"), "A servant named Ziba answered: there is Jonathan's son, Mephibosheth. He is lame in both feet.", "palace",
    [cm("David", 90, 150, .5, acts=[(0, "idle"), (3, "hands")]), cm("Elder", 45, 172, .55, flip=0, acts=[(0, "point")]), cm("Soldier", 140, 172, .55, flip=1)], HALL),
 g6(("SUMMONED","TO THE PALACE"), "Mephibosheth was brought to the palace, trembling, and fell on his face before the king.", "palace",
    [cm("David", 90, 150, .5), cm("Boy", 70, 190, .6, walk=(0, 2.5, 90), acts=[(0, "idle"), (2.6, "bow")]), cm("Soldier", 140, 172, .55, flip=1)], HALL),
 g6(("DO NOT","BE AFRAID"), "Do not be afraid. I will show you kindness for your father Jonathan's sake. You will always eat at my table.", "palace",
    [cm("David", 90, 150, .5, speaks=True, acts=[(0, "welcome")]), cm("Boy", 90, 184, .6, acts=[(0, "bow"), (3.2, "cheer")]), cm("Soldier", 140, 172, .55, flip=1)], HALL, voice="David", echo="hall"),
 g6(("A SEAT AT","THE TABLE"), "From that day on, he ate at the king's table, like one of the king's own sons.", "palace",
    [cm("David", 90, 160, .5, acts=[(0, "welcome")]), cm("Boy", 52, 166, .45, acts=[(0, "cheer")]), cm("Elder", 130, 166, .5, acts=[(0, "cheer")])], ["throne", "table"]),
 OP6(("2 SAMUEL","9"), "Who showed you kindness you did not deserve? Tell us in the comments."),
],
})
