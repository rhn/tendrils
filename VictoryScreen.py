"""
"Victoly!"  - Samurai Showdown
"A WINNER IS YOU!" - Pro Wrestling
"SEE YOU NEXT - TECMO" - Some tecmo game

At last, the battle is won, and the ending credits roll while some happy
music plays.  (And to make things a little bit more interesting, the
player can fly a ship around in the credits)
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

VScreen = None

class VictoryScreen(Screen.TendrilsScreen):
    FontSize = 32
    MaxCreditTimer = 450 #500
    MaxMonsterTimer = 100
    MaxMonsters = 4
    MaxArrowTick = 1
    def __init__(self, App):
        global VScreen
        Screen.TendrilsScreen.__init__(self,App)
        self.ShipSprite = None # Once this exists, the minigame is started
        self.ReloadTime = 0
        self.ArrowTick = self.MaxArrowTick
        self.CreditTimer = 0
        self.MonsterTimer = 100
        self.CreditIndex = None
        VScreen = self
        self.GetCredits()
        self.RenderInitialScreen()
    def GetPlayTimeString(self):
        Time = Global.Party.TotalPlayTime
        Str = ""
        Days = Time / 3600*24
        Time = Time % (3600*24)
        if Days:
            Str = "%d D "%Days
        Hours = Time / 3600
        Time = Time % 3600
        if Hours:
            Str = "%d'"%Hours
        Minutes = Time / 60
        Str = "%d\""%Minutes
        return Str
    def GetCredits(self):
        self.AddShipIndex = 4
        HeroStrings = ["THE HEROES:",]
        for Player in Global.Party.Players:
            HeroStrings.append("%s the %s"%(Player.Name, Player.Species.Name))
        self.CreditItems = [["YOU HAVE WON."],
                       ["Thanks to your","courage and skill,","Mother Brain is no more."], 
                       ["The people of a thousand worlds","are saved at last."],
                       HeroStrings,
                       ["Oh no!", "The credits are under attack!", "(Use arrows and space bar)"],                       
                       ["T E N D R I L S","The Role-playing Remix"],
                       ["- - Staff - -"],
                       ["Main Programmer", "- - - - - -", "Stephen Tanner"],
                       ["Graphics Master", "- - - - - -", "Sean Curtis"],
                       ["Music Director", "- - - - - -", "BadBadtzMaru"],
                       ["Design Assist", "- - - - - -", "Robert Goodwin", "David Jeppesen", "Max William"],
                       ["Linux Gurus", "- - - - - -", "Jonathan Matthew", "Joshua Wise", ],
                       
                       ["Testing", "- - - - - -", "Eb Oesch", "rone", "Frank Chang", "Jonathan Matthew"],
                       ["More Testing", "- - - - - -", "Bryan Chase", "Matthew Reinbold", "Michael Hall", "Elizabeth Sanders"],
                       ["Total Kills","%d"%Global.Party.KillCount],
                       ["Total Play",self.GetPlayTimeString()],
                       ["VERY THANKS..!!","See you next game..."],
                       [],
                       [],
                            ]


    def RenderInitialScreen(self):
        self.PlayerBullets = pygame.sprite.Group()
        self.EnemyBullets = pygame.sprite.Group()
        self.MonsterSprites = pygame.sprite.Group()
        self.LetterSprites = pygame.sprite.Group()
        self.DrawStars()
        self.SummonSong("credits")
        # %%%
        ##self.AddShip()
    def DrawStars(self):
        StarryNight = pygame.Surface((self.Width, self.Height))
        for Index in range(100):
            Name = os.path.join(Paths.ImagesMisc, "Star.%d"%random.randrange(0,4))
            Image = Resources.GetImage(Name)
            X = random.randrange(800)
            Y = random.randrange(600)
            StarryNight.blit(Image, (X, Y))
        LiteBriteNiteSprite = GenericImageSprite(StarryNight, 0, 0)
        self.AddBackgroundSprite(LiteBriteNiteSprite)
    def Update(self):
        self.CreditTimer -= 1
        if self.CreditTimer <= 0:
            self.CreditTimer = self.MaxCreditTimer
            self.ShowCredits()
        self.MonsterTimer -= 1
        if self.MonsterTimer <= 0:
            self.MonsterTimer = self.MaxMonsterTimer
            if self.ShipSprite and len(self.MonsterSprites.sprites()) < self.MaxMonsters:
                self.AddMonster()
        self.ReloadTime = max(0, self.ReloadTime - 1)
        self.ArrowTick -= 1
        if self.ArrowTick <= 0:
            self.ArrowTick = self.MaxArrowTick
            self.MoveShip()
    def AddShip(self):
        if not self.ShipSprite:
            Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Ship.png"))
            self.ShipSprite = GenericImageSprite(Image, 400, 580) #GenericTextSprite("X", 400, 580)
            self.ShipSprite.rect.bottom = 600
            self.AddForegroundSprite(self.ShipSprite)
            self.ShipSprite.XDir = 0
    def AddMonster(self):
        Name = random.choice(("Pooka","Goomba","Galaga Red","Sorcerer","Invader1"))
        X = random.choice((-10, 200, 400, 600, 810))
        Y = -50
        Sprite = MonsterSprite(Name, X, Y)
        self.AddForegroundSprite(Sprite)
        self.MonsterSprites.add(Sprite)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if not self.ShipSprite:
            return
        if Key == 32 and self.ShipSprite and self.ReloadTime <= 0:
            self.FireCannon()
            self.ReloadTime = 10
            return
    def MoveShip(self):
        if not self.ShipSprite:
            return 
        KeysPressed = pygame.key.get_pressed()
        if KeysPressed[Keystrokes.Left[0]] or KeysPressed[Keystrokes.Left[1]]:
            #self.ShipSprite.rect.left = max(0, self.ShipSprite.rect.left - 5)
            self.ShipSprite.XDir = max(self.ShipSprite.XDir - 1, -8)
        elif KeysPressed[Keystrokes.Right[0]] or KeysPressed[Keystrokes.Right[1]]:
            self.ShipSprite.XDir = min(self.ShipSprite.XDir + 1, 8)
            #self.ShipSprite.rect.right = min(800, self.ShipSprite.rect.right + 5)
        else:
            if self.ShipSprite.XDir > 0:
                self.ShipSprite.XDir -= 1
            elif self.ShipSprite.XDir < 0:
                self.ShipSprite.XDir += 1
        self.ShipSprite.rect.left += self.ShipSprite.XDir
        self.ShipSprite.rect.left = max(0, self.ShipSprite.rect.left)
        self.ShipSprite.rect.right = max(0, self.ShipSprite.rect.right)
    def FireCannon(self):
        Sprite = BulletSprite(self.ShipSprite.rect.center[0], self.ShipSprite.rect.top)
        self.AddAnimationSprite(Sprite)
        self.PlayerBullets.add(Sprite)
        Resources.PlayStandardSound("Step.wav")
    def ShowCredits(self):
        if self.CreditIndex == None:
            self.CreditIndex = 0
        else:
            self.CreditIndex += 1
        if self.CreditIndex >= len(self.CreditItems):
            Global.App.PopScreen(self)
            Global.App.ReturnToTitle()
            return
        if self.CreditIndex == len(self.CreditItems) - 1:
            Music.FadeOut()
            # Shorter:
            self.CreditTimer /= 2
        if self.CreditIndex == self.AddShipIndex:
            self.AddShip()
        Items = self.CreditItems[self.CreditIndex]
        Y = 600
        for Item in Items:
            X = 0
            RowSprites = []
            for Letter in Item:
                if Letter == " ":
                    X += 20
                    continue
                ##print Letter
                Sprite = LetterSprite(Letter, X, Y)
                self.AddAnimationSprite(Sprite)
                self.LetterSprites.add(Sprite)
                RowSprites.append(Sprite)
                X += Sprite.rect.width
            PadX = 400 - X/2
            for Sprite in RowSprites:
                Sprite.SetX(Sprite.rect.left + PadX)
            Y += 25
    def AnimateParticles(self, X, Y, ShrapnelClass, ParticleCount=50):
        for Index in range(ParticleCount):
            Sprite = ShrapnelClass(X+random.randrange(-5,6),Y+random.randrange(-5,6),25)
            self.AllSprites.add(Sprite)
            self.AnimationSprites.add(Sprite)

class BulletSprite(GenericImageSprite):
    BulletImage = pygame.Surface((2,20))
    BulletImage.fill(Colors.White)
    def __init__(self, X, Y):
        GenericImageSprite.__init__(self, self.BulletImage, X, Y)
    def Update(self, Dummy = None):
        self.rect.top -= 8
        Sprite = pygame.sprite.spritecollideany(self, VScreen.MonsterSprites)
        if Sprite:
            if Sprite.TargetLetter:
                Sprite.TargetLetter.Owner = None
                Sprite.TargetLetter.Targeter = None
                Sprite.AliveFlag = 0
                #print "Freed a letter!"
            Sprite.kill()
            VScreen.AnimateParticles(self.rect.center[0], self.rect.center[1], BloodSprite, 10)
            Resources.PlayStandardSound("Kill.wav")
            self.kill()
        if self.rect.bottom < 0:
            self.kill()

class MonsterSprite(GenericImageSprite):
    MaxTick = 10
    def __init__(self, Name, X, Y):
        self.Name = Name
        self.ImageIndex = 0
        self.AliveFlag = 1
        self.Tick = self.MaxTick
        self.XDir = random.randrange(-10, 10) / 20.0
        self.YDir = 0
        self.TargetLetter = None
        self.GetImages()
        GenericImageSprite.__init__(self, self.Images[0], X, Y)
        self.PickTargetLetter()
    def GetImages(self):
        Index = 0
        self.Images = []
        while (1):
            Path = os.path.join(Paths.ImagesCritter, self.Name, "Stand.%d.png"%Index)
            #print Path
            if not os.path.exists(Path):
                #print "Maccavity's not there!"
                break
            try:
                Image = Resources.GetImage(Path)
            except:
                break
            Image.set_colorkey(Colors.Black)
            self.Images.append(Image)
            Index += 1
    def PickTargetLetter(self):
        if not self.AliveFlag:
            return
        Targets = VScreen.LetterSprites.sprites()
        if len(Targets) < 5:
            self.kill()
            return
        Cycle = 0
        while (1):
            Sprite = random.choice(Targets)
            if Sprite.rect.top > 300 and not Sprite.Targeter and Sprite.Letter!="-":
                break
            Cycle += 1
            if Cycle > 50:
                return
        self.TargetLetter = Sprite
        self.TargetLetter.Targeter = self
    def Update(self, Dummy = None):
        if not self.AliveFlag:
            if self.TargetLetter:
                self.TargetLetter.Owner = None
                self.TargetLetter.Targeter = None
                self.TargetLetter = None
            self.kill()
            return 
        # Move:
        self.rect.left += self.XDir
        self.rect.top += self.YDir
        # Animate:
        self.Tick -= 1
        if self.Tick<=0:            
            self.Tick = self.MaxTick
            self.ImageIndex = (self.ImageIndex + 1) % len(self.Images)
            Center = self.rect.center
            self.image = self.Images[self.ImageIndex]
            self.rect = self.image.get_rect()
            self.rect.center = Center
            if not self.TargetLetter:
                self.PickTargetLetter()
        if not self.TargetLetter:
            Accelerate(self, self.rect.center[0], -100, 2)
            if self.rect.bottom < -10:
                self.kill()
            return
        # Escaping behavior:
        if self.TargetLetter.Owner == self:
            Accelerate(self, self.EscapeX, self.EscapeY, 1.5)
            self.TargetLetter.rect.top = self.rect.center[1]
            self.TargetLetter.rect.left = self.rect.center[0]
            if self.rect.right < -30 or self.rect.left >= 830:
                self.TargetLetter.Owner = None
                self.TargetLetter.Targeter = None
                self.TargetLetter.kill()
                self.TargetLetter = None
                self.kill()
                return
        else:
            # Chasing behavior:
            Accelerate(self, self.TargetLetter.rect.center[0], self.TargetLetter.rect.center[1], 2)        
            if self.TargetLetter in pygame.sprite.spritecollide(self, VScreen.LetterSprites, 0):
                Resources.PlayStandardSound("Bleep1.wav")
                self.TargetLetter.Owner = self
                self.TargetLetter.Touched = 1
                self.EscapeX = random.choice((-1000, 1000))
                self.EscapeY = random.choice((200, 250, 300, 350, 400, 450))
        
class LetterSprite(GenericImageSprite):
    YSpeed = 0.8 # 0.5
    def __init__(self, Letter, X, Y):
        Image = TextImage(Letter, FontSize = 16, FontName = Fonts.PressStart)
        GenericImageSprite.__init__(self, Image, X, Y)
        self.HalfHeight = self.rect.height / 2
        self.Letter = Letter
        self.XDir = 0
        self.YDir = -self.YSpeed
        self.TargetX = self.rect.center[0]
        self.TargetY = self.rect.center[1]
        self.Owner = None
        self.Targeter = None
        self.Touched = 0
    def SetX(self, X):
        self.rect.left = X
        self.TargetX = self.rect.center[0]
    def Update(self, Dummy = None):
        self.TargetY -= self.YSpeed
        if not self.Touched:
            self.rect.top = self.TargetY - self.HalfHeight
            if self.rect.bottom < -10:
                self.kill()
            return
        if not self.Owner:
            self.rect.left += self.XDir
            self.rect.top += self.YDir
            Accelerate(self, self.TargetX, self.TargetY, 5)
        if self.rect.top < -30:
            self.kill()
            if self.Targeter:
                self.Targeter.PickTargetLetter()
        
def Accelerate(Sprite, X, Y, MaxSpeed):
    Acc = MaxSpeed / 10.0
    if (Sprite.rect.center[0] < X):
        Sprite.XDir = min(Sprite.XDir + Acc, MaxSpeed)
        if Sprite.rect.center[0] + Sprite.XDir * 5 > X:
            Sprite.XDir = max(0.1, Sprite.XDir - Acc)
    if (Sprite.rect.center[0] > X):
        Sprite.XDir = max(Sprite.XDir - Acc, -MaxSpeed)
        if Sprite.rect.center[0] + Sprite.XDir * 5 < X:
            Sprite.XDir = min(-0.1, Sprite.XDir + Acc)
    if Sprite.rect.center[1] < Y:
        Sprite.YDir = min(Sprite.YDir + Acc, MaxSpeed)
        if Sprite.rect.center[1] + Sprite.YDir * 5 > Y:
            Sprite.YDir = max(0.1, Sprite.YDir - Acc)
    if Sprite.rect.center[1] > Y:
        Sprite.YDir = max(Sprite.YDir - Acc, -MaxSpeed)
        if Sprite.rect.center[1] + Sprite.YDir * 5 < Y:
            Sprite.YDir = min(-0.1, Sprite.YDir + Acc)


        