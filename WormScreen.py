"""
A minigame similar to Worms, or Scorched Earth, or all the other shoot-things-at-other-tanks
games.
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
from BattleSprites import *
import math
import Critter
import Magic
import sys

WScreen = None

Deg2Rad = math.pi / 180.0

class WormStates:
    ComputerTurn = 0
    ComputerAimingGun = 5
    ComputerPowering = 6
    PlayerTurn = 1
    BulletFlying = 2
    Exploding = 3
    Ending = 4

class TankSprite(GenericImageSprite):
    Width = 36
    Height = 20
    Radius = 10
    GunRadius = 20
    def __init__(self, X, Y, Pilot, Wall): # CenterX and baseY
        self.image = pygame.Surface((self.Width, self.Height))
        GenericImageSprite.__init__(self, self.image, X, Y)
        self.Label = None
        self.Angle = -45 * Deg2Rad
        self.HP = 100
        self.Pilot = Pilot # A string, or a player instance
        self.Reposition(X, Y, Wall)
        self.Draw()
        
        #self.BuildLabel()
    def Reposition(self, X, Y, Wall):
        self.rect.bottom = Y
        self.rect.left = X - self.rect.width / 2
        self.Wall = Wall # The wallsprite we're sitting on
        if not self.Label:
            self.BuildLabel()
        else:
            self.Label.rect.center = (self.rect.center[0], self.rect.bottom + 10)
    def IsAlive(self):
        return (self.HP > 0)
    def IsPlayer(self):
        if isinstance(self.Pilot, Critter.Critter):
            return 1
        return 0
    def GetName(self):
        if isinstance(self.Pilot, Critter.Critter):
            return self.Pilot.Name
        return self.Pilot
    def BuildLabel(self):
        if type(self.Pilot) == type(""):
            Color = Colors.Red
        else:
            Color = Colors.Green
        Sprite = GenericTextSprite(self.GetName(), self.rect.center[0], self.rect.bottom + 1, Color, CenterFlag = 1)
        Sprite.rect.center = (self.rect.center[0], self.rect.bottom + 10)
        self.Label = Sprite
    def GetCannonTip(self):
        (X, Y) = (self.rect.width / 2, self.rect.height) #(self.rect.center[0], self.rect.bottom)
        LineX = X + (self.GunRadius * math.cos(self.Angle))
        LineY = Y + (self.GunRadius * math.sin(self.Angle))
        return (self.rect.left + LineX, self.rect.top + LineY)
    def Draw(self):
        self.image.fill(Colors.Black)
        if self.HP == 100:
            Color = Colors.LightGrey
        elif self.HP > 60:
            Color = Colors.Green
        elif self.HP > 30:
            Color = Colors.Yellow
        else:
            Color = Colors.Red
        (X, Y) = (self.rect.width / 2, self.rect.height) #(self.rect.center[0], self.rect.bottom)
        StartAngle = 0
        EndAngle = 2 * math.pi - 0.1
        pygame.draw.circle(self.image, Color, (X, Y), self.Radius, 0)
        pygame.draw.circle(self.image, Colors.White, (X, Y), self.Radius, 1)
        LineX = X + (self.GunRadius * math.cos(self.Angle))
        LineY = Y + (self.GunRadius * math.sin(self.Angle))
        pygame.draw.line(self.image, Color, (X, Y), (LineX, LineY), 2)        
    def MoveCannon(self, Delta):
        self.Angle += Delta
        self.Angle = min(self.Angle, -math.pi * 0.05)
        self.Angle = max(-math.pi * 0.95, self.Angle)
        self.Draw()
    def Drive(self):
        OldX = self.rect.center[0]
        self.rect.left += self.dX
        MoveOK = 1
        # Check for collisions:
        Tanks = pygame.sprite.spritecollide(self, WScreen.TankSprites, 0)
        for Tank in Tanks:
            if Tank != self:
                MoveOK = 0
        Walls = pygame.sprite.spritecollide(self, WScreen.WallSprites, 0)
        for Wall in Walls:
            if Wall != self.Wall:
                MoveOK = 0
        # Check for running off the edge:
        if self.rect.left < self.Wall.rect.left:
            MoveOK = 0
        if self.rect.right > self.Wall.rect.right:
            MoveOK = 0
        if MoveOK:
            self.Label.rect.left += self.dX 
        else:
            self.rect.left -= self.dX
            self.dX = 0
            ##print "OOF!"
Horizontal = 0
Vertical = 1

class WallSprite(GenericImageSprite):
    def __init__(self, X, Y, Layout, Length, Indestructible = 0):
        if Layout == Horizontal:
            Width = Length
            Height = 10
        else:
            Width = 10
            Height = Length
        self.Layout = Layout
        self.image = pygame.Surface((Width, Height))
        pygame.draw.rect(self.image, Colors.MediumGrey, (0, 0, Width, Height), 0)
        pygame.draw.rect(self.image, Colors.White, (0, 0, Width, Height), 1)
        GenericImageSprite.__init__(self, self.image, X, Y)
        self.Indestructible = Indestructible

class BulletSprite(GenericImageSprite):
    Gravity = 0.001
    BounceDecay = 0.65
    BounceMinorDecay = 0.85
    MaxFuse = 600
    MovesPerTick = 3
    MinVelocity = 0.001
    def __init__(self, Tank, dX, dY):
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "Bullet.png"))
        (X, Y) = Tank.rect.center
        GenericImageSprite.__init__(self, Image, X, Y)
        self.rect.center = (X, Y)
        self.X = X
        self.Y = Y
        self.dX = dX
        self.dY = dY
        self.Fuse = 0
        self.Tank = Tank
        self.Exploded = 0
        self.TicksSinceBounce = 0
        self.LastWall = None
    def Velocity(self):
        return max(abs(self.dX), abs(self.dY))
    def TestTrajectory(self):
        OldX, OldY = self.rect.center
        self.TicksSinceBounce = 0
        for Tick in range(self.MaxFuse * self.MovesPerTick):
            self.MoveTick()
            if self.Velocity() < self.MinVelocity and self.TicksSinceBounce < 10:
                break
            if self.Exploded:
                break
        (X, Y) = self.rect.center
        self.rect.center = (OldX, OldY)
        return (X, Y)
    def GetCollideTank(self):
        Sprite = pygame.sprite.spritecollideany(self, WScreen.TankSprites)
        if Sprite:
            if Sprite==self.Tank and self.Fuse<40:
                return None # shell is still exiting the shaft!
            # Don't hit the empty part of the sprite:
            dX = (self.rect.center[0] - Sprite.rect.center[0])
            dY = (self.rect.center[1] - Sprite.rect.bottom)
            Dist = math.sqrt(dX**2 + dY**2)
            ##print Dist, TankSprite.Radius
            if Dist > TankSprite.Radius+4:
                return None
            return Sprite
    def MoveTick(self):
        self.TicksSinceBounce += 1
        (OldX, OldY) = (self.X, self.Y)
        self.X += self.dX
        self.Y += self.dY
        if self.X > 800:
            self.X = 0
        if self.X < 0:
            self.X = 800 
        self.dY += self.Gravity
        Bounce = 0
        CollideTank = self.GetCollideTank()
        if CollideTank:
            self.Explode()
        CollideWalls = pygame.sprite.spritecollide(self, WScreen.WallSprites, 0)
        for CollideWall in CollideWalls:
            if CollideWall:# and (CollideWall != self.LastWall):
                Bounce = 1
                self.TicksSinceBounce = 0
                self.LastWall = CollideWall
                if CollideWall.Layout == Horizontal:
                    # Did we hit the top/bottom, or the side?
                    HitFace = 1
                    if (CollideWall.rect.top < self.rect.center[1] < CollideWall.rect.bottom):
                        HitFace = 0
                    if HitFace:
                        #print "Face --"
                        self.dY = -self.dY
                        if (self.dY > 0 and self.dY < 0.01):
                            self.dY = 0
                        self.dY = self.dY * self.BounceDecay
                        self.dX = self.dX * self.BounceMinorDecay
                        self.rect.center = (self.X,self.Y)
                        if self.dY < 0:
                            self.rect.bottom = CollideWall.rect.top - 1
                        else:
                            self.rect.top = CollideWall.rect.bottom + 1
                        (self.X, self.Y) = self.rect.center
                    else:
                        #print "Side --"
                        self.dX = -self.dX
                        self.dX = self.dX * self.BounceDecay
                        self.dY = self.dY * self.BounceMinorDecay
                        self.rect.center = (self.X,self.Y)
                        if self.dX < 0:
                            self.rect.right = CollideWall.rect.left - 1
                        else:
                            self.rect.left = CollideWall.rect.right + 1
                        (self.X, self.Y) = self.rect.center
                else:
                    # Did we hit the top/bottom, or the side?
                    HitFace = 1
                    if (CollideWall.rect.left < self.rect.center[0] < CollideWall.rect.right):
                        HitFace = 0
                    if HitFace:
                        #print "Face |"
                        self.dX = -self.dX
                        self.dX = self.dX * self.BounceDecay
                        self.dY = self.dY * self.BounceMinorDecay
                        self.rect.center = (self.X,self.Y)
                        if self.dX < 0:
                            self.rect.right = CollideWall.rect.left - 1
                        else:
                            self.rect.left = CollideWall.rect.right + 1
                        (self.X, self.Y) = self.rect.center
                        
                    else:
                        #print "Side |"
                        self.dY = -self.dY
                        self.dY = self.dY * self.BounceDecay
                        self.dX = self.dX * self.BounceMinorDecay
                        if self.dY < 0:
                            self.rect.bottom = CollideWall.rect.top - 1
                        else:
                            self.rect.top = CollideWall.rect.bottom + 1
                        (self.X, self.Y) = self.rect.center
                #print "New directions:", self.dX, self.dY
                #sys.stdin.readline()
        if Bounce:
            pass
##            self.X = OldX
##            self.Y = OldY
        else:
            self.LastWall = None
        self.rect.center = (self.X,self.Y)
        return Bounce
    def Update(self, Dummy = None):
        Bounce = 0
        for X in range(5):
            Bounce = self.MoveTick() or Bounce
        if Bounce and (max(abs(self.dX), abs(self.dY))>0.15) and WScreen.TicksSinceNoise > 5:
            Resources.PlayStandardSound("Bleep2.wav")
            WScreen.TicksSinceNoise = 0
        self.Fuse += 1
        if self.Fuse >= self.MaxFuse:
            self.Explode()
        if self.Velocity() < self.MinVelocity and self.TicksSinceBounce < 10:
            self.Explode()
    def Explode(self):
        self.Exploded = 1

class PowerSprite(GenericImageSprite):
    def __init__(self, X, Y):
        self.image = pygame.Surface((200, 16))
        GenericImageSprite.__init__(self, self.image, X, Y)
        self.Draw(0)
    def Draw(self, PowerLevel):
        self.image.fill(Colors.Black)
        pygame.draw.rect(self.image, Colors.White, (0, 0, 199, 15), 1)
        if PowerLevel:
            pygame.draw.rect(self.image, Colors.Red, (1, 1, PowerLevel*2, 13), 0)

class WormScreen(Screen.TendrilsScreen):
    FontSize = 32
    def __init__(self, App):
        global WScreen
        Screen.TendrilsScreen.__init__(self,App)
        WScreen = self
        self.CannonSpeed = 0
        self.PowerLevel = None
        self.PowerDir = 1
        self.Timer = 0
        self.TicksSinceNoise = 0
        self.TurnsSinceAction = 0 # Detect (and prevent) stalemate
        self.SummonSong("tower")
        self.Start()
    def AnimateParticles(self, X, Y, ShrapnelClass, ParticleCount=50):
        for Index in range(ParticleCount):
            Sprite = ShrapnelClass(X+random.randrange(-5,6),Y+random.randrange(-5,6),25)
            self.AllSprites.add(Sprite)
            self.AnimationSprites.add(Sprite)        
    def Start(self):
        self.State = WormStates.PlayerTurn
        self.ShrapnelSprites = pygame.sprite.Group()
        self.TankSprites = pygame.sprite.Group()
        self.TankList = []
        self.CurrentTankIndex = None
        self.WallSprites = pygame.sprite.Group()
        self.Timer = 0
        self.PlaceWallsAndTanks()
        # Background stuff:
        self.StatusBarSprite = GenericTextSprite("XXX", 2, 575, FontSize = 36)
        self.AddBackgroundSprite(self.StatusBarSprite)
        Sprite = GenericTextSprite("Power (hold SPACE to charge and fire)", 500, 565)
        self.AddBackgroundSprite(Sprite)
        self.PowerSprite = PowerSprite(500, 582)
        self.AddForegroundSprite(self.PowerSprite)
        self.StartNextTurn()
    def GetDamages(self, ExplosionPos):
        (X, Y) = ExplosionPos
        List = []
        for Tank in self.TankList:
            if Tank.IsAlive():
                dX = X - Tank.rect.center[0]
                dY = Y - Tank.rect.center[1]
                Distance = math.sqrt(dX**2 + dY**2)
                if Distance > 50:
                    continue
                if Distance > 40:
                    Damage = 10
                elif Distance > 30:
                    Damage = 20
                else:
                    Damage = 40
                List.append((Tank, Damage))
        return List
    def Update(self):
        self.TicksSinceNoise += 1
        if self.State == WormStates.PlayerTurn:
            self.UpdatePlayerTurn()
        elif self.State == WormStates.BulletFlying:
            self.UpdateBulletFlying()
        elif self.State == WormStates.Exploding:
            self.UpdateExploding()
        elif self.State == WormStates.ComputerTurn:
            self.UpdateComputerTurn()
        elif self.State == WormStates.ComputerAimingGun:
            self.UpdateComputerAim()
        elif self.State == WormStates.ComputerPowering:
            self.UpdateComputerPowering()
    def UpdateComputerPowering(self):
        if not self.PowerLevel:
            self.PowerLevel = 0
        if self.PowerLevel < self.BestShot[1]:
            self.PowerLevel += 0.5
            self.PowerSprite.Draw(self.PowerLevel)
        else:
            self.FireCannon(self.PowerLevel)
    def UpdateComputerAim(self):
        Tank = self.TankList[self.CurrentTankIndex]
        Angle = self.BestShot[0]
        if Tank.Angle < Angle:
            Tank.Angle = min(Tank.Angle + 0.015, Angle)
        elif Tank.Angle > Angle:
            Tank.Angle = max(Tank.Angle - 0.015, Angle)
        else:
            self.State = WormStates.ComputerPowering
        Tank.Draw()
    def UpdateComputerTurn(self):
        self.Timer -= 1
        if self.Timer <= 0:
            # Try to teleport, if the game is getting stale:
            if self.TurnsSinceAction > 6: #%%% 6
                Teleported = self.TeleportComputerPlayer()
                if Teleported:
                    return
            self.State = WormStates.ComputerAimingGun
            return
        if self.Timer % 9 == 0:
            self.ComputerConsiderMove()
    def TeleportComputerPlayer(self):
        
        Tank = self.TankList[self.CurrentTankIndex]
        # Find a tank position taht's not TOO close to the rest:
        for Position in self.TankPositions:
            (X, Y, Wall) = (Position[0], Position[1], Position[2])
            Dist = self.GetDistanceToLiveTank(X, Y)
            if Dist >= 100:
                break
        if Dist<=100:
            return 0 # failed!  Nowhere to go.
        # %%% More animation here?
        Resources.PlayStandardSound("MegamanNoise.wav")
        Tank.Reposition(X, Y, Wall)
        self.Redraw()
        self.ForegroundSprites.remove(Tank)
        self.ForegroundSprites.remove(Tank.Label)
        self.AddBackgroundSprite(Tank)       
        self.StartNextTurn()
        return 1 # success
    def GetDistanceToLiveTank(self, X, Y):
        Distance = 1000
        for Tank in self.TankList:
            if not Tank.IsAlive():
                continue
            dX = X - Tank.rect.center[0]
            dY = Y - Tank.rect.bottom            
            Dist = math.sqrt(dX**2 + dY**2)
            Distance = min(Dist, Distance)
        return Distance

    def ComputerConsiderMove(self):
        Tank = self.TankList[self.CurrentTankIndex]
        Angle = -random.randrange(30, 150) * Deg2Rad
        Power = random.randrange(0, 100)
        (dX, dY) = self.GetVelocity(Angle, Power)
        TempSprite = BulletSprite(Tank, dX, dY)
        (X,Y) = TempSprite.TestTrajectory()
        Tuples = self.GetDamages((X, Y))
        Score = 0
        for (Tank, Damage) in Tuples:
            if Tank.IsPlayer():
                Score += Damage
            else:
                Score -= Damage
##        print "The shot (%s, %s) has score %d"%(Angle, Power, Score)
        if Score > self.BestScore:
            self.BestScore = Score
            # Add some crappiness:
            Angle += random.randrange(-50, 50) / 800.0
            Power += random.randrange(-8, 9)
            Power = min(100, max(Power, 0))
            self.BestShot = (Angle, Power)
            
    def UpdateExploding(self):
        self.Timer -= 1
        if self.Timer <= 0:
            self.StartNextTurn()
    def UpdateBulletFlying(self):
        if not self.Bullet.Exploded:
            return
        Resources.PlayStandardSound("2600Dragon.wav")
        self.Bullet.kill()
        Sprite = Magic.MagicSprite(self.Bullet.rect.center[0],self.Bullet.rect.center[1],
                                   "fire1", 7, 10)
        self.AddAnimationSprite(Sprite)
        Damages = self.GetDamages(self.Bullet.rect.center)
        if len(Damages):
            self.TurnsSinceAction = 0
        else:
            self.TurnsSinceAction += 1
        for DamageTuple in Damages:
            (Tank, Damage) = DamageTuple
            Tank.HP -= Damage
            if not Tank.IsAlive():
                self.AnimateParticles(Tank.rect.center[0], Tank.rect.center[1], BattleSprites.BloodSprite)
                Tank.kill()
            else:
                Tank.Draw()
        self.Redraw()
        self.State = WormStates.Exploding
        self.Timer = 70
        self.Bullet = None
    def UpdatePlayerTurn(self):
        KeysPressed = pygame.key.get_pressed()
        Tank = self.TankList[self.CurrentTankIndex]
        # Cannon angle:
        if KeysPressed[Keystrokes.Up[0]] or KeysPressed[Keystrokes.Up[1]]:
            self.CannonSpeed = min(self.CannonSpeed + 0.002, .05)
        elif KeysPressed[Keystrokes.Down[0]] or KeysPressed[Keystrokes.Down[1]]:
            self.CannonSpeed = max(self.CannonSpeed - 0.002, -.05)
        else:
            if self.CannonSpeed > 0:
                self.CannonSpeed = max(self.CannonSpeed - 0.005, 0)
            else:
                self.CannonSpeed = min(self.CannonSpeed + 0.005, 0)
        if self.CannonSpeed != 0:
            Tank.MoveCannon(self.CannonSpeed)
        # Tank position:
        if KeysPressed[Keystrokes.Left[0]] or KeysPressed[Keystrokes.Left[1]]:
            Tank.dX = max(Tank.dX - 1, -4)
        elif KeysPressed[Keystrokes.Right[0]] or KeysPressed[Keystrokes.Right[1]]:
            Tank.dX = min(Tank.dX + 1, 4)
        else:
            if Tank.dX > 0:
                Tank.dX = max(0, Tank.dX - 1)
            else:
                Tank.dX = min(0, Tank.dX + 1)
        if Tank.dX != 0:
            Tank.Drive()
        # Power level:
        if self.PowerLevel!=None:
            self.PowerLevel += self.PowerDir
            if self.PowerLevel <= 0:
                self.PowerDir = abs(self.PowerDir)
            if self.PowerLevel >= 100:
                self.PowerDir = -abs(self.PowerDir)
            self.PowerSprite.Draw(self.PowerLevel)
        if KeysPressed[32]:
            if self.PowerLevel == None:
                self.PowerLevel = 0
                #%%%sfx
                self.PowerDir = 1
        else:
            if self.PowerLevel != None:
                self.FireCannon(self.PowerLevel)
    def GetVelocity(self, Angle, Power):
        dX = math.cos(Angle)
        dY = math.sin(Angle)        
        dX *= 1.5 * (Power + 5) / 100.0
        dY *= 1.5 * (Power + 5) / 100.0
        return (dX, dY)        
    def FireCannon(self, Power):
        "Power from 0 to 100"
        self.State = WormStates.BulletFlying
        Tank = self.TankList[self.CurrentTankIndex]
        self.StatusBarSprite.image = TextImage("%s fires!"%Tank.GetName())
        (dX, dY) = self.GetVelocity(Tank.Angle, Power)
        Resources.PlayStandardSound("GolgoM16.wav")
        Sprite = BulletSprite(Tank, dX, dY)
        self.AddAnimationSprite(Sprite)
        self.ForegroundSprites.remove(Tank)
        self.AddBackgroundSprite(Tank)
        self.ForegroundSprites.remove(Tank.Label)
        self.Redraw()
        self.Bullet = Sprite
    def HandleKeyPressed(self, Key):
        if Key == Keystrokes.Debug:
            #self.TeleportComputerPlayer()
            for Tank in self.TankList:
                if not Tank.IsPlayer():
                    Tank.HP = 0
            print "DEATH!!!"
    def AddWall(self, X, Y, Layout, Length, TankFlag = 0, Indestructible = 0):
        Wall = WallSprite(X, Y, Layout, Length, Indestructible)
        self.WallSprites.add(Wall)
        self.AddBackgroundSprite(Wall)
        TankX = X + Wall.rect.width / 2
        if TankFlag:
            self.TankPositions.append((TankX, Y, Wall))
        return Wall
    def PlaceWalls(self):
        # Ceiling:
        self.AddWall(0, 0, Horizontal, 800, 0, 1)
        # Floor:
        Wall = self.AddWall(0, 550, Horizontal, 800, 0, 1)
        for X in ((400,)):
            self.TankPositions.append((X, 550, Wall))
        # Upper row:
        self.AddWall(150, 137, Horizontal, 175, 1)
        self.AddWall(475, 137, Horizontal, 175, 1)
        # Middle row:
        self.AddWall(0, 274, Horizontal, 200, 1)
        self.AddWall(300, 274, Horizontal, 200, 1)
        self.AddWall(600, 274, Horizontal, 200, 1)
        self.AddWall(395, 284, Vertical, 130)
        # Lower row:
        self.AddWall(75, 411, Horizontal, 200, 1)
        self.AddWall(525, 411, Horizontal, 200, 1)
        self.AddWall(175, 500, Vertical, 50)
        self.AddWall(625, 500, Vertical, 50)
    def PlaceWallsAndTanks(self):
        self.TankPositions = [] # Entries: (x, base-y, resting-wall)
        self.PlaceWalls()
        self.AddTanks(self.TankPositions[:])
    def AddTanks(self, TankPositions):
        Names = ["Fwiffo", "Duke", "Biggles", "Zim", "Puchiko", "Krk'zzt", "Vega", "Pants"]
        PlayerNames = []
        for Player in Global.Party.Players:
            PlayerNames.append(Player.Name)
        Pilots = []
        while len(Pilots) < 4:
            Name = random.choice(Names)
            if Name in PlayerNames:
                continue
            Pilots.append(Name)
            Names.remove(Name)
        for Player in Global.Party.Players:
            Pilots.append(Player)
        random.shuffle(Pilots) # Roll initiative! #%%%
        for Pilot in Pilots:
            Position = random.choice(TankPositions)
            self.AddTank(Pilot, Position)
            TankPositions.remove(Position)
    def AddTank(self, Pilot, Position):
        # Position Entries: (x, base-y, resting-wall)
        Tank = TankSprite(Position[0], Position[1], Pilot, Position[2])
        self.AddBackgroundSprite(Tank)
        ##self.AddBackgroundSprite(Tank.Label)
        self.TankSprites.add(Tank)
        self.TankList.append(Tank)
    def RedrawBackground(self):
        "Override: Paint tank labels over the walls"
        self.BackgroundSurface.fill(Colors.Black)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        TempGroup = pygame.sprite.RenderUpdates()
        for Tank in self.TankList:
            if Tank.IsAlive() and Tank.Label not in self.ForegroundSprites.sprites():
                TempGroup.add(Tank.Label)
        TempGroup.draw(self.BackgroundSurface)
        TempGroup.empty()
        del TempGroup
        Dirty(self.BackgroundSurface.get_rect())
        
    def StartTurn(self, Tank):
        #print "Start turn:", Tank.GetName()
        self.CannonSpeed = 0
        self.PowerLevel = None
        self.PowerDir = 1
        self.PowerSprite.Draw(0)
        self.BackgroundSprites.remove(Tank)
        self.AddForegroundSprite(Tank)
        self.AddForegroundSprite(Tank.Label)
        if Tank.IsPlayer():
            self.StatusBarSprite.image = TextImage("%s's turn."%(Tank.GetName()))
        else:
            self.StatusBarSprite.image = TextImage("%s is thinking..."%Tank.GetName())
        Hilite = TankHighlightSprite(Tank)
        self.AddAnimationSprite(Hilite)
        self.Redraw()
        Tank.dX = 0
        if Tank.IsPlayer():
            self.State = WormStates.PlayerTurn
        else:
            self.State = WormStates.ComputerTurn
            self.BestScore = -1
            self.BestShot = None
            self.Timer = 100 
    def StartNextTurn(self):
        # First, check to see if the players won or lost:
        PlayersAlive = 0
        EnemiesAlive = 0
        for Tank in self.TankList:
            if Tank.IsAlive():
                if Tank.IsPlayer():
                    PlayersAlive = 1
                else:
                    EnemiesAlive = 1
        if not PlayersAlive:
            Global.App.ShowNewDialog("<CENTER><CN:BRIGHTRED>DEFEAT</C>\n\nYour tank batallion has been wiped out!",Callback = Global.App.ReturnToTitle)
            Global.App.PopScreen(self)
            return
        if not EnemiesAlive:
            Global.App.ShowNewDialog("<CENTER><CN:BRIGHTGREEN>VICTORY</C>\n\nYou have defeated the enemy tanks!")
            Global.App.PopScreen(self)
            return
        if self.CurrentTankIndex == None:
            # Find the first player:
            Index = 0
            for Tank in self.TankList:
                if Tank.IsAlive() and Tank.IsPlayer():
                    self.CurrentTankIndex = Index
                    break
                Index += 1
        else:
            while (1):
                self.CurrentTankIndex += 1
                if self.CurrentTankIndex >= len(self.TankList):
                    self.CurrentTankIndex = 0
                if self.TankList[self.CurrentTankIndex].IsAlive():
                    break
        self.StartTurn(self.TankList[self.CurrentTankIndex])

class TankHighlightSprite(GenericImageSprite):
    MaxTick = 9
    def __init__(self, Tank):
        self.Tick = self.MaxTick
        self.Tank = Tank
        self.Radius = 150
        self.Draw()
        GenericImageSprite.__init__(self, self.image, 0, 0)
        self.rect.center = Tank.rect.center
    def Update(self, Dummy = None):
        self.Tick -= 1
        if self.Tick <= 0:
            self.Tick = self.MaxTick
            self.Radius = int(self.Radius * 0.8)
            if (self.Radius <= 20):
                self.kill()
                return
            self.Draw()
    def Draw(self):
        self.image = pygame.Surface((self.Radius*2, self.Radius*2))
        self.image.set_colorkey(Colors.Black)
        pygame.draw.rect(self.image, Colors.White, (0, 0, self.Radius*2, self.Radius*2), 1)
        self.rect = self.image.get_rect()
        self.rect.center = self.Tank.rect.center
        self.rect.top += 10
pass
