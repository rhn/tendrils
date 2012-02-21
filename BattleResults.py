"""
A fancy dialog box for showing combat results.
"""
from Utils import *
from Constants import *
import Screen
import MessagePanel
import Music
import Global
import string
import NewDialogScreen

RatingNames = ["D", "C", "B", "A", "AA", "AAA"]
RatingSounds = ["RatingD.wav", "RatingC.wav", "RatingB.wav", "RatingA.wav", "RatingAA.wav", "RatingAAA.wav"]
EXPMultipliers = [0.5, 1.0, 1.25, 2.0, 3.0, 5.0]

def GetRating(HitTotals):
    """
    Assigns a player a rating (from 0:D to 5:AAA).
    ...hm, how does DDR do this?  We can't quite use their method,
    because we may have gone through the song exactly once, less than
    once, or multiple times.  Here's our plan:
    - Give at most an A if they didn't hit 20 arrows.  (Don't want people to get big EXP bonus by
    tapping two arrows and then summoning Bahamut)
    - Otherwise, compute a POINT AVERAGE based on hit-quality.  Use that to assign the grade.
    """
    TotalPoints = 0
    TotalArrows = 0
    TotalPoints += 10 * HitTotals[HitQuality.Perfect]
    TotalArrows += HitTotals[HitQuality.Perfect]
    TotalPoints += 3 * HitTotals[HitQuality.Good]
    TotalArrows += HitTotals[HitQuality.Good]
    TotalPoints += 1 * HitTotals[HitQuality.Poor]
    TotalArrows += HitTotals[HitQuality.Poor]
    TotalArrows += HitTotals[HitQuality.Miss]
    if TotalArrows < 20:
        return 3 # No arrows? An A.
    AveragePoint = TotalPoints / float(TotalArrows)
    if AveragePoint < 3.0:
        Score = 0
    elif AveragePoint < 5.0:
        Score = 1
    elif AveragePoint < 7.0:
        Score = 2
    elif AveragePoint < 9.0:
        Score = 3
    elif AveragePoint < 9.5:
        Score = 4
    else:
        Score = 5 # Some damn fine work!
    if TotalArrows < 20:
        Score = min(3, Score)
    return Score
class BattleFeedback(NewDialogScreen.DialogScreen):
    MaxDelay = 10
    def __init__(self, HitTotals, Callback, HeaderText = "", FooterText = ""):
        self.HitTotals = HitTotals
        self.HeaderText = HeaderText
        self.FooterText = FooterText
        self.CurrentDelay = 0
        self.NextTextLine = 0
        self.NextY = 0
        self.TextWidth = 475
        self.ButtonsDrawn = 0
        self.CurrentChannel = None
        self.ProduceTextImages()
        NewDialogScreen.DialogScreen.__init__(self, Global.App, "", Callback = Callback)
        
    def ProduceTextImages(self):
        self.TextImages = []
        self.TextSounds = []
        # Header:
        if self.HeaderText:
            Images = TaggedRenderer.RenderToRows(self.HeaderText, WordWrapWidth = self.TextWidth)
            for Image in Images:
                self.TextImages.append(Image)
                self.TextSounds.append(None)
        # Song performance:
        Image = TaggedRenderer.RenderToImage("<CN:BRIGHTGREEN>Perfect: %d</c>"%self.HitTotals[HitQuality.Perfect])
        self.TextImages.append(Image)
        self.TextSounds.append("Boop3.wav")
        Image = TaggedRenderer.RenderToImage("<CN:GREEN>Good: %d</c>"%self.HitTotals[HitQuality.Good])
        self.TextImages.append(Image)
        self.TextSounds.append("Boop1.wav")
        Image = TaggedRenderer.RenderToImage("<CN:BRIGHTBLUE>Bad: %d</c>"%self.HitTotals[HitQuality.Poor])
        self.TextImages.append(Image)
        self.TextSounds.append("Boop2.wav")
        Image = TaggedRenderer.RenderToImage("<CN:Red>Miss: %d</c>"%self.HitTotals[HitQuality.Miss])
        self.TextImages.append(Image)
        self.TextSounds.append("Boop4.wav")
        Rating = GetRating(self.HitTotals)
        Image = TaggedRenderer.RenderToImage("Rating: %s</c>"%RatingNames[Rating])
        self.TextImages.append(Image)
        self.TextSounds.append(RatingSounds[Rating])
        # Footer:
        if self.FooterText:
            Images = TaggedRenderer.RenderToRows(self.FooterText, WordWrapWidth = self.TextWidth)
            for Image in Images:
                self.TextImages.append(Image)
                self.TextSounds.append(None)
        #print len(self.TextImages)
        #print self.TextSounds
    def RenderInitialScreen(self):
        self.Height = 30 # padding!
        # Add height for text lines:
        for Image in self.TextImages:
            self.Height += Image.get_rect().height
        # ...and height for buttons:
        self.Height += self.ButtonHeight
        # Ok, build the shell:
        Image = pygame.Surface((self.Width, self.Height))
        DialogY = 300 - (self.Height / 2)
        ##self.NextY = DialogY + 20
        self.MasterSprite = GenericImageSprite(Image, 400 - (self.Width / 2), DialogY, 0)
        self.BackgroundSprites.add(self.MasterSprite)
        # Draw the colorful boxy thingy:
        self.MasterSprite.image.fill(Colors.Green)
        pygame.draw.rect(self.MasterSprite.image, Colors.White, (4, 4, self.Width - 8, self.Height - 8), 1)
        pygame.draw.rect(self.MasterSprite.image, Colors.Black, (10, 10, self.Width - 20, self.Height - 20), 0)
        self.CurrentDelay = 1
        self.Redraw()
    def Update(self):
        if self.ButtonsDrawn:
            return
        if (not self.CurrentChannel) or (not self.CurrentChannel.get_busy()):
            self.CurrentChannel = None
            PlayedSound = 0
            #print "UPDATE CONTENTS!"
            while (self.NextTextLine < len(self.TextImages)):
                # Render the next line(s) of text:
                #Sprite = GenericImageSprite(self.TextImages[self.NextTextLine], 0, self.NextY)
                Image = self.TextImages[self.NextTextLine]
                self.MasterSprite.image.blit(Image, (15, 10 + self.NextY))
                self.NextY += Image.get_rect().height
                #self.AddBackgroundSprite(Sprite)
                if self.TextSounds[self.NextTextLine]:
                    self.CurrentChannel = Resources.PlayStandardSound(self.TextSounds[self.NextTextLine])
                    PlayedSound = 1
                self.NextTextLine += 1
                #print "NextTextLine is now:", self.NextTextLine
                if PlayedSound or (self.NextTextLine >= len(self.TextImages)):
                    break
                if self.TextSounds[self.NextTextLine]:
                    if (not self.TextSounds[self.NextTextLine - 1]):
                        self.CurrentDelay = self.MaxDelay / 2
                    break
            # Draw buttons, if we should:
            if self.NextTextLine >= len(self.TextImages):
                self.DrawButtons()
                self.SetButtonPositions(1)
                self.ButtonsDrawn = 1
            self.Redraw()
    def CountButtonRows(self):
        return 1
