import importlib.util
import subprocess
import random
import time
import sys
for package in ['pyautogui','pygetwindow']:
    if importlib.util.find_spec(package) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
import pygetwindow
import pyautogui
def chapterRun(chapter):
    if chapter==0:
        global name
        name=input(f"You turn back, into a cozy bedroom. A violet hearth crackles in the corner. A voice in your head speaks. You are not shocked by this, because you are used to it, though you've never heard it before. \nPray tell, adventurer, what is your name? ").strip().capitalize()
        dialogueChoice=input(f"Ah, {name}. Nice to make your acquaintance. My name is... Well, I doubt you need to know that. You may call me Fiaguhop for now. \nDialogue options: \nA: Is that a title? \nB: C'mon, you can tell me your name. It can't be that bad, right? \nC: Oookay, Fiaguhop. Where am I? \n{name}: ").strip().lower()
        if dialogueChoice=="a":
            print("Of sorts. I guess you could call it more of a... nickname")
        elif dialogueChoice=="b":
            print("Nosy, I see. And here I was so looking forward to you. I thought you'd be different. Ah well, no matter. ")
            time.sleep(5)
            lose()
        elif dialogueChoice=="c":
            print("Why, you're in your bedroom. Don't you recognize it? ")
            time.sleep(1)
            print("You do. Strangely enough, though you've never been here, it feels familiar.")
        else:
            print("Now, now, I told you. No typos. No misspellings.")
            time.sleep(1)
            lose()
        print("Now, enough questions. It's time for business. Go over to the hearth. ")
        time.sleep(1)
        print("You walk over to the hearth, and notice that the flames are swirling counterclockwise. They spin faster and faster, and reach out to you. You reach your hand out to it, and it sucks you in. ")
        chapname="the prologue"
    else:
        try:
            print(f"Chapter {chapter}: {chapterTitles[chapter]}")
        except IndexError:
            print("That's all for now! See you again.")
            exit()
        chapname=f"chapter {chapter}"
        if chapter==1:
            choice=input(f"The flames spit you out, and you roll to a stop in a grassy meadow. There are many colorful flowers surrounding you. \nYour first task? Getting home. \nDon't die. It would such a shame. \nDo you: \nA: Look around\nB: Pick a flower\n{name}: ").strip().lower()
            if "a" in choice:
                print("You look around. The meadow stretches endlessly. The flowers are pretty, so you go to pick a few.")
            elif "b" in choice:
                print("You pick up the closest flower.")
            else:
                print("Now, now, I told you. No typos. No misspellings.")
                time.sleep(1)
                lose()
            global violets
            roses=0
            violets=0
            clovers=0
            daffodils=0
            picking=True
            while picking:
                flower=random.choice(['Rose','Violet','Clover','Daffodil'])
                print(f"It's a {flower}.")
                if flower=='Rose':
                    print("You pick it up gently so you don't get pricked.")
                    roses+=1
                elif flower=='Violet':
                    print("It shimmers enchantingly purple.")
                    violets+=1
                elif flower=='Clover':
                    if random.choice(["Clover","NOT"])=="Clover":
                        print("You are slightly disappointed, but then you notice it has 4 leaves.")
                    else:
                        print("You pick it up, and notice it has 3 leaves. It's pretty.")
                    clovers+=1
                elif flower=='Daffodil':
                    print("The petals fans out like a yellow star, catching the light.")
                    daffodils+=1
                if 'n' in input(f"Would you like to pick another flower? \n{name}: ").strip().lower():
                    picking=False
            if roses+violets+clovers+daffodils==1:
                print("It's a pretty flower.")
            else:
                print(f"You have {roses+violets+clovers+daffodils} flowers.")
            choice=input(f"You see a tree in the distance, and walk to it. It looks dead. \nDo you: \nA: Grab a few twigs \nB: Try to climb it \n{name}:").strip().lower()
            if "a" in choice:
                print("You grab a handful of dry twigs. They look like good kindling.")
            elif "b" in choice:
                print("You grab the first branch and pull yourself up. \nThe branch cracks. You fall. ")
                time.sleep(1.5)
                lose()
            else:
                print("Now, now, I told you. No typos. No misspellings.")
                time.sleep(1)
                lose()
            print("With nothing else to do, you gather the sticks in a pile and try to light them on fire, with the hope that the magical hearth fire will reappear. \nSurprisingly, a fire starts, but it looks like a normal fire. ")
            if violets>=1:
                print("Remembering that the magic fire is violet, you add a violet to the flame. The fire flares brightly, and the hue changes to violet. The flames start swirling again.")
                violets-=1
            else:
                print("You remember the magic hearth was violet, but you don't see a way to change it. Frustrated, you grab a handful of foliage and throw it at the fire.")
                flower=random.choice(['Rose','Violet','Clover','Daffodil'])
                if "Violet"==flower:
                    print("It works, and the fire turns violet. The flames begin to swirl counterclockwise.")
                else:
                    print(f"The fire eats up the grass and {flower.lower()}, but it was the wrong flower. It flares up brightly, and burns you. You angrily throw another handful of foliage in.")
                    flower=[random.choice(['Rose','Violet','Clover','Daffodil']),random.choice(['Rose','Violet','Clover','Daffodil'])]
                    if "Violet"==flower[0] or "Violet"==flower[1]:
                        print("It works, and the fire turns violet. The flames begin to swirl counterclockwise slowly.")
                    else:
                        if flower[0]==flower[1]:
                            print(f"The fire eats up the grass and {random.choice([flower[0],flower[1]]).lower()}s but they were wrong. The flames flare up angrily, and you are sucked into a world of flames.")
                        else:
                            print(f"The fire eats up the grass, {flower[0].lower()}, and {flower[1].lower()}, but they were the wrong flowers. It flares up angrily, and you are sucked into a world of flames.")
                        lose()
        if chapter==2:
            print("The flames spit you out back into your bedroom.")
        if chapter==3:
            print("Not done yet")
    if "y" in input(f"Congratulations. You've {random.choice(['completed','finished'])} {chapname}. Would you like to continue? \n").strip().lower():
        chapterRun(chapter+1)
    else:
        lose()
chapterTitles=['The beginning','The meadow']
def lose():
    print("Bye!")
    time.sleep(1)
    pyautogui.FAILSAFE=False
    pythonRunner=pygetwindow.getActiveWindow()
    restorationAttempted=False
    while True:
        if restorationAttempted:
            dangerMode=False
            if dangerMode:
                pyautogui.hotkey('alt', 'tab')
                pyautogui.hotkey('alt', 'f4')
            else:
                print("Gotcha.")
                time.sleep(1)
                pyautogui.hotkey('alt', 'f4')
        else:
            if not pythonRunner.isMinimized:
                pythonRunner.minimize()
                restorationAttempted=True
door=input(f"\n\n\nWelcome to my game! Please use proper spelling or you will die. (Or I guess your computer will die but same difference) \n\nYou enter a room. It is empty of all furniture, and the walls are stark white. There are two doors, marked: \n Life. \n Death. \n A sign reads: \nChoose neither. \nTurn back. \n\nNow. \nWhat would you like to do? \n").strip().lower()
if door!="life": 
    if "turn back" in door or "neither" in door:
        chapterRun(0)
    else:
        print("The door leads to a pitfall. You fall in. ")
        time.sleep(1)
        lose()
else:
    print("You walk in the door. A beautiful garden is outside, and there are butterflies fluttering around. The sun is shining, the birds are chirping, and everything is great.")
    time.sleep(3)
    print("Everything is peaceful. You're safe.")
    time.sleep(1)
    print("Or so you think.")
    time.sleep(1)
    lose()