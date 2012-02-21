"""
Joystick config screen.  Simple, functional.
"""
from Utils import *
from Constants import *
import Screen
import ItemPanel
import Global
import Resources
import os
import time
import math
import string
import Party


class JoyConfigScreen(Screen.TendrilsScreen):
    def __init__(self):
        self.LabelSprites = {} # map direction (or "start" or "select") to sprite
        self.SettingSprites = {} # map direction (or "start" or "select") to sprite
        self.DirNames = ["Up", "Down", "Left", "Right", "Start", "Select", "NW", "NE", "SW", "SE"]
        self.Directions = [1,2,3,4,"start","select",5,6,7,8]
        Screen.TendrilsScreen.__init__(self, Global.App)
        self.HighlightedLabelSprite = None
        self.DrawBackground()
    def DrawBackground(self):
        self.ButtonSprites = pygame.sprite.Group()
        self.LabelGroup = pygame.sprite.Group()
        TheImage = TaggedRenderer.RenderToImage("<CENTER><CN:YELLOW>Joy Config</C>\nPress dance pad to configure the <CN:BRIGHTGREEN>highlighted</C> direction.</CENTER>", 700, FontSize = 24)
        Sprite = GenericImageSprite(TheImage, 50, 10)
        self.AddBackgroundSprite(Sprite)
        Sprite = GenericTextSprite("(Click to pick a setting to change.  Hit ESC to clear a setting)", 400, 60, FontSize = 24, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        Y = 150
        LabelX = 20
        FirstLabelSprite = None
        PrevLabelSprite = None
        for Index in range(len(self.DirNames)):
            Direction = self.Directions[Index]
            # Clickable label, with direction name 
            LabelSprite = GenericTextSprite(self.DirNames[Index]+":", LabelX, Y, FontSize = 36)
            LabelSprite.Direction = Direction
            X = LabelSprite.rect.right + 5
            if not FirstLabelSprite:
                FirstLabelSprite = LabelSprite
            self.AddBackgroundSprite(LabelSprite)
            self.LabelGroup.add(LabelSprite)
            self.LabelSprites[Direction] = LabelSprite
            if PrevLabelSprite:
                PrevLabelSprite.Next = LabelSprite
            PrevLabelSprite = LabelSprite
            # Current button setting:
            ButtonSetting = Global.JoyConfig.Arrows.get(self.Directions[Index])
            if ButtonSetting == None:
                Str = "None"
            else:
                Str = "Button %s"%ButtonSetting
            Sprite = GenericTextSprite(Str, X, Y, FontSize = 36)
            self.AddBackgroundSprite(Sprite)
            self.SettingSprites[Direction] = Sprite
            Y += Sprite.rect.height + 20
            if Index==5:
                Y = 150
                LabelX = 420
        LabelSprite.Next = FirstLabelSprite # wrap around to the top!
        # And exit button in the corner:
        Sprite = FancyAssBoxedSprite("Done", 720, 550, HighlightIndex = 0)
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        self.HighlightLabelSprite(FirstLabelSprite)
    def HandleJoyButton(self, Event):
        #print Event
        #print dir(Event)
        #print Event.button
        Button = Event.button
        # Redraw our setting sprite:
        Direction = self.HighlightedLabelSprite.Direction
        self.SettingSprites[Direction].ReplaceText("Button %s"%Button)
        # Set in the memory card:
        Global.MemoryCard.Set("JoyConfig%s"%Direction, Button)
        Global.JoyConfig.Load(Global.MemoryCard)
        # Highlight the next sprite:
        self.HighlightLabelSprite(self.HighlightedLabelSprite.Next)
    def ClearCurrentButton(self):
        # Redraw our setting sprite:
        Direction = self.HighlightedLabelSprite.Direction
        self.SettingSprites[Direction].ReplaceText("None")
        # Set in the memory card:
        Global.MemoryCard.Set("JoyConfig%s"%Direction, None)
        # Highlight the next sprite:
        self.HighlightLabelSprite(self.HighlightedLabelSprite.Next)
    def HandleKeyPressed(self, Key):
        if Key is pygame.K_ESCAPE:
            self.ClearCurrentButton()
            return
        if Key == ord("d"):
            Global.App.PopScreen(self)
            return
    def HighlightLabelSprite(self, Sprite):
        if self.HighlightedLabelSprite:
            self.HighlightedLabelSprite.Color = Colors.White
            # Force a re-coloring:
            self.HighlightedLabelSprite.ReplaceText(self.HighlightedLabelSprite.Text)
        self.HighlightedLabelSprite = Sprite
        self.HighlightedLabelSprite.Color = Colors.Green
        self.HighlightedLabelSprite.ReplaceText(self.HighlightedLabelSprite.Text)
        self.Redraw()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for button clicks:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            Global.App.PopScreen(self)
            return
        Sprite = pygame.sprite.spritecollideany(Dummy,self.LabelGroup)
        if Sprite:
            self.HighlightLabelSprite(Sprite)
