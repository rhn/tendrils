import math
import random
from Utils import *
from Options import *
import Resources
import sys
import Global
import Music
import types

ARROW_KEY_TICKS = 12

class ScreenTypes:
    "Enumeration: These are all the screens used in Tendrils"
    Battle = "Battle"
    Dialog = "Dialog"
    Maze = "Maze"
    AttractMode = "Attract Mode"
    NameEntry = "Name Entry"
    Equip = "Equip"
    Shop = "Shop"
    Roster = "Roster"

class HighlightingBoxSprite(pygame.sprite.Sprite):
    Pad = 1
    LineWidth = 1
    AnimateSpeed = 25
    def __init__(self,Sprite,Pane):
        pygame.sprite.Sprite.__init__(self)
        self.Pane = Pane
        Width = Sprite.rect.width + self.LineWidth*2 + self.Pad*2
        Height = Sprite.rect.height + self.LineWidth*2 + self.Pad*2
        self.image = pygame.Surface((Width,Height))
        self.image.fill(Colors.Black)
        self.image.set_colorkey(Colors.Black)
        pygame.draw.rect(self.image,Colors.White,(0,0,Width,Height),self.LineWidth)
        self.rect = self.image.get_rect()
        self.rect.left = Sprite.rect.left - self.LineWidth - self.Pad + self.Pane.BlitX
        self.rect.top = Sprite.rect.top - self.LineWidth - self.Pad + self.Pane.BlitY
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.Pane.Surface.blit(self.Pane.BackgroundSurface,self.rect,self.rect)
        Dirty(self.rect)
    def Update(self,AnimationCycle):
        ##print "Update!"
        Factor = 0.3 + 0.7 * abs(AnimationCycle%(self.AnimateSpeed*2) - self.AnimateSpeed) / float(self.AnimateSpeed)
        self.image.set_alpha(int(Factor*255))




class TendrilsGUI:
    "Mixin class for GUI - either a SCREEN (the whole display area), or a PANE (a sub-rectangle of the display area"
    def __init__(self):
        # The three layers of sprites - disjoint, and include ALL sprites:        
        self.BackgroundSprites = pygame.sprite.RenderUpdates()
        self.ForegroundSprites = pygame.sprite.RenderUpdates()
        self.AnimationSprites = pygame.sprite.RenderUpdates()
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        # Useful sprite groups:
        self.AllSprites = pygame.sprite.RenderUpdates()
        self.MouseOverSprites = pygame.sprite.Group() # singleton
        #self.TooltipSprites = pygame.sprite.RenderUpdates()
        #
        self.BlitX=0
        self.BlitY=0
    def KillSpritesInGroup(self,Group):
        for Sprite in Group.sprites():
            Sprite.kill()
    def AddAnimationSprite(self,Sprite):
        self.AnimationSprites.add(Sprite)
        self.AllSprites.add(Sprite)
    def AddForegroundSprite(self,Sprite):
        self.ForegroundSprites.add(Sprite)
        self.AllSprites.add(Sprite)
    def AddBackgroundSprite(self,Sprite):
        self.BackgroundSprites.add(Sprite)
        self.AllSprites.add(Sprite)
        
class TendrilsPane(TendrilsGUI):
    """
    A pane is a rectangular piece of a larger screen.  Panes are re-usable (e.g. the same pane could be used
    on equipment and shopping screens), and have their own collections of sprites.  
    """
    def __init__(self,Master,BlitX,BlitY,Width,Height,Name="Pane"):
        TendrilsGUI.__init__(self)
        self.Master = Master
        self.Name=Name
        self.BlitX=BlitX
        self.BlitY=BlitY
        self.Width=Width
        self.Height=Height        
        self.Surface = Master.Surface.subsurface((BlitX,BlitY,Width,Height))       
        self.BackgroundSurface = Master.BackgroundSurface.subsurface((BlitX,BlitY,Width,Height))
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
    def Redraw(self):        
        self.RedrawBackground()
        self.Surface.fill(Colors.Black)
        self.Surface.blit(self.BackgroundSurface,(0,0))
        self.ForegroundSprites.draw(self.Surface)
        self.AnimationSprites.draw(self.Surface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
    def GetLocalPosition(self,MasterSurfacePosition):
        (MasterX,MasterY) = MasterSurfacePosition
        if MasterX<self.BlitX or MasterX>self.BlitX+self.Width:
            return None
        if MasterY<self.BlitY or MasterY>self.BlitY+self.Height:
            return None
        return (MasterX-self.BlitX,MasterY-self.BlitY)        
    def FindMouseOverSprites(self,Position):        
        self.MouseOverSprites.empty()
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite:
            self.MouseOverSprites.add(Sprite)            
    def HandleMouseMoved(self,Position,Buttons):
        return
        ##print "HMM in pane:LP=",LongPause
        if LongPause and len(self.TooltipSprites.sprites()):            
            return
        for Sprite in self.TooltipSprites.sprites():
            Sprite.kill()
        self.FindMouseOverSprites(Position)
    def HandleLoop(self):        
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface)
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface)
        self.Update()
        DirtyRects = self.ForegroundSprites.draw(self.Surface)
        Dirty(DirtyRects,self.BlitX,self.BlitY)
        DirtyRects = self.AnimationSprites.draw(self.Surface)
        Dirty(DirtyRects,self.BlitX,self.BlitY)
    def Update(self):
        pass
    def HandleMouseClickedHere(self,Position,Button):
        pass
   
class TendrilsScreen(TendrilsGUI):
    """
    A screen handles events and sprites, plus the relevant gameplay.  The most important subclass is
    BattleScreen.
    """
    ScreenType = None
    CanCancel = 0
    PickleAttributes=[]
    UseBackground = 0
    def __init__(self,App):
        TendrilsGUI.__init__(self)
        self.SongY = 600
        self.App=App
        self.GetSurfaces()
        self.AnimationCycle = 0
        self.MouseOverCount = 0
        self.SubPanes = []
        # Magic to make joypad work well:
        self.ArrowKeyResponseCount = 0
        self.ArrowKeyResponseWait = 0
        self.ArrowKeysPressed=[]
        # Tracking the currently highlighted thing:
        self.HighlightedSprite = None
        self.HighlightSprite = None        
        self.PopupMenu = None
        self.OldMousePosition=None
        self.SongInfoSprite = None
    def SetHighlightedSprite(self, Sprite, OwningPane = None):
        if self.HighlightSprite:
            self.HighlightSprite.kill()
            self.HighlightSprite=None
        self.HighlightedSprite = Sprite
        if Sprite:
           self.HighlightSprite = HighlightingBoxSprite(Sprite, OwningPane)
           self.AddAnimationSprite(self.HighlightSprite)
    def GetArrowKeyState(self):
        TheList = []
        KeysPressed = pygame.key.get_pressed()
        if KeysPressed[Keystrokes.Up[0]] or KeysPressed[Keystrokes.Up[1]]:
            TheList.append(Directions.Up)
        if KeysPressed[Keystrokes.Down[0]] or KeysPressed[Keystrokes.Down[1]]:
            TheList.append(Directions.Down)
        if KeysPressed[Keystrokes.Left[0]] or KeysPressed[Keystrokes.Left[1]]:
            TheList.append(Directions.Left)
        if KeysPressed[Keystrokes.Right[0]] or KeysPressed[Keystrokes.Right[1]]:
            TheList.append(Directions.Right)
        return TheList
    def HandleArrowKeys(self,PushedList):
        pass # override this to make arrow keys DO things!
    def GetSurfaces(self):
        MasterSurface = self.App.GetMainSurface()        
        self.Width=MasterSurface.get_width()
        self.Height=MasterSurface.get_height()
        self.Surface = MasterSurface        
        self.BackgroundSurface = self.App.BackgroundSurface        
    def Reactivate(self):
        self.MasterSurface = self.App.GetMainSurface()
        self.BlitX=0
        self.BlitY=0
        self.Width=self.MasterSurface.get_width()
        self.Height=self.MasterSurface.get_height()
        self.BackgroundSurface = self.App.BackgroundSurface ##pygame.Surface((self.Width,self.Height))
        self.Surface = self.App.GetMainSurface() #pygame.Surface((self.Width,self.Height))
        self.Surface.set_colorkey(Colors.Black)
        self.Surface.fill(Colors.Black)
        if hasattr(self,"AllSprites"):
            self.KillSpritesInGroup(self.AllSprites)
        self.AllSprites = pygame.sprite.RenderUpdates()        
        self.BackgroundSprites = pygame.sprite.RenderUpdates()
        self.ForegroundSprites = pygame.sprite.RenderUpdates()
        self.AnimationSprites = pygame.sprite.RenderUpdates()        
        self.MouseOverSprites = pygame.sprite.Group() # singleton
        self.SubPanes = []
        self.MouseOverCount=0
        self.AnimationCycle=0
        self.HighlightedSprite = None
        self.HighlightSprite = None
        self.PopupMenu = None
        ##
        self.ArrowKeyResponseCount = 0
        self.ArrowKeyResponseWait = 0
        self.ArrowKeysPressed=[]
        self.OldMousePosition=None
        
        
    def HandleMouseClicked(self,Position,Button):
        for SubPane in self.SubPanes:
            SubPosition = SubPane.GetLocalPosition(Position)
            if SubPosition:
                SubPane.HandleMouseClickedHere(SubPosition,Button)
        self.HandleMouseClickedHere(Position,Button)
    def HandleMouseClickedHere(self,Position,Button):
        pass
    def HandleMouseMoved(self,Position,Buttons):
        return
    def FindMouseOverSprites(self,Position):        
        self.MouseOverSprites.empty()
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.AllSprites)
        if Sprite:
            self.MouseOverSprites.add(Sprite)            
        
    def BaseGetState(self):        
        Dict = {"AnimationCycle":0}
        for AttributeName in self.PickleAttributes:
            Dict[AttributeName] = getattr(self,AttributeName,None)
        return Dict
    def BaseSetState(self,Dict):
        self.AllSprites=pygame.sprite.RenderUpdates()
        for Item in Dict.items():
            setattr(self,Item[0],Item[1])
    def IsSaveable(self):
        return 0
    def Save(self,File):
        pass
    def Restore(self,File):
        pass
    def RedrawBackground(self):
        #%%%
        self.BackgroundSurface.fill((Colors.Black))
        self.DeepSprites.draw(self.BackgroundSurface)
        #self.BackgroundSurface.fill(Colors.Black)
        #self.BackgroundSprites.draw(self.Surface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty(self.BackgroundSurface.get_rect())
        ##print "Redraw back..."
    def Redraw(self):
        self.RedrawBackground()
        #self.B.fill((0,0,0))
        self.Surface.blit(self.BackgroundSurface,(0,0))
        for Pane in self.SubPanes:
            Pane.Redraw()
        self.ForegroundSprites.draw(self.Surface)
        self.AnimationSprites.draw(self.Surface)
        Dirty(self.Surface.get_rect())
        ##pygame.display.flip()
    def IsActive(self):
        return (self == self.App.CurrentScreen)        
    def HandleLoop(self):
        """
        HandleLoop is an important function (which is generally overridden in subclasses).  It is called
        once per tick.  The HandleLoop method should (1) erase foreground sprites, (2) handle user events
        and do other gameplay stuff, and (3) redraw foreground sprites.  Whatever changes/additions/deletions
        you make to the sprites in step (2) are reflected in the screen update of step (3).
        """
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface) 
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface)
        self.AnimationCycle+=1
        if (self.AnimationCycle>MaxAnimationCycle):
            self.AnimationCycle=0        
        for Sprite in self.AllSprites.sprites():
            Sprite.Update(self.AnimationCycle)
        for Pane in self.SubPanes:
            Pane.HandleLoop()
        self.Update()
        self.HandleEvents()
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)
    def Update(self):
        pass

    def HandleJoyButton(self, Event):
        pass
    def HandleJoyButtonUp(self, Event):
        pass
    def HandleEvent(self,Event):
        if Event.type is pygame.MOUSEMOTION:
            if Event.pos!=self.OldMousePosition:
                self.OldMousePosition=Event.pos
                self.HandleMouseMoved(Event.pos,Event.buttons)
        elif Event.type is (pygame.JOYBUTTONDOWN):
            Global.JoyButtons[Event.button] = 1
            self.HandleJoyButton(Event)
        elif Event.type is (pygame.JOYBUTTONUP):
            Global.JoyButtons[Event.button] = 0
            self.HandleJoyButtonUp(Event)
        elif Event.type is pygame.QUIT:
            self.App.Quitting = 1
            return
        elif Event.type is pygame.KEYDOWN:
            if Event.key == 61 and not IsEXE(): # =
                print "\n>>>SUB-INTERPRETER: ACTIVE<<<"
                while (1):
                    SomeCode = sys.stdin.readline()
                    if SomeCode[0]=="=":
                        SomeCode = SomeCode[1:]
                    if not SomeCode.strip():
                        print ">>>SUB-INTERPRETER: OFFLINE<<<"
                        pygame.event.pump() # Test...
                        break
                    try:
                        exec(SomeCode, globals(), locals())
                    except:
                        traceback.print_exc()
                    #print eval(SomeCode)
            else:
                self.HandleKeyPressed(Event.key)
        elif Event.type is pygame.MOUSEBUTTONDOWN:
            self.HandleMouseClicked(Event.pos,Event.button)
        elif Event.type is pygame.MOUSEBUTTONUP:
            self.HandleMouseUp(Event.pos, Event.button)
        elif Event.type == SongOverEvent:
            self.HandleSongComplete()
######        else:
######            print Event, type(Event)
    def HandleSongComplete(self):
        print "Screen::HandleSongComplete()"
        if Global.CurrentSong.Type != SongType.Sting:
            Music.RestartSong() # start again!
            return
        Global.CurrentSong = None
        if Global.QueueSong:
            Global.CurrentSong = None
            Music.PlaySong(Global.QueueSong)
            Global.QueueSong = None
        
    def HandleMouseUp(self, Position, Button):
        pass
    def HandleEvents(self):
        # Handle arrow keys!  We respond to held-down keys once every few ticks.
        # When they lift up arrow keys, we respond (if we haven't already).
        # When response-count gets high, descrease the wait time?
        NewArrowKeys = self.GetArrowKeyState()
        if self.ArrowKeysPressed!=NewArrowKeys:
            # Handle on lift-up:
##            if len(NewArrowKeys)==0 and len(self.ArrowKeysPressed) and self.ArrowKeyResponseCount==0:
##                self.HandleArrowKeys(self.ArrowKeysPressed)
            ###print "HANDLE arrow keys!", self.ArrowKeysPressed
            self.ArrowKeysPressed = NewArrowKeys
            self.HandleArrowKeys(self.ArrowKeysPressed)
            self.ArrowKeyResponseWait=0
            self.ArrowKeyResponseCount=0
        else:
            if len(self.ArrowKeysPressed):
                self.ArrowKeyResponseWait += 1
                # Handle on hold-down:
                if self.ArrowKeyResponseWait>ARROW_KEY_TICKS:
                    self.HandleArrowKeys(self.ArrowKeysPressed)
                    self.ArrowKeyResponseCount+=1
                    self.ArrowKeyResponseWait=0
        for Event in pygame.event.get():
            self.HandleEvent(Event)
    def Debug(self):
        print "Debug:",self
        self.Redraw()
    def HandleKeyPressed(self,Key):
        if Key==Keystrokes.Debug:
            self.Debug()
        elif Key is pygame.K_ESCAPE:
            if self.CanCancel:
                self.App.PopScreen(self)
                return
    def GetSurface(self):
        return self.Surface
    def Activate(self):
        self.Redraw()
        for SubPane in self.SubPanes:
            SubPane.Redraw()
    def DrawBackground(self):
        pass
    def PopupMenuChoice(self,Text):
        pass
    def SummonSong(self, SongName, SongTempo = 1.0):
        #print "SUMMON SONG:", SongName, self.SongY
        if type(SongName) in (types.StringType, types.UnicodeType):
            Song = Global.MusicLibrary.GetSong(SongName) #Resources.SongDict.get(SongName.lower(), None)
        else:
            Song = SongName
        if not Song:
            print "** Error: Missing song '%s'"%SongName
            return
        Result = Music.PlaySong(Song)
        if Result:
            if self.SongInfoSprite:
                self.SongInfoSprite.kill()
            if Song:
                #print "Build sprite:"
                self.SongInfoSprite = SongInfoSprite(self, Song, self.SongY)
                self.AddAnimationSprite(self.SongInfoSprite)
    def GetPanelWrapImage(self, Width, Height, Color, Label):
        "Get wrapping image for panels"
        BasePad = 4
        TopPad = 5
        TextX = 50
        Image = pygame.Surface((Width, Height))
        Text = TextImage(Label)
        pygame.draw.rect(Image, Color, (0, 0, Image.get_rect().width, Image.get_rect().height), 0)
        pygame.draw.rect(Image, Colors.Black, (BasePad*2 + 1, BasePad + TopPad*2 + 1, 
                                               Image.get_rect().width - BasePad*4 - 2,
                                               Image.get_rect().height - (TopPad*2+BasePad*4) - 2),0)
        Image.blit(Text, (TextX, TopPad + 1 - (Text.get_rect().height / 2)))
        X = TextX + Text.get_rect().width + 10
        pygame.draw.line(Image, Colors.White, (X, TopPad+1), (Width - BasePad - 1, TopPad+1))
        pygame.draw.line(Image, Colors.White, (Width - BasePad - 1, TopPad+1), (Width - BasePad-1, Height - BasePad-1))
        pygame.draw.line(Image, Colors.White, (Width - BasePad-1, Height - BasePad-1), (BasePad+1, Height - BasePad-1))
        pygame.draw.line(Image, Colors.White, (BasePad+1, Height - BasePad-1), (BasePad+1, TopPad+1))
        pygame.draw.line(Image, Colors.White, (BasePad+1, TopPad+1), (TextX, TopPad+1))
        return Image        
    def ShowGlowingText(self, Text, Y = None, Delay = 0):
        if not Y:
            Y = self.Height / 2
        Sprite = GlowingTextSprite(self, Text, self.Width / 2, Y, Delay = Delay)
        self.AddAnimationSprite(Sprite)


class SongInfoSprite(TidySprite):
    # Y is the BOTTOM of the sprite.
    def __init__(self, Pane, Song, Y):
        TidySprite.__init__(self,Pane)
        Str = "<IMG:Music>%s\n"%Song.Name
        if Song.SourceGame:
            Str += "<CN:LIGHTGREY>From: <CN:WHITE>%s\n"%Song.SourceGame
        if Song.Author:
            Str += "<CN:LIGHTGREY>By: <CN:WHITE>%s\n"%Song.Author
        if Song.Dumper:
            Str += "<CN:LIGHTGREY>Dump: <CN:WHITE>%s\n"%Song.Dumper
        if Song.Remixer:
            Str += "<CN:LIGHTGREY>Remix: <CN:WHITE>%s\n"%Song.Remixer
        self.TextImage = TaggedRenderer.RenderToImage(Str)
        TextRect = self.TextImage.get_rect()
        self.image = pygame.Surface((TextRect.width, TextRect.height))
        self.image.set_alpha(0)
        self.image.set_colorkey(Colors.Black)
        self.image.blit(self.TextImage,(0,0))
        self.rect = self.image.get_rect()
        self.rect.right = Pane.Width
        self.rect.bottom = Y
        self.Tick = 0
        self.PermamentFlag = 0
    def Update(self,AnimationCycle):
        if self.PermamentFlag:
            return
        self.Tick += 1
        if (self.Tick < (63)):
            Alpha = self.Tick*4
        elif self.Tick > 500 :
            Alpha = 255 - (self.Tick - 500)*3
        else:
            return
        if Alpha<0:
            self.kill()
            return
        self.image.set_alpha(Alpha)
        Dirty(self.rect)    


        
class PopupMenu(pygame.sprite.Sprite):
    """
    Popup menus - not really used yet.
    """
    Alpha = 150
    def __init__(self,Screen,Names,X,Y):
        pygame.sprite.Sprite.__init__(self)
        self.Screen=Screen
        if self.Screen.PopupMenu:
            self.Screen.PopupMenu.kill()
        self.Screen.PopupMenu = self
        self.Names=Names
        self.NameY=[]
        self.RegularImages = []
        self.HiliteImages = []
        self.SelectedIndex=0
        self.GenerateMenu()
        self.rect=self.image.get_rect()
        if (X + self.rect.width > self.Screen.Width):
            X -= (X + self.rect.width - self.Screen.Width)
        if (Y + self.rect.height > self.Screen.Height):
            Y -= (Y + self.rect.height - self.Screen.Height)
        self.rect.left=X
        self.rect.top=Y
        self.Draw()
        self.Screen.AddAnimationSprite(self)
    def Update(self,AnimationCycle):
        self.Screen.Surface.blit(self.Screen.BackgroundSurface,self.rect,self.rect)
        Dirty(self.rect)
    def GenerateMenu(self):
        Width = 0
        Height = 0
        Font = GetFont(FONT_PRESS_START,24)
        Images=[]
        CurrentY=0
        for Name in self.Names:
            # Normal and hilite images:
            Image = Font.render(Name,1,Colors.White)
            Image.set_alpha(self.Alpha)
            self.RegularImages.append(Image)
            Image = Font.render(Name,1,Colors.Black)
            #Image.set_alpha(self.Alpha)
            TempImage = pygame.Surface((Image.get_width(),Image.get_height()))
            TempImage.fill(Colors.White)
            TempImage.blit(Image,(0,0))
            #TempImage.set_alpha(self.Alpha)
            self.HiliteImages.append(TempImage)
            # Track positions:
            self.NameY.append(CurrentY)
            CurrentY += Image.get_height()
            Width = max(Width,Image.get_width())
            Height += Image.get_height()
        self.image = pygame.Surface((Width,Height))
        self.image.set_alpha(self.Alpha)
    def Draw(self):
        self.image.fill(Colors.Black)
        for Index in range(len(self.Names)):
            if Index==self.SelectedIndex:
                Image = self.HiliteImages[Index]
            else:
                Image = self.RegularImages[Index]
            self.image.blit(Image,(0,self.NameY[Index]))
    def ScrollUp(self):
        self.SelectedIndex -= 1
        if self.SelectedIndex<0:
            self.SelectedIndex=0
        self.Draw()
    def ScrollDown(self):
        self.SelectedIndex += 1
        if self.SelectedIndex>=len(self.Names):
            self.SelectedIndex=len(self.Names)-1
        self.Draw()
    def Choose(self):
        self.Screen.PopupMenu=None
        self.kill()
        self.Screen.PopupMenuChoice(self.Names[self.SelectedIndex])
    def Cancel(self):
        self.Screen.PopupMenu=None
        self.kill()
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.Screen.Surface.blit(self.Screen.BackgroundSurface,self.rect,self.rect)
        Dirty(self.rect)



if PSYCO_ON:
    psyco.bind(TendrilsScreen.HandleLoop)
    psyco.bind(TendrilsScreen.HandleEvent)         