"""
Peg solitaire: The Sport of Nerds!
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

# Click and drag to jump
# Or, if only one move is available, double-click to jump.
# Unlimited levels of UNDO are available.
# 01234567
#    ooo    0
#    ooo    1
# ...ooo... 2 
# ...o.o... 3 
# ......... 4
#    ...    5
#    ...    6


# Here are some peg solitaire puzzles.
class PuzzleDefinition:
    def __init__(self, Name, InitialPegs):
        self.Name = Name
        self.InitialPegs = InitialPegs

PuzzleDefinitions = []
InitialPegs = ((3,1), (3,2), (3,3), (3,4), (3, 5), (2,3), (1,3), (4,3), (5,3))
Puzzle = PuzzleDefinition("Plus", InitialPegs)
PuzzleDefinitions.append(Puzzle)

InitialPegs = ((2,0), (3,0), (4,0),
               (2,1), (3,1), (4,1),
               (2,2), (3,2), (4,2),
               (2,3), (4,3),
               )
Puzzle = PuzzleDefinition("Fireplace", InitialPegs)
PuzzleDefinitions.append(Puzzle)

InitialPegs = ((3,1), (2,2), (3,2), (4,2),
               (1,3),(2,3),(3,3),(4,3),(5,3),
               (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),
               )
Puzzle = PuzzleDefinition("Pyramid", InitialPegs)
PuzzleDefinitions.append(Puzzle)

InitialPegs = ((3,0), (2,1), (3,1), (4,1),
               (1,2),(2,2),(3,2),(4,2),(5,2),
               (3,3), (3,4),
               (2,5),(3,5),(4,5), (2,6),(3,6),(4,6),
               )
Puzzle = PuzzleDefinition("Arrow", InitialPegs)
PuzzleDefinitions.append(Puzzle)

InitialPegs = ((2,0),(3,0),(4,0),
               (2,1),(3,1),(4,1),
               (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
               (0,3),(1,3),(2,3),      (4,3),(5,3),(6,3),
               (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),
               (2,5),(3,5),(4,5),
               (2,6),(3,6),(4,6),
               )
Puzzle = PuzzleDefinition("Solitaire", InitialPegs)
PuzzleDefinitions.append(Puzzle)

def GetPuzzleDefinition(Name):
    for Puzzle in PuzzleDefinitions:
        if Puzzle.Name.lower() == Name.lower():
            return Puzzle
    if Name in ("1", "2", "3"):
        return PuzzleDefinitions[int(Name)]
    return None

GridWidth = 7
GridHeight = 7
GridPixels = 55

class GridContents:
    Hole = 0
    Peg = 1
    Forbidden = 2

EmptyGrid = {}
for X in range(GridWidth):
    for Y in range(GridHeight):
        EmptyGrid[(X,Y)] = GridContents.Forbidden # default
for Y in (0,1,5,6):
    for X in (2,3,4):
        EmptyGrid[(X,Y)] = GridContents.Hole
for Y in (2,3,4,):
    for X in range(7):
        EmptyGrid[(X,Y)] = GridContents.Hole

class GridClass:
    def __init__(self):
        self.Grid = EmptyGrid.copy()
        self.History = []
        self.PadX = (800 - GridWidth*GridPixels) / 2
        self.PadY = (600 - GridWidth*GridPixels) / 2
    def GetScreenX(self, X):
        return X*GridPixels + self.PadX
    def GetScreenY(self, Y):
        return Y*GridPixels + self.PadY
    def IsSolved(self):
        # We're not solved if there's a peg in anything other than (3,3):
        for X in range(GridWidth):
            for Y in range(GridHeight):
                Stuff = self.Grid[(X,Y)]
                if (Stuff == GridContents.Peg) and (X!=3 or Y!=3):
                    return 0
        return 1
    def PerformMove(self, X1, Y1, Direction):
        if not self.CanMove(X1, Y1, Direction):
            print "Bad move in GridClass::PerformMove()"
            return
        self.History.append(self.Grid.copy())
        XDir = XDirs[Direction]
        YDir = YDirs[Direction]
        X2 = X1 + XDir
        Y2 = Y1 + YDir
        X3 = X2 + XDir
        Y3 = Y2 + YDir        
        self.Grid[(X1, Y1)] = GridContents.Hole
        self.Grid[(X2, Y2)] = GridContents.Hole
        self.Grid[(X3, Y3)] = GridContents.Peg
    def UndoMove(self):
        if self.History:
            self.Grid = self.History[-1]
            self.History = self.History[:-1]
    def CanMove(self, X1, Y1, Direction):
        XDir = XDirs[Direction]
        YDir = YDirs[Direction]
        X2 = X1 + XDir
        Y2 = Y1 + YDir
        X3 = X2 + XDir
        Y3 = Y2 + YDir
        # Sanity check:
        if (X3 < 0 or X3 >= GridWidth):
            return 0
        if (Y3 < 0 or Y3 >= GridWidth):
            return 0
        if self.Grid[(X1, Y1)]!=GridContents.Peg:
            return 0
        if self.Grid[(X2, Y2)]!=GridContents.Peg:
            return 0
        if self.Grid[(X3, Y3)]!=GridContents.Hole:
            return 0
        return 1
    def GetContents(self, X, Y):
        return self.Grid.get((X,Y), GridContents.Forbidden)
    def InitFromPuzzle(self, Puzzle):
        for X in range(GridWidth):
            for Y in range(GridHeight):
                OldContents = self.Grid[(X,Y)]
                if (X,Y) in Puzzle.InitialPegs:
                    self.Grid[(X,Y)] = GridContents.Peg
                elif self.Grid[(X,Y)] == GridContents.Peg:
                    self.Grid[(X,Y)] = GridContents.Hole
                
GameGrid = None # global variable
PegImages = [] # Hole, normal peg and 'Ghost'

XDirs = (0,0,0,-1,1)
YDirs = (0,-1,1,0,0)

    
class PegSprite(GenericImageSprite):
    """
    """
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        ScreenX = GameGrid.GetScreenX(self.X)
        ScreenY = GameGrid.GetScreenY(self.Y)
        Contents = GameGrid.GetContents(self.X, self.Y)
        self.image = PegImages[Contents]
        GenericImageSprite.__init__(self,self.image, ScreenX, ScreenY)
    def CanMove(self, Direction):
        return GameGrid.CanMove(self.X, self.Y, Direction)
    def GetLegalMoves(self):
        Dirs = []
        for Direction in (Directions.Up, Directions.Down, Directions.Left, Directions.Right):
            if self.CanMove(Direction):
                Dirs.append(Direction)
        return Dirs
    def UpdateImage(self):
        Contents = GameGrid.GetContents(self.X, self.Y)
        self.SwapImage(PegImages[Contents])
    def SetImage(self, ImageNumber):
        self.SwapImage(PegImages[ImageNumber])
    
class PegScreen(Screen.TendrilsScreen):
    "Peg Solitaire screen"
    def __init__(self, App, PuzzleName = None, SolveCallback = None, FreePlay = 0):
        global GameGrid
        print "Init peg screen."
        print "PuzzleName", PuzzleName
        Screen.TendrilsScreen.__init__(self,App)
        if not PuzzleName:
            PuzzleName = Global.MemoryCard.Get("CurrentPegPuzzle", "Plus")
        print "CurrentPuzzle:", PuzzleName
        self.SongY = 420
        self.LoadPegImages()
        GameGrid = GridClass()
        #self.MoveCountSprite = None
        self.FreePlay = FreePlay
        #self.PuzzleName = PuzzleName
        self.Puzzle = GetPuzzleDefinition(PuzzleName)
        self.PegSprites = pygame.sprite.Group()
        self.PegSpriteDict = {}
        self.ButtonSprites = pygame.sprite.Group()
        self.ActivePeg = None
        self.GhostPeg = None
        self.UndoButton = None
        self.DragStart = None
        self.SolveCallback = SolveCallback
        #self.AllowedMoveSprites = []
        self.PuzzleSprites = []
        self.DescriptionSprites = pygame.sprite.Group()
        self.RenderPegs()
        self.BuildPuzzle()
        self.LoadPuzzle()
        self.DrawDescriptionSprites()
        self.LastClickTime = 0
        self.RenderBackground()
        #self.PlaySong()
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        self.PlaySong()
    def PlaySong(self):
        Song = Global.MusicLibrary.GetBlockSong()
        self.SummonSong(Song)
    def SavePuzzle(self):
        "Save the current state"
        PuzzleState = GameGrid.Grid.copy()
        # If we're in free-play mode, save on the MEMORY CARD:
        if self.FreePlay:
            Global.MemoryCard.Set("PegPuzzle:%s"%self.Puzzle.Name, PuzzleState)
        else:
            Global.Party.EventFlags["PegPuzzle%s"%self.Puzzle.Name] = PuzzleState
        print "Saved puzzle %s"%self.Puzzle.Name
    def LoadPuzzle(self):
        "Load saved puzzle-state, if any"
        print "LOAD this puzzle:", self.Puzzle.Name
        if self.FreePlay:
            State = Global.MemoryCard.Get("PegPuzzle:%s"%self.Puzzle.Name)
        else:
            State = Global.Party.EventFlags.get("PegPuzzle%s"%self.Puzzle.Name, None)
        if State:
            GameGrid.Grid = State.copy()
            GameGrid.History = []
            print "LOADED!"
            print State
        else:
            print "Failed to load!"
        self.UpdatePegs()
    def LoadPegImages(self):
        global PegImages
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Hole.png"))
        PegImages.append(Image)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Peg.png"))
        PegImages.append(Image)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Ghost.png"))
        PegImages.append(Image)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "HilitePeg.png"))
        PegImages.append(Image)
        
    def RenderPegs(self):
        for Peg in self.PegSprites.sprites():
            Peg.kill()
        for X in range(GridWidth):
            for Y in range(GridHeight):
                if GameGrid.GetContents(X,Y) != GridContents.Forbidden:
                    Sprite = PegSprite(X, Y)
                    self.PegSprites.add(Sprite)
                    self.PegSpriteDict[(X,Y)] = Sprite
                    self.BackgroundSprites.add(Sprite)
    def BuildPuzzle(self):
        #self.Puzzle = GetPuzzleDefinitio.get(self.PuzzleName)
        print "BuildPuzzle:", self.Puzzle, type(self.Puzzle) #%%%
        Global.MemoryCard.Set("CurrentPegPuzzle", self.Puzzle.Name)
        #self.GameGrid = GridClass(self.Puzzle.Width, self.Puzzle.Height)
        print "Load from default...", self.Puzzle.Name
        GameGrid.InitFromPuzzle(self.Puzzle)
    def CheckVictory(self):
        if GameGrid.IsSolved():
            # Yay!
            self.Redraw()
            self.PuzzleSolved()
    def PuzzleSolved(self):
        # Default name for 'solver'
        Music.FadeOut()
        Resources.PlayStandardSound("MegaHappy.wav")
        self.DrawDescriptionSprites()
        Key = "PegPuzzleSolved:%s"%self.Puzzle.Name
        Global.MemoryCard.Set(Key, 1)
        if not self.SolveCallback:
            # Free play:
            self.ResetPuzzle(1)
            Str = "You have solved the puzzle!"
            Global.App.ShowNewDialog(Str)
        else:
            apply(self.SolveCallback)
            Global.App.PopScreen(self)
    def RenderBackground(self):
        "Called once, up-front."
        # Want to draw lines around the puzzle's edge:
        for Sprite in self.PuzzleSprites:
            Sprite.kill()
        Sprite = LineSprite(GameGrid.GetScreenX(0), GameGrid.GetScreenY(2),
                            GameGrid.GetScreenX(2), GameGrid.GetScreenY(2), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(2), GameGrid.GetScreenY(2),
                            GameGrid.GetScreenX(2), GameGrid.GetScreenY(0), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(2), GameGrid.GetScreenY(0),
                            GameGrid.GetScreenX(5), GameGrid.GetScreenY(0), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(5), GameGrid.GetScreenY(0),
                            GameGrid.GetScreenX(5), GameGrid.GetScreenY(2), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(5), GameGrid.GetScreenY(2),
                            GameGrid.GetScreenX(7), GameGrid.GetScreenY(2), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(7), GameGrid.GetScreenY(2),
                            GameGrid.GetScreenX(7), GameGrid.GetScreenY(5), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(7), GameGrid.GetScreenY(5),
                            GameGrid.GetScreenX(5), GameGrid.GetScreenY(5), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(5), GameGrid.GetScreenY(5),
                            GameGrid.GetScreenX(5), GameGrid.GetScreenY(7), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(5), GameGrid.GetScreenY(7),
                            GameGrid.GetScreenX(2), GameGrid.GetScreenY(7), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(2), GameGrid.GetScreenY(7),
                            GameGrid.GetScreenX(2), GameGrid.GetScreenY(5), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(2), GameGrid.GetScreenY(5),
                            GameGrid.GetScreenX(0), GameGrid.GetScreenY(5), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(GameGrid.GetScreenX(0), GameGrid.GetScreenY(5),
                            GameGrid.GetScreenX(0), GameGrid.GetScreenY(2), Colors.Grey)
        self.PuzzleSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        #######################################
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
        if self.FreePlay:
            Button = FancyAssBoxedSprite("Prev", 10, 560)
            Button.Command = "Prev"
            self.AddBackgroundSprite(Button)
            self.ButtonSprites.add(Button)
            Button = FancyAssBoxedSprite("Next", 80, 560)
            Button.Command = "Next"
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
        if Key == ord("u"):
            self.Undo()
        if Key == ord("h"):
            self.ClickHelp()
    def Undo(self):
        if GameGrid.History:
            Resources.PlayStandardSound("Bleep3.wav")
        GameGrid.UndoMove()
        self.UpdatePegs()
    def UpdatePegs(self):
        self.ForegroundSprites.remove(self.ActivePeg)
        self.ForegroundSprites.remove(self.GhostPeg)
        self.ActivePeg = None
        self.GhostPeg = None
        for X in range(GridWidth):
            for Y in range(GridHeight):
                Sprite = self.PegSpriteDict.get((X,Y), None)
                if Sprite:
                    Sprite.UpdateImage()
        if GameGrid.History and not self.UndoButton:
            self.UndoButton = FancyAssBoxedSprite("Undo", 730, 520, HighlightIndex = 0)
            self.UndoButton.Command = "Undo"
            self.AddBackgroundSprite(self.UndoButton)
            self.ButtonSprites.add(self.UndoButton)
        if (not GameGrid.History) and self.UndoButton:
            self.UndoButton.kill()
            self.UndoButton = None
        self.Redraw()
    def ResetPuzzle(self, Silent = 0):
        if not Silent:
            Resources.PlayStandardSound("Turn Undead.wav")
        GameGrid.InitFromPuzzle(self.Puzzle)
        GameGrid.History = []
        self.UpdatePegs()
        self.Redraw()
    def DrawDescriptionSprites(self):
        "In free-play mode, show some extra info about the puzzle."
        if not self.FreePlay:
            return
        for Sprite in self.DescriptionSprites.sprites():
            Sprite.kill()
        Y = 30
        Sprite = GenericTextSprite('%s'%self.Puzzle.Name, 350, Y, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        Y += Sprite.rect.height
        Key = "PegPuzzleSolved:%s"%self.Puzzle.Name
        Solved = Global.MemoryCard.Get(Key, None)
        if Solved:
            Str = "Solved: <CN:GREEN>Yes!</C>"
        else:
            Str = "Solved: <CN:RED>Not yet</C>"
            
        Image = TaggedRenderer.RenderToImage(Str, FontSize = 24)
        Sprite = GenericImageSprite(Image, 350, Y)
        self.AddBackgroundSprite(Sprite)
        self.DescriptionSprites.add(Sprite)
        Y += Sprite.rect.height
        
    def NextPuzzle(self, Dir = 1):
        print "SAVE THIS PUZZLE:", self.Puzzle.Name
        self.SavePuzzle()
        Index = PuzzleDefinitions.index(self.Puzzle)
        Index = (Index + Dir)
        if Index >= len(PuzzleDefinitions):
            Index = 0
        elif Index < 0:
            Index = len(PuzzleDefinitions) - 1
        self.Puzzle = PuzzleDefinitions[Index]
        self.BuildPuzzle()
        self.LoadPuzzle()
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
            elif Sprite.Command == "Help":
                self.ClickHelp()
            elif Sprite.Command == "Next":
                self.NextPuzzle()
                return
            elif Sprite.Command == "Prev":
                self.NextPuzzle(-1)
                return
            elif Sprite.Command == "Undo":
                self.Undo()
        # Now check for blocks:
        Pegs = pygame.sprite.spritecollide(Dummy, self.PegSprites, 0)
        if not Pegs:
            return
        Peg = Pegs[0]
        Contents = GameGrid.GetContents(Peg.X, Peg.Y)
        if Contents != GridContents.Peg:
            return
        ClickTime = time.time()
        if ClickTime - self.LastClickTime < 0.5:
            # Double-click: Do the "obvious move", if there is one.
            ValidDirs = []
            for Direction in range(1,4):
                if Peg.CanMove(Direction):
                    ValidDires.append(Direction)
            if len(ValidDirs)==1:
                GameGrid.PerformMove(Peg.X, Peg.Y, Direction)
                self.UpdatePegs()
                self.CheckVictory()
                return
        # Start dragging:
        if pygame.mouse.get_pressed()[0]:
            self.ActivePeg = Peg
            self.DragStart = Position
            Peg.SetImage(3)
            self.AddForegroundSprite(self.ActivePeg) 
            #self.ShowAllowedMoves(Block, PossibleMoves)
            self.Redraw()
    def ClickHelp(self):
        HelpText = """<CENTER><CN:YELLOW>Peg Solitaire</c>
A peg can jump over another peg, either horizontally or vertically.  Jumped pegs \
are removed, like checkers.  The objective is to eliminate all but one peg, by \
jumping over the rest.  <CN:BRIGHTRED>THERE CAN BE ONLY ONE!</C>

To do a jump, <CN:BRIGHTGREEN>click and drag</C> a peg, then <CN:BRIGHTGREEN>release the mouse</C> when \
the move is ready.  You can undo moves if you get stuck."""
        Global.App.ShowNewDialog(HelpText)
        
    def HandleMouseMoved(self, Position, Buttons, LongPause = 0):
        if self.ActivePeg and self.DragStart:
            # Move the block, maybe!
            if Position[0] < self.DragStart[0] - 30:
                self.ShowGhostMove(3)
            elif Position[0] > self.DragStart[0] + 30:
                self.ShowGhostMove(4)
            elif Position[1] < self.DragStart[1] - 30:
                self.ShowGhostMove(1)
            elif Position[1] > self.DragStart[1] + 30:
                self.ShowGhostMove(2)
    def ShowGhostMove(self, Direction):
        X = self.ActivePeg.X + XDirs[Direction]*2
        Y = self.ActivePeg.Y + YDirs[Direction]*2
        Ghost = self.PegSpriteDict.get((X,Y), None)
        if not Ghost:
            if self.GhostPeg:
                self.ForegroundSprites.remove(self.GhostPeg)
                self.GhostPeg.SetImage(0)
                self.GhostPeg = None
            return
        if self.GhostPeg != Ghost and self.GhostPeg:
            self.ForegroundSprites.remove(self.GhostPeg)
            self.GhostPeg.SetImage(0)
        # Only ghost-ify if empty:
        if GameGrid.CanMove(self.ActivePeg.X, self.ActivePeg.Y, Direction):
            self.GhostPeg = Ghost
            self.GhostPeg.SetImage(2)
            self.AddForegroundSprite(self.GhostPeg)
            
    def HandleMouseUp(self, Position, Button):
        if self.ActivePeg:
            if Position[0] < self.DragStart[0] - 30:
                GameGrid.PerformMove(self.ActivePeg.X, self.ActivePeg.Y, 3)
            elif Position[0] > self.DragStart[0] + 30:
                GameGrid.PerformMove(self.ActivePeg.X, self.ActivePeg.Y, 4)
            elif Position[1] < self.DragStart[1] - 30:
                GameGrid.PerformMove(self.ActivePeg.X, self.ActivePeg.Y, 1)
            elif Position[1] > self.DragStart[1] + 30:
                GameGrid.PerformMove(self.ActivePeg.X, self.ActivePeg.Y, 2)
            #self.ActivePeg = None
            #self.GhostPeg = None
            self.UpdatePegs()
            self.CheckVictory()
        