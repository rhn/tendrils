"""
The combat screen!  The screen is divided into an arrow-swath (on the left), a battle area (upper right), and
a status panel (lower right).  The status panel is defined in the StatusPanel module.
This is the most important and most complicated of the screens in Tendrils.
"""
from Constants import *
from Utils import *
import Screen
import Global
import Resources
import time
import Music
import Critter
import StatusPanel
import Magic
from BattleSprites import *
import SpiralMeister
import Bard
import ChestScreen
import BattleResults
from DancingScreen import *

# The last tick of the system clock when arrows last moved.  (Arrows past the critical mark
# are no longer tracked by TSS, so we use the system clock to move them)
LastArrowTick = time.clock()

class EventTypes:
    """
    The BatteScreen keeps a list of "events" that are coming up - these are actions that will happen
    when AnimationCycle reaches some new value.  For instance, spells work by queueing damage events
    that trigger at the same time their animation finishes.  It is possible for events to be 
    delayed (if a Summon occurs, the AnimationCycle clock keeps ticking, but no events fire), or
    canceled (if someone is killed or incapacitated, their Spell and UseItem events go away).
    """
    Damage = 0 # somebody takes damage
    Projectile = 1 # projectile is fired
    Spell = 2 # spell is cast
    SummonMove = 3 #summoned critter starts moving
    Resurrect = 4 # somebody springs back to life
    UseItem = 5 # somebody finishes using an item, and we animate!
    Flee = 6
    Condition = 7 # Add or cure a condition like poison
    Turn = 8 # turn undead!
    ItemEffect = 9 # item animation is done, and it takes effect
    SpellAttach = 10
    GainMP = 11

class BattleScreen(DancingScreen):
    MinArrowCreateWait = 1500
    CanRewind = 0
    def __init__(self, App, MonsterRanks, Booty, RequestedSong = None, BossBattle = None, CanFlee = 1):
        """
        - MonsterRanks is a list of lists.  Each rank is a list of Critter instances.
        - Booty is a tuple of the form (BootyItems, SpecialItems, BootyType)
        - RequestedSong is always set
        - If BossBattle is set, we set the party's boss flag on victory.  (And other funky stuff, like
          the Spell of Confusion, can happen)
        """
        DancingScreen.__init__(self, App, MonsterRanks, RequestedSong)
        self.EventHandlers = {EventTypes.Damage: self.HandleDamageEvent,
                         EventTypes.Projectile: self.HandleProjectileEvent,
                         EventTypes.Spell: self.HandleSpellEvent,
                         EventTypes.UseItem: self.HandleUseItemEvent,
                         EventTypes.SummonMove: self.HandleSummonMoveEvent,
                         EventTypes.Resurrect: self.HandleResurrectEvent,
                         EventTypes.Flee: self.HandleFleeEvent,
                         EventTypes.Condition: self.HandleConditionEvent,
                         EventTypes.ItemEffect: self.HandleItemEffectEvent,
                         EventTypes.Turn: self.HandleTurnEvent,
                         EventTypes.SpellAttach: self.HandleSpellAttachEvent,
                         EventTypes.GainMP: self.HandleGainMPEvent,
                         }
        # AttachedSpellSprites: For spells and affects that "attach" to a player/monster.  
        self.AttachedSpellSprites = pygame.sprite.Group()
        BloodSprite.BloodBank = 0 # Reset the blood supply
        self.SongY = 450 # The y-coordinate where the song name appears (above our status panel)
        Global.BattleScreen = self
        self.Booty = Booty
        self.BossBattle = BossBattle
        self.CanFlee = CanFlee
        self.MousePosition = (0,0)
        # When a summoning is in progress (SummonSprite is not None), all battle events are "frozen" (moved
        # out of the queue).  When the summoning is complete, we move the events back in.  BattleFreezeTick
        # is the AnimationCycle where we froze everything.
        self.SummonSprite = None
        self.BattleFreezeTick = None
        self.ArrowSprites = pygame.sprite.RenderUpdates()
        self.HitTotals = {HitQuality.Miss:0, HitQuality.Poor:0, HitQuality.Good:0, HitQuality.Perfect:0}
        # The member BattleConclusion is set when the last monster (or last player) is killed.  Once BattleConclusion
        # is set, we end the battle a few ticks after.  We wait a few ticks so that the attack/death animation can
        # finish, so the player definitely knows how everything ended.            
        self.BattleConclusion = None        
        self.FinishOnCycle = None
        self.StatusPanel = StatusPanel.StatusPanel(self, 149, 448, 638, 138)
        self.SubPanes.append(self.StatusPanel)
        if self.BossBattle == "Dopefish":
            self.ShowGlowingText("DOPEFISH LIVES!", 250)
        else:
            self.ShowGlowingText("~ Get ready! ~", 250)
    def HandleGainMPEvent(self, Tuple):
        "Done by the Siphon spell."
        CritterSprite = Tuple[0]
        MP = int(Tuple[1])
        if CritterSprite.Critter.IsDead():
            return
        if MP>0:
            Gain = min(CritterSprite.Critter.MP + MP, CritterSprite.Critter.MaxMP) - CritterSprite.Critter.MP
            Color = Colors.Blue
            CritterSprite.Critter.MP += Gain
        else:
            OldMP = CritterSprite.Critter.MP
            CritterSprite.Critter.MP = max(CritterSprite.Critter.MP + MP, 0)
            Gain = abs(OldMP - CritterSprite.Critter.MP)
            Color = Colors.Orange
        self.DisplayBouncyNumber(CritterSprite.rect.center[0], CritterSprite.Y, int(Gain), Color)
        
    def QueueGainMPEvent(self, CritterSprite, MP, Delay):
        self.PendingEvents.append((EventTypes.GainMP, CritterSprite, MP, 
                            (self.AnimationCycle + Delay) % MaxAnimationCycle))
        
    def AttachSpellSprite(self, CritterSprite, SpellName):
        for Sprite in self.AttachedSpellSprites.sprites():
            if Sprite.SpellName == SpellName and Sprite.CritterSprite == CritterSprite:
                return # Already there!
        Sprites = Magic.AttachSpellSprites(CritterSprite, SpellName)
        if not Sprites:
            return
        for Sprite in Sprites:
            self.AttachedSpellSprites.add(Sprite)
            self.AddAnimationSprite(Sprite)
    def RemoveSpellSprite(self, CritterSprite, SpellName):
        for Sprite in self.AttachedSpellSprites.sprites():
            if Sprite.CritterSprite == CritterSprite and Sprite.SpellName == SpellName:
                Sprite.kill()
    def RemoveAllSpellSprites(self, CritterSprite):
        for Sprite in self.AttachedSpellSprites.sprites():
            if Sprite.CritterSprite == CritterSprite:
                Sprite.kill()        
    def Activate(self):
        """
        If the player gets to snipe, the sniping screen goes on top of us, and we
        are re-activated when the snipe screen goes away.  Clear out all the dead
        monsters (no need to animate, as that's alrady been done)
        """
        for MonsterSprite in self.MonsterSprites:
            if MonsterSprite.Critter.IsDead():
                MonsterSprite.image = Global.NullImage
                try:
                    self.AliveMonsters.remove(MonsterSprite.Critter)
                except:
                    pass
        self.CheckVictoryOrDeath()
        Screen.TendrilsScreen.Activate(self)
    def CheckVictoryOrDeath(self):
        "Check whether the battle is over"
        if self.BattleConclusion:
            return
        FoundLivingPlayer = 0
        for Player in Global.Party.Players:
            if Player.IsAlive():
                FoundLivingPlayer = 1
                break
        if not FoundLivingPlayer:
            self.BattleConclusion = "Lost"
            self.ShowGlowingText("DEFEAT!", 250)
        else:            
            if not len(self.AliveMonsters):
                self.BattleConclusion = "Won"
                self.ShowGlowingText("--- VICTORY! ---", 250)
                if self.BossBattle:
                    Global.Party.KilledBosses[(Global.Maze.Level, self.BossBattle)] = 1
                    # Special boss code:
                    if self.BossBattle == "Clippy":
                        Resources.PlayStandardSound("ClippyDies.wav")
                        Global.Party.KeyItemFlags["The Head of Clippy"] = 1 
                Global.Party.KillCount += len(self.Monsters)
        if self.BattleConclusion:
            # Stop the arrows!
            self.FinishOnCycle = (self.AnimationCycle + 200) % MaxAnimationCycle
            for Sprite in self.ArrowList:
                Sprite.kill()
            # Update performance log:
            Global.Party.BigBrother.UpdateSongPerformance(self.RequestedSong.SongPath, self.HitTotals)
    def DisplayBouncyNumber(self, X, Y, Number, Color = Colors.White):
        "Display a bouncy number, CENTERED around the given X coordinate"
        DigitWidth = 13 # hard coded :(  Using sprite widths looks bad, like this:  m   i   s   s
        NumberStr = str(Number)
        X = X - int(DigitWidth * len(NumberStr)/2.0)
        for Index in range(len(NumberStr)):
            Digit = NumberStr[Index]
            Sprite = BouncyNumber(Digit,X,Y,Color,Index*5)
            self.AddAnimationSprite(Sprite)
            X += Sprite.rect.width - 2 # Digitwidth
    def DrawBackground(self):
        "Draw the battle background-art"
        DancingScreen.DrawBackground(self)
    def StartBattle(self):
        "Prepare for battle!  Generate all the sprites, and START THE MUSIC!"
        if self.BossBattle == "Necromancers" or self.BossBattle == "Ultros":
            # CONFUSION spell:
            self.TryArrowInternal = self.TryArrow 
            self.TryArrow = self.TryArrowReversed
            self.MoveFreezeArrow = self.MoveFreezeArrowReversed
        DancingScreen.StartBattle(self)
        for Player in Global.Party.Players:
            Player.TurnedFlag = 0 # 'reload' the player's turning ability
            Player.CurrentAction = "" # nobody is busy now.
        self.StatusPanel.ReRender()
    def MoveFreezeArrowReversed(self, Arrow):
        "Copied from MoveFreezeArrow; hacked for confusion spell"
        ##########################################
        # If the arrow is complete, then trigger now:
        if Arrow.TicksLeft<=-Arrow.FreezeTime:
            self.HandleHitArrow(Arrow, Arrow.FreezeQuality, 1)
            return
        if Arrow.FreezeQuality == None and Arrow.TicksLeft > -HitQuality.MaxPoorTicks:
            return
        ##########################################
        # If the arrow's not complete and the key is up, then fail:
        Keys = Arrow.GetReversedKey()
        Pressed = pygame.key.get_pressed()
        for Key in Keys:
            if Pressed[Key]:
                return
        Button = Global.JoyConfig.Arrows[OppositeDirections[Arrow.Direction]]
        if Button!=None and Global.JoyButtons[Button]:
            return
        # Denied!
        self.HandleHitArrow(Arrow, HitQuality.Miss)
    def TryArrowReversed(self, Direction):
        "CONFUSION spell!"
        self.TryArrowInternal(OppositeDirections[Direction])
    def HandleHitArrow(self, Arrow, Quality, Force = 0):
        "Hit the specified arrow with the specified quality. (Overridden!)"
##        if Quality == HitQuality.Miss:
##            print "%.2f MISSED arrow: Arrow %s with quality %s: %s"%(time.clock(), Arrow.ID, Quality, Arrow)
##        else:
##            print "%.2f HIT arrow: Arrow %s with quality %s: %s"%(time.clock(), Arrow.ID, Quality, Arrow)
        # Handle the START of a freeze arrow:
        if Arrow.FreezeTime and (Quality != HitQuality.Miss) and not Force:
            Arrow.FreezeQuality = Quality
            FeedbackSprite = HitQualitySprite(Arrow.X, Arrow.Y, Quality)
            self.AddAnimationSprite(FeedbackSprite)
            return 
        Arrow.TriggeredFlag = 1
        self.HitTotals[Quality] += 1
        if Arrow.Direction < 5:
            SubDirection = Arrow.Direction
            Player = Global.Party.Players[Arrow.Direction - 1]
        else:
            SubDirection = random.choice(SubDirections[Arrow.Direction])
            Player = Global.Party.Players[SubDirection - 1]
        # Show a feedback sprite:
        if Arrow.FreezeTime:
            #special "Ok!" or "Denied!"
            if Quality == HitQuality.Miss:
                self.Streak = 0
                self.ComboSprite.Set(self.Streak)
                if Arrow.FreezeQuality != HitQuality.Miss:
                    FeedbackSprite = HitQualitySprite(Arrow.X, ArrowClass.CriticalY, HitQuality.FreezeDenied)
                else:
                    FeedbackSprite = HitQualitySprite(Arrow.X, ArrowClass.CriticalY, HitQuality.Miss)
            else:
                FeedbackSprite = HitQualitySprite(Arrow.X, Arrow.CriticalY, HitQuality.FreezeOk)
        else:
            self.ComboSprite.Set(self.Streak)
            FeedbackSprite = HitQualitySprite(Arrow.X, Arrow.Y, Quality)
        if Quality in (HitQuality.Miss, HitQuality.Poor):
            self.Streak = 0
        else:
            self.Streak += 1
        self.ComboSprite.Set(self.Streak)                
            
        self.AddForegroundSprite(FeedbackSprite)
        # You don't get your attacks when you're in the process of using items (or casting spells),
        # since otherwise the strategy of CONSTANTLY queueing up potions (which
        # is no fun) would be effective:
        if Arrow.IsOffense and (Player.CurrentAction or Player.IsIncapacitated()):
            return
        # Find the monster who's attacking/defending:
        if Arrow.IsOffense:
            Monster = self.GetTargetMonster()
        else:
            Monster = self.GetAttackingMonster()
        if not Monster:
            return            
        # Look up the monster and player sprites:
        MonsterSprite = self.MonsterSprites[self.Monsters.index(Monster)]
        PlayerSprite = self.PlayerSprites[SubDirection - 1]
        if Arrow.IsOffense:
            Attacker = Player
            Defender = Monster
            AttackerSprite = PlayerSprite
            DefenderSprite = MonsterSprite
            # If they missed an attack arrow, don't even animate it.  They just suck.
            if Quality == HitQuality.Miss:
                return
        else:
            DefenderSprite = PlayerSprite
            AttackerSprite = MonsterSprite
            Quality = HitQuality.ReversedQuality[Quality]
            # Pick a live player:
            if Player.IsDead():
                Player = self.GetTargetPlayer()
                PlayerSprite = self.GetSpriteForCritter(Player)
                DefenderSprite = PlayerSprite
            Attacker = Monster
            Defender = Player
        IsHit = Attacker.MeleeSwing(Defender, Quality)
        if IsHit:
            Damage = Attacker.MeleeDamage(Defender, Quality)
            if Arrow.FreezeTime:
                Damage *= 2 # Freeze arrows are super-attacks!
            Damage = Attacker.GetResistedDamage(Defender, Damage)
        else:
            Damage = 0
        AnimationCycles = AttackerSprite.AnimateAttack()
        Projectile = AttackerSprite.Critter.GetProjectile()
        # Use the projectile's speed to decide when to show damage:
        if Projectile:
            self.PendingEvents.append((EventTypes.Projectile, AttackerSprite, DefenderSprite, self.AnimationCycle + CritterSpriteClass.BaseAnimateDelay * Projectile[1]))
            ProjectileDelay = (Projectile[1] + Projectile[2]) * CritterSpriteClass.BaseAnimateDelay
            TriggerCycle = (self.AnimationCycle + ProjectileDelay)%MaxAnimationCycle
            # Special sfx:
            FileName = Attacker.GetAttackSound()
            if FileName:
                Resources.PlayStandardSound(FileName)
            
            # Process special effects like PoisonStrike now:
            self.HandleConditionStrikes(AttackerSprite, DefenderSprite, ProjectileDelay)
        else:
            # Process special effects like PoisonStrike now:
            self.HandleConditionStrikes(AttackerSprite, DefenderSprite, AnimationCycles)                
            TriggerCycle = (self.AnimationCycle + AnimationCycles)%MaxAnimationCycle
        self.PendingEvents.append((EventTypes.Damage, AttackerSprite, Damage, DefenderSprite, Colors.White, TriggerCycle))
    def HandleConditionStrikes(self, AttackerSprite, VictimSprite, Delay):
        "Handle poison and other conditions that can come with damage."
        Attacker = AttackerSprite.Critter
        Victim = VictimSprite.Critter
        if Attacker.HasPerk("Poison Strike"):
            if random.random() < 0.01 and not Victim.HasPerk("Poison Immune"):
                Time = 200
                self.QueueConditionEvent(AttackerSprite, VictimSprite, "Poison", Time, Delay)
        if Attacker.HasPerk("Sleep Strike"):
            if random.random() < 0.01 and not Victim.HasPerk("Sleep Immune"):
                Time = 700
                self.QueueConditionEvent(AttackerSprite, VictimSprite, "Sleep", Time, Delay)
        if Attacker.HasPerk("Silence Strike"):
            if random.random() < 0.01 and not Victim.HasPerk("Silence Immune"):
                Time = 300
                self.QueueConditionEvent(AttackerSprite, VictimSprite, "Silence", Time, Delay)
        if Attacker.HasPerk("Paralysis Strike"):
            if random.random() < 0.01 and not Victim.HasPerk("Paralysis Immune"):
                Time = 700
                self.QueueConditionEvent(AttackerSprite, VictimSprite, "Paralysis", Time, Delay)
        if Attacker.HasPerk("Stoning Strike"):
            if random.random() < 0.005 and not Victim.HasPerk("Stoning Immune"):
                Time = 2500
                self.QueueConditionEvent(AttackerSprite, VictimSprite, "Stone", Time, Delay)
        
    def QueueSpellAttachEvent(self, AttackerSprite, VictimSprite, Name, NewValue, Delay):
        self.PendingEvents.append((EventTypes.SpellAttach, AttackerSprite, VictimSprite,
                                   Name, NewValue, 
                                   (self.AnimationCycle + Delay) % MaxAnimationCycle))        
    def QueueConditionEvent(self, AttackerSprite, VictimSprite, Name, NewValue, Delay):
        self.PendingEvents.append((EventTypes.Condition, AttackerSprite, VictimSprite,
                                   Name, NewValue, 
                                   (self.AnimationCycle + Delay) % MaxAnimationCycle))
    def QueueItemEvent(self, User, Item, Target):
        Delay = 500 - User.DEX * 4
        if User.HasPerk("Haste"):
            Delay = int(Delay * HasteFactor)
        UserSprite = self.PlayerSprites[User.Index]
        TargetSprite = self.PlayerSprites[Target.Index]
        self.PendingEvents.append((EventTypes.UseItem, UserSprite, Item, TargetSprite,
                                   (self.AnimationCycle + Delay) % MaxAnimationCycle))
    def QueueResurrectEvent(self, DeadGuySprite, HealHP, Delay):
        self.PendingEvents.append((EventTypes.Resurrect, DeadGuySprite, HealHP, 
                                   (self.AnimationCycle + Delay) % MaxAnimationCycle))
    def QueueFleeEvent(self):
        Delay = 1200
        for Player in Global.Party.Players:
            if Player.HasPerk("Haste"):
                Delay = int(Delay * HasteFactor)
                break
        self.PendingEvents.append((EventTypes.Flee, (self.AnimationCycle + Delay) % MaxAnimationCycle))
        # Cancel any pending SPELLS or ITEM-USES.  The party is too busy retreating to do anything cool.
        for Event in self.PendingEvents[:]:
            for Player in Global.Party.Players:
                self.CancelActionsByPlayer(Player)
    def QueueTurnEvent(self, Player, Delay):
        self.PendingEvents.append((EventTypes.Turn, Player, (self.AnimationCycle + Delay) % MaxAnimationCycle))
    def CancelActionsByPlayer(self, CancelCritter):
        for Event in self.PendingEvents[:]:
            if isinstance(Event[1], Critter.Critter):
                TheCritter = Event[1]
            else:
                if hasattr(Event[1], "Critter"):
                    TheCritter = Event[1].Critter
                else:
                    continue
            if Event[0] == EventTypes.Spell and TheCritter == CancelCritter:
                self.PendingEvents.remove(Event) # Schnip!
            if Event[0] == EventTypes.UseItem and TheCritter == CancelCritter:
                self.PendingEvents.remove(Event) # Schnip!
            if Event[0] == EventTypes.Turn and TheCritter == CancelCritter:
                self.PendingEvents.remove(Event) # Schnip!
    def HandleSummonMoveEvent(self, Crud):
        if self.SummonSprite:
            self.SummonSprite.StartedFlag = 1
    def HandlePendingEvents(self):
        DamageDone = 0
        for Event in self.PendingEvents[:]:
            if Event[-1] != self.AnimationCycle:
                continue
            self.PendingEvents.remove(Event) # Processed!
            Handler = self.EventHandlers[Event[0]]
            if Event[0] == EventTypes.Damage:
                DamageDone = apply(Handler, (Event[1:],)) or DamageDone #avoid short-circuit!
            else:
                apply(Handler, (Event[1:],))
            if Event[0] == EventTypes.Condition:
                DamageDone = 1            
        if DamageDone:
            self.StatusPanel.ReRender()
            self.CheckVictoryOrDeath()
    def HandleUseItemEvent(self, Tuple):
        """
        Use an item.  Kicks off animation, and queue up an ItemEffect event
        that will do the actual change to HP, etc.
        """
        UserSprite = Tuple[0]
        Item = Tuple[1]
        TargetSprite = Tuple[2]
        if UserSprite.Critter.IsDead():
            # Refund the unused item:
            Global.Party.GetItem(Item.Name)
            return
        UserSprite.Critter.CurrentAction = ""
        # Animate:
        Resources.PlayStandardSound("Heal.wav")
        Magic.SpellAnimateCure(self, None, TargetSprite)
        # And queue event:
        TriggerCycle = (self.AnimationCycle + 99) % MaxAnimationCycle
        self.PendingEvents.append((EventTypes.ItemEffect, UserSprite, Item, TargetSprite, TriggerCycle))
    def HandleItemEffectEvent(self, Tuple):
        """
        Item animation is done, and now it takes effect:
        """
        self.StatusPanel.UseItemEffect(Tuple[0].Critter, Tuple[1], Tuple[2].Critter)
        # Awkward place for this, but...
        if Tuple[2].Critter.IsAlive():
            Tuple[2].AnimateStand()
    def HandleResurrectEvent(self, Tuple):
        Sprite = Tuple[0]
        HP = Tuple[1]
        if Sprite.Critter.IsDead():
            Sprite.Critter.HP = HP
            Sprite.AnimateStand()
    def HandleTurnEvent(self, Event):
        Player = Event[0]
        Player.CurrentAction = ""
        Resources.PlayStandardSound("Turn Undead.wav")
        # Do damage based on the character's level and wisdom.
        # Damage should be high (clerics are special and undead are
        # not common) but not overwhelming (this costs no MP, after all)
        Damage = 8 * (1.7 ** Player.Level)
        Damage *= (Player.WIS / float(MaxStat))
        Damage = int(max(Damage, 1))
        for MonsterSprite in self.MonsterSprites:
            Monster = MonsterSprite.Critter
            if Monster.IsAlive() and Monster.HasPerk("Undead"): # this line of code is cute!
                self.QueueDamageEvent(None, MonsterSprite, Damage, 1, Colors.White)
    def HandleSpellAttachEvent(self, Event):
        Target = Event[1]
        Name = Event[2]
        NewCount = Event[3]
        if Target.Critter.IsDead():
            return
        if NewCount==0:
            Target.Critter.SpellPerks[Name] = 0 # Dispel!
        else:
            OldCount = Target.Critter.SpellPerks.get(Name, 0)
            Target.Critter.SpellPerks[Name] = max(OldCount, NewCount)
        self.AttachSpellSprite(Target, Name)
    def HandleConditionEvent(self, Event):
        Target = Event[1]
        Name = Event[2]
        NewCount = Event[3]
        ###print "Condition:", Target, Name, NewCount
        if NewCount==0:
            Target.Critter.Perks[Name] = 0 # Cure!
        else:
            OldCount = Target.Critter.Perks.get(Name, 0)
            Target.Critter.Perks[Name] = max(OldCount, NewCount)
        if Target.Critter.IsIncapacitated():
            self.CancelActionsByPlayer(Target.Critter)
    def HandleFleeEvent(self, Event):
        Music.FadeOut()
        #Resources.PlayStandardSound("Flee.wav") #%%%
        Text = "<CENTER><CN:BRIGHTRED>PANIC!</C>\n\n\nYou flee head over heels!"
        self.App.ShowNewDialog(Text, Callback = self.EndBattle)
    def HandleSpellEvent(self, SpellEvent):
        CasterCritter = SpellEvent[0]
        Spell = SpellEvent[1]
        TargetCritter = SpellEvent[2] # Critter instance or None
        if CasterCritter.IsDead():
            return
        if CasterCritter.IsPlayer():
            CasterSprite = self.PlayerSprites[CasterCritter.Index]
        else:
            for MonsterSprite in self.MonsterSprites:
                if MonsterSprite.Critter == CasterCritter:
                    CasterSprite = MonsterSprite
                    break
        CasterCritter.MP = max(0, CasterCritter.MP - Spell.Mana)
        CasterCritter.CurrentAction = ""
        if CasterCritter.IsPlayer():
            # Single target:
            if Spell.Target == Magic.SpellTarget.OneMonster:
                TargetMonster = self.GetTargetMonster()
                TargetSprite = self.MonsterSprites[self.Monsters.index(TargetMonster)]
                apply(Spell.BattleEffectCode, (self, CasterSprite, TargetSprite))
                apply(Spell.AnimationCode, (self, CasterSprite, TargetSprite))
            elif Spell.Target == Magic.SpellTarget.MonsterRow:
                TargetMonster = self.GetTargetMonster()
                TargetSprite = self.MonsterSprites[self.Monsters.index(TargetMonster)]
                # Hit all the monster sprites with the same X as this one!
                for Sprite in self.MonsterSprites:
                    if Sprite.Critter.IsAlive() and Sprite.Rank == TargetSprite.Rank:
                        if Spell.BattleEffectCode:
                            apply(Spell.BattleEffectCode, (self, CasterSprite, TargetSprite))
                apply(Spell.AnimationCode, (self, CasterSprite, TargetSprite))
            elif Spell.Target == Magic.SpellTarget.EachMonster:
                if Spell.AnimationCode:
                    apply(Spell.AnimationCode, (self, CasterSprite, None))
                for Sprite in self.MonsterSprites:
                    if Sprite.Critter.IsAlive():
                        apply(Spell.BattleEffectCode, (self, CasterSprite, Sprite))                                    
            elif Spell.Target == Magic.SpellTarget.AllMonsters:
                if Spell.AnimationCode:
                    apply(Spell.AnimationCode, (self, CasterSprite, None))
                apply(Spell.BattleEffectCode, (self, CasterSprite, None))
            elif Spell.Target == Magic.SpellTarget.AllPlayers:
                if Spell.AnimationCode:
                    apply(Spell.AnimationCode, (self, CasterSprite, None))
                apply(Spell.BattleEffectCode, (self, CasterSprite, None))
            elif Spell.Target == Magic.SpellTarget.OnePlayer:
                TargetSprite = self.PlayerSprites[TargetCritter.Index]
                apply(Spell.BattleEffectCode, (self, CasterSprite, TargetSprite))
                apply(Spell.AnimationCode, (self, CasterSprite, TargetSprite))
        else:
            # MONSTER casting a spell:
            if Spell.Target == Magic.SpellTarget.OneMonster:
                # Choose a random player to hit:
                TargetPlayer = self.GetTargetPlayer()
                TargetSprite = self.PlayerSprites[TargetPlayer.Index]
                apply(Spell.BattleEffectCode, (self, CasterSprite, TargetSprite))
                apply(Spell.AnimationCode, (self, CasterSprite, TargetSprite))            
            elif Spell.Target == Magic.SpellTarget.OnePlayer:
                # Choose a friendly monster to cast on.
                Targets = []
                for MonsterSprite in self.MonsterSprites:
                    if (Spell.Name == "Raise" and MonsterSprite.Critter.IsDead()) or \
                       (MonsterSprite.Critter.IsAlive() and MonsterSprite.Critter.HP < MonsterSprite.Critter.MaxHP):
                        Targets.append(MonsterSprite)
                if not Targets:
                    return # Canceled!
                TargetSprite = random.choice(Targets)
                apply(Spell.BattleEffectCode, (self, CasterSprite, TargetSprite))
                apply(Spell.AnimationCode, (self, CasterSprite, TargetSprite))
            elif Spell.Target == Magic.SpellTarget.EachMonster or Spell.Target == Magic.SpellTarget.MonsterRow:
                # Hit every player!
                if Spell.AnimationCode:
                    apply(Spell.AnimationCode, (self, CasterSprite, None))
                if Spell.BattleEffectCode:
                    for Sprite in self.PlayerSprites:
                        if Sprite.Critter.IsAlive():
                            apply(Spell.BattleEffectCode, (self, CasterSprite, Sprite))
                
    def HandleDamageEvent(self, DamageEvent):
        AttackerSprite = DamageEvent[0]
        if isinstance(AttackerSprite, Critter.Critter):
            Attacker = AttackerSprite
            AttackerSprite = self.GetSpriteForCritter(Attacker)
        else:
            if AttackerSprite:
                Attacker = AttackerSprite.Critter
            else:
                Attacker = None
        Damage = DamageEvent[1]
        VictimSprite = DamageEvent[2]
        if isinstance(VictimSprite, Critter.Critter):
            Victim = VictimSprite
            VictimSprite = self.GetSpriteForCritter(Victim)
        else:
            Victim = VictimSprite.Critter
        Color = DamageEvent[3]
        if self.BattleConclusion:
            return # Battle is over, stop handling events!
        # If the victim is dead, and it's a melee attack, select a new victim:
        # This is a little iffy, because animations may or may not appear to target a particular enemy.
        if Victim.IsDead():
            if Attacker and Attacker.IsPlayer() and Attacker.CanSwitchTargets():
                Monster = self.GetTargetMonster()
                VictimSprite = self.MonsterSprites[self.Monsters.index(Monster)]
                Victim = VictimSprite.Critter
            else:
                return # No beating a dead horse!
        if Damage > 0:
            # AC applise here:
            Damage = Victim.BlockDamageWithAC(Damage)
            # STONESKIN applies here:
            if Victim.HasPerk("Stoneskin"):
                Damage = max(1, int(Damage * 0.60))
            # BLOODLUST applies here:
            if Attacker and Attacker.HasPerk("Bloodlust"):
                Damge = int(Damage * 1.4)
            if Victim.IsInvulnerable():
                Damage = 0
            Victim.HP -= Damage
            VictimSprite.AnimateOuch(Damage, Color)
            # Make some noises!
            FileName = None
            if Attacker:
                # Don't play a special sound now; play species-specific sounds when the shot is fired.
                if Attacker.Species.Projectile:
                    FileName=None
                else:
                    FileName = Attacker.GetAttackSound()
            if not FileName:
                FileName = random.choice(("Hit.wav","Hit2.wav","Hit3.wav","Hit4.wav"))
            Resources.PlayStandardSound(FileName)
            # Taking damage wakes you up:
            if Victim.Perks.get("Sleep", None):
                Victim.Perks["Sleep"] = 0
                if Victim.IsPlayer():
                    self.StatusPanel.ReRender()
        elif Damage < 0:
            if Victim.IsAlive():
                HealedAmount = min(Victim.MaxHP - Victim.HP, abs(Damage))
                HealedAmount = int(HealedAmount)
                self.DisplayBouncyNumber(VictimSprite.rect.center[0], VictimSprite.rect.top, HealedAmount, Color)
                Victim.HP += HealedAmount
        else:
            VictimSprite.AnimateDodge()
            Resources.PlayStandardSound("Miss.wav")
        if Victim.HP <= 0:
            self.ProcessDeath(VictimSprite)
        return 1
    def ProcessDeath(self, VictimSprite):
        VictimSprite.Critter.RemoveAttachedSpells()
        VictimSprite.AnimateDeath()
        self.RemoveAllSpellSprites(VictimSprite)
        if VictimSprite.Critter.IsPlayer():
            VictimSprite.Critter.CurrentAction = ""
        self.CheckVictoryOrDeath()
        if VictimSprite.Critter in self.AliveMonsters:
            self.AliveMonsters.remove(VictimSprite.Critter)
    def EndBattle(self, Dummy = None):
        AliveFlag = 0
        for Player in Global.Party.Players:
            Player.CurrentAction = ""
            if Player.IsAlive():
                AliveFlag = 1
        self.App.PopScreen(self)
        if not AliveFlag:
            Global.App.ReturnToTitle()
    def HandleLevelUp(self, Dummy = None):
        TextItems = []
        # Keep calling HandleLevelUp as long as there are players who can level up:
        for Player in Global.Party.Players:            
            if Player.EXP > Player.GetEXPToLevel():
                self.App.LevelPlayerUp(Player, self.HandleLevelUp)
                return
        self.HandlePostBattleEvents()
    def RollCreditsBaby(self):
        Global.App.DoVictory()
        Global.App.PopScreen(self)
    def StartMotherBrain2(self):
        Monsters = [[Global.Bestiary.GetCritter("Brain2"),]]
        Global.App.BeginBattle(Monsters, ({},{},0), BossBattleName = "MotherBrain2", SongFileName="FFVI - Grand Finale.mp3", CanFlee = 0)
        Global.App.PopScreen(self)
    def HandlePostBattleEvents(self):
        """
        Called after battle-stats and level-up, but before opening chest.  Mostly used as a dialog
        hook for boss levels.
        """
        if self.BossBattle == "Dragons":
            Str = "The twin dragons are defeated, and the town of Skara Brae is safe.\n\n(You unlocked the <CN:ORANGE>FREE PLAY</c> mini-game!)"
            Global.MemoryCard.Set("MiniGameFreePlay")
            Global.App.ShowNewDialog(Str, Callback = self.HandleGetBooty)
            return 1
        if self.BossBattle == "L4Boss":
            Str = "The great stone golem falls dead at your feet.\n\nIn its innards, you discover a <CN:BRIGHTBLUE>holy sigil</C>.  Clerics can now cast the spells <CN:BRIGHTBLUE>Stoneskin</C> and <CN:BRIGHTBLUE>Repel</C>!"
            Global.Party.FoundClericSpells[5]=1
            Global.Party.FoundClericSpells[6]=1
            Global.App.ShowNewDialog(Str, Callback = self.HandleGetBooty)
            return 1
        if self.BossBattle == "MotherBrain2":
            Str = "<CN:ORANGE><BIG>KABOOM!</BIG></CN>\n\nAn explosion consumes the quivering mass that was once Mother Brain, destroyer of worlds.\n\n<BIG><CN:BRIGHTGREEN>YOU HAVE WON!"
            Global.App.ShowNewDialog(Str, Callback = self.RollCreditsBaby)
        if self.BossBattle == "Dopefish":
            BoostMagicStr = ""
            for Index in range(11):
                BoostMagicStr += Global.Party.LearnSpell("Mage",Index)
            for Index in range(10):
                BoostMagicStr += Global.Party.LearnSpell("Cleric",Index)
            for Index in range(10):
                BoostMagicStr += Global.Party.LearnSpell("Summoner",Index)
            if not BoostMagicStr:
                BoostMagicStr = "<CN:YELLOW>[ However, your well-prepared magic users learned no new spells ]"
            Str = "The second-dumbest creature in the universe has been vanquished.\n\nA strange old man crawls out of the fish's huge belly.  He says:<CN:ORANGE>HOORAY!  FREE AT LAST!</C>\n\nThe grateful wizard reviews some magic with you.\n\n%s"%BoostMagicStr
            Global.App.ShowNewDialog(Str, Callback = self.HandleGetBooty)
        # We're not doing anything special, so go straight to booty:
        self.HandleGetBooty()
    def HandleGetBooty(self, Dummy = None):
        # The third entry in the booty tuple is 0 for no chest, 1 for a random chest,
        # and 2 for a fixed-position chest (trap determined by x,y,z).
        if self.Booty[2]:
            self.App.AskDisarmChest(self.Booty[0], self.Booty[1], self.Booty[2])
            self.App.PopScreen(self)
            return
        # Still show the "you get stuff" dialog if there's no chest but there are some
        # items to get:
        GetStuff = 0
        if len(self.Booty[0].keys()):
            GetStuff = 1
        # Gold is already looted:
        try:
            del self.Booty["gold"]
        except:
            pass
        for Key in self.Booty[1].keys():
            if Key.lower()!="gold":
                GetStuff = 1
        if GetStuff:
            #def GetTreasureChestStuff(ChestItems, ChestSpecial, ChestType, SpecialLootString = None):
            ChestScreen.GetTreasureChestStuff(self.Booty[0], self.Booty[1], 1, "You have gained treasure:\n\n")
        self.App.PopScreen(self)
    def HandleVictory(self):
        Music.FadeOut()
        # Battle spells wear off now:
        for Player in Global.Party.Players:
            Player.RemoveAttachedSpells()
        if self.BossBattle == "MotherBrain1":
            Str = "<BIG><CENTER>...!?"
            Global.App.ShowNewDialog(Str, Callback = self.StartMotherBrain2)
            return
            
        Header = "<CN:PURPLE><CENTER><BIG>Victory!</BIG></C></CENTER>\n" 
        EXP = 0
        Gold = 0
        for Monster in self.Monsters:
            EXP += Monster.GetEXPValue()
            Gold += Monster.GetGoldValue()
        Multiplier = self.GetEXPMultiplier()
        Footer = "\n<CN:GREY>EXP Multiplier: %.1f</C>\n"%Multiplier
        EXP = int(EXP * Multiplier)
        Footer += "EXP Gained: %d\n"%EXP
        for Player in Global.Party.Players:
            if Player.IsAlive():
                Player.EXP += EXP
        # You only get gold now if there's no chest:
        if self.Booty[2] == 0:
            Footer += "You collected <CN:YELLOW>%d zenny</C>.\n"%Gold
            Global.Party.Gold += Gold
        else:
            if not self.Booty[1].has_key("Gold") and not self.Booty[1].has_key("gold"):
                self.Booty[1]["Gold"] = Gold
        Screen = BattleResults.BattleFeedback(self.HitTotals, self.HandleLevelUp, Header, Footer)
        Global.App.PushNewScreen(Screen)
        #self.App.ShowNewDialog(Text, Callback = self.HandleLevelUp)
    def GetEXPMultiplier(self):
        "Assign a multiplier to earned-exp, based on the player's performance"
        Rating = BattleResults.GetRating(self.HitTotals)
        return BattleResults.EXPMultipliers[Rating]
       
    def HandleDefeat(self):
        Music.FadeOut()
        Resources.PlayStandardSound("Defeat.wav")
        Text = """The brave party of adventurers have been wiped out, and the hopes of thousands have perished with them."""
        self.App.ShowNewDialog(Text, Callback = self.EndBattle)
        
        #self.App.ShowDialogScreen(Text, Callback = self.EndBattle)
    def HandleConditions(self):
        # Handle conditions like poison, sleep, paralysis.
        # Conditions wear off a little bit, and poison inflicts damage.
        # (Also, Regen takes effect now!  And bard powers fire now!)
        for MonsterSprite in self.MonsterSprites:
            Monster = MonsterSprite.Critter
            if Monster.IsAlive():
                Monster.MitigateConditions()
            if Monster.Perks.get("Poison"):
                self.QueueDamageEvent(None, MonsterSprite, Monster.GetPoisonDamage(), 0, Colors.Purple)
            if Monster.HasPerk("Regen"):
                self.QueueDamageEvent(None, MonsterSprite, -Monster.GetPoisonDamage(), 0, Colors.Green)
        for PlayerSprite in self.PlayerSprites:
            Player = PlayerSprite.Critter
            if Player.IsAlive():
                Player.MitigateConditions()
            if Player.Perks.get("Poison"):
                self.QueueDamageEvent(None, PlayerSprite, Player.GetPoisonDamage(), 0, Colors.Purple)
            if Player.HasPerk("Regen"):
                self.QueueDamageEvent(None, PlayerSprite, -Player.GetPoisonDamage(), 0, Colors.Green)
        Bard.ApplyBardPower(Global.Party)
        self.StatusPanel.ReRender() # This might not be necessary, but it's not worth keeping track.
    def CastMonsterSpells(self):
        if self.SummonSprite:
            return
        for Monster in self.AliveMonsters:
            if Monster.CurrentAction:
                continue
            if random.random() > 0.9 and Monster.CanCast(): # do somewhat rarely
                SpellName = Monster.Species.ChooseSpell()
                if not SpellName:
                    continue
                Spell = Magic.GetSpell(SpellName)
                if not Spell:
                    print "** ERROR: Unknown spell '%s'"%Spell
                if Monster.MP < Spell.Mana:
                    print "Not enough MP:", Monster.MP, Spell.Mana
                    continue
                TriggerTime = (self.AnimationCycle + Monster.GetCastingTime(Spell))%MaxAnimationCycle
                Tuple = (EventTypes.Spell, Monster, Spell, None, TriggerTime)
                self.PendingEvents.append(Tuple)
                Monster.CurrentAction = "Cast"
                #self.QueueSpellEvent(
    def HandleLoop(self):
        if not self.PauseFlag:        
            self.AnimationCycle+=1
            if (self.AnimationCycle>=MaxAnimationCycle):
                self.AnimationCycle=0
            if self.AnimationCycle%1000 == 0 and self.FinishOnCycle==None:
                self.HandleConditions()
            if self.AnimationCycle%100 == 0 and self.FinishOnCycle==None:
                self.CastMonsterSpells()
            if not self.SummonSprite:                
                if self.AnimationCycle == self.FinishOnCycle:
                    # All pending actions cancel:
                    for Player in Global.Party.Players:
                        Player.CurrentAction = ""
                    if self.BattleConclusion == "Won":
                        self.HandleVictory()                
                    else:
                        self.HandleDefeat()
                    return
        else:
            time.sleep(0.05)
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface) 
        self.ArrowSprites.clear(self.Surface,self.BackgroundSurface) 
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface) 
        if self.SummonSprite:
            self.CheckSummonFinish()
        # Processing if the battle isn't decided yet:        
        if not self.BattleConclusion and not self.SummonSprite:
            self.MoveArrows()        
        self.HandleEvents() # pygame events
        if not self.PauseFlag:
            for Sprite in self.AllSprites.sprites():
                Sprite.Update(self.AnimationCycle)
            for Pane in self.SubPanes:            
                Pane.HandleLoop()
            self.HandlePendingEvents() # animation starter events.  Do this LAST, in case we triggered one with no delay
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        if not self.PauseFlag:
            DirtyRects = self.ArrowSprites.draw(self.Surface) 
            Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)
    def FreezeBattleEvents(self):
        """
        During a summoned-monster animation, no spells are cast and no arrows move.  We move all the
        spell-cast and item-use events into a separate queue, and log the start time
        """
        self.BattleFreezeTick = self.AnimationCycle
        for Event in self.PendingEvents[:]:
            if Event[0] in (EventTypes.Spell, EventTypes.UseItem, EventTypes.Turn):
                self.FrozenEvents.append(Event)
                self.PendingEvents.remove(Event)
                print "FROZE this event:", Event #%%%
    def ThawBattleEvents(self):
        """
        Update the trigger-times of our frozen events, and dump them back into the queue.
        """
        for Event in self.FrozenEvents:
            MomoTaroTime = (self.AnimationCycle - self.BattleFreezeTick)
            if (MomoTaroTime < 0):
                MomoTaroTime += MaxAnimationCycle
            print "Event time %s + momotaro %s"%(Event[-1], MomoTaroTime)
            Event = list(Event)
            Event[-1] = (Event[-1] + MomoTaroTime) % MaxAnimationCycle
            Event = tuple(Event)
            if Event[0] in (EventTypes.Spell, EventTypes.UseItem, EventTypes.Turn):
                print "THAWED this event:", Event
                self.PendingEvents.append(Event)
        self.FrozenEvents = []
    def StartSummon(self, SummonSprite):
        if self.BattleConclusion:
            return # No summoning, the battle's ending!
        self.SummonSprite = SummonSprite
        self.AddAnimationSprite(self.SummonSprite)
        # Hide arrows, freeze casting action:
        self.Arrows = {}
        self.ArrowList = []
        for ArrowSprite in self.ArrowSprites.sprites():
            ArrowSprite.kill()
        self.FreezeBattleEvents()
        # Kick off motion in a few moments, but first show some glowy text o' doom:
        StartCycle = (self.AnimationCycle + 200)%MaxAnimationCycle
        Event = (EventTypes.SummonMove, StartCycle)
        self.ShowGlowingText("Summoned %s!"%SummonSprite.Name, 250)
        self.ShowGlowingText("Follow with the mouse pointer!", 300)
        self.PendingEvents.append(Event)
    def CheckSummonFinish(self):
        if not self.SummonSprite.Done:
            return # Still going!
        Damage = self.SummonSprite.GetDamage()
        self.ThawBattleEvents()
        if self.SummonSprite.Spell.Target == Magic.SpellTarget.AllPlayers:
            # Target is players: Heal!
            for PlayerSprite in self.PlayerSprites:
                if PlayerSprite.Critter.IsAlive():
                    self.QueueDamageEvent(None, PlayerSprite, -abs(Damage), 1, Colors.Green)
        else:
            # Do damage!
            DamageDealt = 0
            for MonsterIndex in range(len(self.Monsters)):
                Monster = self.Monsters[MonsterIndex]
                if Monster.IsAlive():
                    Damage = Damage + random.randrange(-5,6)
                    Damage = max(Damage, 1)
                    DamageDealt += Damage
                    self.QueueDamageEvent(None, self.MonsterSprites[MonsterIndex], Damage, 0)
            # Some special effects:
            print "SummonSprite name:", self.SummonSprite.Name
            # Mr. Sandman causes SLEEP:
            if self.SummonSprite.Name == "Mr. Sandman":
                for MonsterIndex in range(len(self.Monsters)):
                    Monster = self.Monsters[MonsterIndex]
                    if Monster.IsAlive() and not Monster.HasPerk("Sleep Immune"):
                        self.QueueConditionEvent(None, self.MonsterSprites[MonsterIndex], "Sleep",
                                                 100 + Damage*10, 1)
            # Metroid HEALS the party:
            if self.SummonSprite.Name == "Metroid":
                HealDamage = DamageDealt / 10
                print "Heal %s"%HealDamage
                for PlayerSprite in self.PlayerSprites:
                    if PlayerSprite.Critter.IsAlive():
                        self.QueueDamageEvent(None, PlayerSprite, -HealDamage, 10, Colors.Orange)
            # Phoenix RAISES party members:
            if self.SummonSprite.Name == "Phoenix":
                for PlayerSprite in self.PlayerSprites:
                    if PlayerSprite.Critter.IsDead():
                        self.QueueResurrectEvent(PlayerSprite, PlayerSprite.Critter.MaxHP / 4, 5)
        self.SummonSprite = None
        self.CheckVictoryOrDeath()
        # Sanity-check: if finish-on-cycle is very far away, make it soon:
        if (self.FinishOnCycle > self.AnimationCycle):
            TimeTillFinish = self.FinishOnCycle - self.AnimationCycle
        else:
            TimeTillFinish = self.FinishOnCycle + (MaxAnimationCycle - self.AnimationCycle)
        if TimeTillFinish > 150:
            self.FinishOnCycle = (self.AnimationCycle + 150) % MaxAnimationCycle
    def HandleKeyPressed(self, Key):
        # Ignore keypresses if winding down:
        if Key == Keystrokes.Debug:
            self.AliveMonsters = []
            self.CheckVictoryOrDeath()
            return #%%%
        if self.BattleConclusion or self.SummonSprite:
            # Ignore keystrokes!
            return
        Result = DancingScreen.HandleKeyPressed(self, Key)
        if not Result:
            self.StatusPanel.HandleKeyPressed(Key)
    def CommandCallback(self, CommandTuple):
        """
        This function is called by the StatusPanel when the user casts a spell.
        """
        if CommandTuple[0]=="Spell":
            self.CommandCallbackSpell(CommandTuple[1:])
        elif CommandTuple[0] == "Turn":
            self.CommandCallbackTurn(CommandTuple[1])
        else:
            print "** Unknown CommandCallback!", CommandTuple
    def CommandCallbackTurn(self, Player):
        "Start turning undead."
        Player.CurrentAction = "Turn"
        TurningTime = 1000
        if Player.HasPerk("Haste"):
            TurningTime = int(TurningTime * HasteFactor)
        Player.TurnedFlag = 1
        self.StatusPanel.ReRender()
        self.QueueTurnEvent(Player, TurningTime)
    def CommandCallbackSpell(self, Tuple):
        # Tuple: Caster critter, spell object, [target critter]
        if Tuple[0].IsPlayer():
            Tuple[0].CurrentAction = "Cast:%s"%Tuple[1].Name
            self.StatusPanel.ReRender()
        TriggerTime = (self.AnimationCycle + Tuple[0].GetCastingTime(Tuple[1])) % MaxAnimationCycle
        Event = (EventTypes.Spell, Tuple[0], Tuple[1], Tuple[2], TriggerTime)
        self.PendingEvents.append(Event)
    def HandleMouseMoved(self,Position,Buttons,LongPause = 0):
        "Track mouse position, for summonings"
        self.MousePosition = Position

if PSYCO_ON:
    psyco.bind(BattleScreen.HandleHitArrow)
    psyco.bind(BattleScreen.HandleLoop)
        