"""
Light-toggle puzzles, yay
"""
from Utils import *
from Constants import *
import Screen
import Music
import BattleSprites
import ItemPanel
import Global
import Resources
import os
import time
import string
import Party
from BattleSprites import *
import math
import Critter
import Magic
import sys
import ChestScreen
import LightsOutPanel

class LightsPuzzleDefinition:
    def __init__(self, Name, Width, Height, MinimalMoves = 10):
        self.Name = Name
        self.Width = Width
        self.Height = Height
        self.InitialLights = {}
        for X in range(Width):
            for Y in range(Height):
                self.InitialLights[(X,Y)] = 0
        self.FilledRows = 0
        self.MinimalMoves = MinimalMoves
        self.Type = "Normal"
    def FillFromString(self, String):
        Bits = String.split(",")
        for Row in range(len(Bits)):
            Bit = Bits[Row]
            for Col in range(len(Bit)):
                if Bit[Col]=="X":
                    self.InitialLights[(Col, Row)] = 1
                if Bit[Col]=="G":
                    self.InitialLights[(Col, Row)] = 2
                    self.Type = "RGB"
                if Bit[Col]=="R":
                    self.InitialLights[(Col, Row)] = 1
                    self.Type = "RGB"

# This function is way too damn long.  Ah well.
def GetPuzzleDefinitions():
    PuzzleDefinitions = []
    Puzzle = LightsPuzzleDefinition("1", 5, 5, 6)
    Puzzle.FillFromString(".....,.....,X.X.X,.....,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("2", 5, 5, 6)
    Puzzle.FillFromString("X.X.X,X.X.X,.....,X.X.X,X.X.X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("3", 5, 5, 6)
    Puzzle.FillFromString(".X.X.,XX.XX,XX.XX,XX.XX,.X.X.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("4", 5, 5, 6)
    Puzzle.FillFromString(".....,XX.XX,.....,X...X,XX.XX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("5", 5, 5, 6)
    Puzzle.FillFromString("XXXX.,XXX.X,XXX.X,...XX,XX.XX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("6", 5, 5, 7)
    Puzzle.FillFromString(".....,.....,X.X.X,X.X.X,.XXX.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("7", 5, 5, 7)
    Puzzle.FillFromString("XXXX.,X...X,X...X,X...X,XXXX.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("8", 5, 5, 7)
    Puzzle.FillFromString(".....,..X..,.X.X.,X.X.X,.X.X.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("9", 5, 5, 7)
    Puzzle.FillFromString(".X.X.,XXXXX,.XXX.,.X.XX,XXX..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("10", 5, 5, 7)
    Puzzle.FillFromString(".XXX.,.XXX.,.XXX.,.....,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("11", 5, 5, 8)
    Puzzle.FillFromString("X.X.X,X.X.X,X.X.X,X.X.X,.XXX.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("12", 5, 5, 8)
    Puzzle.FillFromString("XXXXX,.X.X.,XX.XX,.XXX.,.X.X.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("13", 5, 5, 8)
    Puzzle.FillFromString("...X.,..X.X,.X.X.,X.X..,.X...,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("14", 5, 5, 8)
    Puzzle.FillFromString(".....,.....,.X...,.X...,.X...,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("15", 5, 5, 8)
    Puzzle.FillFromString(".....,.X...,.....,.X...,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("16", 5, 5, 9)
    Puzzle.FillFromString("X....,X....,X....,X....,XXXXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("17", 5, 5, 9)
    Puzzle.FillFromString(".....,.....,..X..,.XXX.,XXXXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("18", 5, 5, 9)
    Puzzle.FillFromString("..X..,.X.X.,X.X.X,.X.X.,..X..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("19", 5, 5, 9)
    Puzzle.FillFromString("X.X.X,.....,X.X.X,.....,X.X.X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("20", 5, 5, 9)
    Puzzle.FillFromString(".....,.....,X...X,.....,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("21", 5, 5, 10)
    Puzzle.FillFromString(".XXXX,.X...,.XXX.,.X...,.X...,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("22", 5, 5, 10)
    Puzzle.FillFromString(".XXX.,X...X,X...X,X...X,.XXX.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("23", 5, 5, 10)
    Puzzle.FillFromString(".....,.....,..XXX,..XX.,..X..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("24", 5, 5, 10)
    Puzzle.FillFromString(".....,.....,X...X,XXXXX,.X..X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("25", 5, 5, 10)
    Puzzle.FillFromString("X....,XX...,XXX..,XXXX.,.XXXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("26", 5, 5, 11)
    Puzzle.FillFromString("X...X,X...X,XXXXX,X...X,X...X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("27", 5, 5, 11)
    Puzzle.FillFromString("..X..,.XXX.,..X..,..X..,..X..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("28", 5, 5, 11)
    Puzzle.FillFromString(".....,.....,..XXX,..XXX,..XXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("29", 5, 5, 11)
    Puzzle.FillFromString(".....,.X...,.....,.....,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("30", 5, 5, 11)
    Puzzle.FillFromString(".....,.....,..X..,.....,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("31", 5, 5, 12)
    Puzzle.FillFromString("X...X,XX..X,X.X.X,X..XX,X...X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("32", 5, 5, 12)
    Puzzle.FillFromString("XXXXX,...X.,..X..,.X...,XXXXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("33", 5, 5, 12)
    Puzzle.FillFromString("...X.,...X.,X.X.X,X...X,X..XX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("34", 5, 5, 12)
    Puzzle.FillFromString("..X.X,X...X,X...X,.XX.X,.XXXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("35", 5, 5, 12)
    Puzzle.FillFromString("...XX,.X.X.,X...X,X.X.X,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("36", 5, 5, 13)
    Puzzle.FillFromString("..X..,.X.X.,X...X,XXXXX,X...X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("37", 5, 5, 13)
    Puzzle.FillFromString(".....,.XXX.,.XXX.,.XXX.,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("38", 5, 5, 13)
    Puzzle.FillFromString("X.X.X,.X.X.,X.X.X,.X.X.,X.X.X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("39", 5, 5, 13)
    Puzzle.FillFromString(".X.X.,X....,XX...,..XX.,.X.X.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("40", 5, 5, 13)
    Puzzle.FillFromString(".....,.....,.X.X.,.....,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("41", 5, 5, 14)
    Puzzle.FillFromString("X...X,.X.X.,..X..,..X..,..X..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("42", 5, 5, 14)
    Puzzle.FillFromString("XXX..,X..X.,XXX..,X..X.,XXX..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("43", 5, 5, 14)
    Puzzle.FillFromString("X...X,XX.X.,XXX..,.X...,.XXX.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("44", 5, 5, 14)
    Puzzle.FillFromString(".....,XX.XX,XXXXX,..X..,.XXX.,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("45", 5, 5, 14)
    Puzzle.FillFromString(".XXX.,X.X..,..XXX,XXXX.,X.X.X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("46", 5, 5, 15)
    Puzzle.FillFromString("..X..,.XXX.,XXXXX,.XXX.,..X..,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("47", 5, 5, 15)
    Puzzle.FillFromString("..X..,XXXXX,X.X..,.X..X,....X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("48", 5, 5, 15)
    Puzzle.FillFromString(".....,X...X,..X..,X...X,.....,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("49", 5, 5, 15)
    Puzzle.FillFromString("X...X,.X.X.,..X..,.X.X.,X...X,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("50", 5, 5, 15)
    Puzzle.FillFromString("XXXXX,XXXXX,XXXXX,XXXXX,XXXXX,")
    PuzzleDefinitions.append(Puzzle)
        
    Puzzle = LightsPuzzleDefinition("X 1", 5, 5, 5)
    Puzzle.FillFromString(".....,.....,.....,R.G.R,R.G.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 2", 5, 5, 5)
    Puzzle.FillFromString(".R...,RR...,..G..,...RR,...R.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 3", 5, 5, 5)
    Puzzle.FillFromString(".G...,GGRG.,.RRGG,....R,...R.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 4", 5, 5, 5)
    Puzzle.FillFromString("..G..,.G.G.,.....,GGGGG,.G.G.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 5", 5, 5, 5)
    Puzzle.FillFromString("RR...,RG...,GGG..,RG...,RR...,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 6", 5, 5, 6)
    Puzzle.FillFromString("RRR..,.RR..,.RRR.,..RR.,..RRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 7", 5, 5, 6)
    Puzzle.FillFromString(".R...,RRG..,.GRG.,..GRR,...R.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 8", 5, 5, 6)
    Puzzle.FillFromString("RGG..,GR...,R...G,GR.RG,RGRGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 9", 5, 5, 6)
    Puzzle.FillFromString(".GGG.,.G.G.,G.G.G,.G.G.,.GGG.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 10", 5, 5, 6)
    Puzzle.FillFromString(".....,.....,RG...,GRG..,RGR..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 11", 5, 5, 7)
    Puzzle.FillFromString("R.G.R,R...R,.RRR.,..R..,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 12", 5, 5, 7)
    Puzzle.FillFromString(".R...,R..G.,GG.GG,.G..R,...R.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 13", 5, 5, 7)
    Puzzle.FillFromString(".....,.....,RR...,R.R..,RRR..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 14", 5, 5, 7)
    Puzzle.FillFromString("RRRRR,.....,.R.R.,..R..,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 15", 5, 5, 7)
    Puzzle.FillFromString(".....,.....,G...G,.GGG.,..G..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 16", 5, 5, 8)
    Puzzle.FillFromString("RGRGR,GR.RG,R...R,GR.RG,RGRGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 17", 5, 5, 8)
    Puzzle.FillFromString(".RRR.,.RRR.,RRGRR,.RRR.,.RRR.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 18", 5, 5, 8)
    Puzzle.FillFromString(".GGG.,G...G,G.G.G,G...G,.GGG.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 19", 5, 5, 8)
    Puzzle.FillFromString("RRR..,..RG.,G.G.G,.GR..,..RRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 20", 5, 5, 8)
    Puzzle.FillFromString("RGR..,RGR..,.G...,RRRR.,.RRRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 21", 5, 5, 9)
    Puzzle.FillFromString("RGRGR,GRGRG,RGGGR,GRGRG,RGRGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 22", 5, 5, 9)
    Puzzle.FillFromString("R..G.,.....,.....,G....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 23", 5, 5, 9)
    Puzzle.FillFromString(".....,.....,R.G.R,.....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 24", 5, 5, 9)
    Puzzle.FillFromString("GRGRG,R.R.R,GRGRG,R.R.R,GRGRG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 25", 5, 5, 9)
    Puzzle.FillFromString("GGGGG,GGGGG,GGRGG,GGGGG,GRGRG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 26", 5, 5, 10)
    Puzzle.FillFromString("RGRGR,GRRRG,RRRRR,GRRRG,RGRGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 27", 5, 5, 10)
    Puzzle.FillFromString("RRRGG,RRRGG,RRRGG,RRRGG,RRRGG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 28", 5, 5, 10)
    Puzzle.FillFromString("R..R.,GRR.R,R..R.,GR.R.,RGRGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 29", 5, 5, 10)
    Puzzle.FillFromString("RGR..,RRRG.,G.R.G,.GRRR,..RGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 30", 5, 5, 10)
    Puzzle.FillFromString("..R..,G.G.G,RGRGR,G.G.G,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 31", 5, 5, 11)
    Puzzle.FillFromString(".R..R,RRGG.,.GGG.,.GGRR,R..R.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 32", 5, 5, 11)
    Puzzle.FillFromString(".GGG.,.....,R.R.R,.....,R.R.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 33", 5, 5, 11)
    Puzzle.FillFromString(".GGG.,.....,G...G,.....,R.R.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 34", 5, 5, 11)
    Puzzle.FillFromString(".RGRR,.RRGR,.G..R,...GR,..RGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 35", 5, 5, 11)
    Puzzle.FillFromString("GR.RG,GR.RG,GRGRG,GR.RG,GR.RG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 36", 5, 5, 12)
    Puzzle.FillFromString(".....,G.R.G,G.G.G,G.R.G,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 37", 5, 5, 12)
    Puzzle.FillFromString("RR.RR,.GR..,.RGGR,RRGGR,.R.R.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 38", 5, 5, 12)
    Puzzle.FillFromString("RGR..,RRGG.,GRGRG,.GGRR,..RGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 39", 5, 5, 12)
    Puzzle.FillFromString("..G..,..G..,.....,..R..,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 40", 5, 5, 12)
    Puzzle.FillFromString("..G..,.GGG.,RRRRR,GRRRG,GGRGG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 41", 5, 5, 13)
    Puzzle.FillFromString("G.R.G,.....,R.G.R,.....,G.R.G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 42", 5, 5, 13)
    Puzzle.FillFromString("R.G.R,..R..,GRGRG,..R..,R.G.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 43", 5, 5, 13)
    Puzzle.FillFromString(".....,.R...,..R..,.R...,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 44", 5, 5, 13)
    Puzzle.FillFromString("GGGRG,GGG.G,G.GG.,GRR.G,R...G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 45", 5, 5, 13)
    Puzzle.FillFromString("RRGRG,GRR.G,RGRR.,RRG.G,RRR.G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 46", 5, 5, 14)
    Puzzle.FillFromString("RGGGR,GRGRG,GGRGG,GRGRG,RGGGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 47", 5, 5, 14)
    Puzzle.FillFromString("..R..,.RRG.,...RR,RGR.R,GG.GG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 48", 5, 5, 14)
    Puzzle.FillFromString(".....,G.R.G,R.R.R,G.R.G,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 49", 5, 5, 14)
    Puzzle.FillFromString(".R...,.R...,..G..,...RR,R....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 50", 5, 5, 14)
    Puzzle.FillFromString(".RRR.,.RGR.,.RRR.,.RRR.,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 51", 5, 5, 15)
    Puzzle.FillFromString("..R..,G...G,G.R.G,G...G,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 52", 5, 5, 15)
    Puzzle.FillFromString("R.R.R,.....,R.G.R,.....,R.R.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 53", 5, 5, 15)
    Puzzle.FillFromString(".RRR.,.RRR.,RGGGR,RGGGR,RGGGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 54", 5, 5, 15)
    Puzzle.FillFromString("G...G,R...R,R...R,R...R,G...G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 55", 5, 5, 15)
    Puzzle.FillFromString(".G.G.,.....,G...G,.RRR.,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 56", 5, 5, 16)
    Puzzle.FillFromString("R.R.R,.....,R.R.R,.....,R.R.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 57", 5, 5, 16)
    Puzzle.FillFromString("RGGGR,RGGGR,RGGGR,RGGGR,RGGGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 58", 5, 5, 16)
    Puzzle.FillFromString(".....,.....,.RGR.,.....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 59", 5, 5, 16)
    Puzzle.FillFromString("..R..,GG.GG,.....,..R..,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 60", 5, 5, 16)
    Puzzle.FillFromString(".....,.....,G...G,.....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 61", 5, 5, 17)
    Puzzle.FillFromString(".G.G.,..G..,G...G,..G..,.G.G.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 62", 5, 5, 17)
    Puzzle.FillFromString(".....,.....,.GRG.,.....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 63", 5, 5, 17)
    Puzzle.FillFromString("RR...,RR...,RRG..,RR...,RR...,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 64", 5, 5, 17)
    Puzzle.FillFromString("R.R.R,.R.R.,R.R.R,.R.R.,R.R.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 65", 5, 5, 17)
    Puzzle.FillFromString("RRRRR,..R..,..R..,..R..,..G..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 66", 5, 5, 18)
    Puzzle.FillFromString("RRRRR,RGGGR,RGGGR,RGGGR,RRRRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 67", 5, 5, 18)
    Puzzle.FillFromString("RRRRR,RRRRR,RRRRR,RRRRR,RRRRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 68", 5, 5, 18)
    Puzzle.FillFromString(".....,.....,..R..,..R..,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 69", 5, 5, 18)
    Puzzle.FillFromString(".R.R.,.....,R...R,.RRR.,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 70", 5, 5, 18)
    Puzzle.FillFromString(".GGG.,..G..,..G..,..G..,.GGG.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 71", 5, 5, 19)
    Puzzle.FillFromString(".....,.....,.....,..R..,..R..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 72", 5, 5, 19)
    Puzzle.FillFromString(".....,.G.G.,RRRRR,..R..,.RRR.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 73", 5, 5, 19)
    Puzzle.FillFromString("G.G.G,.G.G.,G.G.G,.G.G.,G.G.G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 74", 5, 5, 19)
    Puzzle.FillFromString(".RRR.,.R.R.,.RRR.,.R.R.,.RRR.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 75", 5, 5, 19)
    Puzzle.FillFromString("RRR..,R....,RR...,R....,RRR..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 76", 5, 5, 20)
    Puzzle.FillFromString("R.R.R,.RRR.,RRRRR,.RRR.,R.R.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 77", 5, 5, 20)
    Puzzle.FillFromString("GGGRR,GGGRR,GGGRR,GGGRR,GGGRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 78", 5, 5, 20)
    Puzzle.FillFromString(".....,.....,G.G.G,.....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 79", 5, 5, 20)
    Puzzle.FillFromString(".G.G.,.R.R.,.G.G.,.R.R.,.G.G.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 80", 5, 5, 20)
    Puzzle.FillFromString("G...G,.....,.....,.....,G...G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 81", 5, 5, 21)
    Puzzle.FillFromString("GGGGG,GGGGG,GGGGG,GGGGG,GGGGG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 82", 5, 5, 21)
    Puzzle.FillFromString("R...R,.....,..R..,.....,R...R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 83", 5, 5, 21)
    Puzzle.FillFromString("RRRRR,RGRGR,RRGRR,RGRGR,RRRRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 84", 5, 5, 21)
    Puzzle.FillFromString(".....,G.G.G,GGGGG,G.G.G,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 85", 5, 5, 21)
    Puzzle.FillFromString(".G...,.R...,.G...,.R.R.,.G.G.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 86", 5, 5, 22)
    Puzzle.FillFromString("GGGGG,GGGGG,GGRGG,GGGGG,GGGGG,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 87", 5, 5, 22)
    Puzzle.FillFromString(".....,.....,.....,.....,R.G.R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 88", 5, 5, 22)
    Puzzle.FillFromString(".....,.....,GG.GG,.....,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 89", 5, 5, 22)
    Puzzle.FillFromString("G.G.G,.GGG.,..R..,.....,G...G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 90", 5, 5, 22)
    Puzzle.FillFromString("GG.RR,GG.RR,GGGGG,GGGRR,GGGRR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 91", 5, 5, 23)
    Puzzle.FillFromString(".....,G...G,G...G,G...G,.....,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 92", 5, 5, 23)
    Puzzle.FillFromString("GGG..,G....,GG...,G....,GGG..,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 93", 5, 5, 23)
    Puzzle.FillFromString("RGRGR,GRGRG,RG.GR,GRGRG,RGRGR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 94", 5, 5, 23)
    Puzzle.FillFromString("GRRRG,R.RGG,R..RG,GRGGR,RR.RR,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 95", 5, 5, 23)
    Puzzle.FillFromString("GRGRG,G.G.G,G.G.G,GGGGG,G.G.G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 96", 5, 5, 24)
    Puzzle.FillFromString("..GGG,..R.R,RGRR.,.GR.G,.G..R,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 97", 5, 5, 24)
    Puzzle.FillFromString("GGR..,.GRRG,G...G,RR.RG,GRGG.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 98", 5, 5, 24)
    Puzzle.FillFromString("G.G..,G..G.,RRGR.,G..RG,RRGG.,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 99", 5, 5, 24)
    Puzzle.FillFromString("GGRGG,.GRG.,G.R.G,.GGG.,G.G.G,")
    PuzzleDefinitions.append(Puzzle)

    Puzzle = LightsPuzzleDefinition("X 100", 5, 5, 24)
    Puzzle.FillFromString("R.G.R,GRGRG,G.R.G,.....,G...G,")
    PuzzleDefinitions.append(Puzzle)
    return PuzzleDefinitions
PuzzleDefinitions = GetPuzzleDefinitions()

def GetPuzzleDefinition(Name):
    for Puzzle in PuzzleDefinitions:
        if Puzzle.Name.lower() == Name.lower():
            return Puzzle
    return None

class BlinkenScreen(Screen.TendrilsScreen):
    "Blinkenlights screen"
    def __init__(self, App, PuzzleName = None):
        Screen.TendrilsScreen.__init__(self,App)
        if not PuzzleName:
            PuzzleName = Global.MemoryCard.Get("CurrentBlinkenPuzzle", "1")
        self.LightsOutPanel = None
        self.SongY = 420
        self.MoveCount = 0
        self.Puzzle = GetPuzzleDefinition(PuzzleName)
        self.ButtonSprites = pygame.sprite.Group()
        self.DescriptionSprites = pygame.sprite.Group()
        self.RenderBackground()
        self.BuildPuzzle()
        self.LoadPuzzle()
        self.DrawDescriptionSprites()
        self.LastClickTime = 0
        
        #self.PlaySong()
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        self.PlaySong()
    def PlaySong(self):
        Song = Global.MusicLibrary.GetBlockSong()
        self.SummonSong(Song)
    def SavePuzzle(self):
        "Save the current state"
        PuzzleState = (self.MoveCount, self.LightsOutPanel.GetPuzzleState())
        # If we're in free-play mode, save on the MEMORY CARD:
        Global.MemoryCard.Set("LightPuzzle:%s"%self.Puzzle.Name, PuzzleState)
    def LoadPuzzle(self):
        "Load saved puzzle-state, if any"
        State = Global.MemoryCard.Get("LightPuzzle:%s"%self.Puzzle.Name)
        if State:
            self.MoveCount = State[0]
            Grid = State[1]
            for (X,Y) in Grid.keys():
                self.LightsOutPanel.lock.setLight(1 + Y*self.Puzzle.Width + X, Grid[(X,Y)])
        self.UpdateMoveCountSprite()
        self.LightsOutPanel.UpdateLightsFromGrid()
    def BuildPuzzle(self):
        Global.MemoryCard.Set("CurrentPegPuzzle", self.Puzzle.Name)
        if self.LightsOutPanel:
            self.LightsOutPanel.kill()
        self.LightsOutPanel = LightsOutPanel.PlayingBoard(self, 50, 100,
                                                          600, 400, self.Puzzle)
        self.SubPanes = [self.LightsOutPanel]
        self.MoveCount = 0
        self.UpdateMoveCountSprite()
    def PuzzleSolved(self):
        Music.PauseSong()
        Resources.PlayStandardSound("TodHappy.wav")
        Key = "BlinkenlightsPuzzleSolved:%s"%self.Puzzle.Name
        OldMoveCount = Global.MemoryCard.Get(Key, None)
        if OldMoveCount!=None:
            NewMoveCount = min(OldMoveCount, self.MoveCount)
        else:
            NewMoveCount = self.MoveCount
        if (OldMoveCount==None or NewMoveCount < OldMoveCount):
            Global.MemoryCard.Set(Key, self.MoveCount)
        Str = "You have solved the puzzle!\nYou used <CN:BRIGHTGREEN>%d</c> moves."%self.MoveCount
        if self.MoveCount <= self.Puzzle.MinimalMoves:
            Str += "\n<CN:ORANGE>OPTIMAL SOLUTION!</C>"
        self.ResetPuzzle(1)
        self.DrawDescriptionSprites()
        Global.App.ShowNewDialog(Str, Callback = Music.UnpauseSong)
    def RenderBackground(self):
        "Called once, up-front."
        TileNumber = Resources.Tiles.get("Puzzle", 1)
        Image = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber))
        Surface = GetTiledImage(800, 600, Image)
        BackSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(BackSprite)
        #######################################
        Sprite = GenericTextSprite("Puzzle:", 680, 50, Colors.LightGrey, FontSize=24)
        self.AddBackgroundSprite(Sprite)
        #
        self.MoveCountSprite = GenericTextSprite("Moves: 0", 680, 100, Colors.Green, FontSize = 24)
        self.AddForegroundSprite(self.MoveCountSprite)
        #
        Sprite = BoxSprite(49, 99, 602, 402)
        self.AddBackgroundSprite(Sprite)
        #
        Image = FancyAssBoxedText("Help", HighlightIndex = 0)
        HelpButton = GenericImageSprite(Image, 730, 440)
        HelpButton.Command = "Help"
        self.AddBackgroundSprite(HelpButton)
        self.ButtonSprites.add(HelpButton)
        ###
        Image = FancyAssBoxedText("Reset", HighlightIndex = 0)
        ResetButton = GenericImageSprite(Image, 730, 480)
        ResetButton.Command = "Reset"
        self.AddBackgroundSprite(ResetButton)
        self.ButtonSprites.add(ResetButton)
        ###
        Image = FancyAssBoxedText("Quit for now!", HighlightIndex = 0)
        Button = GenericImageSprite(Image, 650, 560)
        Button.rect.right = ResetButton.rect.right
        Button.Command = "Stop"
        self.AddBackgroundSprite(Button)
        self.ButtonSprites.add(Button)
        ###
        Button = FancyAssBoxedSprite("Back x10", 198, 520)
        Button.Command = "Back x10"
        self.AddBackgroundSprite(Button)
        self.ButtonSprites.add(Button)
        Button = FancyAssBoxedSprite("Back", 300, 520)
        Button.Command = "Back"
        self.AddBackgroundSprite(Button)
        self.ButtonSprites.add(Button)
        Button = FancyAssBoxedSprite("Next", 370, 520)
        Button.Command = "Next"
        self.AddBackgroundSprite(Button)
        self.ButtonSprites.add(Button)
        Button = FancyAssBoxedSprite("Next x10", 440, 520)
        Button.Command = "Next x10"
        self.AddBackgroundSprite(Button)
        self.ButtonSprites.add(Button)
        
    def HandleKeyPressed(self, Key):
        # Debug key: Check that things are up-to-date:
        if Key == Keystrokes.Debug:
            self.PuzzleSolved()
            return
        if Key == pygame.K_ESCAPE:
            pass
        if Key == 113: # Q is for Quit
            self.SavePuzzle()
            self.App.PopScreen(self)
            return
        if Key == 114: # R is for Reset
            self.ResetPuzzle()
            return
        if Key == ord("h"):
            self.ClickHelp()
    def ResetPuzzle(self, Silent = 0):
        if not Silent:
            Resources.PlayStandardSound("Turn Undead.wav")
        self.BuildPuzzle()
        self.Redraw()
    def DrawDescriptionSprites(self):
        "Show extra info about the puzzle."
        for Sprite in self.DescriptionSprites.sprites():
            Sprite.kill()
        Sprite = GenericTextSprite("%s"%self.Puzzle.Name, 705, 70, FontSize=24)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        Key = "BlinkenlightsPuzzleSolved:%s"%self.Puzzle.Name
        MovesUsed = Global.MemoryCard.Get(Key, None)
        if MovesUsed==None:
            Str = "<CN:ORANGE>Unsolved</C>"
        else:
            if MovesUsed <= self.Puzzle.MinimalMoves:
                Optimal = "\n<CN:BRIGHTBLUE>Optimal!"
            else:
                Optimal = ""
            Str = "Best Solution:\n<CN:GREEN>%s</C> moves%s"%(MovesUsed, Optimal)
        Image = TaggedRenderer.RenderToImage(Str, FontSize = 24)
        Sprite = GenericImageSprite(Image, 670, 150)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
    def NextPuzzle(self, Dir = 1):
        self.SavePuzzle()
        Index = PuzzleDefinitions.index(self.Puzzle)
        Index = (Index + Dir)
        if Index >= len(PuzzleDefinitions):
            Index -= len(PuzzleDefinitions)
        elif Index < 0:
            Index += len(PuzzleDefinitions)
            #Index = len(PuzzleDefinitions) - 1
        self.Puzzle = PuzzleDefinitions[Index]
        self.BuildPuzzle()
        self.LoadPuzzle()
        self.DrawDescriptionSprites()
        self.Redraw()
    def HandleMouseClicked(self,Position,Button):
        for SubPane in self.SubPanes:
            SubPosition = SubPane.GetLocalPosition(Position)
            if SubPosition:
                MoveFlag = SubPane.HandleMouseClickedHere(SubPosition,Button)
                if MoveFlag:
                    self.MoveCount += 1
                    self.UpdateMoveCountSprite()
                    if self.LightsOutPanel.IsDisarmed():
                        self.PuzzleSolved()
                    
        self.HandleMouseClickedHere(Position,Button)
    def UpdateMoveCountSprite(self):
        self.MoveCountSprite.ReplaceText("Moves: %s"%self.MoveCount)
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for buttons:
        Sprite = pygame.sprite.spritecollideany(Dummy, self.ButtonSprites)
        if Sprite:
            if Sprite.Command == "Stop":
                self.SavePuzzle()
                self.App.PopScreen(self)
                return
            elif Sprite.Command == "Reset":
                self.ResetPuzzle()
                return
            elif Sprite.Command == "Help":
                self.ClickHelp()
            elif Sprite.Command == "Next":
                self.NextPuzzle()
                return
            elif Sprite.Command == "Next x10":
                self.NextPuzzle(10)
                return
            elif Sprite.Command == "Back":
                self.NextPuzzle(-1)
                return
            elif Sprite.Command == "Back x10":
                self.NextPuzzle(-10)
                return
    def ClickHelp(self):
        HelpText = """<CENTER><CN:YELLOW>Blinkenlights</c>
        
Click a light to flip it on or off.  The adjacent lights will also togle. \
The object of the game is to turn <CN:BRIGHTGREEN>all lights green</c>.  Can \
you do it?  And...how many moves do you need?"""
        Global.App.ShowNewDialog(HelpText)
