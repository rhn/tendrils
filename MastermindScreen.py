"""
Lock: Mastermind game.  Guess the combination; get gold marks for right color in right place and
silver marks for right color in wrong place.  
"""
from Utils import *
from Constants import *
import Screen
import Global
import Resources
import os
import time
import string
import Party
import math
import ChestScreen

MScreen = None

class MastermindLock(ChestScreen.TrapPanel):
    "Master" # this string displayed on Calfo
    FontSize = 32
    CenterX = 400
    CenterY = 250
    BottomY = 500
    GuessX = [20, 20, 20, 20, 20, 20, 20, 20,
              420, 420, 420, 420, 420, 420, 420, 420]
    GuessY = [20, 60, 100, 140, 180, 220, 260, 300,
              20, 60, 100, 140, 180, 220, 260, 300,
              ]
    PegWidth = 37
    def __init__(self, *args, **kw):
        ChestScreen.TrapPanel.__init__(self, *args, **kw)
        self.Won = 0
        self.ReloadTime = 0
        self.ButtonSprites = pygame.sprite.Group()
        self.GuessSprites = []
    def ShowInstructions(self):
        Str = """Enter the combination before running out of guesses.  With each guess, you find the \
number of correct symbols, and the number of correct symbols in the wrong position.
"""
        Global.App.ShowNewDialog(Str, Callback = self.Start)
        self.VictoryTimer = None
    def IsFailed(self):
        return (self.GuessIndex >= self.GuessCount) and not self.Won
    def IsDisarmed(self):
        return (self.Won)
    def InitTrap(self):
        self.LoadImages()
        self.BuildPuzzle()
        TimeLimits = [0, 90, 80, 70, 60, 50,
                      90, 80, 70, 60, 50,
                      90, 80, 70, 60, 50,]
        self.TimeLimit = TimeLimits[self.DungeonLevel]
        if self.HasNinja:
            self.TimeLimit *= 1.5
        self.RenderInitialScreen()
    def LoadImages(self):
        # Load the COLOR PEG images, and the SUCCESS THINGY images.
        self.PegImages = []
        Dir = os.path.join(Paths.ImagesTraps, "Master")
        for Index in range(6):
            Path = os.path.join(Dir, "%d.png"%Index)
            Image = Resources.GetImage(Path)
            self.PegImages.append(Image)
        Path = os.path.join(Dir, "Silver.png")
        self.SilverImage = Resources.GetImage(Path)
        Path = os.path.join(Dir, "Gold.png")
        self.GoldImage = Resources.GetImage(Path)
    def BuildPuzzle(self):
        ColorCounts = [0, 4, 3, 4, 4, 4, 4, 5, 5, 4, 5]
        SymbolCounts = [0, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6]
        self.ColorCount = ColorCounts[self.DungeonLevel]
        self.SymbolCount = SymbolCounts[self.DungeonLevel]
        self.GuessCount = 2 + self.ColorCount + self.SymbolCount
        
        if self.HasNinja:
            self.GuessCount += 3
        self.Combo = []
        Colors = list(range(self.ColorCount))
        for Index in range(self.SymbolCount):
            self.Combo.append(random.choice(Colors))
        # Ok, we're ready to go!
        self.GuessIndex = 0
    def HandleKeyPressed(self, Key):
        if Key == 8: # backspace
            self.ClickBackspace()
            return
        Color = Key - ord("1")
        if Color in range(0, self.ColorCount):
            self.ClickColor(Color)
    def ClickBackspace(self):
        if len(self.GuessSprites):
            self.GuessSprites[-1].kill()
            self.GuessSprites = self.GuessSprites[:-1]
            self.Redraw()
        Resources.PlayStandardSound("Bleep1.wav")
        
    def RenderInitialScreen(self):
        # Draw clickable buttons:
        X = 100
        for Color in range(self.ColorCount):
            Sprite = GenericImageSprite(self.PegImages[Color], X, 400)
            self.AddBackgroundSprite(Sprite)
            Sprite.Color = Color
            self.ButtonSprites.add(Sprite)
            # And label:
            Sprite = GenericTextSprite(str(Color+1), X + 10, 440, FontSize = 32)
            self.AddBackgroundSprite(Sprite)
            X += 70
        # Backspace button:
        Sprite = GenericTextSprite("RUB", X, 500)
        self.AddBackgroundSprite(Sprite)
        Sprite.Color = None
        self.ButtonSprites.add(Sprite)
        # Status info:
        Sprite = GenericTextSprite("%d symbols in combo"%len(self.Combo), 550, 400, FontSize = 32)
        self.AddBackgroundSprite(Sprite)
        self.GuessesSprite = GenericTextSprite("%d guesses left"%(self.GuessCount - self.GuessIndex), 550, 450, FontSize = 32)
        self.AddBackgroundSprite(self.GuessesSprite)
        self.Redraw()
    def FinishRow(self):
        # Draw pegs:
        UsedFlags = [0] * len(self.Combo)
        MatchedFlags = [0]*len(self.Combo)
        GoldPegs = 0
        SilverPegs = 0
        # Gold pegs:
        for Index in range(len(self.Combo)):
            if self.GuessSprites[Index].Color == self.Combo[Index]:
                UsedFlags[Index] = 1
                MatchedFlags[Index] = 1
                GoldPegs += 1
        # Silver pegs:
        for Index in range(len(self.Combo)):
            for OtherIndex in range(len(self.Combo)):
                if not UsedFlags[Index] and not MatchedFlags[OtherIndex] \
                   and self.GuessSprites[Index].Color == self.Combo[OtherIndex]:
                    SilverPegs += 1
                    UsedFlags[Index] = 1
                    MatchedFlags[OtherIndex] = 1
        if GoldPegs == len(self.Combo):
            # Right answer!
            self.Won = 1
        else:
            Resources.PlayStandardSound("Bleep4.wav")
        X = self.GuessX[self.GuessIndex] + self.PegWidth*len(self.Combo)
        for Index in range(GoldPegs):
            Sprite = GenericImageSprite(self.GoldImage, X, self.GuessY[self.GuessIndex])
            self.AddBackgroundSprite(Sprite)
            X += Sprite.rect.width + 5
        for Index in range(SilverPegs):
            Sprite = GenericImageSprite(self.SilverImage, X, self.GuessY[self.GuessIndex])
            self.AddBackgroundSprite(Sprite)
            X += Sprite.rect.width + 5
        self.GuessIndex += 1
        GuessesLeft = (self.GuessCount - self.GuessIndex)
        if GuessesLeft!=1:
            Text = "%d guesses left"%GuessesLeft
        else:
            Text = "1 guess left"
        self.GuessesSprite.ReplaceText(Text)
        self.GuessSprites = []
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        # Backspace:
        if Sprite.Color == None:
            self.ClickBackspace()
            return
        self.ClickColor(Sprite.Color)
    def ClickColor(self, Color):
        # Add to our pattern:
        NewSprite = GenericImageSprite(self.PegImages[Color], self.GuessX[self.GuessIndex] + self.PegWidth*len(self.GuessSprites), self.GuessY[self.GuessIndex])
        NewSprite.Color = Color
        self.AddBackgroundSprite(NewSprite)
        self.GuessSprites.append(NewSprite)
        if len(self.GuessSprites) == len(self.Combo):
            self.FinishRow()
            self.Redraw()
            return
        else:
            Resources.PlayStandardSound("Bleep3.wav")
            self.Redraw()
            return

        