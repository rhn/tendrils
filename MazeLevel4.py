"""
Special maze locations for level 4.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import Maze
import MazeRooms

def EnterMazeLevel():
    "Event handler: Entering this maze level"
    M = Global.Maze
    #print "EnterMazeLevel 4....do we unlock the door?"
    if Global.Party.EventFlags.get("L4DoorUnlock") or Global.Party.KilledBosses.get((4, "L4Boss")):
        #print "YES!"
        M.Walls[0][(17,8)] = 2
    else:
        #print "No!"
        pass


def L4DoFireKnight(Screen, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    WoundStr = ""
    for Player in Global.Party.Players:
        Fraction = random.randrange(10, 49) / float(100)
        if Player.IsAlive():
            Wound = Fraction * Player.MaxHP
            Player.HP -= Wound
            WoundStr += "%s takes %d damage!\n"%(Player.Name, Wound)
            if Player.HP < 0:
                Player.Die()
                WoundStr += "<CN:BRIGHTRED>%s is DEAD!!</C>\n"%Player.Name
    Screen.Redraw()
    Global.Party.X = 17
    Global.Party.Y = 14
    Global.Party.Heading = 1
    Str = """<CN:BRIGHTRED>As you step forward, a knight gallops forward, cutting the air with a great red blade.  His \
armor is the color of ash, and his steed has a mane of flame.  You beat a hasty retreat, as though the fires of hell \
itself were hot on your heels!\n\nYou have sustained some wounds...\n"""+WoundStr
    Global.App.ShowNewDialog(Str, Callback=Maze.CheckForAllDead)
    return 0 # do NOT move into the knight's room        

def L4DoLava(Screen, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
##    if Global.Party.KeyItemFlags.get("Lava Juice", None):
##        return 1
    WoundStr = ""
    WoundCount = 0
    for Player in Global.Party.Players:
        if Player.HasPerk("Mark of Fire"):
            WoundStr += "%s is protected by Mark of Fire\n"%Player.Name
            continue
        if Player.IsAlive():
            Fraction = random.randrange(10, 49) / float(100)
            Wound = Fraction * Player.MaxHP
            Player.HP -= Wound
            WoundStr += "%s takes %d damage!\n"%(Player.Name, Wound)
            if Player.HP < 0:
                Player.Die()
                WoundStr += "<CN:BRIGHTRED>%s is DEAD!!</C>\n"
            WoundCount += 1
    Screen.Redraw()
    if WoundCount:
        Str = """<CN:BRIGHTRED>LAVA!\n\n"""+WoundStr
        Global.App.ShowNewDialog(Str, Callback = Maze.CheckForAllDead)
    else:
        Screen.SignText = "<CN:RED><CENTER>Lava!\nThe Mark of Fire protects you"
    return 1    

KeysToParts = {"Purple Key": ("Blue Key", "Red Key"),
          "Orange Key": ("Red Key", "Yellow Key"),
          "Green Key": ("Blue Key", "Yellow Key"),
          "White Key": ("Blue Key", "Red Key", "Yellow Key"),
          }
PartsToKeys = {("Blue Key", "Red Key"):"Purple Key",
               ("Blue Key", "Yellow Key"): "Green Key",
               ("Red Key", "Yellow Key"): "Orange Key",
               ("Blue Key", "Red Key", "Yellow Key"):"White Key",
               ("Purple Key", "Yellow Key"):"White Key",
               ("Green Key", "Red Key"):"White Key",
               ("Blue Key", "Orange Key"):"White Key",
               }
AllKeys = ["Blue Key", "Red Key", "Yellow Key", "Purple Key", "Green Key", "Orange Key", "White Key"]

SimpleKeys = ["Blue Key", "Red Key", "Yellow Key"]
CompositeKeys = ["Purple Key", "Green Key", "Orange Key", "White Key"]

def L4DoKey(Screen, Maze, X, Y, KeyName):    
    """
    The key puzzle from level 4: Keys can be combined and split.  The red and blue keys
    combine into a purple key, for instance.  This function is called when the
    user enters a key room.  They find the key iff they've never found it before.
    """
    if L4PartyHasKey(KeyName):
        return 1
    return MazeRooms.DoChest(Screen, Maze, X, Y, {}, {KeyName:1})    
    
def L4DoForge(Screen, Maze, X, Y):
    Global.Party.X = X+3
    Global.Party.Y = Y+3
    Screen.RenderMaze()
    Screen.Redraw()
    SawForge = Global.Party.EventFlags.get("L4SawForge", None)
    if not SawForge:
        Global.Party.EventFlags["L4SawForge"] = 1
        Str = """Uncomfortably hot air blows from a wicked-looking machine that fills most of this room.  A sign \
dangling from the ceiling reads "THE HELLFORGE" in fierce gothic letters.  It doesn't look like any forge you've \
ever seen before.  There is a hopper on the left, and a hopper on the right; pipes lead from the hoppers into a tangle \
mess of iron and steel.\n\nIt's too dark to see what the pipes lead to, but it's clearly very hot in there..."""
        Global.App.ShowNewDialog(Str, Callback = L4UseForge)
        return 1
    else:
        L4UseForge()
        return 1
def L4DoSniperRifle(Screen, Maze, X, Y):
    if Global.Party.KeyItemFlags.get("Sniper Rifle", None):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    Screen.Redraw()
    Str = """<CN:BRIGHTGREEN>SNIPER RIFLE ACQUIRED!</C>\n\nYou found a sniper rifle, complete \
with instruction manual:<CN:GREEN>\n\nCongratulations on your purchase of the 27B/6 sniper \
rifle.  We hope it will give you many years of trouble-free maiming.  To use it, use the \
mouse to quickly center the crosshairs on the target monster, then click to shoot.\n\nBecause \
ninjas are so adept \
at sneaking around, you can snipe more often if you have a ninja in your party."""
    Global.Party.KeyItemFlags["Sniper Rifle"] = 1
    Global.App.ShowNewDialog(Str)
    return 1
    
def L4PartyHasKey(KeyName):
    #HasKey = Global.Party.KeyItemFlags.get(KeyName, 0)
    for Key in L4PartyGetKeys():
        if Key==KeyName:
            return 1
        if KeyName in KeysToParts.get(Key, []):
            return 1
    

def L4PartyGetKeys():
    Keys = []
    for Key in AllKeys:
        if Global.Party.KeyItemFlags.get(Key,0):
            Keys.append(Key)
    return Keys

def L4UseForge():
    Keys = L4PartyGetKeys()
    SimpleCount = 0
    CompositeCount = 0
    for Key in Keys:
        if Key in SimpleKeys:
            SimpleCount += 1
        else:
            CompositeCount += 1
    if len(Keys)==0:
        Str = """You don't seem to have anything to feed into the Hellforge..."""
        Global.App.ShowNewDialog(Str)
        return
    if (SimpleCount+CompositeCount>1 and CompositeCount):
        Str = """Put keys into the right or left hopper?"""
        Global.App.ShowNewDialog(Str, CustomButtons = ("Left", "Right"), Callback = L4UseForgeSimpleComplex)
        return
    if CompositeCount:
        L4UseForgeComplex()
    else:
        L4UseForgeSimple()
        
def L4UseForgeSimpleComplex(Command):
    if Command == "Left":
        L4UseForgeSimple()
    if Command == "Right":
        L4UseForgeComplex()

def L4UseForgeSimple():
    Keys = L4PartyGetKeys()
    PartySimpleKeys = []
    for Key in Keys:
        PartySimpleKeys.append(Key)
    if len(PartySimpleKeys)<2:
        Str = """The hopper has slots for two items.  Perhaps if you had a second key..."""
        Global.App.ShowNewDialog(Str)
        return
    Str = """Click two items to feed into the left hopper."""
    PartySimpleKeys.append("Cancel")
    Global.App.ShowMultiDialog(Str, PartySimpleKeys, 2, L4FusedSimpleKeys)

def L4FusedSimpleKeys(StringList):
    if len(StringList)<2:
        return
    StringList.sort()
    NewKey = PartsToKeys.get(tuple(StringList), None)
    if not NewKey:
        print "** ERROR in key forge:", StringList
        return
    for Key in StringList:
        Global.Party.KeyItemFlags[Key] = 0
    Global.Party.KeyItemFlags[NewKey] = 1
    Str = """The forge gulps down both keys, and emits a horrible belching noise.  After a few ominous moments \
filled with grinding noises, the forge spits a <CN:BRIGHTGREEN>%s</C> into the right hopper, along with copious \
quantities of acrid, inky smoke.  You take the key, which still smells faintly of brimstone."""%NewKey
    Global.App.ShowNewDialog(Str)

def L4UseForgeComplex():
    Keys = L4PartyGetKeys()
    PartyCompositeKeys = []
    for Key in Keys:
        if Key in CompositeKeys:
            PartyCompositeKeys.append(Key)
    Str = """Click a key to feed into the right hopper."""
    Options = PartyCompositeKeys
    Options.append("Cancel")
    Global.App.ShowNewDialog(Str, CustomButtons = Options, Callback = L4MeltedCompositeKey)

def AddN(Str):
    if Str[0].lower() in ("a","e","i","o","u"):
        return "n"
    return ""

def L4MeltedCompositeKey(Str):
    if Str not in AllKeys:
        return
    Parts = KeysToParts.get(Str, None)
    if not Parts:
        print "** ERROR in key unforge:", Str
    Global.Party.KeyItemFlags[Str] = 0
    for Key in Parts:
        Global.Party.KeyItemFlags[Key] = 1
    if len(Parts)==2:
        KeyStr = "a%s %s and a%s %s"%(AddN(Parts[0]), Parts[0], AddN(Parts[1]),Parts[1])
    else:
        KeyStr = "a%s %s, a%s %s and a%s %s"%(AddN(Parts[0]),Parts[0], AddN(Parts[1]),Parts[1], AddN(Parts[2]),Parts[2])
    Str = """The key slides into the forge.  After an ominous silence, the machine emits a high-pitched whine and\
floods the room with steam.\n\nWhen the mist clears, you notice that the left hopper contains %s.  You take them."""%KeyStr
    Global.App.ShowNewDialog(Str)

def DoMarkOfFire(S,M,X,Y):
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    #S.Redraw()
    Str = "<CN:RED>The wall glows red here.\n\nWho will touch?"
    Global.App.ShowNewDialog(Str, ButtonGroup.PickPlayer,Callback=MarkTouch)

def MarkTouch(Player):
    Str = "<CN:BRIGHTRED>Ouch!</C>\n\nIt left a mark!"
    Player.HP -= 20
    if Player.HP <= 0:
        Player.Die()
        Str += "\n<CN:BRIGHTRED>%s has perished!"%Player.Name
    Player.Perks["Mark of Fire"] = 1
    Global.App.ShowNewDialog(Str, Callback = Maze.CheckForAllDead)
    return 1
        
def DoGypsy(S,M,X,Y):
    if Global.Party.EventFlags.get("L4Gypsy"):
        return 1
    Global.App.DoNPC("Gypsy")
    return 0

def DoL4ShopAccessories(Screen, Maze, X, Y):
    Inventory = {"Potion":None, "Hi-Potion":None, "Antidote":None, "Black Coffee":None,}
    Global.App.GoShopping(Inventory, "Ye Potion Shoppe")
    return 0 # Don't stay inside

def DoL4ShopWeapons(Screen, Maze, X, Y):
    Inventory = {"Neko Hat":None, "Butterfly Knife":None, "Lordly Robe":None, "Feather Boots":None,
                 "Valheru Armor":None, "Choco Shield":None}
    Global.App.GoShopping(Inventory, "Survival Gear")
    return 0 # Don't stay inside

def DoL4Boss(S,M,X,Y):
    if Global.Party.KilledBosses.get((4, "L4Boss")):
        return 1
    Monsters = [[Global.Bestiary.GetCritter("StoneHead")]] #%%%
    Booty = ({}, {}, 0)
    # Note: This is the summoner's quest; the party CAN flee, since otherwise they're dead if they show
    # up without a summoner!
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "L4Boss", SongFileName="Gamelan.xm", CanFlee = 1)
    return 0

def DoKingRastan(S,M,X,Y):
    Global.App.DoNPC("KingRastan")
    return 0

EnterRoomRoutines = {#250: Knight, but these rooms aren't enterable
                     251: L4DoFireKnight,
                     252: L4DoLava,
                     253: lambda Screen,Maze,X,Y: L4DoKey(Screen, Maze, X, Y, "Red Key"),
                     254: L4DoForge,
                     255: L4DoSniperRifle,
                     256: lambda Screen,Maze,X,Y: L4DoKey(Screen, Maze, X, Y, "Blue Key"),
                     260:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "Watch your step - lava!"),
                     261:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "The Maze of Knights"),
                     ##262:lambda Screen,Maze,X,Y,I ={"Death Sickle":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S), 
                     263:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "There is a <CN:BRIGHTBLUE>blue</C> door here."),
                     264:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "There is an <CN:ORANGE>orange</C> door here."),
                     265:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "There is a <CN:PURPLE>purple</C> door here."),
                     266:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "There is a <CN:BRIGHTGREEN>green</C> door here."),
                     267:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "There is a <CN:BRIGHTRED>red</C> door here."),
                     268:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CN:LIGHTGREY>There is a </C>white<CN:LIGHTGREY> door here."),
                     269:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "There is an <CN:ORANGE>orange</C> door here."),
                     270:lambda Screen,Maze,X,Y: L4DoKey(Screen, Maze, X, Y, "Yellow Key"),
                     271:lambda Screen,Maze,X,Y,I ={},S={"Knight Map":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S), 
                     272:DoMarkOfFire,
                     273:lambda Screen,Maze,X,Y,I ={"Blaze Robe":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     274:lambda Screen,Maze,X,Y,I ={"Power Glove":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     275:lambda Screen,Maze,X,Y,I ={"Ruby Earring":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     276:lambda Screen,Maze,X,Y,I ={"Fairy Shoes":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     277:lambda Screen,Maze,X,Y,I ={},S={"CHA seed":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     278:lambda Screen,Maze,X,Y,I ={},S={"INT seed":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     279:lambda Screen,Maze,X,Y,I ={},S={"Mage:4":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     280:lambda Screen,Maze,X,Y,I ={},S={"Mage:5":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     281:DoGypsy,
                     282:DoL4ShopWeapons,
                     283:DoL4ShopAccessories,
                     284:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:ORANGE>Fortune Teller"),
                     285:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER>Ye Potion Shoppe"),
                     286:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER>Survival Gear"),
                     287:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER>Dragon's Tail Inn"),
                     288:DoL4Boss,
                     289:lambda Screen,Maze,X,Y,I ={},S={"Summoner:3":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     290:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER>Ye King of Towne"),
                     291:DoKingRastan,
                     292:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"""Runes are carved into the wall here.  They read:
<CENTER><CN:ORANGE>Golem, golem, golem!
I made you out of clay.
And when you're dry and ready,
My rivals I shall slay!</C></CENTER>"""),
                     293:lambda Screen,Maze,X,Y,I ={"Hi-Potion":7, "Phoenix Down":3},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     294:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CN:RED>Fire Exit</c>"),
                     295:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CN:RED>Warning: One-way door</c>"),
                     296:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CN:Blue>Welcome to Midgard</c>\n<CN:RED>No Beastly Fidos Allowed"),
                    }