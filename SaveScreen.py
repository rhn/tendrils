"""
A screen for saving the game.  The player can NOT save at arbitrary points
in the maze.  (A possible change: Allow a "quick-save", which can be only
loaded once, at any point in the maze...  It's a little awkward having two
types of save, however)
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
import cPickle
import time
import string
import Maze

LegalSavedGameLetters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-'! "

ShiftTranslate = string.maketrans("abcdefghijklmnopqrstuvwxyz1","ABCDEFGHIJKLMNOPQRSTUVWXYZ!")
def GetBackgroundArt():
    Image = pygame.Surface((800,600))
    Image.fill((0,33,0))
    return Image

def LoadParty(FilePath):
    File = open(FilePath, "rb")
    Party = cPickle.load(File)
    File.close()
    # Add any potentially-missing members here:
    if not hasattr(Party, "BlinkenCount"):
        Party.BlinkenCount = 0
    if not hasattr(Party, "PawnedStuff"):
        Party.PawnedStuff = {}
    if not hasattr(Party, "TotalPlayTime"):
        Party.TotalPlayTime = 0
    return Party

def GetSaveDir():
    return os.path.join(GetUserDataDir(), "Save")

def GetSavedGameList():
        """
        Get a list of saved games.  Order them by file modification date.  
        """
        SavedParties = []
        # Make sure save-dir exists:
        SaveDir = GetSaveDir()
        try:
            os.mkdir(SaveDir)
        except:
            pass
        # Look up all the saves, sort them:
        SortedList = []
        for FileName in os.listdir(SaveDir):
            FilePath = os.path.join(SaveDir, FileName)
            ModDate = os.stat(FilePath).st_mtime
            SortedList.append((ModDate, FilePath))
            SortedList.sort()
            SortedList.reverse() # Newest files (with largest numeric mod-date) at the top
        # Now process each file into a party and a sprite:
        for (ModDate, FilePath) in SortedList:
            Party = None
            if os.path.isdir(FilePath): # Skip directories (Just in case!)
                continue 
            try:
                Party = LoadParty(FilePath)
            except:
                traceback.print_exc() #%%%
                continue
            if Party:
                Party.ModDate = ModDate
                Party.FilePath = FilePath
                Party.FileName = (os.path.split(FilePath)[1])
                Party.FileName = Party.FileName.split(".")[0]
                SavedParties.append(Party)
        return SavedParties

class SavePanel(Screen.TendrilsPane):
    SaveHeight = 90
    SavePadding = 24
    SavesAtOnce = 4
    ScrollArrowX = 770
    UpArrowY = 10
    DownArrowY = 410
    def __init__(self, OwningScreen, BlitX, BlitY, Width, Height, SavingFlag):
        Screen.TendrilsPane.__init__(self,OwningScreen,BlitX,BlitY,Width,Height,"SavePanel")
        self.ScrollRow = 0
        self.SavingFlag = SavingFlag #are we saving, or loading?
        self.EditGameIndex = None
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        self.CursorSprite = None
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))        
        self.SavedParties = []
        self.SavedSpriteList = []
        self.SavedSprites = pygame.sprite.Group()        
        self.GetSavedSpriteList()
        self.DrawBackground()
        self.Render()
    def GetSavedSpriteList(self):
        # Kill any old stuff:
        for Sprite in self.SavedSpriteList:
            Sprite.kill()
        self.SavedParties = GetSavedGameList()
        self.SavedSpriteList = []
        for Party in self.SavedParties:
                Sprite = self.MakeSavedSprite(Party)
                self.SavedSpriteList.append(Sprite)
                self.SavedSprites.add(Sprite)
                self.AddBackgroundSprite(Sprite)
        if self.SavingFlag:
                # Also produce a "new save" sprite:
                Sprite = self.MakeSavedSprite(None)
                self.SavedParties.append(None)
                self.SavedSpriteList.append(Sprite)
                self.SavedSprites.add(Sprite)
                self.AddBackgroundSprite(Sprite)
                self.Render()
                self.Redraw()            
    def DrawBackground(self):
        Rect = self.UpArrowImage.get_rect()
        X = self.ScrollArrowX + Rect.width/2
        Sprite = LineSprite(X, self.UpArrowY + Rect.height, X, self.DownArrowY, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
    def Render(self):
        Y = 5
        self.ScrollRow = min(self.ScrollRow, len(self.SavedParties) - self.SavesAtOnce)
        self.ScrollRow = max(self.ScrollRow, 0)
        for Index in range(len(self.SavedParties)):
            Sprite = self.SavedSpriteList[Index]
            if Index in range(self.ScrollRow, self.ScrollRow + self.SavesAtOnce):
                Sprite.rect.top = Y
                Sprite.rect.left = 5
                Y += self.SaveHeight + self.SavePadding
            else:
                Sprite.rect.top = 601 # off-screen
        self.DrawScrollArrows()
        self.Redraw()
    def DrawScrollArrows(self):
        TotalRows = len(self.SavedParties)
        self.ScrollRow = max(0, min(self.ScrollRow, TotalRows - self.SavesAtOnce))
        if self.ScrollRow > 0:
            if not self.UpArrowSprite:
                self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.UpArrowY)
                self.AddForegroundSprite(self.UpArrowSprite)
        else:
            if self.UpArrowSprite:
                self.UpArrowSprite.kill()
                self.UpArrowSprite = None
        if self.ScrollRow < (TotalRows - self.SavesAtOnce):
            if not self.DownArrowSprite:
                self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DownArrowY)
                self.AddForegroundSprite(self.DownArrowSprite)
        else:
            if self.DownArrowSprite:
                self.DownArrowSprite.kill()
                self.DownArrowSprite = None
            

    def SaveParty(self, Party, FilePath):
        File = open(FilePath, "wb")
        cPickle.dump(Party, File)
        File.close()
    def MakeSavedSprite(self, Party):
        """
        Make a sprite for this save.  If party is null, do the "new save" sprite.
        """
        SpriteSurface = pygame.Surface((750, 100))
        self.RenderParty(Party, SpriteSurface)
        return GenericImageSprite(SpriteSurface, 0, 0)
    def RenderParty(self, Party, SpriteSurface, EditPos = None):
        # Highlighting rectangle:
        pygame.draw.rect(SpriteSurface, Colors.DarkGreen, (0,0,750,100),0)
        pygame.draw.rect(SpriteSurface, Colors.White, (2,2,746,96),1)
        pygame.draw.rect(SpriteSurface, Colors.Black, (5,5,740,90),0)
        if Party == None:
            Image = TextImage("New Save", Colors.Grey, FontSize = 32)
            SpriteSurface.blit(Image, (9, 9))
            return GenericImageSprite(SpriteSurface, 0, 0)
        # Line 1 - date, and save name:
        TimeStr = time.strftime("%d %b, %Y %H:%M", time.localtime(Party.ModDate))
        Image1 = TextImage("%s - "%(TimeStr), Colors.Grey, FontSize = 32)
        SpriteSurface.blit(Image1, (9, 9))
        LeftX = 9 + Image1.get_rect().width
        Image2 = TextImage(Party.FileName, Colors.Yellow, FontSize = 32)
        SpriteSurface.blit(Image2, (LeftX, 9))
        LeftX = LeftX + Image2.get_rect().width
        if EditPos!=None:
            X = LeftX + self.BlitX + 5#EditPos[0] + 9 + Image.get_rect().width + 1 + self.BlitX
            Y = EditPos[1] + 12 + self.BlitY
            if not self.CursorSprite:
                self.CursorSprite = CursorSprite(self, X, Y, Colors.White, 20, 25)
                #self.AddAnimationSprite(self.CursorSprite)
                self.Master.AddAnimationSprite(self.CursorSprite)
            self.CursorSprite.rect.top = Y
            self.CursorSprite.rect.left = X
        # Line 2 - Character names  #%%%
        X = 9
        for Label in range(1, 5):
                Player = Party.Players[PlayerLabelToPlayerIndex[Label]]
                WordImage = TextImage(Player.Name, FontSize = 24)
                SpriteSurface.blit(WordImage, (X, 35))
                X += 150
##        Image = TextImage("Stuff and junk...", FontSize = 32)
##        SpriteSurface.blit(Image, (9, 31))        
        # Line 3 - Character levels #%%%
        X = 9
        for Label in range(1, 5):
                Player = Party.Players[PlayerLabelToPlayerIndex[Label]]
                Str = "Lvl%d %s"%(Player.Level, Player.Species.Name)
                WordImage = TextImage(Str, Colors.LightGrey, FontSize = 24)
                SpriteSurface.blit(WordImage, (X, 61))
                X += 150
        
    def ClickUpArrow(self):
        self.ScrollRow = max(self.ScrollRow - 1, 0)
        self.Render()
    def ClickDownArrow(self):
        self.ScrollRow = min(self.ScrollRow + 1, len(self.SavedParties) - self.SavesAtOnce)
        self.ScrollRow = max(self.ScrollRow, 0)
        self.Render()
        
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First handle scrolly buttons:
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite and Sprite == self.UpArrowSprite and self.EditGameIndex==None:
            self.ClickUpArrow()
            return
        if Sprite and Sprite == self.DownArrowSprite and self.EditGameIndex==None:
            self.ClickDownArrow()
            return
        # Now handle saved games:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.SavedSprites)
        if not Sprite:
            return
        
        SpriteIndex = self.SavedSpriteList.index(Sprite)
        # First, handle the "load game" case:
        if not self.SavingFlag:
            Global.Party = self.SavedParties[SpriteIndex]
            print "Load a game: We're on level:", Global.Party.Z, type(Global.Party.Z)
            Resources.PreloadImageCache()
            Maze.GoToMazeLevel(Global.Party.Z)
            #Global.Maze.Level = Global.Party.Z
            #Global.Maze.Load()
            Global.App.ShowTheMaze()
            Global.App.PopScreen(self.Master)
            return
        # Handle the case where we were editing another game, but then we clicked on this one:
        if (self.EditGameIndex!=None and self.EditGameIndex!=SpriteIndex):
            self.CancelCurrentEdit()
        # If you click the same box again, nothing happens:
        if self.EditGameIndex == SpriteIndex:
            return
        self.EditGameIndex = SpriteIndex
        if self.SavedParties[SpriteIndex]:
                Global.Party.FileName = self.SavedParties[SpriteIndex].FileName
        else:
                Global.Party.FileName = ""
        Global.Party.ModDate = time.time()
        Sprite = self.SavedSpriteList[SpriteIndex]
        self.RenderParty(Global.Party, Sprite.image, (Sprite.rect.left, Sprite.rect.top))
        self.Redraw()
    def CancelCurrentEdit(self):
        if self.EditGameIndex!=None:
            self.RenderParty(self.SavedParties[self.EditGameIndex], self.SavedSpriteList[self.EditGameIndex].image)
        if self.CursorSprite:
            self.CursorSprite.kill()
            self.CursorSprite = None
        self.EditGameIndex = None
    def HandleLetterPressed(self, Char):
        if self.EditGameIndex==None:
            return
        if len(Global.Party.FileName)>=30:
            # That's plenty!
            Resources.PlayStandardSound("Error.wav")
            return
        Global.Party.FileName += Char
        Sprite = self.SavedSpriteList[self.EditGameIndex]
        self.RenderParty(Global.Party, Sprite.image,  (Sprite.rect.left, Sprite.rect.top))
        self.Redraw()
    def HandleBackspace(self):
        if self.EditGameIndex==None:
            return
        if len(Global.Party.FileName):
            Global.Party.FileName = Global.Party.FileName[:-1]
            Sprite = self.SavedSpriteList[self.EditGameIndex]
            self.RenderParty(Global.Party, Sprite.image,  (Sprite.rect.left, Sprite.rect.top))
            self.Redraw()
    def HandleEnter(self):
        if self.EditGameIndex==None:
            return
        SaveDir = GetSaveDir()
        # If we're saving over an old file, trash it:
        if self.SavedParties[self.EditGameIndex]:
            Path = self.SavedParties[self.EditGameIndex].FilePath
            if os.path.exists(Path):
                try:
                    os.remove(self.SavedParties[self.EditGameIndex].FilePath)
                except:
                    # Damn!
                    Global.App.ShowNewDialog("Unable to save game to that file!")
                    return
        # Generate a unique name:
        SaveIndex = 1
        FilePath = os.path.join(SaveDir, "%s.sav"%Global.Party.FileName)
        if not Global.Party.FileName or os.path.exists(FilePath):
                SaveIndex = 1
                while (1):
                    FilePath = os.path.join(SaveDir, "%s.%s.sav"%(Global.Party.FileName, SaveIndex))
                    if not os.path.exists(FilePath):
                        break
                    SaveIndex += 1
        self.SaveParty(Global.Party, FilePath)
        self.EditGameIndex = None
        self.CursorSprite.kill()
        self.CursorSprite = None
        self.ScrollRow = 0
        self.GetSavedSpriteList() # Re-draw everything!
        Sprite = GlowingTextSprite(self.Master, "--- Saved! ---", self.Width / 2, 92)
        self.Master.AddAnimationSprite(Sprite)

class LoadScreen(Screen.TendrilsScreen):                
    SavePanelX = 0
    SavePanelY = 110
    SavePanelWidth = 800
    SavePanelHeight = 450    
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.RenderInitialScreen()
    def RenderInitialScreen(self):
        self.DrawBackground()
        self.SavePanel = SavePanel(self, self.SavePanelX, self.SavePanelY, self.SavePanelWidth,
                                   self.SavePanelHeight, 0)
        self.SubPanes.append(self.SavePanel)
    def DrawBackground(self):
        Image = GetBackgroundArt()
        BigBiff = GenericImageSprite(Image, 0, 0)
        self.DeepSprites.add(BigBiff)
        
        Sprite = GenericTextSprite("Click on a saved game to load.",self.Width / 2, 0, FontSize = 32, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        Sprite = GenericTextSprite("(press ESC to cancel)", self.Width / 2, 30, FontSize = 32, Color = Colors.Blue, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
    def HandleKeyPressed(self, Key):
        if Key == pygame.K_ESCAPE:
            self.App.PopScreen(self)
            return
        if Key in (280, 265): # pgUp
            self.SavePanel.ClickUpArrow()
            return
        if Key in (281, 259): # pgDown
            self.SavePanel.ClickDownArrow()
            return
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.DeepSprites.draw(self.BackgroundSurface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        


class SaveScreen(Screen.TendrilsScreen):
    SavePanelX = 0
    SavePanelY = 110
    SavePanelWidth = 800
    SavePanelHeight = 450
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        self.HoldingKey = None
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.RenderInitialScreen()
        self.PlaySaveMusic()
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.DeepSprites.draw(self.BackgroundSurface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
        
    def PlaySaveMusic(self):
        #Music.PlaySongByName("SavePoint")
        self.SummonSong("SavePoint")
    def RenderInitialScreen(self):
        self.DrawBackground()
        self.SavePanel = SavePanel(self, self.SavePanelX, self.SavePanelY, self.SavePanelWidth,
                                   self.SavePanelHeight, 1)
        self.SubPanes.append(self.SavePanel)
    def DrawBackground(self):
        Image = GetBackgroundArt()
        BigBiff = GenericImageSprite(Image, 0, 0)
        self.DeepSprites.add(BigBiff)
        
        #
        Sprite = GenericTextSprite("Welcome to the Temple of Kibo",self.Width / 2, 0, FontSize = 32, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        #
        Sprite = GenericTextSprite("Are you ready to be saved?", self.Width / 2, 25, FontSize = 32, Color = Colors.Blue, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        #
        Sprite = GenericTextSprite("(Click on a save slot, type a name, and press ENTER)", self.Width / 2, 53, FontSize = 24, Color = Colors.Green, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        #
        Sprite = LineSprite(0, self.SavePanelY-1, 800, self.SavePanelY - 1)
        self.AddBackgroundSprite(Sprite)
        #Sprite = LineSprite(0, self.SavePanelY + self.SavePanelHeight + 1, 800, self.SavePanelY + self.SavePanelHeight + 1)
        #self.AddBackgroundSprite(Sprite)
        
        #
        #ExitImage = FancyAssBoxedText("Exit")
        #self.ExitSprite = GenericImageSprite(ExitImage, 740, 50)
        self.ExitSprite = FancyAssBoxedSprite("Exit", 740, 50, HighlightIndex = 1, BackColor = (11,11,11))
        self.AddForegroundSprite(self.ExitSprite) # Put in foreground so we can collide with it easily

    def HandleKeyPressed(self, Key):
        if Key == pygame.K_ESCAPE:
            if self.SavePanel.EditGameIndex!=None:
                self.SavePanel.CancelCurrentEdit()
                self.SavePanel.Redraw()
                return
            self.App.PopScreen(self)
            return
        # X is for eXit:
        if Key == ord("x") and self.SavePanel.EditGameIndex == None:
            if self.SavePanel.EditGameIndex!=None:
                self.SavePanel.CancelCurrentEdit()
                self.SavePanel.Redraw()
                return                
            self.App.PopScreen(self)
            return
                
        if Key in range(256) and chr(Key) in LegalSavedGameLetters:
            self.HoldingKey = Key
            self.KeyRepeatTime = KeyRepeatDelay                        
            Char = chr(Key)
            KeyMods = pygame.key.get_mods()
            if (KeyMods & pygame.KMOD_LSHIFT) or (KeyMods & pygame.KMOD_RSHIFT):
                Char = string.translate(Char, ShiftTranslate)
            self.SavePanel.HandleLetterPressed(Char)
            return
        if Key == 8:
            self.HoldingKey = Key
            self.KeyRepeatTime = KeyRepeatDelay                        
            self.SavePanel.HandleBackspace()
        if Key == 13:
            self.SavePanel.HandleEnter()
        if self.SavePanel.EditGameIndex==None:
            if Key in (280, 265): # pgUp
                self.SavePanel.ClickUpArrow()
                return
            if Key in (281, 259): # pgDown
                self.SavePanel.ClickDownArrow()
                return
            
    def Update(self):
        if self.HoldingKey:
            self.KeyRepeatTime -= 1
            if self.KeyRepeatTime <= 0:
                Pressed = pygame.key.get_pressed()
                if Pressed[self.HoldingKey]:
                    self.HandleKeyPressed(self.HoldingKey)
                    self.KeyRepeatTime = MaxKeyRepeatTime
                else:
                    self.HoldingKey = None
            
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite == self.ExitSprite:
            self.App.PopScreen(self)
            return                                       
        