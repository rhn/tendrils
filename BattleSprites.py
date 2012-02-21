"""
Sprite classes for use by the battle screen.  Includes sprites that can
animate themselves.
"""
from Utils import *
from Constants import *
import Global
import Resources

# From left to right, the arrows shown are: left, down, up, right.  (To match other rhythm games)
ArrowXByDirection = [0, 94, 56, 19, 131,
                     37, 113, 37, 113]

class ComboSprite(GenericTextSprite):
    BounceY = [0, -5, -9, -12, -13, -12, -9, -5, 0, -3, -5, -3, ]
    def __init__(self, Count, X, Y):
        self.Count = Count
        self.X = X
        self.Y = Y
        self.BounceTime = 0
        GenericTextSprite.__init__(self, "", X, Y, Colors.White, FontSize=24, CenterFlag=1)
    def Set(self, Count):
        if Count==self.Count:
            return
        if Count < 20:
            self.Color = Colors.LightGrey
        elif Count < 30:
            self.Color = Colors.White
        elif Count < 40:
            self.Color = Colors.Yellow
        elif Count < 50:
            self.Color = Colors.Orange
        elif Count < 60:
            self.Color = Colors.Purple
        else:
            self.Color = Colors.Green
        self.Count = Count
        if self.BounceTime == 0:
            self.BounceTime = 1
        if Count<10:
            self.ReplaceText("")
        else:
            self.ReplaceText("%d Hit!"%self.Count)

    def Update(self, Cycle):
        if Cycle%3==0:
            if self.BounceTime>0:
                self.BounceTime += 1
                if self.BounceTime >= len(self.BounceY):
                    self.BounceTime = 0
                self.rect.top = self.Y + self.BounceY[self.BounceTime]

class BouncyNumber(GenericImageSprite): #GenericTextSprite):
    """
    When creatures take damage, numbers pop out of them to show the damage; each digit is an instance of this
    class.
    """
    Lifetime = 100
    BouncyNumberHeights = [0, 5, 10, 15, 19, 22, 25, 27, 28, 29, 30, 29, 28, 27, 25, 22, 19, 15, 10, 5,
        0, 2, 5, 7, 9, 11, 12, 13, 14, 14, 15, 14, 14, 13, 12, 11, 9, 7, 5, 2]    
    def __init__(self,Digit,X,Y,Color=(255,255,255),Wait=0):
        if HappyFonts.has_key(Color):
            Image = HappyFonts[Color][Digit]
        else:
            Image = TextImage(Digit, Color, FontSize = 24)
        GenericImageSprite.__init__(self, Image, X, Y)
        self.rect.top -= 9 #self.rect.height / 2
        #GenericTextSprite.__init__(self,Digit,X,Y,Color,FontSize=24,CenterFlag=1)
        self.Wait = Wait
        self.Ticks = 0
        self.X = X
        self.Y = Y
        self.Move()
    def Update(self,AnimationCycle):
        self.Move()
    def Move(self):
        self.Ticks+=1
        if self.Ticks>self.Lifetime:
            self.kill()
            return
        AnimationIndex = self.Ticks - self.Wait
        if (AnimationIndex<0 or AnimationIndex>=len(self.BouncyNumberHeights)):
            BounceHeight=0
        else:
            BounceHeight = self.BouncyNumberHeights[AnimationIndex]
        #X = self.X - (self.image.get_width() / 2)
        Y = self.Y - BounceHeight
        self.rect.top = Y - self.rect.height / 2
        #self.rect.left = self.X - self.rect.width / 2
        #self.rect = pygame.Rect(X,Y,self.image.get_width(),self.image.get_height())


class BloodSprite(pygame.sprite.Sprite):
    # Avoid creating too many blood-sprites at once, since that will drop our fps to a crawl:
    MaxBloodCount = 50
    BloodBank = 0    
    def __init__(self,X,Y,Fuse):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.GetImage()
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.left = X
        self.rect.top = Y
        self.X=X
        self.Y=Y
        self.XDir = random.randrange(-5,6)
        self.YDir = random.randrange(-10,3)
        self.Fuse = Fuse
        self.DelayTicks = 3
        self.Draw()
        if BloodSprite.BloodBank >= BloodSprite.MaxBloodCount:
            self.DelayTicks = 0 #We'll immediately go away
            self.Fuse = 0
        else:
            BloodSprite.BloodBank += 1
    def GetImage(self):
        return pygame.Surface((3,3))
    def Draw(self):
        self.image.fill((random.randrange(156)+100,random.randrange(80),random.randrange(80)))
    def Update(self,AnimationCycle):
        self.DelayTicks -= 1
        if self.DelayTicks>0:
            return
        self.X=self.X+self.XDir+random.randrange(5)-2
        self.Y=self.Y+self.YDir+random.randrange(5)-2
        self.YDir=self.YDir+1
        self.rect[0]=self.X
        self.rect[1]=self.Y
        self.Draw()
        self.DelayTicks = 3
        self.Fuse -= 1
        if self.Fuse<=0:
            BloodSprite.BloodBank -= 1
            self.kill()

class CritterSpriteClass(GenericImageSprite):
    """
    Sprite for one of the critters (PCs or enemies) in the battle.  This class
    knows how to carry out ANIMATIONS (stand, attack, dodge, ouch, die).
    """
    BaseAnimateDelay = 5
    def __init__(self, Screen, Critter, X, Y):
        self.Critter = Critter
        self.Screen = Screen
        self.X = X
        self.Y = Y
        self.AnimateDelay = 0
        self.Critter.Species.LoadAnimationImages()
        self.CurrentAnimation = self.Critter.GetAnimation(AnimationType.Stand)
        self.CurrentAnimationStep = 0
        GenericImageSprite.__init__(self, self.CurrentAnimation.GetImage(0), X, Y)
        # Keep track of our center, so that people can shoot at it:
        (self.CenterX, self.CenterY) = self.rect.center
        if self.Critter.Species.RecenterX != None:
            self.CenterX = self.rect.left + self.Critter.Species.RecenterX
            self.CenterY = self.rect.top + self.Critter.Species.RecenterY
        self.StartAnimation(AnimationType.Stand)
    def PlayDead(self):
        # Show our final death frame, forever:
        DeathAnimation = self.Critter.GetAnimation(AnimationType.Death)
        if DeathAnimation:
            self.SwapImage(DeathAnimation.Images[-1]) #image = DeathAnimation.Images[-1] #GetImage(self.CurrentAnimationStep)
            self.rect.left += DeathAnimation.XPositions[-1]
            self.CurrentAnimation = None
    def AnimateDeath(self, Forced = 0):
        if self.CurrentAnimation.Type == AnimationType.Attack and not Forced:
            return # not yet!
        if not self.Critter.IsPlayer():
            if not self.Critter.GetAnimation(AnimationType.Death):
                self.Screen.AnimateParticles(self.rect.center[0], self.rect.center[1], BloodSprite)
                self.image = Global.NullImage 
                return
        
        self.StartAnimation(AnimationType.Death, Forced)
    def AnimateStand(self, Forced = 0):
        if self.CurrentAnimation and self.CurrentAnimation.Type == AnimationType.Attack and not Forced:
            return # not yet!  Finish the attack        
        self.StartAnimation(AnimationType.Stand)
    def AnimateOuch(self, Damage, Color = Colors.White):
        self.Screen.DisplayBouncyNumber(self.CenterX, self.CenterY, Damage, Color)
        if self.CurrentAnimation and self.CurrentAnimation.Type == AnimationType.Attack:
            return
        self.StartAnimation(AnimationType.Ouch)
    def AnimateDodge(self):
        self.Screen.DisplayBouncyNumber(self.CenterX, self.rect.center[1], "miss")
        if self.CurrentAnimation and self.CurrentAnimation.Type == AnimationType.Block:
            return
        self.StartAnimation(AnimationType.Block)
    def StartAnimation(self, Type, Force = 1):
        Animation = self.Critter.GetAnimation(Type)
        if not Animation:
            return
        if (not Force) and self.CurrentAnimation and self.CurrentAnimation.Type == AnimationType.Attack and Type!=AnimationType.Attack:
            return # Don't interrupt attack animations!
        self.AnimateDelay = self.BaseAnimateDelay
        self.CurrentAnimation = Animation
        self.CurrentAnimationStep = 0
        self.SwapImage(self.CurrentAnimation.GetImage(0))
        self.rect.left = self.X + self.CurrentAnimation.GetX(0)
        self.rect.top = self.Y + self.CurrentAnimation.GetY(0)
    def AnimateAttack(self):
        "Returns the number of update-cycles until DAMAGE should be displayed!"
        self.StartAnimation(AnimationType.Attack)
        if self.CurrentAnimation.Type == AnimationType.Attack:
            return 1 + self.CurrentAnimation.CriticalFrameNumber * self.BaseAnimateDelay
        else:
            return 1
    def Update(self, AnimationCycle):
        # If we're dead and not visible, return:
        if self.image == Global.NullImage:
            return
        self.AnimateDelay -= 1
        if self.AnimateDelay>0:
            return
        self.AnimateDelay = self.BaseAnimateDelay
        if not self.CurrentAnimation:
            return
        OldCel = self.CurrentAnimation.FrameCels[self.CurrentAnimationStep]
        self.CurrentAnimationStep += 1
        # Finish animation:
        if self.CurrentAnimationStep >= len(self.CurrentAnimation.FrameCels):
            self.CurrentAnimationStep = 0
            # Die, if we need to...
            if self.Critter.HP <= 0:
                if self.CurrentAnimation.Type != AnimationType.Death:
                    self.AnimateDeath(1)
                    return
                elif not self.Critter.IsPlayer():
                    self.image = Global.NullImage
                    return
            # Death animation doesn't cycle, it stays on the last image:
            if self.CurrentAnimation.Type == AnimationType.Death:
                self.CurrentAnimationStep = len(self.CurrentAnimation.FrameCels) - 1
                return
            # Repeat, or start the 'stand' animation
            if (not self.CurrentAnimation.RepeatFlag) and self.CurrentAnimation.Type != AnimationType.Stand:
                self.StartAnimation(AnimationType.Stand, 1)
                return

        NewCel = self.CurrentAnimation.FrameCels[self.CurrentAnimationStep]
        if NewCel == OldCel:
            return
        #Frame = self.CurrentAnimation.Frames[self.CurrentAnimationStep]
        NextImage = self.CurrentAnimation.GetImage(self.CurrentAnimationStep)
        if not NextImage:
            print "*** ERROR!!!"
            print self.CurrentAnimationStep
            print NewCel
        self.SwapImage(NextImage)
        #self.image = self.CurrentAnimation.GetImage(self.CurrentAnimationStep)        
        self.rect.left = self.X + self.CurrentAnimation.GetX(self.CurrentAnimationStep)
        self.rect.top = self.Y + self.CurrentAnimation.GetY(self.CurrentAnimationStep)
        Dirty(self.rect)
        
class HitQualitySprite(GenericImageSprite):
    "Display 'miss!' or 'bad!' when the player hits (or fails to hit) an arrow"
    def __init__(self, X, Y, Quality):
        FileName = "Miss.png"
        if Quality == 1:
            FileName = "Bad.png"
        elif Quality == 2:
            FileName = "Good.png"
        elif Quality == 3:
            FileName = "Perfect.png"
        elif Quality == HitQuality.FreezeDenied:
            FileName = "FreezeDenied.png"
        elif Quality == HitQuality.FreezeOk:
            FileName = "FreezeOk.png"
        ImagePath = os.path.join(Paths.ImagesMisc,FileName)
        self.Image = Resources.GetImage(ImagePath)
        self.Age = 0
        GenericImageSprite.__init__(self, self.Image, X, Y)
    def Update(self,AnimationCycle):
        "Move up, gradually"
        self.rect.top -= 1
        self.Age += 1
        if (self.Age > 100):
            self.kill()

class ProjectileSprite(GenericImageSprite):
    "A projectile, like an arrow or fireball.  Interpolates between start and end pixels."
    MaxImageDelay = 5
    def __init__(self, Screen, StartX, StartY, EndX, EndY, Name, TickTotal, FlipFlag = 0):
        self.StartX = StartX
        self.EndX = EndX
        self.StartY = StartY
        self.EndY = EndY
        self.Name = Name
        self.TickTotal = TickTotal
        self.Tick = 0
        self.ImageTick = 0
        self.ImageDelay = self.MaxImageDelay
        self.Screen = Screen
        self.FlipFlag = FlipFlag
        GenericImageSprite.__init__(self, Global.AmmoDump.GetImage(Name, self.ImageTick),self.StartX, self.StartY)
    def Update(self, Dummy):
        if self.Tick > self.TickTotal:
            self.kill()
            return
        self.Tick += 1
        self.ImageDelay -= 1
        self.rect.left = int(self.StartX + (self.EndX - self.StartX) * self.Tick / float(self.TickTotal))
        self.rect.top = int(self.StartY + (self.EndY - self.StartY) * self.Tick / float(self.TickTotal))
        if self.ImageDelay>0:
            return
        self.ImageTick += 1
        self.ImageDelay = self.MaxImageDelay
        self.image = Global.AmmoDump.GetImage(self.Name, self.ImageTick, self.FlipFlag)
       

DirKeys = {1:(264, 273), 2:(258,274), 3:(260,276), 4:(262,275),
           5:(263,),6:(265,),7:(257,), 8:(259,)}
class ArrowClass(GenericImageSprite):
    "An arrow, in the arrow swath"
    DefaultX = 50
    PixelsPerTick = 0.25 #%%
    PixelsPerMsec = 0.25 * 1.024 #%%
    CriticalY = 80 #80 #%%
    TicksToMsec = (0.001 / 2**-10)
    def __init__(self, ID, Direction, Color, IsOffense, Ticks, FreezeTime = 0, X = 0):
        self.Direction = Direction
        if (self.Direction < 1):
            self.Direction = 1
        if self.Direction > 8:
            self.Direction = 8
        self.FreezeTime = FreezeTime
        self.IsOffense = IsOffense
        self.Color = Color
        self.ID = ID
        self.GetImage()
        self.HalfWidth = self.Image.get_width() / 2
        self.HalfHeight = self.HalfWidth #self.Image.get_height() / 2
        self.TicksLeft = Ticks
        self.TriggeredFlag = 0
        self.FreezeQuality = None
        self.Y = int(self.CriticalY + self.PixelsPerTick * Ticks)
        self.X = X 
        GenericImageSprite.__init__(self, self.Image, self.X - self.HalfWidth, self.Y - self.HalfHeight)
    def __str__(self):
        return "<Arrow %s %s %s>"%(self.Direction, self.IsOffense, self.TicksLeft)
    def SetX(self, X):
        self.X = X
        self.rect.left = X - self.HalfWidth
    def GetImage(self):
        "set self.Image, based on direction and offense flag"
        if self.IsOffense:
            FileName = ["","OffenseUp","OffenseDown","OffenseLeft","OffenseRight","OffenseNW","OffenseNE","OffenseSW","OffenseSE"][self.Direction]
        else:
            FileName = ["","DefenseUp","DefenseDown","DefenseLeft","DefenseRight","DefenseNW","DefenseNE","DefenseSW","DefenseSE"][self.Direction]
        if self.FreezeTime:
            self.GetImageFreeze(FileName)
            return
        ImagePath = os.path.join(Paths.ImagesMisc,"%s.png"%FileName)
        self.Image = Resources.GetImage(ImagePath)
    def GetImageFreeze(self, FileName):
        """
        This is a FREEZE arrow.  The image will be a blur of smaller arrows, one every few pixels until we've
        gone far enough.
        """
        self.Width = 38
        self.Height = 38 + (self.PixelsPerTick * self.FreezeTime)
        self.Image = pygame.Surface((self.Width, self.Height))
        Y = 0
        Digit = 0
        while (Y < self.Height - 38):
            ImagePath = os.path.join(Paths.ImagesMisc, "%s.%d.png"%(FileName, Digit))
            Digit = (Digit+1)%3
            Image = Resources.GetImage(ImagePath)
            Image.set_colorkey(Colors.Black)
            self.Image.blit(Image, (0, Y))
            Y += 9
        #self.rect = self.image.get_rect()
    def Update(self,AnimationCycle):
        pass # Handled by BattleScreen
    def SetTicks(self, NewTicks):
        self.TicksLeft = NewTicks
        self.Y = int(self.CriticalY + self.PixelsPerTick * NewTicks)
        self.rect.top = self.Y - self.HalfHeight
    def MoveMsec(self, Msec):
        self.TicksLeft -= Msec / self.TicksToMsec
        self.Y = int(self.CriticalY + self.PixelsPerTick * self.TicksLeft)
        self.rect.top = self.Y - self.HalfHeight
    def GetKey(self):
        return DirKeys[self.Direction]
    def GetReversedKey(self):
        return DirKeys[OppositeDirections[self.Direction]]


if PSYCO_ON:
    psyco.bind(BouncyNumber.Move)
    psyco.bind(BouncyNumber.__init__)
    psyco.bind(ArrowClass.__init__)
