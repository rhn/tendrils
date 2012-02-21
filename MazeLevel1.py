"""
Special maze locations for level 1.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms
import Maze

def EnterMazeLevel():
    "Event handler: Entering this maze level"
    M = Global.Maze
    #print "EnterMazeLevel 1....do we unlock the door?"
    if Global.Party.EventFlags.get("L1DoorUnlock"):
        #print "YES!"
        M.Walls[1][(19,5)] = 2
    else:
        #print "No!"
        pass


def L1DoSignSouth(Screen, Maze, X, Y):
    Screen.SignText = "A sign here reads:\nSouth main street - West to Adventurer's Inn and Bard's Guild.  East to Armory."
    return 1

def L1DoSignMiddle(Screen, Maze, X, Y):
    Screen.SignText = "A sign here reads:\nSkara Brae Town Center - West to Supply Hut, East to AAA's House"
    return 1

def L1DoSignNorth(Screen, Maze, X, Y):
    Screen.SignText = "A sign here reads:\nNorth main street - West to Shrine, East to Trainer"
    return 1

def L1DoSignTownExit(Screen, Maze, X, Y):
    Screen.SignText = "A sign here reads:\n<CENTER>** WARNING **\nWandering beasts beyond this door!\nPlease do not feed the monsters!"
    return 1

def L1DoSignSecretDoors(Screen, Maze, X, Y):
    Screen.SignText = "Scrawled on the wall in an unsteady hand are the words:\n\nThere are secret doors in this dungeon.  You can open them just like a normal door.  Now, if only there was a way to tell where they are!"
    return 1

def L1ShopArmory(Screen, Maze, X, Y):
    #Inventory = {"Cape":1, "Tunic":1, "Whip":1, "Glove":1, "Wooden Boomerang":1}
    Inventory = {"Bamboo Stick":None, "Short Sword":None, "Cuirass":None, "Leather Armor":None,
                 "Tunic":None, "Glove":None, "Bronze Shield":None, }
    Global.App.GoShopping(Inventory, "Charsi's Forge", "Shop2")
    return 0 # Don't stay inside

def L1ShopSupplies(Screen, Maze, X, Y):
    Inventory = {"Potion":None, "Antidote":None}
    Global.App.GoShopping(Inventory, "Asidonhopo's Curiosity Shoppe")
    return 0 # Don't stay inside

def L1DoDragons(Screen, Maze, X, Y):
    # Dun-dun-dun!  It's the first boss battle!
    Booty = ({"Ancient Sword":1}, {"Gold":500}, 2)
    # If the dragons are dead, it's just a chest, or an ordinary room:
    if Global.Party.KilledBosses.get((1, "Dragons")):
        if Global.Party.LootedChests.get((X, Y, Maze.Level)):
            return 1 # empty room!
        Global.App.AskDisarmChest(Booty[0], Booty[1], Booty[2])
        return 1
    #%%% Request a boss battle-song here
    Monsters = [[Global.Bestiary.GetCritter("2600DragonA"),Global.Bestiary.GetCritter("2600DragonB")]]
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "Dragons", SongFileName="FFVI - Grand Finale.mp3", CanFlee = 0)
    return 1

def L1DoKeySearch():
    GotKeyStr = """You nervously stick your arm into the stone feline.  You feel an item inside!  You \
quickly pull it out.

<CN:GREEN>You found a Copper Key!</CN>"""
    Global.Party.KeyItemFlags["Copper Key"] = 1
    Global.App.ShowNewDialog(GotKeyStr, ButtonGroup.Ok)
    
def L1DoKeyRoom(Screen, Maze, X, Y):
    # If they're carrying the key, return:
    if Global.Party.KeyItemFlags.get("Copper Key", None):
        return 1
    # If they've used the key already, return:
    if Global.Party.EventFlags.get("L1DoorUnlock"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y    
    Screen.RenderMaze()
    Screen.Redraw()
    # Ask them if they want to search:
    StatueStr = """A granite statue of a <CN:RED>lion</C> stands in the center of this room, one paw resting upon a giant \
bell.  In the flickering half-light, its tail seems to twitch back and forth.  A placard at the statue's base \
reads "COURAGE".

The statue's mouth is open in a roar, and it appears to be hollow.

<CN:BRIGHTGREEN>Reach your arm into the lion's mouth?</C>"""
    Global.App.ShowNewDialog(StatueStr, ButtonGroup.YesNo, Callback = L1DoKeySearch)
    return 1

def L1DoKittyGirl(Screen, Maze, X, Y):
    Global.App.DoNPC("KittyGirl")
    return 0

def L1DoTrainer(Screen, Maze, X, Y):
    Global.App.DoNPC("L1AdviceGuy")
    return 0

def L1MisterAAA(Screen, Maze, X, Y):
    Global.App.DoNPC("AAA")
    return 0

def L1DoLostKitty(Screen, Maze, X, Y):
    if Global.Party.EventFlags.get("L1SavedKitty"):
        return 1
    if Global.Party.KeyItemFlags.get("A Kitty"):
        return 1    
    Global.Party.X = X
    Global.Party.Y = Y    
    Screen.RenderMaze()
    Screen.Redraw()
    Global.App.ShowNewDialog("At the end of this passage, you find a forlorn-looking little kitten, \
    shivering in the corner.  The poor little fuzzball gazes up at you and mews plaintively.  It seems eager \
    to follow you home.")
    Global.Party.KeyItemFlags["A Kitty"] = 1
    return 1

def L1DoRapidTransitRoom(Screen, Maze, X, Y):
    Str = "A circle of mushrooms sprouts from the ground here.  A moldy wooden sign reading \
<CN:GREEN>tO thE tOwN</C> points into the ring's center.\n\nStep into the fairy ring?"
    Global.Party.X = X
    Global.Party.Y = Y    
    Screen.RenderMaze()
    Screen.Redraw()    
    Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = L1WarpToTown)

def L1WarpToTown():
    Global.Party.X = 5
    Global.Party.Y = 0
    Global.Party.Heading = Directions.Up
    Resources.PlayStandardSound("MegamanNoise.wav")

def L1WarpToCathedral(S, M, X, Y):
    Global.Party.X = 4
    Global.Party.Y = 15
    #Global.Party.Z = 3
    Maze.GoToMazeLevel(3)
    Global.Party.Heading = Directions.Left
    #Global.Maze.Level = 3    
    #Global.Maze.Load()
    S.RenderMaze(1)
    S.Redraw()
    Resources.PlayStandardSound("MegamanNoise.wav")



EnterRoomRoutines = {101:L1DoKittyGirl,
                     103:MazeRooms.DoInn, 
                     104:L1ShopArmory,
                     105:L1ShopSupplies,
                     106:L1MisterAAA,
                     108:L1DoTrainer,
                     109:L1DoSignTownExit,
                     110:L1DoSignSecretDoors,
                     111:lambda Screen,Maze,X,Y,I ={"Ribbon":1},S={"gold":50}: MazeRooms.DoChest(Screen, Maze, X, Y, I,S),
                     112:lambda Screen,Maze,X,Y,I = {"Axe":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I),
                     113:lambda Screen,Maze,X,Y,I ={"Boomerang":1},S={"gold":100}: MazeRooms.DoChest(Screen, Maze, X, Y, I,S),
                     114:L1DoKeyRoom,
                     115:L1DoRapidTransitRoom,
                     116:L1DoDragons,
                     118:L1DoSignSouth,
                     119:L1DoSignMiddle,
                     120:L1DoSignNorth,
                     121:lambda Screen,Maze,X,Y,I = {"Phoenix Down":2}: MazeRooms.DoChest(Screen, Maze, X, Y, I),
                     122:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """Peering at the wall, you notice that someone has carved some words into the living rock:\n\n"Here there be dragons!  Beware, lest ye aaaaaagggh"\n\nHmm...he must have died while carving it."""),
                     123:L1DoLostKitty,
                     124:L1WarpToCathedral,
                     125:lambda Screen,Maze,X,Y,I ={},S={"Red Puzzle Box":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I,S),
                     126:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>Adventurer's Inn"),
                     127:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>Armory"),
                     128:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>Supplies"),
                     129:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>House of AAA"),
                     130:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>Shrine of Kibo"),
                     131:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>Training House"),
                     132:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "<CENTER><CN:GREEN>Bard's Guild"),
                     133:lambda S,M,X,Y, Intro=1:MazeRooms.DoBardsGuild(S,M,X,Y,Intro),
                     }                     
