"""
Joust-pong!  A combination of Joust and Pong.  Idea cheerfully stolen from Kirk Israel
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
import Music
from BattleSprites import *

JoustPongImageDir = os.path.join(Paths.ImagesMisc, "JoustPong")

JPScreen = None

MinBallSpeed = 2.0
BallSpeed = 2.0

VictoryPoints = 9

class JPStates:
    Pause = 0
    Play = 1
    PlayerPause = 2

PlayfieldTop = 75
PlayfieldBottom = 450
PlayfieldLeft = 100
PlayfieldRight = 700

class PaddleSprite(GenericImageSprite):
    def __init__(self, Images, X, Y):
        self.Images = Images
        self.X = X
        self.Y = Y
        #self.XDir = 0
        self.YDir = 0
        self.FlapTimer = 0
        GenericImageSprite.__init__(self, self.Images[0], X, Y)
    def Update(self, Dummy = None):
        if self.FlapTimer:
            self.FlapTimer -= 1
            if self.FlapTimer<=0:
                self.SwapImage(self.Images[0])
        self.YDir = min(self.YDir + 0.05, 7.5)
        self.Y += self.YDir
        if self.Y <= PlayfieldTop:
            self.YDir = abs(self.YDir * 0.5)
            self.Y = PlayfieldTop
        if self.Y >= PlayfieldBottom-35:
            self.YDir = -abs(self.YDir * 0.5)
            self.Y = PlayfieldBottom-35
        self.rect.top = self.Y
    def Flap(self):
        self.YDir = max(self.YDir - 1.5, -10)
        self.FlapTimer = 10
        self.SwapImage(self.Images[1])
        Resources.PlayStandardSound("Miss.wav")

class BallSprite(GenericImageSprite):
    def __init__(self, X, Y, XDir, YDir):
        self.X = X
        self.Y = Y
        self.XDir = XDir
        self.YDir = YDir
        Path = os.path.join(JoustPongImageDir, "Ball.png")
        Image = Resources.GetImage(Path)
        GenericImageSprite.__init__(self, Image, X, Y)
    def Update(self, Dummy):
        self.X += self.XDir
        self.Y += self.YDir
        if self.Y <= PlayfieldTop:
            self.YDir = abs(self.YDir)
            self.Y = PlayfieldTop
        if self.Y >= PlayfieldBottom-10:
            self.YDir = -abs(self.YDir)
            self.Y = PlayfieldBottom-10
        if self.X < PlayfieldLeft:
            JPScreen.HandlePlayerMissBall()
            JPScreen.RedrawRequested = 1
        if self.X > PlayfieldRight-18:
            JPScreen.HandleOpponentMissBall()
            JPScreen.RedrawRequested = 1
        self.rect.left = self.X
        self.rect.top = self.Y
    def GetReturnY(self):
        # Returns the Y coordinate we'll have when we hit the next wall.
        X = self.X
        Y = self.Y
        YDir = self.YDir
        BounceCount = 1
        while (X < PlayfieldRight-20):
            X += self.XDir
            Y += YDir
            if Y <= PlayfieldTop:
                YDir = abs(YDir)
                Y = PlayfieldTop
                BounceCount += 1
            if Y >= PlayfieldBottom-10:
                YDir = -abs(YDir)
                Y = PlayfieldBottom-10
                BounceCount += 1
        Delta = random.randrange(max(0, BounceCount-2)*15, BounceCount*15)
        if random.random()>0.5:
            Delta *= -1
        Y += Delta
        return Y
    
class JoustPongScreen(Screen.TendrilsScreen):
    def __init__(self, App, FreePlay):
        global JPScreen
        self.FreePlay = FreePlay
        self.PlayerScore = 0
        self.RedrawRequested = 0
        self.OpponentScore = 0
        JPScreen = self
        self.SongY = 350 # The y-coordinate where the song name appears (above our status panel)
        Screen.TendrilsScreen.__init__(self,App)
        self.State = JPStates.Pause
        self.Countdown = None
        self.PaddleSprites = pygame.sprite.Group()
        self.ButtonSprites = pygame.sprite.Group()
        self.SummonSong("daleks")
        self.DrawBackground()
        self.BuildPaddles()
        self.BallSprite = None
        self.LastPointToPlayer = 0 # who gets to serve?
        self.AITargetY = None
        self.Serve()
        self.ShownHelp = 0
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # There's a quit button, in freeplay mode:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            self.ClickQuit()
    def ClickQuit(self):
        Global.App.PopScreen(self)
            
        
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        if not self.ShownHelp:
            self.ShownHelp = 1
            self.ShowHelp()
    def Win(self):
        Music.PauseSong()
        Resources.PlayStandardSound("TodHappy.wav")
        if self.FreePlay:
            Str = "<CENTER><BIG><CN:BRIGHTGREEN>Victory!</C></BIG></CENTER>\n\n\nYou win!"
        else:
            Str = "<CENTER><BIG><CN:BRIGHTGREEN>Victory!</C></BIG></CENTER>\n\n\nYou defeated the Black Knight!\n\n<CN:ORANGE>(You have unlocked the Joust-Pong minigame)"
            Global.Party.EventFlags["L10JoustPong"] = 1
            Global.MemoryCard.Set("MiniGameJoustPong", 1)
        Global.App.ShowNewDialog(Str)
        Global.App.PopScreen(self)
    def Lose(self):
        Resources.PlayStandardSound("jou_pter.wav")
        if self.FreePlay:
            Str = "<CENTER><BIG><CN:BRIGHTRED>Defeat!</C></BIG></CENTER>\n\n\nYou lost!"
        else:
            Str = "<CENTER><BIG><CN:BRIGHTRED>Defeat!</C></BIG></CENTER>\n\n\nThe Black Knight has triumphed!"
        Global.App.ShowNewDialog(Str)
        Global.App.PopScreen(self)
        
    def BuildPaddles(self):
        Path = os.path.join(JoustPongImageDir, "Player.0.png")
        Image0 = Resources.GetImage(Path)
        Path = os.path.join(JoustPongImageDir, "Player.1.png")
        Image1 = Resources.GetImage(Path)
        self.PlayerSprite = PaddleSprite((Image0, Image1), PlayfieldLeft + 3, 300)
        self.PaddleSprites.add(self.PlayerSprite)
        self.AddForegroundSprite(self.PlayerSprite)
        #
        Path = os.path.join(JoustPongImageDir, "Opponent.0.png")
        Image0 = Resources.GetImage(Path)
        Path = os.path.join(JoustPongImageDir, "Opponent.1.png")
        Image1 = Resources.GetImage(Path)
        self.OpponentSprite = PaddleSprite((Image0, Image1), 0, 300)
        self.OpponentSprite.rect.right = PlayfieldRight - 3
        self.PaddleSprites.add(self.OpponentSprite)
        self.AddForegroundSprite(self.OpponentSprite)
    def HandlePlayerMissBall(self):
        self.BallSprite.kill()
        self.OpponentScore += 1
        self.OpponentScoreSprite.ReplaceText("Opponent: %s"%self.OpponentScore)
        self.State = JPStates.Pause
        self.Countdown = 30
        Resources.PlayStandardSound("AttackWight.wav")
        self.LastPointToPlayer = 0
        #self.Redraw()
    def HandleOpponentMissBall(self):
        self.BallSprite.kill()
        self.PlayerScore += 1
        self.PlayerScoreSprite.ReplaceText("Player: %s"%self.PlayerScore)
        self.State = JPStates.Pause
        self.Countdown = 30
        Resources.PlayStandardSound("RatingC.wav")
        self.LastPointToPlayer = 1
        #self.Redraw()
    def Serve(self):
        global BallSpeed 
        if self.BallSprite:
            self.BallSprite.kill()
        BallSpeed = MinBallSpeed
        Y = random.randrange(50, 450)
        YDir = random.randrange(-20, 20) / 10.0
        if self.LastPointToPlayer:
            X = PlayfieldRight - 25
            XDir = -BallSpeed
        else:
            X = PlayfieldLeft + 25
            XDir = BallSpeed
        self.BallSprite = BallSprite(X, Y, XDir, YDir)
        self.AddAnimationSprite(self.BallSprite)
        self.AITargetY = None
        self.State = JPStates.Play
    def HandleLoop(self):
        """
        HandleLoop is an important function (which is generally overridden in subclasses).  It is called
        once per tick.  The HandleLoop method should (1) erase foreground sprites, (2) handle user events
        and do other gameplay stuff, and (3) redraw foreground sprites.  Whatever changes/additions/deletions
        you make to the sprites in step (2) are reflected in the screen update of step (3).
        """
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface) 
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface)
        self.AnimationCycle+=1
        if (self.AnimationCycle>MaxAnimationCycle):
            self.AnimationCycle=0
        if self.State != JPStates.PlayerPause:
            for Sprite in self.AllSprites.sprites():
                Sprite.Update(self.AnimationCycle)
        self.Update()
        self.HandleEvents()
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)
    def Update(self):
        global BallSpeed
        if self.State == JPStates.Pause:
            self.Countdown -= 1
            if self.Countdown <= 0:
                # End game, or serve:
                if self.PlayerScore >= VictoryPoints:
                    self.Win()
                    self.State = JPStates.Pause
                    self.Countdown = 999
                    return
                if self.OpponentScore >= VictoryPoints:
                    self.Lose()
                    self.State = JPStates.Pause
                    self.Countdown = 999
                    return
                self.Serve()
        elif self.State == JPStates.PlayerPause:
            time.sleep(0.05) # niceness!
        else:
            Sprite = pygame.sprite.spritecollideany(self.BallSprite, self.PaddleSprites)
            if Sprite:
                # Pow!
                BallSpeed = min(BallSpeed + 0.1, 4.0)
                if Sprite == self.PlayerSprite:
                    self.BallSprite.XDir = BallSpeed
                    self.BallSprite.YDir = self.PlayerSprite.YDir
                    YOffset = self.PlayerSprite.rect.center[1] - self.BallSprite.rect.center[1]
                    self.BallSprite.YDir += (YOffset * 0.1)
                else:
                    self.BallSprite.XDir = -BallSpeed
                    self.BallSprite.YDir = self.OpponentSprite.YDir
                    YOffset = self.OpponentSprite.rect.center[1] - self.BallSprite.rect.center[1]
                    self.BallSprite.YDir += (YOffset * 0.1)
                    # Limit opponent's trickshot ability:
                    self.BallSprite.YDir = max(self.BallSprite.YDir, -5)
                    self.BallSprite.YDir = min(self.BallSprite.YDir, 5)
                    
                self.AITargetY = None
            # AI time!
            if not self.AITargetY:
                self.FindAITargetY()
            if self.OpponentSprite.FlapTimer < 3:
                #print "Y is %s target is %s"%(self.OpponentSprite.Y, self.AITargetY)
                if self.OpponentSprite.Y > self.AITargetY and self.OpponentSprite.YDir >= 0 and random.random() > 0.5:
                    self.OpponentSprite.Flap()
                elif self.OpponentSprite.Y > self.AITargetY+20 and self.OpponentSprite.YDir >= -1 and random.random() > 0.7:
                    self.OpponentSprite.Flap()
                elif random.random() > 0.995:
                    self.OpponentSprite.Flap()
        if self.RedrawRequested:
            self.Redraw()
            self.RedrawRequested = 0
    def FindAITargetY(self):
        if self.BallSprite.XDir <= 0:
            self.AITargetY = random.randrange(200, 400)
            #print "TargetY is now:", self.AITargetY
            return
        self.AITargetY = self.BallSprite.GetReturnY()
        #print "TargetY is now:", self.AITargetY
    def DrawBackground(self):
        Title = GenericTextSprite("Joust-Pong", 400, 5, Colors.Purple, CenterFlag = 1, FontSize = 36)
        self.AddBackgroundSprite(Title)
        # Background image:
        Path = os.path.join(Paths.ImagesMisc, "JoustPong", "Background.png")
        Image = Resources.GetImage(Path)
        Image = pygame.transform.scale(Image, (800, 600))
        pygame.draw.rect(Image, Colors.Black, (PlayfieldLeft, PlayfieldTop, (PlayfieldRight-PlayfieldLeft),
                              (PlayfieldBottom-PlayfieldTop)), 0)
        Sprite = GenericImageSprite(Image, 0, 0)
        self.AddBackgroundSprite(Sprite)
        # Playfield borders:
        Border = LineSprite(PlayfieldLeft, PlayfieldTop, PlayfieldRight, PlayfieldTop, Colors.Grey)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(PlayfieldLeft, PlayfieldBottom, PlayfieldRight, PlayfieldBottom, Colors.Grey)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(PlayfieldLeft, PlayfieldTop, PlayfieldLeft, PlayfieldBottom, Colors.Grey)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(PlayfieldRight, PlayfieldTop, PlayfieldRight, PlayfieldBottom, Colors.Grey)
        self.AddBackgroundSprite(Border)
        # Scores:
        self.PlayerScoreSprite = GenericTextSprite("Player: 0", 50, PlayfieldBottom + 10, FontSize = 24)
        self.AddBackgroundSprite(self.PlayerScoreSprite)
        self.OpponentScoreSprite = GenericTextSprite("Opponent: 0", 650, PlayfieldBottom + 10, FontSize = 24)
        self.AddBackgroundSprite(self.OpponentScoreSprite)
        # button, if free-play mode:
        if self.FreePlay:
            Sprite = FancyAssBoxedSprite("Quit", 650, PlayfieldBottom + 40, HighlightIndex = 0)
            self.AddBackgroundSprite(Sprite)
            self.ButtonSprites.add(Sprite)
    def ShowHelp(self):
        Str = "<CENTER>Joust-Pong</CENTER>\n\nYou are the <CN:BRIGHTGREEN>left</c> player.  You must <CN:BRIGHTGREEN>hit the ball</C>.  Press the <CN:BRIGHTGREEN>space bar</C> to flap.  First player to 9 points wins."
        Global.App.ShowNewDialog(Str)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if self.State == JPStates.Play:
            if Key == ord(" "): # Flap!
                self.PlayerSprite.Flap()
        if Key == ord("q") and self.FreePlay:
            self.ClickQuit()
        if Key == pygame.K_ESCAPE:
            if self.State == JPStates.PlayerPause:
                self.State = JPStates.Play
                self.PauseSprite.kill()
            elif self.State == JPStates.Play:
                self.State = JPStates.PlayerPause
                PausedImage = FancyAssBoxedText("Paused (press ESC)", Fonts.PressStart, 24, Spacing = 6)
                self.PauseSprite = GenericImageSprite(PausedImage, 475 - PausedImage.get_rect().width / 2,
                                                      225 - PausedImage.get_rect().height / 2)
                self.AddAnimationSprite(self.PauseSprite)
                