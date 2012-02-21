"""
The initial screen.  Displays a pretty logo and gives the player to "resume" the most recently saved game,
start a "new game", "load game", or see some "instructions".  For those of you reading code, THIS is a good
screen to look at first, because it's simple.  (Save BattleScreen for last, ok?)
"""

from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import os
import cPickle
import time
import string
import SaveScreen
import Party
import Maze
from Constants import *

from BattleSprites import *
import Instructions

CrittersToLoad = 12

class StarSprite(GenericImageSprite):
    def __init__(self, Image, X, Y, XDir):
        self.X = X
        self.XDir = XDir
        GenericImageSprite.__init__(self, Image, X, Y)
    def Update(self, AnimationCycle):
        self.X -= self.XDir
        if self.X < -10:
            self.X = 810 # Wrap around!
        self.rect.left = int(self.X)
        Dirty(self.rect)

class WelcomeScreen(Screen.TendrilsScreen):
    LogoY = 130
    ButtonHeight = 35
    ScrollArrowX = 760
    UpArrowY = 130
    DownArrowY = 410
    SongY = -50 # don't show
    InfoButtonX = 180
    GameButtonX = 400
    MiniGameButtonX = 620
    InfoButtonXNarrow = 300
    GameButtonXNarrow = 500
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        self.MarchingCritters = [[],[]]
        self.TitleSprites = pygame.sprite.Group()
        self.InstructionsSprites = pygame.sprite.Group()
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))                
        self.ShowingInstructions = 0
        self.InstructionScrollRow = 0
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        self.InstructionRowImages = None
        self.ButtonHeaders = {}
        self.CritterQueue = []
        self.RenderInitialScreen()
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        self.SummonSong("intro")
    def ShowInstructions(self, ReleaseNotes = 0):
        self.ShowingInstructions = 1
        for Star in self.StarSprites:
            Star.kill()
        for Star in self.TitleSprites.sprites():
            Star.kill()
        self.ButtonHeaders = {}
        # Draw a black rectangle with a white border:
        Image = pygame.Surface((800, 350))
        Image.fill(Colors.Black)
        pygame.draw.rect(Image, Colors.White, (1, 1, 798, 348), 1)
        Sprite = GenericImageSprite(Image, 0, 125)
        self.InstructionsSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        # Draw the "done" button:
        Image = FancyAssBoxedText("Ok!",FontSize = 36, Spacing = 5, HighlightIndex = 0, BackColor = (11,11,11))
        Rect = Image.get_rect()
        ButtonSprite = GenericImageSprite(Image, 700, 450)
        ButtonSprite.Command = "InstructionsDone"        
        self.AddForegroundSprite(ButtonSprite)
        self.InstructionsSprites.add(ButtonSprite)
        self.ButtonSprites.add(ButtonSprite)
        # Surface for instructionblitting:
        Image = pygame.Surface((760,320))
        self.InstructionText = GenericImageSprite(Image, 3, 128)
        self.InstructionsSprites.add(self.InstructionText)
        self.AddBackgroundSprite(self.InstructionText)
        self.InstructionScrollRow = 0
        # Get the instruction images:
        if ReleaseNotes:
            InstructionsStr = Instructions.ReleaseNotes
        else:
            InstructionsStr = Instructions.HelpText
        self.InstructionRowImages = TaggedRenderer.RenderToRows(InstructionsStr, WordWrapWidth = self.InstructionText.rect.width)
        self.RowsAtOnce = self.InstructionText.rect.height / self.InstructionRowImages[1].get_rect().height
        self.BlitInstructionText()
    def BlitInstructionText(self):
        self.DrawScrollArrows()
        Y = 0
        self.InstructionText.image.fill((Colors.Black))
        for RowImage in self.InstructionRowImages[self.InstructionScrollRow:self.InstructionScrollRow + self.RowsAtOnce]:
            self.InstructionText.image.blit(RowImage, (0,Y))
            Y += RowImage.get_rect().height
            if Y > self.InstructionText.rect.bottom:
                break # That's all that fits!
        self.Redraw()
    def DrawScrollArrows(self):
        TotalRows = len(self.InstructionRowImages)
        self.InstructionScrollRow = max(0, min(self.InstructionScrollRow, TotalRows - self.RowsAtOnce))
        if self.InstructionScrollRow > 0:
            if not self.UpArrowSprite:
                self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.UpArrowY)
                self.AddForegroundSprite(self.UpArrowSprite)
                self.InstructionsSprites.add(self.UpArrowSprite)
        else:
            if self.UpArrowSprite:
                self.UpArrowSprite.kill()
                self.UpArrowSprite = None
        if self.InstructionScrollRow < (TotalRows - self.RowsAtOnce):
            if not self.DownArrowSprite:
                self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DownArrowY)
                self.AddForegroundSprite(self.DownArrowSprite)
                self.InstructionsSprites.add(self.DownArrowSprite)
        else:
            if self.DownArrowSprite:
                self.DownArrowSprite.kill()
                self.DownArrowSprite = None
        
    def DismissInstructions(self):
        for Sprite in self.InstructionsSprites.sprites():
            Sprite.kill()
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        self.ShowingInstructions = 0
        self.RenderLogo()
        self.RenderButtons()
        self.RenderStars()
        self.Redraw()
    def Update(self):
        """
        Consider adding more monsters to march across the screen.
        """
        if len(self.CritterQueue) < CrittersToLoad:
            self.PreloadMarchingCritters()
        else:
            self.UpdateCritters(self.MarchingCritters[0], 125)
            self.UpdateCritters(self.MarchingCritters[1], 600)
    def UpdateCritters(self, Critters, Y):
        MinX = 800
        for Critter in Critters:
            MinX = min(Critter.rect.left, MinX)
            Critter.rect.left += 1
            Critter.X += 1
            if Critter.X > 800:
                Critter.kill()
                try:
                    self.MarchingCritters[0].remove(Critter)
                except:
                    self.MarchingCritters[1].remove(Critter)
        if MinX > 120 and random.random() < 0.02:
            CritterSprite = self.GetMarchingCritterSprite()
            CritterSprite.rect.right = 0
            CritterSprite.X = CritterSprite.rect.left
            CritterSprite.rect.bottom = Y
            CritterSprite.Y = CritterSprite.rect.top
            self.AddAnimationSprite(CritterSprite)
            Critters.append(CritterSprite)
    def PreloadMarchingCritters(self):
        # It's slightly slow to load new creature images (slow enough that there's a jerk in the starfield),
        # so load all the images up-front and keep a queue of ready-to-march sprites on hand.
        for Index in range(2):
            Critter = Global.Bestiary.GetMarchingCritter()
            Sprite = CritterSpriteClass(self, Critter,-200,-200)
            self.CritterQueue.append(Sprite)
        if len(self.CritterQueue)==CrittersToLoad:
            self.RenderStars()
    def GetMarchingCritterSprite(self):
        #Critter = Global.Bestiary.GetMarchingCritter()
        #Sprite = CritterSpriteClass(self, Critter,0,0)
        Sprite = self.CritterQueue[0]
        self.CritterQueue = self.CritterQueue[1:]
        self.CritterQueue.append(Sprite)
        return Sprite
    def RenderStars(self):
        for Star in self.StarSprites:
            Star.kill()
        TopY = 120
        BottomY = 440
        CenterY = (TopY + BottomY) / 2
        for Index in range(50):
            Y = random.randrange(TopY, BottomY)
            MaxSpeed = 4 + abs((Y-CenterY)/40.0)
            XDir = random.randrange(30,100) * (MaxSpeed / 100.0)
            Sprite = StarSprite(random.choice(self.StarImages), random.randrange(0,800), Y, XDir)
            self.AddAnimationSprite(Sprite)
            self.StarSprites.append(Sprite)
    def RenderInitialScreen(self):
        # Logo:
        self.RenderLogo()
        # Buttons:
        self.RenderButtons()
        # Zooming stars (cosmic cycler, hoshizora cycling, run run run away home)
        self.StarImages = []
        for Index in range(4):
            Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Star.%d.png"%Index))
            self.StarImages.append(Image)        
        self.StarSprites = []
        
    def DoSavedGamesExist(self):
        try:
            SaveDir = os.path.join(GetUserDataDir(), "Save")
            if len(os.listdir(SaveDir)):
                return 1
        except:
            pass
        return 0
    def AddButton(self, Label, X, Y, EnabledFlag = 1, HighlightIndex = 0):
        FontSize = 20
        Spacing = 2
        if EnabledFlag:
            Image = FancyAssBoxedText(Label, FontSize = FontSize, Spacing = Spacing, HighlightIndex = HighlightIndex)
            Rect = Image.get_rect()
            ButtonSprite = GenericImageSprite(Image, X - (Rect.width/2), Y)
            ButtonSprite.Command = Label
            self.AddBackgroundSprite(ButtonSprite)
            self.ButtonSprites.add(ButtonSprite)
            self.TitleSprites.add(ButtonSprite)
            Y += self.ButtonHeight
        else:
            Sprite = GenericTextSprite(Label, X, Y, Colors.MediumGrey, FontSize = FontSize, CenterFlag = 1)
            self.AddBackgroundSprite(Sprite)
            self.TitleSprites.add(Sprite)
            Y += self.ButtonHeight
        return Y
    def AddButtonHeader(self, Label, X, Y):
        if self.ButtonHeaders.get(Label):
            return Y
        self.ButtonHeaders[Label] = 1
        Sprite = GenericTextSprite(Label, X, Y, Colors.Yellow, FontSize = 20, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        self.TitleSprites.add(Sprite)
        Y += Sprite.rect.height + 5
        return Y
    def AreMiniGamesAvailable(self):
        if Global.MemoryCard.Get("MiniGameFreePlay"):
            return 1
        if Global.MemoryCard.Get("MiniGameSlidingBlock"):
            return 1
        if Global.MemoryCard.Get("MiniGameDaleks"):
            return 1
        if Global.MemoryCard.Get("MiniGameBlezmon"):
            return 1
        if Global.MemoryCard.Get("MiniGameJoustPong"):
            return 1
        if Global.MemoryCard.Get("MiniGamePegJump"):
            return 1
        if Global.MemoryCard.Get("MiniGameBlinkenlights"):
            return 1
        
    def RenderButtons(self):
        self.ButtonSprites = pygame.sprite.Group()
        #
        MiniGames = self.AreMiniGamesAvailable()
        if MiniGames:
            InfoButtonX = self.InfoButtonX
            GameButtonX = self.GameButtonX
        else:
            InfoButtonX = self.InfoButtonXNarrow
            GameButtonX = self.GameButtonXNarrow
        Y = 260
        Y = self.AddButtonHeader("(info)", InfoButtonX, Y)
        Y = self.AddButton("Instructions", InfoButtonX, Y)
        Y = self.AddButton("About", InfoButtonX, Y)
        Y = self.AddButton("Key Config", InfoButtonX, Y)
        Y += 50
        Y = self.AddButton("Tendrils Homepage", InfoButtonX, Y, HighlightIndex = None)
        #############
        Y = 260
        Y = self.AddButtonHeader("(game)", GameButtonX, Y)
        Y = self.AddButton("New Game", GameButtonX, Y)
        SavedGamesExist = self.DoSavedGamesExist()
        Y = self.AddButton("Load Game", GameButtonX, Y, SavedGamesExist)
        Y = self.AddButton("Resume", GameButtonX, Y, SavedGamesExist)
        Y += 80
        Y = self.AddButton("Exit", GameButtonX, Y, HighlightIndex = 1)
        ############
        Y = 260
        if MiniGames:
            Y = self.AddButtonHeader("(mini-games)", self.MiniGameButtonX, Y)
        if Global.MemoryCard.Get("MiniGameFreePlay"):
            Y = self.AddButton("Free Play", self.MiniGameButtonX, Y, HighlightIndex = None)
        if Global.MemoryCard.Get("MiniGameSlidingBlock"):
            Y = self.AddButton("Sliding Blocks", self.MiniGameButtonX, Y, HighlightIndex = None)
        if Global.MemoryCard.Get("MiniGameDaleks"):
            Y = self.AddButton("Daleks", self.MiniGameButtonX, Y, HighlightIndex = None)
        if Global.MemoryCard.Get("MiniGameBlezmon"):
            Y = self.AddButton("Blezmon", self.MiniGameButtonX, Y, HighlightIndex = None)
        if Global.MemoryCard.Get("MiniGameJoustPong"):
            Y = self.AddButton("Joust-Pong", self.MiniGameButtonX, Y, HighlightIndex = None)
        if Global.MemoryCard.Get("MiniGamePegJump"):
            Y = self.AddButton("Peg Jump", self.MiniGameButtonX, Y, HighlightIndex = None)
        if Global.MemoryCard.Get("MiniGameBlinkenlights"):
            Y = self.AddButton("Blinkenlights", self.MiniGameButtonX, Y, HighlightIndex = None)
    def HandleKeyPressed(self, Key):
        if self.ShowingInstructions:
            if Key == pygame.K_ESCAPE or Key == ord("o"):
                self.DismissInstructions()
                return
            if Key in (280, 265): # pgUp
                self.ClickUpArrow()
                return
            if Key in (281, 259): # pgDown
                self.ClickDownArrow()
                return
            
        else:
            if Key == ord("i"):
                self.ShowInstructions()
                return
            elif Key == ord("k"):
                self.DoKeyConfig()
                return
            elif Key == ord("x"):
                self.App.PopScreen(self)
                return
            elif Key == ord("l") and self.DoSavedGamesExist():
                Global.App.ShowLoadScreen()
                return
            elif Key == ord("r") and self.DoSavedGamesExist():
                self.ClickResume()
                return
            elif Key == ord("n"):
                self.StartNewGame()
                return
            elif Key == ord("a"):
                self.ShowInstructions(1)
                return
    def DoKeyConfig(self):
        Global.App.ShowJoyConfig()
    def RenderLogo(self):
        Logo = GenericTextSprite("Tendrils", self.Width / 2, self.LogoY, FontSize = 144, CenterFlag = 1)
        self.AddBackgroundSprite(Logo)
        self.TitleSprites.add(Logo)
    def ClickUpArrow(self):
        self.InstructionScrollRow = max(self.InstructionScrollRow - 4, 0)
        self.BlitInstructionText()
    def ClickDownArrow(self):        
        self.InstructionScrollRow = min(self.InstructionScrollRow + 4, len(self.InstructionRowImages) - self.RowsAtOnce)
        self.InstructionScrollRow = max(self.InstructionScrollRow, 0)
        self.BlitInstructionText()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # FIRST: Try clicking the instructions scrollies
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite and Sprite == self.UpArrowSprite:
            self.ClickUpArrow()
            return
        if Sprite and Sprite == self.DownArrowSprite:
            self.ClickDownArrow()
            return
        # NOW: Try clicking normal buttons
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        if self.ShowingInstructions:
            if Sprite.Command == "InstructionsDone":
                self.DismissInstructions()
                return
            return
        if Sprite.Command == "Exit":
            self.App.PopScreen(self)
            return
        if Sprite.Command == "Resume":
            self.ClickResume()
            return
        if Sprite.Command == "New Game":
            self.StartNewGame()
        if Sprite.Command == "Load Game":
            Global.App.ShowLoadScreen()
            return
        if Sprite.Command == "Instructions":
            self.ShowInstructions()
            return
        if Sprite.Command == "Key Config":
            self.DoKeyConfig()
            return
        if Sprite.Command == "About":
            self.ShowInstructions(1)
            return
        if Sprite.Command == "Tendrils Homepage":
            import webbrowser
            webbrowser.open("http://www.necrofamicon.com/Tendrils/", 1)
        if Sprite.Command == "Free Play":
            Global.App.StartFreePlay()
            return
        if Sprite.Command == "Daleks":
            Global.App.ShowDalekScreen(1)
            return
        if Sprite.Command == "Joust-Pong":
            Global.App.ShowJoustPongScreen(1)
            return
        if Sprite.Command == "Blezmon":
            Global.App.ShowBlezmonScreen(1)
            return
        if Sprite.Command == "Sliding Blocks":
            Global.App.ShowBlockScreen(FreePlay = 1)
            return
        if Sprite.Command == "Peg Jump":
            Global.App.ShowPegSolitaireScreen(FreePlay = 1)
            return
        if Sprite.Command == "Blinkenlights":
            Global.App.ShowBlinkenlightsScreen()
            return
        
    def ClickResume(self):
        Parties = SaveScreen.GetSavedGameList()
        Global.Party = Parties[0]
        Resources.PreloadImageCache()
        print "GoToMazeLevel:",Global.Party.Z
        Maze.GoToMazeLevel(Global.Party.Z)
        Global.App.ShowTheMaze()
        
    def StartNewGame(self):
        Global.Maze.Level = 1
        Global.Party.Z = 1
        Global.Maze.Load()
        Resources.PreloadImageCache()
        Global.Party = Party.GetNewParty()
        Global.App.ShowTheMaze(1)
        Global.App.ShowFirstScreen()
        return            
            