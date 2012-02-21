"""
Lock: Shoot from the sides, breaking down castle walls to get at the nougaty center.
"""
from Utils import *
from Constants import *
import Screen
import Global
import Resources
import os
import time
import string
import Party
import math
import ChestScreen

from BattleSprites import *

CScreen = None

TwoPi = 2*math.pi

class CastleLock(ChestScreen.TrapPanel):
    "Castle" # this string displayed on Calfo
    FontSize = 32
    CenterX = 400
    CenterY = 250
    BottomY = 500
    def __init__(self, *args, **kw):
        ChestScreen.TrapPanel.__init__(self, *args, **kw)
        self.Won = 0
        self.ReloadTime = 0
        self.LastShotIndex = None
        self.CastleSprites = []
    def ShowInstructions(self):
        Str = """Fire cannons from the four edges of the screen, by pressing the arrow keys. \
Hit the center node behind its rotating shields.  You have limited ammunition - if you run \
out of shots, the lock resets.

Press the <CN:GREEN>space bar</C> to reset the game"""
        Global.App.ShowNewDialog(Str, Callback = self.Start)
        
        self.VictoryTimer = None
    def IsDisarmed(self):
        return (self.Won and self.VictoryTimer<=0)
    def InitTrap(self):        
        self.BuildCastle()
        TimeLimits = [0, 90, 80, 70, 60, 50,
                      90, 80, 70, 60, 50,
                      90, 80, 70, 60, 50,]
        self.TimeLimit = TimeLimits[self.DungeonLevel]
        if self.HasNinja:
            self.TimeLimit *= 1.5
        self.RenderInitialScreen()
        self.BulletSprites = pygame.sprite.Group()
    def BuildCastle(self):
        if self.DungeonLevel <= 3:
            self.Radii = [40, 80]
            if self.DungeonLevel == 1:
                self.AngleSpeeds = [0.01, 0.03]
            if self.DungeonLevel == 2:
                self.AngleSpeeds = [0.01, 0.03]
            if self.DungeonLevel == 3:
                self.AngleSpeeds = [0.02, 0.04]
        elif self.DungeonLevel <= 8:
            self.Radii = [30, 60, 90]
            self.AngleSpeeds = [0.03, 0.02, 0.01]
        else:
            self.Radii = [20, 45, 80, 120]
            self.AngleSpeeds = [0.03, 0.008, 0.01, 0.015]
        self.Angles = [0]*len(self.Radii)
        
        self.Walls = []
        self.Walls.append([1]*6)
        self.Walls.append([1]*8)
        if len(self.Radii)>2:
            self.Walls.append([1]*15)
        if len(self.Radii)>3:
            self.Walls.append([1]*22)
        AmmoByLevel = [0, 2, 1, 1, 4, 3,
                       3, 2, 5, 4, 3,
                       5, 4, 4]
        Ammo = AmmoByLevel[self.DungeonLevel]
        self.Ammo = [Ammo, Ammo, Ammo, Ammo]
    def ResetCastle(self):
        self.BuildCastle()
        for Sprite in self.BulletSprites.sprites():
            Sprite.kill()
        self.UpdateAmmo()
        Resources.PlayStandardSound("MegamanNoise.wav")
    def RenderInitialScreen(self):
        for Radius in self.Radii:
            Image = pygame.Surface((Radius*2, Radius*2))
            Sprite = GenericImageSprite(Image, 405, self.CenterY)
            Sprite.rect.left -= Radius
            Sprite.rect.top -= Radius
            self.CastleSprites.append(Sprite)
            self.AddForegroundSprite(Sprite)
        self.ShrapnelSprites = pygame.sprite.Group()
        self.AmmoSprites = []
        X = [self.CenterX, self.CenterX, 790, 10]
        Y = [self.BottomY - 20, 0, self.CenterY, self.CenterY]
        for Index in range(4):
            Sprite = GenericTextSprite(self.Ammo[Index], X[Index], Y[Index], CenterFlag = 1)
            self.AmmoSprites.append(Sprite)
            self.AddForegroundSprite(Sprite)
    def UpdateAmmo(self):
        for Index in range(4):
            Sprite = self.AmmoSprites[Index]
            Sprite.image = TextImage(self.Ammo[Index])
    def Update(self):
        if not self.Master.Disarming:
            return
        if not self.Won:
            self.ReloadTime = max(0, self.ReloadTime - 1)
            self.UpdateCastles()
        else:
            for Sprite in self.AnimationSprites.sprites():
                Sprite.Update(0)
            self.VictoryTimer -= 1
    def UpdateCastles(self):
        # Move the castle:
        WallColors = ((255,155,155),(80,180,80),(155,155,255),
                      (180,80,80),(155,255,155), (80, 80, 180))
        for Index in range(len(self.CastleSprites)):
            self.Angles[Index] += self.AngleSpeeds[Index]
            if (self.Angles[Index] >= math.pi * 2):
                self.Angles[Index] -= (math.pi * 2)
            Castle = self.CastleSprites[Index]
            Castle.image.fill(Colors.Black)
            Radius = self.Radii[Index]
            AnglePerChunk = math.pi * 2 / float(len(self.Walls[Index]))
            for Chunk in range(len(self.Walls[Index])):
                Color = WallColors[Chunk % len(WallColors)]
                if self.Walls[Index][Chunk]:
                    AngleStart = self.Angles[Index] + AnglePerChunk*Chunk
                    AngleStop = self.Angles[Index] + AnglePerChunk*(Chunk+1)
                    pygame.draw.arc(Castle.image, Color, (0, 0, Radius*2, Radius*2),
                                    AngleStart, AngleStop,2)
        for Sprite in self.BulletSprites.sprites():
            OldCenter = Sprite.rect.center
            Sprite.rect.top += Sprite.dY
            Sprite.rect.left += Sprite.dX
            NewCenter = Sprite.rect.center
            # Hit things:
            if Sprite.dY:
                for Index in range(len(self.Radii)):
                    Radius = self.Radii[Index]
                    if OldCenter[1] >= (self.CenterY + Radius) and NewCenter[1] <= (self.CenterY + Radius):
                        self.HitCircle(Index, math.pi * 1.5, Sprite)
                    if OldCenter[1] <= (self.CenterY + Radius) and NewCenter[1] >= (self.CenterY + Radius):
                        self.HitCircle(Index, math.pi * 1.5, Sprite)
                    if OldCenter[1] >= (self.CenterY - Radius) and NewCenter[1] <= (self.CenterY - Radius):
                        self.HitCircle(Index, math.pi * 0.5, Sprite)
                    if OldCenter[1] <= (self.CenterY - Radius) and NewCenter[1] >= (self.CenterY - Radius):
                        self.HitCircle(Index, math.pi * 0.5, Sprite)
            if Sprite.dX:
                for Index in range(len(self.Radii)):
                    Radius = self.Radii[Index]
                    if OldCenter[0] >= (self.CenterX + Radius) and NewCenter[0] <= (self.CenterX + Radius):
                        self.HitCircle(Index, math.pi * 0.0, Sprite)
                    if OldCenter[0] <= (self.CenterX + Radius) and NewCenter[0] >= (self.CenterX + Radius):
                        self.HitCircle(Index, math.pi * 0.0, Sprite)
                    if OldCenter[0] >= (self.CenterX - Radius) and NewCenter[0] <= (self.CenterX - Radius):
                        self.HitCircle(Index, math.pi * 1.0, Sprite)
                    if OldCenter[0] <= (self.CenterX - Radius) and NewCenter[0] >= (self.CenterX - Radius):
                        self.HitCircle(Index, math.pi * 1.0, Sprite)
            if Sprite.dX > 0 and Sprite.rect.right >= self.CenterX:
                self.Win()
            if Sprite.dX < 0 and Sprite.rect.left <= self.CenterX:
                self.Win()
            if Sprite.dY > 0 and Sprite.rect.bottom >= self.CenterY:
                self.Win()
            if Sprite.dY < 0 and Sprite.rect.top <= self.CenterY:
                self.Win()
    def Win(self):
        Resources.PlayStandardSound("Kill.wav")
        self.Won = 1
        self.Master.DisableTrap()
        self.VictoryTimer = 120
        Sprite = GenericTextSprite("Hit!", self.CenterX, 100, FontSize = 32, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        self.Redraw()
        while len(self.ShrapnelSprites.sprites())<50:
            Sprite = ShrapnelClass(self.CenterX+random.randrange(-20,20), self.CenterY+random.randrange(-20,20))
            self.AddAnimationSprite(Sprite)
            self.ShrapnelSprites.add(Sprite)
    def HitCircle(self, Index, Angle, Sprite):
        if Angle == 0.0:
            Critical = math.pi * 1.3
        else:
            Critical = TwoPi
        AnglePerChunk = math.pi * 2 / float(len(self.Walls[Index]))
        for Chunk in range(len(self.Walls[Index])):
            AngleStart = self.Angles[Index] + AnglePerChunk*Chunk
            AngleStop = self.Angles[Index] + AnglePerChunk*(Chunk+1) + 0.01
            if (AngleStart >= Critical):
                AngleStart -= TwoPi
            if (AngleStop >= Critical):
                AngleStop -= TwoPi
            if (AngleStart < Angle <= AngleStop):
                if self.Walls[Index][Chunk]:
                    self.Walls[Index][Chunk] = 0
                    Sprite.kill()
                    if 0 == self.Ammo[0] == self.Ammo[1] == self.Ammo[2] == self.Ammo[3] and \
                       len(self.BulletSprites.sprites())==0:
                        self.ResetCastle()
                else:
                    pass
                    ##print "SWISH!", Index, Chunk
                return
    def HandleKeyPressed(self, Key):
        if Key == ord(" "):
            self.ResetCastle()
            return
        if Key in Keystrokes.Up:
            self.Shoot(0, self.CenterX, self.BottomY, 0, -1)
            return
        if Key in Keystrokes.Down:
            self.Shoot(1, self.CenterX, 000, 0, 1)
            return
        if Key in Keystrokes.Left:
            self.Shoot(2, 800, self.CenterY, -1, 0)
            return
        if Key in Keystrokes.Right:
            self.Shoot(3, 0, self.CenterY, 1, 0)
            return
    def Shoot(self, Index, X, Y, dX, dY):
        if self.Ammo[Index]<=0:
            return
        if self.ReloadTime > 0 and self.LastShotIndex == Index:
            return
        self.ReloadTime = 20
        self.LastShotIndex = Index
        self.Ammo[Index] -= 1
        self.UpdateAmmo()
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Bullet.png"))
        Sprite = GenericImageSprite(Image, X, Y)
        Sprite.dX = dX * 5
        Sprite.dY = dY * 5
        self.AddAnimationSprite(Sprite)
        self.BulletSprites.add(Sprite)

class ShrapnelClass(GenericImageSprite):
    def __init__(self, X, Y):
        Size = random.randrange(5, 10)
        Image = pygame.Surface((Size, Size))
        Image.fill((random.randrange(255),random.randrange(255),random.randrange(255)))
        GenericImageSprite.__init__(self, Image, X, Y)
        self.dX = random.randrange(-80, 80) / 5.0
        self.dY = random.randrange(-80, 0) / 5.0
    def Update(self, Dummy = None):
        self.rect.left += self.dX
        self.rect.top += self.dY
        self.dY = min(10.0, self.dY + 0.2)
        if self.rect.top > 500:
            self.kill()