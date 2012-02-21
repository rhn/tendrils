"""
On the NPC screen, you talk with townspeople.  (Tendrils isn't intended to be really
plot-heavy, but it's still nice to have a little conversation power).  See NPC.py
for the dialog support classes.
"""

from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import Critter

RecruitCost = 200

def GetBackgroundArt():
    Image = pygame.Surface((800,600))
    TriUp = Resources.GetImage(os.path.join(Paths.ImagesMisc, "ChaseTriUp.png"))
    TriUp.set_colorkey(Colors.Black)
    TriDown = Resources.GetImage(os.path.join(Paths.ImagesMisc, "ChaseTriDown.png"))
    TriDown.set_colorkey(Colors.Black)
    for Y in range(10):
        for X in range(-2, 20):
            TriImage = (TriUp, TriDown)[(X+Y)%2]
            Image.blit(TriImage, (X*50, Y*100 - 50))
    return Image


class NPCScreen(Screen.TendrilsScreen):
    NPCImageX = 400
    NPCImageY = 10
    DialogY = 200
    ResponseY = 400
    ScrollArrowX = 720
    UpArrowY = 221
    DownArrowY = 350    
    def __init__(self, App, ImageName, DialogTree):
        Screen.TendrilsScreen.__init__(self,App)
        self.ImageName = ImageName
        self.DialogTree = DialogTree
        self.EnterDialogTree()
        self.DialogSprites = pygame.sprite.Group()
        self.ButtonSprites = pygame.sprite.Group()
        self.TalkImageSprites = []
        self.ScrollRow = 0
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))                        
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        self.HiliteSprite = None
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.RenderInitialScreen()
        self.StartMusic()
    def StartMusic(self):
        NPCToSong = {"sinistar":"metalgear",
                     "pastry chef":"options", #wacky!
                     "l1adviceguy":"gato", 
                     "kittygirl":"dragonwarrior",
                     "rabbita":"startout",
                     "rabbitb":"commando",
                     "aaa":"town2",
                     "bard":"options",
                     "queenofhearts":"town2",
                     "jackofspades":"gato",
                     "kingofclubs":"commando",
                     "queenofdiamonds":"dragonwarrior",
                     "joker":"options",
                     "author":"90",
                     }
        SongName = NPCToSong.get(self.ImageName.lower(), "house")
        self.SummonSong(SongName)
    def EnterDialogTree(self):
        self.Node = self.DialogTree.GetFirstNode()
    def RenderInitialScreen(self):
        self.DrawBackground()
        self.DrawDialogNode()
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        for Z in range(0,10):
            for Sprite in self.DeepSprites.sprites():
                if Sprite.Z == Z:
                    #self.DeepSprites.draw(self.BackgroundSurface)
                    self.BackgroundSurface.blit(Sprite.image, (Sprite.rect.left, Sprite.rect.top))
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
    def DrawBackground(self):
        Image = GetBackgroundArt()
        BigBiff = GenericImageSprite(Image, 0, 0)
        BigBiff.Z = 0
        self.DeepSprites.add(BigBiff)
        Image = Resources.GetImage(os.path.join(Paths.ImagesNPC, self.ImageName))
        Sprite = GenericImageSprite(Image, self.NPCImageX, self.NPCImageY, TransparentBack = 0)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        SurroundSprite = BoxSprite(Sprite.rect.left - 1, Sprite.rect.top - 1,
                                   Sprite.rect.width + 2, Sprite.rect.height + 2)
        SurroundSprite.image.set_colorkey(Colors.Black)
        self.AddBackgroundSprite(SurroundSprite)
        ###
        self.UpperPanelImage = self.GetPanelWrapImage(700, 180, Colors.DarkBlue, "They say:")
        Image = pygame.Surface((self.UpperPanelImage.get_rect().width, self.UpperPanelImage.get_rect().height))
        self.UpperPanelSprite = GenericImageSprite(Image, 50, 200, TransparentBack = 0)
        self.UpperPanelSprite.image.blit(self.UpperPanelImage, (0,0))
        self.UpperPanelSprite.Z = 1
        self.DeepSprites.add(self.UpperPanelSprite)
        #self.AddBackgroundSprite(self.UpperPanelSprite)
        ###
        self.LowerPanelImage = self.GetPanelWrapImage(700, 180, Colors.DarkGreen, "You respond:")
        Image = pygame.Surface((self.UpperPanelImage.get_rect().width, self.UpperPanelImage.get_rect().height))
        self.LowerPanelSprite = GenericImageSprite(Image, 50, 400, TransparentBack = 0)
        self.LowerPanelSprite.image.blit(self.LowerPanelImage, (0,0))
        #self.AddBackgroundSprite(self.LowerPanelSprite)
        self.LowerPanelSprite.Z = 1
        self.DeepSprites.add(self.LowerPanelSprite)
        
    def RenderTalkImages(self):
        for Sprite in self.TalkImageSprites:
            Sprite.kill()
        Y = self.DialogY + 15
        self.RowsAtOnce = 7
        for Image in self.TalkImages[self.ScrollRow:self.ScrollRow + self.RowsAtOnce]:
            Sprite = GenericImageSprite(Image, 60, Y)
            self.TalkImageSprites.append(Sprite)
            self.AddBackgroundSprite(Sprite)
            Y += Sprite.rect.height + 1
        self.RenderScrollButtons()
        self.Redraw()
    def RenderScrollButtons(self):
        TotalRows = len(self.TalkImages)
        self.ScrollRow = max(0, min(self.ScrollRow, TotalRows - self.RowsAtOnce))
        if self.ScrollRow > 0:
            if not self.UpArrowSprite:
                self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.UpArrowY)
                self.AddForegroundSprite(self.UpArrowSprite)
        else:
            if self.UpArrowSprite:
                self.UpArrowSprite.kill()
                self.UpArrowSprite = None
        if self.ScrollRow < (TotalRows - self.RowsAtOnce):
            if not self.DownArrowSprite:
                self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DownArrowY)
                self.AddForegroundSprite(self.DownArrowSprite)
        else:
            if self.DownArrowSprite:
                self.DownArrowSprite.kill()
                self.DownArrowSprite = None
    
    def DrawDialogNode(self):
        if not self.Node.Text:
            # Follow link again!
            for Branch in self.Node.Choices:
                if (not Branch.PreLogic) or (apply(Branch.PreLogic, (Global.Party, Global.Maze))):
                    self.Node = self.DialogTree.GetNextNode(Branch)
                    self.DrawDialogNode()
                    return
        for Sprite in self.DialogSprites.sprites():
            Sprite.kill()
        self.HiliteSprite = None
        self.ScrollRow = 0
        self.TalkImages = TaggedRenderer.RenderToRows(self.Node.Text, 665)
        ##Image = TaggedRenderer.RenderToImage(self.Node.Text, 690)
        self.RenderTalkImages()
        ###
        # Responses:
        Y = self.ResponseY + 25
        for Response in self.Node.GetChoices():
            Sprite = ResponseSprite(self, Response.Text, 70, Y) #GenericTextSprite(Response.Text, 70, Y)
            Sprite.Choice = Response
            self.ButtonSprites.add(Sprite)
            self.DialogSprites.add(Sprite)
            self.AddForegroundSprite(Sprite)
            Y += Sprite.rect.height + 3
        self.Redraw()

    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite and Sprite == self.UpArrowSprite:
            self.ClickUpArrow()
            return
        if Sprite and Sprite == self.DownArrowSprite:
            self.ClickDownArrow()
            return
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        Resources.PlayStandardSound("Bleep7.wav")
        # Now, figure out where to go:
        NextNode = self.DialogTree.GetNextNode(Sprite.Choice)
        if not NextNode:
            self.App.PopScreen(self)
            return
        self.Node = NextNode
        self.DrawDialogNode()
    def ClickUpArrow(self):
        self.ScrollRow = max(self.ScrollRow - 4, 0)
        self.RenderTalkImages()
    def ClickDownArrow(self):
        self.ScrollRow = min(self.ScrollRow + 4, len(self.TalkImages) - self.RowsAtOnce)
        self.ScrollRow = max(self.ScrollRow, 0)
        self.RenderTalkImages()
    def HandleMouseMoved(self,Position,Buttons):
        self.FindMouseOverSprites(Position)
       
    def FindMouseOverSprites(self,Position):
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite!=self.HiliteSprite and self.HiliteSprite:
            self.HiliteSprite.StopStrobe()
            #self.HiliteSprite.set_alpha(255) # Move OFF
        if Sprite != self.HiliteSprite:
            self.HiliteSprite = Sprite
            if self.HiliteSprite:
                self.HiliteSprite.StartStrobe()
        
    def HandleKeyPressed(self, Key):
        if Key in (280, 265): # pgUp
            self.ClickUpArrow()
            return
        if Key in (281, 259): # pgDown
            self.ClickDownArrow()
            return

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
        print "trobe ON!"
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
    