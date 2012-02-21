"""
Ah, the first screen of a new game!  Here we give the user a few options: Song difficulty,
and initial party.  
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

IntroTexts = ["Now, it is the beginning of a fantastic story!  Let's make a journey to the cave of monsters!  Good luck!",
              "VisualShock! SpeedShock! SoundShock! Now is time to the 68000 heart on fire!",
              "An emergency massage is received from Space Transport Dagal...",
              "To clear all the levels, you must be an all-rounder with highly technical DJ skill.",
              "It is the 00s and there is time for TENDRILS."
              ]
NextIntroNumber = random.randrange(len(IntroTexts))

AllowedChars = "abcdefghijklmnopqrstuvwxyz1234567890 .!"
ShiftTranslate = string.maketrans("abcdefghijklmnopqrstuvwxyz1","ABCDEFGHIJKLMNOPQRSTUVWXYZ!")

NameFontSize = 24
NameColor = Colors.Yellow

class IntroTextSprite(GenericImageSprite):
    def __init__(self):
        global NextIntroNumber
        Str = IntroTexts[NextIntroNumber]
        NextIntroNumber = (NextIntroNumber+1)%len(IntroTexts)
        Image = TaggedRenderer.RenderToImage("<CENTER>%s"%Str, 200)
        GenericImageSprite.__init__(self, Image, 600, 600)
        self.Y = self.rect.top
    def Update(self, Dummy):
        self.Y -= 0.5
        self.rect.top = self.Y
        if self.rect.bottom < 0:
            self.kill()

class FirstScreen(Screen.TendrilsScreen):
    FirstClassY = 290
    ClassHeight = 80
    MaxWordLen = 10
    def __init__(self, App, Args):
        Screen.TendrilsScreen.__init__(self,App)
        self.SongY = 550 # The y-coordinate where the song name appears (above our done button)
        self.HoldingKey = None
        self.IntroTextSprites = pygame.sprite.Group()
        self.IntroPause = 0
        self.RenderInitialScreen()
    def RenderInitialScreen(self):
        self.DrawBackground()
        self.SongSprites = pygame.sprite.Group()
        self.DrawSongButtons()
        self.ClassSprites = pygame.sprite.Group()
        self.ClassSpritesForPlayer = []
        self.NameSprites = pygame.sprite.Group()
        self.EditName = None
        self.CursorSprite = None
        self.DrawNameButtons()        
        self.DrawClassButtons()
        self.DrawDecorations()
        # Done button:
        self.ButtonSprites = pygame.sprite.Group()
        self.DoneSprite = FancyAssBoxedSprite("Let's Go!", 660, 550, HighlightIndex = 6, BackColor = Colors.AlmostBlack)
        self.ButtonSprites.add(self.DoneSprite)
        self.AddAnimationSprite(self.DoneSprite)
        self.SummonSong("startout")
    def DrawDecorations(self):
        self.MegaSprite = Magic.MagicSprite(540, 150, "MegaDance", 4, 20)
        self.MegaSprite.LoopFlag = 1
        self.AddForegroundSprite(self.MegaSprite)
    def SetMegaSpeed(self):
        Value = Global.Party.Options["SongDifficulty"]
        if Value == 0:
            self.MegaSprite.MaxImageDelay = 25
        elif Value == 1:
            self.MegaSprite.MaxImageDelay = 16
        else:
            self.MegaSprite.MaxImageDelay = 9
    def DrawBackground(self):
        TileNumber = Resources.Tiles.get("Misc", 1)
        Image = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber))
        Surface = GetTiledImage(800, 600, Image)
        pygame.draw.rect(Surface, Colors.Black, (20, 20, 555, 165), 0)
        pygame.draw.rect(Surface, Colors.White, (20, 20, 555, 165), 1)
        pygame.draw.rect(Surface, Colors.Black, (20, 200, 555, 393), 0)
        pygame.draw.rect(Surface, Colors.White, (20, 200, 555, 393), 1)
        pygame.draw.rect(Surface, (0,44,0), (600, 0, 555, 610), 0)
        pygame.draw.rect(Surface, Colors.White, (600, 0, 555, 610), 1)
        BackSprite = GenericImageSprite(Surface, 0, 0)
        
        self.DeepSprites.add(BackSprite)
        ###
##        Str = "<CENTER><CN:GREY>Now, it is the beginning of a fantastic story!\nLet's make a journey to the cave of monsters!\nGood luck!"
##        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 200)
##        Sprite = GenericImageSprite(Image, 600, 440)
        #Sprite.rect.left -= Sprite.rect.width / 2
        #self.AddBackgroundSprite(Sprite)
        #
        Str = "<CN:BRIGHTGREEN>1.</C>  Choose the battle difficulty."
        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 600, FontSize = 32)
        Sprite = GenericImageSprite(Image, 50, 20)
        self.AddBackgroundSprite(Sprite)
        Str = "If you are new to rhythm games, choose <CN:GREEN>wimpy</C>.\nSelect <CN:GREEN>mania</c> if you possess <CN:RED>mad skills</C>."
        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 600, FontSize = 24)
        Sprite = GenericImageSprite(Image, 50, 65)
        self.AddBackgroundSprite(Sprite)
        #
        Str = "<CN:BRIGHTGREEN>2.</C>  Build a starting party."
        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 600, FontSize = 32)
        Sprite = GenericImageSprite(Image, 50, 200)
        self.AddBackgroundSprite(Sprite)
        #
        Str = "<CN:LIGHTGREY>Click character's current name to rename"
        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 600, FontSize = 24)
        Sprite = GenericImageSprite(Image, 50, 230)
        self.AddBackgroundSprite(Sprite)
        
        Str = "<CN:GREY>(If this is your first game, the default party should work fine)"
        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 600, FontSize = 24)
        Sprite = GenericImageSprite(Image, 50, 249)
        self.AddBackgroundSprite(Sprite)
        #
        # Front, left flank, etc:
        Y = self.FirstClassY
        for Label in range(1, 5):
            Str = PlayerLabelNames[Label]
            Sprite = GenericTextSprite(Str+":", 10, Y, Colors.Blue, FontSize = NameFontSize)
            Sprite.rect.right = 120
            self.AddBackgroundSprite(Sprite)
            Y += self.ClassHeight
    def DrawNameButtons(self):
        Y = self.FirstClassY
        for Label in range(1, 5): #Index in range(len(Global.Party.Players)):
            Index = PlayerLabelToPlayerIndex[Label]
            Player = Global.Party.Players[Index]
            NameSprite = GenericTextSprite(Player.Name, 130, Y, NameColor, FontSize = NameFontSize)
            NameSprite.Player = Player
            self.NameSprites.add(NameSprite)
            self.AddForegroundSprite(NameSprite)
            Y += self.ClassHeight
    def DrawClassButtons(self):
        Y = self.FirstClassY + 25
        for Sprite in self.ClassSprites.sprites():
            Sprite.kill()
        for Label in range(1, 5): #Index in range(len(Global.Party.Players)):
            Index = PlayerLabelToPlayerIndex[Label]
            Player = Global.Party.Players[Index]
            #self.ClassSpritesForPlayer.append([])
            X = 50
            for ClassName in Critter.PlayerClassNames:
                if Player.Species.Name == ClassName:
                    DrawBox = 1
                else:
                    DrawBox = 0
                Sprite = FancyAssBoxedSprite(ClassName, X, Y, DrawBox = DrawBox)
                Sprite.Player = Player
                X += Sprite.rect.width + 20
                self.AddBackgroundSprite(Sprite)
                self.ClassSprites.add(Sprite)
            Y += self.ClassHeight
    def DrawSongButtons(self):
        X = 200
        Y = 130
        for Sprite in self.SongSprites.sprites():
            Sprite.kill()
        for (Name, Value) in (("Wimpy",0), ("Normal",1), ("MANIA!",2)):
            Sprite = OptionsScreen.RadioButtonSprite(Name, X, Y, "SongDifficulty", Value)
            X += 100
            self.SongSprites.add(Sprite)
            self.AddForegroundSprite(Sprite)
    def ClickDone(self):
        # Easter egg:
        EasterEgg = 1
        for Player in Global.Party.Players:
            if Player.Name.lower() != "melvin":
                EasterEgg = 0
        if EasterEgg:
            Global.Party.Gold = 666
            Str = "<BIG><CENTER>MELVIN!</CENTER></BIG>\n\n\n<CN:ORANGE>Team Melvin rides again!\n\n\
<CN:BRIGHTGREEN>Melvin:<CN:PURPLE>We have to save Melvin!\n\
<CN:BRIGHTGREEN>Melvin:<CN:PURPLE>Where is Melvin?\n\
<CN:BRIGHTGREEN>Melvin:<CN:PURPLE>MELVIN!"
            Global.App.ShowNewDialog(Str, CustomButtons = ("Melvin", "Melvin?", "Melvin!"))
        Global.App.PopScreen(self)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if Key == ord("g") and self.EditName == None:
            self.ClickDone()
            return
        if self.EditName:
            if Key in (303, 304):
                return # shift keys
            if Key is pygame.K_ESCAPE or Key == 13:
                self.FinishNameEdit()
                return
            if Key == 8:
                self.HoldingKey = Key
                self.KeyRepeatTime = KeyRepeatDelay
                if not len(self.EditName.Player.Name):
                    Resources.PlayStandardSound("Heartbeat.wav")
                    return
                self.EditName.Player.Name = self.EditName.Player.Name[:-1]
                self.UpdateWord()
                return
            if Key in range(256) and chr(Key) in AllowedChars:
                self.HoldingKey = Key
                self.KeyRepeatTime = KeyRepeatDelay
                Char = chr(Key)
                KeyMods = pygame.key.get_mods()
                if (KeyMods & pygame.KMOD_LSHIFT) or (KeyMods & pygame.KMOD_RSHIFT):
                    Char = string.translate(Char, ShiftTranslate)
                if len(self.EditName.Player.Name) >= self.MaxWordLen:
                    Resources.PlayStandardSound("Heartbeat.wav")
                    return
                self.EditName.Player.Name += Char
                self.UpdateWord()
                return
    def Update(self):
        if len(self.IntroTextSprites.sprites()) < 2:
            self.IntroPause -= 1
            if self.IntroPause <= 0:
                Sprite = IntroTextSprite()
                self.AddForegroundSprite(Sprite)
                self.IntroPause = 480
        if self.HoldingKey:
            self.KeyRepeatTime -= 1
            if self.KeyRepeatTime <= 0:
                Pressed = pygame.key.get_pressed()
                if Pressed[self.HoldingKey]:
                    self.HandleKeyPressed(self.HoldingKey)
                    self.KeyRepeatTime = MaxKeyRepeatTime
                else:
                    self.HoldingKey = None
    def HandleClassClick(self, Sprite):
        "Click on a class name -> change that player's class"
        self.FinishNameEdit()
        NewClass = Critter.ClassNameToClass[Sprite.Text]
        Sprite.Player.ChangeClass(NewClass)
        self.DrawClassButtons()
        Resources.PlayStandardSound("Boop2.wav")
        self.Redraw()
    def HandleNameClick(self, NameSprite):
        "Click on a player name -> start editing it"
        self.FinishNameEdit()
        self.EditName = NameSprite
        self.EditName.OldName = self.EditName.Player.Name
        self.CursorSprite = CursorSprite(self, NameSprite.rect.right + 3, NameSprite.rect.top, Colors.White, 10, 23)
        self.AddAnimationSprite(self.CursorSprite)
    def UpdateWord(self):
        "Update the player-name currently being edited"
        if not self.EditName:
            return
        (X,Y) = (self.EditName.rect.left, self.EditName.rect.top)
        self.EditName.image = TextImage(self.EditName.Player.Name, NameColor, FontSize = NameFontSize)
        self.EditName.rect = self.EditName.image.get_rect()
        self.EditName.rect.left = X
        self.EditName.rect.top = Y
        self.CursorSprite.rect.left = self.EditName.rect.right + 3
    def FinishNameEdit(self):
        if not self.EditName:
            return
        # Restore old name, if the name is empty:
        if not self.EditName.Player.Name.strip():
            self.EditName.Player.Name = self.EditName.OldName
            self.UpdateWord()
        # Ok, kill the cursor and un-select the name:
        if self.CursorSprite:
            self.CursorSprite.kill()
        self.EditName = None
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, try clicking wimpy/normal/mania song difficulty buttons:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.SongSprites)
        if Sprite:
            self.FinishNameEdit()
            Sprite.HandleClick(Position)
            self.SetMegaSpeed()
            self.DrawSongButtons()
            self.Redraw()
            return
        # Now, try clicking on classes:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ClassSprites)
        if Sprite:
            self.HandleClassClick(Sprite)
            return
        # Now, try clicking on names:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.NameSprites)
        if Sprite:
            self.HandleNameClick(Sprite)
            return
        # Done button:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            self.ClickDone()
            return
            
        
