"""
Special maze locations for level 2.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms

def L2DoPowerPill(Screen, Maze, X, Y):
    Str = "A small white spheroid floats in the air here, glowing serenely\n\nSomehow, it looks rather appetizing...\n\nWho will eat?"
    Global.App.ShowNewDialog(Str, ButtonGroup.PickPlayer, Callback = L2EatPowerPill)
    return 1

def L2EatPowerPill(Player):
    Player.MP = Player.MaxMP
    if Player.MaxMP:
        Str = "%s swallows the glowing orb...and feels magically refreshed!\n\n%s has recovered MP!"%(Player.Name, Player.Name)
    else:
        Str = "%s swallows the glowing orb...and feels magically refreshed!\n\n(But, %s has no MP to restore)"%(Player.Name, Player.Name)
    Global.App.ShowNewDialog(Str)
    Global.Maze.Rooms[(Global.Party.X, Global.Party.Y)] = 0 # it's gone now.

def L2DoFruit(Screen, Maze, X, Y):
    Str = "A large strawberry is floating here in midair, with no visible means of support.\n\nIt looks rather appetizing...\n\nWho will eat?"
    Global.App.ShowNewDialog(Str, ButtonGroup.PickPlayer, Callback = L2EatFruit)
    return 1

def L2EatFruit(Player):
    if Player.HP < Player.MaxHP:
        Player.HP = min(Player.HP + 25, Player.MaxHP)
        Str = "%s eats the fruit...and feels better!\n\n%s has recovered HP!"%(Player.Name, Player.Name)
    else:
        Str = "%s eats the fruit...it tastes very nice"%(Player.Name)
    Global.App.ShowNewDialog(Str)
    Global.Maze.Rooms[(Global.Party.X, Global.Party.Y)] = 0 # it's gone now.


def L2DoGhostBoss(Screen, Maze, X, Y):
    Booty = ({"Pendant of Bub":1, "Pendant of Bob":1}, {"Gold":1500}, 2)
    # If the bosses are dead, it's just a chest, or an ordinary room:
    if Global.Party.KilledBosses.get((2, "Ghosts")):
        if Global.Party.LootedChests.get((X, Y, Maze.Level)):
            return 1 # empty room!
        Global.App.AskDisarmChest(Booty[0], Booty[1], Booty[2])
        return 1
    #%%% Request a boss battle-song here
    Monsters = [[Global.Bestiary.GetCritter("Inky"),Global.Bestiary.GetCritter("Blinky")],
                [Global.Bestiary.GetCritter("Pinky"),Global.Bestiary.GetCritter("Clyde")],
                ]
    Global.App.BeginBattle(Monsters, Booty, "MountainMix.xm", BossBattleName = "Ghosts", CanFlee = 0)
    return 1

EnterRoomRoutines = {150:L2DoPowerPill,
                     151:L2DoGhostBoss,
                     152:lambda Screen,Maze,X,Y,I ={},S={"Mage:2":2}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     153:lambda Screen,Maze,X,Y,I ={},S={"Cleric:2":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     154:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """You feel a vague unease here, as though the warp and weft of reality were twisted slightly."""),
                     155:lambda Screen,Maze,X,Y,I ={},S={"Summoner:1":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     156:lambda Screen,Maze,X,Y,I ={"Bombs":1},S={"gold":50}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     157:L2DoFruit,
                     158:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """Above the door, <CN:RED>GHOST HOUSE</C> is spelled out in ominous letters."""),
                     159:lambda Screen,Maze,X,Y,I ={},S={"WIS seed":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     #159:lambda Screen,Maze,X,Y,I ={},S={"Green Puzzle Box":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     160:lambda Screen,Maze,X,Y,I ={"Galmia Shoes":1},S={"gold":50}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     161:lambda Screen,Maze,X,Y,I ={"Galuf's Amulet":1},S={"gold":50}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     162:lambda Screen,Maze,X,Y,I ={"Star Armlet":1},S={"gold":50}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     163:lambda Screen,Maze,X,Y,I ={"Materia Armor":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     164:lambda Screen,Maze,X,Y,I ={},S={"DEX seed":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     165:lambda Screen,Maze,X,Y,I ={"Potion":10},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                    }