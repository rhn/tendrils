"""
ChestScreen!
There are chests at certain spots in the maze, which can be opened once per game.  These are called "maze chests".
Some hold very important stuff, like new spells or unique equipment.  Others hold less-vital but still-useful
stuff, like rare equipment or money or potion/elixir/ether stashes.  When the user gets to a room with a 
maze-chest, they can choose whether to open it or not; they can decide to come back later.

Also, monster groups can drop chests ("monster chests").  These are lost if the user doesn't disarm them right away.

Note that treasures from "boss battles" are not in chests.  (It's a pain to track a new maze chest once the boss
has been killed...and anyway, the player has been through a lot by beating the boss!)
"""
from Utils import *
from Constants import *
import Screen
import Music
import BattleSprites
import ItemPanel
import Global
import Resources
import string
import Maze
import sys

TrapDamagesByLevel = [0, 8, 12, 20, 30, 40, 60, 80, 100, 125, 150, 175, 200, 250]

FuseWidth = 765

def RollRandomTrap(BootyType, DungeonLevel):
    """
    What puzzle must one solve to disarm a trap?  And what effect does the trap have if you fail?
    Returns a tuple of the form (Trap panel class, Damage function)
    Note: This is called BEFORE showing the chest screen, because the party might cast Calfo to probe the
    trap and decide whether it's worth the risk (especially if it's a mini-game they suck at!)
    """
    import LightsOutPanel
    import WireLock
    import Cards
    import CastleLock
    import WordDialTrap
    import MastermindScreen
##    if not IsEXE():
##        Locks = (LightsOutPanel.PlayingBoard, ) #(WordDialTrapPanel, RedGreenTrapPanel, LightsOutPanel.PlayingBoard)
##    else:
    Locks = (MastermindScreen.MastermindLock, CastleLock.CastleLock, WordDialTrap.WordDialTrapPanel, RedGreenTrapPanel, LightsOutPanel.PlayingBoard, WireLock.WirePuzzlePanel)
    if Global.Maze.Level < 3:
        Traps = (SpringPoisonNeedle, SpringCrossbowBolt, SpringStunner)
    elif Global.Maze.Level < 7:
        Traps = (SpringPoisonNeedle, SpringCrossbowBolt, SpringStunner,
                 SpringCockatriceBlood, SpringExplodingBox, )
    else:
        Traps = (SpringCockatriceBlood, SpringExplodingBox, SpringFigbyFist,
                 SpringMalboroCountry)
    if BootyType == 1:
        LockClass = random.choice(Locks)    
        TrapCode = random.choice(Traps)
    else:
        #The lock and trap you get are determined by your X, Y, Z coordinates in the maze.  That
        #way, the player can cast Calfo on a fixed-position chest, wander home, bring back a ninja,
        #and the lock and trap are still the same.
        X = Global.Party.X
        Y = Global.Party.Y
        LockIndex = X*7 + Y*5 + DungeonLevel
        TrapIndex = X*13 + Y*11 + DungeonLevel
        LockClass = Locks[LockIndex%len(Locks)]
        TrapCode = Traps[TrapIndex%len(Traps)]
    return (LockClass, TrapCode)

def SpringPoisonNeedle():
    "Poison Needle" # docstring is displayed to user on Calfo
    EventStr = "<CN:BRIGHTBLUE>Poison Needle!</C>\n\n"
    Player = Global.Party.GetLiveMember()
    if not Player:
        return EventStr
    PoisonTime = Global.Maze.Level * 100
    Player.Perks["Poison"] = max(Player.Perks.get("Poison", 0), PoisonTime)
    EventStr += "%s has been <CN:PURPLE>POISONED!</C>\n"%(Player.Name)
    return EventStr

def SpringStunner():
    "Stunner" # docstring is displayed to user on Calfo
    EventStr = "<CN:BRIGHTBLUE>Stunner!</C>\n\n"
    Player = Global.Party.GetLiveMember()
    if not Player:
        return EventStr
    Time = Global.Maze.Level * 200
    Player.Perks["Paralysis"] = max(Player.Perks.get("Paralysis", 0), Time)
    EventStr += "%s has been <CN:PURPLE>PARALYZED!</C>\n"%(Player.Name)
    return EventStr

def SpringCrossbowBolt():
    "Crossbow Bolt" # docstring is displayed to user on Calfo
    EventStr = "<CN:BRIGHTBLUE>Crossbow Bolt!</C>\n\n"
    Player = Global.Party.GetLiveMember()
    if not Player:
        return EventStr
    Damage = TrapDamagesByLevel[Global.Maze.Level]
    # Randomize a bit:
    Multiplier = random.randrange(60, 141) / float(100)
    Damage = int(Damage * Multiplier)
    Player.HP -= Damage
    EventStr += "%s takes <CN:RED>%d</C> damage!\n"%(Player.Name, Damage)
    if Player.HP <= 0:
        Player.Die()
        EventStr += "%s is <CN:BRIGHTRED>DEAD!</C>\n"%(Player.Name)
    return EventStr

def SpringCockatriceBlood():
    "Cockatrice Blood" # docstring is displayed to user on Calfo
    EventStr = "<CN:ORANGE>Cockatrice Blood!</C>\n\n"
    Player = Global.Party.GetLiveMember()
    if not Player:
        return EventStr
    Time = Global.Maze.Level * 500
    if Player.HasPerk("Stoning Immune"):
        EventStr += "Luckily, %s is immune to stoning!"%Player.Name
    else:
        Player.Perks["Stone"] = max(Player.Perks.get("Stone", 0), Time)
        EventStr += "%s has been <CN:ORANGE>TURNED TO STONE!</C>\n"%(Player.Name)
    return EventStr

def SpringExplodingBox():
    "Exploding Box" # docstring is displayed to user on Calfo
    EventStr = "<CN:BRIGHTRED>Exploding Box!</C>\n\n"
    for Player in Global.Party.Players:
        if Player.IsDead():
            continue
        Damage = TrapDamagesByLevel[Global.Maze.Level]
        # Randomize a bit:
        Multiplier = random.randrange(60, 141) / float(100)
        Damage = int(Damage * Multiplier)
        Player.HP -= Damage
        EventStr += "%s takes <CN:RED>%d</C> damage!\n"%(Player.Name, Damage)
        if Player.HP <= 0:
            Player.Die()
            EventStr += "%s is <CN:BRIGHTRED>DEAD!</C>\n"%(Player.Name)
    return EventStr

def SpringMalboroCountry(): # Yes, it's a bad pun.
    "Malboro Country" # docstring is displayed to user on Calfo
    EventStr = "<CN:YELLOW>Malboro Country!</C>\n\n"
    for Player in Global.Party.Players:
        if Player.IsDead():
            continue
        Time = Global.Maze.Level * 500
        if random.random() > 0.85:
            if Player.HasPerk("Stoning Immune"):
                EventStr += "Luckily, %s is immune to stoning!\n"%Player.Name
            else:
                Player.Perks["Stone"] = max(Player.Perks.get("Stone", 0), Time)
                EventStr += "%s has been <CN:ORANGE>TURNED TO STONE!</C>\n"%(Player.Name)
        if random.random() > 0.25:
            if Player.HasPerk("Poison Immune"):
                EventStr += "Luckily, %s is immune to poison!\n"%Player.Name
            else:
                Player.Perks["Poison"] = max(Player.Perks.get("Poison", 0), Time)
                EventStr += "%s has been <CN:PURPLE>POISONED!</C>\n"%(Player.Name)
        if random.random() > 0.5:
            if Player.HasPerk("Paralysis Immune"):
                EventStr += "Luckily, %s is immune to paralysis!\n"%Player.Name
            else:
                Player.Perks["Paralysis"] = max(Player.Perks.get("Paralysis", 0), Time)
                EventStr += "%s has been <CN:BRIGHTBLUE>PARALYZED!</C>\n"%(Player.Name)
        if random.random() > 0.5:
            if Player.HasPerk("Silence Immune"):
                EventStr += "Luckily, %s is immune to silence!\n"%Player.Name
            else:
                Player.Perks["Silence"] = max(Player.Perks.get("Silence", 0), Time)
                EventStr += "%s has been <CN:BRIGHTBLUE>SILENCED!</C>\n"%(Player.Name)
    return EventStr

def SpringFigbyFist():
    "Figby Fist" # docstring is displayed to user on Calfo
    EventStr = "<CN:ORANGE>Figby Fist!</C>\n\n"
    Player = Global.Party.GetLiveMember()
    if not Player:
        return EventStr
    EventStr += "%s has been <CN:BRIGHTRED>CRUSHED to death!</C>\n"%Player.Name
    Player.Die()
    return EventStr
    
class ChestScreen(Screen.TendrilsScreen):
    "Shown after the player decides to disarm the trap."
    TrapPanelX = 0
    TrapPanelY = 50
    TrapPanelHeight = 500
    TimePanelY = 551
    def __init__(self, App, TrapPanelClass, TrapTriggerFunction, ChestItems = {}, ChestSpecial = {},
                 ChestType = 1,
                 OverrideLevel = None):
        Screen.TendrilsScreen.__init__(self,App)
        # Trap panel.  (Need to choose your subclass before insantiating!)
        Level = Global.Maze.Level
        if OverrideLevel:
            Level = OverrideLevel
        self.TrapPanel = TrapPanelClass(self, self.TrapPanelX, self.TrapPanelY, self.Width - self.TrapPanelX,
                                   self.TrapPanelHeight, Level, Global.Party.HasNinja())
        self.SubPanes.append(self.TrapPanel)
        self.TrapTriggerFunction = TrapTriggerFunction
        self.ChestItems = ChestItems
        self.ChestSpecial = ChestSpecial
        self.ChestType = ChestType
        self.StartTime = None
        self.TriggerTime = None
        self.TimerX = None
        self.Disarming = 0
        self.TrapEnabled = 1
        self.ShownInstructions = 0
        self.RenderInitialScreen()
        self.PlayDisarmMusic()
    def PlayDisarmMusic(self):
        self.SummonSong("disarm") # %%%
        pass
    def RenderInitialScreen(self):
        # Separator lines:
        Sprite = LineSprite(0, self.TrapPanelY - 1, self.Width, self.TrapPanelY)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(0, self.TimePanelY, self.Width, self.TimePanelY)
        self.AddBackgroundSprite(Sprite)
        # Fuse (at bottom of screen):
        self.RenderFuse()
        # Title (at top of screen):
        Sprite = GenericTextSprite("Opening a chest - Defuse the trap before time runs out!", self.Width / 2, 10, Colors.Yellow, CenterFlag = 1, FontSize = 32)
        self.AddBackgroundSprite(Sprite)
    def RenderFuse(self):
        # Load the fuse images:
        Images = []
        Images.append(Resources.GetImage(os.path.join(Paths.ImagesMisc, "TimerRed.png")))
        Images.append(Resources.GetImage(os.path.join(Paths.ImagesMisc, "TimerYellow.png")))
        Images.append(Resources.GetImage(os.path.join(Paths.ImagesMisc, "TimerGreen.png")))
        # And the BOMB image:
        Image = Resources.GetImage(os.path.join(Paths.ImagesTraps, "Old School Bomb.png"))
        Sprite = GenericImageSprite(Image, 0, 550)
        #self.AddBackgroundSprite(Sprite)
        self.AddForegroundSprite(Sprite)
        # Blit the fuse images across the length of the sprite:
        FuseSurface = pygame.Surface((FuseWidth, 98))
        X = 0
        while X < FuseWidth:
            if X<100:
                Image = Images[0]
            elif X<400:
                Image = Images[1]
            else:
                Image = Images[2]
            FuseSurface.blit(Image, (X, 50))
            X += Images[0].get_rect().width
        self.FuseSprite = GenericImageSprite(FuseSurface, 800-FuseWidth, 516)
        self.AddForegroundSprite(self.FuseSprite)
        self.TimerX = FuseWidth
    def HandleKeyPressed(self, Key):
        if Key == Keystrokes.Debug:
            self.Disarming = 0
            Resources.PlayStandardSound("TrapDisarmed.wav")
            self.FuseSprite.image.fill(Colors.Black)
            self.FinishGetStuff()
        self.TrapPanel.HandleKeyPressed(Key) # delegate!
    def DisableTrap(self):
        """
        Our panel can call this method to disable trap-triggering while it finishes some
        animation.
        """
        self.TrapEnabled = 0
    def Update(self):
        if not self.Disarming:
            return
        Now = time.time()
        if self.TrapEnabled:
            # Update the "fuse" graphic:
            TimerX = (self.TriggerTime - Now) / float(self.TriggerTime - self.StartTime)
            TimerX = int(TimerX * FuseWidth)
            pygame.draw.rect(self.FuseSprite.image, Colors.Black, (TimerX, 0, self.TimerX, 200), 0)
            self.TimerX = TimerX
        # Handle FAILURE:
        if self.TrapPanel.IsFailed() or (Now >= self.TriggerTime and self.TrapEnabled):
            self.Disarming = 0
            self.FuseSprite.image.fill(Colors.Black)
            self.FinishTrapTriggered()
        if self.TrapPanel.IsDisarmed():
            self.Disarming = 0
            Global.Party.BigBrother.UpdateTrapPerformance(self.TrapPanel.__doc__, 1)
            Resources.PlayStandardSound("TrapDisarmed.wav")
            self.FuseSprite.image.fill(Colors.Black)
            if self.TrapPanel.__doc__ == "Lights out":
                Global.Party.BlinkenCount += 1
                if Global.Party.BlinkenCount >= 2 and not Global.MemoryCard.Get("MiniGameBlinkenlights"): #%%%
                    Global.MemoryCard.Set("MiniGameBlinkenlights", 1)
                    Str = "<CN:GREEN>Success!</c>\n\nAlso...\n<CN:ORANGE>You have unlocked the Blinkenlights mini-game!"
                    Global.App.ShowNewDialog(Str, Callback = self.FinishGetStuff)
                    return
            self.FinishGetStuff()
    def StartTimer(self):
        self.StartTime = time.time()
        self.TriggerTime = self.StartTime + self.TrapPanel.TimeLimit
        self.Disarming = 1
    def FinishTrapTriggered(self):
        Music.FadeOut()
        # Get rid of the trap panel, its work here is done:
        self.SubPanels = []
        Global.Party.BigBrother.UpdateTrapPerformance(self.TrapPanel.__doc__, 0)
        # Zoinks!  This can't be good!
        Resources.PlayStandardSound("TrapTriggered.wav")
        FeedbackString = "Egad!  You bungled it.\n\n"
        FeedbackString += apply(self.TrapTriggerFunction)
        self.App.ShowNewDialog(FeedbackString, Callback = self.FinishGetStuff)
    def FinishGetStuff(self):
        Music.FadeOut()
        if Maze.CheckForAllDead():
            return # They're all dead, dave.  Everyone's dead.
        GetTreasureChestStuff(self.ChestItems, self.ChestSpecial, self.ChestType)
        self.App.PopScreen(self)
    def Activate(self):
        self.Redraw()
        if not self.ShownInstructions:
            self.TrapPanel.ShowInstructions()
            self.ShownInstructions = 1
            return
        
def GetSpecialChestStuff(ChestSpecial):
    Str = ""
    for RawKey in ChestSpecial.keys():
        Key = RawKey.lower()
        # Spells:
        Bits = Key.split(":")
        if len(Bits)>1:            
            SpellIndex = int(Bits[1])
            if Bits[0].lower()=="mage":
                Spell = Global.Spellbook.MageSpells[SpellIndex]
                Str += "A tome of magic!\n<CN:RED>You have found the mage spell: %s!</C>\n"%Spell.Name
                Global.Party.FoundMageSpells[SpellIndex] = 1
            elif Bits[0].lower()=="cleric":
                Spell = Global.Spellbook.ClericSpells[SpellIndex]
                Str += "A priestly book!\n<CN:RED>You have found the cleric spell: %s</C>\n"%Spell.Name
                Global.Party.FoundClericSpells[SpellIndex] = 1
            elif Bits[0].lower()=="summoner":
                Spell = Global.Spellbook.SummonerSpells[SpellIndex]
                Str += "A rune of invocation!\n<CN:RED>You have found the summoner spell: %s</C>\n"%Spell.Name
                Global.Party.FoundSummonerSpells[SpellIndex] = 1
            else:
                print "** Unexpected colon in special item:", Bits
                pass
        elif Key == "gold":
            Global.Party.Gold += ChestSpecial[RawKey]
            Str += "You looted <CN:YELLOW>%d zenny</C>\n"%ChestSpecial[RawKey]
        else:
            OldCount = Global.Party.KeyItemFlags.get(RawKey, 0)
            Global.Party.KeyItemFlags[RawKey] = OldCount + 1
            Str += "You found: %s\n"%RawKey
    return Str
    
def GetTreasureChestStuff(ChestItems, ChestSpecial, ChestType, SpecialLootString = None):
    if ChestType == 2 or ChestType == 3:
        # Flag the chest as looted:
        Global.Party.LootedChests[(Global.Party.X, Global.Party.Y, Global.Maze.Level)] = 1 #%%%
    if SpecialLootString:
        FeedbackString = SpecialLootString
    else:
        FeedbackString = "<CENTER>You eagerly loot the chest.\n<IMG:CHEST></CENTER>\n\n\n\n"
    for Key in ChestItems.keys():
        Item = Global.QuarterMaster.GetItem(Key)
        if not Item:
            print "** WARNING: Unknown chest item '%s' skipped"%Key
            continue
        Count = ChestItems[Key]
        if Count==1:
            FeedbackString += "You found: <CN:BRIGHTBLUE>%s</C>\n"%Item.Name
        else:
            FeedbackString += "You found: <CN:BRIGHTBLUE>%s</C> <CN:BRIGHTGREEN>x%d</C>\n"%(Item.Name,Count)
        for Index in range(Count):
            Global.Party.GetItem(Item)
    # Wevel chest:
    WevelFlag = 0
    if ChestSpecial.has_key("wevel8"):
        del ChestSpecial["wevel8"]
        WevelFlag = 1
    # Now handle the 'special' chest stuff:
    FeedbackString += GetSpecialChestStuff(ChestSpecial)
    ##FeedbackString = "You got some stuff.  Huzzah." #%%%
    if WevelFlag:
        Global.App.ShowNewDialog(FeedbackString, Callback = WevelComplete)
    else:
        Global.App.ShowNewDialog(FeedbackString)

def WevelComplete():
    if not Global.Party.EventFlags.has_key("wevel8"):
        Global.Party.EventFlags["wevel8"] = 0
    Global.Party.EventFlags["wevel8"] += 1
    if Global.Party.EventFlags["wevel8"] == 10:
        Resources.PlayStandardSound("PowerUp.wav")
        Str = "<CENTER><CN:PURPLE>WEVEL BONUS</C></CENTER>\n\n<CN:YELLOW>All chests collected!\n\nYou get: <CN:WHITE>Diamond Armor"
        Global.Party.GetItem("Diamond Armor")
        Global.App.ShowNewDialog(Str)
        
class TrapPanel(Screen.TendrilsPane):
    """
    "It's a trap!" -- Admiral Ackbar
    The trap pannel occupies the full width of the screen, and most of the height.  It's where
    the trap mini-games are played.  
    """
    def __init__(self, Master, BlitX, BlitY, Width, Height, DungeonLevel = 1, HasNinja = 0):
        Screen.TendrilsPane.__init__(self, Master, BlitX, BlitY, Width, Height, "Trap")
        self.DungeonLevel = DungeonLevel
        self.HasNinja = HasNinja
        self.TimeLimit = 10 # in seconds        
    def IsFailed(self):
        "Returns true if the player has REALLY pooched it, and triggered the trap before time ran out"
        return 0
    def IsDisarmed(self):
        return 0
    def InitTrap(self):
        """
        The 'real' traps - subclasses of TrapPanel - override this method to do their initial setup
        and create their starting sprites.  They should also probably override self.TimeLimit
        """
        Sprite = GenericTextSprite("Test trap!", 100, 100)
        self.AddForegroundSprite(Sprite)
        self.Surface.fill(Colors.Green)
        self.Redraw()
    def Update(self):        
        Screen.TendrilsPane.Update(self)
        for Sprite in self.AnimationSprites.sprites():
            Sprite.Update(self.Master.AnimationCycle)
    def HandleKeyPressed(self, Key):
        "Override this, if the disarm can use keystrokes"
        pass
    def ShowInstructions(self):
        Global.App.ShowNewDialog("Here are some instructions on how to disarm this kind of trap.  Good luck!", Callback = self.Start)
        return
        # Or, you can just start the fun now:
        self.InitTrap()
        self.Master.StartTimer()
    def Start(self):
        self.InitTrap()
        self.Master.StartTimer()

Rot13Trans = string.maketrans("abcdefghijklmnopqrstuvwxyz","nopqrstuvwxyzabcdefghijklm")
def Rot13(Str):
    return string.translate(Str,Rot13Trans)

class FlashingSprite(TidySprite):
    AnimateSpeed = 35
    def __init__(self, Pane, Image, X, Y):
        TidySprite.__init__(self, Pane)
        Rect = Image.get_rect()
        self.image = pygame.Surface((Rect.width, Rect.height))  
        self.image.set_alpha(100)
        self.image.set_colorkey(Colors.Black)
        self.image.blit(Image, (0,0))
        self.rect = self.image.get_rect()
        self.rect.left = X
        self.rect.top = Y
    def Update(self,AnimationCycle):        
        Factor = 0.3 + 0.7 * abs(AnimationCycle%(self.AnimateSpeed*2) - self.AnimateSpeed) / float(self.AnimateSpeed)
        self.image.set_alpha(int(Factor*255))
        ##print Factor
class FlashableSprite(TidySprite):
    FadeSpeed = 9
    def __init__(self, Pane, Image, X, Y):
        TidySprite.__init__(self, Pane)
        Rect = Image.get_rect()
        self.image = pygame.Surface((Rect.width, Rect.height))  
        self.image.set_alpha(60)
        self.image.set_colorkey(Colors.Black)
        self.image.blit(Image, (0,0))
        self.rect = self.image.get_rect()
        self.rect.left = X
        self.rect.top = Y
        self.Alpha = 60
    def Update(self, AnimationCycle):
        OldAlpha = self.Alpha
        self.Alpha = max(self.Alpha - self.FadeSpeed, 60)
        if OldAlpha != self.Alpha:
            self.image.set_alpha(self.Alpha)
            Dirty(self.rect)
    def Flash(self):
        self.Alpha = 255
    
LowerLetters = "abcdefghijklmnopqrstuvwxyz1"
Letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!'

class RedGreenStates:
    Green = 0
    Red = 1

class RedLightSprite(GenericImageSprite):
    MaxPause = 3
    def __init__(self, Images, X, Y):
        GenericImageSprite.__init__(self, Images[0], X, Y)
        self.ImageIndex = 0
        self.Dir = 0
        self.Pause = self.MaxPause
        self.Images = Images
    def TurnRed(self):
        self.Dir = 1
    def TurnGreen(self):
        self.Dir = -1
    def Update(self, Dummy):
        if self.Dir:
            self.Pause -= 1
            if self.Pause <= 0:
                self.Pause = self.MaxPause
                self.ImageIndex += self.Dir
                if self.ImageIndex<0:
                    self.ImageIndex = 0
                    self.Dir = 0
                if self.ImageIndex>=len(self.Images):
                    self.ImageIndex = len(self.Images) - 1
                    self.Dir = 0
                self.image = self.Images[self.ImageIndex]
    
class RedGreenTrapPanel(TrapPanel):
    "Pounder" # docstring is displayed to user on Calfo
    RedLightX = 400
    RedLightY = 250
    LeftArrowX = 300
    RightArrowX = 500
    MidArrowX = 400
    MidArrowY = 250
    TopArrowY = 150
    BottomArrowY = 350
    BarY = 420
    def __init__(self, *args, **kw):
        self.SwitchTime = None
        TrapPanel.__init__(self, *args, **kw)
    def InitTrap(self):
        FileNames = ["Arrow.Up.png", "Arrow.Down.png", "Arrow.Left.png", "Arrow.Right.png"]
        self.ArrowImages = []
        for Index in range(4):
            Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, FileNames[Index]))
            self.ArrowImages.append(Image)
        self.InitLightSprite()
        self.ArrowSprites = {}
        self.State = RedGreenStates.Green
        self.ResetDirections()
        self.SwitchTime = (self.Master.AnimationCycle + random.randrange(100, 400)) % MaxAnimationCycle
        self.LastHit = None
        self.BarX = 0.0
        self.PenaltyX = 1.0
        self.ForwardX = 3.0
        self.BarDistance = 180 + (self.DungeonLevel * 22)
        self.TimeLimit = 18
        if self.HasNinja:
            self.TimeLimit *= 2
        self.StartX = 400 - self.BarDistance / 2
        self.FinishLineX = 400 + self.BarDistance / 2
        self.DrawBall()
        self.ReRender()
    def ResetDirections(self):
        self.DirFlags = {}
        self.DirFlags[Directions.Up] = 0
        self.DirFlags[Directions.Down] = 0
        self.DirFlags[Directions.Left] = 0
        self.DirFlags[Directions.Right] = 0
        if self.DungeonLevel < 5:
            if random.random() > 0.5:
                self.DirFlags[Directions.Up] = 1
                self.DirFlags[Directions.Down] = 1
            else:
                self.DirFlags[Directions.Left] = 1
                self.DirFlags[Directions.Right] = 1
        else:
            Choices = [Directions.Up, Directions.Down, Directions.Left, Directions.Right]
            Dir = random.choice(Choices)
            self.DirFlags[Dir] = 1
            Choices.remove(Dir)
            Dir = random.choice(Choices)
            self.DirFlags[Dir] = 1
            Choices.remove(Dir)
    def InitLightSprite(self):         
        LightImages = []
        for Index in range(5):
            Image = Resources.GetImage(os.path.join(Paths.ImagesTraps, "RedGreen", "redgreen%d.png"%Index))
            LightImages.append(Image)
        self.LightSprite = RedLightSprite(LightImages, self.RedLightX, self.RedLightY)
        self.LightSprite.rect.left -= self.LightSprite.rect.width / 2
        self.LightSprite.rect.top -= self.LightSprite.rect.height / 2
        self.AddAnimationSprite(self.LightSprite)
    def MoveBallSprite(self):
        self.BallSprite.rect.left = self.StartX + self.BarX - self.BallWidth
    def DrawBall(self):
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "ButtonProgress.png"))
        self.BallSprite = GenericImageSprite(Image, 0, self.BarY)
        self.BallWidth = self.BallSprite.rect.width / 2
        BallHeight = self.BallSprite.rect.height / 2
        self.MoveBallSprite()
        #self.BallSprite.rect.left -= self.BallWidth
        self.AddForegroundSprite(self.BallSprite)
        Sprite = LineSprite(self.StartX, self.BarY + BallHeight - 15, self.StartX, self.BarY + BallHeight + 15)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(self.FinishLineX, self.BarY + BallHeight - 15, self.FinishLineX, self.BarY + BallHeight + 15)
        self.AddBackgroundSprite(Sprite)        
    def ShowInstructions(self):
        """
        Display instructions.
        """
        Str = """<CN:BLUE>The Pounder</C>\n\nTap the arrows (alternating directions) as fast as possible.\
\n\nBut STOP, when the light turns red.\n\nMove the bar all the way across before time runs out."""
        self.SwitchTime = None
        Global.App.ShowNewDialog(Str, Callback = self.Start, DialogY = 150)
        #self.Start()
    def ReRender(self):
        for Sprite in self.ArrowSprites.values():
            Sprite.kill()
        self.ArrowSprites = {}
        if self.State == RedGreenStates.Red:
            self.LightSprite.TurnRed()
        else:
            self.LightSprite.TurnGreen()
            if self.DirFlags[Directions.Left]:
                Sprite = FlashableSprite(self, self.ArrowImages[2], self.LeftArrowX, self.MidArrowY)
                self.ArrowSprites[Directions.Left]=Sprite
                self.AddAnimationSprite(Sprite)
                Sprite.rect.left -= (Sprite.rect.width)/2
                Sprite.rect.top -= (Sprite.rect.height)/2
            if self.DirFlags[Directions.Right]:
                Sprite = FlashableSprite(self, self.ArrowImages[3], self.RightArrowX, self.MidArrowY)
                self.ArrowSprites[Directions.Right]=Sprite
                self.AddAnimationSprite(Sprite)
                Sprite.rect.left -= (Sprite.rect.width)/2
                Sprite.rect.top -= (Sprite.rect.height)/2
            if self.DirFlags[Directions.Up]:
                Sprite = FlashableSprite(self, self.ArrowImages[0], self.MidArrowX, self.TopArrowY)
                self.ArrowSprites[Directions.Up]=Sprite
                self.AddAnimationSprite(Sprite)
                Sprite.rect.left -= (Sprite.rect.width)/2
                Sprite.rect.top -= (Sprite.rect.height)/2
            if self.DirFlags[Directions.Down]:
                Sprite = FlashableSprite(self, self.ArrowImages[1], self.MidArrowX, self.BottomArrowY)
                self.ArrowSprites[Directions.Down]=Sprite
                self.AddAnimationSprite(Sprite)
                Sprite.rect.left -= (Sprite.rect.width)/2
                Sprite.rect.top -= (Sprite.rect.height)/2
        self.Redraw()
    def Update(self):
        for Sprite in self.AnimationSprites.sprites():
            Sprite.Update(1)
        if self.SwitchTime == None:
            return
        if self.Master.AnimationCycle == self.SwitchTime:
            if self.State == RedGreenStates.Red:
                self.ResetDirections()
                self.State = RedGreenStates.Green
                self.SwitchTime = (self.Master.AnimationCycle + random.randrange(100, 400)) % MaxAnimationCycle
            else:
                self.State = RedGreenStates.Red
                self.SwitchTime = (self.Master.AnimationCycle + random.randrange(50, 200)) % MaxAnimationCycle
            Resources.PlayStandardSound("Bleep2.wav")
            self.ReRender()
    def HandleKeyPressed(self, Key):
        "Override this, if the disarm can use keystrokes"
        Arrow = None
        if Key in Keystrokes.Up:
            Arrow = "Up"
        elif Key in Keystrokes.Down:
            Arrow = "Down"
        elif Key in Keystrokes.Left:
            Arrow = "Left"
        elif Key in Keystrokes.Right:
            Arrow = "Right"
        if not Arrow:
            return
        if self.State == RedGreenStates.Red:
            self.BarX -= self.PenaltyX
            self.MoveBallSprite()
            return
        if self.DirFlags[Directions.Up] and self.LastHit != "Up" and Arrow == "Up":
            self.BarX += self.ForwardX
            self.MoveBallSprite()
            self.LastHit = "Up"
            self.ArrowSprites[Directions.Up].Flash()
            return
        if self.DirFlags[Directions.Down]  and self.LastHit != "Down" and Arrow == "Down":
            self.BarX += self.ForwardX
            self.MoveBallSprite()
            self.LastHit = "Down"
            self.ArrowSprites[Directions.Down].Flash()
            return
        if self.DirFlags[Directions.Left]  and self.LastHit != "Left" and Arrow == "Left":
            self.BarX += self.ForwardX
            self.MoveBallSprite()
            self.LastHit = "Left"
            self.ArrowSprites[Directions.Left].Flash()
            return
        if self.DirFlags[Directions.Right]  and self.LastHit != "Right" and Arrow == "Right":
            self.BarX += self.ForwardX
            self.MoveBallSprite()
            self.LastHit = "Right"
            self.ArrowSprites[Directions.Right].Flash()
            return
    def IsFailed(self):
        return 0
    def IsDisarmed(self):
        if self.BarX >= self.BarDistance:
            return 1
        return 0