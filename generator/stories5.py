def g(title, text, st="day", cast=(), props=()):
    return sc(title, "gen", text, set=st, cast=list(cast), props=list(props))
def L(text): return sc(("WHAT WE","LEARN"), "lesson", text)
def OUT(ref=("","")): return sc(ref, "outro2", "Which story is next? Comment below.")
J, P, D, M, Ma, So, A, E = "Jesus", "Peter", "David", "Moses", "Mary", "Solomon", "Adam", "Eve"
STORIES.update({
"basket": [
 g(("BABY","MOSES"), "A baby in a basket, floating on the Nile. Whose life was he about to change?", "river", [(Ma, 40, 143, .45, 0)], [("basket", 110, 158)]),
 g(("A CRUEL","DECREE"), "Pharaoh ordered that every Hebrew baby boy be thrown into the river.", "palace", [(So, 90, 150, .5, 0)], [("throne", 90)]),
 g(("A MOTHER'S","PLAN"), "A mother hid her baby for three months. Then she placed him in a basket among the reeds.", "river", [(Ma, 36, 143, .45, 0)], [("basket", 104, 158)]),
 g(("FOUND","BY A PRINCESS"), "Pharaoh's daughter found the basket, and took pity on the baby.", "river", [(Ma, 60, 143, .5, 0, 20)], [("basket", 110, 158)]),
 g(("A NEW","NAME"), "She named him Moses, and he grew up in the palace, to one day lead his people out.", "palace", [(M, 70, 172, .55, 0), (So, 120, 172, .55, 1)], [("throne", 150)]),
 L("What did we learn? God can prepare a great plan, even in the smallest, weakest moment."), OUT(("EXODUS","2"))],
"zacchaeus": [
 g(("THE TAX","COLLECTOR"), "A tax collector climbed a tree to see Jesus. And Jesus called him by name.", "day", [(D, 120, 120, .35, 0)], [("tree", 120, 90), ("crowd", 20, 90, 6, 175)]),
 g(("TOO SHORT","TO SEE"), "Zacchaeus was short, and the crowd blocked his view. So he ran ahead, and climbed a sycamore tree.", "day", [(D, 120, 110, .35, 0), (J, 50, 172, .55, 0, 20)], [("tree", 120, 90)]),
 g(("COME","DOWN"), "Jesus looked up and said: Zacchaeus, come down. I am staying at your house today.", "day", [(J, 70, 172, .6, 0), (D, 120, 130, .38, 1)], [("tree", 125, 90), ("glow", 120, 110, 18)]),
 g(("A NEW","HEART"), "The crowd grumbled. But Zacchaeus promised to give half his money to the poor.", "day", [(D, 100, 172, .6, 0), (J, 55, 172, .6, 0)], [("house", 130, 34, 30), ("crowd", 20, 90, 4, 176)]),
 L("What did we learn? Jesus offers a fresh start, even to people everyone else gave up on."), OUT(("LUKE","19"))],
"ruth": [
 g(("RUTH AND","NAOMI"), "She lost everything, but refused to leave her mother in law.", "desert", [(Ma, 60, 172, .55, 0), (Ma, 100, 172, .55, 0)], []),
 g(("A BROKEN","FAMILY"), "Naomi lost her husband and both sons. She decided to return home to Bethlehem.", "desert", [(Ma, 40, 172, .55, 0, 60)], [("mount", 150, 70, 40)]),
 g(("WHERE YOU","GO, I GO"), "Ruth said: where you go, I will go. Your people will be my people.", "dusk", [(Ma, 70, 172, .6, 0), (Ma, 110, 172, .6, 1)], [("sun", 90, 120)]),
 g(("THE","HARVEST"), "In Bethlehem, Ruth gathered leftover grain in the fields of a man named Boaz.", "dawn", [(Ma, 50, 172, .55, 0), (P, 125, 172, .6, 1)], [("tree", 160, 60)]),
 g(("A NEW","FAMILY"), "Boaz married Ruth. She became the great grandmother of King David.", "day", [(Ma, 70, 172, .6, 0), (P, 110, 172, .6, 1)], [("house", 130, 34, 30), ("glow", 90, 120, 20)]),
 L("What did we learn? Loyalty and kindness can change the story, for generations."), OUT(("BOOK OF","RUTH"))],
"gideon": [
 g(("GIDEON'S","ARMY"), "Three hundred men against an enormous army. And God said that was still too many.", "night", [(D, 60, 172, .5, 0), (D, 80, 172, .5, 0), (D, 100, 172, .5, 0)], [("flame", 110, 160, .8)]),
 g(("A FEARFUL","MAN"), "Gideon was hiding wheat from raiders when God called him a mighty warrior.", "day", [(D, 80, 172, .6, 0)], [("house", 120, 36, 30)]),
 g(("TOO MANY","SOLDIERS"), "God said: your army is too big. Gideon went from thirty two thousand men to three hundred.", "day", [(D, 60, 172, .6, 0)], [("crowd", 90, 170, 6, 175)]),
 g(("TRUMPETS","AND TORCHES"), "At night, each man held a trumpet and a torch hidden in a jar.", "night", [(D, 50, 172, .5, 0), (D, 90, 172, .5, 0), (D, 130, 172, .5, 0)], [("flame", 52, 150, .6), ("flame", 92, 150, .6), ("flame", 132, 150, .6)]),
 g(("THE","VICTORY"), "They broke the jars, blew the trumpets, and the enemy fled in panic.", "dark", [(D, 90, 172, .6, 0)], [("flame", 40, 160, 1.0), ("flame", 150, 160, 1.0)]),
 L("What did we learn? God does not need big numbers. He needs trust."), OUT(("JUDGES","6 TO 7"))],
"esther": [
 g(("QUEEN","ESTHER"), "A queen risked her life to save her people, without being invited.", "palace", [(Ma, 60, 172, .6, 0), (So, 120, 172, .6, 1)], [("throne", 150)]),
 g(("A NEW","QUEEN"), "Esther, a Jewish orphan, was chosen as queen of Persia. She kept her heritage secret.", "palace", [(Ma, 70, 172, .6, 0), (So, 120, 172, .6, 1)], [("throne", 90)]),
 g(("THE","PLOT"), "Haman, a powerful official, tricked the king into signing a law to destroy the Jews.", "dark", [(P, 80, 172, .6, 0), (So, 130, 172, .6, 1)], []),
 g(("IF I","PERISH"), "Her cousin Mordecai begged her to speak. Esther said: if I perish, I perish.", "palace", [(Ma, 60, 172, .6, 0, 40), (D, 150, 172, .5, 1)], []),
 g(("THE","SCEPTER"), "She entered unsummoned. The king held out his scepter, and she exposed the plot.", "palace", [(Ma, 60, 172, .6, 0, 30), (So, 110, 150, .5, 1)], [("throne", 120), ("glow", 110, 130, 22)]),
 L("What did we learn? Courage means acting, even when you are afraid."), OUT(("BOOK OF","ESTHER"))],
"lastsupper": [
 g(("THE LAST","SUPPER"), "Jesus knew it was his last night with his friends. Here is what he did.", "night", [(J, 90, 172, .6, 0)], [("table", 90), ("crowd", 30, 150, 6, 176)]),
 g(("BREAD AND","WINE"), "He took bread, gave thanks, and broke it. This is my body, he said.", "night", [(J, 90, 172, .6, 0), (P, 50, 172, .55, 0)], [("table", 90), ("glow", 90, 140, 20)]),
 g(("A BETRAYAL","FORETOLD"), "Then he said: one of you will betray me. The disciples looked at each other in shock.", "dark", [(J, 90, 172, .6, 0), (P, 50, 172, .55, 0), (D, 130, 172, .55, 1)], [("table", 90)]),
 g(("WASHING","FEET"), "Jesus even knelt and washed his disciples' feet. A teacher, serving his students.", "night", [(J, 70, 172, .6, 0), (P, 115, 172, .55, 1)], [("flame", 150, 160, .7)]),
 L("What did we learn? Real greatness looks like serving others."), OUT(("JOHN","13"))],
"job": [
 g(("THE STORY","OF JOB"), "He lost everything in one day. And still refused to curse God.", "dark", [(D, 90, 172, .6, 0)], []),
 g(("A BLESSED","MAN"), "Job was rich, healthy, and faithful, with a large family and many flocks.", "day", [(D, 90, 172, .6, 0)], [("sheep", 30, 172), ("sheep", 50, 174), ("house", 120, 36, 30)]),
 g(("EVERYTHING","LOST"), "In a single day, he lost his animals, his wealth, and his children.", "storm", [(D, 90, 172, .6, 0)], [("lightning",)]),
 g(("FRIENDS","WHO BLAMED"), "His friends said he must have sinned. But Job said: I will keep trusting God.", "dusk", [(D, 60, 172, .6, 0), (P, 120, 172, .6, 1)], []),
 g(("RESTORED","",), "In the end, God restored Job, and gave him twice as much as before.", "dawn", [(D, 90, 172, .6, 0)], [("sheep", 30, 172), ("sheep", 50, 174), ("glow", 90, 130, 24)]),
 L("What did we learn? Faith is not only for good days. It is for the hardest ones too."), OUT(("BOOK OF","JOB"))],
"jacobladder": [
 g(("JACOB'S","LADDER"), "A man runs from home, falls asleep on a stone, and sees heaven open.", "night", [(D, 70, 175, .5, 0)], [("ladder", 120)]),
 g(("RUNNING","AWAY"), "Jacob fled from his brother Esau, after tricking him. He was alone, and afraid.", "dusk", [(D, 60, 172, .55, 0, 50)], []),
 g(("A STONE","PILLOW"), "At night, he lay down and used a stone as a pillow.", "night", [(D, 90, 176, .45, 0)], [("star", 40, 40), ("star", 140, 50)]),
 g(("THE","LADDER"), "He dreamed of a ladder reaching to heaven, with angels going up and down.", "night", [(D, 60, 176, .45, 0)], [("ladder", 120)]),
 g(("I AM","WITH YOU"), "God said: I am with you, and I will not leave you. Jacob named the place Bethel.", "dawn", [(D, 90, 172, .6, 0)], [("glow", 90, 100, 30)]),
 L("What did we learn? Even when you feel alone, you are not."), OUT(("GENESIS","28"))],
"storm": [
 g(("JESUS CALMS","THE STORM"), "A storm so violent the boat was filling with water. And Jesus was asleep.", "storm", [], [("boat", 90, 150), ("lightning",)]),
 g(("A SUDDEN","STORM"), "The disciples were crossing the lake when a furious storm hit.", "storm", [], [("boat", 90, 150)]),
 g(("TEACHER","WAKE UP"), "They woke him, shouting: Teacher, don't you care that we are drowning?", "storm", [(J, 90, 150, .4, 0)], [("boat", 90, 150)]),
 g(("PEACE","BE STILL"), "Jesus stood up, and said to the wind and waves: peace, be still.", "dawn", [(J, 90, 172, .6, 0)], [("glow", 90, 130, 24)]),
 g(("CALM","AT LAST"), "The wind stopped, and the sea became completely calm. Why are you afraid, he asked.", "sea", [], [("boat", 90, 150)]),
 L("What did we learn? Jesus is with you in the storm, and he is stronger than it."), OUT(("MARK","4"))],
"lazarus": [
 g(("LAZARUS","RISES"), "Four days after he died, Jesus walked to his tomb and called his name.", "dusk", [(J, 80, 172, .6, 0)], [("mount", 140, 100, 40)]),
 g(("TOO","LATE"), "Lazarus was sick, and Jesus did not come in time. His sisters were heartbroken.", "dusk", [(Ma, 60, 172, .55, 0), (Ma, 100, 172, .55, 0)], []),
 g(("JESUS","WEPT"), "When Jesus saw them crying, he wept too.", "dusk", [(J, 80, 172, .6, 0), (Ma, 120, 172, .55, 1)], []),
 g(("THE STONE","REMOVED"), "At the tomb, he said: take away the stone. Then he prayed.", "day", [(J, 70, 172, .6, 0)], [("mount", 140, 100, 40)]),
 g(("COME","OUT"), "Then he shouted: Lazarus, come out! And the man who had died walked out alive.", "dawn", [(J, 60, 172, .6, 0), (D, 120, 172, .6, 1)], [("glow", 120, 130, 24)]),
 L("What did we learn? Jesus gives hope, even when it seems far too late."), OUT(("JOHN","11"))],
"naaman": [
 g(("NAAMAN","THE GENERAL"), "A powerful general was suffering from a skin disease, and a servant girl knew the cure.", "palace", [(So, 90, 172, .6, 0)], []),
 g(("A SERVANT","GIRL"), "She said: there is a prophet in Israel who could heal you.", "palace", [(Ma, 50, 172, .5, 0), (So, 120, 172, .6, 1)], []),
 g(("WASH","SEVEN TIMES"), "The prophet Elisha only said: go wash in the Jordan river seven times.", "day", [(P, 70, 172, .6, 0), (So, 130, 172, .6, 1)], []),
 g(("PRIDE","VS FAITH"), "Naaman was angry. It seemed too simple. But his servants convinced him to try.", "river", [(So, 90, 160, .45, 0)], []),
 g(("HEALED","",), "He washed seven times, and his skin became healthy, like a child's.", "dawn", [(So, 90, 172, .6, 0)], [("glow", 90, 130, 26)]),
 L("What did we learn? Humility opens the door to healing."), OUT(("2 KINGS","5"))],
"hannah": [
 g(("HANNAH'S","PRAYER"), "She cried and prayed for a child. And God answered in a way she never expected.", "palace", [(Ma, 80, 172, .6, 0)], [("glow", 80, 130, 24)]),
 g(("A TEARFUL","PRAYER"), "Hannah wanted a child so badly that she wept in the temple. The priest Eli thought she was drunk.", "palace", [(Ma, 60, 172, .6, 0), (P, 120, 172, .6, 1)], []),
 g(("GOD","ANSWERS"), "Eli blessed her, and God gave her a son. She named him Samuel.", "dawn", [(Ma, 90, 172, .6, 0)], [("baby", 100, 176), ("glow", 90, 130, 24)]),
 g(("A PROMISE","KEPT"), "Hannah kept her promise, and brought Samuel to serve God in the temple.", "palace", [(Ma, 60, 172, .55, 0, 30), (P, 130, 172, .6, 1)], []),
 g(("A VOICE","AT NIGHT"), "One night, Samuel heard a voice calling his name. Speak, Lord, your servant is listening.", "night", [(D, 90, 176, .4, 0)], [("glow", 90, 110, 26)]),
 L("What did we learn? Prayer is not wasted, and God hears the quiet ones."), OUT(("1 SAMUEL","1 TO 3"))],
"jacobesau": [
 g(("JACOB AND","ESAU"), "He tricked his own brother out of his blessing. And spent years paying for it.", "dusk", [(D, 60, 172, .55, 0), (M, 120, 172, .55, 1)], []),
 g(("A BOWL","OF STEW"), "Esau came home starving, and sold his birthright to Jacob for a bowl of stew.", "day", [(D, 60, 172, .55, 0), (M, 120, 172, .55, 1)], [("house", 140, 34, 30)]),
 g(("THE STOLEN","BLESSING"), "Later, Jacob disguised himself, and tricked his blind father into giving him the blessing.", "dark", [(D, 60, 172, .55, 0), (P, 125, 176, .5, 1)], []),
 g(("RUNNING","AWAY"), "Esau was furious, so Jacob fled. For twenty years, he lived far from home.", "desert", [(D, 50, 172, .55, 0, 70)], []),
 g(("A REUNION","",), "When they finally met again, Esau ran to him, and hugged him. He had forgiven him.", "dawn", [(D, 60, 172, .6, 0, 20), (M, 130, 172, .6, 1, -20)], [("glow", 95, 130, 24)]),
 L("What did we learn? Forgiveness can heal even the oldest wounds."), OUT(("GENESIS","25 TO 33"))],
"furnace": [
 g(("THE FIERY","FURNACE"), "Three men refused to bow to a golden statue. So the king threw them into a furnace.", "fire", [(D, 40, 172, .5, 0), (P, 70, 172, .5, 0), (M, 100, 172, .5, 0)], [("furnace", 150)]),
 g(("A GOLDEN","STATUE"), "King Nebuchadnezzar built a huge golden statue, and ordered everyone to bow when the music played.", "day", [], [("statue", 90), ("crowd", 20, 160, 8, 176)]),
 g(("THEY WILL","NOT BOW"), "Three young men, Shadrach, Meshach and Abednego, refused to worship it.", "day", [(D, 50, 172, .55, 0), (P, 80, 172, .55, 0), (M, 110, 172, .55, 0), (So, 150, 172, .6, 1)], [("statue", 150)]),
 g(("SEVEN TIMES","HOTTER"), "The king ordered the furnace heated seven times hotter, and threw them in.", "fire", [], [("furnace", 90)]),
 g(("A FOURTH","FIGURE"), "But the king saw four men walking in the fire, and the fourth looked like a son of the gods.", "fire", [(J, 90, 172, .6, 0)], [("furnace", 90)]),
 g(("NOT EVEN","SMOKE"), "They walked out unharmed. They did not even smell like smoke.", "day", [(D, 50, 172, .55, 0), (P, 80, 172, .55, 0), (M, 110, 172, .55, 0)], [("glow", 80, 130, 24)]),
 L("What did we learn? Standing firm is worth it, because you are never alone."), OUT(("DANIEL","3"))],
"handwriting": [
 g(("WRITING ON","THE WALL"), "A king threw a huge feast. Then a hand appeared, and began to write on the wall.", "palace", [(So, 90, 172, .6, 0)], [("script", 140, 80)]),
 g(("A ROYAL","FEAST"), "King Belshazzar drank from the sacred cups stolen from the temple in Jerusalem.", "palace", [(So, 90, 172, .6, 0), (P, 50, 172, .55, 0)], [("table", 120)]),
 g(("A HAND","APPEARS"), "Suddenly, fingers of a human hand wrote words on the wall. The king turned pale.", "palace", [(So, 70, 172, .6, 0)], [("script", 140, 80)]),
 g(("DANIEL","INTERPRETS"), "Daniel explained: your days are numbered, you have been weighed and found lacking.", "palace", [(P, 60, 172, .6, 0), (So, 130, 172, .6, 1)], [("script", 140, 70)]),
 g(("THAT","NIGHT"), "That very night, the kingdom fell.", "dark", [(So, 90, 172, .6, 0)], []),
 L("What did we learn? Pride has an expiry date, and humility lasts."), OUT(("DANIEL","5"))],
"bartimaeus": [
 g(("BLIND","BARTIMAEUS"), "A blind man shouted so loudly that the crowd told him to be quiet. He shouted louder.", "day", [(D, 40, 172, .55, 0)], [("crowd", 80, 170, 6, 175)]),
 g(("A BLIND","BEGGAR"), "Bartimaeus sat by the road, begging, when he heard that Jesus was passing by.", "day", [(D, 50, 172, .55, 0)], [("tree", 20, 70)]),
 g(("SHOUTING","FOR HELP"), "He cried out: Jesus, son of David, have mercy on me! Many told him to be quiet.", "day", [(D, 50, 172, .55, 0), (J, 130, 172, .6, 1)], [("crowd", 80, 110, 3, 176)]),
 g(("WHAT DO YOU","WANT?"), "Jesus stopped and called him. What do you want me to do for you? Teacher, I want to see.", "day", [(D, 70, 172, .6, 0), (J, 115, 172, .6, 1)], []),
 g(("HE CAN","SEE"), "Jesus said: go, your faith has healed you. Immediately he could see, and he followed Jesus.", "dawn", [(D, 70, 172, .6, 0), (J, 115, 172, .6, 1)], [("glow", 95, 130, 24)]),
 L("What did we learn? Do not let the crowd silence you. Keep calling out."), OUT(("MARK","10"))],
"damascus": [
 g(("SAUL'S","LIGHT"), "He hunted Christians. Then a blinding light knocked him to the ground.", "desert", [(P, 60, 172, .55, 0, 40)], [("light", 120)]),
 g(("A HARSH","PERSECUTOR"), "Saul was determined to arrest Jesus's followers, and was traveling to Damascus.", "desert", [(P, 40, 172, .55, 0, 60)], []),
 g(("A BLINDING","LIGHT"), "On the road, a light from heaven flashed around him. A voice said: Saul, why do you persecute me?", "day", [(P, 90, 176, .45, 0)], [("light", 90), ("glow", 90, 100, 36)]),
 g(("THREE DAYS","BLIND"), "He was blind for three days, and did not eat or drink.", "dark", [(P, 90, 172, .55, 0)], []),
 g(("A NEW","MAN"), "Then Ananias prayed for him, and his sight returned. He became Paul, one of the greatest missionaries.", "dawn", [(P, 90, 172, .6, 0), (D, 130, 172, .55, 1)], [("glow", 90, 130, 24)]),
 L("What did we learn? No one is too far gone for God to change."), OUT(("ACTS","9"))],
"denial": [
 g(("PETER'S","DENIAL"), "He swore he would never leave Jesus. Hours later, he denied him three times.", "night", [(P, 70, 172, .6, 0)], [("flame", 130, 160, .9)]),
 g(("I WILL NEVER","LEAVE YOU"), "Peter promised: even if everyone leaves you, I never will.", "night", [(P, 60, 172, .6, 0), (J, 120, 172, .6, 1)], []),
 g(("A COLD","NIGHT"), "After Jesus was arrested, Peter waited by a fire in the courtyard. People recognized him.", "dark", [(P, 80, 172, .6, 0)], [("flame", 130, 160, .9)]),
 g(("THREE","TIMES"), "Three times he said: I do not know the man. Then a rooster crowed.", "dark", [(P, 80, 172, .6, 0)], [("flame", 130, 160, .9)]),
 g(("TEARS","AND GRACE"), "Peter wept bitterly. But after the resurrection, Jesus forgave him, and trusted him again.", "dawn", [(P, 70, 172, .6, 0), (J, 120, 172, .6, 1)], [("glow", 95, 130, 24)]),
 L("What did we learn? Failing does not make you a failure. Grace gives a second chance."), OUT(("LUKE","22"))],
"baptism": [
 g(("JESUS IS","BAPTIZED"), "The heavens opened, a dove descended, and a voice spoke.", "river", [(J, 90, 150, .5, 0)], [("dove", 90, 50), ("light", 90)]),
 g(("JOHN THE","BAPTIST"), "John was baptizing crowds in the Jordan river, and calling people to change their hearts.", "river", [(P, 70, 150, .5, 0)], [("crowd", 110, 170, 4, 148)]),
 g(("JESUS","ARRIVES"), "Then Jesus came to be baptized. John said: I should be baptized by you.", "river", [(P, 60, 150, .5, 0), (J, 120, 150, .5, 1)], []),
 g(("HEAVEN","OPENS"), "As he came up out of the water, the heavens opened, and the Spirit descended like a dove.", "river", [(J, 90, 150, .5, 0)], [("dove", 90, 50), ("light", 90)]),
 g(("A VOICE","FROM HEAVEN"), "A voice said: this is my beloved son, with whom I am well pleased.", "day", [(J, 90, 172, .6, 0)], [("glow", 90, 100, 36)]),
 L("What did we learn? Before Jesus did anything, he was already loved. So are you."), OUT(("MATTHEW","3"))],
"temptation": [
 g(("TEMPTED","IN THE DESERT"), "Forty days with no food. Then the tempter showed up.", "desert", [(J, 90, 172, .6, 0)], []),
 g(("FORTY DAYS","FASTING"), "After his baptism, Jesus went into the desert and fasted for forty days.", "desert", [(J, 90, 172, .6, 0)], [("mount", 150, 80, 40)]),
 g(("STONES TO","BREAD"), "The tempter said: if you are the son of God, turn these stones into bread. Jesus answered: people live on every word from God.", "desert", [(J, 70, 172, .6, 0)], []),
 g(("THE HIGH","PLACE"), "Next, he was taken to the top of the temple. Jesus said: do not put God to the test.", "day", [(J, 90, 120, .45, 0)], [("mount", 90, 90, 36)]),
 g(("ALL THE","KINGDOMS"), "Finally, he was offered every kingdom of the world, if he would bow. Jesus said: worship God alone.", "dawn", [(J, 90, 172, .6, 0)], [("glow", 90, 130, 24)]),
 L("What did we learn? Truth is stronger than temptation, when you know it by heart."), OUT(("MATTHEW","4"))],
"manna": [
 g(("BREAD FROM","HEAVEN"), "Millions of people in the desert, and nothing to eat. Then bread fell from the sky.", "desert", [(M, 90, 172, .6, 0)], [("bread",)]),
 g(("HUNGRY","IN THE DESERT"), "The Israelites complained: in Egypt, at least we had food.", "desert", [], [("crowd", 20, 160, 8, 176)]),
 g(("A STRANGE","FLAKE"), "God said: I will rain down bread. In the morning, white flakes covered the ground.", "dawn", [(M, 90, 172, .6, 0)], [("bread",)]),
 g(("JUST","ENOUGH"), "They were told to gather only what they needed for that day. Anyone who kept extra found it spoiled.", "desert", [(M, 70, 172, .55, 0)], [("crowd", 100, 160, 4, 176)]),
 g(("FORTY","YEARS"), "God provided manna for forty years, until they reached the promised land.", "day", [(M, 90, 172, .6, 0)], [("glow", 90, 130, 24)]),
 L("What did we learn? God provides what we need today, and asks us to trust him for tomorrow."), OUT(("EXODUS","16"))],
"sunstill": [
 g(("THE SUN","STOOD STILL"), "Joshua asked God to stop the sun. And the sun stood still.", "day", [(D, 90, 172, .6, 0)], [("sun", 130, 50)]),
 g(("AN ALLIANCE","UNDER ATTACK"), "Five kings attacked Gibeon, a city that had made peace with Israel. Joshua came to defend it.", "dusk", [(D, 80, 172, .6, 0)], [("wall", 120, 170)]),
 g(("A NIGHT","MARCH"), "Joshua marched all night, and surprised the enemy at dawn.", "night", [(D, 50, 172, .55, 0, 60)], [("star", 40, 40), ("moon", 140, 40)]),
 g(("HAILSTONES","FROM SKY"), "God sent huge hailstones that fell on the fleeing armies.", "storm", [(D, 90, 172, .55, 0)], []),
 g(("A LONG","DAY"), "Joshua prayed: sun, stand still. And the sun stayed in the sky, until Israel won.", "day", [(D, 90, 172, .6, 0)], [("sun", 100, 40), ("moon", 140, 50)]),
 L("What did we learn? Bold prayers matter, and God can do what looks impossible."), OUT(("JOSHUA","10"))],
"well": [
 g(("THE WOMAN","AT THE WELL"), "Jesus asked a stranger for water, and the conversation changed her whole life.", "desert", [(J, 60, 172, .6, 0), (Ma, 130, 172, .55, 1)], [("well", 95), ("sun", 90, 40)]),
 g(("NOON AT","THE WELL"), "At noon, a Samaritan woman came to draw water. Jesus was sitting there, tired.", "desert", [(J, 60, 172, .6, 0), (Ma, 140, 172, .55, 1)], [("well", 100)]),
 g(("A STRANGE","REQUEST"), "He said: give me a drink. She was surprised, because Jews did not speak with Samaritans.", "desert", [(J, 60, 172, .6, 0), (Ma, 130, 172, .55, 1)], [("well", 95)]),
 g(("LIVING","WATER"), "Jesus told her about living water, and a spring that never runs dry. He knew her whole story.", "day", [(J, 60, 172, .6, 0), (Ma, 130, 172, .55, 1)], [("well", 95), ("glow", 95, 130, 20)]),
 g(("SHE RAN","TO TELL"), "She left her water jar, and ran back to town. Come and see a man who knows everything about me.", "day", [(Ma, 140, 172, .55, 0, -100)], [("house", 20, 36, 30), ("well", 90)]),
 L("What did we learn? Jesus meets us as we are, and offers something no one else can."), OUT(("JOHN","4"))],
"temple": [
 g(("JESUS CLEARS","THE TEMPLE"), "Jesus made a whip, and turned over the tables.", "palace", [(J, 90, 172, .65, 0)], [("table", 40), ("table", 140)]),
 g(("A HOUSE OF","PRAYER"), "The temple courtyard was full of merchants and money changers.", "palace", [(P, 40, 172, .5, 0)], [("table", 50), ("crowd", 90, 160, 4, 176)]),
 g(("TABLES","FLIPPED"), "Jesus drove them out, and overturned their tables. Stop turning my father's house into a market.", "palace", [(J, 90, 172, .65, 0, 20)], [("table", 40), ("glow", 90, 130, 24)]),
 g(("ANGRY","LEADERS"), "The religious leaders were furious, but the people listened to him.", "palace", [(J, 80, 172, .6, 0), (So, 140, 172, .6, 1)], []),
 L("What did we learn? Jesus cares about honest worship, not business as usual."), OUT(("JOHN","2"))],
})

# lesson scenes disabled for now (user asked for them only later)
for _k in list(STORIES):
    STORIES[_k] = [s for s in STORIES[_k] if s["draw"] != "lesson"]
