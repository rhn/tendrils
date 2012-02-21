"""
General-purpose and functions for Tendrils. 
"""
import pygame
import os
import sys
import traceback
import random
import types
import time
import Resources
import threading
from Constants import *

# Ugly hack:
# Directions are numbered 1 (up), 2 (down), 3 (left), 4 (right).  The direction is the player's index (in the
#   party array) plus 1.
# Players on screen are labeled 1 (left), 2 (up), 3 (down), 4 (right).
# These lists map between player labels and player indices.
PlayerLabelToPlayerIndex = [0, 2, 0, 1, 3]
PlayerIndexToPlayerLabel = [2,3,1,4]
PlayerLabelNames = ["","Front","Right Flank", "Left Flank", "Rear"]

# Max STR/DEX/CON/INT/WIS/CHA:
MaxStat = 30

HasteFactor = 0.66 # 1/3 less time when hasted


# Screens update their animation-cycle once per call to HandleLoop.
# When animationcycle gets big, it wraps around to zero:
MaxAnimationCycle = 5000


def RollDice(DieCount, Sides):
    "Return a random number by 'rolling' the indicated dice"
    Total = 0
    if not Sides:
        return 0
    for Die in range(DieCount):
        Total += random.randrange(1,Sides+1)
    return Total

def CenterCoord(Long,Short):
    return (Long/2) - (Short/2)

def AssertEqual(X,Y,Epsilon=0):
    if (Epsilon==0 and X!=Y) or (Epsilon>0 and abs(X-Y)>Epsilon):
        print "Assertion error! %s (%s) != %s (%s)"%(X,type(X),Y,type(Y))
        traceback.print_exc()
        raise SystemError

# Pygame events:
EVENT_BUTTON_LEFT_CLICK = 1
EVENT_BUTTON_MIDDLE_CLICK = 2
EVENT_BUTTON_RIGHT_CLICK = 3
EVENT_BUTTON_WHEEL_UP = 4
EVENT_BUTTON_WHEEL_DOWN = 5



# used?
def CycleListMembers(List,Member,Direction):
    Index = List.index(Member)
    Index += Direction
    if (Index>=len(List)):
        Index=0
    if Index<0:
        Index = len(List)-1
    return List[Index]        

DirtyRectangles=[]
def Dirty(Rectangles,BlitX=0,BlitY=0):
    global DirtyRectangles
    if type(Rectangles)!=types.ListType:
        Rectangles = [Rectangles]
    for Entry in Rectangles:
        DirtyRectangles.append((Entry[0]+BlitX,Entry[1]+BlitY,Entry[2],Entry[3]))

def UpdateDirtyRectangles():
    global DirtyRectangles
    pygame.display.update(DirtyRectangles)
    DirtyRectangles = []
    
class GenericImageSprite(pygame.sprite.Sprite):
    """
    Wrapper for the standard Sprite class.
    """
    def __init__(self, Image, X, Y, TransparentBack = 1):
        pygame.sprite.Sprite.__init__(self)
        ##self.Screen = Screen
        self.image = Image
        if TransparentBack:
            self.image.set_colorkey(Colors.Black)
        self.rect = Image.get_rect()
        self.rect.left = X
        self.rect.top = Y
    def SwapImage(self,Image):
        #OldCenter = self.rect.center
        OldX = self.rect.left
        OldY = self.rect.top
        self.image=Image
        self.image.set_colorkey(Colors.Black)
        self.rect = self.image.get_rect()
        #self.rect.center = OldCenter
        self.rect.top = OldY
        self.rect.left = OldX
    def Update(self,AnimationCycle):
        pass



FONT_CACHE = {}
FONT_USE_TIME = {}
MAX_FONT_CACHE_SIZE = 25
def CleanFontCache():
    global FONT_CACHE
    global FONT_USE_TIME
    TimeList = []
    for Item in FONT_USE_TIME.items():
        TimeList.append((Item[1],Item[0]))
    if len(TimeList)<=MAX_FONT_CACHE_SIZE:
        return
    TimeList.sort()
    for Index in range(len(TimeList) - MAX_FONT_CACHE_SIZE):
        Key = TimeList[Index]
        del FONT_CACHE[Key]
        del MAX_FONT_CACHE_SIZE[Key]

def GetFont(Name=None,Size=12):
    global FONT_CACHE
    global FONT_USE_TIME    
    if Name==None:
        Name = "bluebold.ttf"
    Name = os.path.join(Paths.Fonts,Name)
    Key = (Name,Size)
    if FONT_CACHE.has_key(Key):
        FONT_USE_TIME[Key]=time.time()
    else:
        TheFont = pygame.font.Font(Name,Size)        
        FONT_CACHE[Key] = TheFont
        FONT_USE_TIME[Key]=time.time()        
    return FONT_CACHE[Key]


TAG_NAMED_COLORS = {"BRIGHTRED":(255,0,0),"RED":(160,10,10),"BRIGHTGREEN":(0,255,0),
                    "GREEN":(10,160,10),"YELLOW":Colors.Yellow,
                    "BRIGHTBLUE":(0,0,255), "BLUE":(10,10,160),
                    "GREY":(100,100,100),"ORANGE":Colors.Orange, "PURPLE":Colors.Purple,
                    "LIGHTGREY":(200,200,200),
                    }

class TaggedTextRenderer:
    """
    Produces an image with the specified text.  Is able to handle some simple HTML-ish tags.
    Tags:
    <CD:#> color by damage type
    <CN:XXX> color by name
    <CENTER> - center
    </CENTER> - stop centering
    <BIG> </BIG> - size boost
    </C> end special color
    """
    def __init__(self):
        self.UncenterNextRow = 0
    def RenderToRows(self,Text,WordWrapWidth = None,Color = Colors.White,FontName=None,FontSize=20,CenteredFlag=0):
        self.WordWrapWidth=WordWrapWidth
        self.MasterColor=Color
        self.CurrentColor = Color
        self.FontName=FontName
        self.BaseFontSize=FontSize
        self.FontSize=FontSize
        self.CenteredFlag=CenteredFlag
        self.RowImages = []
        self.CurrentColumnImages = []
        self.CurrentRowWidth = 0
        self.MaxRowWidth = 0
        self.MasterFont = GetFont(FontName,FontSize)
        self.CurrentFont = self.MasterFont
        Words = Text.split(" ")
        for Word in Words:
            if len(Word)==0:
                continue            
            StrippedWord = Word.strip()
            # Handle "\nfoo" or "\nfoo\nbar"
            while Word!="" and Word[0]=="\n":
                self.FinishCurrentRow(1)
                Word = Word[1:]
            # Stop after "\n"
            if not StrippedWord:
                continue
            # Handle "foo\nbar" or "\nfoo\nbar\n" or "\nfoo\nbar"
            WordBits = StrippedWord.split("\n")
            if len(WordBits)==1:
                self.RenderWord(StrippedWord)
            else:
                for Index in range(len(WordBits)):
                    WordBit = WordBits[Index]
                    self.RenderWord(WordBit)
                    if Index < len(WordBits)-1:
                        self.FinishCurrentRow(1)
            # Handle trailing newlines:
            while Word!="" and Word[-1]=="\n":
                self.FinishCurrentRow(1)
                Word = Word[:-1]                
        self.FinishCurrentRow()
        return self.RowImages
    def RenderToImage(self,Text,WordWrapWidth = None,Color = Colors.White,FontName=None,FontSize=20,CenteredFlag=0):
        self.RenderToRows(Text,WordWrapWidth,Color,FontName,FontSize,CenteredFlag)
        return self.MergeImages()
    def RenderToSprite(self,Text,WordWrapWidth = None,Color = Colors.White,FontName=None,FontSize=20,CenteredFlag=0):
        Sprite = pygame.sprite.Sprite()
        Sprite.image = self.RenderToImage(Text,WordWrapWidth,Color,FontName,FontSize,CenteredFlag)
        Sprite.rect = Sprite.image.get_rect()
        return Sprite
    def MergeImages(self):
        Height = 0
        for Image in self.RowImages:
            Height += Image.get_height()
        MasterImage = pygame.Surface((self.MaxRowWidth,Height))
        Y = 0
        X = 0
        for Image in self.RowImages:
            MasterImage.blit(Image,(X,Y))
            Y += Image.get_height()
        return MasterImage
    def RenderTag(self,Tag):
        TagGuts = Tag[1:-1].upper()
        if TagGuts[:4] == "IMG:":
            ImageName = TagGuts[4:].lower()
            Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, ImageName))
            if not Image:
                return
            if (self.WordWrapWidth) and (Image.get_width() + self.CurrentRowWidth > self.WordWrapWidth):
                self.FinishCurrentRow()
            self.CurrentColumnImages.append(Image)
            self.CurrentRowWidth += Image.get_width()            
            return
        Pieces = TagGuts.split(":")
        if TagGuts == "/BIG":
            self.FontSize = self.BaseFontSize
            self.CurrentFont = self.MasterFont
        if TagGuts == "BIG":
            self.FontSize = int(self.BaseFontSize*2.5)
            self.CurrentFont = GetFont(self.FontName, self.FontSize)
        if TagGuts=="/C":
            self.CurrentColor = self.MasterColor
            return
        if TagGuts == "CENTER":
            self.CenteredFlag = 1 # this line of code is very egoistic.  Ayn Rand approves!
        if TagGuts == "/CENTER":
            self.UncenterNextRow = 1
        if Pieces[0]=="CD":
            self.CurrentColor = DAMAGE_TYPE_COLORS[int(Pieces[1])]
            return
        if Pieces[0]=="CN":
            self.CurrentColor = TAG_NAMED_COLORS.get(Pieces[1],Colors.White)
            return
    def FinishCurrentRow(self, Force = 1):
        if len(self.CurrentColumnImages):
            RowImage = ConcatenateSurfaces(self.CurrentColumnImages)
            if self.CenteredFlag:
                Rect = RowImage.get_rect()
                RealRowImage = pygame.Surface((self.WordWrapWidth, RowImage.get_rect().height))
                X = (self.WordWrapWidth - RowImage.get_rect().width) / 2
                RealRowImage.blit(RowImage, (X, 0))
                RowImage = RealRowImage
            self.RowImages.append(RowImage)
            self.MaxRowWidth = max(self.MaxRowWidth,RowImage.get_width())
        elif Force:
            RowImage = pygame.Surface((10, 20))
            self.RowImages.append(RowImage)
        if self.UncenterNextRow:
            self.CenteredFlag = 0
            self.UncenterNextRow = 0
        self.CurrentColumnImages=[]
        self.CurrentRowWidth=0
    def RenderWord(self, Word, AddToRow = 1):
        if len(Word)<1:
            return pygame.Surface((0,0))
        if AddToRow:
            Word += " "
        # Split off tags from the word proper:
        TagStart = Word.find("<")
        if TagStart!=-1:
            TagEnd = Word.find(">", TagStart+1)
            Image1 = self.RenderWord(Word[:TagStart], 0)
            self.RenderTag(Word[TagStart:TagEnd+1])
            if TagEnd != -1:
                Image2 = self.RenderWord(Word[TagEnd+1:], 0)
                Image = pygame.Surface((Image1.get_width() + Image2.get_width(), max(Image1.get_height(), Image2.get_height())))
                Image.blit(Image1, (0,0))
                Image.blit(Image2, (Image1.get_width(), 0))
            else:
                Image = Image1
        else:
            Image = self.CurrentFont.render(Word,1,self.CurrentColor)
        if AddToRow:
            # Wrap, if we must:
            if (self.WordWrapWidth) and (Image.get_width() + self.CurrentRowWidth > self.WordWrapWidth):
                self.FinishCurrentRow()
            self.CurrentColumnImages.append(Image)
            self.CurrentRowWidth += Image.get_width()
        return Image

# Create a renderer, so that it's always available:
TaggedRenderer = TaggedTextRenderer()

def RenderWrappedText(Text,WordWrapWidth,Color = Colors.White, FontName=None,FontSize=14,CenterFlag = 0):
    Font = GetFont(FontName,FontSize)
    Words = Text.split()
    Lines=[]
    CurrentLine=""
    MaxWidth = 0
    while (Words):
        if (CurrentLine!=""):
            TryLine=CurrentLine+" "+Words[0]
        else:
            TryLine=Words[0]
        Width = Font.size(TryLine)[0]
        if Width>WordWrapWidth and CurrentLine!="":
            Lines.append(CurrentLine)
            CurrentLine=""
        else:
            del Words[0]
            CurrentLine=TryLine
            MaxWidth = max(MaxWidth,Width)
    if (CurrentLine!=""):
        Lines.append(CurrentLine)
    Image = pygame.Surface((MaxWidth,Font.get_linesize() * len(Lines)))
    Y=0
    X = 0
    Image.fill((0,0,0))
    for Line in Lines:
        TempImage = Font.render(Line,1,Color)
        if CenterFlag:
            X = CenterCoord(MaxWidth,TempImage.get_width())
        Image.blit(TempImage,(X,Y))
        Y += Font.get_linesize()
    return Image

def ConcatenateSurfaces(ImageList):
    TotalImageWidth = 0
    TotalImageHeight = 0
    for Image in ImageList:
        TotalImageWidth += Image.get_width()
        TotalImageHeight = max(TotalImageHeight,Image.get_height())
    MasterImage = pygame.Surface((TotalImageWidth,TotalImageHeight))
    ImageX = 0
    for Image in ImageList:
        MasterImage.blit(Image,(ImageX,0))
        ImageX += Image.get_width()
    return MasterImage

def TextImage(Text, Color = Colors.White, FontSize = 18, FontName = None):
    Font = GetFont(FontName,FontSize)
    return Font.render(str(Text),1,Color)
    
class GenericTextSprite(pygame.sprite.Sprite):
    def __init__(self,Text,X,Y,Color=Colors.White,FontSize=18,FontName=None,CenterFlag=0,
                 WordWrapWidth = None):
        pygame.sprite.Sprite.__init__(self)
        self.Text=Text
        self.WordWrapWidth = WordWrapWidth
        self.FontName=FontName
        self.FontSize=FontSize
        self.Color=Color
        self.X=X
        self.Y=Y
        self.CenterFlag=CenterFlag
        self.Draw()
    def __str__(self):
        return "<Text sprite '%s'>"%(str(self.Text)[:50])
    def ReplaceText(self, NewText):
        self.Text = NewText
        self.Draw()
    def Draw(self):
        Font = GetFont(self.FontName,self.FontSize)
        if self.WordWrapWidth!=None:
            self.image = RenderWrappedText(str(self.Text),self.WordWrapWidth,self.Color,self.FontName,self.FontSize,self.CenterFlag)
        else:
            self.image = Font.render(str(self.Text),1,self.Color)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()        
        if self.CenterFlag:
            RectLeft = self.X - (self.image.get_width() / 2)
        else:
            RectLeft = self.X
        self.rect = pygame.Rect(RectLeft,self.Y,self.image.get_width(),self.image.get_height())        
    def Update(self,AnimationCycle):
        pass

class DummySprite:
    def __init__(self,rect):
        self.rect=rect

class TidySprite(pygame.sprite.Sprite):
    def __init__(self,Pane,*args,**kw):
        pygame.sprite.Sprite.__init__(self)
        self.Pane=Pane
    def kill(self):        
        pygame.sprite.Sprite.kill(self)
        self.Pane.Surface.blit(self.Pane.BackgroundSurface,self.rect,self.rect)
        Dirty(self.rect)
    def Update(self,AnimationCycle):
        pass    
    
class WidthTextSprite(pygame.sprite.Sprite):
    def __init__(self,Text,X,Y,Width,Height,Color=(255,255,255),FontSize=18,FontName=None,CenterFlag=0):
        pygame.sprite.Sprite.__init__(self)
        self.Text=Text
        self.FontName=FontName
        self.FontSize=FontSize
        self.Color=Color
        self.X=X
        self.Y=Y
        self.Width=Width
        self.Height=Height
        self.CenterFlag=CenterFlag
        self.Draw()
    def Draw(self):
        Font = GetFont(self.FontName,self.FontSize)
        self.image = pygame.Surface((self.Width,self.Height))
        self.rect = self.image.get_rect()        
        self.image.set_colorkey((0,0,0))
        self.image.fill((0,0,0))        
        FontSurface = Font.render(str(self.Text),1,self.Color)
        BlitX = (self.Width - FontSurface.get_width()) / 2
        BlitY = (self.Height - FontSurface.get_height()) / 2
        self.image.blit(FontSurface,(BlitX,BlitY))
##        
##        if self.CenterFlag:
##            RectLeft = self.X - (self.image.get_width() / 2)
##        else:
##            RectLeft = self.X
        self.rect = pygame.Rect(self.X,self.Y,self.Width,self.Height) ##RectLeft,self.Y,self.image.get_width(),self.image.get_height())        
    def Update(self,AnimationCycle):
        pass

class TextButtonSprite(pygame.sprite.Sprite):
    BorderWidth=1
    BorderPadX=2
    BorderPadY=2
    def __init__(self,Text,X,Y,Color=(255,255,255),FontSize=18,FontName=None,CenterFlag=0):
        pygame.sprite.Sprite.__init__(self)
        self.Text=Text
        self.Command=Text
        Font = GetFont(FontName,FontSize)
        TextImage = Font.render(str(Text),1,Color)
        self.image = pygame.Surface((TextImage.get_width() + self.BorderPadX*2,
                                     TextImage.get_height() + self.BorderPadY*2))
        self.rect = self.image.get_rect()
        self.image.blit(TextImage,(self.BorderPadX,self.BorderPadY))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image,(255,255,255),(0,0,self.image.get_width(),self.image.get_height()),self.BorderWidth)
        if (CenterFlag):
            X = X - (self.image.get_width() / 2)
        self.rect = pygame.Rect(X,Y,self.image.get_width(),self.image.get_height())
    def Update(self,AnimationCycle):
        pass

class BoxSprite(pygame.sprite.Sprite):
    "A sprite with a rectangle drawn on it.  Not very exciting."
    def __init__(self,X,Y,Width,Height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((Width,Height))
        self.image.fill(Colors.Black)
        #BoxSprite.image.set_colorkey(Colors.Black)
        pygame.draw.rect(self.image,Colors.White,(0,0,Width,Height),1)
        self.rect = self.image.get_rect()
        self.rect.left = X
        self.rect.top = Y      
    def Update(self,AnimationCycle):
        pass
    
class LineSprite(pygame.sprite.Sprite):
    "A sprite with a line (horizontal or vertical) drawn on it.  Not very exciting."
    def __init__(self,X,Y,X2,Y2,Color = Colors.White, Thickness = 1):
        pygame.sprite.Sprite.__init__(self)
        if (X==X2):
            Height = abs(Y2-Y)
            Width = Thickness
        else:
            Width = abs(X2-X)
            Height = Thickness
        self.image = pygame.Surface((Width,Height))
        self.image.fill(Color)
        #BoxSprite.image.set_colorkey(Colors.Black)
        #pygame.draw.rect(self.image,(255,255,255),(0,0,Width,Height),1)
        self.rect = self.image.get_rect()
        self.rect.left = min(X,X2)
        self.rect.top = min(Y,Y2)
    def Update(self,AnimationCycle):
        pass
    
def FancyAssBoxedText(Text, Font = None, FontSize = 24, Color = Colors.White, Spacing = 2, DrawBox = 1,
                      HighlightColor = Colors.Red, HighlightIndex = None, BackColor = Colors.Black):
    if HighlightIndex!=None:
        TextA = TextImage(Text[:HighlightIndex], Color, FontSize, Font)
        TextB = TextImage(Text[HighlightIndex], HighlightColor, FontSize, Font)
        TextC = TextImage(Text[HighlightIndex+1:], Color, FontSize, Font)
        Width = TextA.get_rect().width + TextB.get_rect().width + TextC.get_rect().width
        Height = max(TextA.get_rect().height, TextB.get_rect().height, TextC.get_rect().height)
        Words = pygame.Surface((Width, Height))
        Words.fill(BackColor)
        Words.blit(TextA, (0, 0))
        Words.blit(TextB, (TextA.get_rect().width, 0))
        Words.blit(TextC, (TextA.get_rect().width + TextB.get_rect().width, 0))
        del TextA
        del TextB
        del TextC
    else:
        Words = TextImage(Text, Color, FontSize, Font)
    Rect = Words.get_rect()
    Width = Rect.width + Spacing*6
    Height = Rect.height + Spacing*6
    Image = pygame.Surface((Width, Height))
    if DrawBox:
        pygame.draw.rect(Image, BackColor, (0, 0, Width, Height), 0) # filled rect #%%% Black?
        pygame.draw.rect(Image, (255,255,255), (0, 0, Width, Height), 1)
        pygame.draw.rect(Image, (160,160,160), (Spacing, Spacing, Width-Spacing*2, Height-Spacing*2), 1)
        pygame.draw.rect(Image, (90,90,90), (Spacing*2, Spacing*2, Width-Spacing*4, Height-Spacing*4), 1)
    Image.blit(Words, (Spacing*3,Spacing*3))
    return Image

def FancyAssBoxedSprite(Text, X, Y, *args, **kw):
    Image = FancyAssBoxedText(Text, *args, **kw)
    Sprite = GenericImageSprite(Image, X, Y)
    Sprite.Text = Text
    return Sprite

class CursorSprite(TidySprite):
    AnimateSpeed = 35
    def __init__(self,Pane,X,Y,Color, Width, Height):
        TidySprite.__init__(self,Pane)
        self.Color = Color
        #self.image = pygame.Surface((3, 3)) #pygame.Surface((RoomWidth + 3, RoomHeight + 3))
        self.image = pygame.Surface((Width, Height))   ##RoomWidth + 3, RoomHeight + 3))
        self.image.set_alpha(100)
        self.image.set_colorkey(Colors.Black)
        self.image.fill(Colors.Black)
        self.Width = Width
        self.Height = Height
        self.Draw()
        self.rect = self.image.get_rect()
        self.rect.left = X
        self.rect.top = Y
    def Draw(self):
        pygame.draw.rect(self.image, self.Color, (0,0, self.Width, self.Height))  #RoomWidth, RoomHeight))
    def Update(self,AnimationCycle):
        Factor = 0.3 + 0.7 * abs(AnimationCycle%(self.AnimateSpeed*2) - self.AnimateSpeed) / float(self.AnimateSpeed)
        self.image.set_alpha(int(Factor*255))



class GlowingTextSprite(TidySprite):
    AnimateSpeed = 35
    def __init__(self, Pane, Text, X, Y, Color = Colors.White, Delay = 0):
        TidySprite.__init__(self,Pane)
        self.TextImage = TextImage(Text, Color, FontSize = 36) ##pygame.Surface((RoomWidth + 3, RoomHeight + 3))
        TextRect = self.TextImage.get_rect()
        self.image = pygame.Surface((TextRect.width, TextRect.height))
        self.image.set_alpha(0)
        self.image.set_colorkey(Colors.Black)
        self.image.blit(self.TextImage,(0,0))
        self.rect = self.image.get_rect()
        self.rect.left = X - self.rect.width / 2
        self.rect.top = Y - self.rect.height / 2
        self.Tick = 0
        self.Delay = Delay
    def Update(self,AnimationCycle):
        self.Tick += 1
        if (self.Tick < (51 + self.Delay)):
            Alpha = max(0, (self.Tick - self.Delay)*5)
        elif self.Tick > 100 :
            Alpha = 255 - (self.Tick - (self.Delay+100))*3
        else:
            return
        if Alpha<0:
            self.kill()
            return
        self.image.set_alpha(Alpha)
        Dirty(self.rect)

def CombatLog(Text):
    #print "--CL--", Text
    # Comment this out, except when we're re-balancing powerlevels:
    #GlobalCombatLog.write(Text+"\n")
    #GlobalCombatLog.flush()
    pass



class BranchedFile:
    """
    Writing to a BranchedFile causes the data to be written to two different files.
    """
    def __init__(self, f, f2):
        self.f = f; self.f2 = f2
        self.lock = threading.Lock()
    def write(self, *args):
        self.lock.acquire()
        try:
            self.f.write(*args)
            self.f.flush()
            self.f2.write(*args)
        finally:
            self.lock.release()


class FlushFile:
    def __init__(self, name, mode):
        self.f = open(name, mode)
    def write(self, *args):
        try:
            self.f.write(*args)
            self.f.flush()
        except:
            pass # :(            



def GetUserDataDir():
    "Returns the name of a directory in which to write user specific stuff"
    # Linux users expect user-specific files to be written to that user's directory.
    # Windows users expect application's files to be written to that application's directory.
    # We do the "expected behavior" in each case.
    if os.name == "posix":
        if os.environ['HOME']:
            return os.path.join(os.environ['HOME'], ".tendrils")
        else:
            sys.exit("$HOME not set - can't write data") # HAW HAW!
    return os.getcwd()

def UserDataFileName(FileName):
    "Constructs a name for a user specific data file"
    return os.path.join(GetUserDataDir(), FileName)

def GetSharedDataDir():
    "Returns the name of a directory in which to write stuff shared between users"
    # otherwise, just stick stuff in the current directory
    # until or unless i figure out something smarter to do
    return os.getcwd()
    
def SharedDataFileName(FileName):
    "Constructs a name for a data file shared between users"
    return os.path.join(GetSharedDataDir(), FileName)


def Glue(BaseFileName, ImageCount):
    "TEMP: Glue several images into one huge one"
    Images = []
    Width = 0
    Height = 0
    for Index in range(ImageCount):
        print BaseFileName
        FilePath = BaseFileName % Index
        TheImage = pygame.image.load(FilePath)
        Images.append(TheImage)
        Height = max(Height, TheImage.get_rect().height)
        Width += TheImage.get_rect().width
    BigBiff = pygame.Surface((Width, Height))
    X = 0
    for Index in range(ImageCount):
        BigBiff.blit(Images[Index],(X, 0), )
        X += Images[Index].get_rect().width
    pygame.image.save(BigBiff, "Glue.bmp")
    
class JoyConfigClass:
    def __init__(self):
        # self.Arrows maps directions (and special buttons "select" and "start") to the
        # index of the button corresponding to that direction. 
        self.Arrows = {}
        self.ButtonToDirection = {}
        for Direction in Directions.AllDirections:
            self.Arrows[Direction] = None
        self.Arrows["start"] = None
        self.Arrows["select"] = None
    def Load(self, MemoryCard):
        # Get from memory-card:
        self.ButtonToDirection = {}
        for Direction in Directions.AllDirections:
            Button = MemoryCard.Get("JoyConfig%s"%Direction)
            self.Arrows[Direction] = Button
            if Button!=None:
                self.ButtonToDirection[Button] = Direction
        StartButton = MemoryCard.Get("JoyConfigstart")
        self.Arrows["start"] = StartButton
        if StartButton:
            self.ButtonToDirection[self.Arrows["start"]] = "start"
        SelectButton = MemoryCard.Get("JoyConfigselect")
        self.Arrows["select"] = SelectButton
        if SelectButton:
            self.ButtonToDirection[self.Arrows["select"]] = "select"
        
# A HappyFont is a font with TWO COLORS - a foreground color, and black.  (Normal text
# sometimes is hard to read, if you get white-on-white or red-on-red).
HappyFonts = {}
def BuildHappyFont(Color, Char):
    global HappyFonts
    Sprite1 = GenericTextSprite(Char, 0, 0, Color, FontSize=24)
    Sprite2 = GenericTextSprite(Char, 0, 0, (11,11,11), FontSize=24)
    Image = pygame.Surface((Sprite1.rect.width + 2, Sprite1.rect.height + 2))
    Image.blit(Sprite2.image, (2, 2))
    Image.blit(Sprite1.image, (0, 0))
    # Save it in the dictionary:
    if not HappyFonts.has_key(Color):
        HappyFonts[Color] = {}
    HappyFonts[Color][Char] = Image
def BuildHappyFonts():
    for Color in (Colors.White, Colors.Red, Colors.Green, Colors.Purple, Colors.Blue):
        for Char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!0123456789":
            BuildHappyFont(Color, Char)

def GetTiledImage(Width, Height, SourceImage):
    Surface = pygame.Surface((Width, Height))
    Y = -5
    while (Y<Height):
        X = -5
        while (X < Width):
            Surface.blit(SourceImage, (X, Y))
            X += SourceImage.get_rect().width
        Y += SourceImage.get_rect().height
    return Surface
            
        

#######################
# For combat system calibration:
GlobalCombatLog = open(UserDataFileName("CombatLog.txt"),"w")
