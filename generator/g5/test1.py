import engine5 as E, time
from PIL import Image
HZ=E.HZ
scenes = [
 dict(env="eden", sky="eden", ground="lush", trees="many", seed=3, dyn=[("river",700,800),("tree_life",240,HZ+30,70),("tree_know",330,HZ+34,56),("butterflies",4),("shafts",260,4,26)],
      cast=[dict(n="Adam",eden=1,x=200,y=HZ+40,s=0.72,acts=[(0,"point")]),dict(n="Eve",eden=1,x=290,y=HZ+44,s=0.72,flip=1,acts=[(0,"hold_fruit")])]),
 dict(env="field", sky="golden", ground="dirt", trees="few", seed=5, props=[("altar",150,HZ+40),("altar",330,HZ+40),("field",380,470)], dyn=[("fire",150,HZ+26,0.9),("smoke",150,HZ+10,0,1.0,0.0),("smoke",330,HZ+30,0,0.3,1.5,False),("fire",330,HZ+26,0.5),("flock",3,30,HZ+60)],
      cast=[dict(n="Abel",x=120,y=HZ+56,acts=[(0,"pray")]),dict(n="Cain",x=360,y=HZ+56,flip=1,acts=[(0,"cower")])]),
 dict(env="plain", sky="grey", ground="dirt", trees="none", seed=7, mountains=True, props=[("logs",60,HZ+70)], dyn=[("ark",250,HZ+40,0.65)],
      cast=[dict(n="Noah",x=120,y=HZ+66,acts=[(0,"point")]),dict(n="Shem",x=180,y=HZ+60,acts=[(0,"hammer")]),dict(n="Ham",x=300,y=HZ+64,acts=[(0,"carry_log")]),dict(n="Japheth",x=400,y=HZ+62,flip=1,acts=[(0,"pitch")])]),
 dict(env="sea", sky="storm", level=HZ-10, dyn=[("ark",240,HZ-14,1.0,False,True)], post=[("rain",0,1.2),("lightning",0,3.0)]),
 dict(env="plain", sky="noon", ground="sand", trees="none", seed=9, props=[("city",0,180,HZ+6),("bricks",380,HZ+60)], dyn=[("tower",300,HZ+30,0.7)],
      cast=[dict(n="Nimrod",x=120,y=HZ+60,acts=[(0,"point_up")]),dict(n="Worker",x=220,y=HZ+58,acts=[(0,"carry")]),dict(n="Worker2",x=400,y=HZ+62,flip=1,acts=[(0,"hammer")]),dict(n="Worker3",x=330,y=HZ+70,acts=[(0,"prostrate")])]),
 dict(env="ararat", sky="dawn", ground="rock", trees="few", seed=11, props=[("altar",240,HZ+50)], dyn=[("ark",150,HZ-30,1.0,False),("fire",240,HZ+36,1.0),("smoke",240,HZ+20,0,1.2),("rainbow",0)],
      cast=[dict(n="Noah",x=200,y=HZ+62,acts=[(0,"praise")]),dict(n="Naamah",x=290,y=HZ+62,flip=1,acts=[(0,"kneel")]),dict(n="Shem",x=330,y=HZ+70,acts=[(0,"pray")])]),
]
t0=time.time()
sh = Image.new("RGB",(3*480, 2*270))
for i,o in enumerate(scenes):
    im = E.compose(o, 3.3, 3.3, [0.0])
    sh.paste(im, ((i%3)*480,(i//3)*270))
print("avg compose", round((time.time()-t0)/len(scenes),3))
sh.resize((sh.width*2, sh.height*2), Image.NEAREST).save("sheet1.png")
E.upscale_post(E.compose(scenes[0],3.3,3.3,[0.0])).save("full1.png")
