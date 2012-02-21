#!/usr/bin/env python

"""
BEFORE DIVING INTO CODE:
You will probably want to have the pygame documentation handy.  Many important
classes are subclasses of pygame.sprite, and the pygame events are what drives the interface.  The core combat
engine is in DancingScreen.py and BattleScreen.py

ARCHITECTURE:
The main objects in Tendrils are:
- TendrilsApplication (main app, coordinates global data)
- Screen objects (user interface stuff, shepherd of sprites)
- Party object (the PCs and their inventory)
- Critter objects (the monsters)
- Maze object (the dungeon)
- Various subclasses of GenericImageSprite (things on screen)
The Tendrils interface is divided into various screens, such as
ShopScreen and BattleScreen (see the Screen module for the base
class).  Screens are organized into a stack - for instance, while in
the Maze screen, you could bring up the Equipment screen and from there,
the SpecialItems screen.  Only the topmost screen receives events and
performs updates.
"""
import sys
import os

# Let's run everything - even the importing, since that triggers loading
# of critters.txt and so forth - from the CORRECT directry!
if len(sys.argv)>0:
    Dir = os.path.split(sys.argv[0])[0]
    if Dir:
        os.chdir(Dir)

from Utils import *
from Constants import *


# Set up logging:
RealLogFileName = UserDataFileName(LogFileName)
# Make directories, if needed:
try:
    os.makedirs(os.path.split(RealLogFileName)[0])
except:
    pass # already exists, probably
if sys.argv[0].lower().endswith('.py'):
    f = open(RealLogFileName,'wt')
    sys.stderr = sys.stdout = BranchedFile(f, sys.stdout)
else:
    sys.stderr = sys.stdout = FlushFile(RealLogFileName, 'wt')

import Global
import MemoryCard
import Resources
import Maze
import Critter
import Party
import traceback
import NewDialogScreen
import Music
import NPC
import LevelUp
import Bard
import SpecialItems

# Throttle, to avoid ludicrous speed (especially on fast CPUs)
MAX_FPS = 90


class CommandLines:
    "Command-line arguments to Tendrils, mostly for testing"
    Play = "play"
    Battle = "battle"
    Equip = "equip"
    Shop = "shop"
    Maze = "maze"
    Map = "map"

    Save = "save"
    Chest = "chest"
    Inn = "inn"
    NPC = "npc"
    Options = "options"
    Snipe = "snipe"
    Demo = "demo"
    Trivia = "trivia"
    Victory = "victory"
    Worm = "worm"
    Block = "block"
    Practice = "practice"
    Dalek = "dalek"
    FreePlay = "free"
    Blezmon = "blezmon"
    Tower = "tower"
    Solitaire = "solitaire"
    JoustPong = "joustpong"
    Pegs = "pegs"
    Blinkenlights = "blinkenlights"
    
class TendrilsApplication:
    """
    The master object for playing Tendrils.  This object contains the main game-loop, and
    creates and kills screens.  It's fairly simple.
    """
    def __init__(self, Surface = None):
        self.ScreenStack = [] # ScreenStack[-1] is the top (visible) screen
        self.CurrentScreen=None
        self.Quitting = 0
        self.Surface = Surface
        self.Width = None
        self.Height = None
        self.AllSprites = pygame.sprite.RenderUpdates()
        self.AnimationSprites = pygame.sprite.RenderUpdates()
        Global.App = self
    def StartTrivia(self):
        import TriviaScreen
        NewScreen = TriviaScreen.TriviaScreen(self)
        self.PushNewScreen(NewScreen)
    def DoSpecialItems(self):
        # Repaint the top screen:
        if self.ScreenStack:
            self.ScreenStack[-1].ForegroundSprites.draw(self.ScreenStack[-1].Surface)
            self.ScreenStack[-1].AnimationSprites.draw(self.ScreenStack[-1].Surface)         
        NewScreen = SpecialItems.GetItemScreen()
        self.PushNewScreen(NewScreen)
    def LevelPlayerUp(self, Player, Callback = None):
        NewScreen = LevelUp.LevelUpScreen(Player, Callback)
        self.PushNewScreen(NewScreen)        
    def ShowMultiDialog(self, Text, Items, Count, Callback):
        NewScreen = NewDialogScreen.MultiButtonDialogScreen(Text, Items, Count, Callback)
        self.PushNewScreen(NewScreen)
    def ReturnToTitle(self):
        "Called when the party perishes.  Kill all screens, then bring up the title screen."
        for Screen in self.ScreenStack[:]: # note: iterate over a copy, since we're changing the original!
            self.PopScreen(Screen)
        # BETA: Save big-brother info
        File = open(UserDataFileName("BigBrother.txt"), "w")
        Global.BigBrother.DumpToFile(File)
        File.close()
        import WelcomeScreen
        NewScreen = WelcomeScreen.WelcomeScreen(self)
        self.PushNewScreen(NewScreen)
    def ShowFadeOutScreen(self, FadeFromScreen, FadeToScreen, DarkPause = 0):
        import FadeScreen
        NewScreen = FadeScreen.FadeScreen(self, FadeFromScreen, FadeToScreen, DarkPause)
        self.PushNewScreen(NewScreen)
    def CalfoChest(self, Cmd, ItemDict, SpecialDict, BootyType):
        import ChestScreen
        if Cmd == "Leave it":
            return
        if Cmd == "Disarm":
            self.DisarmChest(ItemDict, SpecialDict, BootyType)
            return
        (Lock, Trap) = ChestScreen.RollRandomTrap(BootyType, Global.Maze.Level)
        Global.Party.CastCalfo()
        Str = "Divine insight is yours.\n\nLock: <CN:BLUE>%s</C>\nTrap: <CN:BLUE>%s</C>\n\nDisarm the trap?"%(Lock.__doc__, Trap.__doc__)
        DisarmCommand = lambda I=ItemDict, S=SpecialDict, B=BootyType: self.DisarmChest(I, S, B, Lock, Trap)
        Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = DisarmCommand)
    def AskDisarmChest(self, ItemDict = {}, SpecialDict = {}, BootyType = 2):
        if Global.Party.CanCalfo():
            DisarmCommand = lambda Cmd, I=ItemDict, S=SpecialDict, B=BootyType: self.CalfoChest(Cmd, I, S, B)
            String = "You found a chest!\n\nWill you attempt to unlock it?"
            Buttons = ["Cast Calfo", "Disarm", "Leave it"]
            Global.App.ShowNewDialog(String, CustomButtons = Buttons, Callback = DisarmCommand)

        else:
            DisarmCommand = lambda I=ItemDict, S=SpecialDict, B=BootyType: self.DisarmChest(I, S, B)
            String = "You found a chest!\n\nWill you attempt to unlock it?"
            Global.App.ShowNewDialog(String, ButtonGroup.YesNo, Callback = DisarmCommand)
    def DoMazeHelp(self):
        import Instructions
        self.ShowNewDialog(Instructions.HelpText)
    def ShowWordEntryDialog(self, Text, Callback, MaxLen = None, LegalChars = None):
        NewScreen = NewDialogScreen.WordEntryScreen(Text, Callback, MaxLen, LegalChars)
        self.PushNewScreen(NewScreen)
    def ShowNewDialog(self, Text, *args, **kw):
        # Repaint the top screen:
        if self.ScreenStack:
            self.ScreenStack[-1].ForegroundSprites.draw(self.ScreenStack[-1].Surface)
            self.ScreenStack[-1].AnimationSprites.draw(self.ScreenStack[-1].Surface) 
        # And lay the dialog on top:
        NewScreen = NewDialogScreen.DialogScreen(self, Text, *args, **kw)
        self.PushNewScreen(NewScreen)
    def PopCurrentScreen(self):
        "Destroy the top screen"
        del self.ScreenStack[-1]
        if len(self.ScreenStack):
            self.CurrentScreen=self.ScreenStack[-1]
            self.ScreenStack[-1].Activate()
    def PopScreen(self,Screen):
        "Pop a screen (not necessarily the top one)"
        if self.CurrentScreen==Screen:
            KilledCurrent = 1
        else:
            KilledCurrent = 0
        try:
            Index = self.ScreenStack.index(Screen)
        except:
            return
        del self.ScreenStack[Index]
        if KilledCurrent:
            if len(self.ScreenStack):
                self.CurrentScreen=self.ScreenStack[-1]
                self.ScreenStack[-1].Activate()
            
    def PushNewScreen(self,Screen,ActivateNow = 1):
        "Activate a new screen"
        self.ScreenStack.append(Screen)
        self.CurrentScreen=Screen
    def GetMainSurface(self):
        return self.Surface
    def SetScreenSize(self,NewScreenSize):
        """
        Note: Tendrils currently assumes the screen is 800x600.  (Any bigger than that, and some of the
        pictures look a little teeny)
        """
        if NewScreenSize == (self.Width,self.Height):
            return # Same as the old boss!
        if not self.Surface:
            self.Surface = pygame.display.set_mode(NewScreenSize)
        # Update ourself:
        self.Width = self.Surface.get_width()
        self.Height = self.Surface.get_height()
        self.Surface.fill(Colors.Black)        
        self.Surface.set_colorkey(Colors.Black)
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(),self.Surface.get_height()))
        #self.BackgroundSurface.set_colorkey((11,11,11))
        self.BackgroundSurface.fill(Colors.Black)         
        self.Surface.blit(self.BackgroundSurface, (0,0))
        pygame.display.flip()
        pygame.display.set_caption("Tendrils")
        pygame.mouse.set_visible(1)
        # Ok, tell the screens about it too!
        for Screen in self.ScreenStack:
            Screen.Reactivate()
            Screen.Activate()
    def SetupScreen(self,FullScreenMode):
        "Setup the Tendrils screen"
        if self.Surface:
            return
        ScreenSize = (800,600)
        self.Surface = pygame.display.set_mode(ScreenSize) #, pygame.FULLSCREEN) ## Windowed display!  (full-screen has issues, I think)
        return
    def BeginRandomBattle(self, LeaveChest = 0):
        Monsters = Global.Bestiary.GetRandomEncounter(Global.Maze.Level)
        # Special:
        if Global.Maze.Level >= 10:

            for MonsterRank in Monsters:
                for Monster in MonsterRank:
                    if Monster.Species.Level < 10:
                        Monster.RollStats(10)
        if LeaveChest:
            BootyTuple = Global.QuarterMaster.GetRandomBooty(Global.Maze.Level)
        else:
            BootyTuple = None
        if random.random() > 0.5:
            AmbushFlag = 1
        else:
            AmbushFlag = 0
        self.BeginBattle(Monsters, BootyTuple, AmbushFlag = AmbushFlag)
    def BeginBattle(self, Monsters, Booty = None, SongFileName = None,
                    BossBattleName = None, CanFlee = 1, AmbushFlag = 0):
        "Start combat!"
        if not Booty:
            Booty = ({},{},0) # Nothing but some gp!
        Global.Party.GetNextRandomBattle()
        print "Tendrils.BeginBattle() : CanFlee", CanFlee
        if SongFileName:
            self.BeginBattleSongSelect(Monsters, Booty, BossBattleName, CanFlee, AmbushFlag, SongFileName)
        else:
            Callback = lambda S,T,Monsters=Monsters, Booty=Booty, BossBattleName=BossBattleName, \
                CanFlee=CanFlee,AmbushFlag=AmbushFlag: self.BeginBattleSongSelect(Monsters,Booty,
                BossBattleName, CanFlee, AmbushFlag, S)
            Bard.GetBattleSong(Global.Maze.Level, Callback)
            return
    def BeginBattleSongSelect(self,Monsters, Booty, BossBattleName, CanFlee, AmbushFlag, SongName):
        "Song is SELECTED."
        import BattleScreen
        if AmbushFlag and Global.Party.KeyItemFlags.get("Sniper Rifle"):
            Music.FadeOut()
            Str = "<CN:BRIGHTRED>Monsters!</C>\n\nBut, you manage to ambush them.\n\nPREPARE TO SNIPE!"
            self.ShowNewDialog(Str, Callback = lambda Monsters=Monsters, Booty=Booty,
                               SongName=SongName, BossBattleName=BossBattleName,
                               CanFlee=CanFlee: self.StartAmbushBattle(Monsters, Booty, SongName, 
                                                                       BossBattleName, CanFlee))
            return
        NewScreen = BattleScreen.BattleScreen(self, Monsters, Booty, SongName, BossBattleName, CanFlee)
        NewScreen.StartBattle()
        self.PushNewScreen(NewScreen)
##        if AmbushFlag and Global.Party.KeyItemFlags.get("Sniper Rifle"):
##            NewScreen = SnipeScreen.SnipeScreen(MergedMonsterList)
##            self.PushNewScreen(NewScreen)
    def StartAmbushBattle(self, Monsters, Booty, SongFileName, BossBattleName, CanFlee):
        import BattleScreen
        import SnipeScreen
        NewScreen = BattleScreen.BattleScreen(self, Monsters, Booty, SongFileName, BossBattleName)
        NewScreen.StartBattle()
        Global.Party.GetNextRandomBattle()
        self.PushNewScreen(NewScreen)
        MergedMonsterList = []
        for MonsterSubList in Monsters:
            MergedMonsterList.extend(MonsterSubList)
        NewScreen = SnipeScreen.SnipeScreen(self, MergedMonsterList)
        self.PushNewScreen(NewScreen)
        
    def MakeTestParty(self):
        "For testing: Make a party"
        Party.GetTestParty()
        Global.Maze = Maze.Maze(1)
        Global.Maze.Load()
    def ShowEquipScreen(self, Player):
        import EquipScreen
        NewScreen = EquipScreen.EquipScreen(self, Player)
        self.PushNewScreen(NewScreen)
        return
    def CommandLineBattle(self):
        Monsters = []
        Song = None

        for Arg in sys.argv[1:]:
            Ext = os.path.splitext(Arg)[1]
            if Ext.upper() in [".XM",".IT",".MOD",".MP3", ".OGG"]:
                Song = Arg
            elif Arg.upper() == "BATTLE":
                continue
            else:
                try:
                    Diff = int(Arg)
                    Diff = min(max(Diff, 0), 2)
                    Global.Party.Options["SongDifficulty"] = Diff
                except:
                    Monster = Global.Bestiary.GetCritter(Arg)
                    Monsters.append(Monster)
        if Monsters:
            Monsters = [Monsters]
        else:
            Monsters = Critter.GetTestMonsters()
        BootyTuple = Global.QuarterMaster.GetRandomBooty(Global.Maze.Level)
        self.BeginBattle(Monsters, BootyTuple, SongFileName = Song, AmbushFlag = 1)
    def ShowInn(self):
        import InnScreen
        NewScreen = InnScreen.InnScreen(self)
        self.PushNewScreen(NewScreen)        
    def GoShopping(self, ShopInventory, ShopName, ShopImageName = None):
        import ShopScreen
        NewScreen = ShopScreen.ShopScreen(self, ShopInventory, ShopName, ShopImageName)
        self.PushNewScreen(NewScreen)
    def DoOptions(self):
        import OptionsScreen
        NewScreen = OptionsScreen.OptionsScreen(self)
        self.PushNewScreen(NewScreen)
    def DoNPC(self, Name):
        import NPCScreen
        DialogTree = NPC.DialogTree(Name)
        DialogTree.Load()
        NewScreen = NPCScreen.NPCScreen(self, Name, DialogTree)
        self.PushNewScreen(NewScreen)
    def ShowSnipeScreen(self, Monsters):
        import SnipeScreen
        NewScreen = SnipeScreen.SnipeScreen(self, Monsters)
        self.PushNewScreen(NewScreen)
    def DoVictory(self):
        import VictoryScreen
        NewScreen = VictoryScreen.VictoryScreen(self)
        self.PushNewScreen(NewScreen)
    def ShowBlezmonScreen(self, FreePlay = 0):
        import BlezmonScreen
        NewScreen = BlezmonScreen.BlezmonScreen(self, FreePlay)
        self.PushNewScreen(NewScreen)
    def ShowSolitaireScreen(self, FreePlay = 0):
        import SolitaireScreen
        NewScreen = SolitaireScreen.SolitaireScreen(self, FreePlay)
        self.PushNewScreen(NewScreen)
        
    def ShowTowerScreen(self):
        import TowerScreen
        NewScreen = TowerScreen.TowerScreen(self)
        self.PushNewScreen(NewScreen)
    def ShowBlinkenlightsScreen(self):
        import Blinkenlights
        NewScreen = Blinkenlights.BlinkenScreen(self)
        self.PushNewScreen(NewScreen)
    def ShowPegSolitaireScreen(self, SolveCallback = None, FreePlay = 0, PuzzleName = None ):
        import PegScreen
        NewScreen = PegScreen.PegScreen(self, SolveCallback = SolveCallback, FreePlay = FreePlay, PuzzleName = PuzzleName)
        self.PushNewScreen(NewScreen)
    def ShowJoustPongScreen(self, FreePlay = 0):
        import JoustPongScreen
        NewScreen = JoustPongScreen.JoustPongScreen(self, FreePlay)
        self.PushNewScreen(NewScreen)
    def ShowDalekScreen(self, FreePlay = 0):
        import DalekScreen
        NewScreen = DalekScreen.DalekScreen(self, FreePlay)

        self.PushNewScreen(NewScreen)
    def StartFreePlay(self):
        import FreePlayScreen
        NewScreen = FreePlayScreen.FreePlayScreen()
        self.PushNewScreen(NewScreen)
    def ShowWormScreen(self):
        import WormScreen
        NewScreen = WormScreen.WormScreen(self)
        self.PushNewScreen(NewScreen)
    def ShowBlockScreen(self, Name = None, Callback = None, FreePlay = 0): #"Hughes", Callback = None):
        import BlockScreen
        NewScreen = BlockScreen.BlockScreen(self, Name, Callback, FreePlay)
        self.PushNewScreen(NewScreen)
    def ShowPracticeScreen(self, InitialState = None, Song = None):
        import PracticeScreen
        if InitialState == None:
            InitialState = PracticeScreen.PracticeStates.Learning1
        #NewScreen = PracticeScreen.PracticeScreen(self, PracticeScreen.PracticeStates.Learning1, RequestedSong = Song)
        print "SPS:", Song
        NewScreen = PracticeScreen.PracticeScreen(self, InitialState, RequestedSong = Song)
        NewScreen.StartBattle()
        self.PushNewScreen(NewScreen)
    def ShowFirstScreen(self):
        import FirstScreen
        NewScreen = FirstScreen.FirstScreen(self, sys.argv)
        self.PushNewScreen(NewScreen)
    def StartScreens(self):
        "Create the first screen and start the game"
        self.MakeTestParty()
        ##Global.Party = self.Party
        self.ScreenStack = []
        if self.Command == CommandLines.Solitaire:
            self.ShowSolitaireScreen()
            return
        if self.Command == CommandLines.Blezmon:
            self.ShowBlezmonScreen()
            return
        if self.Command == CommandLines.Tower:
            self.ShowTowerScreen()
            return
        if self.Command == CommandLines.Dalek:
            self.ShowDalekScreen()
            return
        if self.Command == CommandLines.JoustPong:
            self.ShowJoustPongScreen()
            return
        if self.Command == CommandLines.Pegs:
            self.ShowPegSolitaireScreen()
            return
        if self.Command == CommandLines.Blinkenlights:
            self.ShowBlinkenlightsScreen()
            return
        
        if self.Command == CommandLines.FreePlay:
            self.StartFreePlay()
            return
        if self.Command == CommandLines.Practice:
            self.ShowPracticeScreen()
            return
        if self.Command == CommandLines.Block:
            self.ShowBlockScreen()
            return
        if self.Command == CommandLines.Worm:
            self.ShowWormScreen()
            return
        if self.Command == CommandLines.Victory:
            self.DoVictory()
            return
        if self.Command == CommandLines.Trivia:
            self.StartTrivia()
            return
        if self.Command == CommandLines.Equip:
            self.ShowEquipScreen(Global.Party.Players[0])
            return
        if self.Command == CommandLines.Snipe:
            # Test snipe monsters:
            Monsters = []
            Monsters.append(Global.Bestiary.GetCritter("Goomba"))
            Monsters.append(Global.Bestiary.GetCritter("Shyguy"))
            Monsters.append(Global.Bestiary.GetCritter("Goomba"))
            Monsters.append(Global.Bestiary.GetCritter("Shyguy"))
            Monsters.append(Global.Bestiary.GetCritter("Goomba"))

            
            self.ShowSnipeScreen(Monsters)
            return
        if self.Command == CommandLines.Options:
            self.DoOptions()
            return
        if self.Command == CommandLines.NPC:
            if len(sys.argv)>2:
                Name = sys.argv[2]
            else:
                Name = "KittyGirl"
            self.DoNPC(Name)
            return
        if self.Command == CommandLines.Shop:
            TestShopInventory = Global.QuarterMaster.Items.copy()
            self.GoShopping(TestShopInventory, "Little Shop of Horrors")
            return
        if self.Command == CommandLines.Map:
            NewScreen = Maze.MapScreen(self, sys.argv)
            self.PushNewScreen(NewScreen)
            return
        if self.Command == CommandLines.Play:
            Global.Maze.Level = 1
            Global.Maze.Load()
            Global.Party = Party.GetNewParty()
            self.ShowTheMaze(1)
            self.ShowFirstScreen()
            return
        if self.Command == CommandLines.Battle:
            self.CommandLineBattle()            
            return
        if self.Command == CommandLines.Inn:
            self.ShowInn()     
            return
        if self.Command == CommandLines.Maze:
            try:
                Global.Party.X = int(sys.argv[2])
                Global.Party.Y = int(sys.argv[3])
                Global.Party.Z = int(sys.argv[4])
                Global.Maze.Level = int(sys.argv[4])
                Global.Maze.Load()
            except:
                pass
            self.ShowTheMaze()
            return
        if self.Command == CommandLines.Save:
            self.SaveGame()
            return
        if self.Command == CommandLines.Chest:
            ChestLevel = Global.Maze.Level
            try:
                ChestLevel = int(sys.argv[2])
            except:
                pass
            BootyTuple = Global.QuarterMaster.GetRandomBooty(ChestLevel)
            self.DisarmChest(BootyTuple[0], BootyTuple[1], BootyTuple[2], Level = ChestLevel)
            return
        # DEFAULT:
        import WelcomeScreen
        NewScreen = WelcomeScreen.WelcomeScreen(self)
        self.PushNewScreen(NewScreen)
        return
    def DisarmChest(self, ChestItems = {}, ChestSpecial = {}, BootyType = 2, Lock = None, Trap = None, Level = None):
        import ChestScreen
        if not Level:
            Level = Global.Maze.Level
        if not Lock:
            (Lock, Trap) = ChestScreen.RollRandomTrap(BootyType, Level)
        NewScreen = ChestScreen.ChestScreen(self, Lock, Trap, ChestItems, ChestSpecial, BootyType, Level)
        self.PushNewScreen(NewScreen)
    def ShowTheMaze(self, NewGame = 0):
        import MazeScreen
        NewScreen = MazeScreen.MazeScreen(self)
        if NewGame:
            NewScreen.AddAnimationSprite(MazeScreen.HelperSprite(NewScreen))

        self.PushNewScreen(NewScreen)
    def ShowLoadScreen(self):
        import SaveScreen
        NewScreen = SaveScreen.LoadScreen(self)
        self.PushNewScreen(NewScreen)
    def ShowJoyConfig(self):
        import JoyConfigScreen
        NewScreen = JoyConfigScreen.JoyConfigScreen()
        self.PushNewScreen(NewScreen)
    def SaveGame(self):
        import SaveScreen
        NewScreen = SaveScreen.SaveScreen(self)
        self.PushNewScreen(NewScreen)
    def SetupTendrils(self,Command):
        "Perform various initialization when starting the application"
        self.Command=Command
        pygame.mixer.pre_init(44100,-16,2, 1024)
        pygame.init()
        pygame.mixer.init()
        pygame.mouse.set_visible(1)
        pygame.joystick.init()
        JoystickCount = pygame.joystick.get_count()
        print "JOY COUNT:", JoystickCount
        if JoystickCount:
            Stick = pygame.joystick.Joystick(0)
            Stick.init()
            print "STICK INIT!"
        Global.JoyConfig = JoyConfigClass()
        Global.JoyConfig.Load(Global.MemoryCard)
        if Command == "PLAY":
            self.SetupScreen(1) # 1! %%%
        else:
            self.SetupScreen(0)
        self.Width = self.Surface.get_width()
        self.Height = self.Surface.get_height()
        ###Glue(r"D:\Tendrils\Images\Magic\Blizzard.%s.png", 20) #%%%
        # We use two surfaces: Surface and BackgroundSurface.  They both cover the whole window.  We
        # generally use three sprite groups: BackgroundSprites (which
        # draw on the BackgroudnSurface), ForegroundSprites (draw on Surface), and AnimationSprites (draw on Surface, ON TOP OF
        # any ForegroundSprites).  The BackgroundSurface is for stuff that's not repainted often.  The color black is
        # transparent on the foreground surface, allowing background images to shine through)        
        self.Surface.fill(Colors.Black)
        self.Surface.set_colorkey(Colors.Black)
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(),self.Surface.get_height()))
        self.BackgroundSurface.fill(Colors.Black)         
        self.Surface.blit(self.BackgroundSurface, (0,0))
        pygame.display.flip()
        pygame.display.set_caption("Tendrils")
        pygame.mouse.set_visible(1)
        BuildHappyFonts()
        self.MasterClock = pygame.time.Clock()
        Critter.DefaultAnimation.LoadImages("")
        Global.NullImage = pygame.Surface((0,0))
        Global.AmmoDump = Critter.AmmoDump()
    def PlayTendrils(self):
        "This is the main method for the program - when it terminates, execution is over!"
        self.StartScreens()
        TidyCount = 0
        pygame.display.flip()
        self.OldCurrentScreen = None
        if self.Quitting:
            return
        OldTime = time.time()
        while 1:
            self.MasterClock.tick(MAX_FPS)
            Time = time.time()
            if (Time > OldTime):
                Global.Party.TotalPlayTime += 1
            OldTime = Time
            pygame.event.pump()
            # Periodically clean up cached resources, to save memory:
            TidyCount += 1
            if TidyCount>=4096:
                CleanFontCache()
                Resources.CleanImageCache()
                Resources.CleanSoundCache()
                TidyCount=0
            if len(self.ScreenStack)<1:
                # Popped last screen.  Bye!
                return 
            self.CurrentScreen = self.ScreenStack[-1]
            try:                
                self.CurrentScreen.HandleLoop()
            except:
                print "** ERROR handling events! **"
                traceback.print_exc()

            # Handle screen-switches:
            if self.OldCurrentScreen!=self.CurrentScreen:
                self.OldCurrentScreen = self.CurrentScreen
                self.CurrentScreen.Activate()
##            DirtyRects = self.AnimationSprites.draw(self.Surface)
            #Dirty(DirtyRects)
            UpdateDirtyRectangles()
            ##pygame.display.flip() ###
            if self.Quitting:
                print "FPS:",self.MasterClock.get_fps()
                return
    def DismissDialog(self,Dialog,Command):
        "Dismiss a dialog screen.  If there's a callback function, call it!  Pass the button that was pressed, if any"
        if Dialog.Callback:
            apply(Dialog.Callback, [Command])
        self.PopScreen(Dialog)
    def DismissDialogBox(self, Dialog, CallbackFunction):
        self.PopScreen(Dialog)
        if CallbackFunction:
            apply(CallbackFunction)
    def RiddleCallback(self, Number, RightAnswers, Answer):
        # Somewhat hacky to put this function here, but...
        # This is a callback for the word-entry dialogs when answering riddles from NPC.
        # The Number identifies the riddle, and the Answer is user's entry.
        print "RIDDLE CALLBACK!"
        print Number, RightAnswers, Answer
        print len(self.ScreenStack)
        NPCScreen = self.ScreenStack[-1]
        print "NPCScreen:", NPCScreen        
        if Answer:
            Answer = Answer.lower()
        if Answer in RightAnswers:
            Global.Party.EventFlags["Riddle:%s"%Number] = 1
            NextNode = NPCScreen.DialogTree.GetNode("Correct")
        else:
            NextNode = NPCScreen.DialogTree.GetNode("Incorrect")
        NPCScreen.Node = NextNode
        NPCScreen.DrawDialogNode()
            
def Main():
    if len(sys.argv)>1:
        Command = sys.argv[1].upper()
    else:
        Command = "" # CommandLines.Play
    App = TendrilsApplication()
    App.SetupTendrils(Command.lower())
    App.PlayTendrils()
    

if __name__=="__main__":
    print "Tendrils Startup..."
    if PSYCO_ON:
        psyco.bind(pygame.sprite.spritecollideany)
        psyco.bind(Resources.PreloadImageCache)
        psyco.bind(Resources.GetImage)
        psyco.bind(os.path.join)
        psyco.bind(Critter.Player.Equip)
        psyco.bind(NPC.DialogTree.Load)
        psyco.bind(pygame.sprite.RenderUpdates.draw)
        psyco.bind(Critter.Critter.GetResistedDamage)
        psyco.bind(pygame.sprite.Sprite.add)
        psyco.bind(TendrilsApplication.PlayTendrils)
        psyco.bind(pygame.sprite.Sprite.kill)
    Main()
    # THE END.
