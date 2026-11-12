
LN = lambda x, y, sd, s=.42, fl=0: cm("lion", x, y, s, flip=fl, seed=sd, calm=False)
STORIES.update({
"daniel6": [
 g6(("DANIEL &","THE LIONS"), "A man was thrown to the lions, just for praying. And he walked out alive.", "palace_dusk",
    [cm("King", 90, 150, .5), cm("Paul", 60, 178, .5, acts=[(0, "kneel")])], HALL),
 g6(("A LAW","AGAINST PRAYER"), "Daniel prayed to God three times a day, even after King Darius signed a law forbidding it. His jealous enemies saw him, and reported him to the king.", "palace_dusk",
    [cm("King", 90, 150, .5, acts=[(0, "idle"), (10.5, "hands")]), cm("Paul", 55, 178, .5, acts=[(0, "kneel")]), cm("Pharisee", 130, 172, .55, flip=1, acts=[(0, "idle"), (6.6, "point")], bubbles=[(7.2, 8.8, "HE PRAYED!")]), cm("Priest", 160, 178, .5, flip=1, acts=[(0, "idle"), (6.9, "point")])], HALL),
 g6(("THE KING'S","SORROW"), "Daniel, may your God, whom you serve faithfully, rescue you.", "palace_dusk",
    [cm("King", 90, 150, .5, speaks=True, acts=[(0, "hands")]), cm("Paul", 60, 178, .5, acts=[(0, "bow")]), cm("Soldier", 140, 175, .55, flip=1)], HALL, voice="King", echo="hall"),
 g6(("INTO THE","DEN"), "The soldiers seized Daniel, and threw him into the den of lions.", "den",
    [cm("Soldier", 58, 108, .42, acts=[(0, "idle"), (2.0, "raise")]), cm("Soldier", 124, 108, .42, flip=1, acts=[(0, "idle"), (2.0, "raise")]),
     cm("Paul", 68, 108, .42, throw=(2.2, 3.1, 92, 168, 45), scream=(2.2, 3.5), bubbles=[(2.2, 3.7, "AAAAH!")], acts=[(3.3, "cower")]),
     LN(28, 168, 1), LN(152, 172, 2, .42, 1), LN(120, 160, 3, .38)], voice=None, sfx=[(2.3, "Paul", "Aaaaaah! No! Help!", 1.15)]),
 g6(("THE ANGEL","COMES"), "But God sent an angel, who shut the lions' mouths.", "den",
    [cm("Paul", 90, 168, .45, acts=[(0, "cower"), (3.0, "kneel")]), cm("Angel", 90, 20, .5, glide=(0.5, 2.6, 90, 160), acts=[(0, "raise")]),
     dict(LN(28, 168, 1), calm=True), dict(LN(152, 172, 2, .42, 1), calm=True), dict(LN(120, 160, 3, .38), calm=True)]),
 g6(("AT","DAWN"), "At dawn, the king hurried to the den, and called out in a worried voice.", "den",
    [cm("King", 60, 108, .42, flip=0, acts=[(0, "hands")]), cm("Paul", 90, 168, .45, acts=[(0, "kneel")]), dict(LN(28, 168, 1), calm=True), dict(LN(152, 172, 2, .42, 1), calm=True)]),
 g6(("HAS YOUR GOD","SAVED YOU?"), "Daniel! Has your God saved you from the lions?", "den",
    [cm("King", 60, 108, .42, flip=0, speaks=True, acts=[(0, "hands")]), cm("Paul", 90, 168, .45, acts=[(0, "kneel")]), dict(LN(28, 168, 1), calm=True), dict(LN(152, 172, 2, .42, 1), calm=True)], voice="King", echo="cave"),
 g6(("MY GOD","SENT AN ANGEL"), "O king, live forever! My God sent his angel, and shut the lions' mouths!", "den",
    [cm("King", 60, 108, .42, flip=0, acts=[(0, "raise")]), cm("Paul", 90, 168, .45, speaks=True, acts=[(0, "cheer")]), dict(LN(28, 168, 1), calm=True), dict(LN(152, 172, 2, .42, 1), calm=True)], voice="Paul", echo="cave"),
 g6(("UNHARMED","AND FREE"), "The king rejoiced, and ordered Daniel lifted out. Not a scratch was found on him, because he trusted his God.", "palace_dusk",
    [cm("King", 90, 150, .5, acts=[(0, "raise")]), cm("Paul", 60, 178, .5, acts=[(0, "cheer")]), cm("Soldier", 140, 175, .55, flip=1, acts=[(0, "cheer")])], HALL),
 OP6(("DANIEL","6"), "Would you keep praying, even if it cost you everything? Tell us in the comments."),
],
})
