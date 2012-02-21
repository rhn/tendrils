"""
Ah, sniping!  There is no game that cannot be improved with the addition of a sniper rifle.
The sniper rifle lets the user start many battles off by ambushing the monsters and dishing
out some heavy damage.  Just like the good old days playing Golgo 13: The Mafat Conspiracy...
"""
from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import string
import math

SpriteFieldMax = 500
SpriteSqrt = math.sqrt(SpriteFieldMax)
SnipeRadius = 250
EndingPause = 50
EndingPauseTimeOver = 50
class SnipeScreen(Screen.TendrilsScreen):
    CenterX = 400
    CenterY = 300
    MaxReloadTime = 45
    def __init__(self, App, Monsters):
        Screen.TendrilsScreen.__init__(self, App)
        self.Monsters = Monsters
        self.OldMousePosition = None
        self.OldMouseX = None
        self.OldMouseY = None
        self.DeltaX = 0
        self.DeltaY = 0
        self.ShotsLeft = 6
        self.ReloadTime = 0
        self.TimeLimit = 15.0
        self.StartInstant = time.clock()
        self.OldTimeStr = "10.0"
        self.QuitCycle = None
        self.RenderInitialScreen()
    def ClearCursor(self):
        # Cursor:
        self.OldCursor = pygame.mouse.get_cursor()
        print self.OldCursor
        Str = []
        for X in range(8):
            Str.append("........")
        Data, Mask = pygame.cursors.compile(Str,"X","Y")
        pygame.mouse.set_cursor((8,8), (4,4), Mask, Mask)
    def RenderInitialScreen(self):
        self.ClearCursor()
        # Circles:
        CrosshairImage = pygame.Surface((500, 500))
        Rad1 = 25
        Rad2 = 150
        Rad3 = 220
        pygame.draw.circle(CrosshairImage, Colors.MediumGrey, (250, 250), Rad1, 1)
        pygame.draw.circle(CrosshairImage, Colors.MediumGrey, (250, 250), Rad2, 1)
        pygame.draw.circle(CrosshairImage, Colors.MediumGrey, (250, 250), Rad3, 1)
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250+Rad1-5, 250), (250+Rad1+5, 250))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250-Rad1-5, 250), (250-Rad1+5, 250))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250, 250+Rad1-5), (250, 250+Rad1+5))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250, 250-Rad1-5), (250, 250-Rad1+5))        
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250+Rad2-5, 250), (250+Rad2+5, 250))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250-Rad2-5, 250), (250-Rad2+5, 250))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250, 250+Rad2-5), (250, 250+Rad2+5))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250, 250-Rad2-5), (250, 250-Rad2+5))        
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250+Rad3-5, 250), (250+Rad3+5, 250))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250-Rad3-5, 250), (250-Rad3+5, 250))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250, 250+Rad3-5), (250, 250+Rad3+5))
        pygame.draw.line(CrosshairImage, Colors.MediumGrey, (250, 250-Rad3-5), (250, 250-Rad3+5))
        CrosshairSprite = GenericImageSprite(CrosshairImage, 150, 50)
        self.AddBackgroundSprite(CrosshairSprite)
        # Title (at top of screen):
        Sprite = GenericTextSprite("sniper rifle 27B/6: targeting mode activated", self.Width / 2, 10, Colors.Green, CenterFlag = 1, FontSize = 32)
        self.AddBackgroundSprite(Sprite)
        Sprite = GenericTextSprite("Scroll mouse to aim!  Click to fire!", self.Width / 2, 30, Colors.Green, CenterFlag = 1, FontSize = 18)
        self.AddBackgroundSprite(Sprite)
        # Monster sprites:
        self.MonsterSprites = pygame.sprite.Group()
        self.BuildMonsterSprites()
        # Time left:
        Sprite = GenericTextSprite("Time:", 650, 200, Color = Colors.Green, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        self.TimeSprite = GenericTextSprite("%.1f"%self.TimeLimit, 650, 220, FontSize = 24)
        self.AddForegroundSprite(self.TimeSprite)
        # Shots left:
        Sprite = GenericTextSprite("Shots:", 650, 300)
        self.AddBackgroundSprite(Sprite)
        self.BulletSprites = []
        X = 640
        BulletImage = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Bullet.png"))
        for Bullet in range(self.ShotsLeft):
            Sprite = GenericImageSprite(BulletImage, X, 320)
            X += BulletImage.get_rect().width + 1
            self.AddForegroundSprite(Sprite)
            self.BulletSprites.append(Sprite)
    def BuildMonsterSprites(self):
        self.AliveSprites = []
        for Monster in self.Monsters:
            Sprite = BattleSprites.CritterSpriteClass(self, Monster,0,0)
            Sprite.SnipeX = random.randrange(-SpriteFieldMax, SpriteFieldMax)
            Sprite.SnipeXDir = random.randrange(-30, 31) / float(10)
            Sprite.SnipeXAcc = random.randrange(-10, 11) / float(500)
            Sprite.SnipeY = random.randrange(-SpriteFieldMax, SpriteFieldMax)
            Sprite.SnipeYDir = random.randrange(-30, 31) / float(10)
            Sprite.SnipeYAcc = random.randrange(-10, 11) / float(500)
            self.MonsterSprites.add(Sprite)
            self.AliveSprites.append(Sprite)
            self.AddForegroundSprite(Sprite)
            self.SetSpriteXY(Sprite)
    def HandleMouseMoved(self,Position,Buttons,LongPause = 0):
        MousePosition = pygame.mouse.get_pos()
        if self.OldMouseX!=None:
            self.DeltaX = (MousePosition[0] - self.OldMouseX)*0.8
            self.DeltaY = (MousePosition[1] - self.OldMouseY)*0.8
        else:
            self.DeltaX = 0
            self.DeltaY = 0
        pygame.mouse.set_pos((self.CenterX, self.CenterY))
        self.OldMouseX = self.CenterX
        self.OldMouseY = self.CenterY
    def HandleLoop(self):
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface) 
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface)
        self.AnimationCycle+=1
        if (self.AnimationCycle>MaxAnimationCycle):
            self.AnimationCycle=0        
        for Sprite in self.AllSprites.sprites():
            Sprite.Update(self.AnimationCycle)
        self.DeltaX = 0
        self.DeltaY = 0
        if not pygame.mouse.get_focused():
            self.OldMouseX = None
            self.OldMouseY = None
        self.HandleEvents()
        self.Update()        
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)
    def Update(self):
        if self.AnimationCycle == self.QuitCycle:
            self.App.PopScreen(self)
        if self.ReloadTime:
            self.ReloadTime -= 1
        TimeLeft = self.TimeLimit - (time.clock() - self.StartInstant)
        if TimeLeft <= 0:
            TimeLeft = 0
            if not self.QuitCycle:
                self.QuitCycle = (self.AnimationCycle + EndingPauseTimeOver) % MaxAnimationCycle
        TimeStr = "%.1f"%(TimeLeft)
        if TimeStr != self.OldTimeStr:
            Image = TextImage(TimeStr, FontSize = 24)
            self.TimeSprite.image = Image
            self.OldTimeStr = TimeStr
        if self.AnimationCycle == self.QuitCycle:
            self.Finish()
        for Sprite in self.AliveSprites:
            Sprite.SnipeX += Sprite.SnipeXDir + self.DeltaX
            Sprite.SnipeY += Sprite.SnipeYDir + self.DeltaY
            Sprite.SnipeXDir += Sprite.SnipeXAcc
            if Sprite.SnipeXDir > 3:
                Sprite.SnipeXAcc = -abs(Sprite.SnipeXAcc)
            if Sprite.SnipeXDir < -3:
                Sprite.SnipeXAcc = abs(Sprite.SnipeXAcc)
            Sprite.SnipeYDir += Sprite.SnipeYAcc
            if Sprite.SnipeYDir > 3:
                Sprite.SnipeYAcc = -abs(Sprite.SnipeYAcc)
            if Sprite.SnipeYDir < -3:
                Sprite.SnipeYAcc = abs(Sprite.SnipeYAcc)
            if (Sprite.SnipeX) > SpriteFieldMax:
                Sprite.SnipeX -= 2*SpriteFieldMax
            if (Sprite.SnipeY) > SpriteFieldMax:
                Sprite.SnipeY -= 2*SpriteFieldMax
            if (Sprite.SnipeX) < -SpriteFieldMax:
                Sprite.SnipeX += 2*SpriteFieldMax
            if (Sprite.SnipeY) < -SpriteFieldMax:
                Sprite.SnipeY += 2*SpriteFieldMax
            self.SetSpriteXY(Sprite)
    def SetSpriteXY(self, Sprite):
        X = self.CenterX + int(SnipeRadius  * Sprite.SnipeX / float(SpriteFieldMax))
        Y = self.CenterY + int(SnipeRadius * Sprite.SnipeY / float(SpriteFieldMax))
        Sprite.rect.center = (X,Y)
        Sprite.CenterX = X
        Sprite.CenterY = Y
        Sprite.X = X
        Sprite.Y = Y
    def Finish(self):
        pygame.mouse.set_cursor(*self.OldCursor)
        self.App.PopScreen(self)
    def ShootMonster(self, Sprite):        
        #Calibrate damage to what characters can do:
        Damage = 0
        for Player in Global.Party.Players:
            Damage = max(Damage, Player.GetDamage())
        Damage *= 7
        if Global.Party.KeyItemFlags.get("Toxic Shells", None):
            if not Sprite.Critter.HasPerk("Poison Immune"):
                Sprite.Critter.Perks["Poison"] = 250
        Sprite.Critter.HP = max(Sprite.Critter.HP - Damage, 0)
        if Sprite.Critter.IsDead():
            Sprite.AnimateDeath()
            self.AliveSprites.remove(Sprite)
        else:
            Sprite.AnimateOuch(Damage)
    def HandleMouseClickedHere(self, Position, Button):
        if self.ReloadTime:
            return
        if (self.ShotsLeft <= 0):
            return
        if self.BulletSprites:
            self.BulletSprites[-1].kill()
            del self.BulletSprites[-1]
        self.ReloadTime = self.MaxReloadTime
        self.ShotsLeft -= 1
        Resources.PlayStandardSound("GolgoM16.wav")
        Dummy = DummySprite(pygame.Rect(self.CenterX, self.CenterY,1,1))
        Sprites = pygame.sprite.spritecollide(Dummy,self.MonsterSprites, 0)
        for Sprite in Sprites:
            if Sprite.Critter.IsAlive():
                self.ShootMonster(Sprite)
        # If we're out of bullets or out of monsters, then we should exit soon:
        if (not self.ShotsLeft) or (not self.AliveSprites):
            self.QuitCycle = (self.AnimationCycle + EndingPause) % MaxAnimationCycle
        #self.Redraw()
    def DisplayBouncyNumber(self, X, Y, Number, Color = Colors.White):
        "Display a bouncy numbered, CENTERED around the given X coordinate"
        DigitWidth=10 # hard coded :(
        NumberStr = str(Number)
        X = X - int(DigitWidth * len(NumberStr)/2.0)
        for Index in range(len(NumberStr)):
            Digit = NumberStr[Index]
            Sprite = BattleSprites.BouncyNumber(Digit,X+(DigitWidth*Index),Y,Color,Index*5)
            self.AddAnimationSprite(Sprite)
    def AnimateParticles(self, X, Y, ShrapnelClass, ParticleCount=50):
        for Index in range(ParticleCount):
            Sprite = ShrapnelClass(X+random.randrange(-5,6),Y+random.randrange(-5,6),25)
            self.AllSprites.add(Sprite)
            self.AnimationSprites.add(Sprite)
            