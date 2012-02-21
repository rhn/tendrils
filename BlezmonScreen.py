"""
Blezmon screen (a clone of Yahtzee).  The player rolls the 5 dice,
clicking on the dice to keep (with up to two re-rolls).  Then they
click on a ROW to apply their score.  Clicking on a row their roll
doesn't fit...results in a cross-out.
"""
from Utils import *
from Constants import *
import Screen
import ItemPanel
import Global
import Resources
import os
import time
import math
import string
import Party
import ChestScreen

HelpText = """<center><CN:ORANGE>Blezmon Rules</C></center>
You can roll the dice <CN:BRIGHTGREEN>3</c> times on your turn.  You can re-roll some or all of the dice.  Click \
on the dice you want to keep.  Once you're done rolling, click a row on your scorecard to earn points.  The row \
is "crossed off" once you use it, and can't be used again.

<CN:Yellow>Number rows</C>: Roll as many of one number as possible; score points for that number only.  For instance, \
if you roll three sixes, you can score 18 on the <CN:GREEN>sixes</C> row.  If you score at least \
<CN:GREEN>63</C> points on the number rows, you get a <CN:GREEN>par bonus</C> of 35 points.

<CN:YELLOW>3 of a kind</C>: Roll at least 3 of any number.  Score the total of all 5 dice.

<CN:YELLOW>4 of a kind</C>: Roll at least 4 of any number.  Score the total of all 5 dice.

<CN:YELLOW>Small Straight</C>: Roll 4 number in a row (for example: 3,4,5,6).  Score <CN:GREEN>30</C> points.

<CN:YELLOW>Large Straight</C>: Roll 5 number in a row (for example: 1,2,3,4,5).  Score <CN:GREEN>40</C> points.

<CN:YELLOW>Full House</C>: Roll 2 of one number and 3 of another (for example: 2,2,2,6,6).  Score <CN:GREEN>25</C> points.

<CN:YELLOW>Blezmon</C>: Roll 5 of any number.  Score <CN:BRIGHTGREEN>50</C> points!

<CN:YELLOW>Chance</C>: The "leftovers" row, you can always take it.  Use it when you can't fill in anything \
else, so that you don't have to cross something off!  Score the total of all 5 dice.
"""

BScreen = None

class BlezmonRow:
    "A scorecard row type"
    def __init__(self, Name):
        self.Name = Name
    def GetScore(self, DieList):
        """
        Returns tuple of the form (Score, DieIndices), where Score is the best achievable score with this
        hand, and DieIndices is the list of indices used.
        """
        raise ValueError, "AbstractMethod"
    def GetPlausibleScore(self, DieList):
        """
        Returns tuple of the form (Score, Odds, DieIndices), where Score is a score to aim for after
        re-roll, Odds the odds of reaching it, and DieIndices the dice to keep.  This doesn't have to
        be accurate, just CLOSE enough to make the AI a non-pathetic opponent.
        """
        raise ValueError, "AbstractMethod"

class BlezmonRowNumber:
    "The 'ones', 'twos', ..., 'sixes' rows"
    def __init__(self, Name, Number):
        self.Name = Name
        self.Number = Number
    def GetScore(self, DieList):
        Total = 0
        Indices = []
        for Index in range(len(DieList)):
            Die = DieList[Index]
            if (Die == self.Number):
                Total += Die
                Indices.append(Index)
        return (Total, Indices)
    def GetPlausibleScore(self, DieList):
        Total = 0
        Rerolls = 0
        Indices = []
        for Index in range(len(DieList)):
            Die = DieList[Index]
            if (Die == self.Number):
                Total += Die
                Indices.append(Index)
            else:
                Rerolls += 1
        return (Total, 1.0, Indices)


class BlezmonRow3Kind:
    def __init__(self):
        self.Name = "3 of a Kind"
    def GetScore(self, DieList):
        Counts = [0]*6
        Total = 0
        KeepIndices = []
        # Count dice of each type:
        for Index in range(len(DieList)):
            Die = DieList[Index]
            Counts[Die-1] += 1
            Total += Die
        # See if we have 3 of a kind:
        CommonNumber = None
        for Pips in range(len(Counts)):
            if Counts[Pips]>=3:
                CommonNumber = Pips+1
        if CommonNumber==None:
            return (0, [])
        for Index in range(len(DieList)):
            if DieList[Index]==CommonNumber:
                KeepIndices.append(Index)
        return (Total, KeepIndices)
    def GetPlausibleScore(self, DieList):
        Counts = [0]*6
        Total = 0
        KeepIndices = []
        # Count dice of each type:
        for Index in range(len(DieList)):
            Die = DieList[Index]
            Counts[Die-1] += 1
        # Find the most common:
        CommonNumber = None
        CommonCount = 0
        for Pips in range(len(Counts)):
            if Counts[Pips]>=CommonCount:
                CommonNumber = Pips+1
                CommonCount = Counts[Pips]
        # If we have 3 of a kind, we reroll any low numbers we're not keeping already:
        if CommonCount>=3:
            for Index in range(len(DieList)):
                if DieList[Index]==CommonNumber:
                    Total += DieList[Index]
                    KeepIndices.append(Index)
                elif DieList[Index]>3:
                    Total += DieList[Index]
                    KeepIndices.append(Index)
                else:
                    Total += 3.5
            return (Total, 1, KeepIndices)
        # We don't have 3-of-a-kind...yet.  Keep the most common number:
        Total = 0
        for Index in range(len(DieList)):
            if DieList[Index]==CommonNumber:
                Total += CommonNumber
                KeepIndices.append(Index)
            else:
                Total += 3.5
        if CommonCount==1: # need 2 more
            Odds = 0.132
        else: # need 1 more
            Odds = 0.421
        return (Total, Odds, KeepIndices)
class BlezmonRow4Kind:
    def __init__(self):
        self.Name = "4 of a Kind"
    def GetScore(self, DieList):
        Counts = [0]*6
        Total = 0
        KeepIndices = []
        # Count dice of each type:
        for Index in range(len(DieList)):
            Die = DieList[Index]
            Counts[Die-1] += 1
            Total += Die
        # See if we have 4 of a kind:
        CommonNumber = None
        for Pips in range(len(Counts)):
            if Counts[Pips]>=4:
                CommonNumber = Pips+1
        if CommonNumber==None:
            return (0, [])
        for Index in range(len(DieList)):
            if DieList[Index]==CommonNumber:
                KeepIndices.append(Index)
        return (Total, KeepIndices)
    def GetPlausibleScore(self, DieList):
        Counts = [0]*6
        Total = 0
        KeepIndices = []
        # Count dice of each type:
        for Index in range(len(DieList)):
            Die = DieList[Index]
            Counts[Die-1] += 1
        # Find the most common:
        CommonNumber = None
        CommonCount = 0
        for Pips in range(len(Counts)):
            if Counts[Pips]>=CommonCount:
                CommonNumber = Pips+1
                CommonCount = Counts[Pips]
        # If we have 4 of a kind, we reroll any low numbers we're not keeping already:
        if CommonCount>=4:
            for Index in range(len(DieList)):
                if DieList[Index]==CommonNumber:
                    Total += DieList[Index]
                    KeepIndices.append(Index)
                elif DieList[Index]>3:
                    Total += DieList[Index]
                    KeepIndices.append(Index)
                else:
                    Total += 3.5
            return (Total, 1, KeepIndices)
        # We don't have 4-of-a-kind...yet.  Keep the most common number:
        Total = 0
        for Index in range(len(DieList)):
            if DieList[Index]==CommonNumber:
                Total += CommonNumber
                KeepIndices.append(Index)
            else:
                Total += 3.5
        print "foo."
        if CommonCount==1: # need 3 more
            Odds = .0085
        elif CommonCount==2:  # need 2 more
            Odds = .074
        else:
            Odds = 0.31
        return (Total, Odds, KeepIndices)


class BlezmonRowSmallStraight:
    def __init__(self):
        self.Name = "Small Straight"
    def GetScore(self, DieList):
        return self.GetSSScore(DieList)
    def GetPlausibleScore(self, DieList):
        return self.GetPlausibleSSScore(DieList)
    def GetSSScore(self, DieList):
        if (1 in DieList and 2 in DieList and 3 in DieList and 4 in DieList):
            return (30, (0,1,2,3,4))
        if (2 in DieList and 3 in DieList and 4 in DieList and 5 in DieList):
            return (30, (0,1,2,3,4))
        if (3 in DieList and 4 in DieList and 5 in DieList and 6 in DieList):
            return (30, (0,1,2,3,4))
        return (0, [])
    def GetPlausibleSSScore(self, DieList):
        # First, see if we have a straight:
        (Score, List) = self.GetScore(DieList)
        if Score:
            return (Score, 1.0, List)
        # Do we have a run of three?
        if (1 in DieList and 2 in DieList and 3 in DieList):
            return (30, 0.31, (DieList.index(1),DieList.index(2),DieList.index(3),))
        if (2 in DieList and 3 in DieList and 4 in DieList):
            return (30, 0.52, (DieList.index(2),DieList.index(3),DieList.index(4),))
        if (3 in DieList and 4 in DieList and 5 in DieList):
            return (30, 0.52, (DieList.index(3),DieList.index(4),DieList.index(5),))
        if (4 in DieList and 5 in DieList and 6 in DieList):
            return (30, 0.31, (DieList.index(4),DieList.index(5),DieList.index(6)))
        # Do we have a broken-run?
        if (1 in DieList and 2 in DieList and 4 in DieList):
            return (30, 0.31, (DieList.index(1),DieList.index(2),DieList.index(4),))
        if (1 in DieList and 3 in DieList and 4 in DieList):
            return (30, 0.31, (DieList.index(1),DieList.index(3),DieList.index(4),))
        if (2 in DieList and 3 in DieList and 5 in DieList):
            return (30, 0.31, (DieList.index(2),DieList.index(3),DieList.index(5),))
        if (2 in DieList and 4 in DieList and 5 in DieList):
            return (30, 0.31, (DieList.index(2),DieList.index(4),DieList.index(5),))
        if (3 in DieList and 4 in DieList and 6 in DieList):
            return (30, 0.31, (DieList.index(3),DieList.index(4),DieList.index(6),))
        if (3 in DieList and 5 in DieList and 6 in DieList):
            return (30, 0.31, (DieList.index(3),DieList.index(5),DieList.index(6),))
        # Odds are...not good.
        return (30, 0.01, [])

class BlezmonRowLargeStraight(BlezmonRowSmallStraight):
    def __init__(self):
        BlezmonRowSmallStraight.__init__(self)
        self.Name = "Large Straight"
    def GetScore(self, DieList):
        if (1 in DieList and 2 in DieList and 3 in DieList and 4 in DieList and 5 in DieList):
            return (40, (0,1,2,3,4))
        if (2 in DieList and 3 in DieList and 4 in DieList and 5 in DieList and 6 in DieList):
            return (40, (0,1,2,3,4))
        return (0,[])
    def GetPlausibleScore(self, DieList):
        # First, see if we have a straight:
        (Score, List) = self.GetScore(DieList)
        if Score:
            return (Score, 1.0, List)
        # Do we have a small straight?
        (Score, List) = self.GetSSScore(DieList)
        if Score:
            if (1 in DieList or 6 in DieList):
                return (40, 0.17, List)
            else:
                return (40, 0.34, List)
        # Do we have a gapped long straight?
        if (1 in DieList and 3 in DieList and 4 in DieList and 5 in DieList):
            return (40, 0.17, (DieList.index(1),DieList.index(3),DieList.index(4),DieList.index(5)))
        if (1 in DieList and 2 in DieList and 4 in DieList and 5 in DieList):
            return (40, 0.17, (DieList.index(1),DieList.index(2),DieList.index(4),DieList.index(5)))
        if (1 in DieList and 2 in DieList and 3 in DieList and 5 in DieList):
            return (40, 0.17, (DieList.index(1),DieList.index(2),DieList.index(3),DieList.index(5)))
        if (2 in DieList and 4 in DieList and 5 in DieList and 6 in DieList):
            return (40, 0.17, (DieList.index(2),DieList.index(4),DieList.index(5),DieList.index(6)))
        if (2 in DieList and 3 in DieList and 5 in DieList and 6 in DieList):
            return (40, 0.17, (DieList.index(2),DieList.index(3),DieList.index(5),DieList.index(6)))
        if (2 in DieList and 3 in DieList and 4 in DieList and 6 in DieList):
            return (40, 0.17, (DieList.index(2),DieList.index(3),DieList.index(4),DieList.index(6)))
        # Odds aren't very good:
        return (40, 0.01, [])

class BlezmonRowFullHouse:
    def __init__(self):
        self.Name = "Full House"
    def GetScore(self, DieList):
        Counts = [0]*7 # zeroth position unused
        for Die in DieList:
            Counts[Die] += 1
        FoundThree = 0
        FoundTwo = 0
        for Count in Counts:
            if Count == 3:
                FoundThree = 1
            elif Count == 2:
                FoundTwo = 1
        if FoundThree and FoundTwo:
            return (25, (0,1,2,3,4))
        return (0, ())
    def GetPlausibleScore(self, DieList):
        Counts = [0]*7 # zeroth position unused
        for Die in DieList:
            Counts[Die] += 1
        CountCounts = [0]*6
        for Count in Counts:
            CountCounts[Count]+=1
        # XXX YY
        if CountCounts[3]==1 and CountCounts[2]==1:
            return (25, 1.0, (0,1,2,3,4))
        # XX YY Z
        if CountCounts[2] == 2:
            KeepIndices = []
            for Index in range(len(DieList)):
                if Counts[DieList[Index]]==2:
                    KeepIndices.append(Index)
            return (25, .17, KeepIndices)
        # XXX YZ
        if CountCounts[3] == 1:
            KeepIndices = []
            for Index in range(len(DieList)):
                if Counts[DieList[Index]]==3:
                    KeepIndices.append(Index)
            return (25, .17, KeepIndices)
        # Odds not good
        return (25, 0.01, [])
        
class BlezmonRowBlezmon:
    def __init__(self):
        self.Name = "Blezmon"
    def GetScore(self, DieList):
        for Die in DieList:
            if Die!=DieList[0]:
                return (0, [])
        return (50, (0,1,2,3,4))
    def GetPlausibleScore(self, DieList):
        Counts = [0]*7 # zeroth position unused
        for Die in DieList:
            Counts[Die] += 1
        # Find the most common number:
        MaxCount = 0
        CommonNumber = None
        for Index in range(len(Counts)):
            if Counts[Index]>=MaxCount:
                MaxCount = Counts[Index]
                CommonNumber = (Index)
        # Find the indices:
        KeepIndices = []
        for Index in range(len(DieList)):
            print "Common number:",CommonNumber
            if DieList[Index]==CommonNumber:
                KeepIndices.append(Index)
        if MaxCount == 5:
            return (50, 1.0, KeepIndices)
        elif MaxCount == 4:
            return (50, 0.17, KeepIndices)
        elif MaxCount == 3:
            return (50, 0.02, KeepIndices)        
        elif MaxCount == 2:
            return (50, 0.0046, KeepIndices)
        else: # re-roll all but max die!
            return (50, 0.00077, KeepIndices)        

class BlezmonRowChance:
    def __init__(self):
        self.Name = "Chance"
    def GetScore(self, DieList):
        Total = 0
        for Die in DieList:
            Total += Die
        return (Total, (0,1,2,3,4))
    def GetPlausibleScore(self, DieList):
        # HACK: We never TRY to roll chance; we use it as a last resort!
        # So, we use odds of .0000001
        KeepIndices = []
        for Index in range(len(DieList)):
            if DieList[Index]>3:
                KeepIndices.append(Index)
        return (1, 0.000000001, KeepIndices)
        
AllBlezmonRows = [BlezmonRowNumber("Ones",1),BlezmonRowNumber("Twos",2),
                  BlezmonRowNumber("Threes",3),BlezmonRowNumber("Fours",4),
                  BlezmonRowNumber("Fives",5),BlezmonRowNumber("Sixes",6),
                  BlezmonRow3Kind(), BlezmonRow4Kind(),
                  BlezmonRowSmallStraight(), BlezmonRowLargeStraight(),
                  BlezmonRowFullHouse(), BlezmonRowBlezmon(), BlezmonRowChance(),
                  ]

for Row in AllBlezmonRows:
    print Row
    print Row.Name

class DieSprite(GenericImageSprite):
    "Roll them bones!"
    RollTimeMax = 50
    def __init__(self, X, Y):
        Image = self.GetImage(6,0)
        GenericImageSprite.__init__(self, Image, X, Y)
        self.rect.left -= self.rect.width / 2
        self.rect.top -= self.rect.height / 2
        self.Digit = 6
        self.KeepFlag = 0
        self.RollingFlag = 0
        self.RollTime = 0
        self.KeepSprite = None
    def UnKeep(self):
        self.KeepFlag = 0
        if self.KeepSprite:
            self.KeepSprite.kill()
        self.ResetImage()
    def ToggleKeep(self):
        if self.KeepFlag:
            self.KeepFlag = 0
            if self.KeepSprite:
                self.KeepSprite.kill()
        else:
            self.KeepFlag = 1
            self.KeepSprite = GenericTextSprite("Hold", self.rect.left, self.rect.bottom + 5)
            BScreen.AddForegroundSprite(self.KeepSprite)
        OldCenter = self.rect.center
        self.image = self.GetImage(self.Digit, self.KeepFlag)
        #self.rect = self.image.get_rect()
        #self.rect.center = OldCenter
    def Roll(self, Ticks):
        self.RollingFlag = 1
        self.KeepFlag = 0
        self.RollTime = 0
        self.Digit = random.randrange(1,7)
    def Update(self, Dummy):
        if not self.RollingFlag:
            return
        self.RollTime += 1
        if self.RollTime >= self.RollTimeMax:
            self.RollingFlag = 0
            self.ResetImage()
            return
        if self.RollTime % 5 == 0:
            self.image = self.GetImage(random.randrange(1,7), 0)
    def ResetImage(self):
        self.image = self.GetImage(self.Digit, self.KeepFlag)
    def GetImage(self, Number, KeepFlag):
        Path = os.path.join(Paths.ImagesMisc, "Blezmon", "%s.%s.png"%(Number, KeepFlag))
        return Resources.GetImage(Path)
        

class BlezmonStates:
    "These are the tick-to-tick states that our screen can be in."
    PlayerRoll = 0 # Time to pick a score row, or pick dice and then roll
    PlayerRolling = 1 # Dice are rolling now.
    ##################
    CPUPicking = 2 # CPU picking dice to keep
    CPURolling = 3 # Dice are rolling now
    CPUPausing = 4 # Pause after CPU fills scorecard row, or starts a turn

class BlezmonScreen(Screen.TendrilsScreen):
    DieX = (240, 310, 380, 450, 520)
    CPUPickTime = 25
    def __init__(self, App, FreePlay):
        global BScreen
        self.FreePlay = FreePlay
        self.PlayerScores = [None]*len(AllBlezmonRows)
        self.OpponentScores = [None]*len(AllBlezmonRows)
        self.IsPlayerTurn = 1
        self.RollNumber = 0
        self.CPUPickRowIndex = 0 # which scorecard row we want
        self.CPUPickIndices = [] # which dice we're keeping
        self.StateTimer = 0        
        self.Score = 0
        BScreen = self
        Screen.TendrilsScreen.__init__(self,App)
        self.SummonSong("blezmon")
        self.DrawBackground()
        self.BuildDice()
        self.StateSprites = []
        
        self.HoverScoreRow = None
        self.HoverScoreSprite = None
        self.EnterState(BlezmonStates.PlayerRoll)
    def EnterState(self, NewState):
        if self.HoverScoreSprite:
            self.HoverScoreSprite.kill()
            self.HoverScoreSprite = None
        self.StateTimer = 0
        self.State = NewState
        for Sprite in self.StateSprites:
            Sprite.kill()
        # Describe the current state:
        if NewState == BlezmonStates.PlayerRoll:
            if self.RollNumber == 0:
                Str = "Your turn.\nRoll the dice!"
            elif (self.RollNumber==1 or self.RollNumber == 2):
                Str = "Your turn.\nClick on dice to keep them, then roll again.\nOr, click a scorecard row to score this hand."
            else:
                Str = "Your turn.\nClick a scorecard row to score this hand."
                for Die in self.DiceSprites.sprites():
                    Die.UnKeep()
        else:
            Str = "Opponent's turn."
        Image = TaggedRenderer.RenderToImage(Str, WordWrapWidth = 358, CenteredFlag = 1)
        Sprite = GenericImageSprite(Image, 221, 50)
        self.AddBackgroundSprite(Sprite)
        self.StateSprites.append(Sprite)
        self.Redraw()
    def BuildDice(self):
        self.DiceSprites = pygame.sprite.Group()
        self.DiceSpriteList = []
        for Index in range(5):
            Sprite = DieSprite(self.DieX[Index], 250)
            self.DiceSprites.add(Sprite)
            self.DiceSpriteList.append(Sprite)
            self.AddForegroundSprite(Sprite)
    def DrawBackground(self):
        "Draw scorecards on the left and on the right."
        Sprite = GenericTextSprite("BLEZMON", 400, 10, Colors.Orange, CenterFlag = 1, FontSize = 32)
        self.AddBackgroundSprite(Sprite)
        # Scorecard headers:
        Sprite = GenericTextSprite("- Your Scorecard -", 100, 10, Colors.Green, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        Sprite = GenericTextSprite("- Opponent -", 700, 10, Colors.Red, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        # Scorecard edges:
        Sprite = LineSprite(200, 0, 200, 600, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(600, 0, 600, 600, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
        # Scorecard rows:
        Y = 100
        self.PlayerScoreX = []
        self.PlayerScoreY = []
        self.OpponentScoreX = []
        self.ClickableScorecardSprites = pygame.sprite.Group()
        for Index in range(len(AllBlezmonRows)):
            Row = AllBlezmonRows[Index]
            Sprite = GenericTextSprite(Row.Name + ":", 10, Y, FontSize = 24)
            self.AddBackgroundSprite(Sprite)
            Sprite.Index = Index
            self.ClickableScorecardSprites.add(Sprite) # Added!
            self.PlayerScoreX.append(Sprite.rect.right + 5)
            self.PlayerScoreY.append(Y)
            Sprite = GenericTextSprite(Row.Name + ":", 620, Y, FontSize = 24)
            self.AddBackgroundSprite(Sprite)
            self.OpponentScoreX.append(Sprite.rect.right + 5)
            Y += 30
            if Index == 5:
                # Par bonus row:
                Sprite = GenericTextSprite("Par bonus:", 10, Y, FontSize = 24)
                self.AddBackgroundSprite(Sprite)
                self.PlayerParBonusSprite = GenericTextSprite("0", Sprite.rect.right + 5, Y, Colors.Blue, FontSize = 24)
                self.AddBackgroundSprite(self.PlayerParBonusSprite)
                ##
                Sprite = GenericTextSprite("Par bonus:", 620, Y, FontSize = 24)
                self.AddBackgroundSprite(Sprite)
                self.OpponentParBonusSprite = GenericTextSprite("0", Sprite.rect.right + 5, Y, Colors.Blue, FontSize = 24)
                self.AddBackgroundSprite(self.OpponentParBonusSprite)
                Y += 30
        # Totals:
        Sprite = LineSprite(0, Y, 200, Y, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
        Sprite = LineSprite(600, Y, 800, Y, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
        Y += 10
        Sprite = GenericTextSprite("Total Score:", 10, Y, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        self.PlayerTotalSprite = GenericTextSprite("0", Sprite.rect.right, Y, FontSize = 24)
        self.AddBackgroundSprite(self.PlayerTotalSprite)
        Sprite = GenericTextSprite("Total Score:", 620, Y, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        self.OpponentTotalSprite = GenericTextSprite("0", Sprite.rect.right, Y, FontSize = 24)
        self.AddBackgroundSprite(self.OpponentTotalSprite)
        # Buttons:
        self.ButtonSprites = pygame.sprite.Group()
        Sprite = FancyAssBoxedSprite("Roll!", 400, 400, HighlightIndex = 0)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        Sprite = FancyAssBoxedSprite("Help", 400, 450, HighlightIndex = 0)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        Sprite = FancyAssBoxedSprite("Give up", 400, 560)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
    def KillHoverSprite(self):
        if self.HoverScoreSprite:
            self.HoverScoreSprite.kill()
            self.HoverScoreSprite = None
    def MakeBlezmonSound(self):
        Resources.PlayStandardSound("RatingAAA.wav")
    def HandleMouseMoved(self,Position,Buttons):
        self.FindMouseOverSprites(Position)
        
    def FindMouseOverSprites(self,Position):
        # When the player mouses over a scorecard-row, show the score
        # they'd get by using their hand to fill that row.
        if self.State != BlezmonStates.PlayerRoll:
            return
        if self.RollNumber == 0:
            return
        OldHoverRow = self.HoverScoreRow
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ClickableScorecardSprites)
        if Sprite==None:
            self.KillHoverSprite()
            return
        if Sprite == OldHoverRow:
            return
        Index = Sprite.Index
        if self.PlayerScores[Index]!=None:
            return
        self.KillHoverSprite() # kill old one
        PotentialScore = AllBlezmonRows[Index].GetScore(self.GetRoll())[0]
        self.HoverScoreSprite = GenericTextSprite("-> %s"%PotentialScore, self.PlayerScoreX[Index], self.PlayerScoreY[Index], Colors.Grey, FontSize = 24)
        self.AddForegroundSprite(self.HoverScoreSprite)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if Key == ord("r"):
            self.ClickRoll()
        elif Key == ord("h"):
            self.ClickHelp()
        else:
            print "--=="*19
            print "Player turn?", self.IsPlayerTurn
            print "Roll number:", self.RollNumber
            print "State:", self.State
            print "State ticks:", self.StateTimer
            
    def RollDice(self):
        self.RollNumber+=1
        if self.IsPlayerTurn:
            self.State = BlezmonStates.PlayerRolling
        else:
            self.State = BlezmonStates.CPURolling
        Resources.PlayStandardSound("Boop2.wav")
        for Die in self.DiceSprites.sprites():
            if not Die.KeepFlag:
                Die.Roll(50)
        self.StateTimer = 0
    def ClickRoll(self):
        # Is it the player's turn?
        if self.IsPlayerTurn and self.State == BlezmonStates.PlayerRoll:
            # And, do they have rolls left?
            if self.RollNumber < 3:
                # Ok, roll!
                self.RollDice()
    def ClickHelp(self):
        Global.App.ShowNewDialog(HelpText)
    def ClickQuit(self):
        Global.App.ShowNewDialog("Really give up?",ButtonGroup.YesNo, Callback = self.ClickQuitReally)
    def ClickQuitReally(self):
        Global.App.PopScreen(self)
    def ClickDie(self, Die):
        # Is it the player's turn?
        if self.IsPlayerTurn and self.State == BlezmonStates.PlayerRoll:
            # And, do they have rolls left?
            if self.RollNumber < 3 and self.RollNumber>0:
                Die.ToggleKeep()
                Resources.PlayStandardSound("Boop3.wav")
    def CPUFillScorecardRow(self):
        Index = self.CPUPickRowIndex
        (Score, Dice) = AllBlezmonRows[Index].GetScore(self.GetRoll())
        if AllBlezmonRows[Index].Name == "Blezmon" and Score:
            self.MakeBlezmonSound()
        print "CPU accepts a score of %s in %s"%(Score, AllBlezmonRows[Index].Name)
        self.OpponentScores[Index] = Score
        Sprite = GenericTextSprite(Score, self.OpponentScoreX[Index], self.PlayerScoreY[Index], Colors.Blue, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        self.UpdateOpponentScore()
        # Is the game over?
        AllDone = 1
        for Entry in self.OpponentScores:
            if Entry==None:
                AllDone = 0
                break
        if AllDone:
            self.FinishGame()
        # And now, next turn:
        self.StartPlayerTurn()
    def FinishGame(self):
        # All scores have been filled.  The game is over!
        self.Redraw()
        PlayerTotal = int(self.PlayerTotalSprite.Text)
        CPUTotal = int(self.OpponentTotalSprite.Text)
        Str = "The final score is %d to %d."%(PlayerTotal, CPUTotal)
        if PlayerTotal > CPUTotal:
            Str += "\n\n<CENTER><CN:BRIGHTGREEN>You have won!</Center></c>"
            if not self.FreePlay:
                Global.MemoryCard.Set("MiniGameBlezmon", 1)
                Global.Party.EventFlags["L8Blezmon"] = 1
                Str += "\n\n(You have unlocked the <CN:ORANGE>Blezmon</C> minigame!)"
        elif PlayerTotal == CPUTotal:
            Str += "\n\n<CENTER><CN:BRIGHTBLUE>It's a tie!</CENTER></C>\nBetter luck next time."
        else:
            Str += "\n\n<CENTER><CN:BRIGHTRED>You have lost!</CENTER></C>\nBetter luck next time."
        if self.FreePlay:
            Global.App.ShowNewDialog(Str, Callback = self.FinishGameFreePlay)
        else:
            Global.App.ShowNewDialog(Str)
            Global.App.PopScreen(self)
    def FinishGameFreePlay(self):
        PlayerTotal = int(self.PlayerTotalSprite.Text)
        OldHighScore = Global.MemoryCard.Get("BlezmonHiscore", 0)
        OldHighScorer = Global.MemoryCard.Get("BlezmonHiscorer", "nobody")
        if PlayerTotal > OldHighScore:
            Str = "A new high score!\n\nEnter your name:"
            Global.App.ShowWordEntryDialog(Str, Callback = self.FreePlayEnterName)
            return
        Str = "You didn't beat the previous high score of <CN:BRIGHTGREEN>%d</C>, held by <CN:BRIGHTBLUE>%s</C>"%(OldHighScore, OldHighScorer)
        Global.App.ShowNewDialog(Str)
        Global.App.PopScreen(self)
    def FreePlayEnterName(self, Name):
        PlayerTotal = int(self.PlayerTotalSprite.Text)
        Global.MemoryCard.Set("BlezmonHiscore", PlayerTotal)
        Global.MemoryCard.Set("BlezmonHiscorer", Name)
        Global.App.PopScreen(self)
    def StartPlayerTurn(self):
        for Die in self.DiceSpriteList:
            Die.UnKeep()        
        self.RollNumber = 0
        self.IsPlayerTurn = 1
        self.EnterState(BlezmonStates.PlayerRoll)

    def ClickScorecardItem(self, Sprite):
        # Is it the player's turn?
        if (not self.IsPlayerTurn) or (self.State != BlezmonStates.PlayerRoll):
            return
        if self.RollNumber == 0:
            return # haven't rolled yet!
        print "Clicked scorecard item!", Sprite
        Index = Sprite.Index
        # Can they still take a score on this item?
        CurrentScore = self.PlayerScores[Index]
        if CurrentScore!=None:
            Resources.PlayStandardSound("Heartbeat.wav")
            return
        # Ok, let's do it!
        Score = AllBlezmonRows[Sprite.Index].GetScore(self.GetRoll())[0]
        if AllBlezmonRows[Sprite.Index].Name == "Blezmon" and Score:
            self.MakeBlezmonSound()
        
        Sprite = GenericTextSprite(Score, self.PlayerScoreX[Index], self.PlayerScoreY[Index], Colors.Blue, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        self.PlayerScores[Index] = Score
        self.UpdatePlayerScore()
        self.StartCPUTurn()
    def StartCPUTurn(self):
        for Die in self.DiceSpriteList:
            Die.UnKeep()        

        # And now, next turn:
        self.RollNumber = 0
        self.IsPlayerTurn = 0
        self.CPUPickIndices = []
        self.CPUPickRowIndex = None
        self.EnterState(BlezmonStates.CPUPicking)
        
    def UpdatePlayerScore(self):
        # Update the sum:
        PlayerTotal = 0
        for Score in self.PlayerScores:
            if Score!=None:
                PlayerTotal += Score
        UpperTotal = 0
        for Score in self.PlayerScores[:6]:
            if Score!=None:
                UpperTotal += Score
        # Par bonus:
        if UpperTotal >= 63:
            self.PlayerParBonusSprite.ReplaceText("35")
            PlayerTotal += 35
        self.PlayerTotalSprite.ReplaceText(PlayerTotal)
    def UpdateOpponentScore(self):
        # Update the sum:
        Total = 0
        for Score in self.OpponentScores:
            if Score!=None:
                Total += Score
        UpperTotal = 0
        for Score in self.OpponentScores[:6]:
            if Score!=None:
                UpperTotal += Score
        # Par bonus:
        if UpperTotal >= 63:
            self.OpponentParBonusSprite.ReplaceText("35")
            Total += 35
        self.OpponentTotalSprite.ReplaceText(Total)
    def GetRoll(self):
        Dice = []
        for Die in self.DiceSpriteList:
            Dice.append(Die.Digit)
        return Dice
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for button clicks:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            if Sprite.Text == "Roll!":
                self.ClickRoll()
            elif Sprite.Text == "Help":
                self.ClickHelp()
            else:
                self.ClickQuit()
            return
        # Now, handle clicked dice:
        Die = pygame.sprite.spritecollideany(Dummy, self.DiceSprites)
        if Die:
            self.ClickDie(Die)
        # Now, handle clicked scorecard-rows:
        Sprite = pygame.sprite.spritecollideany(Dummy, self.ClickableScorecardSprites)
        if Sprite:
            ##print "Clicked scorecard row!", Sprite
            self.ClickScorecardItem(Sprite)
        
    def ChooseCPUMove(self):
        # Look at each unfilled row.  If it's our last roll, rank them by the
        # score we can get right now.  Otherwise, rank by ODDS and then by EXPECTED score.
        List = []
        for RowIndex in range(len(AllBlezmonRows)):
            # Skip filled rows:
            if self.OpponentScores[RowIndex]!=None:
                continue
            if self.RollNumber == 3:
                Tuple = AllBlezmonRows[RowIndex].GetScore(self.GetRoll())
                #print AllBlezmonRows[RowIndex].Name, Tuple
                (Total, KeepDice) = Tuple
                List.append((Total, KeepDice, RowIndex))
            else:
                Tuple = AllBlezmonRows[RowIndex].GetPlausibleScore(self.GetRoll())
                #print AllBlezmonRows[RowIndex].Name, Tuple
                (Total, Odds, KeepDice) = Tuple
                List.append((Odds, Total, KeepDice, RowIndex))
        List.sort()
        
        self.CPUPickRowIndex = List[-1][-1]
        self.CPUPickIndices = List[-1][-2]
        if self.RollNumber == 3:
            # Avoid picking chance, if there's other stuff to pick:
            if len(List)>1 and AllBlezmonRows[self.CPUPickRowIndex].Name == "Chance":
                self.CPUPickRowIndex = List[-2][-1]
                self.CPUPickIndices = List[-2][-2]
            #print "CPU roll:", self.GetRoll()
            #print "CPU choice: %s offers a score of %s"%(AllBlezmonRows[self.CPUPickRowIndex].Name, List[-1][0])
        else:
            #print "CPU roll:", self.GetRoll()
            #print "CPU choice: %s offers odds %s with plausible score of %s"%(AllBlezmonRows[self.CPUPickRowIndex].Name, List[-1][0], List[-1][1])
            #print "CPU will keep these dice:", self.CPUPickIndices
            pass
        
    def Update(self):
        self.StateTimer += 1
        # Finish die rolls:
        if self.State == BlezmonStates.PlayerRolling:
            if self.StateTimer > DieSprite.RollTimeMax+1:
                if self.IsPlayerTurn:
                    self.EnterState(BlezmonStates.PlayerRoll)
                else:
                    self.EnterState(BlezmonStates.CPUPicking)
        if self.State == BlezmonStates.CPURolling:
            if self.StateTimer > DieSprite.RollTimeMax+1:
                self.CPUPickNumber = 0
                self.ChooseCPUMove()
                self.EnterState(BlezmonStates.CPUPicking)
        if self.State == BlezmonStates.CPUPicking:
            if self.StateTimer > self.CPUPickTime:
                # It's time for the computer to *do* something.
                # Move FORWARD over the list of dice to hold:
                if self.RollNumber in (1,2) and len(self.CPUPickIndices)<5:
                    for Index in range(5):
                        Sprite = self.DiceSpriteList[Index]
                        if (Index in self.CPUPickIndices) and (not Sprite.KeepFlag):
                            Sprite.ToggleKeep()
                            Resources.PlayStandardSound("Boop3.wav")
                            print "CPU TOGGLED this one ON #%d = %d"%(Index, Sprite.Digit)
                            self.StateTimer = 0
                            return
                        if (Index not in self.CPUPickIndices) and (Sprite.KeepFlag):
                            Sprite.ToggleKeep()
                            Resources.PlayStandardSound("Boop3.wav")
                            print "CPU TOGGLED this one OFF #%d = %d"%(Index, Sprite.Digit)
                            self.StateTimer = 0
                            return
                self.EnterState(BlezmonStates.CPUPausing)
        if self.State == BlezmonStates.CPUPausing:
            # Ok, no more picking to do.  Time to ROLL or PICK A SCORECARD.
            # Choose a scorecard row if we're out of rerolls, or if we're keeping everything.
            if (self.RollNumber==3) or len(self.CPUPickIndices)==5:
                self.CPUFillScorecardRow()
                return
            self.RollDice()
    
