"""
This screen lets the player pick a song, or set up a playlist, for freestyle dance play.
Top: Title, and dance level selector
Bottom: Song scroller, and buttons
"""
from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import os
import time
import string
import Party
import OptionsScreen
import Critter
import Magic
import PracticeScreen

Parties = [("Bard", "Cleric", "Fighter", "Mage"),
           ("Ninja", "Bard", "Cleric", "Summoner"),
           ("Fighter", "Fighter", "Fighter", "Cleric"),
           ("Ninja", "Cleric", "Fighter", "Mage"),
           ("Cleric", "Mage", "Ninja", "Summoner"),
           ]
           

class FreePlayScreen(Screen.TendrilsScreen):
    SongSpriteListY = 300
    def __init__(self):
        Screen.TendrilsScreen.__init__(self,Global.App)
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))
        self.SongY = 310 # The y-coordinate where the song name appears (above our done button)
        self.ScrollRow = 0
        self.RowsAtOnce = 15
        self.ClickedSongSprite = None
        self.ClickedSongTime = None
        self.SpeedDescriptionSprite = None
        self.CurrentSortOrder = "Name"
        self.ButtonSprites = pygame.sprite.Group()
        self.SortButtons = pygame.sprite.Group()
        self.RenderInitialScreen()
    def RenderInitialScreen(self):
        self.DrawBackground() 
        self.SpeedSprites = pygame.sprite.Group()
        self.DrawSpeedControls()
        self.SongList = Global.MusicLibrary.GetBattleSongList()
        self.SongSprites = pygame.sprite.Group()
        self.DrawSongList()
        
        self.DrawButtons()
        self.Redraw()
        self.SummonSong("mariocave")
    def DrawButtons(self):
        ButtonX = 710
        Sprite = FancyAssBoxedSprite("Random", ButtonX, 420, HighlightIndex = 0)
        self.ButtonSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        ##
        Sprite = FancyAssBoxedSprite("Triple", ButtonX, 465, HighlightIndex = 0)
        self.ButtonSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        ##
        Sprite = FancyAssBoxedSprite("Nonstop!", ButtonX, 510, HighlightIndex = 0)
        self.ButtonSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        ##
        Sprite = FancyAssBoxedSprite("Exit", ButtonX, 555, HighlightIndex = 1)
        self.ButtonSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
    def DrawSongList(self):
        "Draw the scrolled list of available songs."
        # Create a sprite for each one:
        self.SongSpriteList = []
        for Song in self.SongList:
            Str = "<CN:BRIGHTGREEN>%s</C>"%Song.Name
            if Song.SourceGame:
                Str += " (<CN:YELLOW>%s</C>)"%Song.SourceGame
            if Song.Author:
                Str += " [<CN:BRIGHTRED>%s</C>]"%Song.Author
            Image = TaggedRenderer.RenderToImage(Str)
            Sprite = GenericImageSprite(Image, 0, 0)
            Sprite.Song = Song
            self.SongSpriteList.append(Sprite)
        self.SortSongSpriteList()
        # Then, call the standard layout procedure:
        self.LayoutSongList()
    def SortSongSpriteList(self):
        List = []
        for Sprite in self.SongSpriteList:
            if self.CurrentSortOrder == "Name":
                Name = Sprite.Song.Name
            elif self.CurrentSortOrder == "Author":
                Name = Sprite.Song.Author
            elif self.CurrentSortOrder == "Game":
                Name = Sprite.Song.SourceGame
            else:
                Name = Sprite.Song.Name
            if Name:
                Name = Name.lower()                                
            List.append((Name, Sprite))
        List.sort()
        self.SongSpriteList = []
        for (Name, Sprite) in List:
            self.SongSpriteList.append(Sprite)
    def LayoutSongList(self):
        for Sprite in self.SongSprites.sprites():
            Sprite.kill()
        Index = self.ScrollRow
        Y = self.SongSpriteListY 
        ScrollDown = 0
        while (1):
            if Index >= len(self.SongSpriteList):
                break
            if Y + self.SongSpriteList[Index].rect.height > 600:
                ScrollDown = 1
                break
            Sprite = self.SongSpriteList[Index]
            Sprite.rect.top = Y
            Sprite.rect.left = 20
            self.SongSprites.add(Sprite)
            self.AddBackgroundSprite(Sprite)
            Y += 20
            Index += 1
        if hasattr(self, "UpArrowSprite"):
            self.UpArrowSprite.kill()
        if hasattr(self, "DownArrowSprite"):
            self.DownArrowSprite.kill()
        if self.ScrollRow:
            self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, 650, 310)
            self.AddForegroundSprite(self.UpArrowSprite)
        if ScrollDown:
            self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, 650, 580)
            self.AddForegroundSprite(self.DownArrowSprite)
        self.Redraw()
    def Update(self):
        time.sleep(0.01)
    def SetMegaSpeed(self):
        Value = Global.Party.Options["SongDifficulty"]
        if Value == 0:
            self.MegaSprite.MaxImageDelay = 25
        elif Value == 1:
            self.MegaSprite.MaxImageDelay = 16
        else:
            self.MegaSprite.MaxImageDelay = 9
    def DrawBackground(self):
        TileNumber = Resources.Tiles.get("FreePlay", 1)
        Image = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber))
        Surface = GetTiledImage(800, 600, Image)
        self.DeepSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(self.DeepSprite)
        
        Str = "<CENTER>Tendrils Freestyle"
        Image = TaggedRenderer.RenderToImage(Str, FontSize = 32, WordWrapWidth = 800)
        Sprite = GenericImageSprite(Image, 400, 3)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        #
        Str = """<CENTER>Instructions:</CENTER>\nDouble-click a song to start.\n\n<CN:YELLOW>[Random]</C> picks a random song.  \
<CN:YELLOW>[Triple]</C> starts a course of three random songs.  And <CN:YELLOW>[Nonstop!]</C> plays everything. \
\n\n(You can add new songs to the Music\\Battle directory.  Tendrils groks .dwi and .sm files)"""
        Image = TaggedRenderer.RenderToImage(Str, FontSize = 20, WordWrapWidth = 400)
        Sprite = GenericImageSprite(Image, 400, 40)
        #Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        ##
        Sprite = LineSprite(0, self.SongSpriteListY - 1, 800, self.SongSpriteListY - 1)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(670, self.SongSpriteListY - 1, 670, 600)
        self.AddBackgroundSprite(Sprite)
        self.RenderSortButtons()
    def RenderSortButtons(self):
        for Sprite in self.SortButtons.sprites():
            Sprite.kill()
        ButtonSprite = FancyAssBoxedSprite("Name", 150, 240, DrawBox = (self.CurrentSortOrder == "Name"))
        self.AddBackgroundSprite(ButtonSprite)
        self.SortButtons.add(ButtonSprite)
        self.ButtonSprites.add(ButtonSprite)
        ButtonSprite = FancyAssBoxedSprite("Author", 250, 240, DrawBox = (self.CurrentSortOrder == "Author"))
        self.AddBackgroundSprite(ButtonSprite)
        self.SortButtons.add(ButtonSprite)
        self.ButtonSprites.add(ButtonSprite)
        ButtonSprite = FancyAssBoxedSprite("Game", 350, 240, DrawBox = (self.CurrentSortOrder == "Game"))
        self.AddBackgroundSprite(ButtonSprite)
        self.SortButtons.add(ButtonSprite)
        self.ButtonSprites.add(ButtonSprite)
        
        
    def DrawSpeedControls(self):
        "Wimpy/normal/Madia speed buttons, with attached dancer"
        X = 20
        Y = 80
        for Sprite in self.SpeedSprites.sprites():
            Sprite.kill()
        for (Name, Value) in (("Wimpy",0), ("Normal",1), ("MANIA!",2)):
            Sprite = OptionsScreen.RadioButtonSprite(Name, X, Y, "SongDifficulty", Value)
            X += 100
            self.SpeedSprites.add(Sprite)
            self.AddForegroundSprite(Sprite)
        if not hasattr(self, "MegaSprite"):
            self.MegaSprite = Magic.MagicSprite(350, 80, "MegaDance", 4, 20)
            self.MegaSprite.LoopFlag = 1
            self.AddForegroundSprite(self.MegaSprite)
        if self.SpeedDescriptionSprite:
            self.SpeedDescriptionSprite.kill()
        Value = Global.Party.Options.get("SongDifficulty",1)
        if Value == 1:
            Str = "<CN:BRIGHTGREEN>You get make the *heavy space* Orz ships and use *GO! GO!* for the *dancing*!"
        elif Value == 2:
            Str = "<CN:BRIGHTRED>*Frumple* be *round* and yet *lumpy*. So bad!!!"
        else:
            Str = "<CN:WHITE>Hello! Hello! Next I will *spit* *slow time* words to you for better *dancing*."
        Image = TaggedRenderer.RenderToImage(Str, FontSize = 18, WordWrapWidth = 300)
        self.SpeedDescriptionSprite= GenericImageSprite(Image, 10, 120)
        #self.SpeedDescriptionSprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(self.SpeedDescriptionSprite)

    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        self.SummonSong("mariocave")
    def StartPractice(self, Song):
        # Randomize party.  (There's no current game, so it's all in good fun)
        ClassNames = random.choice(Parties)
        for Index in range(4):
            Global.Party.Players[Index] = Critter.Player("Melvin", getattr(Critter, ClassNames[Index]))
        # Show screen:
        Global.App.ShowPracticeScreen(PracticeScreen.PracticeStates.Sparring, Song)
    def IsOKRandomSong(self, Song):
        return (os.path.split(Song.SongPath)[1]!="MetalGear.xm")
    def ClickRandom(self):
        while (1):
            Song = random.choice(self.SongList)
            # don't use the practice song:
            if self.IsOKRandomSong(Song):
                break
        self.StartPractice(Song)
    def ClickTriple(self):
        List = self.SongList[:]
        Triplet = []
        while len(Triplet)<3:
            Song = random.choice(List)
            if self.IsOKRandomSong(Song):
                Triplet.append(Song)
            List.remove(Song) # Don't re-pick same one
        self.StartPractice(Triplet)
    def ClickNonstop(self):
        List = self.SongList[:]
        random.shuffle(List)
        for Entry in List[:]:
            if not self.IsOKRandomSong(Entry):
                List.remove(Entry)
        self.StartPractice(List)
    def HandleKeyPressed(self, Key):
        "Handle keystrokes - shortcuts for buttons, and pgup/pgdn for list"
        if Key == ord("x"): # eXit
            Global.App.PopScreen(self)
        elif Key == ord("r"): # Random
            self.ClickRandom()
        elif Key == ord("t"): # Triple
            self.ClickTriple()
        elif Key == ord("n"): # Music.  Non-stop.
            self.ClickNonstop()
        elif Key in (280, 265):
            self.ScrollSongList(-1)
            return
        elif Key in (281, 259):
            self.ScrollSongList(1)
            return
    def DoubleClickSong(self, Sprite):
        self.StartPractice(Sprite.Song)
    def ChangeSortOrder(self, NewOrder):
        if NewOrder == self.CurrentSortOrder:
            return
        Resources.PlayStandardSound("Bleep6.wav")
        self.CurrentSortOrder = NewOrder
        self.SortSongSpriteList()
        self.LayoutSongList()
        self.RenderSortButtons()
        self.Redraw()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # Did they click a song?
        Sprite = pygame.sprite.spritecollideany(Dummy,self.SongSprites)
        if Sprite:
            Now = time.clock()
            if Sprite == self.ClickedSongSprite and (Now - self.ClickedSongTime) < 2.0:
                self.DoubleClickSong(Sprite)
            else:
                self.ClickedSongSprite = Sprite
                self.ClickedSongTime = Now
        # Now, try clicking wimpy/normal/mania song difficulty buttons:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.SpeedSprites)
        if Sprite:
            Sprite.HandleClick(Position)
            self.SetMegaSpeed()
            self.DrawSpeedControls()
            self.Redraw()
            return
        # Buttons:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            if Sprite.Text == "Name":
                self.ChangeSortOrder("Name")
            elif Sprite.Text == "Author":
                self.ChangeSortOrder("Author")
            elif Sprite.Text == "Game":
                self.ChangeSortOrder("Game")
            elif Sprite.Text == "Exit":
                Global.App.PopScreen(self)
            elif Sprite.Text == "Random":
                self.ClickRandom()
            elif Sprite.Text == "Triple":
                self.ClickTriple()
            elif Sprite.Text == "Nonstop!":
                self.ClickNonstop()
        # Ok, how about the scrolly buttons?
        Sprite = pygame.sprite.spritecollideany(Dummy, self.ForegroundSprites)
        if Sprite and hasattr(self, "UpArrowSprite") and Sprite == self.UpArrowSprite:
            self.ScrollSongList(-1)
        if Sprite and hasattr(self, "DownArrowSprite") and Sprite == self.DownArrowSprite:
            self.ScrollSongList(1)
    def ScrollSongList(self, Direction):
        self.ScrollRow += Direction*12
        if self.ScrollRow > len(self.SongList) - self.RowsAtOnce:
            self.ScrollRow = len(self.SongList) - self.RowsAtOnce
        if self.ScrollRow < 0:
            self.ScrollRow = 0
        self.LayoutSongList()
        self.Redraw()
        