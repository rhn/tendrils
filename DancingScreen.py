"""
This is the dancing screen base class.  It handles arrow movement,
hits, combos, and so on.  The battle screen is a more sophisticated
subclass.  The free-play dance screen is a near-identical subclass.
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

class DancingScreen(Screen.TendrilsScreen):
    ArrowAreaWidth = 150 
    # Up, down, left, right:
    PlayerCoords = [(630,40),(630,330),(560,185),(710,185)]
    BattleAreaHeight = 450
    StatusAreaHeight = 150
    # Positions of monster ranks (from back to front)
    MidRank1 = 220
    FrontRank2 = 350
    RearRank2 = 200
    RearRank3 = 170
    MidRank3 = 285
    FrontRank3 = 400
    RearmostRank4 = 160
    RearRank4 = 260
    FrontRank4 = 360
    FrontmostRank4 = 460
    MinArrowCreateWait = 1500
    CanRewind = 1
    def __init__(self, App, MonsterRanks, RequestedSong = None):
        """
        - MonsterRanks is a list of lists.  Each rank is a list of Critter instances.
        - Booty is a tuple of the form (BootyItems, SpecialItems, BootyType)
        - RequestedSong is always set
        - If BossBattle is set, we set the party's boss flag on victory.  (And other funky stuff, like
          the Spell of Confusion, can happen)
        """
        Screen.TendrilsScreen.__init__(self,App)
        self.EventHandlers = {EventTypes.Damage: self.HandleDamageEvent,
                         EventTypes.Projectile: self.HandleProjectileEvent,
                         }
        self.SilentFlag = 0
        self.SongY = 450 # The y-coordinate where the song name appears (above our status panel)
        self.BattleFreezeTick = None
        self.Arrows = {} # dictionary: Arrow-ID to arrow sprite
        self.ArrowList = [] # Arrows listed from early to late
        self.PauseFlag = 0
        if type(RequestedSong) == types.StringType:
            RequestedSong = Global.MusicLibrary.GetBattleSong(RequestedSong)
        if not RequestedSong:
            RequestedSong = Global.MusicLibrary.GetBattleSong()
        self.RequestedSong = RequestedSong
        self.ArrowSprites = pygame.sprite.RenderUpdates()
        self.DeepSprites =pygame.sprite.RenderUpdates()        
        self.HitTotals = {HitQuality.Miss:0, HitQuality.Poor:0, HitQuality.Good:0, HitQuality.Perfect:0}
        # The member BattleConclusion is set when the last monster (or last player) is killed.  Once BattleConclusion
        # is set, we end the battle a few ticks after.  We wait a few ticks so that the attack/death animation can
        # finish, so the player definitely knows how everything ended.            
        self.BattleConclusion = None        
        self.FinishOnCycle = None
        # PendingEvents is a list of animations to perform.  When a creature starts its attack, we
        # kick off the attack animation in the Sprite, and make a note that we will apply damage at the
        # appropriate time.  Attack animations are not interruptible by ANYTHING except for other attack
        # animations (it's possible to do a stuttered swi-swi-swing of a sword, but not to get knocked out
        # of a sword swing).  Once the attack animation starts, an attack animation is going to be shown in
        # its entirety, and damage is going to happen.  Entries in this list have the form
        # (event type, ..., trigger time)
        self.PendingEvents = []
        self.FrozenEvents = []
        self.MonsterRanks = MonsterRanks
        self.Monsters = [] # A flat list of all monsters
        for Rank in MonsterRanks:
            self.Monsters.extend(Rank)
        self.AliveMonsters = self.Monsters[:] # Dynamic list of living monsters
        # for "judge mode":
        self.Whiffs = []
        self.WaitTicksAfterUnpause = 0
    def AnimateParticles(self, X, Y, ShrapnelClass, ParticleCount=20):
        for Index in range(ParticleCount):
            Sprite = ShrapnelClass(X+random.randrange(-5,6),Y+random.randrange(-5,6),25)
            self.AllSprites.add(Sprite)
            self.AnimationSprites.add(Sprite)
    def DrawBattleBackground(self):
        Image = None
        # If its a StepMania song, it may have its very own background image:
        try:
            Image = pygame.image.load(self.RequestedSong.ImagePath).convert()
            Image = pygame.transform.scale(Image, (650, 435))
        except:
            pass ##traceback.print_exc() # %%%
        if not Image:
            try:
                Image = Resources.GetBattleBackground()
                Image = pygame.transform.scale(Image, (650, 435))
            except:
                print "** warning: Missing a battle-background!"
                traceback.print_exc()
        if Image:
            BattleBackgroundSprite = GenericImageSprite(Image, self.ArrowAreaWidth + 1, 0)
            #self.AddBackgroundSprite(BattleBackgroundSprite)
            self.DeepSprites.add(BattleBackgroundSprite)
        # Panel border:
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc,"StatusPanel.png"))
        BigBiff = GenericImageSprite(Image, 135, 0)
        self.DeepSprites.add(BigBiff,) 
        self.RenderLHSBack()
        print "BattleBack drawn...!"
    def RenderLHSBack(self):
        TileIndex = Resources.Tiles.get(Global.Maze.Level, 1)
        Image1 = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png")%TileIndex)
        Surface = pygame.Surface((138, 600))
        Y = -5
        X = -5
        while (Y<600):
            X = -5
            while (X<140):
                Surface.blit(Image1, (X,Y))
                X += Image1.get_rect().width
            Y += Image1.get_rect().height
        self.LHSBackSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(self.LHSBackSprite)       
    def DrawBackground(self):
        "Draw the battle background-art"
        print "DrawBackground()"
        self.DrawBattleBackground()
        # Draw the arrow area's edge:
        #BattleBoxSprite = BoxSprite(self.ArrowAreaWidth, 0, 1, self.Height)
        #self.AddBackgroundSprite(BattleBoxSprite)
        # Draw the status bar edge:
        #BattleBoxSprite = BoxSprite(self.ArrowAreaWidth, self.BattleAreaHeight, self.Width, self.Height)
        #self.AddBackgroundSprite(BattleBoxSprite)
        # Draw the critical line that arrows cross:
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "CriticalLine"))
        ArrowLineSprite = GenericImageSprite(Image, 0, ArrowClass.CriticalY - 1)
        #ArrowLineSprite = BoxSprite(0, ArrowClass.CriticalY, self.ArrowAreaWidth, 1)
        self.AddBackgroundSprite(ArrowLineSprite)
        # Ghost lines:
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "GhostUp.png"))
        Sprite = GenericImageSprite(Image, ArrowXByDirection[1], ArrowClass.CriticalY)
        Sprite.rect.left -= Sprite.rect.width / 2
        Sprite.rect.top -= Sprite.rect.height / 2
        self.AddBackgroundSprite(Sprite)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "GhostDown.png"))
        Sprite = GenericImageSprite(Image, ArrowXByDirection[2], ArrowClass.CriticalY)
        Sprite.rect.left -= Sprite.rect.width / 2
        Sprite.rect.top -= Sprite.rect.height / 2
        self.AddBackgroundSprite(Sprite)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "GhostLeft.png"))
        Sprite = GenericImageSprite(Image, ArrowXByDirection[3], ArrowClass.CriticalY)
        Sprite.rect.left -= Sprite.rect.width / 2
        Sprite.rect.top -= Sprite.rect.height / 2
        self.AddBackgroundSprite(Sprite)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "GhostRight.png"))
        Sprite = GenericImageSprite(Image, ArrowXByDirection[4], ArrowClass.CriticalY)
        Sprite.rect.left -= Sprite.rect.width / 2
        Sprite.rect.top -= Sprite.rect.height / 2
        self.AddBackgroundSprite(Sprite)
    def DrawPlayers(self):
        "At battle start: Draw the 4 players"
        self.PlayerSprites = []
        for PlayerIndex in range(4):
            Player = Global.Party.Players[PlayerIndex]
            if not Player:
                continue
            Coords = self.PlayerCoords[PlayerIndex]
            PlayerSprite = CritterSpriteClass(self, Player, Coords[0], Coords[1]) #PlayerSpriteClass(Player, self.PlayerCoords[PlayerIndex])
            if Player.IsDead():
                PlayerSprite.PlayDead()
            self.AddForegroundSprite(PlayerSprite)
            self.PlayerSprites.append(PlayerSprite)
    def DrawMonsters(self):
        "At battle start: Create sprites for all monsters"
        self.MonsterSprites = []
        if len(self.MonsterRanks)==1:
            self.DrawMonsterRank(self.MonsterRanks[0], self.MidRank1, 0)
        elif len(self.MonsterRanks)==2:
            self.DrawMonsterRank(self.MonsterRanks[0], self.RearRank2, 0)
            self.DrawMonsterRank(self.MonsterRanks[1], self.FrontRank2, 1)            
        elif len(self.MonsterRanks)==3:
            self.DrawMonsterRank(self.MonsterRanks[0], self.RearRank3, 0)
            self.DrawMonsterRank(self.MonsterRanks[1], self.MidRank3, 1)
            self.DrawMonsterRank(self.MonsterRanks[2], self.FrontRank3, 2)
        elif len(self.MonsterRanks)==4:
            self.DrawMonsterRank(self.MonsterRanks[0], self.RearmostRank4, 0)
            self.DrawMonsterRank(self.MonsterRanks[1], self.RearRank4, 1)
            self.DrawMonsterRank(self.MonsterRanks[2], self.FrontRank4, 2)
            self.DrawMonsterRank(self.MonsterRanks[3], self.FrontmostRank4, 3)
        else:
            self.DrawMonsterRank(self.MonsterRanks[0], 160, 0)
            self.DrawMonsterRank(self.MonsterRanks[1], 230, 1)
            self.DrawMonsterRank(self.MonsterRanks[2], 300, 2)
            self.DrawMonsterRank(self.MonsterRanks[3], 370, 3)
            self.DrawMonsterRank(self.MonsterRanks[4], 440, 4)
    def DrawMonsterRank(self, Monsters, X, RankNumber):
        "At battle start: Draw one rank (column) of monsters"
        for MonsterIndex in range(len(Monsters)):
            Monster = Monsters[MonsterIndex]
            Y = (self.BattleAreaHeight - 80) * ((MonsterIndex+1) / float(len(Monsters)+1))
            Y = int(Y) + 5
            MonsterSprite = CritterSpriteClass(self, Monster, X, Y) 
            MonsterSprite.Rank = RankNumber
            self.MonsterSprites.append(MonsterSprite)
            self.AddForegroundSprite(MonsterSprite)
    def StartBattle(self):
        "Prepare for battle!  Generate all the sprites, and START THE MUSIC!"
        self.DrawBackground()
        self.DrawPlayers()
        self.DrawMonsters()
        self.Streak = 0
        self.ComboSprite = ComboSprite(self.Streak, 75, 180)
        self.AddAnimationSprite(self.ComboSprite)
        self.SummonSong(self.RequestedSong)
    def MoveFreezeArrow(self, Arrow):
        ##########################################
        # If the arrow is complete, then trigger now:
        if Arrow.TicksLeft<=-Arrow.FreezeTime:
            self.HandleHitArrow(Arrow, Arrow.FreezeQuality, 1)
            return
        if Arrow.FreezeQuality == None and Arrow.TicksLeft > -HitQuality.MaxPoorTicks:
            return
        ##########################################
        # If the arrow's not complete and the key is up, then fail:
        Keys = Arrow.GetKey()
        Pressed = pygame.key.get_pressed()
        for Key in Keys:
            if Pressed[Key]:
                return
        Button = Global.JoyConfig.Arrows[Arrow.Direction]
        if Button and Global.JoyButtons[Button]:
            return
        # Denied!
        self.HandleHitArrow(Arrow, HitQuality.Miss)
    def MoveArrows(self):
        "Move arrows in accordance with what's going on in the music playback."
        global LastArrowTick
        ArrowTickTime = time.clock()
        if self.PauseFlag:
            LastArrowTick = ArrowTickTime
            return
        if self.WaitTicksAfterUnpause > 0:
            self.WaitTicksAfterUnpause -= 1
            return
        #print LastArrowTick, ArrowTickTime, ArrowTickTime - LastArrowTick
        ArrowDiff = Global.Party.Options["SongDifficulty"]
        TSSArrowState = Music.GetArrows(ArrowDiff)[:]
        ArrowsToProcess = self.Arrows.values()
        for (ID, Ticks, Direction, IsOffense, FreezeTime) in TSSArrowState:
            if not self.Arrows.has_key(ID):
                # Create a new arrow, unless this one is TOO CLOSE to create or TOO FAR to bother with:
                if Ticks < self.MinArrowCreateWait or Ticks > 8000: #%%%
                    continue
                Arrow = ArrowClass(ID, Direction, 1, IsOffense, Ticks, FreezeTime)
                self.Arrows[ID] = Arrow
                self.ArrowSprites.add(Arrow)
                self.ArrowList.append(Arrow)
                Arrow.SetX(ArrowXByDirection[Direction])
            else:
                ArrowsToProcess.remove(self.Arrows[ID])
                Arrow = self.Arrows[ID]
                if Arrow.TicksLeft < -HitQuality.MaxPoorTicks and (Arrow.FreezeQuality==None and not Arrow.TriggeredFlag):
                    self.HandleHitArrow(Arrow, HitQuality.Miss)
                    #Arrow.TriggeredFlag = 1                    
            # Set the ticks for this arrow:
            self.Arrows[ID].SetTicks(Ticks)
            if Arrow.FreezeTime and not Arrow.TriggeredFlag:
                self.MoveFreezeArrow(Arrow)
        # Arrows that have scrolled past the critical mark keep coasting along:
        MoveTime = 1000 * (ArrowTickTime - LastArrowTick)
        if (MoveTime < 0):
            print "???", MoveTime, ArrowTickTime, LastArrowTick
        for Arrow in ArrowsToProcess:
            Arrow.MoveMsec(MoveTime)
            if Arrow.FreezeTime and not Arrow.TriggeredFlag:
                self.MoveFreezeArrow(Arrow)
            else:
                # Handle misses:
                if Arrow.TicksLeft < -HitQuality.MaxPoorTicks and not Arrow.TriggeredFlag:
                    self.HandleHitArrow(Arrow, HitQuality.Miss)
                    Arrow.TriggeredFlag = 1
                # Remove old arrows from the list (stop animating them):
                if Arrow.rect.bottom < -10:
                    del self.Arrows[Arrow.ID]
                    self.ArrowList.remove(Arrow)
                    Arrow.kill()
        LastArrowTick = ArrowTickTime
    def HandleHitArrow(self, Arrow, Quality, Force = 0):
        "Hit the specified arrow with the specified quality."
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
            Attacker = Monster
            Defender = Player
        IsHit = random.choice((0,1,1,1)) #Attacker.MeleeSwing(Defender, Quality)
        AnimationCycles = AttackerSprite.AnimateAttack()
        Projectile = AttackerSprite.Critter.GetProjectile()
        # Use the projectile's speed to decide when to show damage:
        if Projectile:
            self.PendingEvents.append((EventTypes.Projectile, AttackerSprite, DefenderSprite, self.AnimationCycle + CritterSpriteClass.BaseAnimateDelay * Projectile[1]))
            ProjectileDelay = (Projectile[1] + Projectile[2]) * CritterSpriteClass.BaseAnimateDelay
            TriggerCycle = (self.AnimationCycle + ProjectileDelay)%MaxAnimationCycle
        else:
            TriggerCycle = (self.AnimationCycle + AnimationCycles)%MaxAnimationCycle
        Damage = 1
        self.PendingEvents.append((EventTypes.Damage, AttackerSprite, Damage, DefenderSprite, Colors.White, TriggerCycle))
    def QueueDamageEvent(self, AttackerSprite, VictimSprite, Damage, Delay, Color = Colors.White):
        self.PendingEvents.append((EventTypes.Damage, AttackerSprite, Damage, VictimSprite, Color,
                                   (self.AnimationCycle + Delay) % MaxAnimationCycle))
    def DebugPrintEvents(self):
        print "---EVENTS---"
        for Event in self.PendingEvents:
            print Event
    def HandlePendingEvents(self):
        for Event in self.PendingEvents[:]:
            if Event[-1] != self.AnimationCycle:
                continue
            self.PendingEvents.remove(Event) # Processed!
            Handler = self.EventHandlers.get(Event[0])
            if Handler:
                apply(Handler, (Event[1:],))
    def HandleProjectileEvent(self, ProjEvent):
        SourceSprite = ProjEvent[0]
        TargetSprite = ProjEvent[1]
        Projectile = SourceSprite.Critter.GetProjectile()
        if not Projectile:
            return
        if SourceSprite.Critter.IsPlayer():
            StartX = SourceSprite.rect.left
            FlipFlag = 0
        else:
            StartX = SourceSprite.rect.right
            FlipFlag = 1
        StartY = SourceSprite.rect.center[1]
        EndX = TargetSprite.CenterX
        EndY = TargetSprite.CenterY
        NewProj = ProjectileSprite(self, StartX, StartY,
                                   EndX, EndY,
                                   Projectile[0], Projectile[2] * CritterSpriteClass.BaseAnimateDelay,
                                   FlipFlag)
        self.AddAnimationSprite(NewProj)
    def GetSpriteForCritter(self, Critter):
        if Critter in Global.Party.Players:
            return self.PlayerSprites[Critter.Index]
        else:
            return self.MonsterSprites[self.Monsters.index(Critter)]
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
        # If the victim is dead, and it's a melee attack, select a new victim:
        # This is a little iffy, because animations may or may not appear to target a particular enemy.
        if Damage > 0:
            VictimSprite.AnimateOuch("", Color)
            # Make some noises!
            FileName = None
            if Attacker:
                FileName = Attacker.GetAttackSound()
            if not FileName:
                FileName = random.choice(("Hit.wav","Hit2.wav","Hit3.wav","Hit4.wav"))
            if not self.SilentFlag:
                Resources.PlayStandardSound(FileName)
        elif Damage < 0:
            pass
        else:
            VictimSprite.AnimateDodge()
            Resources.PlayStandardSound("Miss.wav")
        return 1
    def GetAttackingMonster(self):
        if not self.AliveMonsters:
            return None
        FrontRank = 1
        List = []
        for RankIndex in range(len(self.MonsterRanks)-1, -1, -1):
            Rank = self.MonsterRanks[RankIndex]
            for Monster in Rank:
                if Monster.IsAlive() and (FrontRank or Monster.Species.Projectile!=None):          
                    List.append(Monster)
            if List:
                FrontRank = 0
        return random.choice(List)
    def GetTargetMonster(self):
        if not self.AliveMonsters:
            return None
        for RankIndex in range(len(self.MonsterRanks)-1, -1, -1):
            Rank = self.MonsterRanks[RankIndex]
            List = []
            for Monster in Rank:
                if Monster.IsAlive():
                    List.append(Monster)
            if List:
                return random.choice(List)
    def EndBattle(self, Dummy = None):
        self.App.PopScreen(self)
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
    def HandleEvents(self):
        """
        The BattleScreen event handler does *not* handle arrow keys in the standard way.
        """
        for Event in pygame.event.get():
            self.HandleEvent(Event)
    def HandleJoyButton(self, Event):
        Dir = Global.JoyConfig.ButtonToDirection.get(Event.button, None)
        print Event.button, Dir
        if Dir==None:
            return
        if Dir=="start":
            if self.PauseFlag:
                self.Unpause()
            else:
                self.Pause()
            return 1
        if Dir == "select":
            if self.CanRewind:
                # Let's back up a little:
                Music.Rewind(5000) # 5 seconds
                self.MinArrowCreateWait = -50
                # Hide arrows, freeze casting action:
                self.Arrows = {}
                self.ArrowList = []
                for ArrowSprite in self.ArrowSprites.sprites():
                    ArrowSprite.kill()            
                return
        if not self.PauseFlag:
            self.TryArrow(Dir)
    def HandleKeyPressed(self, Key):
        "Return TRUE if we did something."
        if not self.PauseFlag:
            if Key in Keystrokes.Up:
                self.TryArrow(Directions.Up)
                return 1
            elif Key in Keystrokes.Down:
                self.TryArrow(Directions.Down)
                return 1
            elif Key in Keystrokes.Left:
                self.TryArrow(Directions.Left)
                return 1
            elif Key in Keystrokes.Right:
                self.TryArrow(Directions.Right)
                return 1
            elif Key == 263:
                self.TryArrow(Directions.NW)
                return 1
            elif Key == 265:
                self.TryArrow(Directions.NE)
                return 1
            elif Key == 257:
                self.TryArrow(Directions.SW)
                return 1
            elif Key == 259:
                self.TryArrow(Directions.SE)
                return 1
        if Key == pygame.K_ESCAPE:
            if self.PauseFlag:
                self.Unpause()
            else:
                self.Pause()
            return 1
        return 0
    def Pause(self):
        Resources.PlayStandardSound("Pause.wav")
        self.ArrowSprites.clear(self.Surface,self.BackgroundSurface) 
        # Draw everything but the arrows:
        DirtyRects = self.ForegroundSprites.draw(self.Surface)
        Dirty(DirtyRects)        
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)                
        Music.PauseSong()
        self.PauseFlag = 1
        # Show the pause screen:
        PausedImage = FancyAssBoxedText("Paused", Fonts.PressStart, 24, Spacing = 6)
        self.PauseSprite = GenericImageSprite(PausedImage, 475 - PausedImage.get_rect().width / 2,
                                              225 - PausedImage.get_rect().height / 2)
        self.AddAnimationSprite(self.PauseSprite)
        self.Redraw()
    def Unpause(self, Dummy = None):
        self.WaitTicksAfterUnpause = 3 # Wait three ticks before trusting music.get_pos() again
        self.PauseSprite.kill()
        self.PauseFlag = 0
        Resources.PlayStandardSound("Pause.wav")
        Music.UnpauseSong()
    def TryArrow(self, Direction):
        "User pressed an arrow-key.  See if they matched any of the song arrows."
        for Arrow in self.ArrowList:
            # If it's the right direction, it hasn't been triggered yet, and it's within range:
            if (not Arrow.TriggeredFlag) and (Arrow.Direction == Direction) and (abs(Arrow.TicksLeft)<HitQuality.MaxMissableTicks):
                Whiffage = abs(Arrow.TicksLeft) # TicksLeft==0 is a perfect hit
                if Whiffage > HitQuality.MaxPoorTicks:
                    Quality = HitQuality.Miss
                elif Whiffage > HitQuality.MaxGoodTicks:
                    Quality = HitQuality.Poor
                elif Whiffage > HitQuality.MaxPerfectTicks:
                    Quality = HitQuality.Good
                else:
                    Quality = HitQuality.Perfect
                self.HandleHitArrow(Arrow, Quality)
                #Arrow.TriggeredFlag = 1
                self.Whiffs.append(Arrow.TicksLeft)
                return # Only one arrow per TryArrow call!  (It's possible to have two in range at once)
    def GetTargetPlayer(self):
        "Pick a player to fold, spindle or mutilate"
        List = []
        for Player in Global.Party.Players:
            if Player.IsAlive():
                List.append(Player)
        if List:
            return random.choice(List)
        return Global.Party.Players[0]
    def HandleMouseMoved(self,Position,Buttons,LongPause = 0):
        "Track mouse position, for summonings"
        self.MousePosition = Position
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.DeepSprites.draw(self.BackgroundSurface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))



if PSYCO_ON:
    psyco.bind(DancingScreen.MoveArrows)
    psyco.bind(DancingScreen.HandleEvents)        