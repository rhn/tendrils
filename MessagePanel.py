from Utils import *
import Resources
import Screen

class MessagePanel(Screen.TendrilsPane):
    def __init__(self,Master,BlitX,BlitY,Width,Height,LineLimit=100):
        Screen.TendrilsPane.__init__(self,Master,BlitX,BlitY,Width,Height,Name="Messages")
        self.TextWidth = self.Width-30
        self.ScrollY = 0
        self.TotalTextHeight = 0
        self.LineLimit=LineLimit
        self.Lines = []
        self.LineSprites = []
        ##self.BottomLineShown=0
        self.Font = GetFont(None,20)
        self.LineHeight = self.Font.get_linesize()
        self.LinesShownAtOnce = self.Height / self.LineHeight
        self.TextSprites = pygame.sprite.Group()
        self.UpButton = None
        self.DownButton = None
        self.CreateButtons()
    def SetScrollY(self,ScrollY):
        Old = self.ScrollY
        self.ScrollY = ScrollY
        self.ScrollY = max(self.ScrollY,0)
        self.ScrollY = min(self.ScrollY,max(0,self.TotalTextHeight - self.Height))
        if self.ScrollY != Old:
            self.UpdateLineHeights()
            self.Redraw()
            self.CreateButtons()
    def Clear(self):
        for Sprite in self.AllSprites.sprites():
            Sprite.kill()
        self.TotalTextHeight = 0
        self.Lines=[]
        self.LineSprites = []
        self.SetScrollY(0)
        self.CreateButtons()
        self.Redraw()
    def CreateButtons(self):
        if self.UpButton:
            self.UpButton.kill()
            self.UpButton = None
        if self.DownButton:
            self.DownButton.kill()
            self.DownButton = None
        if self.ScrollY: ##self.BottomLineShown - self.LinesShownAtOnce > -1:            
            UpImage = Resources.GetImage(os.path.join("images","MessagePanelUp.png"))
            self.UpButton = GenericImageSprite(UpImage,self.TextWidth,0)
            self.AllSprites.add(self.UpButton)
            self.ForegroundSprites.add(self.UpButton)
        if self.ScrollY + self.Height < self.TotalTextHeight: ##self.BottomLineShown < len(self.Lines) - 1:
            DownImage = Resources.GetImage(os.path.join("images","MessagePanelDown.png"))
            self.DownButton = GenericImageSprite(DownImage,self.TextWidth,self.Height-30)
            self.AllSprites.add(self.DownButton)
            self.ForegroundSprites.add(self.DownButton)
    def HandleMouseClickedHere(self,Position,Button):
        if self.UpButton and self.UpButton.rect.collidepoint(Position):
            self.SetScrollY(self.ScrollY - 100)
        elif self.DownButton and self.DownButton.rect.collidepoint(Position):
            self.SetScrollY(self.ScrollY + 100)
    def ScrollToTop(self):
        self.SetScrollY(0)
    def UpdateLineHeights(self):
        Y = 0
        self.TotalTextHeight = 0
        for Sprite in self.LineSprites:
            Sprite.rect.top = Y - self.ScrollY
            Y += Sprite.rect.height
            self.TotalTextHeight += Sprite.rect.height
    def AddItem(self,Text,Prefix="* "):
        """Adds a text item to our scrolly window, using word wrapping.  Later,
        want to include color tags in text..."""
        Text = Prefix+Text
        self.Lines.append(Text)
        Sprite = TaggedRenderer.RenderToSprite(Text,WordWrapWidth = self.TextWidth)
        Sprite.rect.left=0
        self.LineSprites.append(Sprite)
        self.AddForegroundSprite(Sprite)
        if len(self.Lines) > self.LineLimit:
            del self.Lines[0]
            self.LineSprites[0].kill()
            del self.LineSprites[0]
        self.UpdateLineHeights()
        self.SetScrollY(self.TotalTextHeight)
        self.CreateButtons()
