import random
names=["Clownpierce","FlameFrags","Mapicc","ManePear","Peentar","Wemmbu"]
deaths=[0,0,0,0,0,0]
for i in range(len(names)*20):
    name=random.choice(names)
    print(f"{name} was slain by Lavapool123")
    deaths[names.index(name)]+=1
    if deaths[names.index(name)]>=20:
        x=names.index(name)
        print(f"{names[x]} was BANNED ")
        print(f"{names[x]} left the game")
        names.pop(x)
        deaths.pop(x)