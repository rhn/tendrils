"""
The Wire Lock puzzle looks like this:

o------------------------------------o 
                    |                 
o------------------------------------o
   |                       |
o------------------------------------o
When you start a ball rolling (at the left, on any row), it
cruises across to the right, following any vertical shunt
that it passes.  The object of the puzzle is to hit the
correct target on the far right.  The deeper in the
dungeon you get, the more shunts there are!
"""
from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import string
import sys

class WirePuzzle:
    def __init__(self, RowCount = 5):
        self.RowCount = RowCount
        self.RowShunts = []
        for Index in range(self.RowCount):
            self.RowShunts.append([])
    def GetShunt(self, Row, X):
        for Shunt in self.RowShunts[Row]:
            if Shunt[0]==X:
                return Shunt
        return None
    def HasShunt(self, Row, X):
        if self.GetShunt(Row, X)!=None:
            return 1
    def AddShunt(self):
        # Add shunts to rows 1 and 3:
        ShuntableRows = range(1, self.RowCount, 2)
        while (1):
            X = random.randrange(1, 60) * 10
            Row = random.choice(ShuntableRows) #(1,3))
            Dir = random.choice((-1, 1))
            if (not self.HasShunt(Row, X)) and (not self.HasShunt(Row+Dir, X)):
                break
        self.RowShunts[Row].append((X, Dir))
        self.RowShunts[Row+Dir].append((X, -Dir))
    def GetEndingRow(self, Row):
        X = 0
        InitialRow = Row
        SwapCount = 0
        while (X < 700):
            X += 10
            Shunt = self.GetShunt(Row, X)
            if Shunt!=None:
                Row += Shunt[1]
                SwapCount += 1
        return (Row, SwapCount)
    def ChooseTarget(self):
        HitCount = [0]*self.RowCount
        MinSwaps = [9999]*self.RowCount
        for Row in range(self.RowCount):
            (Target, SwapCount) = self.GetEndingRow(Row)
            HitCount[Target] += 1
            MinSwaps[Target] = min(MinSwaps[Target], SwapCount)
        Best = None
        BestRow = None
        for Row in range(self.RowCount):
            if HitCount[Row] and (Best==None or MinSwaps[Row]>Best):
                BestRow = Row
                Best = MinSwaps[Row] #HitCount[Row]
        if Best<2 or len(self.RowShunts[BestRow])==0:
            return None # This puzzle is too easy!
        return BestRow

class BallSprite(GenericImageSprite):
    MaxPause = 20
    def __init__(self, X, Y):
        self.Images = []
        for Index in range(2):
            Path = os.path.join(Paths.ImagesProjectile, "Bullet.%d.png"%Index)
            self.Images.append(Resources.GetImage(Path))
        GenericImageSprite.__init__(self, self.Images[0], X, Y)
        self.Pause = self.MaxPause
        self.ImageIndex = 0
    def Update(self, Dummy = None):
        self.Pause -= 1
        if self.Pause <= 0:
            self.Pause = self.MaxPause
            self.ImageIndex += 1
            if self.ImageIndex >= len(self.Images):
                self.ImageIndex = 0
            self.image = self.Images[self.ImageIndex]
    
class WirePuzzlePanel(Screen.TendrilsPane):
    "Wire Lock"
    WireStartX = 100
    WireEndX = 700
    WireY = 100
    TimesByLevel = [0, 8, 7, 6, 5, 4,
                    10, 9, 8, 7, 6,
                    16, 15, 14]
    RowCountByLevel = [0,5,5,5,5,5,
                       7,7,7,7,7,
                       9,9,9]
    Instructions = """<CENTER><CN:BRIGHTBLUE>Wire Lock</C></CENTER>\n\nClick on one of the targets on the left to start the ball \
rolling.  The ball rolls to the right, following any shunts it encounters.  Try to hit the \
target on the far right."""
    def __init__(self, Master, BlitX, BlitY, Width, Height, DungeonLevel = 1, HasNinja = 0):
        Screen.TendrilsPane.__init__(self, Master, BlitX, BlitY, Width, Height, "Trap")
        self.DungeonLevel = DungeonLevel
        self.HasNinja = HasNinja
        self.TimeLimit = self.TimesByLevel[DungeonLevel] # in seconds
        print "Limit:", self.TimeLimit
        if HasNinja:
            self.TimeLimit *= 1.5
        self.Animating = 0
        self.Disarmed = 0
        self.Triggered = 0
    def IsFailed(self):
        return self.Triggered
    def GetPuzzle(self):
        RowCount = self.RowCountByLevel[self.DungeonLevel]
        self.RowHeight = (260 / RowCount)
        while (1):
            self.Puzzle = WirePuzzle(RowCount)
            Shunts = 3 + 2*self.DungeonLevel
            for Index in range(Shunts):
                self.Puzzle.AddShunt()
            self.TargetRow = self.Puzzle.ChooseTarget()
            if self.TargetRow!=None:
                break
    def RowY(self, Row):
        return 20 + (Row * self.RowHeight)
    def RenderPuzzle(self):
        self.MasterSurface = pygame.Surface((600, 300))
        self.MasterSurface.fill(Colors.Black)
        Sprite = GenericImageSprite(self.MasterSurface, self.WireStartX, self.WireY)
        self.AddBackgroundSprite(Sprite)
        # Draw the shunts:
        Row = 1
        while Row < self.Puzzle.RowCount:
            Y = self.RowY(Row)
            for Shunt in self.Puzzle.RowShunts[Row]:
                X = Shunt[0] 
                EndY = Y + self.RowHeight * Shunt[1]
                pygame.draw.circle(self.MasterSurface, Colors.DarkBlue, (X, Y), 3, 0)
                pygame.draw.circle(self.MasterSurface, Colors.DarkBlue, (X, EndY), 3, 0)
                pygame.draw.line(self.MasterSurface,  Colors.White, (X, Y), (X,EndY))
            Row += 2
        # Draw the wires:
        for RowIndex in range(self.Puzzle.RowCount):
            Y = self.RowY(RowIndex)
            pygame.draw.line(self.MasterSurface,  Colors.White, (0, Y), (600,Y))
        # Draw the targets:
        for RowIndex in range(self.Puzzle.RowCount):
            if RowIndex == self.TargetRow:                              
                Sprite = GenericTextSprite("Here!", 700, self.WireY + self.RowY(RowIndex))
                Sprite.rect.top -= Sprite.rect.height / 2
                self.AddBackgroundSprite(Sprite)
        # Draw the clickable starters:
        self.StarterSprites = pygame.sprite.Group()
        for RowIndex in range(self.Puzzle.RowCount):
            Sprite = GenericTextSprite("Go->", 100, self.WireY + self.RowY(RowIndex))
            Sprite.Row = RowIndex
            Sprite.rect.right = self.WireStartX
            Sprite.rect.top -= Sprite.rect.height / 2
            self.AddBackgroundSprite(Sprite)
            self.StarterSprites.add(Sprite)
    def IsDisarmed(self):
        return self.Disarmed
    def InitTrap(self):
        self.GetPuzzle()
        self.RenderPuzzle()
        self.Redraw()
    def Update(self):        
        Screen.TendrilsPane.Update(self)
        for Sprite in self.AnimationSprites.sprites():
            Sprite.Update(self.Master.AnimationCycle)
        if self.Animating:
            if self.BallSprite.XDir:
                self.BallSprite.rect.left += self.BallSprite.XDir * 5
                X = self.BallSprite.rect.center[0]
                Shunt = self.Puzzle.GetShunt(self.BallSprite.Row, X - self.WireStartX)
                if Shunt!=None:
                    self.BallSprite.XDir = 0
                    self.BallSprite.YDir = Shunt[1]
                    Y = self.BallSprite.rect.center[1]
                    self.BallSprite.TargetRow = self.BallSprite.Row + Shunt[1]
                    self.BallSprite.TargetY = self.RowY(self.BallSprite.TargetRow) + self.WireY
                if X>=self.WireEndX:
                    self.FinishBallMotion(self.BallSprite.Row)
            else:
                self.BallSprite.rect.top += self.BallSprite.YDir * 5
                Y = self.BallSprite.rect.center[1] 
                if (self.BallSprite.YDir>0 and Y>= self.BallSprite.TargetY) or \
                    (self.BallSprite.YDir<0 and Y<=self.BallSprite.TargetY):
                    self.BallSprite.rect.top = self.BallSprite.TargetY - (self.BallSprite.rect.height / 2)
                    self.BallSprite.Row = self.BallSprite.TargetRow
                    self.BallSprite.YDir = 0
                    self.BallSprite.XDir = 1
    def FinishBallMotion(self, Row):
        if Row == self.TargetRow:
            self.Disarmed = 1
        else:
            self.Triggered = 1
    def ShowInstructions(self):
        Global.App.ShowNewDialog(self.Instructions, Callback = self.Start)
        return
    def Start(self):
        self.InitTrap()
        self.Redraw()
        self.Master.StartTimer()
    def StartBall(self, Row):
        self.Master.DisableTrap()
        for Sprite in self.StarterSprites.sprites():
            Sprite.kill()
        self.Animating = 1
        self.BallSprite = BallSprite(0,0) #GenericTextSprite("XYZ", 0, 0)
        self.BallSprite.rect.center = (self.WireStartX, self.RowY(Row) + self.WireY)
        self.BallSprite.Row = Row
        self.BallSprite.XDir = 1
        self.BallSprite.YDir = 0
        self.AddAnimationSprite(self.BallSprite)
        self.Redraw()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for equipment taking-off:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.StarterSprites)
        if Sprite:
            self.StartBall(Sprite.Row)
    def HandleKeyPressed(self, Key):
        pass