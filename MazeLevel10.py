"""
Special maze locations for level 10.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms

def DoBlackKnight(S,M,X,Y):
    if Global.Party.EventFlags.get("L10JoustPong"):
        return 1
    Str = """A dark knight stands before you.  "<CN:ORANGE>NONE SHALL PASS!</C>", he says.\n\n\
You can challenge him to a duel, but if he wins, he shall hurl you into the lava below.\n\nFight him?"""
    Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = BlackKnightBattle)
    return 0

def BlackKnightBattle():
    Global.App.ShowJoustPongScreen()

def DoFinalBoss(S,M,X,Y):
    Rank1 = [Global.Bestiary.GetCritter("Mother Brain"),]
    Rank2 = [Global.Bestiary.GetCritter("BrainGuy"),Global.Bestiary.GetCritter("BrainGuy"),Global.Bestiary.GetCritter("BrainGuy"),Global.Bestiary.GetCritter("BrainGuy"),]
    Monsters = [Rank1,[],Rank2]
    Booty = ({},{},0)
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "MotherBrain1", SongFileName="MountainMix.xm", CanFlee = 0)
    return 1


def DoOldWoman(Screen, Maze, X, Y):
    Global.App.DoNPC("Old Woman")
    return 0

def DoOldMan(Screen, Maze, X, Y):
    Global.App.DoNPC("Old Man")
    return 0

def DoWhatAmI(S,M,X,Y):
    if Global.Party.EventFlags.get("L10EVIL"):
        return 1
    Str = "There is an expectant silence.\nWhat do you say?"
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    Global.App.ShowWordEntryDialog(Str, WhatAmICallback, 10) # limit to 10 chars (real answer is 4 chars)
    return 0

def WhatAmICallback(Word):
    if Word.lower().strip() == "evil":
        Global.Party.EventFlags["L10EVIL"] = 1
        Global.Maze.Walls[1][(15,8)] = 0
        Global.Maze.Walls[0][(15,7)] = 0
        Str = "The wall before you crumbles to dreamlike nothingness.\n\nYou hear a horrid laughter in the distance..."
        Global.App.ShowNewDialog(Str)
    else:
        Str = "There is an ominous murmur...then nothing."
        Global.App.ShowNewDialog(Str)
        
def DoDopefish(S,M,X,Y):
    if Global.Party.KilledBosses.get((10, "Dopefish")):
        return 1
    Monsters = [[Global.Bestiary.GetCritter("Dopefish"),
                ]] 
    Booty = ({}, {}, 0)
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "Dopefish", SongFileName = "Bubble Bobble.xm", CanFlee = 0)
    #Global.App.ScreenStack[-1].Redraw()
    #Str = "<CENTER><CN:PURPLE>Octopus!</C>\n\nThe kraken casts a spell of <CN:ORANGE>Confusion</C>!\n\n<CENTER><CN:BRIGHTRED>All arrows are reversed!</C>\n(Hit <CN:GREEN>LEFT</C> when arrows point <CN:GREEN>RIGHT</C>!)"
    #Global.App.ShowNewDialog(Str)
    return 1

def DoSinistar(S, M, X, Y):
    "Rematch!"
    if Global.Party.EventFlags.get("L10Sinistar", 0):
        return 1
    # Start the Sinistar conversation, followed by trivia.  
    Global.Party.EventFlags["L10Sinistar"] = 1
    Global.App.DoNPC("Sinistar")
    return 1
    
def DoEskimo(S,M,X,Y):
    Global.App.DoNPC("Eskimo")
    return 0

def DoPegPuzzle(S,M,X,Y):
    if Global.Party.EventFlags.get("L10PegDoor"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    Str = """A door is here, with a strange lock mechanism.\n\nAttempt to unlock it?"""
    Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback=TryPegPuzzle)

def DoPegLoot(S,M,X,Y):
    if Global.Party.EventFlags.get("L10PegLoot"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    Global.Party.EventFlags["L10PegLoot"] = 1
    Str = """You have found a cache of spells!\n"""
    Str += Global.Party.LearnSpell("Mage", 14)
    Str += Global.Party.LearnSpell("Cleric", 14)
    Str += Global.Party.LearnSpell("Summoner", 12)
    Global.App.ShowNewDialog(Str)    

def TryPegPuzzle(Dummy = None):
    Global.App.ShowPegSolitaireScreen(SolveCallback = PegPuzzleSuccess, PuzzleName = "Fireplace")

def PegPuzzleSuccess():
    Global.Party.EventFlags["L10PegDoor"] = 1
    M = Global.Maze
    M.Walls[1][(24,0)] = 0
    M.Walls[0][(24,29)] = 0
    Str = "<CENTER>SUCCESS!</CENTER>\n\nThe door swings open.\n\n<CN:YELLOW>(You have unlocked the <CN:GREEN>Peg Jump<CN:YELLOW> minigame!)"
    Global.MemoryCard.Set("MiniGamePegJump")
    Global.App.ShowNewDialog(Str)
    
def EnterMazeLevel():
    "Event handler: Entering this maze level"
    M = Global.Maze
    ##############################
    # The peg door may already be open:
    if Global.Party.EventFlags.get("L10PegDoor"):
        M.Walls[1][(24,0)] = 0
        M.Walls[0][(24,29)] = 0
    if Global.Party.EventFlags.get("L10EVIL"):
        M.Walls[1][(15,8)] = 0
        M.Walls[0][(15,7)] = 0

def DoWevelsOnly(S,M,X,Y):
    Ready = 1
    for X in range(1, 11):
        if not Global.Party.KeyItemFlags.get("Tendril %d"%X):
            Ready = 0
    if not Ready:
        Global.App.ShowNewDialog("A voice booms out:\n\nTHOU HAST NOT THE TENDRILS - YOU SHALL NOT PASS.\n\n<CN:GREY>You sense that this room is optional...")
        return 0
    MazeRooms.DoSign(S,M,X,Y, """WELCOME, GATHERER OF TENDRILS.""")
    return 1

def DoGameDesigner(S,M,X,Y):
    Global.App.DoNPC("Author")
    return 0

EnterRoomRoutines = {550:lambda Screen,Maze,X,Y,I ={"Myer Sword":1},S={}: MazeRooms.DoChest(Screen,Maze,X,Y,I,S),
                     551:lambda Screen,Maze,X,Y,I ={"Elf Mantle":1},S={}: MazeRooms.DoChest(Screen,Maze,X,Y,I,S),
                     552:lambda Screen,Maze,X,Y,I ={"Cats Claws":1},S={}: MazeRooms.DoChest(Screen,Maze,X,Y,I,S),
                     553:DoBlackKnight,
                     554:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y, """Letters of pale fire are engraved into the floor:\n\n<CN:BRIGHTRED><CENTER>I am at the beginning of legends"""),
                     555:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y, """Letters of pale fire are engraved into the floor:\n\n<CN:BRIGHTRED><CENTER>I am in plain sight"""),
                     556:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y, """Letters of pale fire are engraved into the floor:\n\n<CN:BRIGHTRED><CENTER>I am the center of gravity"""),
                     557:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y, """Letters of pale fire are engraved into the floor:\n\n<CN:BRIGHTRED><CENTER>I am at the end of time"""),
                     558:DoWhatAmI,
                     559:DoOldWoman,
                     560:DoOldMan,
                     561:DoDopefish,
                     562:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y, """Maze of Glass"""),
                     563:DoEskimo,
                     564:DoSinistar,
                     565:DoPegPuzzle,
                     566:DoPegLoot,
                     567:lambda Screen,Maze,X,Y,I ={"Mantra Band":1},S={}: MazeRooms.DoChest(Screen,Maze,X,Y,I,S),
                     568:DoWevelsOnly,
                     569:DoGameDesigner,
                     666:DoFinalBoss,
                    }