"""
All living things that can be in a battle - monsters, and player characters too - are Critters.  A monster
has an associated Species, each player has an associated Class.

Game balance hinges on some of the values defined in this module.  Tweak wisely, o tweakers!
"""
from Utils import *
from Constants import *
import Resources
import random
import Global

class ClassNames:
    Fighter="Fighter"
    Mage="Mage"
    Cleric="Cleric"
    Bard="Bard"
    Summoner="Summoner"
    Ninja="Ninja"

PlayerClassNames = [ClassNames.Fighter, ClassNames.Mage, ClassNames.Cleric,
                    ClassNames.Bard, ClassNames.Summoner, ClassNames.Ninja]
ClassNameToClass = {}

#################################################################################
# The available stats, and what they control:  <-- not all implemented yet! * denotes incomplete or missing
# STR - Affects damage done in melee.
# DEX - You make an opposed dex check to hit a monster in combat.  *Chest disarm skill.
# CON - Affects HP gain, and rate of recovery from bad effects (poison, sleep, ...)
# INT - Mage spell power; magic resistance; MP gain for mages/summoners
# WIS - Cleric spell power; magic evasion; MP gain for clerics
# CHA - *Bard powers (song choice, song speed, MP recovery rate)
# HP - How much damage you can take before dying
# MP - How many spells you can cast

# More detailed description:
# STR - Each weapon (or monster-species) has a base melee damage.  Each point of STR above (below) 10
# adds (subtracts) 10% from the damage done.  Max STR = 300% of normal damage
# DEX - Evasion chance is (defender dex) / 2*(defender dex + 3 * attacker dex).  For evenly matched
# dex scores, the chance is 13%; if your dex is double theirs, the chance is 20%; if your dex is half
# theirs, the chance is 7%.
# The range that qualifies as a hit (or a good hit, or a perfect hit) is increased by 5% for each point
# that dex rises over 10, to a maximum of double.  Many weapons are "awkward", decreasing the range
# to a minimum of half-normal; a high dex counter-acts this tendency.
# INT - For each point your INT is above your opponent's, decrease magic damage 2% to minimum 50%.
# For each level-up of a magic-user class: MP gain is 10, with a bonus (if INT is high) of INT-12 and
# a bonus (if WIS is high) of WIS-12.
# WIS - Magic evasion works like physical evasion, but uses WIS in place of DEX
# CON - For each level-up, HP gain due to class receives a bonus (if CON is high) of CON-12
# Chance of shaking off a bad effect is (CON-10) * 4% per round.
# CHA - Bards can choose between 2-5 songs, depending on CHA (and a random factor).  They can slow and
# speed songs by 5% per point CHA rises above 15, max of 150% or 50%.  They use the average of STR and CHA
# for damage computation.
# Average stats at level 1 are 10.5 (3d6).  Recruited characters have limited stat-potential (you won't
# get all-18s no matter HOW long you wait)  With each level-up, you may (33%) get lucky and add a point
# to a randomly-chosen stat; you always get to choose one stat to increase, too.  Some equipment also
# affects various stats.  The maximum character level is 30.  The maximum value for each stat is 30.

# Rule of thumb:
# For a monster species on dungeon level n, average stat is 5 + 2n.  Level 0 monsters have average stat 5.
# Monster species may affect stats as well.

# Equipment raises at most (dungeon-level) points of stat.

########################
# Animation definitions:

class Animation:
    def __init__(self, Type, Cels):
        self.Type = Type
        self.Images = []
        self.ImageNumbers = range(Cels)
        self.XPositions = [0]*Cels
        self.YPositions = [0]*Cels
        self.FrameCels = range(Cels) # By default: move one spot through this array per tick
        self.RepeatFlag = 0
        self.CriticalFrameNumber = 0
        self.MissingImageFlag = 0
    def __str__(self):
        return "<Animation %s>"%self.Type
    def LoadImages(self, Name):
        if self.Images:
            return # already loaded!
        ImageDir = os.path.join(Paths.ImagesCritter, Name)
        MaxImageNumber = max(self.ImageNumbers)
        for ImageNumber in range(MaxImageNumber+1):
            FilePath = os.path.join(ImageDir, "%s.%d.png"%(self.Type, ImageNumber))
            try:
                self.Images.append(Resources.GetImage(FilePath, 1))
            except:
                #traceback.print_exc()
                # Hmm...try the stand images.
                FoundImage = 0
                if self.Type != AnimationType.Stand:
                    FilePath = os.path.join(ImageDir, "%s.%d.png"%(AnimationType.Stand, ImageNumber))
                    try:
                        self.Images.append(Resources.GetImage(FilePath, 1))
                        FoundImage = 1
                    except:
                        #traceback.print_exc()
                        #print "**WARNING: Missing image for '%s'-%s: %s"%(Name, self.Type, FilePath)
                        self.MissingImageFlag = 1                        
                        pass
                if not FoundImage:
                    print "**WARNING: Missing image for '%s': %s"%(Name, FilePath)
                    traceback.print_exc()
                    #traceback.print_stack()
                    self.MissingImageFlag = 1
                    self.Images.append(Resources.GetDefaultCritterImage())
                #self.Images.append(pygame.surface(0,0))
    def GetImage(self, Frame):
        try:
            return self.Images[self.ImageNumbers[self.FrameCels[Frame]]]
        except:
            print "Animation.GetImage() failed!"
            print Frame
            print self.FrameCels
            print self.ImageNumbers
            print self.Images
    def GetX(self, Frame):
        try:
            return self.XPositions[self.FrameCels[Frame]]
        except:
            print Frame, self.FrameCels, self.FrameCels[Frame], self.XPositions, self.Type
    def GetY(self, Frame):
        try:
            return self.YPositions[self.FrameCels[Frame]]
        except:
            print "*** ERROR getting Y!  Frame is %d, framecel is %d, and self.ypos is %s"%(Frame, self.FrameCels[Frame], str(self.YPositions))

class AmmoDump:
    def __init__(self):
        self.PicCounts = {"Bullet":2, "Fireball":4, "Arrow":1, "KiFire":2, "Berzerk":1,
                          "Axe":16, "OldBullet":1, "DemonFire":2,
                          "Shuriken":3,"Bubble":4, "Slime":4,
                          "Rock":1, "MagicBeam":2, "Flare":1,
                          "Heart":2, "Meteor":4, "ArrowB":1,
                          "Goo":1, "BrainGlob":2, "RetroSpear":1,
                          }
        self.Images = {}
        self.FlippedImages = {}
        #Global.AmmoDump = self
        self.LoadImages()
    def LoadImages(self):
        for (Name, Count) in self.PicCounts.items():
            self.Images[Name] = []
            for ImageIndex in range(Count):
                Image = Resources.GetImage(os.path.join(Paths.ImagesProjectile, "%s.%d.png"%(Name, ImageIndex)))
                Image.set_colorkey(Colors.Black)
                self.Images[Name].append(Image)
    def GetImage(self, Name, Number, FlipFlag = 0):
        if FlipFlag:
            if not self.FlippedImages.has_key(Name):
                self.FlippedImages[Name] = []
                for Image in self.Images[Name]:
                    FlippedImage = pygame.transform.flip(Image, 1, 0)
                    self.FlippedImages[Name].append(FlippedImage)
            return self.FlippedImages[Name][Number % self.PicCounts[Name]]
        else:
            return self.Images[Name][Number % self.PicCounts[Name]]
        
class Species:
    """
    A species is a type of critter, like 'Red Koopa' or 'Blue Oktorok'.  The stats for a species are
    provided as multipliers; these are applied to the "normal" stat for the species' level.  (This way,
    you can change the species' level without having to change many other numbers). 
    """
    def __init__(self, Level, Name):
        self.Level = Level
        self.Name = Name
        self.STRMultiplier = 1.0
        self.DEXMultiplier = 1.0
        self.CONMultiplier = 1.0
        self.WISMultiplier = 1.0
        self.INTMultiplier = 1.0
        self.CHAMultiplier = 1.0
        self.DamageMultiplier = 1.0
        self.DamageDieCount = 1
        self.DamageDie = 6
        self.HPMultiplier = 1.0
        self.MPMultiplier = 0.0
        self.HP = 25
        self.ACMultiplier = 1.0
        self.AttackSounds = []
        #self.MaxHP = self.HP
        self.MP = 10
        #self.MaxMP = self.MP
        self.EXPMultiplier = 1.0
        self.GoldMultiplier = 1.0
        self.Animations = {}
        self.Perks = {}
        self.SpellsKnown = {}
        self.Projectile = None # Tuple: (pic, start-frame, travel-time)
        self.RecenterX = None
        self.RecenterY = None
    def GetDamage(self):
        return RollDice(self.DamageDieCount, self.DamageDie)
    def LoadAnimationImages(self):
        for Animation in self.Animations.values():
            Animation.LoadImages(self.Name)
    def FreeAnimationImages(self):
        for Animation in self.Animations.values():
            del Animation.Images
            Animation.Images = []
    def ChooseSpell(self):
        Keys = self.SpellsKnown.keys()
        if not Keys:
            return None
        return random.choice(Keys)
    def Validate(self):
        # Integrity check:
        Bob = Critter(self)
        # Check that our images are present:
        for Type in AnimationType.AllTypes:
            Animation = Bob.GetAnimation(Type)
            if Animation:
                Animation.LoadImages(self.Name)
                if Animation.MissingImageFlag:
                    print "** Critter '%s' missing image for animation %s"%(self.Name, Type)
        for Perk in self.Perks.keys():
            if not (AllPerks.has_key(Perk)):
                print "** Critter '%s' has weird perk '%s'"%(self.Name, Perk)
        # %%% known spells, too
    
HPByLevel = [12,40,110]
for Level in range(3,14):
    HPByLevel.append(HPByLevel[-1] * 2.3)
MPByLevel = [10,10,20]
for Level in range(3,14):
    MPByLevel.append(MPByLevel[-1] * 2.0)
ACByLevel = [1,3,5]
for Level in range(3,14):
    ACByLevel.append(ACByLevel[-1] * 1.8)
DamageByLevel = [0,3,6,10,15,20,
                 26,32,38,44,50]
for Level in range(3,14):
    DamageByLevel.append(DamageByLevel[-1] * 1.85)

class Critter:
    def __init__(self, Species):
        self.Species = Species
        self.RollStats()
        self.Perks = {}
        self.SpellPerks = {}
        for Key in self.Species.Perks.keys():
            self.Perks[Key] = 1
        self.CurrentAction = ""
        # The player's current action (like "paralyzed" or "cast:magicmissile") is shown on the status line.
        # Monsters have current actions, too, when they cast spells!
        self.CurrentAction = ""
    def RemoveAttachedSpells(self):
        if self.SpellPerks.has_key("Bloodlost"):
            del self.SpellPerks["Bloodlust"]
        if self.SpellPerks.has_key("Stoneskin"):
            del self.SpellPerks["Stoneskin"]
    def GetResistedDamage(self, Target, Damage):
        if self.HasPerk("Fire Strike"):
            Damage *= Target.GetElementMultiplier("Fire")
            return int(Damage)
        if self.HasPerk("Cold Strike"):
            Damage *= Target.GetElementMultiplier("Cold")
            return int(Damage)
        if self.HasPerk("Lightning Strike"):
            Damage *= Target.GetElementMultiplier("Lightning")
            return int(Damage)
        return int(Damage)
    def GetElementMultiplier(self, ElementName):
        if self.HasPerk("Resist %s"%ElementName):
            return 0.33
        if self.HasPerk("Vulnerable %s"%ElementName):
            #print "I, %s, am vulnerable to %s, and so take MORE damage!"%(self.Species.Name, ElementName)
            return 1.5
        return 1.0
    def IsInvulnerable(self):
        """
        Is the critter immune to all damage?  (This doesn't happen often; we use it to make the
        summoner-required boss on level 4...
        """
        if self.Species.Name == "StoneHead" and not hasattr(self, "Broken"):
            return 1
    def CanCast(self):
        if self.MP==0 or self.IsIncapacitated() or self.HasPerk("Silence") or self.CurrentAction:
            return 0
        return 1
    def IsIncapacitated(self):
        if self.IsDead() or self.HasPerk("Sleep") or self.HasPerk("Paralysis") \
           or self.HasPerk("Stone"):
            return 1
        return 0
    def HasPerk(self, Name):
        Result = self.Perks.get(Name, None)
        if not Result:
            Result = self.SpellPerks.get(Name, None)
        return Result
    
    def GetAttackSound(self):
        if self.Species.AttackSounds:
            return random.choice(self.Species.AttackSounds) + ".wav"
        return None
    def GetProjectile(self):
        return self.Species.Projectile
    def GetEXPValue(self):
        Base = 10 * (1.6 ** (self.Species.Level + 1))
        return int(Base * self.Species.EXPMultiplier)
    def GetGoldValue(self):
        BaseValue = int(1.6**(self.Species.Level+1) * 10 * self.Species.GoldMultiplier)
        if BaseValue <= 0:
            return 0
        return random.randrange(int(BaseValue * 0.5), int(BaseValue * 1.5))
    def IsAlive(self):
        return (self.HP > 0)
    def IsDead(self):
        return (self.HP <= 0)
    def RollStat(self, Level, Multiplier):
        if (Level < 1):
            AverageStat = 5.0
        else:
            AverageStat = 10.0 + 2 * Level
        AverageStat *= Multiplier
        BoostMultiplier = (100 + random.randrange(-30,30)) / 100.0
        return int(AverageStat * BoostMultiplier)
    def RollStats(self, Level = None):
        if Level == None:
            Level = self.Species.Level
        self.STR = self.RollStat(Level, self.Species.STRMultiplier)
        self.DEX = self.RollStat(Level, self.Species.DEXMultiplier)
        self.CON = self.RollStat(Level, self.Species.CONMultiplier)
        self.WIS = self.RollStat(Level, self.Species.WISMultiplier)
        self.INT = self.RollStat(Level, self.Species.INTMultiplier)
        self.CHA = self.RollStat(Level, self.Species.CHAMultiplier)
        # If we're overriding the power level, then use BASE HP for the level.
        # (King Slime on level 10 should be beatable in reasonably fast time)
        if Level != self.Species.Level:
            self.HP = HPByLevel[Level]
        else:
            self.HP = HPByLevel[Level] * self.Species.HPMultiplier
        self.MaxHP = self.HP
        self.MP = MPByLevel[Level] * self.Species.MPMultiplier
        self.MaxMP = self.MP
        self.AC = ACByLevel[Level] * self.Species.ACMultiplier
        self.DamageDieCount = 2
        self.DamageDie = int((DamageByLevel[Level]/2.0)  * self.Species.DamageMultiplier)
        self.ToHitBonus = 0
    def IsPlayer(self):
        return 0
    def GetName(self):
        return self.Species.Name
    def MeleeSwing(self, Opponent, Quality):
        "Returns TRUE if we hit the opponent"
        EvasionChance = Opponent.DEX / float((2 * self.DEX) + self.ToHitBonus + (5 * Opponent.DEX))
        if Quality == HitQuality.Miss:
            if self.IsPlayer():
                # If they don't press a key, they will not hit:
                CombatLog("%s Swings: No keypress, no hit."%self.GetName())
                return 0
            else:
                # A perfect dodge!  Good evasion chance:
                EvasionChance *= 5.0
        elif Quality == HitQuality.Poor:
            EvasionChance *= 2.0
        elif Quality == HitQuality.Perfect:
            EvasionChance *= 0.5
        EvasionChance = min(EvasionChance, 0.5)
        CombatLog("")
        CombatLog("%s Swings at %s: Dex %svs%s (%s), evade %.2f%%"%(\
            self.GetName(), Opponent.GetName(), self.DEX, Opponent.DEX,
            HitQuality.QualityNames[Quality], EvasionChance*100))
        if random.random() < EvasionChance:
            CombatLog("...MISS!")
            return 0
        CombatLog("...HIT!")
        return 1
    def GetAverageDamage(self):
        Damage = 0.0
        for Die in range(self.DamageDice):
            Damage += (self.DamageDie + 1) / 2.0
        Damage += self.DamageBonus
        Damage *= self.GetSTRDamageMultiplier()
        Damage *= (1.08**self.Level)
        Damage += (5.0 * self.Level)
        return "%.1f"%Damage
    def GetSTRDamageMultiplier(self):
        return (1.0 + (self.STR - 10)*0.1)
    def MeleeDamage(self, Opponent, Quality):
        BaseDamage = self.GetDamage()
        if self.IsPlayer():        
            if (Quality == HitQuality.Miss):
                BaseDamage *= 0.5 # unused!
            elif (Quality == HitQuality.Poor):
                BaseDamage *= 0.5
            elif (Quality == HitQuality.Perfect):
                BaseDamage *= 2.0
            # Experience level affects damage:
            BaseDamage *= (1.08**self.Level)
            BaseDamage += (5.0 * self.Level)
        else:
            # Monster:
            # - monsters get a bigger damage boost for a 'perfect'
            # - Players on the back ranks take less damage than the point man
            if (Quality == HitQuality.Miss):
                BaseDamage *= 0.5
            elif (Quality == HitQuality.Poor):
                BaseDamage *= 0.75
            elif (Quality == HitQuality.Perfect):
                BaseDamage *= 2.0 # 3x is a little high
            if Opponent.Index in [0,1]:
                BaseDamage *= 0.75
            elif Opponent.Index == 3:
                BaseDamage *= 0.5
        BaseDamage *= self.GetSTRDamageMultiplier()
        CombatLog("%s rolls damage, gets %d"%(self.GetName(), BaseDamage))
        return int(BaseDamage)
    def BlockDamageWithAC(self, Damage):
        ActualDamage = BlockDamageWithAC(self.AC, Damage)
        CombatLog("%s's %d AC blocks %d points of damage, takes %d"%(self.GetName(), self.AC,
                                                                     (Damage-ActualDamage), ActualDamage))
        return ActualDamage
    def GetDamage(self):
        return RollDice(self.DamageDieCount, self.DamageDie)
    def GetAnimation(self, DesiredAnimationType):
        Animation = self.Species.Animations.get(DesiredAnimationType, None)
        if Animation:
            return Animation
        if (DesiredAnimationType == AnimationType.Stand) and (not Animation):
            return DefaultAnimation
        return None
    def MitigateCondition(self, ConditionName):
        Stat = self.Perks.get(ConditionName, None)
        if Stat!=None:
            Stat -= self.CON
            if self.HasPerk("Recovery"):
                Stat -= self.CON * 2 # recover thrice as fast!
            if Stat<=0:
                del self.Perks[ConditionName]
            else:
                self.Perks[ConditionName] = Stat
    def MitigateConditions(self):
        self.MitigateCondition("Poison")
        self.MitigateCondition("Sleep")
        self.MitigateCondition("Paralysis")
        self.MitigateCondition("Silence")
        self.MitigateCondition("Stone")
    def GetPoisonDamage(self):
        return int(1 + (self.MaxHP / 30))
    def GetCastingTime(self, Spell):
        BaseTime = Spell.CastingTime
        if self.IsPlayer() and self.Species.Name == "Cleric":
            Stat = self.WIS
        else:
            Stat = self.INT
        CastTime = int(BaseTime * (1.0 + 0.02 * (Stat - 15)))
        if self.HasPerk("Haste"):
            CastTime = int(CastTime * HasteFactor)
        return max(min(CastTime, 1000), 5)
        
def BlockDamageWithAC(AC, Damage):
    CostPerPoint = 1
    BoundaryStep = Damage * 0.4
    NextBoundary = BoundaryStep 
    for PointIndex in range(Damage):
        if (PointIndex >= NextBoundary):
            CostPerPoint *= 3
            BoundaryStep *= 0.6
            NextBoundary += BoundaryStep
        if AC < CostPerPoint:
            return (Damage - PointIndex)
        AC -= CostPerPoint
    return 1

        

class Player(Critter):
    NakedDamageDice = 1
    NakedDamageDie = 2
    def __getstate__(self):
        """
        Special code for pickling the player:  Don't pickle the player's class (species).  For one thing,
        the class doesn't change over the course of the game; for another thing, it has links to Surface
        instances!
        """
        Dict = self.__dict__.copy()
        Dict["Species"] = self.Species.Name
        return Dict
    def __setstate__(self, Dict):
        self.__dict__ = Dict
        self.Species = ClassesByName[self.Species]
    def MitigateConditions(self):
        Critter.MitigateConditions(self)
        for Key in self.SpellPerks.keys():
            self.SpellPerks[Key] -= 1
            if self.SpellPerks[Key]<=0:
                del self.SpellPerks[Key]
    def HasPerk(self, Name):
        Value = self.Perks.get(Name, None)
        if Value==None:
            Value = self.EquipPerks.get(Name, None)
        if Value == None:
            Value = self.SpellPerks.get(Name, None)
        return Value
    def __init__(self, Name, Class):
        self.Name = Name
        self.Level = 1
        self.Party = None
        self.Index = None # index in a party
        self.Species = Class
        Critter.__init__(self, Class)
        self.Equipment = {} # mapping: SLOT to ITEM-TYPE
        self.DamageDice = self.NakedDamageDice
        self.DamageDie = self.NakedDamageDie
        self.DamageBonus = 0
        self.Perks = {}
        self.EquipPerks = {}
        self.SpellPerks = {} # Perks granted from a spell, temporarily.  
        self.EXP = 0
        self.TurnedFlag = 0 # set to 1 when a cleric uses their turning up
        self.HP = self.GetMaxHP() #self.Species.HP * 10
        self.MaxHP = self.HP
        self.MP = self.GetMaxMP() #self.Species.MP
        self.MaxMP = self.MP
    def ChangeClass(self, NewClass):
        "Call this only during character-creation time!"
        OldItems = self.Equipment.values()
        self.Strip()
        self.Species = NewClass
        # Fix STR/DEX/etc
        self.RollStats()
        # Fix HP and MP:
        self.HP = self.GetMaxHP() #self.Species.HP * 10
        self.MaxHP = self.HP
        self.MP = self.GetMaxMP() #self.Species.MP
        self.MaxMP = self.MP
        for Item in OldItems:
            self.Equip(Item)
    def GetNakedStat(self, StatName):
        Value = getattr(self, StatName)
        for Item in self.Equipment.values():
            if Item:
                Value -= getattr(Item, StatName)
        return Value
    def CanSwitchTargets(self):
        return 1 # %%% return false for an attack (like shuriken-throw) that can't switch targets in mid-animation
    def LevelUp(self):
        "Gain a level of exp!  Returns a list of strings for display to the user"
        self.EXP = 0
        self.Level += 1
        Str = "<BIG><CENTER><CN:ORANGE>Power up!</C></CENTER></BIG>\n\n\n<CN:BRIGHTGREEN>%s</C> the <CN:BRIGHTGREEN>%s</C> has advanced to level <CN:BRIGHTRED>%d</C>!\n\n"%(self.Name, self.Species.Name, self.Level)
        ######
        # Lucky stat gain:
        if random.random() > 0.66:
            StatName = random.choice(("STR","DEX","CON","INT","WIS","CHA"))
            Stat = self.GetNakedStat(StatName)
            if Stat < MaxStat:
                setattr(self, StatName, Stat+1)
            Str += "<CN:BRIGHTBLUE>Lucky!</C>  Gained a point of <CN:RED>%s</C>.\n"%StatName
        ######
        OldMaxHP = self.MaxHP
        self.MaxHP = self.GetMaxHP()
        HPGain = (self.MaxHP - OldMaxHP)
        if self.IsAlive():
            self.HP += HPGain
        if HPGain:
            Str += "Gained <CN:RED>%d</C> hit points!\n"%HPGain
        ######
        OldMaxMP = self.MaxMP
        self.MaxMP = self.GetMaxMP()
        MPGain = (self.MaxMP - OldMaxMP)
        if self.IsAlive():
            self.MP += MPGain
        if MPGain:
            Str += "Gained <CN:BRIGHTBLUE>%d</c> magic points!\n"%MPGain
        return Str
    def GetEXPToLevel(self):
        return max(0, self.Species.GetEXPToNextLevel(self.Level) - self.EXP)
    def IsPlayer(self):
        return 1
    def RollStats(self):
        # Called when rolling a new character:
        self.STR = self.Species.STR # RollDice(3,6)
        self.DEX = self.Species.DEX #RollDice(3,6)
        self.CON = self.Species.CON #RollDice(3,6)
        self.WIS = self.Species.WIS #RollDice(3,6)
        self.INT = self.Species.INT #RollDice(3,6)
        self.CHA = self.Species.CHA #RollDice(3,6)
        self.AC = 0 # Humans don't get a base AC (well, maybe ninjas should...)
        self.ToHitBonus = 0 # ...or a base to-hit and to-dam (...)
    def GetDamage(self):
        Damage = RollDice(self.DamageDice, self.DamageDie)
        Damage += self.DamageBonus
        CombatLog("%s rolls %dd%d + %d = %d damage"%(self.GetName(), self.DamageDice, self.DamageDie, self.DamageBonus, Damage))        
        return Damage 
    def GetEquip(self, Slot):
        return self.Equipment.get(Slot, None)
    def OptimizeEquipment(self):
        self.Strip()
        for Slot in EquipSlots.Slots:
            BestItem = Global.Party.FindBestEquipForSlot(Slot, self)
            self.Equip(BestItem)
    def CanEquip(self, Item):
        if Item.Slot==None: # Grey out potions and such on equip screen:
            return 0
        if self.Species.Letter in Item.Classes:
            return 1
        return 0
    def Equip(self, Item):
        if not Item:
            return
        OldItem = self.Equipment.get(Item.Slot, None)
        if OldItem:
            self.Remove(OldItem)
        OldMaxHP = self.MaxHP
        OldMaxMP = self.MaxMP
        for StatAttribute in ["STR", "DEX", "CON", "INT", "WIS", "CHA", "AC", "DamageBonus", "ToHitBonus"]:
            OldAttribute = getattr(self, StatAttribute)
            ItemAttribute = getattr(Item, StatAttribute)
            setattr(self, StatAttribute, OldAttribute + ItemAttribute)
        if Item.DamageDice:
            self.DamageDice = Item.DamageDice
            self.DamageDie = Item.DamageDie
        self.Equipment[Item.Slot] = Item
        self.FixPerks()
        self.MaxHP = self.GetMaxHP()
        self.MaxMP = self.GetMaxMP()        
        # HP juggling: When you put on a +HP item, you gain HP, and when you take it off, you lose them:
        if self.IsAlive():
            self.HP += (self.MaxHP - OldMaxHP)
            self.HP = max(self.HP, 1) # Don't die just by taking off your hat.  That's just too sad.
        self.MP = max(0, min(self.MP, OldMaxMP))
        if self.Party:
            self.Party.DropItem(Item)
    def Strip(self):
        for Item in self.Equipment.values():
            if Item:
                self.Remove(Item)
    def Remove(self, Item):
        if not Item:
            return
        OldMaxHP = self.MaxHP
        OldMaxMP = self.MaxMP
        OldMP = self.MP
        for StatAttribute in ["STR", "DEX", "CON", "INT", "WIS", "CHA", "AC", "DamageBonus", "ToHitBonus"]:
            OldAttribute = getattr(self,StatAttribute)
            ItemAttribute = getattr(Item, StatAttribute)
            setattr(self, StatAttribute, OldAttribute - ItemAttribute)
        self.Equipment[Item.Slot] = None
        self.MaxHP = self.GetMaxHP()
        self.MaxMP = self.GetMaxMP()
        if Item.DamageDice:
            self.DamageDice = self.NakedDamageDice
            self.DamageDie = self.NakedDamageDie
        if self.IsAlive():
            self.HP += (self.MaxHP - OldMaxHP)
            self.HP = max(self.HP, 1) # Don't die just by taking off your hat.  That's just too sad.
        self.MP = max(0, min(self.MaxMP, OldMP))
        if self.Party:
            self.Party.GetItem(Item)
        self.FixPerks()
    def FixPerks(self):
        self.EquipPerks = {}
        for Item in self.Equipment.values():
            if Item:
                for Name in Item.Perks.keys():
                    self.EquipPerks[Name] = 1
    def GetPerks(self):
        Dict = {}
        for Perk in self.Perks.keys():
            if self.Perks[Perk]:
                Dict[Perk]=self.Perks[Perk]
        for Perk in self.EquipPerks.keys():
            if self.EquipPerks[Perk]:            
                Dict[Perk]=self.EquipPerks[Perk]
        return Dict
    def GetNakedPerks(self, Slot):
        Perks = {}
        for Perk in self.Perks.keys():
            Perks[Perk] = self.Perks[Perk]
        for OtherSlot in EquipSlots.Slots:
            if Slot==OtherSlot:
                continue
            Item = self.Equipment.get(OtherSlot, None)
            if Item:
                for Perk in Item.Perks:
                    Perks[Perk] = 1
        return Perks
    def CanCastSpells(self):
        if self.HP>0 and self.Species.Name in [ClassNames.Mage, ClassNames.Cleric, ClassNames.Summoner]:
            if not self.Perks.get("Stone") and not self.Perks.get("Sleep") and not self.Perks.get("Paralysis") and not self.Perks.get("Silence"):
                return 1
    def CanTurn(self):
        if self.Species.Name == ClassNames.Cleric and not self.TurnedFlag and not self.CurrentAction:
            return 1
    def GetStatus(self, CurrentDisplay = None):
        if self.IsDead():
            return ("Dead", Colors.Red, )
        Statuses = [None, "Poisoned","Asleep","Paralyzed","Stone","Silenced"]
        try:
            Index = Statuses.index(CurrentDisplay[0])
        except:
            Index = 0
        while (1):
            if self.Perks.get("Poison", None) and (Index<1):
                return ("Poisoned", Colors.Purple)
            if self.Perks.get("Sleep", None) and (Index<2):
                return ("Asleep", Colors.Yellow)
            if self.Perks.get("Paralysis", None) and (Index<3):
                return ("Paralyzed", Colors.Yellow)
            if self.Perks.get("Stone", None) and (Index<4):
                return ("Stone", Colors.Grey)
            if self.Perks.get("Silence", None) and (Index<5):
                return ("Silenced", Colors.Orange)
            if (Index==0):
                return ("Ok", Colors.White)
            Index = 0 # Cycle through once more
    def Die(self):
        self.CurrentAction = ""
        self.Perks["Poison"]=0
        self.Perks["Sleep"]=0
        self.Perks["Paralysis"]=0
        self.Perks["Stone"]=0
        self.Perks["Silence"]=0
        self.HP = 0
    def GetMaxHP(self):
        MaxHP = self.Species.HP * 8
        for Level in range((self.Level - 1)):
            Multiplier = min(8.0, 1.0 + Level*0.5)
            MaxHP += self.Species.HP + (self.CON/2.0) * Multiplier
        for Item in self.Equipment.values():
            if Item:
                MaxHP += Item.MaxHP
        return int(MaxHP)
    def GetMaxMP(self):
        if self.Species.Name==ClassNames.Cleric:
            Stat = self.WIS
        elif self.Species.Name in [ClassNames.Mage, ClassNames.Summoner]:
            Stat = self.INT
        else:
            return 0
        MaxMP = self.Species.MP * 2
        for Level in range((self.Level - 1)):
            Multiplier = min(8.0, 1.0 + Level*0.5)
            MaxMP += self.Species.MP + (Stat/3.0) * Multiplier
        for Item in self.Equipment.values():
            if Item:
                MaxMP += Item.MaxMP
        return int(MaxMP)
class Item:
    def __init__(self):
        self.Level = [1,] # Corresponds to dungeon level where it's likely found
        self.Cost = 0
        self.MaxHP = 0
        self.MaxMP = 0
        self.STR = 0
        self.DEX = 0
        self.CON = 0
        self.INT = 0
        self.WIS = 0
        self.CHA = 0
        self.AC = 0
        self.DamageDice = 0
        self.DamageDie = 0
        self.DamageBonus = 0
        self.ToHitBonus = 0
        self.Perks = {}
        self.Slot = None
        self.Classes = ""
    def __str__(self):
        return "<item '%s'>"%self.Name
    def Validate(self):
        "Called by the integrity-checker"
        try:
            Pic = Resources.GetImage(os.path.join("Images","Item","%s.png"%self.Name), 1)
        except:
            print "Missing item image for '%s'"%self.Name
        for Perk in self.Perks.keys():
            if not AllPerks.has_key(Perk):
                print "Weird perk '%s' found on item '%s'"%(Perk, self.Name)
        
        

class PlayerClass(Species):
    def __init__(self, Name, HP, MP, EXPRequirement = 1.0):
        global ClassNameToClass
        Species.__init__(self, 1, Name)
        ClassNameToClass[Name] = self
        self.HP = HP
        self.MP = MP
        self.Letter = Name[0]
        self.EXPRequirement = EXPRequirement
        self.STR = 10
        self.DEX = 10
        self.CON = 10
        self.INT = 10
        self.WIS = 10
        self.CHA = 10
    def GetEXPToNextLevel(self, Level):
        BaseEXP = 800
        if self.Name == ClassNames.Fighter:
            BaseEXP = 600
        elif self.Name == ClassNames.Cleric:
            BaseEXP = 850
        elif self.Name == ClassNames.Mage:
            BaseEXP = 900
        elif self.Name == ClassNames.Summoner:
            BaseEXP = 1000
        EXPRequired = (1.40 ** Level) * BaseEXP
        EXPRequired = int(EXPRequired * self.EXPRequirement)
        return EXPRequired


class BestiaryClass:
    PredefinedAnimations = {"Cycle7":"0,0,1,1,2,2,3,3,4,4,5,5,6,6|0,1,2,3,4,5,6",
                            "Cycle6":"0,0,1,1,2,2,3,3,4,4,5,5|0,1,2,3,4,5",
                            "Cycle5":"0,0,1,1,2,2,3,3,4,4|0,1,2,3,4",
                            "Cycle4Slow":"0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3|0,1,2,3",
                            "Cycle4":"0,0,1,1,2,2,3,3|0,1,2,3",
                            "Cycle3":"0,0,1,1,2,2|0,1,2",
                            "Cycle3Slow":"0,0,0,0,1,1,1,1,2,2,2,2|0,1,2",
                            "Cycle2":"0,0,0,1,1,1|0,1",
                            "Cycle2Slow":"0,0,0,0,0,1,1,1,1,1|0,1",
                            "Cycle1":"0,0,0,0,0|0",
                            "Cycle1Slow":"0,0,0,0,0,0,0,0,0|0",
                            #"Lunge":"|0,0,0,0,0,0,0,0,0,0,0,0,0|-2,-4,-5,-4,-2,0,3,6,10,15,10,6,3||9"}
                            "Lunge":"|0,0,0,0,0,0,0,0,0,0,0,0,0|-4,-8,-10,-8,-4,0,6,12,20,30,20,12,6||9",
                            "Hover":"0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7|0,1,0,1,0,1,0,1||0,-5,-9,-5,0,5,9,5",
                            "Jumpy":"0,1,2,3,4,5,6,6,6,6,7,8,9,10,11|0, 0,  0,  0,  0, 0, 0, 0, 0, 0, 0, 0|0, 5,  9, 11, 13,17,23,20,17,14,11, 6|0,-6,-10,-12,-10,-6, 0,-3,-3, 0,-3,-3",
                            "Circle":"0,1,2,3,4,5,6,7,8,9,10,11,12,13,14|0,1,2,0,1,2,0,1,2,0,1,2,0,1,2|14,12,9,4,-1,-6,-11,-13,-13,-11,-7,-1,4,9,12|0,-5,-10,-13,-13,-12,-8,-2,2,8,12,13,13,10,5",
                            }
    def __init__(self):
        self.AllSpecies = {}
        # Mapping: Level to a list of random encounters for the level.  Boss battles are
        # all named, and live in the same dictionary.  An encounter is a list of ranks, and each ranks
        # is a list of monster species.  For example:
        # Encounter1 = (("Dracula"),("Bat","Bat")) - Dracula in the back rank, 2 bats in the front rank
        self.Encounters = {} 
        self.CreateDefaultSpecies()        
        self.LoadCritters()
        self.LoadEncounterTables()
    def CheckImageCase(self):
        SpeciesToFind = []
        for Species in self.AllSpecies.values():
            SpeciesToFind.append(Species.Name)
        for FileName in os.listdir(Paths.ImagesCritter):
            if FileName in SpeciesToFind:
                SpeciesToFind.remove(FileName)
        print "The following species don't seem to have image-dirs, probably due to inconsistent capitals:"
        print SpeciesToFind
        
            
    def ValidateCritters(self):
        for Critter in self.AllSpecies.values():
            Critter.Validate()
    def GetMarchingCritter(self):
        "For the Welcome screen"
        Insanity = 0
        while (1):
            Names = self.AllSpecies.keys()
            Name = random.choice(Names)
            Critter = self.GetCritter(Name)
            if Critter.Species.UniqueFlag:
                continue
            Animation = Critter.GetAnimation(AnimationType.Stand)
            if not Animation.MissingImageFlag:
                return Critter
            Insanity += 1
            if Insanity>25:
                # Stop the insanity!
                return Critter
    def CreateDefaultSpecies(self):
        self.DefaultSpecies = Species(1, "Goomba")
        self.AllSpecies["goomba"] = self.DefaultSpecies
    def GetCritter(self, SpeciesName):
        Species = self.AllSpecies.get(SpeciesName.lower(), None)
        if not Species:
            print "**WARNING: Invalid species '%s' in GetCritter()"%SpeciesName
            Species = self.DefaultSpecies
        return Critter(Species)
    def ValidateEncounters(self):
        "Integrity-check our list of encounters to see that they make some sense"
        UnusedCritters = {}
        for Name in self.AllSpecies.keys():
            if not self.AllSpecies[Name].UniqueFlag:
                UnusedCritters[Name] = 1
        for Level in self.Encounters.keys():
            for Encounter in self.Encounters[Level]:
                for Rank in Encounter:
                    for Name in Rank:
                        if not self.AllSpecies.has_key(Name.lower()):
                            print "** Weird species '%s' in an encounter on level %s"%(Name, Level)
                            print "Encounter:", Encounter
                        try:
                            del UnusedCritters[Name.lower()]
                        except:
                            pass
        print "Unused critters:"
        Names = UnusedCritters.keys()
        Names.sort()
        for Name in Names:
            print Name
    def LoadEncounterTables(self):
        File = open("Encounters.txt","r")
        LineNumber = 0
        for FileLine in File.xreadlines():
            LineNumber += 1
            FileLine = FileLine.strip()
            if not FileLine or FileLine[0]=="#":
                continue
            Bits = FileLine.split("\t")
            try:
                self.LoadEncounter(Bits)
            except:
                print "* Error loading an encounter.  Offending line %d:"%LineNumber
                print FileLine
                traceback.print_exc()               
    def GetRandomEncounter(self, Level):
        EncounterMonsters = random.choice(self.Encounters[Level])
        MonsterRankList = self.GetMonsterLists(EncounterMonsters)
        return MonsterRankList
    def GetMonsterLists(self, MonsterList):
        Ranks = []
        for NameList in MonsterList:
            Rank = []
            for MonsterName in NameList:
                Rank.append(self.GetCritter(MonsterName))
            Ranks.append(Rank)
        return Ranks
    def LoadEncounter(self, Bits):
        "Load one encounter into our tables."
        Level = Bits[0].strip()
        if len(Level)<1:
            return
        try:
            Level = int(Level)
        except:
            pass
        NewEncounter = []
        for Bit in Bits[1:]:            
            Bit = Bit.strip()
            if len(Bit)<1:
                continue
            if (Bit[0] == '"' and Bit[-1] == '"'):
                Bit = Bit[1:-1]
            Rank = Bit.split(",")
            RealRank = []
            for SpeciesName in Rank:
                SpeciesName = SpeciesName.strip()
                if SpeciesName:
                    RealRank.append(SpeciesName)
            NewEncounter.append(RealRank)
        if not self.Encounters.has_key(Level):
            self.Encounters[Level] = []
        self.Encounters[Level].append(NewEncounter)

    def LoadCritters(self):
        File = open("Critters.txt","r")
        LineNumber = 0
        for FileLine in File.xreadlines():
            LineNumber += 1
            FileLine = FileLine.strip()
            if not FileLine or FileLine[0]=="#" or FileLine[:2]=='"#':
                continue
            Bits = FileLine.split("\t")
            try:
                self.LoadSpecies(Bits)
            except:
                print "* Error loading a species.  File line %d:"%LineNumber
                print FileLine
                traceback.print_exc()
    def LoadSpecies(self, Bits):
        Name = Bits[0].strip()
        if not Name:
            return
        while len(Bits)<27:
            Bits.append("")
        Level = int(Bits[2])
        NewSpecies = Species(Level, Name)
        self.AllSpecies[Name.lower()] = NewSpecies
        NewSpecies.HPMultiplier = self.GetFloat(Bits[3], 1.0)
        NewSpecies.MPMultiplier = self.GetFloat(Bits[4], 0.0)
        NewSpecies.ACMultiplier = self.GetFloat(Bits[5])
        NewSpecies.ExpMultiplier = self.GetFloat(Bits[6])
        NewSpecies.GoldMultiplier = self.GetFloat(Bits[7])
        NewSpecies.DamageMultiplier = self.GetFloat(Bits[8])
##        NewSpecies.DamageDieCount = self.GetInt(Bits[7], 1)
##        NewSpecies.DamageDie = self.GetInt(Bits[8], 6)
        NewSpecies.STRMultiplier = self.GetFloat(Bits[9])
        NewSpecies.DEXMultiplier = self.GetFloat(Bits[10])
        NewSpecies.CONMultiplier = self.GetFloat(Bits[11])
        NewSpecies.INTMultiplier = self.GetFloat(Bits[12])
        NewSpecies.WISMultiplier = self.GetFloat(Bits[13])
        NewSpecies.CHAMultiplier = self.GetFloat(Bits[14])
        self.GetAnimation(NewSpecies, Bits[15], AnimationType.Stand)
        self.GetAnimation(NewSpecies, Bits[16], AnimationType.Attack)
        self.GetAnimation(NewSpecies, Bits[17], AnimationType.Ouch)
        self.GetAnimation(NewSpecies, Bits[18], AnimationType.Block)
        self.GetAnimation(NewSpecies, Bits[19], AnimationType.Death)
        self.LoadProjectile(NewSpecies, Bits[20])
        File = Bits[21].strip()
        if File:
            NewSpecies.AttackSounds = [File]
        self.GetPerks(NewSpecies, Bits[22])
        self.GetSpells(NewSpecies, Bits[23])
        Bit = Bits[24].strip()
        if Bit:
            Bit = Bit.replace('"',"")
            Chunks = Bit.split(",")
            NewSpecies.RecenterX = int(Chunks[0])
            NewSpecies.RecenterY = int(Chunks[1])
        NewSpecies.UniqueFlag = self.GetInt(Bits[25])
    def GetSpells(self, Species, Str):
        Str = Str.strip().replace('"',"")
        Bits = Str.split(",")
        for Bit in Bits:
            Species.SpellsKnown[Bit.strip()] = 1
    def GetPerks(self, Species, Str):
        Str = Str.strip().replace('"',"")
        Bits = Str.split(",")
        for Bit in Bits:
            Bit = Bit.strip()
            if Bit:
                Species.Perks[Bit] = 1
    def LoadProjectile(self, Species, Str):
        Str = Str.strip().replace('"',"")
        if not Str:
            return
        Bits = Str.split(",")
        Species.Projectile = (Bits[0], int(Bits[1]), int(Bits[2]))
    def GetAnimation(self, Species, Str, Type):
        Str = Str.strip().replace('"',"")
        if not Str:
            return        
        Str = self.PredefinedAnimations.get(Str, Str)
        PipeBits = Str.split("|")
        # Pipe bits:
        # Frame-to-cel, images, xpos, ypos
        # or:
        # Frame-to-cel, images, xpos, ypos, critical-frame
        ImageNumbers = None
        while len(PipeBits)<5:
            PipeBits.append("")
        FrameToCel = self.StrToIntArray(PipeBits[0])
        ImageNumbers = self.StrToIntArray(PipeBits[1])
        XPos = self.StrToIntArray(PipeBits[2])
        YPos = self.StrToIntArray(PipeBits[3])
        Cels = max(len(ImageNumbers), len(XPos), len(YPos))
        if len(FrameToCel):
            Cels = max(Cels, max(FrameToCel)+1)
        NewAnimation = Animation(Type, Cels)
        if FrameToCel:
            NewAnimation.FrameCels = FrameToCel
        if XPos:
            NewAnimation.XPositions = XPos
        if YPos:
            NewAnimation.YPositions = YPos
        if ImageNumbers:
            NewAnimation.ImageNumbers = ImageNumbers
        if PipeBits[4]!="":
            NewAnimation.CriticalFrameNumber = self.GetInt(PipeBits[4], 0)
        Species.Animations[Type] = NewAnimation
    def StrToIntArray(self, Str, Separator = ","):
        Arr = []
        Str = Str.strip()
        if not Str:
            return []        
        for Number in Str.split(Separator):
            Arr.append(int(Number))
        return Arr
    def GetFloat(self, Str, Default = 1.0):
        try:
            Val = float(Str)
        except:
            Val = Default
        return Val

    def GetInt(self, Str, Default = 0):
        try:
            Val = int(Str)
        except:
            Val = Default
        return Val

def GetTestMonsters():
    return Global.Bestiary.GetRandomEncounter(1)
    MonsterA = Global.Bestiary.GetCritter("Trooper")
    MonsterB = Global.Bestiary.GetCritter("RedTrooper")
    #MonsterB = Global.Bestiary.GetCritter("Firecrawler")
    #MonsterC = Global.Bestiary.GetCritter("Alien")
    return [MonsterA, MonsterB]
    #return [MonsterA,MonsterC,MonsterB]
    #return [MonsterA, MonsterB, MonsterC]

Global.Bestiary = BestiaryClass()

DefaultAnimation = Animation(AnimationType.Stand, 1)

##### This is the Simon Belmont version:
def BuildNinjaClass(Ninja):
    Ninja.STR = 13
    Ninja.DEX = 17
    Ninja.CON = 13
    Ninja.INT = 10
    Ninja.WIS = 8
    Ninja.CHA = 6
    ##
    StandAnimation = Animation(AnimationType.Stand, 3)
    StandAnimation.FrameCels = [0,0,1,1,2,2,2,2]
    StandAnimation.RepeatFlag = 1
    Ninja.Animations[AnimationType.Stand] = StandAnimation
    ###
    AttackAnimation = Animation(AnimationType.Attack, 7)
    AttackAnimation.FrameCels = [0,0,0,0,1,2,3,4,5,6,6,6,6,6]
    AttackAnimation.XPositions = [-116]*7
    AttackAnimation.YPositions = [2]*7
    AttackAnimation.CriticalFrameNumber = 8
    Ninja.Animations[AnimationType.Attack] = AttackAnimation
    ###
    BlockAnimation = Animation(AnimationType.Block, 1)
    BlockAnimation.FrameCels = [0]*15
    Ninja.Animations[AnimationType.Block] = BlockAnimation
    ###
    OuchAnimation = Animation(AnimationType.Ouch, 1)
    OuchAnimation.FrameCels = [0]*15
    Ninja.Animations[AnimationType.Ouch] = OuchAnimation
    ###
    DeathAnimation = Animation(AnimationType.Death, 3)
    DeathAnimation.FrameCels = [0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2]
    DeathAnimation.XPositions = [-14,-14,-14]
    Ninja.Animations[AnimationType.Death] = DeathAnimation

def BuildFighterClass(Fighter):
    Fighter.STR = 16
    Fighter.DEX = 12
    Fighter.CON = 15
    Fighter.INT = 8
    Fighter.WIS = 8
    Fighter.CHA = 8
    StandAnimation = Animation(AnimationType.Stand, 2)
    StandAnimation.FrameCels = [0,0,0,0,1,1,1,1]
    StandAnimation.RepeatFlag = 1
    Fighter.Animations[AnimationType.Stand] = StandAnimation
    ###
    AttackAnimation = Animation(AnimationType.Attack, 5)
    AttackAnimation.FrameCels = [0,0,1,1,1,1,2,3,4,4,4]
    AttackAnimation.XPositions = [-38]*5
    AttackAnimation.YPositions = [-35]*5
    AttackAnimation.CriticalFrameNumber = 10
    Fighter.Animations[AnimationType.Attack] = AttackAnimation
    ###
    BlockAnimation = Animation(AnimationType.Block, 1)
    BlockAnimation.FrameCels = [0]*15
    BlockAnimation.XPositions = [-30]
    BlockAnimation.YPositions = [-50]
    Fighter.Animations[AnimationType.Block] = BlockAnimation
    ###
    OuchAnimation = Animation(AnimationType.Ouch, 2)
    OuchAnimation.ImageNumbers = [0,0,0,0,1,1,1,1,1,1,1,1,1]
    OuchAnimation.FrameCels = [0,0,0,0,1,2,3,4,5,6,7,8,9]
    #OuchAnimation.YPositions = [0, -5, -9, -11, -12, -11, -9, -5, 0, -2, -3, -2, 0]
    #OuchAnimation.YPositions = [-5, -10, -14, -15, -16, -15, -13, -9, -4, -6, -7, -6, -4]
    OuchAnimation.YPositions = [-25, -30, -34, -35, -36, -35, -33, -29, -24, -26, -27, -26, -24]
    OuchAnimation.XPositions = [-3,-1,1,3,  5,7,9,11,12,13,14,15,16]
    Fighter.Animations[AnimationType.Ouch] = OuchAnimation
    ###
    DeadAnimation = Animation(AnimationType.Death, 1)
    DeadAnimation.RepeatFlag = 1
    Fighter.Animations[AnimationType.Death] = DeadAnimation


def BuildSummonerClass(Summoner):
    Summoner.STR = 6
    Summoner.DEX = 10
    Summoner.CON = 8
    Summoner.INT = 16
    Summoner.WIS = 12
    Summoner.CHA = 13
    StandAnimation = Animation(AnimationType.Stand, 2)
    StandAnimation.FrameCels = [0, 0, 0, 0, 1, 1, 1, 1]
    StandAnimation.RepeatFlag = 1
    Summoner.Animations[AnimationType.Stand] = StandAnimation
    ###
    AttackAnimation = Animation(AnimationType.Attack, 5)
    AttackAnimation.FrameCels = [0,0,1,1,0,0,1,1,2,2,3,3,4,4]
    AttackAnimation.XPositions = [1]*5
    AttackAnimation.YPositions = [-18]*5
    AttackAnimation.CriticalFrameNumber = 11
    Summoner.Animations[AnimationType.Attack] = AttackAnimation
    ###
    BlockAnimation = Animation(AnimationType.Block, 1)
    BlockAnimation.FrameCels = [0]*15
    Summoner.Animations[AnimationType.Block] = BlockAnimation
    ###
    OuchAnimation = Animation(AnimationType.Ouch, 2)
    OuchAnimation.ImageNumbers = [0,1,1]
    OuchAnimation.FrameCels =  [0,0,0,1,1,2,2,1,1,2,2]
    OuchAnimation.YPositions = [0,0,0]
    OuchAnimation.XPositions = [0,0,10]
    Summoner.Animations[AnimationType.Ouch] = OuchAnimation
    ###
    DeadAnimation = Animation(AnimationType.Death, 1)
    DeadAnimation.RepeatFlag = 1
    Summoner.Animations[AnimationType.Death] = DeadAnimation

def BuildClericClass(Cleric):
    Cleric.STR = 13
    Cleric.DEX = 8
    Cleric.CON = 13
    Cleric.INT = 10
    Cleric.WIS = 16
    Cleric.CHA = 10
    StandAnimation = Animation(AnimationType.Stand, 2)
    StandAnimation.FrameCels = [0, 0, 0, 0, 1, 1, 1, 1]
    StandAnimation.RepeatFlag = 1
    Cleric.Animations[AnimationType.Stand] = StandAnimation
    ###
    AttackAnimation = Animation(AnimationType.Attack, 3)
    #AttackAnimation.FrameCels = [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,]
    AttackAnimation.FrameCels = [0,0,0,1,1,1,2,2,2]
    AttackAnimation.XPositions = [-18]*5
    AttackAnimation.YPositions = [8]*5
    AttackAnimation.CriticalFrameNumber = 11
    Cleric.Animations[AnimationType.Attack] = AttackAnimation
    Cleric.Projectile = ("Arrow", 6, 10)
    ###
    BlockAnimation = Animation(AnimationType.Block, 1)
    BlockAnimation.FrameCels = [0]*15
    Cleric.Animations[AnimationType.Block] = BlockAnimation
    ###
    OuchAnimation = Animation(AnimationType.Ouch, 2)
    OuchAnimation.ImageNumbers = [0,1,1]
    OuchAnimation.FrameCels =  [0,0,0,1,1,2,2,1,1,2,2]
    OuchAnimation.YPositions = [0,0,0]
    OuchAnimation.XPositions = [0,0,10]
    Cleric.Animations[AnimationType.Ouch] = OuchAnimation
    ###
    DeadAnimation = Animation(AnimationType.Death, 1)
    DeadAnimation.FrameCels = [0]
    DeadAnimation.RepeatFlag = 1
    Cleric.Animations[AnimationType.Death] = DeadAnimation
    ##
    
def BuildMageClass(Mage):
    Mage.STR = 8
    Mage.DEX = 8
    Mage.CON = 8
    Mage.INT = 16
    Mage.WIS = 12
    Mage.CHA = 10
    StandAnimation = Animation(AnimationType.Stand, 2)
    StandAnimation.FrameCels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    StandAnimation.RepeatFlag = 1
    Mage.Animations[AnimationType.Stand] = StandAnimation
    ###
    AttackAnimation = Animation(AnimationType.Attack, 4)
    #AttackAnimation.FrameCels = [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,]
    AttackAnimation.ImageNumbers = [1,2,3]
    AttackAnimation.FrameCels = [0,0,0,0,1,1,2,2]
    AttackAnimation.XPositions = [-1]*3
    AttackAnimation.YPositions = [0]*3
    AttackAnimation.CriticalFrameNumber = 8
    Mage.Animations[AnimationType.Attack] = AttackAnimation
    Mage.Projectile = ("Fireball", 6, 10)
    ###
    BlockAnimation = Animation(AnimationType.Block, 1)
    BlockAnimation.FrameCels = [0]*15
    Mage.Animations[AnimationType.Block] = BlockAnimation
    ###
    OuchAnimation = Animation(AnimationType.Ouch, 2)
    OuchAnimation.ImageNumbers = [0,1,1]
    OuchAnimation.FrameCels =  [0,0,0,1,1,2,2,1,1,2,2]
    OuchAnimation.YPositions = [0,0,0]
    OuchAnimation.XPositions = [0,0,10]
    Mage.Animations[AnimationType.Ouch] = OuchAnimation
    ###
    DeadAnimation = Animation(AnimationType.Death, 1)
    DeadAnimation.FrameCels = [0]
    DeadAnimation.RepeatFlag = 1
    Mage.Animations[AnimationType.Death] = DeadAnimation
    ##

def BuildBardClass(Bard):
    Bard.STR = 11
    Bard.DEX = 15
    Bard.CON = 10
    Bard.INT = 9
    Bard.WIS = 8
    Bard.CHA = 16
    StandAnimation = Animation(AnimationType.Stand, 8)
    StandAnimation.FrameCels = [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,]
    StandAnimation.RepeatFlag = 1
    Bard.Animations[AnimationType.Stand] = StandAnimation
    ###
    AttackAnimation = Animation(AnimationType.Attack, 8)
    ##AttackAnimation.FrameCels = [0,0,1,1,1,1,2,3,4,4,4]
    AttackAnimation.XPositions = [-87]*8
    AttackAnimation.YPositions = [-28]*8
    AttackAnimation.CriticalFrameNumber = 5
    Bard.Animations[AnimationType.Attack] = AttackAnimation
    ###
    BlockAnimation = Animation(AnimationType.Block, 1)
    BlockAnimation.FrameCels = [0]*5
    BlockAnimation.XPositions = [0]
    BlockAnimation.YPositions = [0]
    Bard.Animations[AnimationType.Block] = BlockAnimation
    ###
    OuchAnimation = Animation(AnimationType.Ouch, 1)
    OuchAnimation.ImageNumbers = [0]*13
    OuchAnimation.FrameCels = [0,1,2,3,4,5,6,7,8,9,10,11,12]
    #OuchAnimation.YPositions = [0, -5, -9, -11, -12, -11, -9, -5, 0, -2, -3, -2, 0]
    #OuchAnimation.YPositions = [-5, -10, -14, -15, -16, -15, -13, -9, -4, -6, -7, -6, -4]
    OuchAnimation.YPositions = [-25, -30, -34, -35,
                                -36, -35, -33, -29,
                                -24, -26, -27, -26,
                                -24]
##    OuchAnimation.XPositions = [-3,-1,1,3,
##                                5,7,9,11,
##                                12,13,14,15,16]
    OuchAnimation.XPositions = [-63,-61,-59,-57,
                                -55,-53,-51,-49,
                                -48,-47,-46,-45,-44]

    Bard.Animations[AnimationType.Ouch] = OuchAnimation
    ###
    DeadAnimation = Animation(AnimationType.Death, 1)
    DeadAnimation.RepeatFlag = 1
    Bard.Animations[AnimationType.Death] = DeadAnimation

    
Fighter = PlayerClass("Fighter", 12, 0)
BuildFighterClass(Fighter)
Cleric = PlayerClass("Cleric", 8, 6)
BuildClericClass(Cleric)
Mage = PlayerClass("Mage", 4, 8)
BuildMageClass(Mage)
Bard = PlayerClass("Bard", 6, 4)
BuildBardClass(Bard)
Summoner = PlayerClass("Summoner", 4, 8)
BuildSummonerClass(Summoner)
Ninja = PlayerClass("Ninja", 10, 0)
BuildNinjaClass(Ninja)
ClassesByName = {"Cleric":Cleric, "Mage":Mage, "Bard":Bard, "Fighter":Fighter, "Summoner":Summoner, "Ninja":Ninja}

def UnitTest():
    import pygame
    pygame.init()
    Surface = pygame.display.set_mode((800,600))
    print "--- Integrity check start ---"
    #Global.Bestiary.ValidateCritters()
    Global.Bestiary.ValidateEncounters()
    Global.Bestiary.CheckImageCase()
    print "--- Integrity check complete ---"
    print "If there are errors, please do what you can to fix them."
    print "Let's love this tree."
    print "Total monsters:", len(Global.Bestiary.AllSpecies.values())

if __name__ == "__main__":
    # If run from the command-line, do unit testing / integrity checking
    UnitTest()