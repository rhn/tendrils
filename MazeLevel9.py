"""
Special maze locations for level 9.
Level 9 is a teleporter-maze made up of sub-levels taken from the
dungeons in The Legend of Zelda.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms


def DoWarp(S,M,X,Y):
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    Resources.PlayStandardSound("MegamanNoise.wav")
    return 0

def DoUltrosSign(S,M,X,Y):
    MazeRooms.DoSign(S,M,X,Y,"""<CENTER><BIG><CN:RED>WARNING</BIG>

A HUGE OCTOPUS
<CN:PURPLE>CODE NO. 29A</C>
<CN:PURPLE>"ULTROS"</C>
IS APPROACHING FAST
    """)
    return 1

def DoUltros(S,M,X,Y):
    if Global.Party.KilledBosses.get((9, "Ultros")):
        return 1
    Monsters = [[Global.Bestiary.GetCritter("Ultros"),
                ]] 
    Booty = ({}, {}, 0)
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "Ultros", SongFileName = "Chrono Trigger.mp3", CanFlee = 0)
    Global.App.ScreenStack[-1].Redraw()
    Str = "<CENTER><CN:PURPLE>Octopus!</C>\n\nThe kraken casts a spell of <CN:ORANGE>Confusion</C>!\n\n<CENTER><CN:BRIGHTRED>All arrows are reversed!</C>\n(Hit <CN:GREEN>LEFT</C> when arrows point <CN:GREEN>RIGHT</C>!)"
    Global.App.ShowNewDialog(Str)
    return 1
    

EnterRoomRoutines = {500:lambda Screen,Maze,X,Y,I ={},S={"Blue Puzzle Box":1}: MazeRooms.DoChest(Screen,Maze,X,Y,I,S),
                     501:lambda Screen,Maze,X,Y,I ={},S={"Mage:13":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     502:lambda Screen,Maze,X,Y,I ={},S={"Cleric:13":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     503:lambda Screen,Maze,X,Y,I ={},S={"Summoner:10":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     504:lambda Screen,Maze,X,Y,I ={},S={"Summoner:11":1,}:MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     505:lambda S,M,X,Y,GotoX=15,GotoY=27:DoWarp(S,M,GotoX,GotoY), #warp A
                     506:lambda S,M,X,Y,GotoX=3,GotoY=24:DoWarp(S,M,GotoX,GotoY), #warp B
                     507:lambda S,M,X,Y,GotoX=4,GotoY=15:DoWarp(S,M,GotoX,GotoY), #warp C
                     508:lambda S,M,X,Y,GotoX=8,GotoY=18:DoWarp(S,M,GotoX,GotoY), #warp D
                     509:lambda S,M,X,Y,GotoX=21,GotoY=20:DoWarp(S,M,GotoX,GotoY), #warp E
                     510:lambda S,M,X,Y,GotoX=14,GotoY=10:DoWarp(S,M,GotoX,GotoY), #warp F
                     511:lambda S,M,X,Y,GotoX=6,GotoY=6:DoWarp(S,M,GotoX,GotoY), #warp G
                     512:lambda S,M,X,Y,GotoX=21,GotoY=2:DoWarp(S,M,GotoX,GotoY), #warp H
                     513:lambda S,M,X,Y,GotoX=12,GotoY=2:DoWarp(S,M,GotoX,GotoY), #warp I
                     
                     514:lambda S,M,X,Y,I ={"Legacy Armor":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     515:lambda S,M,X,Y,I ={"Shield of Justice":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     516:lambda S,M,X,Y,I ={"Mister Angry Eyes":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                     517:DoUltrosSign,
                     518:DoUltros,
                     519:lambda S,M,X,Y,I ={"Flaming Sword":1},Sp={}: MazeRooms.DoChest(S, M, X, Y, I, Sp),
                    }