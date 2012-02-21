"""
Magic!

The SpellClass holds basic information about a spell (name, mana cost), and has links to the magic functions
that are called when the spell is cast in combat.
"""
from Utils import *
from Constants import *
from BattleSprites import *
import Maze
import Resources
import random
import Global
import Critter
import math
import SummonPositions
import DancingScreen

class SpellTarget:
    NoTarget = 0
    OnePlayer = 1
    AllPlayers = 2
    OneMonster = 3
    MonsterRow = 4
    AllMonsters = 5
    EachMonster = 6
    
class SpellClass:
    def __init__(self, Name, Mana, Level, CombatUse, MazeUse, Target,
                 CastingTime, MazeEffectCode, BattleEffectCode, AnimationCode):
        self.Name = Name
        self.Mana = Mana
        self.Level = Level # minimum caster level
        self.CombatUse = CombatUse
        self.MazeUse = MazeUse
        self.Target = Target
        self.CastingTime = CastingTime
        self.MazeEffectCode = MazeEffectCode
        self.BattleEffectCode = BattleEffectCode
        self.AnimationCode = AnimationCode
    def IsValidTarget(self, Player):
        if self.Name == "Cure" and Player.IsDead():
            return 0
        return 1

class Spellbook:
    MageSpellCount = 15
    def __init__(self):
        self.MageSpells = []
        self.ClericSpells = []
        self.SummonerSpells = []

def GetSpell(Name):
    for Spell in Global.Spellbook.MageSpells:
        if Spell.Name == Name:
            return Spell
    for Spell in Global.Spellbook.ClericSpells:
        if Spell.Name == Name:
            return Spell
    for Spell in Global.Spellbook.SummonerSpells:
        if Spell.Name == Name:
            return Spell

def GetDamageForCaster(BaseDamage, Caster):
    """
    Give the damage done by a spell by a given caster.  (Modify the base damage
    using caster stats and perks)
    """
    Damage = BaseDamage
    if Caster.IsPlayer():
        if Caster.Species.Name=="Cleric":
            CastingStat = Caster.WIS
        else:
            CastingStat = Caster.INT
        Damage += Caster.Level
        Damage = Damage * (1.0 + (CastingStat-10)*0.07)
        Damage = Damage * (1.0 + Caster.Level*0.07)
    else:
        CastingStat = Caster.INT
        Damage = Damage * (1.0 + (CastingStat-10)*0.03)
        NerfFactor = 0.5
        if BaseDamage > 100:
            NerfFactor = 0.25
        Damage *= NerfFactor # nerf monster-spells
    return int(Damage)
    
def SpellDoDamage(Screen, CasterSprite, TargetSprite, SpellDamage, Delay, DamageType = None):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    BaseDamage = GetDamageForCaster(SpellDamage, Caster)
    if Caster.IsPlayer():
        if Caster.Species.Name=="Cleric":
            CastingStat = Caster.WIS
        else:
            CastingStat = Caster.INT
    else:
        CastingStat = Caster.INT
    # Handle magic-resistance:
    if Target.INT > 13:
        DamageMultiplier = 1.0 - min(0.75, (Target.INT - 12) * 0.02)
    else:
        DamageMultiplier = 1.0
    Damage = BaseDamage*DamageMultiplier + random.randrange(-3, 4)
    # Elemental resistance:
    if DamageType:
        Damage *= Target.GetElementMultiplier(DamageType)
    Damage = int(Damage)
    Damage = max(1, Damage)
    # Handle magic-evasion.  A 5% chance, given equal stats.
    EvadeChance = Target.WIS / float(7*CastingStat + 13*Target.WIS)
    if random.random() < EvadeChance:
        Screen.QueueDamageEvent(None, TargetSprite, 0, Delay, Colors.Red)
        return
    Screen.QueueDamageEvent(None, TargetSprite, Damage, Delay, Colors.Red)

class MagicSprite(GenericImageSprite):
    DefaultMaxImageDelay = 5
    def __init__(self, X, Y, Name, ImageCount, MaxImageDelay = DefaultMaxImageDelay):
        self.Name = Name
        self.ImageCount = ImageCount
        self.GetImages()
        self.image = self.Images[0]
        self.MaxImageDelay = MaxImageDelay
        self.ImageDelay = MaxImageDelay
        self.Tick = 0
        self.LoopFlag = 0
        self.ImageNumber = 0
        GenericImageSprite.__init__(self, self.image, X, Y)
        # CENTER on the given coords:
        self.rect.left -= self.rect.width / 2
        self.rect.top -= self.rect.height / 2
        self.SetMaxAge()
    def SetMaxAge(self):
        self.MaxAge = self.MaxImageDelay * len(self.Images)
    def GetImages(self):
        self.Images = []
        for ImageIndex in range(self.ImageCount):
            Image = Resources.GetImage(os.path.join(Paths.Images, "Magic", "%s.%d.png"%(self.Name, ImageIndex)))
            Image.set_colorkey(Colors.Black) #%%%
            self.Images.append(Image)
    def Update(self, Dummy):        
        self.Tick += 1
        if not self.LoopFlag and self.Tick >= self.MaxAge:
            self.kill()
            return
        self.ImageDelay -= 1
        if self.ImageDelay>0:
            return
        self.ImageNumber += 1
        if self.ImageNumber >= (self.ImageCount):
            self.ImageNumber = 0 # wrap
        self.ImageDelay = self.MaxImageDelay
        self.image = self.Images[self.ImageNumber] #Global.AmmoDump.GetImage(self.Name, self.ImageTick)
        Dirty(self.rect)

class SummonSpriteClass(GenericImageSprite):
    DefaultMaxImageDelay = 5
    FeedbackFrequency = 50
    def __init__(self, Screen, Spell, Positions, ImageCount, MaxImageDelay = DefaultMaxImageDelay):
        self.Screen = Screen
        self.Spell = Spell
        self.Name = Spell.Name
        self.StartedFlag = 0 # BattleScreen toggles this to get us going
        self.Positions = Positions # This is how we go gadding about the screen
        self.ImageCount = ImageCount
        self.GetImages()
        self.image = self.Images[0]
        self.MaxImageDelay = MaxImageDelay
        self.ImageDelay = MaxImageDelay
        self.Tick = 0
        self.Done = 0
        self.Damage = 0
        self.TotalDistance = 0
        self.ImageNumber = 0
        self.InvertX = random.choice((0,1))
        self.InvertY = random.choice((0,1))
        self.TimeUntilFeedback = self.FeedbackFrequency
        GenericImageSprite.__init__(self, self.image, self.Positions[0][0], self.Positions[0][1])
        # CENTER on the given coords:
        self.SetPosition(self.Positions[0])
    def SetPosition(self, Position):
        if self.InvertX:
            Position = (800 - Position[0], Position[1])
        if self.InvertY:
            Position = (Position[0], 600 - Position[1])
        self.rect.center = Position
    def GetDamage(self):
        Dist = self.GetAverageDistance()
        if Dist < 10:
            Damage = self.Damage
        else:
            Power = -(Dist-10) / 20.0
            Damage = self.Damage * (1.3 ** Power)
        return int(Damage)
    def GetImages(self):
        self.Images = []
        Name = self.Name
        if self.Name == "Mr. Sandman":
            Name = "MrSandman"
        for ImageIndex in range(self.ImageCount):
            Image = Resources.GetImage(os.path.join(Paths.Images, "Magic", "%s.%d.png"%(Name, ImageIndex)))
            Image.set_colorkey(Colors.Black) # important!
            self.Images.append(Image)
        if self.Spell.Name == "Metroid":
            self.Images.append(self.Images[2])
            self.Images.append(self.Images[1])
            self.ImageCount += 2
        if self.Spell.Name == "Thief":
            self.Images.append(self.Images[1])
            self.ImageCount += 1
        if self.Spell.Name == "Bahamut":
            self.Images.append(self.Images[2])
            self.Images.append(self.Images[1])
            self.ImageCount += 2
        if self.Spell.Name == "Phoenix":
            print self.ImageCount, self.Images
            NewImages = (self.Images[0], self.Images[1], self.Images[2], self.Images[1],
                         self.Images[0], self.Images[1], self.Images[2], self.Images[1],
                         self.Images[0], self.Images[1], self.Images[2], self.Images[1],
                         self.Images[3], self.Images[4], self.Images[5], self.Images[4], self.Images[3])
            self.Images = NewImages
            #self.Images.append(self.Images[2])
            #self.Images.append(self.Images[1])
            self.ImageCount = len(self.Images)
            
    def Update(self, Dummy):
        self.UpdateMovement()
        self.UpdatePicture()
        Dirty(self.rect)        
    def UpdateMovement(self):
        if not self.StartedFlag:
            return
        self.Tick += 1
        if self.Tick >= len(self.Positions):
            self.kill()
            self.Done = 1
            return
        Dist = math.sqrt((self.rect.center[0] - self.Screen.MousePosition[0])**2 +
                                        (self.rect.center[1] - self.Screen.MousePosition[1])**2)
        self.TotalDistance += Dist
        self.SetPosition(self.Positions[self.Tick])
        self.TimeUntilFeedback -= 1
        if self.TimeUntilFeedback <= 0:
            self.TimeUntilFeedback = self.FeedbackFrequency
            if Dist<20:
                Quality = HitQuality.Perfect
            elif Dist<70:
                Quality = HitQuality.Good
            elif Dist<150:
                Quality = HitQuality.Poor
            else:
                Quality = HitQuality.Miss
            FeedbackSprite = HitQualitySprite(self.rect.center[0], self.rect.center[1], Quality)
            self.Screen.AddAnimationSprite(FeedbackSprite)
        
    def UpdatePicture(self):        
        self.ImageDelay -= 1
        if self.ImageDelay>0:
            return
        self.ImageNumber += 1
        if self.ImageNumber >= (self.ImageCount):
            self.ImageNumber = 0
        self.ImageDelay = self.MaxImageDelay
        self.image = self.Images[self.ImageNumber] #Global.AmmoDump.GetImage(self.Name, self.ImageTick)
        
    def GetAverageDistance(self):
        return self.TotalDistance / len(self.Positions)



class FireballSprite(ProjectileSprite):
    def Update(self, Dummy):
        if self.Tick > self.TickTotal:
            # Print a wall of fire at our destination:
            FireSprite = MagicSprite(self.EndX, self.EndY, "fire1", 7)
            self.Screen.AddAnimationSprite(FireSprite)
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
        Dirty(self.rect)
    
    
def SpellAnimateFire(Screen, Caster, Target):
    if Caster.Critter.IsPlayer():
        StartX = Caster.rect.left
        FlipFlag = 0
    else:
        StartX = Caster.rect.right
        FlipFlag = 1        
    StartY = Caster.rect.center[1]
    ##
    EndX = Target.CenterX
    EndY = Target.CenterY
    Sprite = FireballSprite(Screen, StartX, StartY, EndX, EndY, "KiFire", 40, FlipFlag)
    Screen.AddAnimationSprite(Sprite)
    Resources.PlayStandardSound("Fireball.wav")

class FlareSprite(ProjectileSprite):
    def __init__(self, Screen, X, Y, XDir, YDir, Name = "Flare"):
        ProjectileSprite.__init__(self, Screen, 0, 0, 0, 0, Name, 100)
        self.X = X
        self.XDir = XDir
        self.Y = Y
        self.YDir = YDir
        self.TickTotal = 100
    def Update(self, Dummy):
        self.Tick += 1
        if self.Tick > self.TickTotal:
            self.kill()
            return
        self.Y += self.YDir
        self.YDir += 0.1
        self.X += self.XDir
        self.rect.top = self.Y
        self.rect.left = self.X
        self.ImageDelay -= 1
        if self.ImageDelay>0:
            return
        self.ImageTick += 1
        self.ImageDelay = self.MaxImageDelay
        self.image = Global.AmmoDump.GetImage(self.Name, self.ImageTick, self.FlipFlag)
        Dirty(self.rect)
        
    

class KaboomSprite(MagicSprite):
    def __init__(self, X, Y, Delay, ImageName, ImageCount, SoundName = None):
        MagicSprite.__init__(self, -500, -500, ImageName, ImageCount)
        self.PauseFlag = 1
        self.X = X - self.rect.width/2
        self.Y = Y - self.rect.height/3
        self.Delay = Delay
        self.SoundName = SoundName
    def Update(self, Dummy):
        if self.PauseFlag:
            self.Tick += 1
            if self.Tick >= self.Delay:
                self.Tick = 0
                self.rect.left = self.X
                self.rect.top = self.Y
                if self.SoundName:
                    Resources.PlayStandardSound("%s.wav"%self.SoundName)
                self.PauseFlag = 0
        else:
            MagicSprite.Update(self, Dummy)

def SpellAnimateFlare(Screen, Caster, Target):
    Resources.PlayStandardSound("ISFXSTRT.WAV")
    for Index in range(10):
        XDist = random.randrange(100, 600)
        if random.random()>0.5:
            XDist *= -1
        XDir = -XDist / 100.0
        StartY = Target.rect.center[1] + random.randrange(-350, 350)
        YDir = (Target.rect.center[1]- StartY - 10000*0.05) / 100.0
        Sprite = FlareSprite(Screen, Target.CenterX + XDist + random.randrange(-60,0), StartY, XDir, YDir)
        Screen.AddAnimationSprite(Sprite)
    # And explosion:
    Sprite = KaboomSprite(Target.CenterX+10, Target.CenterY-70, 100, "Kaboom", 4, "Kaboom")
    Screen.AddAnimationSprite(Sprite)
    Sprite = KaboomSprite(Target.CenterX-60, Target.CenterY-20, 120, "Kaboom", 4)
    Screen.AddAnimationSprite(Sprite)
    Sprite = KaboomSprite(Target.CenterX, Target.CenterY+20, 140, "Kaboom", 4, "Kaboom")
    Screen.AddAnimationSprite(Sprite)


def SpellAnimateSoulSmash(Screen, Caster, Target):
    Resources.PlayStandardSound("Beeyoorrm!.wav")
    X = Target.rect.center[0]
    Y = Target.rect.bottom    
    for Index in range(10):
        Color = (random.randrange(200, 255), random.randrange(0,100), random.randrange(0,100))
        Sprite = RegenLineSprite(X + random.randrange(-25, 25), Y, Index*7, Color)
        Screen.AddAnimationSprite(Sprite)
    # And explosion:
    Sprite = KaboomSprite(Target.CenterX, Target.CenterY-40, 100, "SoulSmash", 5, "SoulSmash")
    Screen.AddAnimationSprite(Sprite)
    Sprite = KaboomSprite(Target.CenterX+20, Target.CenterY+10, 110, "SoulSmash", 5)
    Screen.AddAnimationSprite(Sprite)
    Sprite = KaboomSprite(Target.CenterX-20, Target.CenterY+10, 120, "SoulSmash", 5, "SoulSmash")
    Screen.AddAnimationSprite(Sprite)


def SpellAnimateHealmore(Screen, Caster, Target):
    Resources.PlayStandardSound("Charging.wav")
    for Index in range(10):
        XDist = random.randrange(100, 600)
        if random.random()>0.5:
            XDist *= -1
        XDir = -XDist / 100.0
        StartY = Target.rect.center[1] + random.randrange(-350, 350)
        YDir = (Target.rect.center[1]- StartY - 10000*0.05) / 100.0
        Sprite = FlareSprite(Screen, Target.CenterX + XDist + random.randrange(-60,0), StartY, XDir, YDir, "Heart")
        Screen.AddAnimationSprite(Sprite)
    Sprite = RaiseAngelSprite(Target.CenterX, Target.CenterY - 40, "HealFull.wav")
    Screen.AddAnimationSprite(Sprite)
        
##    # And explosion:
##    Sprite = KaboomSprite(Target.CenterX+10, Target.CenterY-70, 100, 1)
##    Screen.AddAnimationSprite(Sprite)
##    Sprite = KaboomSprite(Target.CenterX-60, Target.CenterY-20, 120)
##    Screen.AddAnimationSprite(Sprite)
##    Sprite = KaboomSprite(Target.CenterX, Target.CenterY+20, 140, 1)
##    Screen.AddAnimationSprite(Sprite)
    
def SpellAnimateBlizzard(Screen, Caster, Target):
    Resources.PlayStandardSound("Blizzard.wav")
    if Caster.Critter.IsPlayer():
        X = 300
        Y = 250
    else:
        X = 650
        Y = 250
    Sprite = MagicSprite(X, Y, "Blizzard", 19)
    Sprite.MaxAge = 80
    Screen.AddAnimationSprite(Sprite)

def SpellAnimateMeteo(Screen, Caster, Target):
    Resources.PlayStandardSound("BladeStorm.wav")
    if Caster.Critter.IsPlayer():
        BaseX = 200 
    else:
        BaseX = 550 
    for Index in range(20):
        EndX = BaseX + random.randrange(200)
        StartX = EndX + random.randrange(-200, 200)
        EndY = 380
        StartY = EndY - random.randrange(50, 2000)
        TickTotal = (EndY - StartY) / 14
        Sprite = ProjectileSprite(Screen, StartX, StartY, EndX, EndY, "Meteor", TickTotal)
        Sprite.ImageTick = random.randrange(4)
        Screen.AddAnimationSprite(Sprite)

def SpellAnimateBlizzard2(Screen, Caster, Target):
    Resources.PlayStandardSound("Blizzard.wav")
    Resources.PlayStandardSound("Blizzard.wav")
    if Caster.Critter.IsPlayer():
        X = 300
        Y = 250
    else:
        X = 650
        Y = 250
    Sprite = MagicSprite(X, Y, "Blizzard2", 19)
    Sprite.MaxAge = 80
    Screen.AddAnimationSprite(Sprite)


class BouncingMagicSprite(MagicSprite):
    DefaultMaxImageDelay = 5
    def __init__(self, LeftX, RightX, Name, ImageCount, MaxImageDelay = DefaultMaxImageDelay):
        self.LeftX = LeftX
        self.RightX = RightX
        X = random.randrange(LeftX, RightX)
        Y = random.randrange(0, 450)
        MagicSprite.__init__(self, X, Y, Name, ImageCount, MaxImageDelay)
        self.DX = random.randrange(-40, 40) / 10.0
        self.DY = random.randrange(-40, 40) / 10.0
    def Update(self, Dummy):
        self.rect.left += self.DX
        self.rect.top += self.DY
        if (self.rect.left < self.LeftX):
            self.rect.right = self.RightX
        elif self.rect.right > self.RightX:
            self.rect.left = self.LeftX
        elif self.rect.top < 0:
            self.rect.bottom = 450
        elif self.rect.bottom > 450:
            self.rect.top = 0
        MagicSprite.Update(self, Dummy)
    def GetImages(self):
        self.Images = []
        for ImageIndex in range(self.ImageCount):
            Image = Resources.GetImage(os.path.join(Paths.Images, "Projectile", "%s.%d.png"%(self.Name, ImageIndex)))
            Image.set_colorkey(Colors.Black)
            self.Images.append(Image)

def SpellAnimateBladeStorm(Screen, Caster, Target):
    Resources.PlayStandardSound("BladeStorm.wav")
    if Caster.Critter.IsPlayer():
        LeftX = 150
        RightX = 400
    else:
        LeftX = 600
        RightX = 800
    for Index in range(20):
        Choice = random.randrange(0, 3)
        if Choice==0: 
            Name = "Axe"
            ImageCount = 16
        elif Choice == 1:
            Name = "Shuriken"
            ImageCount = 3
        elif Choice == 2:
            Name = "Boomerang"
            ImageCount = 4
        Sprite = BouncingMagicSprite(LeftX, RightX, Name, ImageCount)
        Sprite.MaxAge = 250
        Screen.AddAnimationSprite(Sprite)

def SpellAnimateHurtmore(Screen, Caster, Target):
    Resources.PlayStandardSound("Zaxx.wav")
    (X, Y)= Target.rect.center
    Sprite = MagicSprite(X, Y, "Claw", 6, 15)
    Screen.AddAnimationSprite(Sprite)


    
def MazeSpellDumapic(Screen, Caster, Spell):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    DirName = ["Fnord","North", "South", "West", "East"][Global.Party.Heading]
    Str = "You close your eyes and orient yourself in space and time...\n\n\
You are at position <CN:RED>%d</C> north and <CN:RED>%d</C> east on dungeon level <CN:RED>%d</C>.\n\
You are currently facing <CN:RED>%s</C>"%(Global.Party.Y, Global.Party.X, Global.Maze.Level, DirName)
    Global.App.ShowNewDialog(Str)
    
def MazeSpellCureDamage(Screen, Caster, Spell, Target, SpellDamage, WavName = "Heal"):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    BaseDamage = GetDamageForCaster(SpellDamage, Caster)
    Damage = max(1, BaseDamage)
    if Target.IsAlive():
        Target.HP = min(Target.HP + Damage, Target.MaxHP)
        Resources.PlayStandardSound("%s.wav"%WavName)
    Screen.StatusPanel.ReRender()

def MazeSpellCureAll(Screen, Caster, Spell, SpellDamage):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    for Target in Global.Party.Players:
        BaseDamage = GetDamageForCaster(SpellDamage, Caster)
        Damage = max(1, BaseDamage)
        if Target.IsAlive():
            Target.HP = min(Target.HP + Damage, Target.MaxHP)
    Resources.PlayStandardSound("Heal.wav")
    Screen.StatusPanel.ReRender()

def MazeSpellRaise(Screen, Caster, Spell, Target):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    Resources.PlayStandardSound("Allelujah.wav")
    if Target.IsDead():
        Target.HP = Target.MaxHP / 5
    if Spell.Name == "Healmore":
        Target.HP = Target.MaxHP
        Target.Perks["Poison"] = 0
        Target.Perks["Sleep"] = 0
        Target.Perks["Silence"] = 0
        Target.Perks["Stone"] = 0
        Target.Perks["Paralysis"] = 0        
    Screen.StatusPanel.ReRender()

def MazeSpellAntidote(Screen, Caster, Spell, Target):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    if Target.IsAlive():
        Target.Perks["Poison"] = 0
        Resources.PlayStandardSound("Antidote.wav")
    Screen.StatusPanel.ReRender()
    
def MazeSpellRegen(Screen, Caster, Spell, Target):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    if Target.IsAlive():
        RegenTime = GetDamageForCaster(10, Caster)
        Target.SpellPerks["Regen"] = RegenTime
    Resources.PlayStandardSound("Twinkle.wav")
    Screen.StatusPanel.ReRender()
def MazeSpellRepel(Screen, Caster, Spell):
    Resources.PlayStandardSound("Beeyoorrm!.wav")
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    Duration = 25 + (Caster.INT * 5)
    Global.Party.ActiveSpells["Repel"] = Duration
    Screen.RenderLHS()
def MazeSpellCompass(Screen, Caster, Spell):
    Resources.PlayStandardSound("Beeyoorrm!.wav")
    if Caster:
        Caster.MP = max(0, Caster.MP - Spell.Mana)
        Duration = 25 + (Caster.INT * 4)
    else:
        Duration = 25 + 10*4
    Global.Party.ActiveSpells["Compass"] = Duration
    Screen.RenderLHS()
    Screen.RenderCompass()

def MazeSpellStairmaster(Screen, Caster, Spell):
    Resources.PlayStandardSound("MegamanNoise.wav")
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    # Special code for level 9, where there are two stairways up (not connected):
    if (Global.Party.Z == 9):
        if Global.Party.X > 24 or (Global.Party.X == 24 and Global.Party.Y < 23) or \
            (Global.Party.X > 20 and Global.Party.Y == 17):
            Global.Party.X = 22
            Global.Party.Y = 17
            Global.Maze.TryEnterNewRoom(Screen, X, Y, Global.Party.Heading)
            Screen.RenderMaze()
            return
    # Standard case: Find a staircase, warp there.            
    for X in range(Maze.MazeWidth):
        for Y in range(Maze.MazeHeight):
            if Global.Maze.CanAscend(X, Y):
                Global.Party.X = X
                Global.Party.Y = Y
                Global.Maze.TryEnterNewRoom(Screen, X, Y, Global.Party.Heading)
                Screen.RenderMaze()
                return
    
def MazeSpellEsuna(Screen, Caster, Spell, Target):
    Caster.MP = max(0, Caster.MP - Spell.Mana)
    if Target.IsAlive():
        Target.Perks["Poison"] = 0
        Target.Perks["Sleep"] = 0
        Target.Perks["Silence"] = 0
        Target.Perks["Stone"] = 0
        Target.Perks["Paralysis"] = 0
    Resources.PlayStandardSound("Heal.wav")
    Screen.StatusPanel.ReRender()

def SpellCureDamage(Screen, CasterSprite, TargetSprite, SpellDamage, Delay):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    if Target.IsAlive():
        BaseDamage = GetDamageForCaster(SpellDamage, Caster)
        Damage = max(1, BaseDamage)
    else:
        Damage = 0
    Screen.QueueDamageEvent(None, TargetSprite, -Damage, Delay, Colors.Green)

def SpellCureAll(Screen, CasterSprite, SpellDamage, Delay):
    Caster = CasterSprite.Critter
    if Caster.IsPlayer():
        for PlayerSprite in Screen.PlayerSprites:
            if PlayerSprite.Critter.IsAlive():
                BaseDamage = GetDamageForCaster(SpellDamage, Caster)
                Damage = max(1, BaseDamage)
                #Target.HP = min(Target.HP + Damage, Target.MaxHP)
                Screen.QueueDamageEvent(None, PlayerSprite, -Damage, Delay, Colors.Green)
    else:
        for MonsterSprite in Screen.MonsterSprites:
            if MonsterSprite.Critter.IsAlive():
                BaseDamage = GetDamageForCaster(SpellDamage, Caster)
                Damage = max(1, BaseDamage)
                Screen.QueueDamageEvent(None, MonsterSprite, -Damage, Delay, Colors.Green)


def SpellAntidote(Screen, CasterSprite, TargetSprite, Delay):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    if not Target.IsAlive():
        return
    Screen.QueueConditionEvent(None, TargetSprite, "Poison", 0, Delay)
    
def SpellRegen(Screen, CasterSprite, TargetSprite, Delay):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    if not Target.IsAlive():
        return
    RegenTime = GetDamageForCaster(10, Caster)
    Screen.QueueSpellAttachEvent(None, TargetSprite, "Regen", RegenTime, Delay)

def SpellStoneskin(Screen, CasterSprite, TargetSprite, Delay):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    if not Target.IsAlive():
        return
    RegenTime = GetDamageForCaster(15, Caster)
    Screen.QueueSpellAttachEvent(None, TargetSprite, "Stoneskin", RegenTime, Delay)

def SpellBloodlust(Screen, CasterSprite, TargetSprite, Delay):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    if not Target.IsAlive():
        return
    RegenTime = GetDamageForCaster(15, Caster)
    Screen.QueueSpellAttachEvent(None, TargetSprite, "Bloodlust", RegenTime, Delay)

def SpellEsuna(Screen, CasterSprite, TargetSprite, Delay):
    Caster = CasterSprite.Critter
    Target = TargetSprite.Critter
    if not Target.IsAlive():
        return
    Screen.QueueConditionEvent(None, TargetSprite, "Poison", 0, Delay)
    Screen.QueueConditionEvent(None, TargetSprite, "Silence", 0, Delay)
    Screen.QueueConditionEvent(None, TargetSprite, "Paralysis", 0, Delay)
    Screen.QueueConditionEvent(None, TargetSprite, "Stone", 0, Delay)
    Screen.QueueConditionEvent(None, TargetSprite, "Sleep", 0, Delay)

def SpellRaise(Screen, Caster, Target, Spell):
    Delay = 100
    Screen.QueueResurrectEvent(Target, Target.Critter.MaxHP / 4, Delay)
    print "SpellRaise:", Caster, Target, Spell, Spell.Name
    if Spell.Name == "Healmore":
        Screen.QueueDamageEvent(Caster, Target, -Target.Critter.MaxHP, Delay, Colors.Green)
        Screen.QueueConditionEvent(None, Target, "Poison", 0, Delay)
        Screen.QueueConditionEvent(None, Target, "Silence", 0, Delay)
        Screen.QueueConditionEvent(None, Target, "Paralysis", 0, Delay)
        Screen.QueueConditionEvent(None, Target, "Stone", 0, Delay)
        Screen.QueueConditionEvent(None, Target, "Sleep", 0, Delay)
        
    
class AttachedMagicSprite(GenericImageSprite):
    def __init__(self, CritterSprite, SpellName, Positions, PositionOffset = 0):
        self.SpellName = SpellName
        self.Positions = Positions
        self.PositionIndex = int(PositionOffset * len(Positions))
        self.ImageNumber = 0
        if PositionOffset>0:
            self.ImageNumber = 1
        if PositionOffset > 0.6:
            self.ImageNumber = 2
        self.CritterSprite = CritterSprite
        self.RadX = (self.CritterSprite.rect.width / 2) + 5
        self.RadY = (self.CritterSprite.rect.height / 2) + 5
        self.Images = []
        for Index in range(3):
            SubPath = os.path.join(Paths.ImagesMagic, "%s.%s.png"%(SpellName,Index))
            self.Images.append(Resources.GetImage(SubPath))
        self.Images.append(self.Images[1]) # xyzyxyzy
        GenericImageSprite.__init__(self, self.Images[0], 0, 0)
        self.UpdateXY()
    def Update(self, Tick):
        if Tick%3==0:
            self.UpdateXY()
        if Tick%20 == 0:
            self.ImageNumber = (self.ImageNumber + 1) % 4
            OldCenter = self.rect.center
            self.image = self.Images[self.ImageNumber]
            self.rect = self.image.get_rect()
            self.rect.center = OldCenter
    def UpdateXY(self):
        (X, Y) = self.CritterSprite.rect.center
        #self.Angle += self.AngleSpeed
        self.PositionIndex = (self.PositionIndex+1)%len(self.Positions)
        Sin, Cos = self.Positions[self.PositionIndex]
        self.X = X - self.RadX * Sin
        self.Y = Y - self.RadY * Cos
        self.rect.left = self.X
        self.rect.top = self.Y

def GetAnglePositions(List, Speed):
    Angle = 0
    while Angle < math.pi * 2:
        List.append((math.cos(Angle), math.sin(Angle)))
        Angle += Speed

def GetRaisePositions(StartAngle):
    Angle = StartAngle
    Radius = 150
    List = []
    for Index in range(125):
        Radius -= 1.2
        List.append((Radius*math.cos(Angle), Radius*math.sin(Angle)))
        Angle += 0.2
    return List

AnglePosBloodlust = []
AnglePosStoneskin = []
RaisePositions = []
GetAnglePositions(AnglePosBloodlust, 0.157)
GetAnglePositions(AnglePosStoneskin, 0.157 * 0.5)
AnglePosStoneskin.reverse()
for Index in range(3):
    RaisePositions.append(GetRaisePositions(Index * 2 * math.pi / 3.0))

def AttachSpellSprites(CritterSprite, SpellName):
    if SpellName == "Bloodlust":
        Sprites = []
        Sprite = AttachedMagicSprite(CritterSprite, "Bloodlust", AnglePosBloodlust)
        Sprites.append(Sprite)
        Sprite = AttachedMagicSprite(CritterSprite, "Bloodlust", AnglePosBloodlust, 0.33)
        Sprites.append(Sprite)
        Sprite = AttachedMagicSprite(CritterSprite, "Bloodlust", AnglePosBloodlust, 0.66)
        Sprites.append(Sprite)
        return Sprites
    if SpellName == "Stoneskin":
        Sprites = []
        Sprite = AttachedMagicSprite(CritterSprite, "Stoneskin", AnglePosStoneskin, 0)
        Sprites.append(Sprite)
        Sprite = AttachedMagicSprite(CritterSprite, "Stoneskin", AnglePosStoneskin, 0.5)
        Sprites.append(Sprite)
        return Sprites

class CureMasterSpriteClass(GenericImageSprite):
    "An Invisible Hand sprite - it spawns child sprites, but has no actual image."
    BasePositions = [(60, 0), (54, -19), (43, -36), (27, -47), (9, -52), (-8, -50),
                     (-24, -43), (-36, -30), (-43, -15), (-44, 0), (-40, 14), (-31, 26),
                     (-19, 34), (-6, 37), (6, 35), (17, 29), (24, 20), (28, 10), (29, 0),
                     (25, -9), (19, -16), (11, -20), (3, -21), (-3, -20), (-9, -16), (-13, -11),
                     (-14, -5), (-13, 0), (-11, 4), (-7, 6), (-4, 7), (-1, 6), (0, 5), (1, 2), (1, 1)]
    ReversePositions = [(-60, 0), (-54, -19), (-43, -36), (-27, -47), (-9, -52), (8, -50), (24, -43),
                        (36, -30), (43, -15), (44, 0), (40, 14), (31, 26), (19, 34), (6, 37), (-6, 35),
                        (-17, 29), (-24, 20), (-28, 10), (-29, 0), (-25, -9), (-19, -16), (-11, -20),
                        (-3, -21), (3, -20), (9, -16), (13, -11), (14, -5), (13, 0), (11, 4), (7, 6),
                        (4, 7), (1, 6), (0, 5), (-1, 2), (-1, 1)]
    TicksPerTwinkle = 3
    def __init__(self, Screen, X, Y, SpriteName = "Twinkle", ImageCount = 4, ReverseFlag = 0):
        self.X = X
        self.Y = Y
        self.ImageCount = ImageCount
        self.SpriteName = SpriteName
        self.Screen = Screen
        if ReverseFlag:
            self.Positions = self.ReversePositions
        else:
            self.Positions = self.BasePositions
        GenericImageSprite.__init__(self, Global.NullImage, X, Y)
        self.Tick = 0
        self.TwinkleIndex = 0
    def Update(self, Dummy):
        if self.Tick % self.TicksPerTwinkle == 0:
            Twinkle = MagicSprite(self.X + self.Positions[self.TwinkleIndex][0],
                                  self.Y + self.Positions[self.TwinkleIndex][1], self.SpriteName, self.ImageCount, 8)
            self.Screen.AddForegroundSprite(Twinkle)
            #self.Screen.AddAnimationSprite(Twinkle) #%%%
            self.TwinkleIndex += 1
            if self.TwinkleIndex >= len(self.Positions):
                self.kill()
        self.Tick += 1

Cure3Positions = []
for Index in range(3):
    Cure3Positions.append([])
    Angle = 2 * math.pi * Index / 3.0
    Radius = 80
    for Tick in range(80):
        Angle += 0.15
        X = math.cos(Angle)*Radius
        Y = math.sin(Angle)*Radius
        Cure3Positions[-1].append((X,Y))
        Radius -= 1
        
HolyPositions = []
for Index in range(7):
    HolyPositions.append([])
    if Index<3:
        Radius = 30
        Dir = 0.08
        Angle = 2 * math.pi * (Index/3.0)
    else:
        Radius = 50
        Dir = -0.03
        Angle = 2 * math.pi * (Index-3)/4.0
    for Tick in range(150):
        Angle += Dir
        if (Tick%40 < 20):
            Radius += 1
        else:
            Radius -= 1
        X = math.cos(Angle)*Radius
        Y = math.sin(Angle)*Radius
        HolyPositions[-1].append((X,Y))
    
class Cure3Sprite(MagicSprite):
    def __init__(self, X, Y, Name, ImageCount, Positions):
        MagicSprite.__init__(self, X, Y, Name, ImageCount)
        (self.X, self.Y) = self.rect.center
        self.Positions = Positions
        self.LoopFlag = 1
    def Update(self, Dummy):
        MagicSprite.Update(self, Dummy)
        if self.Tick >= len(self.Positions):
            self.kill()
            return
        X = self.X + self.Positions[self.Tick][0]
        Y = self.Y + self.Positions[self.Tick][1]
        self.rect.center = (X, Y)

class RaiseAngelSprite(MagicSprite):
    def __init__(self, X, Y, SoundName = "Allelujah.wav"):
        MagicSprite.__init__(self, X, Y, "RaiseAngel", 2)
        self.image = Global.NullImage
        self.MaxImageDelay = 10
        self.Visible = 0
        self.MaxAge = 150
        self.SoundName = SoundName
    def Update(self, Dummy):
        self.Tick += 1
        if self.Visible:
            MagicSprite.Update(self, Dummy)
        else:
            if self.Tick >= 100:
                self.Visible = 1
                self.Tick = 0
                Resources.PlayStandardSound(self.SoundName)

def SpellAnimateCure3(Screen, CasterSprite, TargetSprite):
    Resources.PlayStandardSound("Heal.wav") #%%%
    (X, Y) = TargetSprite.rect.center
    Sprite = Cure3Sprite(X, Y, "Twinkle", 4, Cure3Positions[0])
    Screen.AddAnimationSprite(Sprite)
    Sprite = Cure3Sprite(X, Y, "BlueTwinkle", 4, Cure3Positions[1])
    Screen.AddAnimationSprite(Sprite)
    Sprite = Cure3Sprite(X, Y, "GreenTwinkle", 4, Cure3Positions[2])
    Screen.AddAnimationSprite(Sprite)

def SpellAnimateHoly(Screen, CasterSprite, TargetSprite):
    Resources.PlayStandardSound("Syreen.wav") #%%%
    (X,Y) = TargetSprite.rect.center
    for Index in range(7):
        Sprite = Cure3Sprite(X, Y, "Holy", 3, HolyPositions[Index])
        Sprite.ImageDelay = Index
        Screen.AddAnimationSprite(Sprite)

class SiphonSprite(MagicSprite):
    PauseLength = 120
    def __init__(self, X, Y, X2, Y2):
        MagicSprite.__init__(self,0, 0, "Siphon", 3)
        self.Paused = 1
        self.StartX = X
        self.StartY = Y
        self.EndX = X2
        self.EndY = Y2
        self.TickTotal = 50
        self.MaxAge = 9999
    def Update(self, Dummy):
        if self.Paused:
            self.Tick += 1
            if self.Tick > self.PauseLength:
                self.Paused = 0
                self.X = self.StartX
                self.Y = self.StartY
                self.Tick = 0
            return
        MagicSprite.Update(self, Dummy)
        if self.Tick > self.TickTotal:
            self.kill()
            return
        self.rect.left = int(self.StartX + (self.EndX - self.StartX) * self.Tick / float(self.TickTotal))
        self.rect.top = int(self.StartY + (self.EndY - self.StartY) * self.Tick / float(self.TickTotal))
        
def SpellAnimateSiphon(Screen, CasterSprite, TargetSprite):
    if not TargetSprite.Critter.MP:
        # Re-select a target:
        if CasterSprite.Critter.IsPlayer():
            for Monster in Screen.MonsterSprites:
                if Monster.Critter.MP:
                    TargetSprite = Monster
                    break
        else:
            for Player in Global.Party.Players:
                if Player.MP:
                    TargetSprite = Player
    Damage = GetDamageForCaster(10, CasterSprite.Critter)
    Suction = min(50, TargetSprite.Critter.MP, Damage)
    Screen.QueueGainMPEvent(TargetSprite, -Suction, 120)
    Screen.QueueGainMPEvent(CasterSprite, Suction, 175)
    (X, Y) = (TargetSprite.CenterX, TargetSprite.CenterY)
    Sprite = Cure3Sprite(X, Y, "Siphon", 3, RaisePositions[0])
    Screen.AddAnimationSprite(Sprite)
    Sprite = Cure3Sprite(X, Y, "Siphon", 3, RaisePositions[1])
    Screen.AddAnimationSprite(Sprite)
    Sprite = Cure3Sprite(X, Y, "Siphon", 3, RaisePositions[2])
    Screen.AddAnimationSprite(Sprite)
    Sprite = SiphonSprite(TargetSprite.rect.center[0], TargetSprite.rect.center[1],
                          CasterSprite.rect.center[0], CasterSprite.rect.center[1])
    Screen.AddAnimationSprite(Sprite)
    
def SpellAnimateRaise(Screen, CasterSprite, TargetSprite):
    (X, Y) = TargetSprite.rect.center
    Sprite = Cure3Sprite(X, Y, "Heart", 2, RaisePositions[0])
    Screen.AddAnimationSprite(Sprite)
    Sprite = Cure3Sprite(X, Y, "Heart", 2, RaisePositions[1])
    Screen.AddAnimationSprite(Sprite)
    Sprite = Cure3Sprite(X, Y, "Heart", 2, RaisePositions[2])
    Screen.AddAnimationSprite(Sprite)
    Sprite = RaiseAngelSprite(X, Y - 40)
    Screen.AddAnimationSprite(Sprite)
    Resources.PlayStandardSound("Spell.wav")
    
    
   
def SpellAnimateAntidote(Screen, CasterSprite, TargetSprite):
    (X, Y) = TargetSprite.rect.center
    Resources.PlayStandardSound("Antidote.wav")
    for Index in range(25):
        Sprite = MagicSprite(X + random.randrange(-30, 30), Y + random.randrange(-30, 30), "BlueTwinkle", 4)
        Screen.AddAnimationSprite(Sprite)
        Delay = random.randrange(100)
        Sprite.ImageDelay += Delay
        Sprite.MaxAge += Delay

class RegenLineSprite(GenericImageSprite):
    def __init__(self, X, BaseY, Delay, Color):
        self.image = pygame.Surface((4, BaseY))
        self.image.set_colorkey(Colors.Black)
        self.Color = Color
        self.Delay = Delay
        self.Age = 0
        self.CurrentY = 0
        self.BaseY = BaseY
        self.State = 0
        self.image.fill(Colors.Black)
        GenericImageSprite.__init__(self, self.image, X, 0)
    def Update(self, Tick):
        self.Age += 1
        if self.State == 0:
            if self.Age > self.Delay:
                self.State = 1
                self.CurrentY = self.BaseY
        elif self.State == 1:
            pygame.draw.rect(self.image, self.Color, (0, 0, 5, self.CurrentY), 0)
            self.CurrentY -= 20
            if self.CurrentY < 0:
                self.State = 2
                self.Age = 0
        elif self.State == 2:
            if self.Age > 50:
                self.State = 3
                self.CurrentY = self.BaseY
        else:
            pygame.draw.rect(self.image, Colors.Black, (0, self.CurrentY, 5, self.BaseY), 0)
            self.CurrentY -= 20
            if self.CurrentY < 0:
                self.kill()
            
def SpellAnimateRegen(Screen, CasterSprite, TargetSprite):
    "A series of lines streak up toward the heavens, elevating the spirits of onlookers.  Go, warriors!  Fight!  For everlasting peace!"
    Resources.PlayStandardSound("Twinkle.wav")
    X = TargetSprite.rect.center[0]
    Y = TargetSprite.rect.bottom
    for Index in range(10):
        ColorBit = random.randrange(150, 255)
        Color = (ColorBit,ColorBit,ColorBit)
        Sprite = RegenLineSprite(X + random.randrange(-25, 25), Y, Index*7, Color)
        Screen.AddAnimationSprite(Sprite)
        
def SpellAnimateCure(Screen, CasterSprite, TargetSprite):
    CureMasterSprite = CureMasterSpriteClass(Screen, TargetSprite.CenterX, TargetSprite.CenterY)
    Screen.AddForegroundSprite(CureMasterSprite)
    Resources.PlayStandardSound("Heal.wav")

def SpellAnimateCureAll(Screen, CasterSprite, Target): # Target=none
    if CasterSprite.Critter.IsPlayer():
        for Sprite in Screen.PlayerSprites:
            CureMasterSprite = CureMasterSpriteClass(Screen, Sprite.CenterX, Sprite.CenterY)
            Screen.AddForegroundSprite(CureMasterSprite)
    else:
        for Sprite in Screen.MonsterSprites:
            if Sprite.Critter.IsAlive():
                CureMasterSprite = CureMasterSpriteClass(Screen, Sprite.CenterX, Sprite.CenterY)
                Screen.AddForegroundSprite(CureMasterSprite)                
    Resources.PlayStandardSound("Heal.wav")

def SpellAnimateCure2All(Screen, CasterSprite, Target): # Target=none
    if CasterSprite.Critter.IsPlayer():
        for Sprite in Screen.PlayerSprites:
            CureMasterSprite = CureMasterSpriteClass(Screen, Sprite.CenterX, Sprite.CenterY, "GreenTwinkle")
            Screen.AddForegroundSprite(CureMasterSprite)
    else:
        for Sprite in Screen.MonsterSprites:
            if Sprite.Critter.IsAlive():
                CureMasterSprite = CureMasterSpriteClass(Screen, Sprite.CenterX, Sprite.CenterY, "GreenTwinkle")
                Screen.AddForegroundSprite(CureMasterSprite)                
    Resources.PlayStandardSound("Cure.wav")


def SpellAnimateCure2(Screen, CasterSprite, TargetSprite):
    CureMasterSprite = CureMasterSpriteClass(Screen, TargetSprite.CenterX, TargetSprite.CenterY)
    Screen.AddForegroundSprite(CureMasterSprite)
    CureMasterSprite = CureMasterSpriteClass(Screen, TargetSprite.CenterX, TargetSprite.CenterY, ReverseFlag = 1)
    Screen.AddForegroundSprite(CureMasterSprite)
    Resources.PlayStandardSound("Cure.wav")


def SpellAnimateBloodlust(Screen, CasterSprite, TargetSprite):
    CureMasterSprite = CureMasterSpriteClass(Screen, TargetSprite.CenterX, TargetSprite.CenterY, "Bloodlust", 3)
    Screen.AddForegroundSprite(CureMasterSprite)
    Resources.PlayStandardSound("Bloodlust.wav")

def SpellAnimateStoneskin(Screen, CasterSprite, TargetSprite):
    CureMasterSprite = CureMasterSpriteClass(Screen, TargetSprite.CenterX, TargetSprite.CenterY, "Stoneskin", 3)
    Screen.AddForegroundSprite(CureMasterSprite)
    Resources.PlayStandardSound("Bloodlust.wav")



def SpellSummonMonster(Screen,Caster,Target,Damage,Spell,ImageCount,Positions,ImageDelay):
    if not isinstance(Caster, Critter.Player):
        Caster = Caster.Critter
    # If this is a summon on the battle screen, then we've already charged the caster MP
    # in the HandleSpellEvent method.  But if it's the maze screen, we must charge them:
    if not isinstance(Screen, DancingScreen.DancingScreen):
        Caster.MP = max(Caster.MP - Spell.Mana, 0)
    BaseDamage = GetDamageForCaster(Damage, Caster)
    # A little boost to "Angel", since it's the only non-cleric healing spell:
    if Spell.Name == "Angel":
        BaseDamage *= 1.0 + (0.1 * (Caster.Level - 1))
    SummonSprite = SummonSpriteClass(Screen, Spell, Positions, ImageCount, ImageDelay)
    SummonSprite.Damage = BaseDamage
    Screen.StartSummon(SummonSprite)
    # Break the invulnerability on the StoneHead:
    if hasattr(Screen, "Monsters"):
        for Monster in Screen.Monsters:
            if Monster.Species.Name == "StoneHead":
                Monster.Broken = 1 # Pow!!

def SpellAnimateLightning(Screen, CasterSprite, TargetSprite):
    Resources.PlayStandardSound("Lightning.wav")
    if CasterSprite.Critter.IsPlayer():
        # Find all the sprites on this column
        Targets = [(0, TargetSprite.rect.center[0], None)]
        for Sprite in Screen.MonsterSprites:
            if Sprite.Rank == TargetSprite.Rank and Sprite.Critter.IsAlive():
                Targets.append((Sprite.rect.center[1], random.randrange(Sprite.rect.left, Sprite.rect.right), Sprite))
        Targets.sort()
        Targets.append((450, TargetSprite.rect.center[0], None))
        
    else:
        Targets = [(CasterSprite.rect.center[0], CasterSprite.rect.right, None)]
        for Index in (0, 2, 3, 1):
            PlayerSprite = Screen.PlayerSprites[Index]
            if PlayerSprite.Critter.IsAlive():
                Targets.append((PlayerSprite.rect.center[1], PlayerSprite.rect.center[0], PlayerSprite))
    ControlSprite = LightningMasterSprite(Screen, CasterSprite, Targets, 30)

def SpellAnimateLightning2(Screen, CasterSprite, TargetSprite):
    Resources.PlayStandardSound("Lightning.wav")
    if CasterSprite.Critter.IsPlayer():
        # Find all the sprites on this column
        Targets = [(0, TargetSprite.rect.left, None)]
        TargetsB = [(0, TargetSprite.rect.right, None)]
        for Sprite in Screen.MonsterSprites:
            if Sprite.Rank == TargetSprite.Rank and Sprite.Critter.IsAlive():
                if len(Targets)%2:
                    Targets.append((Sprite.rect.center[1], Sprite.rect.right, Sprite))
                    TargetsB.append((Sprite.rect.center[1], Sprite.rect.left, None))
                else:
                    Targets.append((Sprite.rect.center[1], Sprite.rect.left, Sprite))
                    TargetsB.append((Sprite.rect.center[1], Sprite.rect.right, None))
        Targets.sort()
        TargetsB.sort()
        if len(Targets)%2:
            TargetsB.append((450, TargetSprite.rect.left - 25, None))
            Targets.append((450, TargetSprite.rect.right + 25, None))
        else:
            Targets.append((450, TargetSprite.rect.left - 25, None))
            TargetsB.append((450, TargetSprite.rect.right + 25, None))
        ControlSprite = LightningMasterSprite(Screen, CasterSprite, Targets, 750)
        ControlSpriteB = LightningMasterSprite(Screen, CasterSprite, TargetsB, 750)
    else:
        Targets = [(CasterSprite.rect.center[0], CasterSprite.rect.right)]
        for PlayerSprite in Screen.PlayerSprites:
            if PlayerSprite.Critter.IsAlive():
                Targets.append((PlayerSprite.rect.center[1], PlayerSprite.rect.center[0], PlayerSprite))
        ControlSprite = LightningMasterSprite(Screen, CasterSprite, Targets, 100)

class LightningSegmentSprite(GenericImageSprite):
    MaxAge = 55
    def __init__(self, PointA, PointB):
        (YA, XA) = PointA[:2]
        (YB, XB) = PointB[:2]
        Left = min(XA, XB)
        Top = min(YA, YB)
        Width = max(XA, XB) - Left + 10
        Height = max(YA, YB) - Top
        self.image = pygame.Surface((Width, Height))
        # Decide whether to go \ or /:
        if (XA < XB and YA < YB) or \
            (XB < XA and YA < YA):
            Start = (5, 0)
            End = (Width-5, Height)
            LeftStart = (0, 0)
            LeftEnd = (Width-10, Height)
            RightStart = (10, 0)
            RightEnd = (Width, Height)
        else:
            Start = (Width-5, 0)
            End = (5, Height)
            LeftStart = (Width-10, 0)
            LeftEnd = (0, Height)
            RightStart = (Width, 0)
            RightEnd = (10, Height)
        pygame.draw.line(self.image, Colors.White, (Start), (End), 3)
        pygame.draw.line(self.image, Colors.LightGrey, (LeftStart), (LeftEnd))
        pygame.draw.line(self.image, Colors.LightGrey, (RightStart), (RightEnd))
        GenericImageSprite.__init__(self, self.image, Left, Top)
        self.Age = 0
    def Update(self, Dummy):
        self.Age += 1
        if self.Age >= self.MaxAge:
            self.kill()
            
class LightningMasterSprite(GenericImageSprite):
    MaxTimer = 3
    def __init__(self, Screen, Caster, Targets, Damage):
        GenericImageSprite.__init__(self, Global.NullImage, 0, 0)
        self.Targets = Targets
        self.Screen = Screen
        self.Timer = 1
        self.CurrentIndex = 0
        self.Caster = Caster
        self.Damage = Damage
        self.Screen.AddForegroundSprite(self)
    def Update(self, Dummy):
        self.Timer -= 1
        print "LightningMaster: Index %d"%self.CurrentIndex
        print self.Targets[self.CurrentIndex]
        if self.Timer <= 0:
            self.Timer = self.MaxTimer
            CritterSprite = self.Targets[self.CurrentIndex][2]
            if CritterSprite:
                SpellDoDamage(self.Screen, self.Caster,
                              CritterSprite, self.Damage, 0, "Lightning")
            Sprite = LightningSegmentSprite(self.Targets[self.CurrentIndex], self.Targets[self.CurrentIndex + 1])
            self.Screen.AddAnimationSprite(Sprite)
            self.CurrentIndex += 1
            if self.CurrentIndex >= len(self.Targets)-1:
                self.kill()
    
def SpellAnimateBio(Screen, CasterSprite, TargetSprite):
    Y = TargetSprite.rect.top - 10
    Index = 0
    DeltaX = (10,30)
    while (1):
        X = TargetSprite.rect.center[0] + DeltaX[Index%2]
        Sprite = MagicSprite(X, Y, "Bio", 2, 4)
        Sprite.rect.left -= Sprite.rect.width / 2
        Sprite.MaxAge = 40
        Screen.AddAnimationSprite(Sprite)
        Index += 1
        Y += Sprite.rect.height
        if Y > TargetSprite.rect.bottom:
            break
    Resources.PlayStandardSound("Bio.wav")

def SpellDoBio(Screen, CasterSprite, TargetSprite, Damage):
    Delay = 40
    if TargetSprite.Critter.HasPerk("Poison Immune"):
        Damage /= 2
    else:
        Screen.QueueConditionEvent(CasterSprite, TargetSprite, "Poison", 50 + (CasterSprite.Critter.INT * 20), Delay)
    SpellDoDamage(Screen, CasterSprite, TargetSprite, Damage, Delay)

def SpellDoHurtmore(Screen, CasterSprite, TargetSprite, Damage):
    Delay = 80
    if random.random() > 0.5:
        if not TargetSprite.Critter.HasPerk("Poison Immune"):
            Screen.QueueConditionEvent(CasterSprite, TargetSprite, "Poison", 50 + (CasterSprite.Critter.INT * 20), Delay)
    if random.random() > 0.5:
        if not TargetSprite.Critter.HasPerk("Sleep Immune"):
            Screen.QueueConditionEvent(CasterSprite, TargetSprite, "Sleep", 50 + (CasterSprite.Critter.INT * 20), Delay)
    if random.random() > 0.3:
        if not TargetSprite.Critter.HasPerk("Silence Immune"):
            Screen.QueueConditionEvent(CasterSprite, TargetSprite, "Silence", 50 + (CasterSprite.Critter.INT * 10), Delay)
    if random.random() > 0.2:
        if not TargetSprite.Critter.HasPerk("Paralysis Immune"):
            Screen.QueueConditionEvent(CasterSprite, TargetSprite, "Paralysis", 50 + (CasterSprite.Critter.INT * 10), Delay)
    SpellDoDamage(Screen, CasterSprite, TargetSprite, Damage, Delay)

def DefineMageSpells():
    Spell = SpellClass("Fire", 3, 1, 1, 0, SpellTarget.OneMonster, 500, 
                       None,
                       lambda Screen,Caster,Target, Damage=20, Delay=75: SpellDoDamage(Screen,Caster,Target,Damage,Delay, "Fire"),
                       SpellAnimateFire)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Dumapic", 1, 2, 0, 1, SpellTarget.AllMonsters, 1200, 
                       MazeSpellDumapic,None,None)
    Global.Spellbook.MageSpells.append(Spell)
                       
    Spell = SpellClass("Lightning", 8, 3, 1, 0, SpellTarget.MonsterRow, 800,  #%%%
                       None,
                       None, #lambda Screen,Caster,Target, Damage=20, Delay=20: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateLightning)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Blizzard", 10, 4, 1, 0, SpellTarget.EachMonster, 1000,
    #Spell = SpellClass("Blizzard", 1, 1, 1, 0, SpellTarget.EachMonster, 5, 
                       None,
                       lambda Screen, Caster, Target, Damage = 40: SpellDoDamage(Screen,Caster,Target,Damage, 80, "Cold"),
                       ##None, #lambda Screen,Caster,Target, Damage=20, Delay=20: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateBlizzard)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Bio", 12, 4, 1, 0, SpellTarget.OneMonster, 1000, 
                       None,
                       lambda Screen, Caster, Target, Damage = 500: SpellDoBio(Screen, Caster, Target, Damage),
                       ##None, #lambda Screen,Caster,Target, Damage=20, Delay=20: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateBio)
    Global.Spellbook.MageSpells.append(Spell)
    
    Spell = SpellClass("Compass", 20, 5, 0, 1, SpellTarget.NoTarget, 0, #%%% L5
                       MazeSpellCompass,
                       None,
                       None)    
    Global.Spellbook.MageSpells.append(Spell)
    
    Spell = SpellClass("Lightning 2", 20, 8, 1, 0, SpellTarget.MonsterRow, 1300, 
                       None,
                       None, #lambda Screen,Caster,Target, Damage=20, Delay=20: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateLightning2)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Blade Storm", 35, 10, 1, 0, SpellTarget.EachMonster, 1500,
    #Spell = SpellClass("Blade Storm", 1, 1, 1, 0, SpellTarget.EachMonster, 5,  
                       None,
                       lambda Screen, Caster, Target, Damage = 1000: SpellDoDamage(Screen,Caster,Target,Damage, 250),
                       ##None, #lambda Screen,Caster,Target, Damage=20, Delay=20: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateBladeStorm)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Stairmaster", 40, 10, 0, 1, SpellTarget.NoTarget, 0,
    #Spell = SpellClass("Stairmaster", 1, 1, 0, 1, SpellTarget.NoTarget, 0,
                       MazeSpellStairmaster,
                       None,
                       None)    
    Global.Spellbook.MageSpells.append(Spell)


    Spell = SpellClass("The Claw", 30, 10, 1, 0, SpellTarget.OneMonster, 1500,
    #Spell = SpellClass("The Claw", 1, 1, 1, 0, SpellTarget.OneMonster, 5, 
                       None,
                       lambda Screen, Caster, Target, Damage = 3000: SpellDoHurtmore(Screen, Caster, Target, Damage),
                       ##None, #lambda Screen,Caster,Target, Damage=20, Delay=20: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateHurtmore)
    Global.Spellbook.MageSpells.append(Spell)
    
    ######
    Spell = SpellClass("Bloodlust", 10, 10, 1, 0, SpellTarget.OnePlayer, 500,
    #Spell = SpellClass("Bloodlust", 1, 1, 1, 0, SpellTarget.OnePlayer, 1, #500, #%%%
                       None,
                       lambda Screen,Caster,Target: SpellBloodlust(Screen,Caster,Target,99),
                       SpellAnimateBloodlust)
    #Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell: MazeSpellAntidote(Screen, Caster, S, Target)
    Global.Spellbook.MageSpells.append(Spell)

    ## For reference, the spell constructor:
    ##    def __init__(self, Name, Mana, Level, CombatUse, MazeUse, Target,
    ##                 CastingTime, MazeEffectCode, BattleEffectCode, AnimationCode):

    #Spell = SpellClass("Blizzard 2", 1, 1, 1, 0, SpellTarget.EachMonster, 5, 
    Spell = SpellClass("Blizzard 2", 50, 11, 1, 0, SpellTarget.EachMonster, 1500, 
                       None,
                       lambda Screen, Caster, Target, Damage = 2000: SpellDoDamage(Screen,Caster,Target,Damage, 80, "Cold"),
                       SpellAnimateBlizzard2)
    Global.Spellbook.MageSpells.append(Spell)

    #Spell = SpellClass("Flare", 1, 1, 1, 0, SpellTarget.OneMonster, 5, 
    Spell = SpellClass("Flare", 50, 12, 1, 0, SpellTarget.OneMonster, 1500, 
                       None,
                       lambda Screen,Caster,Target, Damage=8000, Delay=150: SpellDoDamage(Screen,Caster,Target,Damage,Delay, "Fire"),
                       SpellAnimateFlare)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Meteo", 75, 15, 1, 0, SpellTarget.EachMonster, 1500, 
    #Spell = SpellClass("Meteo", 1, 1, 1, 0, SpellTarget.EachMonster, 5, 
                       None,
                       lambda Screen,Caster,Target, Damage=7000, Delay=150: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateMeteo)
    Global.Spellbook.MageSpells.append(Spell)

    Spell = SpellClass("Soulsmash", 100, 18, 1, 0, SpellTarget.OneMonster, 1500, 
    #Spell = SpellClass("Soulsmash", 1, 1, 1, 0, SpellTarget.OneMonster, 5, 
                       None,
                       lambda Screen,Caster,Target, Damage=25000, Delay=150: SpellDoDamage(Screen,Caster,Target,Damage,Delay),
                       SpellAnimateSoulSmash)
    Global.Spellbook.MageSpells.append(Spell)


def DefineClericSpells():
    # Delay for cure is 30 twinkles * 3 ticks per twinkle
    ######
    Spell = SpellClass("Cure", 5, 1, 1, 1, SpellTarget.OnePlayer, 300,
                       None,
                       lambda Screen,Caster,Target, Damage=25, Delay=99: SpellCureDamage(Screen,Caster,Target,Damage,Delay),                       
                       SpellAnimateCure)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell, Damage=25: MazeSpellCureDamage(Screen, Caster, S, Target, Damage)
    Global.Spellbook.ClericSpells.append(Spell)
    ######
    Spell = SpellClass("Antidote", 3, 1, 1, 1, SpellTarget.OnePlayer, 350,
                       None,
                       lambda Screen,Caster,Target: SpellAntidote(Screen,Caster,Target,99),
                       SpellAnimateAntidote)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell: MazeSpellAntidote(Screen, Caster, S, Target)
    Global.Spellbook.ClericSpells.append(Spell)
    ##########
    Spell = SpellClass("Calfo", 3, 2, 0, 0, SpellTarget.NoTarget, 0, # Note: cost is hard-coded in Party.py!
                       None, #SpellCalfo
                       None,
                       None)    
    Global.Spellbook.ClericSpells.append(Spell)
    ######
    #Spell = SpellClass("Regen", 1, 1, 1, 0, SpellTarget.OnePlayer, 5,
    Spell = SpellClass("Regen", 10, 3, 1, 1, SpellTarget.OnePlayer, 500,
                       None,
                       lambda Screen,Caster,Target: SpellRegen(Screen,Caster,Target,99),
                       SpellAnimateRegen)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell: MazeSpellRegen(Screen, Caster, S, Target)
    Global.Spellbook.ClericSpells.append(Spell)
    ######
    #Spell = SpellClass("Cure 2", 1, 1, 1, 1, SpellTarget.OnePlayer, 3,
    Spell = SpellClass("Cure 2", 15, 4, 1, 1, SpellTarget.OnePlayer, 300,
                       None,
                       lambda Screen,Caster,Target, Damage=100, Delay=99: SpellCureDamage(Screen,Caster,Target,Damage,Delay),                       
                       SpellAnimateCure2)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell, Damage=100: MazeSpellCureDamage(Screen, Caster, S, Target, Damage, "Cure")
    Global.Spellbook.ClericSpells.append(Spell)
    ######
    Spell = SpellClass("Stoneskin", 5, 5, 1, 0, SpellTarget.OnePlayer, 500,
    #Spell = SpellClass("Stoneskin", 1, 1, 1, 0, SpellTarget.OnePlayer, 5,
                       None,
                       lambda Screen,Caster,Target: SpellStoneskin(Screen,Caster,Target,99),
                       SpellAnimateStoneskin)
    Global.Spellbook.ClericSpells.append(Spell)
    
    ##########
    Spell = SpellClass("Repel", 20, 5, 0, 1, SpellTarget.NoTarget, 0,  
                       MazeSpellRepel, #SpellCalfo
                       None,
                       None)    
    Global.Spellbook.ClericSpells.append(Spell)

    ##########
    Spell = SpellClass("Esuna", 15, 5, 1, 1, SpellTarget.OnePlayer, 700,
                       None,
                       lambda Screen,Caster,Target: SpellEsuna(Screen, Caster, Target, 99),
                       SpellAnimateRegen)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell: MazeSpellEsuna(Screen, Caster, S, Target)
    Global.Spellbook.ClericSpells.append(Spell)
    ######
    #Spell = SpellClass("Cure All", 1, 1, 1, 1, SpellTarget.AllPlayers, 3,
    Spell = SpellClass("Cure All", 25, 6, 1, 1, SpellTarget.AllPlayers, 1000,
                       None,
                       lambda Screen, Caster, Target, Damage=50, Delay=99: SpellCureAll(Screen,Caster,Damage,Delay),                       
                       SpellAnimateCureAll)
    Spell.MazeEffectCode = lambda Screen, Caster, Spell, Damage=50: MazeSpellCureAll(Screen, Caster, Spell, Damage)
    Global.Spellbook.ClericSpells.append(Spell)
    
    ######
    #Spell = SpellClass("Raise", 1, 1, 1, 1, SpellTarget.OnePlayer, 5,
    Spell = SpellClass("Raise", 50, 8, 1, 1, SpellTarget.OnePlayer, 800,
                       None,
                       lambda Screen, Caster, Target, S = Spell: SpellRaise(Screen, Caster, Target, S),
                       SpellAnimateRaise)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell: MazeSpellRaise(Screen, Caster, S, Target)
    Global.Spellbook.ClericSpells.append(Spell)

    ######
    #Spell = SpellClass("Cure 3", 1, 1, 1, 1, SpellTarget.OnePlayer, 3,
    Spell = SpellClass("Cure 3", 50, 8, 1, 1, SpellTarget.OnePlayer, 500,
                       None,
                       lambda Screen,Caster,Target, Damage=500, Delay=99: SpellCureDamage(Screen,Caster,Target,Damage,Delay),                       
                       SpellAnimateCure3)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell, Damage=500: MazeSpellCureDamage(Screen, Caster, S, Target, Damage, "Heal") #%%%
    Global.Spellbook.ClericSpells.append(Spell)

    ######
    #Spell = SpellClass("Siphon", 0, 1, 1, 0, SpellTarget.OneMonster, 5,
    Spell = SpellClass("Siphon", 0, 8, 1, 0, SpellTarget.OneMonster, 500,
                       None,
                       lambda Screen, Caster, Target: 1,
                       SpellAnimateSiphon)
    Global.Spellbook.ClericSpells.append(Spell)

    ######
    #Spell = SpellClass("Cure2 All", 1, 1, 1, 1, SpellTarget.AllPlayers, 3,
    Spell = SpellClass("Cure2 All", 75, 10, 1, 1, SpellTarget.AllPlayers, 1200,
                       None,
                       lambda Screen, Caster, Target, Damage=150, Delay=99: SpellCureAll(Screen,Caster,Damage,Delay),
                       SpellAnimateCure2All)
    Spell.MazeEffectCode = lambda Screen, Caster, Spell, Damage=150: MazeSpellCureAll(Screen, Caster, Spell, Damage) #%%%
    Global.Spellbook.ClericSpells.append(Spell)

    ######
    #Spell = SpellClass("Holy", 1, 1, 1, 0, SpellTarget.OneMonster, 5,
    Spell = SpellClass("Holy", 144, 13, 1, 0, SpellTarget.OneMonster, 1200,
                       None,
                       lambda Screen, Caster, Target, Damage = 10000: SpellDoDamage(Screen,Caster,Target,Damage, 150),
                       SpellAnimateHoly)
    Global.Spellbook.ClericSpells.append(Spell)

    ######
    #Spell = SpellClass("Healmore", 1, 1, 1, 1, SpellTarget.OnePlayer, 3,
    Spell = SpellClass("Healmore", 150, 15, 1, 1, SpellTarget.OnePlayer, 1500,
                       None,
                       None,
                       SpellAnimateHealmore)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, S = Spell: SpellRaise(Screen, Caster, Target, S)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, S=Spell: MazeSpellRaise(Screen, Caster, S, Target)
    Global.Spellbook.ClericSpells.append(Spell)

def SummonYoshi(Screen, Caster, Target = None):
    Spell = GetSpell("Yoshi")
    # Random positions:
    List = []
    for Index in range(6):
        Tuple = (random.randrange(25, 775), random.randrange(25, 575))
        for SubIndex in range(80):
            List.append(Tuple)
    ##Freddy = lambda Screen, Caster, Target, Damage=100, S = YSpell, ImageCount=1, Positions=SummonPositions.ChocoboPositions:
    SpellSummonMonster(Screen, Caster, Target, 100, Spell , 1, List, 10)

def SummonThief(Screen, Caster, Target = None):
    "Summon the thief - he streaks around quickly from place to place!"
    Spell = GetSpell("Thief")
    OldPosition = (random.randrange(25, 775), random.randrange(25, 575))
    List = []
    for Index in range(6):
        while (1):
            Position = (random.randrange(25, 775), random.randrange(25, 575))
            dX = Position[0]-OldPosition[0]
            dY = Position[1]-OldPosition[1]
            if math.sqrt(dX**2 + dY**2) > 300:
                break
        for Instant in range(125):
            X = OldPosition[0] + (Position[0] - OldPosition[0]) * (Instant / 125.0)
            Y = OldPosition[1] + (Position[1] - OldPosition[1]) * (Instant / 125.0)
            List.append((X,Y))
        OldPosition = Position
    SpellSummonMonster(Screen, Caster, Target, 100, Spell, 3, List, 10)
    
def SummonChocobo(Screen, Caster, Target = None):
    Spell = GetSpell("Chocobo")
    # Random bouncing:
    YDir = 0
    XDir = random.randrange(10, 20) / 3.0
    X = random.randrange(200, 600)
    Y = 50
    List = []
    for Index in range(600):
        X += XDir
        Y += YDir
        YDir += 0.1
        if (Y >= 550):
            YDir = -abs(YDir)
        if (X <= 25):
            XDir = abs(XDir)
        if (X >= 775):
            XDir = -abs(XDir)
        List.append((int(round(X)),int(round(Y))))
    ##Freddy = lambda Screen, Caster, Target, Damage=100, S = YSpell, ImageCount=1, Positions=SummonPositions.ChocoboPositions:
    Damage = 150
    SpellSummonMonster(Screen, Caster, Target, Damage, Spell , 2, List, 10)

def DefineSummonerSpells():
    Spell = SpellClass("ZergRush", 12, 1, 1, 0, SpellTarget.AllMonsters, 1000,
                       None,
                       None,
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=50, S=Spell, ImageCount=16, Positions=SummonPositions.ZergPositions: SpellSummonMonster(Screen,Caster,Target,50,S,16,Positions, 5)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Angel", 15, 2, 1, 1, SpellTarget.AllPlayers, 1500, #500,
                       None,
                       None,
                       None)
    Spell.MazeEffectCode = lambda Screen, Caster, Target, Damage=20, S=Spell, ImageCount=3, Positions=SummonPositions.AngelPositions: SpellSummonMonster(Screen,Caster,Target,-20,S,3,Positions, 25)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=20, S=Spell, ImageCount=3, Positions=SummonPositions.AngelPositions: SpellSummonMonster(Screen,Caster,Target,-20,S,3,Positions, 25)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    TheSpell = SpellClass("Chocobo", 20, 3, 1, 0, SpellTarget.AllMonsters, 2200, #1500,
                       None,
                       None, 
                       None)
    #Pablo = lambda Screen, Caster, Target, Damage=100, S = TheSpell, ImageCount=2, Positions=SummonPositions.ChocoboPositions: SpellSummonMonster(Screen,Caster,Target,100,S,2,Positions, 10)
    TheSpell.BattleEffectCode = SummonChocobo
    Global.Spellbook.SummonerSpells.append(TheSpell)
    ###########################
    Spell = SpellClass("Bowser", 30, 4, 1, 0, SpellTarget.AllMonsters, 3000,
                       None,
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=500, S = Spell,ImageCount=2, Positions=SummonPositions.BowserPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 10)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Mr. Sandman", 40, 5, 1, 0, SpellTarget.AllMonsters, 4000,
                       None,
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=900, S = Spell,ImageCount=2, Positions=SummonPositions.SandmanPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 20)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    YSpell = SpellClass("Yoshi", 50, 6, 0, 1, SpellTarget.AllMonsters, 2500,
                       None,
                       None, 
                       None)
    YSpell.MazeEffectCode = SummonYoshi
    Global.Spellbook.SummonerSpells.append(YSpell)
    ###########################
    Spell = SpellClass("Ifrit", 50, 7, 1, 0, SpellTarget.AllMonsters, 4500,
                       None,
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=1800, S = Spell,ImageCount=1, Positions=SummonPositions.IfritPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 10)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Eye of Argon", 75, 8, 0, 1, SpellTarget.AllMonsters, 5000,
    #Spell = SpellClass("Eye of Argon", 1, 1, 0, 1, SpellTarget.AllMonsters, 5,
                       None,
                       None, 
                       None)
    # "Damage" means "duration" in this case:
    Spell.MazeEffectCode = lambda Screen, Caster, Target, Damage=200, S = Spell, ImageCount=4, Positions=SummonPositions.ArgonPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 10)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Shiva", 75, 9, 1, 0, SpellTarget.AllMonsters, 5000,
                       None, 
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=3000, S = Spell,ImageCount=2, Positions=SummonPositions.ShivaPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 20)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Metroid", 80, 10, 1, 0, SpellTarget.AllMonsters, 5500,
                       None,
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=5000, S = Spell,ImageCount=4, Positions=SummonPositions.AngelPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 10)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Thief", 100, 11, 0, 1, SpellTarget.AllMonsters, 1500,
                       None,
                       None, 
                       None)
    Spell.MazeEffectCode = SummonThief
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    #Spell = SpellClass("Phoenix", 1, 1, 1, 0, SpellTarget.AllMonsters, 5,
    Spell = SpellClass("Phoenix", 150, 12, 1, 0, SpellTarget.AllMonsters, 6000,
                       None,
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=7500, S = Spell,ImageCount=6, Positions=SummonPositions.ZergPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 10)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    #Spell = SpellClass("Bahamut", 1, 1, 1, 0, SpellTarget.AllMonsters, 5,
    Spell = SpellClass("Bahamut", 200, 13, 1, 0, SpellTarget.AllMonsters, 7500,
                       None,
                       None, 
                       None)
    Spell.BattleEffectCode = lambda Screen, Caster, Target, Damage=12000, S = Spell,ImageCount=4, Positions=SummonPositions.BowserPositions: SpellSummonMonster(Screen,Caster,Target,Damage,S,ImageCount,Positions, 10)
    Global.Spellbook.SummonerSpells.append(Spell)
    ###########################
    Spell = SpellClass("Dumapic", 1, 2, 0, 1, SpellTarget.AllMonsters, 1200, 
                       MazeSpellDumapic, None, None)
    Global.Spellbook.SummonerSpells.append(Spell)

def DefineSpells():
    Global.Spellbook = Spellbook()
    DefineMageSpells()
    DefineClericSpells()
    DefineSummonerSpells()

    
DefineSpells()    
    
    