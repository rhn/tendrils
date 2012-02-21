"""
Ok, just one more screen.  The PRACTICE screen.
This screen is the little brother of the BattleScreen.  It displays arrows, and can handle
arrow-hitting; however, it doesn't do any real battle.  This screen displays various instructions
to walk people through the basics of battle.  It could also be used for a "practice" room in the
dungeon!
"""
from Constants import *
from Utils import *
import Screen
import Global
import Resources
import time
import Music 
import Critter
import Magic
from BattleSprites import *
from DancingScreen import *
import BattleResults
import Instructions

class PracticeStates:
    Paused = 0
    Playing = 1 # No player sprites
    Sparring = 2
    Quitting = 3
    Learning1 = 4
    Learning2 = 5
    Transitioning = 6 # brief pause between songs!


class PracticeScreen(DancingScreen):
    def __init__(self, App, StartState = PracticeStates.Playing, RequestedSong = None, SongTempo = 1.0):
        if StartState == PracticeStates.Sparring:
            Monsters = self.GetRandomMonsters()
        else:
            Monsters = []
        DancingScreen.__init__(self, App, Monsters, None)
        self.SilentFlag = 1 # No battle noise!
        self.EventHandlers["NextSong"] = self.HandleNextSong
        self.ButtonSprites = pygame.sprite.Group()
        self.InstructionSprites = []
        self.State = StartState
        self.RequestedSong = RequestedSong
        self.SongIndex = 0
    def GetRandomMonsters(self):
        Level = random.randrange(1, 9)
        Monsters = Global.Bestiary.GetRandomEncounter(Level)
        return Monsters
    def StartBattle(self):
        "Prepare for battle!  Generate all the sprites, and START THE MUSIC!"
        print "DRAW BACKGROUND:"
        self.DrawBackground()
        if self.State == PracticeStates.Sparring:
            self.DrawPlayers()
            self.DrawMonsters()
        self.Streak = 0
        self.ComboSprite = ComboSprite(self.Streak, 75, 180)
        self.AddAnimationSprite(self.ComboSprite)
        self.StartScreen(self.State)
        #self.SummonSong(self.RequestedSong)
    def EraseInstructions(self):
        for Sprite in self.InstructionSprites:
            Sprite.kill()
        self.InstructionSprites = []
    def ShowInstructions(self, String, ButtonString = "Ok"):
        Image = TaggedRenderer.RenderToImage(String, 600)
        Sprite = GenericImageSprite(Image, 170, 50)
        self.InstructionSprites.append(Sprite)
        self.AddBackgroundSprite(Sprite)
        #
        ButtonSprite = FancyAssBoxedSprite(ButtonString, 500, 500, HighlightIndex = 0)
        ButtonSprite.rect.center = (475, Sprite.rect.bottom + 25)
        self.InstructionSprites.append(ButtonSprite)
        self.AddBackgroundSprite(ButtonSprite)
        self.ButtonSprites.add(ButtonSprite)
    def StartScreen(self, State):
        if State == PracticeStates.Learning1:
            self.State = PracticeStates.Learning1
            self.ShowInstructions(Instructions.DanceInstructions1)
        elif State == PracticeStates.Playing:
            self.State = PracticeStates.Sparring
            self.ShowGlowingText("Music Practice", 250)
            self.ShowGlowingText("This is galactic dancing!", 300, 100)
            self.DrawSparringStuff()
            self.StartTheMusic()
            self.Redraw()
        elif State == PracticeStates.Sparring:
            self.ShowGlowingText("Get Ready!", 300, 50)
            self.DrawSparringStuff()
            self.StartTheMusic()
            self.Redraw()            
        self.State = State
    def HandleNextSong(self, Time):
        #print "HandleNextSong!!"
        self.State = PracticeStates.Sparring
        for Monster in self.MonsterSprites:
            Monster.kill()
        self.MonsterSprites = []
        self.MonsterRanks = self.GetRandomMonsters()
        self.Monsters = [] # A flat list of all monsters
        for Rank in self.MonsterRanks:
            self.Monsters.extend(Rank)
        self.AliveMonsters = self.Monsters[:] # Dynamic list of living monsters
        self.DrawMonsters()
        self.State = PracticeStates.Sparring
        self.StartTheMusic()
    def StartTheMusic(self):
        if not self.RequestedSong:
            Song = Global.MusicLibrary.GetBattleSong("MetalGear.xm")
        elif self.DoingCourse():
            Song = self.RequestedSong[self.SongIndex]
            self.SongIndex = (self.SongIndex + 1)
        else:
            Song = self.RequestedSong
        if hasattr(self, "SongInfoSprite") and self.SongInfoSprite:
            self.SongInfoSprite.kill()
        self.SongInfoSprite = Screen.SongInfoSprite(self, Song, 600)
        self.SongInfoSprite.PermanentFlag = 1
        self.SongInfoSprite.image.set_alpha(255)
        self.AddBackgroundSprite(self.SongInfoSprite)
        self.Redraw()
        for Sprite in self.ArrowSprites.sprites():
            Sprite.kill()
        self.Arrows = {}
        self.ArrowList = []
        Music.PlaySong(Song)
    def DrawBattleBackground(self):
        Image = Resources.GetImage(os.path.join("Images", "Background", "Bards.png"))
        Image = pygame.transform.scale(Image, (650, 435))
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
    def DoingCourse(self):
        return (type(self.RequestedSong) in (type([]), types.TupleType))
    def DrawSparringStuff(self):
        Image = TextImage("Tendrils Freestyle", FontSize = 24)
        Sprite = GenericImageSprite(Image, 180, 480)
        self.AddForegroundSprite(Sprite)
        #
        ButtonSprite = FancyAssBoxedSprite("Quit", 180, 530, HighlightIndex = 0)
        self.ButtonSprites.add(ButtonSprite)
        self.AddForegroundSprite(ButtonSprite)
        #
        if self.DoingCourse():
            if len(self.RequestedSong)>3:
                ButtonSprite = FancyAssBoxedSprite("Prev", 280, 530, HighlightIndex = 0)
                self.ButtonSprites.add(ButtonSprite)
                self.AddForegroundSprite(ButtonSprite)
            ButtonSprite = FancyAssBoxedSprite("Next", 340, 530, HighlightIndex = 0)
            self.ButtonSprites.add(ButtonSprite)
            self.AddForegroundSprite(ButtonSprite)
    def FinishLearning1(self):
        self.EraseInstructions()
        self.ShowInstructions(Instructions.DanceInstructions2)
        self.State = PracticeStates.Learning2
        self.Redraw()
        Resources.PlayStandardSound("Bleep2.wav")
    def FinishLearning2(self):
        self.EraseInstructions()
        self.ShowInstructions(Instructions.DanceInstructions3, "Quit")
        self.State = PracticeStates.Playing
        self.StartTheMusic()
        self.Redraw()
        Resources.PlayStandardSound("Bleep2.wav")
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # Click on Ok or Quit buttons
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            if self.State == PracticeStates.Learning1:
                self.FinishLearning1()
            elif self.State == PracticeStates.Learning2:
                self.FinishLearning2()
            elif self.State in (PracticeStates.Playing, PracticeStates.Sparring):
                if Sprite.Text == "Quit":
                    self.Quit()
                elif Sprite.Text == "Next":
                    self.ClickNext()
                elif Sprite.Text == "Prev":
                    self.ClickPrev()
    def DoJudging(self):
        "CALIBRATION!"
        Count = len(self.Whiffs)
        if Count:
            print "---(calibration)---"
            Total = 0
            for Item in self.Whiffs:
                Total += Item
            Average = Total / float(Count)
            print "Average arrow ticks remaining: %.2f"%Average
            if Count>2:
                HalfwayPoint = Count/2
                HalfTotal = 0
                MiniCount = 0
                for Item in self.Whiffs[:HalfwayPoint]:
                    HalfTotal += Item
                    MiniCount += 1
                print "Average in first half (up to %d): %.2f"%(HalfwayPoint, HalfTotal / float(MiniCount))
                HalfTotal = 0
                MiniCount = 0
                for Item in self.Whiffs[HalfwayPoint:]:
                    HalfTotal += Item
                    MiniCount += 1
                print "Average in last half: %.2f"%(HalfTotal / float(MiniCount))
        self.Whiffs = []
    def HandleSongComplete(self):
        #print "PracticeScreen::HandleSongComplete()"
        Music.FadeOut()
        self.DoJudging()
        #print self.SongIndex
        #print self.DoingCourse()
        if not self.DoingCourse():
            self.Quit()
            return
        if self.SongIndex >= len(self.RequestedSong):
            if len(self.RequestedSong)>3:
                self.SongIndex = 0 # wrap around!
            else:
                self.Quit()
                return
        self.Arrows = {}
        self.ArrowList = []
        TriggerCycle = (self.AnimationCycle + 100)%MaxAnimationCycle
        self.PendingEvents.append(("NextSong", TriggerCycle))
        for Sprite in self.ArrowSprites.sprites():
            Sprite.kill()
        self.State = PracticeStates.Transitioning
        self.ComboSprite.image = Global.NullImage
        self.ShowGlowingText("Get Ready!", 300, 0)
    def ClickNext(self):
        if self.State == PracticeStates.Transitioning or self.PauseFlag:
            return
        #self.SongIndex += 1
        Music.FadeOut()
        self.HandleSongComplete()
    def ClickPrev(self):
        if self.State == PracticeStates.Transitioning or self.PauseFlag:
            return        
        self.SongIndex = max(0, self.SongIndex - 2)
        Music.FadeOut()
        self.HandleSongComplete()
    def Quit(self):
        Music.FadeOut()
        Count = 0
        for Quality in HitQuality.AllQualities:
            Count += self.HitTotals[Quality]
        if Count:
            Callback = self.Dismiss
            Dialog = BattleResults.BattleFeedback(self.HitTotals, Callback, "<CENTER><CN:ORANGE>Completed</C></CENTER>")
            Global.App.PushNewScreen(Dialog)
        else:
            self.Dismiss()
    def Dismiss(self):
        Global.App.PopScreen(self)
        return
    def HandleKeyPressed(self, Key):
        if Key == 113: # Q is for Quit:
            if self.State in (PracticeStates.Playing, PracticeStates.Sparring):
                self.Quit()
        elif Key in (13, ord("o")):
            if self.State == PracticeStates.Learning1:
                self.FinishLearning1()
            elif self.State == PracticeStates.Learning2:
                self.FinishLearning2()
        elif Key == ord("p"):
            self.ClickPrev()
            return
        elif Key == ord("n"):
            self.ClickNext()
            return
        elif Key == Keystrokes.Debug:
            Music.FadeOut()
            self.HandleSongComplete()
        else:
            DancingScreen.HandleKeyPressed(self, Key)
    def Update(self):
        self.MoveArrows()
    def DisplayBouncyNumber(self, X, Y, Number, Color = Colors.White):
        "Display a bouncy numbered, CENTERED around the given X coordinate"
        DigitWidth=10 # hard coded :(
        if Number>0:
            Str = random.choice(("Biff!","Pow!","Hit!","Hit!","Hit!","Hit!"))
        else:
            Str = "Miss"
        X = X - int(DigitWidth * len(Str)/2.0)
        for Index in range(len(Str)):
            Digit = Str[Index]
            Sprite = BouncyNumber(Digit,X+(DigitWidth*Index),Y,Color,Index*5)
            self.AddAnimationSprite(Sprite)
    def HandleLoop(self):
        "We override HandleLoop so that we can render our fancy ArrowSprites correctly"
        if not self.PauseFlag:        
            self.AnimationCycle+=1        
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface)
        self.ArrowSprites.clear(self.Surface,self.BackgroundSurface) 
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface)
        if (self.AnimationCycle>MaxAnimationCycle):
            self.AnimationCycle=0
        if not self.PauseFlag:
            for Sprite in self.AllSprites.sprites():
                Sprite.Update(self.AnimationCycle)
        if self.State != PracticeStates.Transitioning:
            self.Update()
        self.HandleEvents()
        self.HandlePendingEvents() # animation starter events.  Do this LAST, in case we triggered one with no delay
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        if not self.PauseFlag:
            DirtyRects = self.ArrowSprites.draw(self.Surface) 
            Dirty(DirtyRects)
    
        