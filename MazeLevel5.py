"""
Special maze locations for level 5.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms
import MazeScreen
import Maze

TreasureDirections = """I have hidden my treasure somewhere in this level.  I know that
you are wondering where it is.  In fact, this note holds the key!  If you start
here and follow my instructions to the letter, you will come to the right spot.
Dig there, and the goods are yours.
"""
#EENESESEWEENSEENW
#EWNENWEESNSNESEES
#EENWNSNSEEEWEES
#EENESES

def EnterMazeLevel():
    "Event handler: Entering this maze level"
    if Global.Party.EventFlags.get("L5Sokoban", 0):
        SolveSokoban(Global.Maze)

def DoTreasureMap(S, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    Str = """A gravestone is here.  On it are carved the words:

<CENTER><CN:RED>Captain Blood
Scourge o' the Seas</C></CENTER>

Beneath it, in fine print, are carved these words:

<CN:BLUE>I have hidden my treasure somewhere in this level.  I know that \
you are wondering where it is.  In fact, this note holds the key!  If you start \
here and follow my instructions to the letter, you will come to the right spot. \
Dig there, and the goods are yours.</C>"""
    Global.App.ShowNewDialog(Str, Callback = TreasureMapOk)
    return 1

def TreasureMapOk(Dummy = None):
    if Global.Party.KeyItemFlags.get("Shovel", 0) or Global.Party.EventFlags.get("L5BuriedTreasure",0):
        return
    Global.App.ShowNewDialog("There is a sturdy <CN:GREEN>shovel</C> next to the grave.  You take it with you.\n\nMaybe you'll be able to dig up the pirate's treasure...")
    Global.Party.KeyItemFlags["Shovel"] = 1

class Soko:
    Box = 308
    Floor = 307
    BoxOnFloor = 306

def SolveSokoban(M):
    for X in range(Maze.MazeWidth):
        for Y in range(Maze.MazeHeight):
            if M.Rooms[(X,Y)] in (Soko.Box, Soko.Floor, Soko.BoxOnFloor):
                M.Rooms[(X,Y)] = 0
    M.Rooms[(19,24)] = 5

def CheckSokoSolve(M):
    for X in range(Maze.MazeWidth):
        for Y in range(Maze.MazeHeight):
            if M.Rooms[(X,Y)] in (Soko.Box, Soko.Floor):
                return
    Global.App.ShowNewDialog("There is a thunderous <CN:BRIGHTBLUE>CRACK!</C> as the weakened floor collapses.  Dust rises \
as each boulder rolls down into the unknown.  When the dust clears, a passage down is visible in a corner.\n\nWith \
a faint <CN:GREY>pop</C>, the magic map vanishes.  Guess you don't need that any more.")
    Global.Party.EventFlags["L5Sokoban"]=1
    try:
        del Global.Party.KeyItemFlags["Magic Map"]
    except:
        pass
    SolveSokoban(M)

def DoSokobanStart(S, M, X, Y):
    # If the puzzle is solved already, clear out the rocks and floors and make the
    # down staircase:
    if Global.Party.EventFlags.get("L5Sokoban", 0):
        SolveSokoban(Global.Maze)
        return 1
    if Global.Party.KeyItemFlags.get("Magic Map",0):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    Global.Party.KeyItemFlags["Magic Map"] = 1
    Str = "On the ground, you find a piece of parchment, glowing with a faint <CN:BLUE>blue</C> light.  It appears to be some sort of map...\n\nYou take it with you."
    Global.App.ShowNewDialog(Str)
    return 1

def DoSokoPush(S, M, X, Y, Floor):
    # Check the wall:
    Heading = Global.Party.Heading
    Wall = Global.Maze.GetWall(X, Y, Heading)
    if Wall:
        #%%% Oof sound
        Global.App.ShowNewDialog("<CN:RED>Ouch!</C>\n\nThe rock won't budge.")
        return 0
    NextX = MazeScreen.GetMovedX(X, Heading)
    NextY = MazeScreen.GetMovedY(Y, Heading)
    Contents = Global.Maze.Rooms[(NextX,NextY)]
    if Contents not in (0, Soko.Floor):
        #%%% Oof sound
        Global.App.ShowNewDialog("<CN:RED>Ouch!</C>\n\nThe rock won't budge.")
        return 0
    #%%% Push sound
    if Contents == 0:
        Global.Maze.Rooms[(NextX, NextY)] = Soko.Box
    else:
        Global.Maze.Rooms[(NextX, NextY)] = Soko.BoxOnFloor
    NearContents = Global.Maze.Rooms[(X,Y)]
    if NearContents == Soko.Box:
        Global.Maze.Rooms[(X,Y)] = 0
    else:
        Global.Maze.Rooms[(X,Y)] = Soko.Floor
        MazeRooms.DoSign(S, M, X, Y, \
            "The floor is cracked here, and looks as though it could be broken through.")
        
    CheckSokoSolve(Global.Maze)
    return 1    

def DoBigButton(S,M,X,Y):
    if Global.Party.KeyItemFlags.get("L5Sokoban"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    Global.App.ShowNewDialog("A big <CN:RED>red</c> button.\n\nPush it?", ButtonGroup.YesNo, Callback=ButtonPush)
    return 1

def ButtonPush(Dummy = None):
    Global.App.ShowNewDialog("Who wouldn't?\n\n\nThere is a rumbling sound, and the ground vibrates for a few moments.")
    # Reset the puzzle:
    for X in range(Maze.MazeWidth):
        for Y in range(Maze.MazeHeight):
            if Global.Maze.Rooms[(X,Y)] == Soko.Box:
                Global.Maze.Rooms[(X,Y)] = 0
            elif Global.Maze.Rooms[(X,Y)] == Soko.BoxOnFloor:
                Global.Maze.Rooms[(X,Y)] = Soko.Floor
    Coords = [(7,23),(7,26),(7,28),(9,27),(9,26),(4,23)]
    for (X,Y) in Coords:
        Global.Maze.Rooms[(X,Y)] = Soko.Box
    

def DoWolfyOutside(S,M,X,Y):
    #Global.Party.EventFlags["L5WolfySquare"] = None # reset the puzzle
    Global.Party.EventFlags["L5WolfyTime"] = None # reset the puzzle
    return 1


def DoWolfyPuzzleComplete(S,M,X,Y):
    Global.Party.EventFlags["L5WolfySolved"] = 1
    return 1

def DoWolfyBarredDoor(S,M,X,Y):
    Solved = 1
    for X in range(30):
        for Y in range(30):
            if Global.Maze.Rooms[(X,Y)] == 310:
                print "Not touched:", X, Y
                Solved = 0
    if Solved:
        S.SignText = "<CN:RED>PRESSURE-SENSITIVE GRID ACTIVATED\n\n<CN:GREY>Please do not slam door"
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.SignText = ""
    S.RenderMaze()
    S.Redraw()
    Str = "A sign above the door blinks:\n<CN:RED>PRESSURE-SENSITIVE GRID NOT ACTIVATED\n\n<CN:GREY>You \
must step on each square\n\n<CN:WHITE>Looks like you're cornered..."
    Global.App.ShowNewDialog(Str, Callback = lambda S=S:DoWolfyCatch(S))
    return 0

def DoWolfyFirstRoom(S,M,X,Y):
    #Square = Global.Party.EventFlags.get("L5WolfySquare", None)
    Time = Global.Party.EventFlags.get("L5WolfyTime", None)
    Solved = Global.Party.EventFlags.get("L5WolfySolved", None)
    if Solved:
        return 1
    if not Time:
        Global.Party.X = X
        Global.Party.Y = Y
        S.RenderMaze()
        S.Redraw()
        Global.Party.EventFlags["L5WolfyTime"] = 30
        #Global.Party.EventFlags["L5WolfySquare"] = (X-1,Y)
        Global.App.ShowNewDialog("With a mighty <CN:BRIGHTRED>WOOF!</c> the guard dog wakes from his doze and begins to follow you.  There's no turning back now!")
        return 1
    return DoWolfyFollow(S,M,X,Y)

def DoWolfyFollow(S,M,X,Y):
    S.SignText = ""
    #Square = Global.Party.EventFlags.get("L5WolfySquare", None)
    Solved = Global.Party.EventFlags.get("L5WolfySolved", None)
    Time = Global.Party.EventFlags.get("L5WolfyTime", 0)
    if Solved:
        return 1
    #if Square == (X,Y) or Time<=0:
    if Time <= 0:
        print "CAUGHT!!!"
        DoWolfyCatch(S)
        return 0
    Time -= 1
    #print Time, Square, X, Y
    Global.Party.EventFlags["L5WolfyTime"] = Time
    #Global.Party.EventFlags["L5WolfySquare"] = (Global.Party.X,Global.Party.Y)
    S.SignText = "You hear the panting of the great hound behind you..."
    print "YOU HEAR THE PANTING!!!"
    # Clear this square:
    Contents = Global.Maze.Rooms[(X,Y)]
    if Contents == 310:
        Global.Maze.Rooms[(X,Y)] = 323
    return 1
    
def DoWolfy(S,M,X,Y):
    #Square = Global.Party.EventFlags.get("L5WolfySquare", None)
    Solved = Global.Party.EventFlags.get("L5WolfySolved", None)
    Time = Global.Party.EventFlags.get("L5WolfyTime", None)
    if Solved:
        S.SignText = "'Wolfy' the guard dog is lounging in the corner.  He wags his tail as you pass."
        return 1
    if Time!=None:
        return DoWolfyFollow(S,M,X,Y)
    S.SignText = "A <CN:BRIGHTRED>HUGE</C> dog, with a mouth large enough to gulp a horse and its rider, rests in the \
corner.  A small sign tacked to the wall nearby reads: <CN:BRIGHTBLUE>PLEASE DO NOT FEED WOLFY"
    return 1

def DoWolfyCatch(S):
    for X in range(30):
        for Y in range(30):
            if Global.Maze.Rooms[(X,Y)] == 323:
                Global.Maze.Rooms[(X,Y)] = 310
    Global.Party.X = 22
    Global.Party.Y = 22
    S.SignText = ""
    print S, S.SignText
    traceback.print_stack()
    S.RenderMaze()
    S.Redraw()
    Global.Party.EventFlags["L5WolfySquare"] = None # reset the puzzle
    Global.Party.EventFlags["L5WolfyTime"] = None # reset the puzzle
    Str = "The great dog has caught you!\n\nHe snaps you up in his massive jaws, carries you outside, and spits you out \
with a sickening <CN:BLUE>SPLUDGE</c>.  You are bruised, covered in dog slobber, but otherwise unhurt."
    Global.App.ShowNewDialog(Str)

def L5DoPriest(S,M,X,Y):
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    if Global.Party.EventFlags.get("L5ClericRemedial"):
        Str = "The head priest explains that he has been very busy lately.  His right-hand man, apparently \
tired of the monastic lifestyle, left to become a paladin of a fertility cult.\n\nYou leave him to his work."
    else:
        Global.Party.EventFlags["L5ClericRemedial"] = 1
        LearnStr = ""
        for Index in range(5):
            LearnStr += Global.Party.LearnSpell("Cleric", Index)
        if not LearnStr:
            LearnStr = "<CN:YELLOW>[ However, your well-prepared clerics learn nothing new ]"
        Str = "The head priest invites you to stay and chat, and he explains his beliefs.  It's a complicated \
system involving reincarnation, where people can earn \"extra lives\", and the faithful can become part of \
a grand \"high score table\".  Along the way, he reviews the casting of some <CN:BRIGHTBLUE>cleric</C> spells. \
\n\n%s"%LearnStr
    Global.App.ShowNewDialog(Str)
    
EnterRoomRoutines = {
                     301:lambda S,M,X,Y: MazeRooms.DoSign(S, M, X, Y, \
                        "<CENTER><CN:BRIGHTRED>Minotaur's Maze\n<CN:RED>Next Save Point:\n2 miles"),
                     302:DoTreasureMap,
                     #303: Do nothing, but that's where you should dig
                     304:lambda S,M,X,Y: MazeRooms.DoSign(S, M, X, Y, \
                        "<CENTER><CN:BRIGHTGREN>EXIT"),
                     305:lambda S,M,X,Y: MazeRooms.DoSign(S, M, X, Y, \
                        "<CENTER><CN:YELLOW>Save Shrine\n<CN:blue>(Open 24 hours)"),
                     # 308 is a rock.  307 is a weak floor.  306 is a rock ON a weak floor.
                     306:lambda S,M,X,Y,Floor=1:DoSokoPush(S,M,X,Y,Floor),
                     307:lambda S,M,X,Y: MazeRooms.DoSign(S, M, X, Y, \
                        "The floor is cracked here, and looks as though it could be broken through."),
                     308:lambda S,M,X,Y,Floor=0:DoSokoPush(S,M,X,Y,Floor),
                     309:DoWolfy,
                     310:DoWolfyFollow,
                     311:DoWolfyBarredDoor,
                     314:DoWolfyFirstRoom, 
                     312:lambda Screen,Maze,X,Y,I ={},S={"Cleric:7":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     313:lambda S,M,X,Y,I ={"Hyper Armor":1, "Master Sword":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     315:lambda S,M,X,Y,I ={"Magic Shield":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     316:lambda S,M,X,Y,I ={"Tiara":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     317:lambda S,M,X,Y,I ={"Ninja Tabi":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     318:lambda S,M,X,Y,I ={"Ring of Prandur":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     319:DoSokobanStart,
                     320:DoBigButton,
                     321:DoWolfyPuzzleComplete,
                     322:DoWolfyOutside,
                     323:DoWolfyFollow,
                     324:lambda Screen,Maze,X,Y,I ={},S={"Green Puzzle Box":1}: MazeRooms.DoChest(Screen,Maze,X,Y,I,S),
                     325:lambda Screen,Maze,X,Y,I ={},S={"Summoner:4":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     326:lambda Screen,Maze,X,Y,I ={},S={"Mage:6":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     327:lambda Screen,Maze,X,Y,I ={},S={"Summoner:5":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     328:lambda S,M,X,Y: MazeRooms.DoSign(S, M, X, Y, \
                        "<CENTER>Church of the <CN:YELLOW>1up"),
                     329:L5DoPriest,
                     330:lambda Screen,Maze,X,Y,I ={"Phoenix Down":3},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S), 

                    }


if __name__=="__main__":
    Str = TreasureDirections.upper()
    NewStr = ""
    for Char in Str:
        if Char in ["N","S","E","W"]:
            NewStr += Char
    Index = 5
    print NewStr

