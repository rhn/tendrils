"""
Word Dial chest lock - stop the spinning dials on the correct letters to spell the password.
"""
from Utils import *
from Constants import *
import ChestScreen
import Global

LowerLetters = "abcdefghijklmnopqrstuvwxyz1"
Letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!'

class WordDialTrapPanel(ChestScreen.TrapPanel):
    "Word dials" # docstring is displayed to user on Calfo
    # We sometimes pick a 'nice trap word' because real words look neat.
    NiceTrapWords = ['OPEN', 'SPAM',
                     # Game names:
                     'ZORK', 'KROZ', 'YARS', 'ADND', 'MRDO', 'DROL', 'QBRT', 'HERO',
                     'RTYP', 'GODS', 'HACK', 'DOOM', 'XCOM', 'HOMM', 'SMAC', 'SIMS',
                     'TMNT', 
                     # Characters and critters:
                     'CHUN', 'RIKA', 'BARD', 'LINK', 'KEN!', 'RYU!', 'ZERG',
                     'ELF!', ]
    LetterHeight = 65
    LetterPad = 10
    LetterWidth = 60
    DialsTop = 150
    LeftLetterX = 230
    DialsCenter = DialsTop + LetterHeight + (LetterHeight/ 2) 
    def InitTrap(self):
        pass # Already done in ShowInstructions
    def SetupTrap(self):
        self.Word = random.choice(self.NiceTrapWords)
        TimeLimits = [40, 40, 36, 33, 30, 28,
                      26, 24, 22, 20, 18,
                      16, 14, 12]
        self.TimeLimit = TimeLimits[self.DungeonLevel]
        if self.HasNinja:
            self.TimeLimit *= 2
        MissAllotment = [0, 10, 10, 10, 10, 10,
                         10, 10, 9, 8, 7,
                         6, 5, 4] 
        self.AllowedMisses = MissAllotment[self.DungeonLevel]
        if self.HasNinja:
            self.AllowedMisses += 5
        Speeds = [-4.0, -4.0, -4.5, -5.0, -5.5, -6.0,
                  -6.3, -6.6, -7.0, -7.3, -7.6,
                  -8.0, -8.3, -8.6]
        self.DeltaY = Speeds[self.DungeonLevel]
        self.SlowestSpeed = min(self.DeltaY / 3.0, -3.0)
        self.DeltaDeltaY = .0001 * abs(self.DeltaY)
    def ShowInstructions(self):
        """
        Get a target password, and display that (plus the initial wheels); User presses 
        space to start spinning the wheel.
        """
        self.GetLetterImages()
        self.TryImage = Resources.GetImage(os.path.join(Paths.ImagesMisc, "TrapTry.png"))
        self.SetupTrap()
        #################
        # The target word:
        X = self.LeftLetterX
        for Letter in self.Word:
            Sprite = GenericImageSprite(self.WhiteLetterImageDict[Letter], X, 10)
            X += self.LetterWidth
            self.AddBackgroundSprite(Sprite)        
        #################
        # The container-sprite for the wheels:
        Image = pygame.Surface((self.LetterWidth * 4, self.LetterHeight * 3))
        self.WheelHolder = GenericImageSprite(Image, self.LeftLetterX, self.DialsTop)
        self.AddForegroundSprite(self.WheelHolder)
        #################
        # A line across the wheels:
        Sprite = LineSprite(self.LeftLetterX - 10, self.DialsCenter,
                            self.LeftLetterX + self.LetterWidth*4 + 10,
                            self.DialsCenter, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
        #################
        # Allowable misses:
        Sprite = GenericTextSprite("Tries left:", 600, 100)
        self.AddBackgroundSprite(Sprite)
        Image = pygame.Surface((150, 200))
        self.AllowedMissesSprite = GenericImageSprite(Image, 580, 125)
        self.DrawAllowedMisses()
        self.AddForegroundSprite(self.AllowedMissesSprite)
        #################
        # The wheels:        
        self.WheelSprites = [[], [], [], []]
        self.WheelTopY = [0, 0, 0, 0]
        self.WheelLetters = ["  AB","  AB","  AB","  AB"]
        self.WheelDone = [0, 0, 0, 0]
        #################
        # Flashing arrows:
        self.RenderArrows()
        X = 0
        for WheelIndex in range(4):
            Y = self.LetterPad
            for LetterIndex in [0,1,2]:
                Y += self.LetterHeight
                self.WheelHolder.image.blit(self.LetterImageDict[" AB"[LetterIndex]], (X, Y))
            X += self.LetterWidth
        self.Redraw()
        Global.App.ShowNewDialog("Combination lock - press arrows to stop each wheel on the right letter", Callback = self.Start, DialogY = 150)
    def DrawAllowedMisses(self):
        X = 0
        Y = 0
        #print "Draw %d allowed misses:"%self.AllowedMisses
        self.AllowedMissesSprite.image.fill(Colors.Black)
        for Index in range(self.AllowedMisses):
            X += 30
            self.AllowedMissesSprite.image.blit(self.TryImage, (X, Y))
            if (X>=110):
                X = 0
                Y += 30
        Dirty(self.AllowedMissesSprite.rect)
    def RenderArrows(self):
        FileNames = ["Arrow.Left.png", "Arrow.Down.png", "Arrow.Up.png", "Arrow.Right.png"]
        X = self.LeftLetterX - 8
        for Index in range(4):
            Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, FileNames[Index]))
            ArrowSprite = ChestScreen.FlashingSprite(self.Master, Image, X, self.DialsCenter - (Image.get_rect().height / 2))
            self.AddAnimationSprite(ArrowSprite)
            X += self.LetterWidth
    def Update(self):
        if not hasattr(self, "DeltaY"):
            return # Not ready
        if self.DeltaY < self.SlowestSpeed:
            self.DeltaY += self.DeltaDeltaY
        X = 0
        self.WheelHolder.image.fill(Colors.Black)
        for WheelIndex in range(4):
            if self.WheelDone[WheelIndex]:
                # This wheel is stopped (on the correct letter).  Easy to draw:
                Image = self.WhiteLetterImageDict[self.WheelLetters[WheelIndex][0]]
                self.WheelHolder.image.blit(Image, (X, self.LetterPad))
                Image = self.WhiteLetterImageDict[self.WheelLetters[WheelIndex][1]]
                self.WheelHolder.image.blit(Image, (X, self.LetterPad + self.LetterHeight))
                Image = self.WhiteLetterImageDict[self.WheelLetters[WheelIndex][2]]
                self.WheelHolder.image.blit(Image, (X, self.LetterPad + 2*self.LetterHeight))
            else:
                self.WheelTopY[WheelIndex] += self.DeltaY
                # Wrap:
                if self.WheelTopY[WheelIndex] < -self.LetterHeight:
                    self.WheelTopY[WheelIndex] += self.LetterHeight
                    #self.WheelTopLetter[WheelIndex] = self.GetNextLetter(self.WheelTopLetter[WheelIndex])
                    self.WheelLetters[WheelIndex] = self.WheelLetters[WheelIndex][1:] + self.GetNextLetter(self.WheelLetters[WheelIndex][-1])
                # Render:
                Y = self.WheelTopY[WheelIndex] + self.LetterPad
                for Letter in self.WheelLetters[WheelIndex]:
                    Image = self.LetterImageDict[Letter]
                    self.WheelHolder.image.blit(Image, (X, Y))
                    Y += self.LetterHeight
            X += self.LetterWidth
        for Sprite in self.AnimationSprites.sprites():
            Sprite.Update(self.Master.AnimationCycle)
        Dirty(self.WheelHolder.rect)
    def GetNextLetter(self, Letter):
        try:
            NextIndex = (Letters.index(Letter) + 1) % len(Letters)
            return Letters[NextIndex]
        except:
            return "A"
    def GetPrevLetter(self, Letter):
        try:
            NextIndex = (Letters.index(Letter) - 1)
            if NextIndex<1:
                NextIndex += len(Letters)
            return Letters[NextIndex]
        except:
            return "A"
        
    def GetLetterImages(self):
        self.LetterImages = []
        self.LetterImageDict = {}
        self.WhiteLetterImageDict = {}
        AugLetters = Letters + " "
        FontSize = 48 #36
        for Letter in AugLetters:
            Image = TextImage(Letter, Colors.Red, FontSize = FontSize, FontName = Fonts.PressStart)
            self.LetterImageDict[Letter] = Image
            self.LetterImages.append(Image)
            Image = TextImage(Letter, Colors.White, FontSize = FontSize, FontName = Fonts.PressStart)
            self.WhiteLetterImageDict[Letter] = Image
    def HandleKeyPressed(self, Key):
        "Override this, if the disarm can use keystrokes"
        if Key in Keystrokes.Up:
            self.WheelStop(2)
        elif Key in Keystrokes.Down:
            self.WheelStop(1)
        elif Key in Keystrokes.Left:
            self.WheelStop(0)
        elif Key in Keystrokes.Right:
            self.WheelStop(3)
    def WheelStop(self, Index):
        if self.WheelDone[Index]:
            Resources.PlayStandardSound("Heartbeat.wav")
            return
        # Are we stopping at the correct letter?
        Y = self.WheelTopY[Index]
        ClosestLetter = None
        ClosestDist = None
        CenterY = self.LetterHeight + self.LetterHeight / 2
        for LetterIndex in range(len(self.WheelLetters[Index])):
            Distance = abs(CenterY - (Y + self.LetterHeight / 2))
            if (ClosestDist==None or Distance<ClosestDist):
                ClosestLetter = self.WheelLetters[Index][LetterIndex]
                ClosestDist = Distance
            Y += self.LetterHeight
        DesiredLetter = self.Word[Index]
        if DesiredLetter != ClosestLetter:
            #print "WRONG LETTER: %s instead of %s"%(ClosestLetter, DesiredLetter)
            Resources.PlayStandardSound("Error.wav")
            self.MissLetter()
            return
        # They hit it!  Good jorb, hamstray!
        Resources.PlayStandardSound("Bleep1.wav")
        self.WheelDone[Index] = 1
        self.WheelTopY[Index] = 0
        # Dumb special case:
        if self.WheelLetters[Index][0]==" ":
            self.WheelLetters[Index] = " " + DesiredLetter + self.GetNextLetter(DesiredLetter)
        else:
            self.WheelLetters[Index] = self.GetPrevLetter(DesiredLetter) + DesiredLetter + self.GetNextLetter(DesiredLetter)
        
    def MissLetter(self):
        "Subtract 1 from our available misses"
        self.AllowedMisses -= 1
        self.DrawAllowedMisses()
        #self.Redraw()
    def IsFailed(self):
        if self.AllowedMisses <= 0:
            return 1
    def IsDisarmed(self):
        for Index in range(4):
            if not self.WheelDone[Index]:
                return 0
        return 1

##Eeeeevil = []
##for Word in Words:
##    Eeeeevil.append(Rot13(Word))
##print Eeeeevil

