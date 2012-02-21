"""
Special maze locations for level 8.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms
import random
import Maze

def DoQueenOfHearts(S,M,X,Y):
    Global.App.DoNPC("QueenOfHearts")
    return 0

def DoKingOfClubs(S,M,X,Y):
    Global.App.DoNPC("KingOfClubs")
    return 0

def DoQueenOfDiamonds(S,M,X,Y):
    Global.App.DoNPC("QueenOfDiamonds")
    return 0

def DoJackOfSpades(S,M,X,Y):
    Global.App.DoNPC("JackOfSpades")
    return 0

def DoWevelChest(S,M,X,Y):
    ItemLevel = random.choice((0,0,0,0,0,1))
    if ItemLevel:
        Items = Global.QuarterMaster.GetRandomBooty(random.randrange(1,3))[0]
    else:
        Items = {}
    Special = {"gold":random.randrange(1,200),
               "wevel8":1}
    return MazeRooms.DoChest(S,M,X,Y,Items,Special,3)

def DoTower(S,M,X,Y):
    if Global.Party.EventFlags.get("L8Tower"):
        Global.App.ShowNewDialog("You've already saved the High Priestess.  (Anyway, you fear for your sanity if you spent more time in there!)")
        return 0
# %%%
##    if not Global.Party.KeyItemFlags.get("Ariadne's Thread"):
##        Global.App.ShowNewDialog("A dizzying labryinth sprawls before you.  Somehow, the tower is bigger inside than it looks from the outside...\n\nYou pull back, to avoid getting lost.")
##        return 0
    Global.App.ShowNewDialog("A dizzying labryinth sprawls before you.  Somehow, the tower is bigger inside than it looks from the outside...\n\nYou enter, hoping to find the High Priestess quickly...", Callback = EnterTower)

def EnterTower():
    Global.App.ShowTowerScreen()

def DoBlezmon(S,M,X,Y):
    if Global.Party.EventFlags.get("L8Blezmon"):
        Global.App.ShowNewDialog("The <CN:ORANGE>Blezmon tourney</C> is over.")
        return 0
    Str = "The <CN:ORANGE>Blezmon tourney</C> is still going on.  After a few games, you are able to challenge the current champion.  Are you ready to play?"
    Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = BlezmonCallback)
    return 0

def BlezmonCallback():    
    Global.App.ShowBlezmonScreen()
    
def DoJoker(S,M,X,Y):
    Global.App.DoNPC("Joker")
    return 0

def DoPoisonShells(Screen, Maze, X, Y):
    if Global.Party.KeyItemFlags.get("Toxic Shells", None):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    Screen.Redraw()
    Screen.RenderMaze()
    Str = """<CN:BRIGHTGREEN>SNIPER RIFLE ACQUIRED!</C>\n\nYou found a sniper rifle, with a supply of <CN:PURPLE>Toxic Shells</C>.

<CN:YELLOW>[ Sniping will now <CN:PURPLE>poison<CN:YELLOW> any critter you hit! ]
"""
    Global.Party.KeyItemFlags["Toxic Shells"] = 1
    Global.Party.KeyItemFlags["Sniper Rifle"] = 1
    Global.App.ShowNewDialog(Str)
    return 1

def DoSolitaireBattle(S,M,X,Y):
    if Global.Party.EventFlags.get("L8Solitaire"):
        return 1
    if Global.Party.EventFlags.get("L8ClubsJoined") and Global.Party.EventFlags.get("L8HeartsJoined") and \
        Global.Party.EventFlags.get("L8DiamondsJoined") and Global.Party.EventFlags.get("L8SpadesJoined"):
        Str = "<CN:BRIGHTRED><CENTER>Goblin Battle!</CENTER>\n\nYour forces need you.  Are you prepared to direct them into formation?"
        Global.App.ShowNewDialog(Str, Callback = StartSolitaireGame)
        return 0
    Str = "<CN:BRIGHTRED><CENTER>Goblins!</CENTER>\n\nA goblin camp stretches before you, and your forces are insufficient for an assault.\n\nYou carefully slink away..."
    Global.App.ShowNewDialog(Str)
    return 0

def StartSolitaireGame():
    Global.App.ShowSolitaireScreen()

def DoShivanDragon(S,M,X,Y):
    if Global.Party.KilledBosses.get((8, "ShivanDragon")):
        return 1
    Monsters = [[Global.Bestiary.GetCritter("Shivan Dragon"),
                 ]] 
    Booty = ({}, {}, 0)
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "ShivanDragon", SongFileName = "SOR.mp3", CanFlee = 0)
    #Global.App.ScreenStack[-1].Redraw()
    #Str = "<CENTER><CN:PURPLE>Necromancers!</C>\n\nThe wizards cast a spell of <CN:ORANGE>Confusion</C>!\n\n<CENTER><CN:BRIGHTRED>All arrows are reversed!</C>\n(Hit <CN:GREEN>LEFT</C> when arrows point <CN:GREEN>RIGHT</C>!)"
    #Global.App.ShowNewDialog(Str)
    return 1
    
def DoChute(S, M, X, Y):
    Global.Party.X = X
    Global.Party.Y = Y
    S.Redraw()
    S.RenderMaze()
    Global.App.ShowNewDialog("<CENTER><CN:BRIGHTRED>A chute!", Callback = lambda S=S: ChuteFall(S))

def ChuteFall(S):
    Global.Party.X = 28
    Global.Party.Y = 15
    Global.Party.Z = 9
    Maze.GoToMazeLevel(9)
    S.Redraw()
    S.RenderMaze(1)
    Global.App.ShowNewDialog("<CENTER><BIG>Thud!")

def DoL8Shop(Screen, Maze, X, Y):
    Inventory = {"Hi-Potion":None, "Antidote":None, "Black Coffee":None, "Medusa Scale":None, "Compass":None, "Escapipe":None}
    Global.App.GoShopping(Inventory, "Inventory Isn't Boring...Inventory Is Life!", "Shop3")
    return 0 # Don't stay inside

    
EnterRoomRoutines = {451:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A large <CN:BRIGHTRED>red heart</c> is emblazoned above the door."),
                     452:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"<CN:BRIGHTRED>The Queen of Hearts</c>"),
                     453:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"You stroll through a well-tended garden.  A topiary has been trimmed into whimsical shapes, and the roses have been freshly painted red."),
                     454:DoQueenOfHearts,
                     455:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"<CENTER>Blezmon Tourney\n\nOnly the most blezmotic shall win!"),
                     456:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A large <CN:GREY>black club</c> is emblazoned above the door."),
                     #457: #Item1
                     458:DoKingOfClubs,
                     459:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"The uneven obsidian walls in this unnatural chasm tilt and\nskew at cruel angles.\nA tower rises vertiginously above you."),
                     460:DoTower,
                     461:DoChute,
                     462:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A large <CN:BRIGHTRED>red diamond</c> is emblazoned above the door."),
                     463:DoQueenOfDiamonds,
                     464:DoWevelChest,
                     465:DoJoker,
                     466:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"A large <CN:GREY>black spade</c> is emblazoned above the door."),
                     467:DoJackOfSpades,
                     468:DoSolitaireBattle,
                     469:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"The floor here is ominously singed.  Bits of bone and ash are strewn about."),
                     470:DoShivanDragon,
                     472:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"You are walking through a grand palace.  Plush <CN:PURPLE>purple</C> carpet muffles your footsteps."),
                     473:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"You are in a lavish water closet.  White porcelain glints in the light.\n\nA lever is here, labeled: ROYAL FLUSH"),
                     474:lambda S,M,X,Y: MazeRooms.DoSign(S,M,X,Y,"You are in a luxurious royal bedroom."),
                     475:DoBlezmon,
                     476:lambda Screen,Maze,X,Y,I ={},S={"Mage:11":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     477:lambda Screen,Maze,X,Y,I ={},S={"Mage:12":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     478:lambda Screen,Maze,X,Y,I ={},S={"Summoner:9":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     479:lambda Screen,Maze,X,Y,I ={},S={"Cleric:11":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     480:lambda Screen,Maze,X,Y,I ={},S={"Cleric:12":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     481:DoPoisonShells,
                     482:lambda Screen,Maze,X,Y,I ={"X-Potion":10},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     483:DoL8Shop,
                     484:lambda Screen,Maze,X,Y,I ={"Red Mage Sword":1, "Studded Mail":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                    }