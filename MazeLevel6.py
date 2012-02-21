"""
Special maze locations for level 6.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms
import sys

def EnterMazeLevel():
    "Event handler: Entering this maze level"
    if Global.Party.EventFlags.get("L6DragonLock", 0):
        Global.Maze.Walls[0][(29,6)] = 0 # OPEN the door!
    if Global.Party.EventFlags.get("L6BasisLock", 0):
        Global.Maze.Walls[0][(0,20)] = 0 # OPEN the door!
        Global.Maze.Walls[1][(0,21)] = 0 # OPEN the door on both sides!


def DoSinistar(S, M, X, Y):
    if Global.Party.EventFlags.get("Sinistar", 0):
        return 1
    # Start the Sinistar conversation, followed by trivia.  
    Global.Party.EventFlags["Sinistar"] = 1
    Global.App.DoNPC("Sinistar")
    return 1
    

LockBases = [
    [(1, 1, 1), (-1, 1, 0), (0, -1, 1)],
    [(1,0,0), (-1, 1, 0), (0, 1, 1)]
    ]

def BuildLockPuzzle():
    Basis = random.choice(LockBases)[:]
    random.shuffle(Basis)
    # Shuffle digits consistently:
    Places = [0, 1, 2]
    A = random.choice(Places)
    Places.remove(A)
    B = random.choice(Places)
    Places.remove(B)
    C = Places[0]
    for Index in range(3):
        Sign = random.choice((1, -1))
        Basis[Index] = (Basis[Index][A]*Sign, Basis[Index][B]*Sign, Basis[Index][C]*Sign)
    Target = random.randrange(1000)
    return (Basis, Target)

def DoLockPuzzle(S, M, X, Y):
    print "X and Y:", X, Y
    if Global.Party.EventFlags.get("L6LockPuzzleSolved", 0):
        Global.Maze.Walls[0][(X,Y)] = 0
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    Puzzle = Global.Party.EventFlags.get("L6LockPuzzle", None)
    if not Puzzle:
        Puzzle = BuildLockPuzzle()
        Global.Party.EventFlags["L6LockPuzzle"] = Puzzle
    Str = "A strange, intricately-worked door looms before you.  Set above the handle are three dials with \
engraved digits.  Above the dials, phosphorescent letters glow:\n\n"
    (Basis, Target) = Puzzle
    for Index in range(len(Basis)):
        Frungy = Basis[Index]
        Str += DescribeBasis(Index, Frungy)
    Str += "\nTarget: %03d"%Target
    Str += "\n\nHow will you turn the dials?"
    Global.App.ShowWordEntryDialog(Str, LockPuzzleEntry, 3, "0123456789")

def LockPuzzleEntry(Str):
    if not Str:
        return
    Puzzle = Global.Party.EventFlags.get("L6LockPuzzle", None)
    (Basis, Target) = Puzzle
    Number = ApplyBasis(Basis, Str)
    if Number == Target: # or Str == "111":
        Global.Party.EventFlags["L6LockPuzzleSolved"] = 1
        Global.App.ShowNewDialog("There is a tinkling of bells, and the door swings open.")
        print "X and Y:", Global.Party.X, Global.Party.Y        
        Global.Maze.Walls[0][(Global.Party.X,Global.Party.Y)] = 0
        return
    Str = "Angry-looking letters flash on the door:\n\n<CN:BRIGHTGREEN>%03d DOES NOT MATCH \
TARGET %03d.\n<CN:BRIGHTRED>INVALID INPUT.  DEATH RAY CHARGING.\nERROR: DEATH RAY NOT FOUND."%(Number, Target)
    Global.App.ShowNewDialog(Str)
    
def DescribeBasis(Index, Basis):
    Str = "<CN:BRIGHTGREEN>Place %d: "%Index
    for Pos in Basis:
        if Pos==1:
            Str += "<CN:BRIGHTBLUE>Up</C>,"
        elif Pos == -1:
            Str += "<CN:BRIGHTRED>Down</C>,"
        else:
            Str += "<CN:GREY>none</C>,"
    return Str[:-1]+"\n"

def ApplyBasis(Basis, Str):
    X = int(Str)
    Ones = X%10
    Hundreds = X/100
    Tens = (X - Ones - Hundreds*100)/10
    Str = ""
    for Digit in range(3):
        NewDigit = Basis[0][Digit]*Hundreds + Basis[1][Digit]*Tens + Basis[2][Digit]*Ones
        while (NewDigit < 0):
            NewDigit += 10
        NewDigit = NewDigit % 10
        Str += "%d"%NewDigit
    return int(Str)

def TestLockBases():
    for Basis in LockBases:
        print "BASIS:"
        print Basis
        for Target in (100, 10, 1):
            for X in range(0, 1000):
                Ones = X%10
                Hundreds = X/100
                Tens = (X - Ones - Hundreds*100)/10
                #print Hundreds, Tens, Ones
                Str = ""
                for Digit in range(3):
                    NewDigit = Basis[0][Digit]*Hundreds + Basis[1][Digit]*Tens + Basis[2][Digit]*Ones
                    while (NewDigit < 0):
                        NewDigit += 10
                    NewDigit = NewDigit % 10
                    Str += "%d"%NewDigit
                #print Str
                if int(Str)==Target:
                    print "%d -> %d"%(X, Target)
                    break
                #sys.stdin.readline()
####
####TestLockBases()

def DoEndOfGame(S, M, X, Y):
    Global.App.DoVictory()

def DoScorchedEarth(S, M, X, Y):
    if not Global.Party.EventFlags.get("L6ScorchedEarth"):
        Global.Party.X = X
        Global.Party.Y = Y
        S.RenderMaze()
        S.Redraw()        
        Str = "A baffling sight greets you beyond this door.  Great metal tortoises climb about, \
apparently spitting balls of fire at each other.  You examine some turtles nearby, which \
appear to be sleeping.  Strangely enough, each is a metal contraption, with a door leading \
inside! \n\nSuddenly, the turtles in the distance begin firing at you.  You have no choice but \
to take refuge in these strange devices...\n\n<CN:BRIGHTGREEN>UH-OH!  THE TANK HAVE STARTED TO MOVE!"
        Global.App.ShowNewDialog(Str, Callback = ScorchedEarthCallback)
        Global.Party.EventFlags["L6ScorchedEarth"]=1
    else:
        S.SignText = "<CENTER><CN:BRIGHTRED>FIRING RANGE</CN>\nWatch for falling bombs."
    return 1

def ScorchedEarthCallback():    
    Global.App.ShowWormScreen()

def DoLetterSign(S,M,X,Y,L):
    MazeRooms.DoSign(S,M,X,Y,"<CENTER>A letter is etched into the floor:\n<CN:YELLOW>%s</CN>"%L)
    return 1

def DoDragonLock(S,M,X,Y):
    if Global.Party.EventFlags.get("L6DragonLock"):
      return 1
    # Display a dialog for entering a 5-digit combo:
    Str = "A sneering mouth is carved into the wall here.\nIt speaks: WHAT IS THE PASSWORD?\nWhat do you reply?"
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    Global.App.ShowWordEntryDialog(Str, DragonLockEntry, 10) # limit to 10 chars (real answer is 6 chars)
    return 0

def DragonLockEntry(Str):
    if not Str:
        return
    if Str.strip().upper() == "DRAGON":
        Str = "The mouth speaks:\n\n\n<CENTER>UNDERSTOOD.</CENTER>\n\n\nThe door silently swings open."
        Global.App.ShowNewDialog(Str)
        Global.Maze.Walls[0][(29,6)] = 0 # OPEN the door!
        Global.Party.EventFlags["L6DragonLock"] = 1
    else:
        Str = "There is a long, awkward silence.  Finally the mouth says:\n<CENTER>INCORRECT.</CENTER>\nThe door remains shut."
        Global.App.ShowNewDialog(Str)

def DoDaleks(S,M,X,Y):
    if Global.Party.EventFlags.get("L6Daleks"):
        return 1
        ##Str = "You have already defeated the giant robots.  Would you like to fight them again for the fun of it?"
        ##Global.App.ShowNewDialog(Str, Buttons = ButtonGroup.YesNo, Callback = StartDalekFight)
    else:
        Str = "You are attacked by a gang of giant robots!\n\n(Luckily, they aren't very bright, so you can probably get them to crash into each other...)"
        Global.App.ShowNewDialog(Str, Callback = StartDalekFight)

def StartDalekFight():
    Global.App.ShowDalekScreen()

def DoEskimo(S,M,X,Y):
    Global.App.DoNPC("Eskimo")
    return 0

def DoRemedialMagicCourse(S, M, X, Y):
    if Global.Party.EventFlags.get("L6MageRemedial"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    LearnStr = ""
    for Index in range(6):
        LearnStr += Global.Party.LearnSpell("Mage", Index)
    Str = "You have wandered into a large room, with rows of chairs facing a raised podium.  From the podium, \
an old mage with an alarmingly large beard is delivering a lecture, and drawing illegible diagrams with \
a magic wand.  He pauses as you enter, and the students glare at you until take your seats on the back row.  \
\n\n<CN:GREY>(Time passes...)</C>\n\nEventually, a bell rings, and everyone disperses.  You're not sure where all these wizards \
came from, and you totally bombed the pop quiz, but your Mages can now cast all beginner spells!\n%s"%LearnStr
    Global.Party.EventFlags["L6MageRemedial"] = 1
    Global.App.ShowNewDialog(Str)
    
def DoBard(S,M,X,Y):
    Global.App.DoNPC("Bard")
    return 0

def DoIceBarrier(S,M,X,Y):
    if Global.Party.EventFlags.get("L6BrokeIce"):
        M.Walls[2][(X,Y)] = 0
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()        
    if Global.Party.EventFlags.get("L6BardTech"):
        Bard = None
        for Player in Global.Party.Players:
            if Player.Species.Name == "Bard":
                Bard = Player
                break
        if Bard:
            Resources.PlayStandardSound("PacmanNoise.wav")
            Global.Party.EventFlags["L6BrokeIce"] = 1
            M.Walls[2][(X,Y)] = 0
            Global.App.ShowNewDialog("A translucent <CN:BRIGHTBLUE>icy wall</C> blocks progress past this corner.\n\n%s plays the Song of Opening, as taught by Syntessa.\n\n<CN:BRIGHTBLUE>The ice-wall shatters!"%Bard.Name)
            return 1
    MazeRooms.DoSign(S,M,X,Y,"A translucent <CN:BRIGHTBLUE>icy wall</C> blocks progress past this corner.\n\nIt seems impervious to your weapons...")
    return 1

# DRAGON puzzle:
# Rooms contain some squares, with some letters rubbed out. The rubbed-out letters are a password!
#D/N
#G/R/T
#A
#B/G/N/R/T
#O
#N
##+----+
##|swam|
##|waXe| < - D
##|aXds|
##|mesh|
##+----+
##+----+
##|luXe|
##|upon|
##|Xoad| < - R (could be T judging by the square, but...)
##|ends|
##+----+
##+----+
##|wXrs|
##|Xbet| < - A
##|redo|
##|stop|
##+----+

##+----+
##|fiXs|
##|idea| < - G (could be N, but it's not)
##|Xear|
##|sari|
##+----+
##+----+
##|hulk|
##|upXn| < - O
##|lXbe|
##|knee|
##+----+
##+----+
##|wiXd|
##|idea|
##|Xear| < - N
##|dark|
##+----+                     
EnterRoomRoutines = {350:DoSinistar,
                     351:lambda Screen,Maze,X,Y,I ={"Hi-Potion":10},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     #351:DoEndOfGame,
                     352:DoLockPuzzle,
                     353:DoScorchedEarth,
                     354:lambda S,M,X,Y,L="a": DoLetterSign(S,M,X,Y,L),
                     355:lambda S,M,X,Y,L="b": DoLetterSign(S,M,X,Y,L),
                     356:lambda S,M,X,Y,L="c": DoLetterSign(S,M,X,Y,L),
                     357:lambda S,M,X,Y,L="d": DoLetterSign(S,M,X,Y,L),
                     358:lambda S,M,X,Y,L="e": DoLetterSign(S,M,X,Y,L),
                     359:lambda S,M,X,Y,L="f": DoLetterSign(S,M,X,Y,L),
                     360:lambda S,M,X,Y,L="g": DoLetterSign(S,M,X,Y,L),
                     361:lambda S,M,X,Y,L="h": DoLetterSign(S,M,X,Y,L),
                     362:lambda S,M,X,Y,L="i": DoLetterSign(S,M,X,Y,L),
                     363:lambda S,M,X,Y,L="j": DoLetterSign(S,M,X,Y,L),
                     364:lambda S,M,X,Y,L="k": DoLetterSign(S,M,X,Y,L),
                     365:lambda S,M,X,Y,L="l": DoLetterSign(S,M,X,Y,L),
                     366:lambda S,M,X,Y,L="m": DoLetterSign(S,M,X,Y,L),
                     367:lambda S,M,X,Y,L="n": DoLetterSign(S,M,X,Y,L),
                     368:lambda S,M,X,Y,L="o": DoLetterSign(S,M,X,Y,L),
                     369:lambda S,M,X,Y,L="p": DoLetterSign(S,M,X,Y,L),
                     370:lambda S,M,X,Y,L="q": DoLetterSign(S,M,X,Y,L),
                     371:lambda S,M,X,Y,L="r": DoLetterSign(S,M,X,Y,L),
                     372:lambda S,M,X,Y,L="s": DoLetterSign(S,M,X,Y,L),
                     373:lambda S,M,X,Y,L="t": DoLetterSign(S,M,X,Y,L),
                     374:lambda S,M,X,Y,L="u": DoLetterSign(S,M,X,Y,L),
                     375:lambda S,M,X,Y,L="v": DoLetterSign(S,M,X,Y,L),
                     376:lambda S,M,X,Y,L="w": DoLetterSign(S,M,X,Y,L),
                     377:lambda S,M,X,Y,L="x": DoLetterSign(S,M,X,Y,L),
                     378:lambda S,M,X,Y,L="y": DoLetterSign(S,M,X,Y,L),
                     379:lambda S,M,X,Y,L="z": DoLetterSign(S,M,X,Y,L),
                     380:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"The letter on the floor has been worn away."),
                     381:DoDragonLock,
                     382:lambda S,M,X,Y,I ={"Rapier":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     383:lambda S,M,X,Y,I ={},Sp={"WIS seed":1, "INT seed":1}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     384:lambda S,M,X,Y,I ={"Teddy Bear Suit":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     385:lambda S,M,X,Y,I ={"108 Gems":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     386:lambda S,M,X,Y,I ={"Gold Helmet":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     387:lambda S,M,X,Y,I ={"Dash Shoes":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     388:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A sign on the door reads:\n<CENTER><CN:BLUE>LITTLE BOYS' ROOM."),
                     389:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A sign on the door reads:\n<CENTER><CN:RED>LITTLE GIRLS' ROOM."),
                     390:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A sign on the door reads:\n<CENTER><CN:GREEN>GIANT ROBOTS' ROOM."),
                     391:DoDaleks,
                     392:DoEskimo,
                     393:lambda Screen,Maze,X,Y,I ={},S={"Mage:7":1, "Mage:8":1}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     394:DoRemedialMagicCourse,
                     395:lambda Screen,Maze,X,Y,I ={},S={"Cleric:8":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     396:lambda Screen,Maze,X,Y,I ={},S={"Summoner:6":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     397:lambda Screen,Maze,X,Y,I ={},S={"Summoner:7":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     398:DoBard,
                     399:DoIceBarrier,
                    }