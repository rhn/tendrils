"""
Code to support sliding block puzzles.  Here's how I define "sliding block puzzle":
- The puzzle is laid out on a GRID.  There are only finitely many LIVE SQUARES; the
  rest of the universe is DEAD SQUARES (pieces can never move into these; they are 'off the world'.
- Each PIECE is made of one or more contiguous (that means horizontally and vertically, not merely
  diagonally) blocks; pieces may slide up, down, left or right a square at a time, provided there
  are no dead squares or other pieces blocking the way.
- The object is to move one or more pieces to a desired ENDING configuration.  Sometimes, several
  pieces are interchangable (all in one "piece class") - e.g. some red squares and some blue squares.
There are many, many sliding block puzzles out there.  "Argh.exe" is the first one I encountered.  Some
date from the early 20th century (if not earlier).

Interface: Create a BlockSprite for every block.  (Draw the background, too).  A BlockSprite can be dragged
with the mouse, or the user can press its letter (possibly followed by an arrow key).

This code is designed for Tendrils, but if you just plain like sliding
block puzzles...hey, feel free to use it on its own!
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

# Here are some sliding block puzzles, with their sources.
# These were taken from Nick Baxter's webpage at www.johnrausch.com - if you like
# sliding block puzzles, you can find many more there!

Shape2x2 = {(0,0):1, (1,0):1, (0,1):1, (1,1):1}
Shape1x1 = {(0,0):1}
Shape2x1 = {(0,0):1, (1,0):1}
Shape1x2 = {(0,0):1, (0,1):1}
ShapeT = {(1,0):1, (0,1):1, (1,1):1, (2,1):1}

class PuzzleDefinition:
    def __init__(self, Name, Author, Width, Height, Instructions):
        self.Name = Name
        self.Author = Author
        self.Instructions = Instructions
        self.VictoryConditions = []
        self.Blocks = None
        self.Width = Width
        self.Height = Height

NamesToPuzzles = {}
MasterPuzzleList = []
# Hughes puzzle - 21 moves.
Puzzle = PuzzleDefinition("Hughes", "", 3, 4, "Move the red block (A) to the bottom right.")
Puzzle.Blocks = (
        ("A", 0, 0, Shape1x2, Colors.Red),
        ("1", 2, 0, Shape1x1, Colors.LightGrey),
        ("2", 2, 1, Shape1x1, Colors.LightGrey),
        ("3", 1, 2, Shape2x1, Colors.LightGrey),
        ("4", 2, 3, Shape1x1, Colors.LightGrey),
        ("5", 0, 3, Shape2x1, Colors.LightGrey),
        ("6", 0, 2, Shape1x1, Colors.LightGrey),
    )
Puzzle.VictoryConditions = (("A", 2, 2),)
NamesToPuzzles[Puzzle.Name] = Puzzle
MasterPuzzleList.append(Puzzle)
# Moving Day puzzle - 17 moves.
Puzzle = PuzzleDefinition("Moving Day", "Sam Loyd", 3, 2, "Interchange pieces A and B")
Puzzle.Blocks = (
        ("A", 2, 0, Shape1x1, Colors.Red),
        ("B", 2, 1, Shape1x1, Colors.Green),
        ("1", 0, 0, Shape1x1, Colors.LightGrey),
        ("2", 0, 1, Shape1x1, Colors.LightGrey),
        ("3", 1, 1, Shape1x1, Colors.LightGrey),
    )
Puzzle.VictoryConditions = (("A", 2, 1),("B",2,0))
NamesToPuzzles[Puzzle.Name] = Puzzle
MasterPuzzleList.append(Puzzle)

# Traffic Cop Tangle - 10 block puzzle by A. Filipiak, 1942 (47 moves)
TrafficCop = PuzzleDefinition("Traffic Cop", "A.Filipiak", 4, 5, "Move the red block (A) to the BOTTOM left, and the green block (B) to the TOP left")
TrafficCop.Blocks = (
        ("A", 0, 0, Shape2x2, Colors.Red),
        ("B", 0, 3, Shape2x2, Colors.Green),
        ("1", 2, 0, Shape1x1, Colors.LightGrey),
        ("2", 3, 0, Shape1x1, Colors.LightGrey),
        ("3", 2, 1, Shape2x1, Colors.Blue),
        ("4", 2, 2, Shape1x1, Colors.LightGrey),
        ("5", 3, 2, Shape1x1, Colors.LightGrey),
        ("6", 2, 3, Shape2x1, Colors.Blue),
        ("7", 2, 4, Shape1x1, Colors.LightGrey),
        ("8", 3, 4, Shape1x1, Colors.LightGrey),
        )
TrafficCop.VictoryConditions = (("A", 0, 3),("B", 0, 0))
NamesToPuzzles[TrafficCop.Name] = TrafficCop
MasterPuzzleList.append(TrafficCop)

# Blockado - Acme Novelty, 1928 - 74 moves!
Blockado = PuzzleDefinition("Blockado", "Acme Novelty", 4, 6, "Move the red block (A) to the bottom left.")
Blockado.Blocks = (
    ("A", 0, 0, Shape2x2, Colors.Red),
    ("1", 2, 0, Shape2x1, Colors.LightGrey),
    ("2", 2, 1, Shape2x1, Colors.LightGrey),
    ("3", 2, 2, Shape2x1, Colors.LightGrey),
    ("6", 2, 3, Shape2x1, Colors.LightGrey),
    ("7", 2, 4, Shape2x1, Colors.LightGrey),
    ("0", 2, 5, Shape2x1, Colors.LightGrey),
    ("4", 0, 3, Shape1x2, Colors.LightGrey),
    ("5", 1, 3, Shape1x2, Colors.LightGrey),
    ("8", 0, 5, Shape1x1, Colors.LightGrey),
    ("9", 1, 5, Shape1x1, Colors.LightGrey),
    )
Blockado.VictoryConditions = (("A", 0, 4),)
NamesToPuzzles[Blockado.Name] = Blockado
MasterPuzzleList.append(Blockado)

# VERY HARD one:
# Supercompo, by Junk Kato - 123 moves!
Supercompo = PuzzleDefinition("Supercompo", "Junk Kato", 4, 5, "Move the red block (A) to the bottom center.")
Supercompo.Blocks = (
    ("A", 1, 0, Shape2x2, Colors.Red),
    ("1", 0, 1, Shape1x1, Colors.LightGrey),
    ("2", 3, 1, Shape1x1, Colors.LightGrey),
    ("3", 0, 2, Shape1x2, Colors.LightGrey),
    ("4", 3, 2, Shape1x2, Colors.LightGrey),
    ("5", 1, 2, Shape2x1, Colors.LightGrey),
    ("6", 1, 3, Shape2x1, Colors.LightGrey),
    ("7", 1, 4, Shape2x1, Colors.LightGrey),
    ("8", 0, 4, Shape1x1, Colors.LightGrey),
    ("9", 3, 4, Shape1x1, Colors.LightGrey),
    )
Supercompo.VictoryConditions = (("A", 1, 3),)
NamesToPuzzles[Supercompo.Name] = Supercompo
MasterPuzzleList.append(Supercompo)
##############
Puzzle = PuzzleDefinition("T-zer", "N.Yoshigahara", 6, 5, "Interchange the T-shaped blocks (move X to the right, Y to the left).")
Puzzle.Blocks = (
    ("X", 0, 0, ShapeT, Colors.Red),
    ("Y", 3, 0, ShapeT, Colors.Green),
    ("A", 0, 3, Shape2x1, Colors.LightGrey),
    ("C", 0, 4, Shape2x1, Colors.LightGrey),
    ("B", 4, 3, Shape2x1, Colors.LightGrey),
    ("D", 4, 4, Shape2x1, Colors.LightGrey),
    ("E", 2, 3, Shape1x1, Colors.LightGrey),
    ("F", 3, 3, Shape1x1, Colors.LightGrey),
    ("G", 2, 4, Shape1x1, Colors.LightGrey),
    ("H", 3, 4, Shape1x1, Colors.LightGrey),
    )
Puzzle.VictoryConditions = (("X",3,0), ("Y", 0, 0))
NamesToPuzzles[Puzzle.Name] = Puzzle
MasterPuzzleList.append(Puzzle)
##############
Puzzle = PuzzleDefinition("Pennant", "L. W. Hardy", 4, 5, "Move the red block (A) to the lower left.")
Puzzle.Blocks = (
    ("A", 0, 0, Shape2x2, Colors.Red),
    ("1", 2, 0, Shape2x1, Colors.LightGrey),
    ("2", 2, 1, Shape2x1, Colors.LightGrey),
    ("3", 2, 3, Shape2x1, Colors.LightGrey),
    ("4", 2, 4, Shape2x1, Colors.LightGrey),
    ("5", 1, 3, Shape1x2, Colors.LightGrey),
    ("6", 0, 3, Shape1x2, Colors.LightGrey),
    ("7", 0, 2, Shape1x1, Colors.LightGrey),
    ("8", 1, 2, Shape1x1, Colors.LightGrey),
    )
Puzzle.VictoryConditions = (("A",0,3),)
NamesToPuzzles[Puzzle.Name] = Puzzle
MasterPuzzleList.append(Puzzle)
##############
Puzzle = PuzzleDefinition("Century", "John Conway", 4, 5, "Move the red block (A) to the bottom center.")
Puzzle.Blocks = (
    ("A", 1, 0, Shape2x2, Colors.Red),
    ("1", 0, 0, Shape1x1, Colors.LightGrey),
    ("2", 3, 0, Shape1x1, Colors.LightGrey),
    ("3", 0, 1, Shape1x2, Colors.Blue),
    ("4", 3, 1, Shape1x2, Colors.Blue),
    ("5", 1, 2, Shape1x2, Colors.Blue),
    ("6", 0, 3, Shape1x1, Colors.LightGrey),
    ("7", 3, 3, Shape1x1, Colors.LightGrey),
    ("8", 0, 4, Shape2x1, Colors.Green),
    ("9", 2, 4, Shape2x1, Colors.Green),
    )
Puzzle.VictoryConditions = (("A",1,3),)
NamesToPuzzles[Puzzle.Name] = Puzzle
MasterPuzzleList.append(Puzzle)



class Square:
    "A space in the sliding block grid."
    #Full = 2 # Currently occupied
    # If full: a reference to the BlockSprite
    Empty = 1 # Alive!
    Dead = 0 # nothing ever moves here

# Size of a GameGrid square, on screen:
GridWidth = 100
GridHeight = 100
    
class GameGridClass:
    def __init__(self, Width, Height):
        global GridWidth
        global GridHeight
        self.Width = Width
        self.Height = Height
        Size = 500 / Height
        Size = min(Size, 600 / Width)
        GridWidth = Size
        GridHeight = Size
        self.PadX = (800 - self.Width * GridWidth) / 2
        self.PadY = (600 - self.Height * GridHeight) / 2
        self.Grid = {}
        self.Blocks = []
        for X in range(Width):
            for Y in range(Height):
                self.Grid[(X, Y)] = Square.Empty
    def GetContents(self, X, Y):
        if X<0 or X>self.Width:
            return Square.Dead
        if Y<0 or Y>self.Height:
            return Square.Dead
        return self.Grid.get((X, Y), Square.Dead)
    def GetCuteName(self, X, Y):
        Contents = self.GetContents(X, Y)
        if isinstance(Contents, BlockSprite):
            return Contents.Name[:1]
        else:
            return Contents
    def GetScreenX(self, X):
        return X * GridWidth + self.PadX
    def GetScreenY(self, Y):
        return Y * GridHeight + self.PadY
    def RemovePiece(self, MovePiece):
        for (Position, Piece) in self.Grid.items():
            if Piece == MovePiece:
                self.Grid[Position] = Square.Empty
    def PlacePiece(self, Piece, X, Y):
        for (SquareX, SquareY) in Piece.Shape.keys():
            PlaceX = X + SquareX
            PlaceY = Y + SquareY
            Contents = self.GetContents(PlaceX, PlaceY)
            if Contents!=Square.Empty:
                print "** WARNING!  The %s, %s Piece of %s (placed at %s, %s) hitting non-empty square at (%d, %d)"%(SquareX, SquareY, Piece.Name, X, Y, PlaceX, PlaceY)
                print "%s + %s = %s"%(X, SquareX, PlaceX)
                print "%s + %s = %s"%(Y, SquareY, PlaceY)
            self.Grid[(PlaceX, PlaceY)] = Piece
        if hasattr(Piece, "rect"):
            Piece.rect.top = self.GetScreenY(Y)
            Piece.rect.left = self.GetScreenX(X)
    def IsSolved(self):
        return 0            
    def FindBlock(self, Name):
        for Block in self.Blocks:
            if Block.Name.lower() == Name.lower():
                return Block
            
GameGrid = None # global variable

XDir = (0,0,0,-1,1)
YDir = (0,-1,1,0,0)
    
class BlockSprite(GenericImageSprite):
    """
    Constructor gives the shape as a dictionary, the color for display, and the initial X and Y of the
    "center" square.
    Shape dictionary example:
    
    Xx - {(0,0):1, (1,0):1, (0,1):1, (1,1):1}
    xx  
    
    """
    def __init__(self, Name, GameGrid, X, Y, Shape = None, Color = None):
        if not Shape:
            Shape = {(0,0):1}
        if not Color:
            Color = Colors.White
        self.GameGrid = GameGrid
        self.GameGrid.Blocks.append(self)
        
        self.Shape = Shape
        self.Color = Color
        self.X = X
        self.Y = Y
        self.Name = Name # Names are for the keyboard interface, and for saving/loading!
        Image = self.GetImage()
        self.GameGrid.PlacePiece(self, X, Y)
        GenericImageSprite.__init__(self, Image, self.GameGrid.GetScreenX(X), self.GameGrid.GetScreenY(Y))
    def GetImage(self):
        # First, figure how big it should be:
        Height = 1
        Width = 1
        for (X, Y) in self.Shape.keys():
            Width = max(Width, X+1)
            Height = max(Height, Y+1)
        Image = pygame.Surface((Width * GridWidth, Height * GridHeight))
        # Now, draw ourselves:
        for (X, Y) in self.Shape.keys():
            RectX = X * GridWidth
            RectY = Y * GridHeight
            pygame.draw.rect(Image, self.Color, (RectX+5, RectY+5, GridWidth-10, GridHeight-10), 0)
            if self.Shape.has_key((X-1, Y)):
                pygame.draw.rect(Image, self.Color, (RectX, RectY + 5, 10, GridHeight-10))
            if self.Shape.has_key((X+1, Y)):
                pygame.draw.rect(Image, self.Color, (RectX + GridWidth-10, RectY + 5, 10, GridHeight - 10))
            if self.Shape.has_key((X, Y-1)):
                pygame.draw.rect(Image, self.Color, (RectX + 5, RectY, GridWidth - 10, 10))
            if self.Shape.has_key((X, Y+1)):
                pygame.draw.rect(Image, self.Color, (RectX + 5, Y + GridHeight - 10, GridWidth - 10, 10))
##            # And corners, too!
##            if self.Shape.has_key((X-1, Y-1)):
##                pygame.draw.rect(Image, self.Color, (RectX, RectY + 5, 10, GridHeight-10))
            #pygame.draw.rect(Image, Colors.Yellow, (RectX, RectY, GridWidth, GridHeight), 1)
        # A quick HACK to draw the missing "corners" at the center of a 2x2:
        if self.Shape.has_key((1,1)) and self.Shape.has_key((0,0)):
            pygame.draw.rect(Image, self.Color, (GridWidth-10, GridHeight-10, 20, 20))
        SubImage = TextImage(self.Name, FontSize = 32)
        BlitX = Image.get_rect().center[0] - SubImage.get_rect().width / 2
        BlitY = Image.get_rect().center[1] - SubImage.get_rect().height / 2
        Image.blit(SubImage, (BlitX, BlitY))
        return Image
    def CanMove(self, Direction):
        for (SquareX, SquareY) in self.Shape.keys():
            X = self.X + SquareX + XDir[Direction]
            Y = self.Y + SquareY + YDir[Direction]
            Contents = self.GameGrid.GetContents(X, Y)
            if Contents!=self and Contents!=Square.Empty:
                return 0
        return 1 # all clear!
    def Move(self, Direction):
        self.GameGrid.RemovePiece(self)
        self.X += XDir[Direction]
        self.Y += YDir[Direction]
        self.rect.left = self.GameGrid.GetScreenX(self.X)
        self.rect.top = self.GameGrid.GetScreenY(self.Y)
        self.GameGrid.PlacePiece(self, self.X, self.Y)
    def GetLegalMoves(self):
        Dirs = []
        for Direction in (Directions.Up, Directions.Down, Directions.Left, Directions.Right):
            if self.CanMove(Direction):
                Dirs.append(Direction)
        return Dirs

class BlockScreen(Screen.TendrilsScreen):
    "A sliding-block-puzzle screen."
    def __init__(self, App, PuzzleName = None, SolveCallback = None, FreePlay = 0):
        Screen.TendrilsScreen.__init__(self,App)
        if not PuzzleName:
            PuzzleName = Global.MemoryCard.Get("CurrentSlidingBlockPuzzle", "Hughes")
        self.SongY = 510
        self.GameGrid = None
        self.MoveCountSprite = None
        self.FreePlay = FreePlay
        self.PuzzleName = PuzzleName
        self.BlockSprites = pygame.sprite.Group()
        self.ButtonSprites = pygame.sprite.Group()
        self.ActiveBlock = None
        self.DragStart = None
        self.SolveCallback = SolveCallback
        self.AllowedMoveSprites = []
        self.PuzzleSprites = []
        self.DescriptionSprites = pygame.sprite.Group()
        self.BuildPuzzle()
        self.LoadPuzzle()
        self.RenderBackground()
        self.PlaySong()
    def PlaySong(self):
        Song = Global.MusicLibrary.GetBlockSong()
        self.SummonSong(Song)
    def SavePuzzle(self):
        BlockTuples = []
        for Block in self.GameGrid.Blocks:
            BlockTuples.append((Block.Name, Block.X, Block.Y))
        PuzzleState = (self.MoveCount, BlockTuples)
        # If we're in free-play mode, save on the MEMORY CARD:
        if self.FreePlay:
            Global.MemoryCard.Set("BlockPuzzle:%s"%self.PuzzleName, PuzzleState)
        else:
            Global.Party.EventFlags["BlockPuzzle%s"%self.PuzzleName] = PuzzleState
    def LoadPuzzle(self):
        "Load saved puzzle-state, if any"
        if self.FreePlay:
            State = Global.MemoryCard.Get("BlockPuzzle:%s"%self.PuzzleName)
        else:
            State = Global.Party.EventFlags.get("BlockPuzzle%s"%self.PuzzleName, None)
        if State==None:
            self.MoveCount = 0
            return
        for Block in self.GameGrid.Blocks:
            self.GameGrid.RemovePiece(Block)
        # Legacy savegames have no movecount %%%
        if type(State[0])!=type(1):
            self.MoveCount = 0
            BlockTuples = State
        else:
            self.MoveCount = State[0]
            BlockTuples = State[1]
        if self.MoveCountSprite:
            self.MoveCountSprite.ReplaceText(self.MoveCount)
        for Tuple in BlockTuples:
            Name = Tuple[0]
            X = Tuple[1]
            Y = Tuple[2]
            Block = self.GameGrid.FindBlock(Name)
            Block.X = X
            Block.Y = Y
            self.GameGrid.PlacePiece(Block, X, Y)
    def AddBlock(self, Name, X, Y, Shape, Color):
        Block = BlockSprite(Name, self.GameGrid, X, Y, Shape, Color)
        self.AddBackgroundSprite(Block)
        self.BlockSprites.add(Block)
    def BuildPuzzle(self):
        self.MoveCount = 0
        if self.MoveCountSprite:
            self.MoveCountSprite.ReplaceText(self.MoveCount)
        for Sprite in self.BlockSprites.sprites():
            Sprite.kill()
        for Sprite in self.AllowedMoveSprites:
            Sprite.kill()
        self.Puzzle = NamesToPuzzles.get(self.PuzzleName)
        Global.MemoryCard.Set("CurrentSlidingBlockPuzzle", self.Puzzle.Name)
        self.GameGrid = GameGridClass(self.Puzzle.Width, self.Puzzle.Height)
        self.RenderPuzzleBackground()
        for BlockDefinition in self.Puzzle.Blocks:
            self.AddBlock(*BlockDefinition)
    def CheckVictory(self):
        for (Name, X, Y) in self.Puzzle.VictoryConditions:
            Block = self.GameGrid.FindBlock(Name)
            if Block.X !=X or Block.Y != Y:
                return
        # Yay!
        self.Redraw()
        self.PuzzleSolved()
    def PuzzleSolved(self):
        # Default name for 'solver'
        Music.FadeOut()
        Resources.PlayStandardSound("cvfury.wav")        
        if self.FreePlay:
            Name = "Player"
        else:
            Name = Global.Party.Players[2].Name
        # Check old score:
        Key = "SlidingBlockHiscore:%s"%self.Puzzle.Name
        OldScore = Global.MemoryCard.Get(Key)
        if OldScore:
            BestMoves = OldScore[0]
        else:
            BestMoves = None
        if (BestMoves == None or self.MoveCount < BestMoves):
            Global.MemoryCard.Set(Key, (self.MoveCount, Name))
        if not self.SolveCallback:
            # Free play:
            MoveCount = self.MoveCount
            self.ResetPuzzle(1)
            if BestMoves!=None and MoveCount >= BestMoves:
                Str = "You have solved the puzzle!\n\nYou didn't beat the record of <CN:PURPLE>%d</C> moves."%BestMoves
                Global.App.ShowNewDialog(Str, Callback = self.HiScoreNameEntry)
            else:
                Str = "You have solved the puzzle!\n\nEnter your name:"
                Global.App.ShowWordEntryDialog(Str, self.HiScoreNameEntry)
            return
        else:
            apply(self.SolveCallback)
            Global.App.PopScreen(self)
    def HiScoreNameEntry(self, Name = None):
        if Name:
            Key = "SlidingBlockHiscore:%s"%self.Puzzle.Name
            Score = list(Global.MemoryCard.Get(Key))
            Score[1] = Name
            Global.MemoryCard.Set(Key, tuple(Score))
        self.PlaySong()
        self.DrawDescriptionSprites()
        self.Redraw()
    def RenderPuzzleBackground(self):
        "Called when the puzzle changes."
        # Want to draw lines around the puzzle's edge:
        for Sprite in self.PuzzleSprites:
            Sprite.kill()
        Sprite = BoxSprite(self.GameGrid.GetScreenX(0), self.GameGrid.GetScreenY(0),
                           GridWidth * self.GameGrid.Width, GridHeight * self.GameGrid.Height)
        # Show the DEAD squares:
        DeadImage = pygame.Surface((GridWidth, GridHeight))
        DeadImage.fill(Colors.Grey)
        for X in range(self.GameGrid.Width):
            for Y in range(self.GameGrid.Height):
                Contents = self.GameGrid.GetContents(X, Y)
                if Contents == Square.Dead:
                    Sprite = GenericImageSprite(DeadImage, self.GameGrid.GetScreenX(X), self.GameGrid.GetScreenY(Y))
                    self.AddBackgroundSprite(Sprite)
                    self.PuzzleSprites.append(Sprite)
        Sprite.image.set_colorkey(Colors.Black)
        self.AddBackgroundSprite(Sprite)
        self.PuzzleSprites.append(Sprite)
        Sprite = GenericTextSprite(self.Puzzle.Instructions, 0, 600, Colors.Purple, FontSize = 24)
        Sprite.rect.top = 5
        self.AddBackgroundSprite(Sprite)
        self.PuzzleSprites.append(Sprite)
    def RenderBackground(self):
        "Called onec, up-front."
        Image = FancyAssBoxedText("Reset", HighlightIndex = 0)
        ResetButton = GenericImageSprite(Image, 730, 500)
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
        if self.FreePlay:
            Button = FancyAssBoxedSprite("Prev", 10, 560)
            Button.Command = "Prev"
            self.AddBackgroundSprite(Button)
            self.ButtonSprites.add(Button)
            Button = FancyAssBoxedSprite("Next", 80, 560)
            Button.Command = "Next"
            self.AddBackgroundSprite(Button)
            self.ButtonSprites.add(Button)
            self.DrawDescriptionSprites()
    def ClearAllowedMoves(self):
        for Sprite in self.AllowedMoveSprites:
            Sprite.kill()
        self.AllowedMoveSprites = []
    def MoveBlock(self, Block, Dir):
        Block.Move(Dir)
        self.MoveCount += 1
        if self.MoveCountSprite:
            self.MoveCountSprite.ReplaceText(self.MoveCount)
        self.CheckVictory()
    def ShowAllowedMoves(self, Block, Moves):
        Sprite = GenericTextSprite("Move %s which way?  Press arrow key, or drag mouse; ESC cancels"%Block.Name, 140, 570, FontSize = 20)
        self.AllowedMoveSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        self.Redraw()
    def HandleKeyPressed(self, Key):
        # Debug key: Check that things are up-to-date:
        if Key == Keystrokes.Debug:
            self.PuzzleSolved()
            return
            print "----------"
            for Y in range(self.GameGrid.Height):
                for X in range(self.GameGrid.Width):
                    print self.GameGrid.GetCuteName(X, Y),
                print
        if Key == pygame.K_ESCAPE:
            if self.ActiveBlock:
                self.ClearAllowedMoves()
                self.ActiveBlock = None
                self.Redraw()
            return
        if Key == 113: # Q is for Quit
            self.SavePuzzle()
            self.App.PopScreen(self)
            return
        if Key == 114: # R is for Reset
            self.ResetPuzzle()
            return            
        # Try arrow keys:
        for (Strokes, Dir) in ((Keystrokes.Up, Directions.Up),
                      (Keystrokes.Down, Directions.Down),
                      (Keystrokes.Left, Directions.Left),
                      (Keystrokes.Right, Directions.Right)):
            if Key in Strokes and self.ActiveBlock:
                if Dir in self.ActiveBlock.GetLegalMoves():
                    self.MoveBlock(self.ActiveBlock, Dir)
                    self.ClearAllowedMoves()
                    self.ActiveBlock = None
                    self.Redraw()
        # It must be a block name, then:
        try:
            Key = chr(Key).upper()
        except:
            return
        for Block in self.GameGrid.Blocks:
            if Block.Name[0] == Key:
                PossibleMoves = Block.GetLegalMoves()
                if not PossibleMoves:
                    return
                if len(PossibleMoves)==1:
                    self.MoveBlock(Block, PossibleMoves[0])
                    self.ClearAllowedMoves()
                    self.ActiveBlock = None
                    self.Redraw()
                    return
                # More than one move:
                self.ActiveBlock = Block
                self.ShowAllowedMoves(Block, PossibleMoves)
                self.Redraw()
                return
    def ResetPuzzle(self, Silent = 0):
        if not Silent:
            Resources.PlayStandardSound("Turn Undead.wav")
        self.MoveCount = 0
        if self.MoveCountSprite:
            self.MoveCountSprite.ReplaceText(self.MoveCount)
        for Block in self.GameGrid.Blocks:
            self.GameGrid.RemovePiece(Block)
        for BlockDefinition in self.Puzzle.Blocks:
            Name = BlockDefinition[0]
            X = BlockDefinition[1]
            Y = BlockDefinition[2]
            Block = self.GameGrid.FindBlock(Name)
            Block.X = X
            Block.Y = Y
            self.GameGrid.PlacePiece(Block, X, Y)
        self.DrawDescriptionSprites()
        self.Redraw()
    def DrawDescriptionSprites(self):
        "In free-play mode, show some extra info about the puzzle."
        if not self.FreePlay:
            return
        for Sprite in self.DescriptionSprites.sprites():
            Sprite.kill()
        Y = 50
        Sprite = GenericTextSprite('"%s"'%self.Puzzle.Name, 5, Y)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        Y += Sprite.rect.height
        #
        if self.Puzzle.Author:
            Sprite = GenericTextSprite(self.Puzzle.Author, 5, Y)
            self.AddBackgroundSprite(Sprite)
            self.DescriptionSprites.add(Sprite)
            Y += Sprite.rect.height
        #
        
        Sprite = GenericTextSprite("Moves:", 5, Y)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        #
        self.MoveCountSprite = GenericTextSprite(self.MoveCount, Sprite.rect.right + 5, Y)
        self.AddForegroundSprite(self.MoveCountSprite)
        self.DescriptionSprites.add(self.MoveCountSprite)
        Y += Sprite.rect.height + 50
        ##
        Sprite = GenericTextSprite("Best solution:", 5, Y)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        Y += Sprite.rect.height
        ###
        BestSolution = Global.MemoryCard.Get("SlidingBlockHiscore:%s"%self.Puzzle.Name)
        if not BestSolution:
            Text = "Unsolved!"
        else:
            (MoveCount, SolverName) = BestSolution
            Text = "%d Moves"%MoveCount
        Sprite = GenericTextSprite(Text, 5, Y, Colors.Orange)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        Y += Sprite.rect.height
        #
        if BestSolution:
            Sprite = GenericTextSprite("By:",5, Y)
            self.AddBackgroundSprite(Sprite)
            self.DescriptionSprites.add(Sprite)
            Y += Sprite.rect.height
            Sprite = GenericTextSprite(SolverName,5, Y, Colors.Orange)
            self.AddBackgroundSprite(Sprite)
            self.DescriptionSprites.add(Sprite)
            Y += Sprite.rect.height
            
    def NextPuzzle(self, Dir = 1):
        self.SavePuzzle()
        Index = MasterPuzzleList.index(self.Puzzle)
        Index = (Index + Dir)
        if Index >= len(MasterPuzzleList):
            Index = 0
        elif Index < 0:
            Index = len(MasterPuzzleList) - 1
        self.PuzzleName = MasterPuzzleList[Index].Name
        self.BuildPuzzle()
        self.LoadPuzzle()
        #self.MoveCount = 0
        #self.RenderBackground()
        self.DrawDescriptionSprites()
        self.Redraw()
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
            elif Sprite.Command == "Next":
                self.NextPuzzle()
                return
            elif Sprite.Command == "Prev":
                self.NextPuzzle(-1)
                return
        # Now check for blocks:
        Blocks = pygame.sprite.spritecollide(Dummy, self.BlockSprites, 0)
        if not Blocks:
            return
        if len(Blocks)==1:
            Block = Blocks[0]
        else:
            # Tricky point: We may have clicked on two sprites.  Think of l-shaped blocks shaped like this:
            # XXy
            # Xyy
            X = (Position[0] - self.GameGrid.PadX) / GridWidth
            Y = (Position[1] - self.GameGrid.PadY) / GridHeight
            Block = self.GameGrid.GetContents(X, Y)
            if type(Block)==type(1):
                Block = Blocks[0]
            
##        Block = pygame.sprite.spritecollideany(Dummy, self.BlockSprites, 0)
        if Block:
            PossibleMoves = Block.GetLegalMoves()
            if len(PossibleMoves)==1:
                self.MoveBlock(Block, PossibleMoves[0])
                self.ClearAllowedMoves()
                self.ActiveBlock = None
                self.Redraw()
                return
            # Start dragging:
            if pygame.mouse.get_pressed()[0]:
                self.ActiveBlock = Block
                self.DragStart = Position
                self.ShowAllowedMoves(Block, PossibleMoves)
                self.Redraw()
    def HandleMouseMoved(self, Position, Buttons, LongPause = 0):
        if self.ActiveBlock and self.DragStart:
            # Move the block, maybe!
            if Position[0] < self.DragStart[0] - (GridWidth/2 + 10):
                if self.ActiveBlock.CanMove(Directions.Left):
                    self.MoveBlock(self.ActiveBlock, Directions.Left)
                    self.Redraw()
                    self.DragStart = (self.DragStart[0] - GridWidth, self.DragStart[1])
                    return
            if Position[0] > self.DragStart[0] + (GridWidth/2 + 10):
                if self.ActiveBlock.CanMove(Directions.Right):
                    self.MoveBlock(self.ActiveBlock, Directions.Right)
                    self.Redraw()
                    self.DragStart = (self.DragStart[0] + GridWidth, self.DragStart[1])  #(self.DragStrat[0] + GridWidth, self.DragStart[1])
                    return
            if Position[1] < self.DragStart[1] - (GridHeight/2 + 10):
                if self.ActiveBlock.CanMove(Directions.Up):
                    self.MoveBlock(self.ActiveBlock, Directions.Up)
                    self.Redraw()
                    self.DragStart = (self.DragStart[0], self.DragStart[1] - GridHeight)
                    return
            if Position[1] > self.DragStart[1] + (GridHeight/2 + 10):
                if self.ActiveBlock.CanMove(Directions.Down):
                    self.MoveBlock(self.ActiveBlock, Directions.Down)
                    self.Redraw()
                    self.DragStart = (self.DragStart[0], self.DragStart[1] + GridHeight)
                    return
                
    def HandleMouseUp(self, Position, Button):
        self.DragStart = None
        if self.ActiveBlock:
            self.ActiveBlock = None
            self.ClearAllowedMoves()
            self.Redraw()

try:
    psyco
    psyco_enabled = True
except NameError:
    psyco_enabled = False
if psyco_enabled:
    psyco.release(BlockSprite.__init__)
    psyco.release(pygame.draw.rect)
