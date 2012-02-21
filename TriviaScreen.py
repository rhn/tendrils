"""
The Trivia Quiz screen!
Layout (from top to bottom): Title, party, question, answers.  There are 10 questions;
the players win if they get enough points.
"""
from Utils import *
from Constants import *
import Screen
import Music
import BattleSprites
import ItemPanel
import Global
import Resources
import os
import time
import string
import Party
from BattleSprites import *
class QuestionClass:
    def __init__(self):
        self.Text = ""
        self.Right = ""
        self.Wrong = []

class TriviaScreen(Screen.TendrilsScreen):
    RequiredScore = 750
    ScoreboardY = 50
    QuestionY = 270
    AnswerY = 300
    ScoreFontSize = 32
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        self.Score = 0
        self.QuestionIndex = None
        self.AnimationTime = None
        self.HiliteSprite = None
        self.RenderInitialScreen()
        self.ReadQuestions()
        self.QuestionSprites = pygame.sprite.Group()
        self.StartQuestion()
        self.SummonSong("umgah")
    def ReadQuestions(self):
        self.Questions = [[],[],[]] # easy, medium, hard
        File = open("Trivia.txt","r")
        for FileLine in File.xreadlines():
            try:
                FileLine = FileLine.strip()
                Bits = FileLine.split("\t")
                if len(Bits) < 6:
                    continue
                if not len(Bits[0]) or Bits[0][0] == "#":
                    continue
                NewQuestion = QuestionClass()
                NewQuestion.Text = Bits[1]
                NewQuestion.Right = Bits[2]
                for Bit in Bits[3:]:
                    if len(Bit):
                        NewQuestion.Wrong.append(Bit)
                Difficulty = int(Bits[0])
                self.Questions[Difficulty].append(NewQuestion)
            except:
                print "Error reading a question!!!"
                print "Line: '%s'"%FileLine
                traceback.print_exc()
    def StartQuestion(self):
        self.AnimationTime = None
        if self.QuestionIndex == None:
            self.QuestionIndex = 0
        else:
            self.QuestionIndex += 1
        if self.QuestionIndex >= 10:
            Music.FadeOut()
            if Global.Maze.Level == 10:
                self.RequiredScore = 1000
                PrizeMoney = 100000
            else:
                self.RequiredScore = 750
                PrizeMoney = 2500
            if self.Score >= self.RequiredScore:
                Resources.PlaySound(os.path.join("Sounds", "Sinistar", "Aargh.wav"))
                Str = "<CN:BRIGHTGREEN><CENTER>A WINNER IS YOU!</CENTER></C>\n\nYou have beaten the Trivia Challenge!  You receive <CN:YELLOW>%s</C> zenny, and a copy of the home game."%PrizeMoney
                Global.Party.Gold += PrizeMoney
                Global.App.ShowNewDialog(Str)
            else:
                Resources.PlaySound(os.path.join("Sounds", "Sinistar", "I Hunger.wav"))
                Str = "<CN:BRIGHTRED><CENTER>DEFEAT!</CENTER></C>\n\nYou have failed the Trivia Challenge.  Your lives are forfeit..."
                Global.App.ShowNewDialog(Str, Callback = Global.App.ReturnToTitle)
            Global.App.PopScreen(self)
        if self.QuestionIndex < 5:
            Diff = 0
            self.PointValue = 100
        elif self.QuestionIndex < 8:
            Diff = 1
            self.PointValue = 200
        else:
            Diff = 2
            self.PointValue = 300
        List = self.Questions[Diff]
        self.Question = random.choice(List)
        List.remove(self.Question) # Don't re-use questions!
        self.RenderQuestion()
    def RenderQuestion(self):
        for Sprite in self.QuestionSprites.sprites():
            Sprite.kill()
        self.HiliteSprite = None
        # The question:
        Text = "<CN:BLUE>Question %s (%s points):</C>%s"%(self.QuestionIndex + 1, self.PointValue, self.Question.Text)
        Images = TaggedRenderer.RenderToRows(Text, WordWrapWidth = 700)
        Y = 320
        for Image in Images:
            Sprite = GenericImageSprite(Image, 44, Y)
            self.AddBackgroundSprite(Sprite)
            self.QuestionSprites.add(Sprite)
            Y += 20
        # The answers:
        Choices = [(1, self.Question.Right)]
        Wrongs = self.Question.Wrong[:]
        for Index in range(3):
            Choice = random.choice(Wrongs)
            Choices.append((0, Choice))
            Wrongs.remove(Choice)
        random.shuffle(Choices)
        Y = 470
        for Index in range(4):
            Letter = ["A","B","C","D"][Index]
            Text = "%s) %s"%(Letter, Choices[Index][1])
            ButtonSprite = ResponseSprite(self, Text, 44, Y) #GenericTextSprite(Text, 44, Y)
            ButtonSprite.RightFlag = Choices[Index][0]
            ButtonSprite.Index = Index
            self.AddForegroundSprite(ButtonSprite)
            self.QuestionSprites.add(ButtonSprite)
            self.ButtonSprites.add(ButtonSprite)
            if Choices[Index][0]:
                self.RightAnswerIndex = Index
            Y += 25
        self.Redraw()
    def RenderInitialScreen(self):
        self.DrawTitle()
        self.DrawScoreboard()
        self.DrawPanels()
        self.ButtonSprites = pygame.sprite.Group()
    def DrawTitle(self):
        Sprite = GenericTextSprite("Trivia Challenge", 400, 0, FontSize=32, CenterFlag=1)
        self.AddBackgroundSprite(Sprite)
    def DrawScoreboard(self):
        ScoreImage = pygame.Surface((500, 200))
        # Blit the players:
        X = 50
        FudgeFactors = {"Cleric":10,"Fighter":20,"Ninja":20}
        for Player in Global.Party.Players:
            ImagePath = os.path.join(Paths.ImagesCritter, Player.Species.Name, "Stand.0")
            Image = Resources.GetImage(ImagePath)
            Y = ScoreImage.get_rect().height - Image.get_rect().height - 20
            Y += FudgeFactors.get(Player.Species.Name, 0)
            ScoreImage.blit(Image, (X, Y))
            X += 100
        # Table-thingy:
        pygame.draw.rect(ScoreImage, Colors.LightGrey, (0, 150, 500, 10), 0)
        pygame.draw.rect(ScoreImage, Colors.White, (0, 150, 500, 10), 1)
        pygame.draw.rect(ScoreImage, Colors.LightGrey, (50, 160, 400, 40), 0)
        pygame.draw.rect(ScoreImage, Colors.White, (50, 160, 400, 40), 1)
        pygame.draw.rect(ScoreImage, Colors.Grey, (200, 160, 100, 25), 0)
        ScoreboardSprite = GenericImageSprite(ScoreImage, 400, self.ScoreboardY)
        ScoreboardSprite.rect.left -= ScoreboardSprite.rect.width / 2
        self.AddBackgroundSprite(ScoreboardSprite)
        self.ScoreSprite = GenericTextSprite("0", 400, 208, FontSize = self.ScoreFontSize, CenterFlag = 1)
        self.AddForegroundSprite(self.ScoreSprite)
    def Update(self):
        if self.AnimationTime != None:
            self.AnimationTime -= 1
            if self.AnimationTime <= 0:
                self.StartQuestion()
    def DrawPanels(self):
        PanelImage = self.GetPanelWrapImage(760, 150, Colors.Blue, "Question")
        Sprite = GenericImageSprite(PanelImage, 20, 300)
        self.AddBackgroundSprite(Sprite)
        PanelImage = self.GetPanelWrapImage(760, 150, Colors.Green, "Answer")
        Sprite = GenericImageSprite(PanelImage, 20, 450)
        self.AddBackgroundSprite(Sprite)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if self.AnimationTime != None:
            return
        if Key in (97, 98, 99, 100):
            self.AnswerQuestion(Key - 97)
            return
    def AnswerQuestion(self, Index):
        if Index == self.RightAnswerIndex:
            Resources.PlayStandardSound("Happy.wav")
            Sprite = GlowingTextSprite(self, "Correct!", self.Width / 2, 520)
            self.AddAnimationSprite(Sprite)
            self.Score += self.PointValue
        else:
            Resources.PlayStandardSound("Sad.wav")
            Sprite = GlowingTextSprite(self, "Wrong!", self.Width / 2, 520)
            self.AddAnimationSprite(Sprite)
        if self.HiliteSprite:
            self.HiliteSprite.StopStrobe()
        for Sprite in self.ButtonSprites.sprites():
            if Sprite.Index != Index:
                Sprite.kill()
        self.RedrawPoints()
        self.Redraw()
        self.AnimationTime = 160
    def RedrawPoints(self):
        Center = self.ScoreSprite.rect.center
        self.ScoreSprite.image = TextImage(self.Score, FontSize = self.ScoreFontSize)
        self.ScoreSprite.rect = self.ScoreSprite.image.get_rect()
        self.ScoreSprite.rect.center = Center
    def HandleMouseMoved(self,Position,Buttons):
        self.FindMouseOverSprites(Position)
        
    def HandleMouseClickedHere(self, Position, Button):
        # Called when the player clicks the screen.  Position is a tuple
        # of the form (X, Y).  And Button is the button that was clicked.
        if self.AnimationTime != None:
            return
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # If they clicked on one of the rectangles, reverse its direction:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            self.AnswerQuestion(Sprite.Index)
    def FindMouseOverSprites(self,Position):
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite!=self.HiliteSprite and self.HiliteSprite:
            self.HiliteSprite.StopStrobe()
            #self.HiliteSprite.set_alpha(255) # Move OFF
        if Sprite != self.HiliteSprite:
            self.HiliteSprite = Sprite
            if self.HiliteSprite and not self.AnimationTime:
                self.HiliteSprite.StartStrobe()
class ResponseSprite(TidySprite):
    AlphaSpeed = 10
    def __init__(self, Pane, Text, X, Y):
        Image = TextImage(Text)
        self.image = pygame.Surface((Image.get_rect().width, Image.get_rect().height))
        self.image.set_alpha(255)
        self.image.set_colorkey(Colors.Black)
        self.image.fill(Colors.Black)
        self.image.blit(Image, (0,0))                        
        TidySprite.__init__(self, Pane)
        self.rect = self.image.get_rect()
        self.rect.left = X
        self.rect.top = Y
        self.StrobeOn = 0
        self.Alpha = 255
        self.AlphaDir = -self.AlphaSpeed
    def StartStrobe(self):
        self.StrobeOn = 1
        self.Alpha = 255
        self.AlphaDir = -self.AlphaSpeed
    def StopStrobe(self):
        self.StrobeOn = 0
        self.Alpha = 255
        self.image.set_alpha(self.Alpha)
    def Update(self, Dummy):
        if self.StrobeOn:
            self.Alpha += self.AlphaDir
            if (self.Alpha > 255):
                self.Alpha = 255
                self.AlphaDir = -self.AlphaSpeed
            elif self.Alpha < 80:
                self.Alpha = 80
                self.AlphaDir = self.AlphaSpeed
            self.image.set_alpha(self.Alpha)
