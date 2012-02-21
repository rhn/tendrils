"""
Code to support all the fancy stuff that can be found in the maze.  This file
includes general-purpose rooms that aren't specific to a dungeon level.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import Maze

# Contents from 0..99 are 'standard' contents, that any scenario is likely to use.
# Contents from 100 to 999 are 'scenario' contents.  100-149 for level 1, 150-199 for level 2,
# and so forth.
ContentsNames = {0:"Empty",
                 1:"Safe", # for town squares
                 2:"Monsters Sometimes",
                 3:"Monsters Always",
                 4:"Stairs up",
                 5:"Stairs down",
                 }

WanderingMonstersOK = {0:1, 4:1, 5:1,}

def GetEnterRoomRoutine(Contents):
    if Contents<100:
        return EnterRoomRoutines.get(Contents, None)
    elif Contents<150:
        import MazeLevel1
        return MazeLevel1.EnterRoomRoutines.get(Contents, None)
    elif Contents<200:
        import MazeLevel2
        return MazeLevel2.EnterRoomRoutines.get(Contents, None)
    elif Contents<250:
        import MazeLevel3
        return MazeLevel3.EnterRoomRoutines.get(Contents, None)
    elif Contents<300:
        import MazeLevel4
        return MazeLevel4.EnterRoomRoutines.get(Contents, None)
    elif Contents<350:
        import MazeLevel5
        return MazeLevel5.EnterRoomRoutines.get(Contents, None)
    elif Contents<400:
        import MazeLevel6
        return MazeLevel6.EnterRoomRoutines.get(Contents, None)
    elif Contents<450:
        import MazeLevel7
        return MazeLevel7.EnterRoomRoutines.get(Contents, None)
    elif Contents<500:
        import MazeLevel8
        return MazeLevel8.EnterRoomRoutines.get(Contents, None)
    elif Contents<550:
        import MazeLevel9
        return MazeLevel9.EnterRoomRoutines.get(Contents, None)
    else:
        import MazeLevel10
        return MazeLevel10.EnterRoomRoutines.get(Contents, None)

# These are functions that are called when the party enters a maze square.
# Return 1 if the player can stay in the room, and return 0 if they should be moved
# back to the room they came from.  For example: Shops return 0, because you don't stay
# inside the door when you're done shopping.

def DoMonstersSometimes(Screen, Maze, X, Y):
    Maze.Rooms[(X,Y)] = 0
    if random.random() > 0.5:
        Global.Party.GetNextRandomBattle() # reset time-to-encounter        
        Global.App.BeginRandomBattle(1)        
    return 1

def DoMonstersAlways(Screen, Maze, X, Y):
    Maze.Rooms[(X,Y)] = 0
    Global.Party.GetNextRandomBattle() # reset time-to-encounter
    Global.App.BeginRandomBattle(1)
    return 1

def DoStairsUp(Screen, Maze, X, Y):
    Screen.SignText = "A stairway here leads upwards.\n\nPress PgUp to ascend."
    return 1

def DoStairsDown(Screen, Maze, X, Y):
    Screen.SignText = "A stairway here leads downwards.\n\nPress PgDown to descend."
    return 1

def DoStairsBoth(Screen, Maze, X, Y):
    Screen.SignText = "A stairway here leads upwards and downwards.\n\nPress PgUp to ascend.\nPress PgDown to descend."
    return 1

def DoSign(Screen, Maze, X, Y, Text):
    Screen.SignText = Text
    return 1
    

def DoChest(Screen, Maze, X, Y, ItemDict = {}, SpecialDict = {}, BootyType = 2):
    # Check to see if the party has already opened the chest here.
    # If they have, this is just an empty room!
    if Global.Party.LootedChests.get((X, Y, Maze.Level)):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y    
    Screen.RenderMaze()
    Screen.Redraw()
    # %%% Dialog should give the option to cast Calfo!
    print SpecialDict
    Global.App.AskDisarmChest(ItemDict, SpecialDict, BootyType)
    return 1

def DoSavePoint(Screen, Maze, X, Y):
    Global.App.SaveGame()    
    return 0

def DoPit(Screen, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    Screen.RenderMaze()
    #Screen.Redraw()
    Str = "<CENTER><CN:BRIGHTRED>Ouch!</C>\n\nYou fell in a pit!\n\n"
    for Player in Global.Party.Players:
        Fraction = random.randrange(10, 49) / float(100)
        if Player.IsAlive():
            Wound = Fraction * Player.MaxHP
            Player.HP -= Wound
            Str += "%s takes %d damage!\n"%(Player.Name, Wound)
            if Player.HP < 0:
                Player.Die()
                Str += "<CN:BRIGHTRED>%s is DEAD!!</C>\n"%Player.Name
    Global.App.ShowNewDialog(Str, Callback = Maze.CheckForAllDead)
    return 1 

def DoGasTrap(Screen, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    Screen.Redraw()
    Str = "<CENTER><CN:PURPLE>GAS TRAP!</C>\n\nToxic fumes!\n\n"
    for Player in Global.Party.Players:
        Fraction = random.randrange(5, 20) / float(100)
        if Player.IsAlive():
            Wound = Fraction * Player.MaxHP
            Player.HP -= Wound
            Str += "%s takes <CN:PURPLE>%d</C> damage!\n"%(Player.Name, Wound)
            if Player.HP < 0:
                Player.Die()
                Str += "<CN:BRIGHTRED>%s is DEAD!!</C>\n"%Player.Name
            elif not Player.HasPerk("Poison Immune"):
                Player.Perks["Poison"] = 900
                Str += "%s is <CN:PURPLE>poisoned</C>!\n"%Player.Name                
    Global.App.ShowNewDialog(Str, Callback = Maze.CheckForAllDead)
    return 1 

def DoManaDrainTrap(Screen, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    Screen.Redraw()
    Str = "<CENTER><CN:PURPLE>Mana Drain!</C>\n\nYou hear a high-pitched whine...\n\n"
    for Player in Global.Party.Players:
        if Player.MP and Player.IsAlive(): # you could always sneak your mage through while dead :)
            Player.MP = 0
            Str += "%s has been drained of magic points!\n"%Player.Name
    Global.App.ShowNewDialog(Str, Callback = Maze.CheckForAllDead)
    return 1 



def DoInn(Screen, Maze, X, Y):
    # Keep track of location (for warp-home spells):
    Global.Party.InnX = X
    Global.Party.InnY = Y
    Global.Party.InnZ = Maze.Level
    Global.App.ShowInn()
    return 0

def DoBardsGuild(S, M, X, Y, Intro):
    if Intro:
        Str = """<CENTER><CN:BRIGHTGREEN>Bard's Guild</C></CENTER>\n\nBards gather here, in a side room of the inn, to practice their music.  You hear various \
instruments, from the tiny Manaflute to the dreaded Dire Bagpipes.\n\nThe bards offer to give you a lesson in \
rhythmic combat before you enter the dungeon.  Do you accept?"""
        Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = DoBardIntro)
    else:
        Str = """The merry sounds of the Bard's Guild greet you.  The bards offer to spar with you.  Do you \
want to practice some battle songs?"""
        Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = DoBardSparring)

def DoBardIntro():
    import PracticeScreen
    Global.App.ShowPracticeScreen(PracticeScreen.PracticeStates.Learning1)

def DoBardSparring():
    import PracticeScreen
    Songs = Global.MusicLibrary.GetPossibleBattleSongs(Global.Maze.Level)
    Song = random.choice(Songs)
    Global.App.ShowPracticeScreen(PracticeScreen.PracticeStates.Sparring, Song)
    
def DoNamingway(S, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()    
    Str = "A strange man in a turban sits here, playing Solitaire at a table.  He smiles at you and says:\n\n<CN:BRIGHTBLUE>Namingway here.  Would you like to change your name?\n\n<CN:GREY>Who will change?"
    Global.App.ShowNewDialog(Str, ButtonGroup.PickPlayer, Callback = DoNamingwayPick)
    return 0

def DoNamingwayPick(Player):
    if Player:
        Str = "Enter a new name for %s the level %d %s:\n<CN:GREY>(press ESC to cancel)\n"%(Player.Name, Player.Level, Player.Species.Name)
        Global.App.ShowWordEntryDialog(Str, lambda S,P=Player:NamingwayEntry(S,P), 10)

def NamingwayEntry(Str, Player):
    Str = Str.strip()
    if Str:
        Player.Name = Str
        try:
            Global.App.ScreenStack[-1].StatusPanel.ReRender()
        except:
            pass
        Str = "Enjoy your new name!"
        Global.App.ShowNewDialog(Str)
        

def DoGetTendrils(S, X, Y, L):
    if Global.Party.KeyItemFlags.get("Tendril %d"%L):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    Global.Party.KeyItemFlags["Tendril %d"%L] = 1
    Global.App.ShowNewDialog("You have acquired: <CN:ORANGE>Tendril #%d</C>\n\nIf you collect all 10, something good may happen..."%L)
    

###############################################################################################################################
###############################################################################################################################
EnterRoomRoutines = {2:DoMonstersSometimes,
                     3:DoMonstersAlways,
                     4:DoStairsUp,
                     5:DoStairsDown,
                     6:DoStairsBoth,
                     7:DoSavePoint,
                     8:DoPit,
                     9:DoInn,
                     10:DoNamingway,
                     11:DoGasTrap, 
                     12:DoManaDrainTrap,
                     20:lambda S,M,X,Y,L=1:DoGetTendrils(S,X,Y,L),
                     21:lambda S,M,X,Y,L=2:DoGetTendrils(S,X,Y,L),
                     22:lambda S,M,X,Y,L=3:DoGetTendrils(S,X,Y,L),
                     23:lambda S,M,X,Y,L=4:DoGetTendrils(S,X,Y,L),
                     24:lambda S,M,X,Y,L=5:DoGetTendrils(S,X,Y,L),
                     25:lambda S,M,X,Y,L=6:DoGetTendrils(S,X,Y,L),
                     26:lambda S,M,X,Y,L=7:DoGetTendrils(S,X,Y,L),
                     27:lambda S,M,X,Y,L=8:DoGetTendrils(S,X,Y,L),
                     28:lambda S,M,X,Y,L=9:DoGetTendrils(S,X,Y,L),
                     29:lambda S,M,X,Y,L=10:DoGetTendrils(S,X,Y,L),
                     
                     }