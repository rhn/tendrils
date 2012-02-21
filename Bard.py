"""
Bard powers:
If a bard is in the party, you get some control over which songs are used in (non-boss)
battles; you also get to tweak the song speed downward a bit if the bard is
particularly charismatic.  The JukeboxDialog lets the users make their selections.
Also: Bards let the party regain MP over time. 
"""
from Utils import *
from Constants import *
import Screen
import MessagePanel
import Music
import Global
import NewDialogScreen
import Critter
import time

def ApplyBardPower(Party):
    """
    Bards provide BardPower with every step through the maze (and even during battle).
    Once the party has accumulated enough BardPower, everyone gains 1 mp.  Bards are useful.
    """
    for Player in Party.Players:
        if Player.IsAlive() and Player.Species.Name == Critter.ClassNames.Bard:
            Party.BardPower += max(0, (Player.CHA - 15)) + Player.Level 
    while Party.BardPower > 50:
        Party.BardPower -= 50
        for Player in Party.Players:
            if Player.IsDead():
                continue
            Player.MP = min(Player.MP + 1, Player.MaxMP)

def GetBattleSong(Level, Callback):
    """
    Main entry point for a function - choose a battle song appropriate to the
    dungeon level (either randomly, or with help from the user), and then call
    our callback function, passing the song name.
    """
    Choices = Global.MusicLibrary.GetPossibleBattleSongs(Level)
    MaxBardCHA = 0
    TheBard = None
    # Use the maximum CHA of any (living) bard in the party:
    for Player in Global.Party.Players:
        if Player.IsDead():
            continue        
        if Player.Species.Name == Critter.ClassNames.Bard:
            if Player.CHA > MaxBardCHA:
                TheBard = Player
                MaxBardCHA = Player.CHA
    if MaxBardCHA == 0:
        apply(Callback, (random.choice(Choices),1.0))
        return random.choice(Choices)
    # Aha!  There's a bard in the party.  They get choices:
    if (MaxBardCHA <= 18): # Note: Bards start at 16
        NumChoices = 2
    elif (MaxBardCHA <= 24):
        NumChoices = 3
    elif (MaxBardCHA <= 28):
        NumChoices = 4
    else:
        NumChoices = 5
    # Don't give them EVERY choice.  (If there's 5 songs, show at most 4)
    NumChoices = max(min(len(Choices)-1, NumChoices), 1)
    random.shuffle(Choices)
    Choices = Choices[:NumChoices]
    NewScreen = JukeboxScreen(Global.App, TheBard, Choices, Callback)
    Global.App.PushNewScreen(NewScreen)

class JukeboxScreen(NewDialogScreen.DialogScreen):
    "Dialog box shown for bards picking a battle song"
    TimeLimit = 15.0
    RowsAtOnce = 50
    def __init__(self, App, TheBard, Choices, Callback):
        self.TheBard = TheBard
        self.Choices = Choices
        self.TempoMultiplier = 1.0
        # We use the standard DialogScreen scaffolding to invoke our "ReturnProperName"
        # callback, at which point we invoke the REAL function, self.TrueCallback
        self.TrueCallback = Callback
        Text = self.GetText()
        self.StartTime = time.clock()
        ButtonLabels = self.GetButtonLabels()
        NewDialogScreen.DialogScreen.__init__(self, App, Text, CustomButtons = ButtonLabels, Callback = self.ReturnProperName)
        self.DrawTimer()
        #self.AddTempoButtons()
    def DrawTimer(self):
        TimeLeft = (self.TimeLimit - (time.clock() - self.StartTime))
        self.TimeString = "%d"%TimeLeft
        ButtonRows = len(self.Choices) + 1
        Y = self.MasterSprite.rect.bottom - self.ButtonHeight*(ButtonRows) - 10
        self.TimerSprite = GenericTextSprite(self.TimeString, 380, Y, FontName = Fonts.PressStart, FontSize = 24)
        self.AddForegroundSprite(self.TimerSprite)
    def Update(self):
        "Update the timer every so often"
        if not (self.AnimationCycle%25):
            TimeLeft = (self.TimeLimit - (time.clock() - self.StartTime))
            if TimeLeft < 1:
                self.App.DismissDialog(self, random.choice(self.Choices))
                #apply(self.TrueCallback, random.choice(self.Choices))
                return
            TimeString = "%d"%TimeLeft            
            if TimeString != self.TimeString:
                self.TimeString = TimeString
                self.TimerSprite.image = TextImage(self.TimeString, FontName = Fonts.PressStart, FontSize = 24)
    def ReturnProperName(self, Label):
        "Pass the chosen song to our callback"
        try:
            Index = self.Labels.index(Label)
            Label = self.Choices[Index]
        except:
            pass
        apply(self.TrueCallback, (Label, self.TempoMultiplier))
    def GetText(self):
        Str = "<CN:BRIGHTRED>An encounter!</C>\n\n"
        Str += "%s the bard prepares a song..."%self.TheBard.Name
        return Str
    def GetButtonLabels(self):
        self.Labels = []
        for Song in self.Choices:
            #Song = Resources.SongDict[Choice]
            if Song.SourceGame:
                Label = "%s (%s)"%(Song.Name, Song.SourceGame)
            else:
                Label = Song.Name
            self.Labels.append(Label)
        return self.Labels
    def CountButtonRows(self):
        self.ButtonRows = len(self.Choices) + 1 # One row for the timer
        return self.ButtonRows
    def AddTempoButtons(self):
        CHA = self.TheBard.CHA
        # Cha 18: -, normal, +
        # Cha 22: --, -, normal, +
        # Cha 26: ---, --, -, normal, +
        if CHA < 18: #18 %%%
            return # no buttons for you!
        Labels = [" + ", "normal", " - "]
        Tempos = [1.1, 1.0, 0.93]
        if (CHA >= 22): #22
            Labels.append("--")
            Tempos.append(0.86)
        if (CHA >= 26):
            Labels.append("---")
            Tempos.append(0.79)
        Labels.reverse()
        Tempos.reverse()
        #########################
        # Build the sprites:
        self.SpeedButtons = pygame.sprite.Group()
        Width = 0
        Buttons = []
        for Index in range(len(Labels)):
            if Labels[Index]=="normal":
                Image = FancyAssBoxedText(Labels[Index])
            else:
                Image = TextImage(Labels[Index], FontSize = 24)
            #Image = FancyAssBoxedText(Labels[Index])
            Button = GenericImageSprite(Image, 0, 0)
            Button.Label = Labels[Index]
            Button.Tempo = Tempos[Index]
            Width += 80 #Button.rect.width + 25
            self.SpeedButtons.add(Button)
            self.AddForegroundSprite(Button)
            Buttons.append(Button)
        #########################
        # Label above
        Image = self.GetPanelWrapImage(Width, 65, Colors.Grey, "Tempo:")
        X = 400 - Width/2
        Y = self.MasterSprite.rect.bottom - self.ButtonHeight*(len(self.Choices)+1) - 30
        Sprite = GenericImageSprite(Image, X, Y)
        self.AddBackgroundSprite(Sprite)
        Y += 35
       
        # Position the sprites:
        
        Width = 80*len(Labels)
        PadX = 40 + (self.Width - Width) / 2
        X = 400 - (self.Width / 2)
        X += PadX
        for Button in Buttons:
            Button.rect.center = (X, Y)
            X += 80
    def SetButtonPositions(self, ButtonRows):
        Y = self.MasterSprite.rect.bottom - self.ButtonHeight*(len(self.Choices)-1) - 10
        for ButtonSprite in self.ButtonSprites:
            ButtonSprite.rect.bottom = Y
            ButtonSprite.rect.left = 400 - (ButtonSprite.rect.width / 2)
            Y += self.ButtonHeight
    def HandleMouseClickedHere(self,Position,Button):
        NewDialogScreen.DialogScreen.HandleMouseClickedHere(self,Position,Button)
##        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
##        ClickedSprite = pygame.sprite.spritecollideany(Dummy,self.SpeedButtons)
##        if ClickedSprite:
##            # Ok - change our TempoMultiplier, and redraw the buttons to reflect the change!
##            self.TempoMultiplier = ClickedSprite.Tempo
##            for Sprite in self.SpeedButtons.sprites():
##                OldCenter = Sprite.rect.center
##                if Sprite == ClickedSprite:
##                    Sprite.image = FancyAssBoxedText(Sprite.Label)
##                else:
##                    Sprite.image = TextImage(Sprite.Label, FontSize = 24)
##                Sprite.rect = Sprite.image.get_rect()
##                Sprite.rect.center = OldCenter