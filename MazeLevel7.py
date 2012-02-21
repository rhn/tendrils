"""
Special maze locations for level 7.

Plot of level seven:
- You meet two rabbits, each wants something (honey, and bread)
- One rabbit wants BREAD, the other wants HONEY.
To get bread, you defeat the SLIME KING for the PASTRY CHEF.
To get honey, you defeat CLIPPY THE PAPER-CLIP for the HIVE OF BEES (cf dk3?)
Once the two rabbits are happy, they agree to help you.  They head into the BEDROOM to make you an ARMY.

If you give some PIE to a PYTHON, he'll give you a SPACESHIP THINGAMABOB which you can give
 to SLIPPY THE TOAD to fix his SPACESHIP.  In gratitude, toad gives you your new spells.

Once the RABBIT ARMY is complete (takes 1 rest in the inn OR one day real time), you can use it to assault
the castle, and finish the level.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms
import time
import Music
import Maze

def EnterMazeLevel():
    "Event handler: Entering this maze level"
    M = Global.Maze
    ##############################
    # The SPACESHIP might be gone:
    if Global.Party.EventFlags.get("L7SpaceshipReward", 0):
        # Erase some maze contents:
        for X in range(3,9):
            for Y in range(14,18):
                M.RemoveWalls(X,Y)
        for X in range(3,9):
            M.Walls[0][(X, 13)] = 0
            M.Walls[1][(X, 18)] = 0
        for X in range(30):
            for Y in range(30):
                if M.Rooms[(X,Y)] in (420, 403): 
                    M.Rooms[(X,Y)] = 0
    
ClippyBooty = ({"X-Potion":3}, {"Gold":5000}, 2)
def DoClippy(S,M,X,Y):
    if Global.Party.KilledBosses.get((7, "Clippy")):
        if Global.Party.LootedChests.get((X, Y, Global.Maze.Level)):
            return 1 # empty room!
        Global.App.AskDisarmChest(ClippyBooty[0], ClippyBooty[1], ClippyBooty[2])
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()    
    S.Redraw()                
    Music.PauseSong()
    Resources.PlayStandardSound("ClippyLives.wav")
    Str = """A <CN:BRIGHTRED>metal golem</C> stands before you, twisted and evil.\n\n<CENTER>PREPARE TO FIGHT!</CENTER>"""
    Global.App.ShowNewDialog(Str, Callback = FightClippyCallback)

def FightClippyCallback():
    Monsters = [[Global.Bestiary.GetCritter("Clippy"),]]
    Global.App.BeginBattle(Monsters, ClippyBooty, BossBattleName = "Clippy", CanFlee = 0)
    return 1

def DoPython(S,M,X,Y):
    Global.App.DoNPC("Python")
    return 0

def DoSpaceshipCockpit(S,M,X,Y):
    # Display some info:
    if Global.Party.EventFlags.get("L7FixedSpaceship"):
        MazeRooms.DoSign(S,M,X,Y,"The starship appears to be in working order.  \
Panels of <CN:BRIGHTBLUE>l<CN:BRIGHTGREEN>i<CN:YELLOW>g<CN:BRIGHTRED>h<CN:PURPLE>t<CN:ORANGE>s<CN:WHITE> \
blink on and off, looking very high-tech.")
        return 1
    
    if Global.Party.KeyItemFlags.get("Spaceship Parts"):
        Str = "You successfully gathered the missing starship parts!\n\n\
After a few profanity-filled hours with the manual, you are able to hook everything back up.  When you finish, the \
starship begins to emit a serene hum, and the letters <CN:BRIGHTGREEN>ALL SYSTEMS FUNCTIONAL</C> appear on the \
primary viewscreen."
        del Global.Party.KeyItemFlags["Spaceship Parts"]
        Global.Party.EventFlags["L7FixedSpaceship"] = 1
        Global.Party.X = X
        Global.Party.Y = Y
        S.RenderMaze()    
        S.Redraw()            
        Global.App.ShowNewDialog(Str)
        return 1
    MazeRooms.DoSign(S,M,X,Y,"This appears to be the control room of the starship.  An impressive command chair \
faces a primary viewscreen (currently dark).  There are no lights or sounds; apparently the crash broke some \
things.")
    return 1 

def DoBeehive(S,M,X,Y):
    Global.App.DoNPC("Bees")
    return 0

def DoPie(S,M,X,Y):
    if Global.Party.EventFlags.get("L7GotPie"):
        MazeRooms.DoSign(S,M,X,Y,"The yummy scent of pie still lingers here")
        return 1
    Global.Party.EventFlags["L7GotPie"] = 1
    Global.Party.KeyItemFlags["Yummy Pie"] = 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()    
    S.Redraw()    
    Global.App.ShowNewDialog("You find a <CN:BRIGHTBLUE>blueberry</C> pie abandoned here.\n\nStrangely enough, it is divided into seven pieces.\n\nYou take the pie with you.")
    return 1 #%%%

def DoBakery(S,M,X,Y):
    Global.App.DoNPC("Pastry Chef")
    return 0

def DoCastle(S,M,X,Y):
    if Global.Party.EventFlags.get("L7DefeatedCastle"):
        MazeRooms.DoSign(S,M,X,Y,"The wreckage from a great battle is here.\n\nDemon <CN:BRIGHTRED>blood</c> is splattered over the walls, floor and ceiling.")
        return 1
    if Global.Party.KeyItemFlags.get("Army of Rabbits"):
        Str = "With a mighty warcry and a wiggling of noses, the rabbit army leaps to the attack!  Demons and \
undead defend the castle as best they can, and soon the field is covered in confusion and tumult.\n\n\
Eventually the dust clears, and you see that you are victorious!  The rabbits collect their wounded and \
go off drinking.  The castle is now clear."
        del Global.Party.KeyItemFlags["Army of Rabbits"]
        Global.Party.EventFlags["L7DefeatedCastle"] = 1
        Global.App.ShowNewDialog(Str)
        return 1
    Str = "The castle is defended by hordes of demons and undead.  It would be suicide to attack it!\n\nYou pull back out of the range of the boiling oil."
    Global.App.ShowNewDialog(Str)
    return 0

def DoBoatMan(S,M,X,Y):
    return 1 #%%%

MoldBooty = ({}, {"Gold":10000}, 2)
def DoMoldMonster(S,M,X,Y):
    MazeRooms.DoSign(S,M,X,Y,"The floor here is <CN:PURPLE>covered in slime</c>."),
    if Global.Party.KilledBosses.get((7, "KingSlime")):
        if Global.Party.LootedChests.get((X, Y, Global.Maze.Level)):
            return 1 # empty room!
        Global.App.AskDisarmChest(MoldBooty[0], MoldBooty[1], MoldBooty[2])
        return 1
    Monsters = [[Global.Bestiary.GetCritter("King Slime"),]]
    Global.App.BeginBattle(Monsters, MoldBooty, "Gamelan.xm", BossBattleName = "KingSlime", CanFlee = 0)
    return 1

def DoClock(S,M,X,Y):
    Str = time.strftime("%I:%M %p (%A)")
    if Str[0]=="0": # looks dorky
        Str = Str[1:]
    Str = "A large clock is here.  The face reads:\n\n<CENTER><CN:BRIGHTGREEN>%s"%Str
    MazeRooms.DoSign(S,M,X,Y,Str)
    return 1 

def DoToad(S,M,X,Y):
    if Global.Party.EventFlags.get("L7SpaceshipReward"):
        MazeRooms.DoSign(S,M,X,Y,"(This makeshift shelter is empty)\n(Your amphibious ally, Slippy, has returned to outer space)")
        return 1
    else:
        Global.App.DoNPC("Toad")
        return 0

def DoRabbitA(S,M,X,Y):
    # The rabbits may be gone:
    BreedTime = Global.Party.EventFlags.get("L7RabbitBreedTime")
    Now = time.time()
    if BreedTime and (Now < BreedTime):
        MazeRooms.DoSign(S,M,X,Y,"(Kuni's house - no one is home)")
        return 1    
    Global.App.DoNPC("RabbitA")
    return 0

def DoRabbitB(S,M,X,Y):
    # The rabbits may be gone:
    BreedTime = Global.Party.EventFlags.get("L7RabbitBreedTime")
    Now = time.time()
    if BreedTime and (Now < BreedTime):
        MazeRooms.DoSign(S,M,X,Y,"(Klo's house - no one is home)")
        return 1    
    Global.App.DoNPC("RabbitB")
    return 0

def DoRabbitArmy(S,M,X,Y):
    #%%%
    return 1

def DoDoNotDisturb(S,M,X,Y):
    BreedTime = Global.Party.EventFlags.get("L7RabbitBreedTime")
    Now = time.time()
    if BreedTime and (Now < BreedTime):
        M.Walls[3][(X, Y)] = 111 #%%%
        MazeRooms.DoSign(S,M,X,Y,"A sign is tacked to the door:\n\n<CN:BRIGHTRED><CENTER>DO NOT DISTURB")
    else:
        M.Walls[3][(X, Y)] = 2
    return 1

def DoRibbonGet(S,M,X,Y):
    if Global.Party.KeyItemFlags.get("Blue Ribbon"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()    
    S.Redraw()
    Global.Party.KeyItemFlags["Blue Ribbon"] = 1
    Str = "You find a silken <CN:BRIGHTBLUE>blue ribbon</c> in the center of the ring of stones.  It seems important, somehow...\n\nSewn into the ribbon are the symbols <CN:BRIGHTGREEN>Z1T0</C>.  Huh...must be some sort of code."
    Global.App.ShowNewDialog(Str)

def DoElevator(S, M, X, Y):
    if Global.Party.KeyItemFlags.get("Blue Ribbon"):
        Global.Party.X = X
        Global.Party.Y = Y
        S.RenderMaze(1)
        S.Redraw()
        Str = "A sign on the wall reads:\n\n<CENTER><CN:ORANGE>Express Elevator</c>\n\nOn the wall a <CN:BRIGHTRED>big red button</c>.\n\nPush it?"
        Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = lambda S=S:TakeElevator(S))
        return 1
    MazeRooms.DoSign(S, M, X, Y, "A sign on the wall reads:\n\n<CENTER><CN:ORANGE>Express Elevator</c>\n<CN:RED>Unauthorized operation prohibited</c></CENTER>\n\nThere is also a big <CN:BRIGHTRED>red</C> button here that doesn't do anything.")
    return 1

def DoSummonerBook(S,M,X,Y):
    if Global.Party.EventFlags.get("L7SummoningBook"):
        MazeRooms.DoSign(S,M,X,Y,"The <CN:PURPLE>Book of Summoning</C> rests here on a pedestal.")
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    LearnString = ""
    for Index in range(6):
        LearnString += Global.Party.LearnSpell("Summoner", Index)
    Str = "You spy a giant book, resting on a pedestal here.  Gothic script on the cover reads: <CN:PURPLE>Marduk's Rainy-Day Fun Book of Invocations</C>.\n\nYou read it...\n\n<CN:YELLOW>[ Your Summoners now know the basic summoning spells! ]\n%s"%LearnString
    Global.Party.EventFlags["L7SummoningBook"] = 1
    Global.App.ShowNewDialog(Str)

def TakeElevator(S):
  Resources.PlayStandardSound("MegamanNoise.wav")
  Maze.GoToMazeLevel(3)
  Global.Party.X = 24
  Global.Party.Y = 26
  S.RenderMaze(1)
  
ClippySign = """A sign on the door reads:

<CENTER><CN:BRIGHTRED>It looks like you want to DIE.
WOULD YOU LIKE ASSISTANCE?
BWA HA HA HA HA HA HA!!!</C></CENTER>
"""
EnterRoomRoutines = {400:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,ClippySign),
                     401:DoClippy,
                     402:DoPython,
                     403:DoSpaceshipCockpit,
                     404:DoBeehive,
                     405:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"There's a wonderful smell wafting down this hallway.  You feel as through it's pulling you onward, like a magnet."),
                     406:DoPie,
                     407:DoBakery,
                     408:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"You stand at the walls of a great <CN:YELLOW>castle</c>, which looms high above you."),
                     409:DoCastle,
                     410:DoBoatMan,
                     411:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"The pungent stench of mildew assails your nostrils.\nThere must be some sort of terrible mold in here..."),
                     412:DoMoldMonster,
                     413:DoClock,
                     414:DoRibbonGet,
                     415:DoToad,
                     416:DoRabbitA,
                     417:DoRabbitB,
                     418:DoRabbitArmy,
                     419:DoDoNotDisturb,
                     420:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"You stand outside the hull of a crashed starship."),
                     421:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"The floor here is <CN:PURPLE>covered in slime</c>."),
                     422:DoElevator,
                     423:lambda Screen,Maze,X,Y,I ={},S={"Mage:9":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     424:lambda Screen,Maze,X,Y,I ={},S={"Mage:10":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     425:lambda Screen,Maze,X,Y,I ={},S={"Cleric:9":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     426:lambda Screen,Maze,X,Y,I ={},S={"Cleric:10":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     427:lambda Screen,Maze,X,Y,I ={},S={"Summoner:8":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     428:DoSummonerBook,
                     429:lambda S,M,X,Y,I ={"Glider Gun":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     430:lambda S,M,X,Y,I ={"Medusa Scale":2},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     431:lambda S,M,X,Y,I ={"Escapipe":2},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                    }