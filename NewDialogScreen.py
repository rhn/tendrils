"""
New-and-improved DIALOG screen.  Displays tagged text, using scroll buttons if necessary.  Also dispalys
either an "OK" button, or "YES" and "NO" buttons.  
"""

from Utils import *
from Constants import *
import Screen
import MessagePanel
import Global
import string

class DialogScreen(Screen.TendrilsScreen):
    ButtonHeight = 45
    ButtonPadding = 18
    ButtonRowPadding = 60
    TextLeftPad = 5
    TextRowHeight = 17
    UpperPadding = 10
    def __init__(self, App, Text, Buttons = ButtonGroup.Ok, CustomButtons = None, Callback = None, CallbackNo = None, Width = 500, DialogY = None):
        Screen.TendrilsScreen.__init__(self,App)
        self.Width = Width
        self.TextWidth = self.Width - 29
        self.Text = Text
        self.Buttons = Buttons
        self.CustomButtons = CustomButtons
        if self.CustomButtons:
            self.Buttons = None # Not a standard group!
        self.ScrollRow = 0
        self.TextSprites = []
        self.ButtonSprites = [] # OK, or YES and NO
        self.Callback = Callback
        self.CallbackNo = CallbackNo
        self.DialogY = DialogY
        self.CustomButtonDict = {} # Map: letter-ord to button-string
        #################################
        # MINOR MAGIC to make the underlying stuff show:
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.BackgroundSurface.blit(self.App.BackgroundSurface,(0,0))
        self.BackgroundSurface.blit(self.App.Surface,(0,0))
        #################################
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))                        
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        
        # Now draw, pardner:
        self.RenderInitialScreen()
    def RedrawBackground(self):
        self.BackgroundSprites.draw(self.BackgroundSurface)
    def CountButtonRows(self):
        RowCount = 1
        X = 0
        for Button in self.ButtonSprites:
            if X:
                X += self.ButtonPadding
            X += Button.rect.width
            if X >= self.Width - self.ButtonRowPadding:
                X = Button.rect.width
                RowCount += 1
        self.ButtonRows = RowCount
        self.RowsAtOnce = (self.Height - (self.ButtonHeight * self.ButtonRows) - 100) / self.TextRowHeight
        return self.ButtonRows
        #return RowCount
    def SetButtonPositions(self, ButtonRows):
        X = 0
        Y = self.MasterSprite.rect.bottom - self.ButtonHeight*ButtonRows - 10
        RowButtons = []
        for Button in self.ButtonSprites:
            if X:
                X += self.ButtonPadding
            #X += Button.rect.width
            if X + Button.rect.width >= self.Width - self.ButtonRowPadding:
                CenteringX = (self.Width - X)/2
                for RowButton in RowButtons:
                    RowButton.rect.left += CenteringX
                RowButtons = []
                X = 0
                Y += self.ButtonHeight
            # Finish the row:
            RowButtons.append(Button)
            Button.rect.top = Y
            Button.rect.left = X + (400 - self.Width / 2)
            X += Button.rect.width
        CenteringX = (self.Width - X)/2
        for RowButton in RowButtons:
            RowButton.rect.left += CenteringX
    def GetTextHeight(self):
        Height = 0
        for Image in self.TextImages:
            Height += Image.get_rect().height + 1        
        self.TextHeight = max(min(Height, 520), 30)
    def RenderInitialScreen(self):
        self.ScrollArrowX = 400 + (self.Width / 2) - 30        
        # Render text to a list of images by row:
        self.TextImages = TaggedRenderer.RenderToRows(self.Text, WordWrapWidth = self.TextWidth)
        self.GetTextHeight()
        # Build sprites for all our buttons now:
        self.DrawButtons()
        ButtonRows = self.CountButtonRows()
        self.Height = self.TextHeight + 40 + self.ButtonHeight*ButtonRows # Padding for the buttons, and for the border:
        # Build *ONE* big ol' sprite for the background:
        Image = pygame.Surface((self.Width, self.Height))
        if self.DialogY:
            DialogY = self.DialogY
        else:
            DialogY = 300 - (self.Height / 2)
        self.UpArrowY = DialogY + 10
        self.DownArrowY = DialogY + self.Height - 30
        self.MasterSprite = GenericImageSprite(Image, 400 - (self.Width / 2), DialogY, 0)
        self.SetButtonPositions(ButtonRows)
        self.BackgroundSprites.add(self.MasterSprite)
        # Draw the colorful boxy thingy:
        self.MasterSprite.image.fill(Colors.Green)
        pygame.draw.rect(self.MasterSprite.image, Colors.White, (4, 4, self.Width - 8, self.Height - 8), 1)
        pygame.draw.rect(self.MasterSprite.image, Colors.Black, (10, 10, self.Width - 20, self.Height - 20), 0)
        # And draw the text:
        self.RenderText()
        # Now draw the buttons:
        ###self.DrawButtons()
        self.Redraw()
    def AddButton(self, Text, HighlightIndex = None):
        Image = FancyAssBoxedText(Text, Spacing = 3, HighlightIndex = HighlightIndex)
        Button = GenericImageSprite(Image, 0, 0)
        Button.Command = Text
        self.ButtonSprites.append(Button)
        self.AddForegroundSprite(Button)
        return Button
    def DrawButtons(self):
        if self.CustomButtons:
            Width = 0
            self.CustomButtonDict = {} # Map: letter-ord to button-string
            for ButtonStr in self.CustomButtons:
                HighlightIndex = None
                for Index in range(len(ButtonStr)):
                    Ord = ord(ButtonStr[Index].lower())
                    if not self.CustomButtonDict.has_key(Ord):
                        self.CustomButtonDict[Ord] = ButtonStr
                        HighlightIndex = Index
                        break
                self.AddButton(ButtonStr)
            return
        if self.Buttons == ButtonGroup.Ok:
            self.AddButton("Ok", 0)
        elif self.Buttons == ButtonGroup.YesNo:
            self.AddButton("No", 0)
            self.AddButton("Yes", 0)
        elif self.Buttons == ButtonGroup.PickPlayer:
            X = 200
            for Label in range(1,5):
                Index = PlayerLabelToPlayerIndex[Label]
                Player = Global.Party.Players[Index]
                if Player.IsDead():
                    continue # Dead people can't do stuff.
                Button = self.AddButton(Player.Name)
##                OldX = X
##                X += (Button.rect.width + 7)
                Button.Command = "Player"
                Button.Index = Index
            self.AddButton("Cancel")
        else:
            self.AddButton("Ok", 400) # default behavior!
    def RenderText(self):
        Y = self.UpperPadding
        pygame.draw.rect(self.MasterSprite.image, Colors.Black, (10, 10, self.Width - 30, self.Height - 20), 0)
        MaxY = self.GetMaxTextHeight()
        for TextImage in self.TextImages[self.ScrollRow:]:
            NewY = Y + (TextImage.get_rect().height + 1)
            if NewY > MaxY:
                break
            self.MasterSprite.image.blit(TextImage, (15, Y))
            Y = NewY
        self.RenderScrollButtons()
        self.Redraw()
    def GetMaxTextHeight(self):
        return self.Height - (self.ButtonHeight*self.ButtonRows) - 20 - self.UpperPadding
    def RenderScrollButtons(self):
        TotalRows = len(self.TextImages)
        #self.ScrollRow = max(0, min(self.ScrollRow, TotalRows - self.RowsAtOnce))
        if self.ScrollRow > 0:
            if not self.UpArrowSprite:
                self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.UpArrowY)
                self.AddForegroundSprite(self.UpArrowSprite)
                self.UpArrowSprite.Command = "Up"
                self.ButtonSprites.append(self.UpArrowSprite)
        else:
            if self.UpArrowSprite:
                self.UpArrowSprite.kill()
                self.ButtonSprites.remove(self.UpArrowSprite)
                self.UpArrowSprite = None
        MaxScrollRow = self.GetMaxScrollRow()
        if self.ScrollRow < MaxScrollRow: #(TotalRows - self.RowsAtOnce):
            if not self.DownArrowSprite:
                self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DownArrowY)
                self.AddForegroundSprite(self.DownArrowSprite)
                self.DownArrowSprite.Command = "Down"
                self.ButtonSprites.append(self.DownArrowSprite)
        else:
            if self.DownArrowSprite:
                self.DownArrowSprite.kill()
                self.ButtonSprites.remove(self.DownArrowSprite)
                self.DownArrowSprite = None
    def ClickUpArrow(self):
        self.ScrollRow = max(0, self.ScrollRow - 5) #(self.RowsAtOnce - 1))
        self.RenderText()
    def GetMaxScrollRow(self):
        Height = self.UpperPadding
        MaxHeight = self.GetMaxTextHeight()
        MaxScrollRow = 0
        for Index in range(len(self.TextImages)-1, -1, -1):
            if Height + self.TextImages[Index].get_rect().height + 1 <= MaxHeight:
                MaxScrollRow = Index
            else:
                break
            Height += self.TextImages[Index].get_rect().height + 1
        return MaxScrollRow
    def ClickDownArrow(self):
        # Our maximum scroll-row is the smallest index for which we can display all the following text rows.
        MaxScrollRow = self.GetMaxScrollRow()
        OldScrollRow = self.ScrollRow
        self.ScrollRow = min(MaxScrollRow, self.ScrollRow + 5)
        self.RenderText()
    def ButtonClicked(self, Command, Button = None):
        if Button and Button == self.UpArrowSprite:
            self.ClickUpArrow()
            return
        if Button and Button == self.DownArrowSprite:
            self.ClickDownArrow()
            return
        if self.CustomButtons:
            if self.Callback:
                self.App.DismissDialogBox(self, lambda S = Command: apply(self.Callback, (S,)))
            else:
                self.App.DismissDialogBox(self, None)
            return
        if Command == "Player":
            self.App.DismissDialogBox(self, lambda P=Global.Party.Players[Button.Index]: apply(self.Callback, (P,)))
            return
        if Command in ["No", "Cancel"]:
            self.App.DismissDialogBox(self, self.CallbackNo)
            return
        self.App.DismissDialogBox(self, self.Callback)
    def HandleMouseClickedHere(self,Position,Button):
        for ButtonSprite in self.ButtonSprites:
            if ButtonSprite.rect.collidepoint(Position):
                self.ButtonClicked(ButtonSprite.Command, ButtonSprite)
    def HandleKeyPressed(self,Key):
        if Key in (280, 265): # pgUp
            self.ClickUpArrow()
            return
        if Key in (281, 259): # pgDown
            self.ClickDownArrow()
            return
        
        # Respond to Escape or Enter (but not Space, since that's a door-opener and people might
        # be tapping away at it already)
        if self.Buttons == ButtonGroup.Ok and (Key is pygame.K_ESCAPE or Key == Keystrokes.Enter or \
                                               Key == 111 or Key == 271): # 271 is the num-pad enter; 111 is letter O
            self.ButtonClicked("Ok")
        if self.Buttons == ButtonGroup.PickPlayer and Key in (pygame.K_ESCAPE,):
            self.ButtonClicked("Cancel")
        if self.Buttons == ButtonGroup.YesNo and Key == 121: #y
            self.ButtonClicked("Yes")
        if self.Buttons == ButtonGroup.YesNo and Key == 110: #n
            self.ButtonClicked("No")
        if self.Buttons == ButtonGroup.PickPlayer:
            PlayerIndex = None
            if Key == ord("1"):
                PlayerIndex = 2
            elif Key == ord("2"):
                PlayerIndex = 0
            elif Key == ord("3"):
                PlayerIndex = 1
            elif Key == ord("4"):
                PlayerIndex = 3
            if PlayerIndex != None:
                self.App.DismissDialogBox(self, lambda P=Global.Party.Players[PlayerIndex]: apply(self.Callback, (P,)))
                return 

        if self.CustomButtonDict.has_key(Key):
            self.ButtonClicked(self.CustomButtonDict[Key])
            
class ImageDialogScreen(DialogScreen):
    def __init__(self, Image):
        self.Image = Image
        DialogScreen.__init__(self, Global.App, "")
    def RenderText(self):
        Sprite = GenericImageSprite(self.Image, 400, self.MasterSprite.rect.top + 11)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.Redraw()
    def GetTextHeight(self):
        self.TextHeight = self.Image.get_rect().height
    
class MultiButtonDialogScreen(DialogScreen):
    "A dialog where you click MULTIPLE buttons."
    def __init__(self, Text, Items, Count, Callback):
        self.DesiredCount = Count
        DialogScreen.__init__(self, Global.App, Text, CustomButtons = Items, Callback = Callback)
    def AddButton(self, Text):
        Image = TextImage(Text, FontSize = 24)
        Rect = Image.get_rect()
        Button = GenericImageSprite(Image, 0, 0)
        Button.Command = Text
        Button.OnFlag = 0
        self.ButtonSprites.append(Button)
        self.AddForegroundSprite(Button)
        return Button
    def ButtonClicked(self, Command, Button = None):
        if Command == "Cancel":
            Global.App.DismissDialogBox(self, None)
            return
        Center = Button.rect.center
        if Button.OnFlag:
            Button.OnFlag = 0            
            Image = TextImage(Command, FontSize = 24)
            Button.image = Image
            Button.rect = Button.image.get_rect()
            Button.rect.center = Center
        else:
            Button.OnFlag = 1
            Image = FancyAssBoxedText(Command, Spacing = 3)
            Button.image = Image
            Button.rect = Button.image.get_rect()
            Button.rect.center = Center
        StrList = []
        for Button in self.ButtonSprites:
            if Button.Command != "Cancel" and Button.OnFlag:
                StrList.append(Button.Command)
        if len(StrList) >= self.DesiredCount:
            Global.App.DismissDialogBox(self, lambda L=StrList: apply(self.Callback, (L,)))


AllowedChars = "abcdefghijklmnopqrstuvwxyz1234567890 .!"
ShiftTranslate = string.maketrans("abcdefghijklmnopqrstuvwxyz1","ABCDEFGHIJKLMNOPQRSTUVWXYZ!")

class WordEntryScreen(DialogScreen):
    WordColor = Colors.Yellow
    WordSize = 24
    def __init__(self, Text, Callback, MaxLen = None, LegalChars = None):
        DialogScreen.__init__(self, Global.App, Text, ButtonGroup.Ok, Callback = Callback)
        self.Word = ""
        self.HoldingKey = None
        self.MaxWordLen = MaxLen
        if not self.MaxWordLen:
            self.MaxWordLen = 15
        self.LegalChars = LegalChars
        if not self.LegalChars:
            self.LegalChars = AllowedChars
        self.CreateCursor()
    def CreateCursor(self):
        self.WordX = 400 - (self.Width / 2) + 12
        self.WordY = 300 + (self.Height / 2) - (self.ButtonHeight * 2)
        self.WordSprite = GenericTextSprite(self.Word, self.WordX, self.WordY, self.WordColor, self.WordSize)
        self.AddForegroundSprite(self.WordSprite)
        self.CursorSprite = CursorSprite(self, self.WordSprite.rect.right, self.WordY, Colors.White, 20, 25)
        self.AddAnimationSprite(self.CursorSprite)
    def CountButtonRows(self):
        "WordEntry adds a fake button-row to hold the text-entry line."
        self.ButtonRows = 2
        self.RowsAtOnce = (self.Height - (self.ButtonHeight * self.ButtonRows) - 100) / self.TextRowHeight
        return self.ButtonRows
    def UpdateWord(self):
        self.WordSprite.image = TextImage(self.Word, self.WordColor, self.WordSize)
        self.WordSprite.rect = self.WordSprite.image.get_rect()
        self.WordSprite.rect.left = self.WordX
        self.WordSprite.rect.top = self.WordY
        self.CursorSprite.rect.left = self.WordSprite.rect.right
    def Finish(self):
        Global.App.DismissDialogBox(self, lambda W=self.Word:self.Callback(W))
        #apply(self.Callback, (self.Word,))
    def Update(self):
        if self.HoldingKey:
            self.KeyRepeatTime -= 1
            if self.KeyRepeatTime <= 0:
                Pressed = pygame.key.get_pressed()
                if Pressed[self.HoldingKey]:
                    self.HandleKeyPressed(self.HoldingKey)
                    self.KeyRepeatTime = MaxKeyRepeatTime
                else:
                    self.HoldingKey = None
        
    def HandleKeyPressed(self, Key):
        if Key in (303, 304):
            return # shift keys
        if Key in range(256) and chr(Key) in self.LegalChars:
            self.HoldingKey = Key
            self.KeyRepeatTime = KeyRepeatDelay            
            Char = chr(Key)
            KeyMods = pygame.key.get_mods()
            if (KeyMods & pygame.KMOD_LSHIFT) or (KeyMods & pygame.KMOD_RSHIFT):
                Char = string.translate(Char, ShiftTranslate)
            if len(self.Word) >= self.MaxWordLen:
                Resources.PlayStandardSound("Heartbeat.wav")
                return
            self.Word += Char
            self.UpdateWord()
            return
        if Key == 8:
            self.HoldingKey = Key
            self.KeyRepeatTime = KeyRepeatDelay            
            if not len(self.Word):
                Resources.PlayStandardSound("Heartbeat.wav")
                return
            self.Word = self.Word[:-1]
            self.UpdateWord()
            return
        if Key == 13:
            self.Finish()
            return
        if Key is pygame.K_ESCAPE:
            self.Word = ""
            self.Finish()
        # Default: bad key
        Resources.PlayStandardSound("Heartbeat.wav")
    def ButtonClicked(self, Command, Button = None):
        self.Finish() #Only one button!
    def SetButtonPositions(self, ButtonRows):
        X = 400
        Y = self.MasterSprite.rect.bottom - self.ButtonHeight*1 + 8
        self.ButtonSprites[0].rect.center = (X,Y)
