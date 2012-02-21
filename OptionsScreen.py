"""
The Options screen lets the player change some game options:
- Song difficulty
- Sound effect volume
- (hopefully not too much else!)
"""

from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import Critter

class RadioButtonSprite(GenericImageSprite):
    def __init__(self, Text, X, Y, OptionName, OptionValue):
        self.OptionName = OptionName
        self.OptionValue = OptionValue
        if Global.Party.Options.get(OptionName) == OptionValue:
            Checked = 1
        else:
            Checked = 0
        ##print "Option %s: %s vs %s"%(OptionName, Global.Party.Options.get(OptionName), OptionValue)
        Image = FancyAssBoxedText(Text, DrawBox = Checked)
        GenericImageSprite.__init__(self, Image, X, Y)
    def HandleClick(self, Position):
        OldValue = Global.Party.Options[self.OptionName]
        if OldValue != self.OptionValue:
            Global.Party.Options[self.OptionName] = self.OptionValue
            Resources.PlayStandardSound("Bleep3.wav")
        print "CLICKED!"

class SliderSprite(GenericImageSprite):
    def __init__(self, X, Y, OptionName):
        self.OptionName = OptionName        
        Image = pygame.Surface((250, 25))
        GenericImageSprite.__init__(self, Image, X, Y)
        self.Draw()
    def Draw(self):
        Value = Global.Party.Options[self.OptionName]
        X = 10 + Value * 2
        self.image.fill(Colors.Black)
        pygame.draw.line(self.image, Colors.White, (10, 13), (210, 13))
        pygame.draw.rect(self.image, Colors.Green, (X-5, 0, 11, self.rect.height), 0)
        Image = TextImage(str(Value), Colors.Blue)
        self.image.blit(Image, (220, 13 - Image.get_rect().height / 2))
    def HandleClick(self, Position):
        X = Position[0] - (self.rect.left + 10)
        if (X>200):
            X = 200
        if (X<0):
            X = 0
        Value = X / 2
        Global.Party.Options[self.OptionName] = Value
        Resources.PlayStandardSound("Kill.wav")
        #self.Draw()
        
class OptionsScreen(Screen.TendrilsScreen):    
    OptionHeight = 100
    FirstOptionY = 80
    LabelHeight = 20
    LabelX = 270
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        #################################
        # MINOR MAGIC to make the underlying stuff show:
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.BackgroundSurface.blit(self.App.BackgroundSurface,(0,0))
        self.BackgroundSurface.blit(self.App.Surface,(0,0))
        #################################        
        self.RenderInitialScreen()
        #self.SummonSong("house")
    def RedrawBackground(self):
        self.BackgroundSprites.draw(self.BackgroundSurface)
        
    def RenderInitialScreen(self):
        self.DrawBackground()
        self.RadioSprites = pygame.sprite.Group()
        self.DrawOptions()
    def DrawOptions(self):
        # Kill old sprites:
        for Sprite in self.RadioSprites.sprites():
            Sprite.kill()
        ###############
        Y = self.FirstOptionY# + self.LabelHeight
        # Song difficulty: 0 wimpy, 1 normal, 2 mania
        Difficulty = Global.Party.Options.get("SongDifficulty", None)
        if Difficulty == None:
            Global.Party.Options["SongDifficulty"] = 1
        Sprite = RadioButtonSprite("Wimpy", 270, Y, "SongDifficulty", 0)
        self.RadioSprites.add(Sprite)
        self.AddForegroundSprite(Sprite)
        Sprite = RadioButtonSprite("Normal", 370, Y, "SongDifficulty", 1)
        self.RadioSprites.add(Sprite)
        self.AddForegroundSprite(Sprite)
        Sprite = RadioButtonSprite("MANIA!", 470, Y, "SongDifficulty", 2)
        self.RadioSprites.add(Sprite)
        self.AddForegroundSprite(Sprite)
        ###############
        # SFX volume: 0 to 255
        Y = self.VolumeY #FirstOptionY + self.OptionHeight + self.LabelHeight
        Volume = Global.Party.Options.get("SFXVolume", None)
        if Volume == None:
            Global.Party.Options["SFXVolume"] = 50
        VolumeSlider = SliderSprite(270, Y, "SFXVolume")
        self.RadioSprites.add(VolumeSlider)
        self.AddForegroundSprite(VolumeSlider)
    def DrawBackground(self):
        BoxWidth = 300
        BoxHeight = 450
        Image = pygame.Surface((BoxWidth, BoxHeight))
        Image.fill((11,11,11))
        pygame.draw.rect(Image, Colors.Grey, (0, 0, BoxWidth, BoxHeight), 8)
        pygame.draw.rect(Image, Colors.White, (3, 3, BoxWidth-6, BoxHeight-6), 1)
        BigSquare = GenericImageSprite(Image, 400 - BoxWidth / 2, 300 - BoxHeight / 2)
        self.AddBackgroundSprite(BigSquare)
        #
        Y = BigSquare.rect.top + 5
        Image = TextImage("OPTIONS", FontSize = 36)
        BigSquare.image.blit(Image, ((BoxWidth - Image.get_rect().width) / 2, Y - BigSquare.rect.top))
        Y += Image.get_rect().height + 10 #Sprite.rect.height + 10
        #
        Image = TextImage("(Press ESC when done)", FontSize = 24)
        BigSquare.image.blit(Image, ((BoxWidth - Image.get_rect().width) / 2, Y - BigSquare.rect.top))
        Y += Image.get_rect().height + 40 #Sprite.rect.height + 10
        #
        Image = TextImage("Song Difficulty:")
        BigSquare.image.blit(Image, ((BoxWidth - Image.get_rect().width) / 2, Y - BigSquare.rect.top))
        Y += Image.get_rect().height + 10 #Sprite.rect.height + 10
        self.FirstOptionY = Y + 5
        Y += 80
        #
        Image = TextImage("SFX Volume:")
        BigSquare.image.blit(Image, ((BoxWidth - Image.get_rect().width) / 2, Y - BigSquare.rect.top))
        Y += Image.get_rect().height + 10 #Sprite.rect.height + 10
        self.VolumeY = Y + 5
        Y += 80
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.RadioSprites)
        if not Sprite:
            return
        Sprite.HandleClick(Position)
        self.DrawOptions()
        self.Redraw()
    def HandleKeyPressed(self,Key):
        if (Key is pygame.K_ESCAPE or Key == Keystrokes.Enter or Key == 271): # 271 is the num-pad enter
            self.App.PopScreen(self)
