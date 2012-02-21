from Utils import *
from Options import *
import Screen
import MessagePanel


BUTTON_OK = "Ok"
BUTTON_YES = "Yes"
BUTTON_NO = "No"


class DialogScreen(Screen.TendrilsScreen):
    CanCancel = 0
    AvailableScreens = {}
    def __init__(self,App, Text, ButtonList=[BUTTON_OK],DefaultButton = None,
                 Callback = None):
        Screen.TendrilsScreen.__init__(self,App)
        self.DialogWidth = 500
        self.Text=Text
        
        #print TextImage, type(TextImage)
        #print dir(TextImage)
        if type(self.Text) == types.StringType:
            TextImage = RenderWrappedText(Text, self.DialogWidth)
            self.DialogHeight = min(TextImage.get_height()+ 30, self.App.GetMainSurface().get_height())
        else:
            self.DialogHeight = int(self.App.GetMainSurface().get_height() * 0.66)
        self.ButtonSprites=pygame.sprite.Group()
        self.ButtonSpriteList=[]
        #self.DialogWidth=Width
        #self.DialogHeight=Height
        
        self.ButtonList = ButtonList
        self.Callback = Callback
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.BackgroundSurface.blit(self.App.BackgroundSurface,(0,0))
        self.BackgroundSurface.blit(self.App.Surface,(0,0))
        self.DialogX = (self.App.GetMainSurface().get_width() /2) - (self.DialogWidth/2)
        self.DialogY = (self.App.GetMainSurface().get_height()/2) - (self.DialogHeight/2)
        self.ButtonRowHeight=30
        self.PanelPadLeft = 5
        self.PanelPadTop = 1
        self.DefaultButton = DefaultButton
        if not self.DefaultButton:
            if ButtonList:
                self.DefaultButton = ButtonList[0]
        ##self.DrawButtons()
        self.Panel = MessagePanel.MessagePanel(self,self.DialogX + self.PanelPadLeft,self.DialogY + self.PanelPadTop,
                                               self.DialogWidth-(self.PanelPadLeft*2),self.DialogHeight-self.ButtonRowHeight-(self.PanelPadTop*2))
        self.SubPanes.append(self.Panel)
        if type(self.Text)==types.StringType:
            self.Panel.AddItem(self.Text,"")
        else:
            for Item in self.Text:
                self.Panel.AddItem(Item)        
    def ButtonClicked(self,Command):
        self.App.DismissDialog(self,Command)
    def Activate(self):
        self.Panel.ScrollToTop()
        self.DrawButtons()
        Screen.TendrilsScreen.Activate(self)
    def DrawButtons(self):
        self.ButtonSpriteList = []
        self.KillSpritesInGroup(self.ButtonSprites)
        # BoxSprite is a white square around the text and buttons
        BigBox = BoxSprite(self.DialogX,self.DialogY,self.DialogWidth,self.DialogHeight)
        self.BackgroundSprites.add(BigBox)
        self.AllSprites.add(BigBox)
        CurrentX=self.DialogX + 20
        ButtonY = self.DialogY + self.DialogHeight - self.ButtonRowHeight
        
        for Index in range(len(self.ButtonList)):
            ButtonCommand = self.ButtonList[Index]
            ButtonSprite = TextButtonSprite(ButtonCommand,CurrentX,ButtonY)
            ButtonSprite.Index = Index
            self.ButtonSprites.add(ButtonSprite)
            self.AddForegroundSprite(ButtonSprite)
            self.ButtonSpriteList.append(ButtonSprite)
            CurrentX += ButtonSprite.rect[0] + 10
            if ButtonCommand == self.DefaultButton:
                self.SetHighlightedSprite(ButtonSprite,self)
        Dirty(self.Surface.get_rect())
    def HandleMouseClickedHere(self,Position,Button):
        for ButtonSprite in self.ButtonSprites.sprites():
            if ButtonSprite.rect.collidepoint(Position):
                self.ButtonClicked(ButtonSprite.Command)        
    def RedrawBackground(self):
        self.BackgroundSprites.draw(self.BackgroundSurface)
        #for Sprite in BackgroundSprites.sprites():
    def HandleKeyPressed(self,Key):
        if Key is pygame.K_ESCAPE or Key == KEY_SPACE or Key == KEY_ENTER:
            self.ButtonClicked(self.DefaultButton)
        if Key == GetKey(KEY_A_BUTTON):
            self.ButtonClicked(self.HighlightedSprite.Text)
        if Key == GetKey(KEY_B_BUTTON):
            self.ButtonClicked(self.DefaultButton)
            
    def HandleArrowKeys(self,KeyList):
        if len(KeyList)<1:
            return
        Index = self.HighlightedSprite.Index
        if KEY_RIGHT in KeyList:
            Index += 1
        elif KEY_LEFT in KeyList:
            Index -= 1
        if Index<0 or Index>=len(self.ButtonSpriteList):
            return
        self.SetHighlightedSprite(self.ButtonSpriteList[Index],self)