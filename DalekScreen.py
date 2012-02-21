"""
Dalek screen.  Robots move directly toward the player.  Robots who crash into each other are destroyed,
leaving a pile of crud.  Robots who crash into a pile of crud are also destroyed.  SPACE HAS A TERRIBLE
POWER.  PLEASE GO STAND BY THE STAIRS.
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
import math
import string
import Party
import ChestScreen
from BattleSprites import *

DalekImage = None
CrudImage = None
DScreen = None

DalekImageDir = os.path.join(Paths.ImagesMisc, "Daleks")

class DalekStates:
    Ready = 0
    Moving = 1
    Sonicating = 2
    Teleporting = 3
    Dying = 4
    Winning = 5

class Contents:
    Empty = 0
    Dalek = 1
    Crud = 2


def GetDalekImage():
    global DalekImage
    if DalekImage:
        return
    DalekImage = Resources.GetImage(os.path.join(DalekImageDir, "Dalek.png"))

class ScrewdriverSprite(GenericImageSprite):
    def __init__(self, Center):
        (X, Y) = Center
        self.Ticks = 0
        Width = GridPixelWidth * 3
        Height = GridPixelHeight * 3
        self.CenterX = Width/2
        self.CenterY = Height/2
        self.image = pygame.Surface((Width, Height))
        X -= Width/2
        Y -= Height/2
        self.Rects = []
        GenericImageSprite.__init__(self, self.image,X, Y) 
    def Update(self, Dummy):
        self.Ticks += 1
        if self.Ticks > 100:
            self.kill()
            return
        if self.Ticks%2 == 0:
            return
        self.image.fill(Colors.Black)
        NewRects = []
        for (Color, Radius) in self.Rects:
            Radius = max(Radius+0.5, Radius * 1.2)
            pygame.draw.circle(self.image, Color, (self.CenterX, self.CenterY), Radius, 1)
            NewRects.append((Color, Radius))
        if len(NewRects)<5:
            Color = random.choice((Colors.MediumGrey, Colors.DarkGreen, Colors.Green, Colors.LightGrey))
            NewRects.append((Color,1.0))
        self.Rects = NewRects
        
class DalekSprite(GenericImageSprite):
    MoveTime = 50
    def __init__(self, GridX, GridY):
        self.image = DalekImage #
        self.X = GridX
        self.Y = GridY
        self.StartX = None
        self.StartY = None
        self.TargetX = None
        self.TargetY = None
        self.DeadFlag = 0
        self.MoveCounter = None
        (ScreenX, ScreenY) = DScreen.GetScreenPosition(GridX, GridY)
        GenericImageSprite.__init__(self, self.image, ScreenX, ScreenY)
    def Update(self, Dummy):
        if self.MoveCounter!=None:
            self.rect.left = (self.StartX) + (self.TargetX - self.StartX) * (self.MoveCounter / self.MoveTime)
            self.rect.top = (self.StartY) + (self.TargetY - self.StartY) * (self.MoveCounter / self.MoveTime)
            if self.MoveCounter >= self.MoveTime:
                self.MoveCounter = None # done!
                
GridWidth = 30
GridHeight = 20
GridPixelWidth = 25
GridPixelHeight = 25        

ScrewdriverCounts = [1, 1, 1, 1, 1]
RobotCounts = [5, 8, 13, 19, 26, 28, 30]
#RobotCounts = [5,]
class DalekScreen(Screen.TendrilsScreen):
    DirMapping = {263: (-1, -1), 264: (0,-1), 265: (1,-1),
                  260: (-1,0), 261: (0,0), 32: (0,0), 262: (1,0),
                  257: (-1,1), 258: (0,1), 259: (1,1)
                  }
    RoundX = 25
    ScrewdriverX = 150
    BotsX = 350
    ButtonX = 550
    def __init__(self, App, FreePlay, RobotCount = 10):
        global DScreen
        self.FreePlay = FreePlay
        self.Score = 0
        GetDalekImage()
        DScreen = self
        self.SongY = 450 # The y-coordinate where the song name appears (above our status panel)
        Screen.TendrilsScreen.__init__(self,App)
        self.State = DalekStates.Ready
        self.RoundNumber = 0
        self.ScrewdriverCount = 0
        self.RobotCount = 0
        self.Countdown = None
        self.Grid = {}
        
        self.DalekSprites = pygame.sprite.Group()
        self.PileSprites = pygame.sprite.Group()
        self.CrudImage = Resources.GetImage(os.path.join(DalekImageDir,"Crud.png"))
        self.PlayerImage = Resources.GetImage(os.path.join(DalekImageDir,"1up.png"))
        self.DeathImage = Resources.GetImage(os.path.join(DalekImageDir,"Death.png"))
        
        self.SummonSong("daleks")
        self.DrawBackground()
        self.StartRound()
    def FinishRound(self):
        self.RoundNumber += 1
        if (not self.FreePlay) and self.RoundNumber >= 4:
            if Global.Party.EventFlags.get("L6Daleks"):
                Str = "You have defeated the robots!\n\n(You already looted their treasure)"
                Global.App.ShowNewDialog(Str)
            else:
                Global.Party.EventFlags["L6Daleks"]=1
                Str = "You have defeated all the robots!  You grab their treasure.\n\n(You have unlocked the <CN:ORANGE>Daleks</C> minigame!)\n\n"
                Global.MemoryCard.Set("MiniGameDaleks")
                ChestItems = {"Crystal Staff":1}
                ChestSpecial = {"gold":12500}
                ChestScreen.GetTreasureChestStuff(ChestItems, ChestSpecial, 2, Str)
            Global.App.PopScreen(self)
        else:
            self.StartRound()
    def Lose(self):
        if self.FreePlay:
            OldHiScore = Global.MemoryCard.Get("DaleksHiScore", 0)
            OldHiScoreName = Global.MemoryCard.Get("DaleksHiScoreName", "nobody")
            Str = "<CENTER><CN:LIGHTGREY>Do you have stairs in your house?</C></CENTER>\n\nYou made it to round <CN:PURPLE>%d</C>, and scored <CN:PURPLE>%d</C> points.\n\n"%(self.RoundNumber+1, self.Score)
            if self.Score <= OldHiScore:
                Str += "You didn't beat the hiscore of <CN:PURPLE>%d</c>, by <CN:PURPLE>%s</c>."%(OldHiScore, OldHiScoreName)
                Global.App.ShowNewDialog(Str)
                Global.App.PopScreen(self)
                return
            else:
                Str += "A new high score!  Enter your name:"
                Global.App.ShowNewDialog
                Global.App.ShowWordEntryDialog(Str, self.HiScoreNameEntry, 10)
                return
        else:
            for Player in Global.Party.Players:
                if Player.IsAlive():
                    Player.HP = 1            
            Str = "<CENTER>You have been <CN:BRIGHTRED>ZAPPED</C> by the robots!\n\nYou don't feel so well..."
            Global.App.ShowNewDialog(Str)
            Global.App.PopScreen(self)
    def HiScoreNameEntry(self, Name):
        Global.MemoryCard.Set("DaleksHiScore", self.Score)
        Global.MemoryCard.Set("DaleksHiScoreName", Name)
        Global.App.PopScreen(self)
    def FinishCurrentState(self):
        self.Countdown = None
        if self.State == DalekStates.Dying:
            self.Lose()
            return
        if self.State == DalekStates.Winning:
            self.FinishRound()
            return
        # Otherwise...we just finished screwdriver or teleport.  Robots' turn.
        self.State = DalekStates.Ready
        self.PerformRobotTurn()
        if self.State == DalekStates.Ready and self.LiveRobotCount <= 0:
            self.State = DalekStates.Winning
            Resources.PlayStandardSound("PowerUp.wav")
            self.Countdown = 100
        self.Redraw()
    def Update(self):
        if self.Countdown:
            self.Countdown -= 1
            if self.Countdown <= 0:
                self.FinishCurrentState()
            else:
                if self.State == DalekStates.Teleporting:
                    (X,Y) = self.GetScreenPosition(self.PlayerSprite.X, self.PlayerSprite.Y)
                    X += self.Countdown * 2 * math.cos(self.Countdown / 3.5)
                    Y += self.Countdown * 2 * math.sin(self.Countdown / 3.5)
                    self.PlayerSprite.rect.left = X
                    self.PlayerSprite.rect.top = Y
                elif self.State == DalekStates.Dying:
                    if self.Countdown%2:
                        self.PlayerSprite.image = self.PlayerImage
                    else:
                        self.PlayerSprite.image = self.DeathImage
    def GetScreenPosition(self, GridX, GridY):
        X = (800 - GridWidth*GridPixelWidth) / 2
        Y = (600 - GridHeight*GridPixelHeight) / 2
        return (X + GridX*GridPixelWidth, Y + GridY*GridPixelHeight)
    def DrawBackground(self):
        # Draw a light grid, to make it clear where everything is:
        Image = pygame.Surface((GridWidth*GridPixelWidth + 1, GridHeight*GridPixelHeight + 1))
        Image.fill(Colors.Black)
        for X in range(GridWidth+1):
            pygame.draw.line(Image, Colors.Grey, (X*GridPixelWidth,0),(X*GridPixelWidth,600))
        for Y in range(GridHeight+1):
            pygame.draw.line(Image, Colors.Grey, (0, Y*GridPixelHeight),(800, Y*GridPixelHeight))
        (X, Y) = self.GetScreenPosition(0, 0)
        GridSprite = GenericImageSprite(Image, X, Y)
        self.AddBackgroundSprite(GridSprite)
        # Build player sprite, it's always around:
        #Image = Resources.GetImage(os.path.join("Images","Misc","Daleks", "1up.png"), 1) 
        self.PlayerSprite = GenericImageSprite(self.PlayerImage,0,0)
        self.AddForegroundSprite(self.PlayerSprite)
        # Round info:
        self.RoundNumberSprite = GenericTextSprite("Round: 1", self.RoundX, 560)
        self.AddBackgroundSprite(self.RoundNumberSprite)
        self.ScrewdriverCountSprite = GenericTextSprite("Screwdrivers: 1", self.ScrewdriverX, 560)
        self.AddBackgroundSprite(self.ScrewdriverCountSprite)
        self.RobotCountSprite = GenericTextSprite("Bots Alive: 5/5", self.BotsX, 560)
        self.AddBackgroundSprite(self.RobotCountSprite)
        # Buttons:
        self.ButtonSprites = pygame.sprite.Group()
        Sprite = FancyAssBoxedSprite("Help", self.ButtonX, 555, HighlightIndex = 0)
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        Sprite = FancyAssBoxedSprite("Sonic", self.ButtonX + 60, 555, HighlightIndex = 0)
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        Sprite = FancyAssBoxedSprite("Teleport", self.ButtonX + 120, 555, HighlightIndex = 0)
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
    def UpdateRobotCount(self):
        self.RobotCountSprite.ReplaceText("Bots Left: %d/%d"%(self.LiveRobotCount, self.RobotCount))
    def UpdateScrewdriverCount(self):
        self.ScrewdriverCountSprite.ReplaceText("Screwdrivers: %d"%(self.ScrewdriverCount))
    def UpdateRoundNumber(self):
        self.RoundNumberSprite.ReplaceText("Round: %d"%(self.RoundNumber+1))
    def StartRound(self):
        for Sprite in self.DalekSprites.sprites():
            Sprite.kill()
        for Sprite in self.PileSprites.sprites():
            Sprite.kill()
        self.RobotCount = RobotCounts[min(self.RoundNumber, len(RobotCounts)-1)]
        self.UpdateRoundNumber()
        self.LiveRobotCount = self.RobotCount
        self.UpdateRobotCount()
        self.ScrewdriverCount = ScrewdriverCounts[min(self.RoundNumber, len(ScrewdriverCounts)-1)]
        self.UpdateScrewdriverCount()
        self.PlaceDaleks()
        self.PlacePlayer()
        self.State = DalekStates.Ready
        # Update the round# %%%
        self.Redraw()
    def PlaceDaleks(self):
        # Clean out old crud:
        for X in range(GridWidth):
            for Y in range(GridHeight):
                self.Grid[(X, Y)] = Contents.Empty
        # Create some robots:
        for RobotIndex in range(self.RobotCount):
            while (1):
                X = random.randrange(GridWidth)
                Y = random.randrange(GridHeight)
                if self.Grid[(X, Y)] == Contents.Empty:
                    self.Grid[(X, Y)] = Contents.Dalek
                    Sprite = DalekSprite(X, Y)
                    self.AddForegroundSprite(Sprite)
                    self.DalekSprites.add(Sprite)
                    break
    def PlacePlayer(self):
        while (1):
            X = random.randrange(GridWidth)
            Y = random.randrange(GridHeight)
            if self.Grid[(X, Y)] == Contents.Empty:
                self.PlayerSprite.X = X
                self.PlayerSprite.Y = Y
                (ScreenX, ScreenY) = self.GetScreenPosition(X, Y)
                self.PlayerSprite.rect.left = ScreenX
                self.PlayerSprite.rect.top = ScreenY
                break
    def ShowHelp(self):
        Str = "<CENTER>Robot Attack</CENTER>\n\nClick (or use the num pad) to move.  Don't let the robots catch you!\n\n\
Sonic <CN:BRIGHTGREEN>s</C>crewdrivers will destroy all robots standing next to you.  Robots are also destroyed if they crash into other robots or junk piles.\n\n\
You can also <CN:BRIGHTGREEN>t</C>eleport to get away, but teleporting is risky..."
        Global.App.ShowNewDialog(Str)
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        if self.State != DalekStates.Ready:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            if Sprite.Text == "Help":
                self.ShowHelp()
            elif Sprite.Text == "Sonic":
                if self.ScrewdriverCount:
                    self.FireScrewdriver()
            elif Sprite.Text == "Teleport":
                self.StartTeleport()
            return
        XDir = 0 #default
        YDir = 0
        if Position[0] < self.PlayerSprite.rect.left:
            XDir = -1
        if Position[0] > self.PlayerSprite.rect.right:
            XDir = 1
        if Position[1] < self.PlayerSprite.rect.top:
            YDir = -1
        if Position[1] > self.PlayerSprite.rect.bottom:
            YDir = 1
        self.MovePlayer(XDir, YDir)
    def MovePlayer(self, XDir, YDir):
        NewX = self.PlayerSprite.X + XDir
        NewY = self.PlayerSprite.Y + YDir
        if (NewX<0 or NewX >= GridWidth):
            return
        if (NewY<0 or NewY >= GridHeight):
            return
        Stuff = self.Grid[(NewX, NewY)]
        if Stuff != Contents.Empty:
            return
        # Movement occurs now!
        self.PlayerSprite.X = NewX
        self.PlayerSprite.Y = NewY
        (ScreenX, ScreenY) = self.GetScreenPosition(NewX, NewY)
        self.PlayerSprite.rect.left = ScreenX
        self.PlayerSprite.rect.top = ScreenY
        self.PerformRobotTurn()
        self.Redraw()
    def PerformRobotTurn(self):
        CrashCount = self.MoveRobots()
        if self.PlayerDies():
            self.State = DalekStates.Dying
            Resources.PlayStandardSound("EerieBuzz.wav")
            self.Countdown = 50
        else:
            if CrashCount:
                if self.State == DalekStates.Ready and self.LiveRobotCount <= 0:
                    self.State = DalekStates.Winning
                    Resources.PlayStandardSound("PowerUp.wav")
                    self.Countdown = 100
                else:
                    Resources.PlayStandardSound("Kill.wav")
                
                
            else:
                Resources.PlayStandardSound("Step.wav")
        
    def MoveRobots(self):
        DeathCount = 0
        # First, move every robot toward the player:
        for Sprite in self.DalekSprites.sprites():
            XDir = 0
            YDir = 0            
            if Sprite.X < self.PlayerSprite.X:
                XDir = 1
            if Sprite.X > self.PlayerSprite.X:
                XDir = -1
            if Sprite.Y < self.PlayerSprite.Y:
                YDir = 1
            if Sprite.Y > self.PlayerSprite.Y:
                YDir = -1
            self.Grid[(Sprite.X, Sprite.Y)] = Contents.Empty
            Sprite.X += XDir
            Sprite.Y += YDir
            (ScreenX, ScreenY) = self.GetScreenPosition(Sprite.X, Sprite.Y)
            Sprite.rect.left = ScreenX
            Sprite.rect.top = ScreenY
        # Now, process all the collisions:
        Sprites = self.DalekSprites.sprites()
        for Sprite in Sprites[:]:
            if Sprite.DeadFlag: # Don't die again.  (You Only Die Twice, by Ian Fleming...)
                continue 
            Stuff = self.Grid[(Sprite.X, Sprite.Y)]
            if Stuff == Contents.Crud:
                Sprite.kill()
                Sprite.DeadFlag = 1
                DeathCount += 1
                self.LiveRobotCount -= 1 # died on a pile
                ##print "One died on pile at (%s, %s)"%(Sprite.X, Sprite.Y)
                self.Score += 1
            elif Stuff == Contents.Dalek:
                Sprite.kill()
                Sprite.DeadFlag = 1
                DeathCount += 1
                self.LiveRobotCount -= 1 # died on another dalek
                self.Score += 1
                self.Grid[(Sprite.X, Sprite.Y)] = Contents.Crud
                self.AddCrudSprite(Sprite.X, Sprite.Y)
                ##print "One started a collision at (%s, %s)"%(Sprite.X, Sprite.Y)
                # Kill the other guy too:
                for OtherGuy in Sprites:
                    if OtherGuy!=Sprite and OtherGuy.X == Sprite.X and OtherGuy.Y == Sprite.Y and not OtherGuy.DeadFlag:
                        OtherGuy.kill()
                        OtherGuy.DeadFlag = 1
                        DeathCount += 1
                        self.LiveRobotCount -= 1
                        self.Score += 1
                        ##print "Killed the other guy at (%s, %s)"%(Sprite.X, Sprite.Y)
                        
            else:
                self.Grid[(Sprite.X, Sprite.Y)] = Contents.Dalek
        self.UpdateRobotCount()
        return DeathCount
    def AddCrudSprite(self, X, Y):
        ScreenX, ScreenY = self.GetScreenPosition(X, Y)
        Sprite = GenericImageSprite(self.CrudImage, ScreenX, ScreenY)
        self.AddBackgroundSprite(Sprite)
        self.PileSprites.add(Sprite)
    def PlayerDies(self):
        # The player dies if there's a robot next door:
        X = self.PlayerSprite.X
        Y = self.PlayerSprite.Y
        if self.Grid[(X, Y)] != Contents.Empty:
            return 1
        return 0
    def FireScrewdriver(self):
        Resources.PlayStandardSound("MagicDodge.wav")
        self.ScrewdriverCount -= 1
        for X in range(self.PlayerSprite.X - 1, self.PlayerSprite.X + 2):
            for Y in range(self.PlayerSprite.Y - 1, self.PlayerSprite.Y + 2):
                # Find bots:
                for Sprite in self.DalekSprites.sprites():
                    if Sprite.X == X and Sprite.Y == Y:
                        Sprite.kill()
                        self.LiveRobotCount -= 1
                        self.Score += 1
                        self.Grid[(X,Y)] = Contents.Empty
        # Update bot count:
        self.UpdateRobotCount()
        # Update screw Count:
        self.UpdateScrewdriverCount()
        # Pzooow!  Animate the screwdriver:
        Sprite = ScrewdriverSprite(self.PlayerSprite.rect.center)
        self.AddAnimationSprite(Sprite)
        self.Countdown = 60
    def StartTeleport(self):
        # Teleport to any empty square:
        self.PlacePlayer()
        self.Countdown = 60
        self.State = DalekStates.Teleporting
        Resources.PlayStandardSound("MegamanNoise.wav")
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if self.State == DalekStates.Ready:
            if Key == ord("h"):
                self.ShowHelp()
                return
            if Key == ord("s"):
                if self.ScrewdriverCount:
                    self.FireScrewdriver()
                return
            if Key == ord("t"):
                self.StartTeleport()
                return
            if self.DirMapping.has_key(Key):
                (XDir,YDir) = self.DirMapping[Key]
                self.MovePlayer(XDir, YDir)
