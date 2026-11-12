HOOK = {
"zacchaeus3":("Nobody wanted this man near Jesus.","Would you climb a tree just to see Jesus?"),
"ruth3":("She lost everything, and still refused to leave.","Who in your life would you never leave?"),
"gideon3":("Three hundred men against a whole army. It makes no sense.","Would you march with just three hundred men?"),
"esther3":("One wrong step and she would die. She stepped anyway.","Would you risk everything to save your people?"),
"lastsupper3":("Jesus knew one of them would betray him. He ate with him anyway.","What would you say at your last dinner with friends?"),
"job3":("He lost his children, his money and his health in one day.","Could you keep trusting God after losing everything?"),
"jacobladder3":("A man on the run saw heaven open.","Have you ever felt God close when you felt alone?"),
"storm3":("The waves were killing them. And Jesus was asleep.","What storm are you facing right now?"),
"lazarus3":("Lazarus had been dead for four days.","What would you say to Jesus at the tomb?"),
"naaman3":("A mighty commander was told to wash in a dirty river.","Would pride have stopped you from washing in the Jordan?"),
"hannah3":("She cried so hard the priest thought she was drunk.","What prayer are you still waiting on?"),
"jacobesau3":("He stole his brother's blessing. Then he had to face him.","Would you have forgiven your brother?"),
"furnace3":("They refused to bow, so the king threw them into the fire.","Would you refuse to bow, even in front of a furnace?"),
"handwriting3":("A hand appeared out of nowhere and wrote on the wall.","What would you do if a hand wrote on your wall?"),
"bartimaeus3":("Everyone told him to be quiet. He shouted louder.","Would you keep shouting when everyone says be quiet?"),
"damascus3":("He hunted Christians, until a light knocked him to the ground.","What was your turning point?"),
"denial3":("Peter swore he would never leave Jesus. Hours later, he lied.","Have you ever denied Jesus out of fear?"),
"baptism3":("When Jesus came out of the water, heaven spoke.","Did you know the Trinity was there at the baptism?"),
"temptation3":("Forty days without food, and then the devil showed up.","Which temptation is hardest for you?"),
"manna3":("Bread fell from the sky every morning.","Would you trust God for daily bread?"),
"sunstill3":("Joshua told the sun to stop. And it did.","Do you believe God can stop the sun?"),
"well3":("A woman went to the well at noon to avoid everyone. Then Jesus spoke to her.","What would you ask for if Jesus offered living water?"),
"temple3":("Jesus flipped the tables and drove them out with a whip.","Was Jesus right to flip the tables?"),
"catch":("They fished all night and caught nothing.","Would you leave everything to follow Jesus?"),
"paralytic":("His friends tore off a roof to get him to Jesus.","Who would you carry to Jesus?"),
"sower":("Same seed. Four different results.","What kind of soil is your heart?"),
"lostsheep":("He left ninety-nine sheep to find one.","Have you ever felt like the lost sheep?"),
"tenlepers":("Ten men were healed. Only one came back.","Are you the one who comes back to say thanks?"),
"balaam":("A donkey spoke, and the prophet answered back.","Would you have listened to the donkey?"),
"widowoil":("She had one jar of oil, and a debt she couldn't pay.","What is your small jar of oil?"),
"pentecost":("Fire fell from the sky and nobody got burned.","Did you know about the day of fire at Pentecost?"),
"tenvirgins":("Half of them were shut out of the wedding.","Would you have been ready with oil?"),
}
for _o,(_h,_q) in HOOK.items():
    _sc = [dict(s) for s in STORIES["n_"+_o]]
    _sc[0]["text"] = _h + " " + _sc[0]["text"]
    _sc[-1]["text"] = _q + " Tell us in the comments. Like, share, and subscribe for more Bible stories."
    STORIES["h_"+_o] = _sc
