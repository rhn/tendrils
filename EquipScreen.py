"""
"Inventory isn't boring.  Inventory is LIFE!"
    - Quartermaster, Fallout Tactics
This is the equipment/status screen, reachable from the maze screen.
The user can change the armor and weapons and relics on all the
characters, and see the stats (STR, HP, EXP-to-level, etc).
"""

from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources

class EquipScreen(Screen.TendrilsScreen):
    UpperPanelHeight = 356
    PlayerSpriteX = 20
    PlayerSpriteY = 100
    ItemListingWidth = 640
    ItemX = 145
    ItemWidth = 104
    UpperItemY = 23
    LowerItemY = 204
    StatsX = 465
    PerksX = 646
    SlotX = [ItemX, ItemX + ItemWidth, ItemX + 2*ItemWidth,
             ItemX, ItemX + ItemWidth, ItemX + 2*ItemWidth]
    SlotY = [UpperItemY,UpperItemY,UpperItemY,
             LowerItemY,LowerItemY,LowerItemY]
    def __init__(self, App, Player):
        Screen.TendrilsScreen.__init__(self,App)
        self.Player = Player
        self.MouseOverEquipSprite = None
        self.MouseOverItemSprite = None
        self.TooltipSprite = None
        self.MousePosition = (0,0)
        self.KeysToFilterSlots = {ord("w"): EquipSlots.Weapon,
                                  ord("h"): EquipSlots.Head,
                                  ord("b"): EquipSlots.Body,
                                  ord("a"): EquipSlots.Arms,
                                  ord("f"): EquipSlots.Feet,
                                  ord("r"): EquipSlots.Relic,
                                  ord("u"): "Supplies"
                                  }        
        self.RenderInitialScreen()
        self.PlayEquipMusic()
    def HandleMouseMoved(self,Position,Buttons):
        self.FindMouseOverSprites(Position)
        SubPosition = self.ItemPanel.GetLocalPosition(Position)
        if SubPosition:
            MouseOverItemSprite = self.ItemPanel.FindMouseOverSprites(SubPosition)
        else:
            MouseOverItemSprite = self.MouseOverEquipSprite
        if MouseOverItemSprite == self.MouseOverItemSprite:
            if self.TooltipSprite:
                self.TooltipSprite.rect.left = Position[0] + 10
                self.TooltipSprite.rect.top = min(600 - self.TooltipSprite.rect.height, Position[1])
            return
        self.MouseOverItemSprite = MouseOverItemSprite
        # The mouse is over a different sprite.  Kill the tooltip sprite (if any)
        if self.TooltipSprite:
            self.TooltipSprite.kill()
            self.TooltipSprite = None
            self.Redraw() # ensure redraw!
        # If we're over a sprite, build a tooltip:
        if self.MouseOverItemSprite and self.MouseOverItemSprite.Item:
            self.TooltipSprite = ItemPanel.BuildTooltipSprite(self.MouseOverItemSprite.Item)
            self.TooltipSprite.rect.left = Position[0] + 10
            self.TooltipSprite.rect.top = min(600 - self.TooltipSprite.rect.height, Position[1])
            self.AddAnimationSprite(self.TooltipSprite)
    def FindMouseOverSprites(self, Position):
        self.MousePosition = Position
        self.MouseOverSprites.empty()
        OldSprite = self.MouseOverEquipSprite
        self.MouseOverEquipSprite = None
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite:
            self.MouseOverSprites.add(Sprite)
        if Sprite and (Sprite in self.EquipSprites.values()):
            self.MouseOverEquipSprite = Sprite
        if self.MouseOverEquipSprite != OldSprite:
            self.DrawStats()
    def RenderInitialScreen(self):
        self.DrawBackground()
        #####
        self.FilterSlot = None
        self.HighlightSprite = None
        self.ButtonSprites = pygame.sprite.Group()
        self.DrawButtons()
        ###
        self.EquipSprites = {}
        self.PlayerSprites = []
        self.DrawPlayer()
        ####
        self.StatSprites = []
        self.MouseOverItem = None
        self.DrawStats()
        ####
        self.ItemPanel = ItemPanel.ItemPanel(self, 0, self.UpperPanelHeight + 1,
            self.ItemListingWidth, self.Height - self.UpperPanelHeight - 1, Global.Party.GetItems(),
                                             self.ItemClicked, Player = self.Player)
        self.SubPanes.append(self.ItemPanel)
        
    def ItemClicked(self, ItemSprite):
        if self.Player.CanEquip(ItemSprite.Item):
            self.Player.Equip(ItemSprite.Item)
            self.MouseOverItem = None
            self.ItemPanel.MouseOverItemSprite = None
            if self.TooltipSprite:
                self.TooltipSprite.kill()
                self.TooltipSprite = None
            self.DrawEquip()
            self.DrawStats()
            self.ItemPanel.Redraw()
            Resources.PlayStandardSound("CursorMove.wav")
            self.ItemPanel.FindMouseOverSprites(self.ItemPanel.MousePosition)
        else:
            Resources.PlayStandardSound("Error.wav")
    def DrawStats(self, AlternateItem = None):
        # Don't modify stats for mouse hanging over a non-usable item
        if AlternateItem and not self.Player.CanEquip(AlternateItem):
            AlternateItem = None
        if self.MouseOverEquipSprite:
            RemovableItem = self.MouseOverEquipSprite.Item
        else:
            RemovableItem = None
        for Sprite in self.StatSprites:
            Sprite.kill()
        self.StatSprites = []
        Y = 10
        StatHeight = 20
        for StatTuple in [("Str", "STR"),
                          ("Dex", "DEX"),
                          ("Con", "CON"),
                          ("Int", "INT"),
                          ("Wis", "WIS"),
                          ("Cha", "CHA"),
                          ("AC","AC"),
                          ("MaxHP","MaxHP"),
                          ("MaxMP","MaxMP"),
                          ("ToHitBonus","ToHitBonus"),
                          ("DamageDice","DamageDice"),
                          ("DamageDie","DamageDie"),
                          ("DamageBonus","DamageBonus"),                          
                          ("AvgDam","AvgDam"),
                          ("Level", "Level"),
                          ("XP", "EXP"),
                          ("To level", "GetEXPToLevel"),
                          
                          ]:
            self.DrawStat(Y, StatTuple[0], StatTuple[1], AlternateItem, RemovableItem)
            Y += 20
        # Now draw perks:
        self.DrawPerks(AlternateItem, RemovableItem)
        self.Redraw()
    def DrawPerks(self, AlternateItem, RemovableItem):
        Y = 10
        CurrentPerks = self.Player.GetPerks()
        if AlternateItem:
            NakedPerks = self.Player.GetNakedPerks(AlternateItem.Slot)
            ModifiedPerks = {}
            for Perk in NakedPerks.keys():
                ModifiedPerks[Perk] = NakedPerks[Perk]
            for Perk in AlternateItem.Perks.keys():
                ModifiedPerks[Perk] = AlternateItem.Perks[Perk]
        elif RemovableItem:
            ModifiedPerks = self.Player.GetNakedPerks(RemovableItem.Slot)
        else:
            ModifiedPerks = CurrentPerks
        # Perks that aren't shown on equip-screen:
        NoShowPerks = {"Poison":1, "Sleep":1, "Silence":1, "Stone":1, "Paralysis":1}
        # Always show the header:
        Sprite = GenericTextSprite("-- Perks --", self.PerksX, Y, Colors.LightGrey)
        self.AddBackgroundSprite(Sprite)
        self.StatSprites.append(Sprite)
        Y += 20
        for Perk in CurrentPerks.keys():
            if not CurrentPerks[Perk]:
                continue
            if NoShowPerks.has_key(Perk):
                continue
            if ModifiedPerks.get(Perk):
                Color = Colors.White
            else:
                Color = Colors.Red
            Sprite = GenericTextSprite(Perk, self.PerksX, Y, Color)
            self.AddBackgroundSprite(Sprite)
            self.StatSprites.append(Sprite)
            Y += 20
        for Perk in ModifiedPerks.keys():
            if not ModifiedPerks[Perk]:
                continue
            if NoShowPerks.has_key(Perk):
                continue
            if not CurrentPerks.get(Perk):
                Sprite = GenericTextSprite(Perk, self.PerksX, Y, Colors.Green)
                self.AddBackgroundSprite(Sprite)
                self.StatSprites.append(Sprite)
                Y += 20
    def DrawStat(self, Y, Label, StatAttributeName, AlternateItem, RemovableItem):
        (OldHP, OldMP) = (self.Player.HP, self.Player.MP)
        if StatAttributeName == "AvgDam":
            CurrentStat = self.Player.GetAverageDamage()
            if AlternateItem:
                CurrentItem = self.Player.GetEquip(AlternateItem.Slot)
                self.Player.Equip(AlternateItem)
                ModifiedStat = self.Player.GetAverageDamage()
                self.Player.Remove(AlternateItem)
                if CurrentItem:
                    self.Player.Equip(CurrentItem)
            else:
                self.Player.Remove(RemovableItem)
                ModifiedStat = self.Player.GetAverageDamage()
                self.Player.Equip(RemovableItem)
        elif StatAttributeName == "GetEXPToLevel":
            CurrentStat = self.Player.GetEXPToLevel()
            ModifiedStat = CurrentStat # default            
        else:
            CurrentStat = getattr(self.Player, StatAttributeName)
            ModifiedStat = CurrentStat # default
        StatSprite = GenericTextSprite("%s: %s"%(Label, CurrentStat), self.StatsX, Y)
        self.AddBackgroundSprite(StatSprite)
        self.StatSprites.append(StatSprite)
        if not AlternateItem and not RemovableItem:
            self.Player.HP = OldHP # Fix!
            self.Player.MP = OldMP # Fix!
            return
        if StatAttributeName in ("GetEXPToLevel", "AvgDam", "EXP", "Level"):
            pass #computed already
        elif StatAttributeName in ("DamageDice", "DamageDie"):
            # Special-case code for DamageDice and DamageDie, which aren't additive:
            NakedStat = getattr(self.Player, "Naked"+StatAttributeName)
            if AlternateItem and getattr(AlternateItem, StatAttributeName):
                ModifiedStat = getattr(AlternateItem, StatAttributeName)
            elif RemovableItem and getattr(RemovableItem, StatAttributeName):
                ModifiedStat = NakedStat
            else:
                ModifiedStat = CurrentStat
        elif StatAttributeName == "MaxHP":
            # Actually toggle the item:
            CurrentStat = self.Player.MaxHP
            ModifiedStat = self.Player.MaxHP # default
            HP = self.Player.HP
            if AlternateItem:
                CurrentItem = self.Player.GetEquip(AlternateItem.Slot)
                self.Player.Equip(AlternateItem)
                ModifiedStat = self.Player.GetMaxHP()
                self.Player.Remove(AlternateItem)
                if CurrentItem:
                    self.Player.Equip(CurrentItem)
            else:
                self.Player.Remove(RemovableItem)
                ModifiedStat = self.Player.GetMaxHP()
                self.Player.Equip(RemovableItem)
            self.Player.HP = HP
        elif StatAttributeName == "MaxMP":
            # Actually toggle the item:
            CurrentStat = self.Player.MaxMP
            ModifiedStat = self.Player.MaxMP # default
            MP = self.Player.MP
            if AlternateItem:
                CurrentItem = self.Player.GetEquip(AlternateItem.Slot)
                self.Player.Equip(AlternateItem)
                ModifiedStat = self.Player.GetMaxMP()
                self.Player.Remove(AlternateItem)
                if CurrentItem:
                    self.Player.Equip(CurrentItem)
            else:
                self.Player.Remove(RemovableItem)
                ModifiedStat = self.Player.GetMaxMP()
                self.Player.Equip(RemovableItem)
            self.Player.MP = MP
        else:
            # Ordinary (additive) attributes:
            if AlternateItem:
                CurrentItem = self.Player.GetEquip(AlternateItem.Slot)
                if CurrentItem:
                    NakedStat = CurrentStat - getattr(CurrentItem, StatAttributeName)
                else:
                    NakedStat = CurrentStat
                ModifiedStat = NakedStat + getattr(AlternateItem, StatAttributeName)
            else:
                # What would happen if we took this off?
                ModifiedStat = CurrentStat - getattr(RemovableItem, StatAttributeName)
        self.Player.HP = OldHP # Fix!
        self.Player.MP = OldMP # Fix!
                
        if ModifiedStat == CurrentStat:
            return
        if float(ModifiedStat) > float(CurrentStat):
            Color = Colors.Green
        else:
            Color = Colors.Red
        ModStatSprite = GenericTextSprite("--> %s"%ModifiedStat, self.StatsX + StatSprite.rect.width + 5, Y, Color)
        self.AddBackgroundSprite(ModStatSprite)
        self.StatSprites.append(ModStatSprite)
        
    def PlayEquipMusic(self):
        ##Resources.PlayBGMSong("Commander.xm")
        pass # Equip screen visits are too short to be worth it
    def DrawBackground(self):
        TileNumber = Resources.Tiles.get("Equip", 1)
        Image = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber))
        Surface = GetTiledImage(800, 600, Image)
        self.DeepSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(self.DeepSprite)
        
        ####
        Border = LineSprite(0, self.UpperPanelHeight, self.PerksX - 2, self.UpperPanelHeight, Colors.LightGrey)
        self.AddBackgroundSprite(Border)
        #Border = LineSprite(self.PerksX - 2, self.UpperPanelHeight, self.PerksX - 2, 600, Colors.LightGrey)
        #self.AddBackgroundSprite(Border)
        Border = LineSprite(self.ItemX - 2, 0, self.ItemX - 2, self.UpperPanelHeight, Colors.LightGrey)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(self.StatsX - 2, 0, self.StatsX - 2, self.UpperPanelHeight, Colors.LightGrey)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(self.PerksX - 2, 0, self.PerksX - 2, 600, Colors.LightGrey)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(self.PerksX - 2, 310, 800, 310, Colors.LightGrey)
        self.AddBackgroundSprite(Border)
        # Gold:
        Image = TaggedRenderer.RenderToImage("<CN:GREY>Funds: <CN:YELLOW>z<CN:WHITE>%s"%Global.Party.Gold, FontSize = 18)
        Sprite = GenericImageSprite(Image, self.ItemListingWidth + 10, self.UpperPanelHeight - 40)
        self.AddBackgroundSprite(Sprite)
    def GetHighlightImage(self, OtherSprite):
        Width = OtherSprite.rect.width + 8
        Height = OtherSprite.rect.height + 8
        Image = pygame.Surface((Width, Height))
        Image.fill(Colors.Black)
        pygame.draw.rect(Image,Colors.White,(1, 1, Width-1, Height-1),1)
        pygame.draw.rect(Image,Colors.White,(3, 3, Width-5, Height-5),1)
        return Image
    def DrawButtons(self):
        for ButtonSprite in self.ButtonSprites.sprites():
            ButtonSprite.kill()
        if self.HighlightSprite:
            self.HighlightSprite.kill()
        self.HighlightSprite = None
        ##
        X = self.ItemListingWidth + 10
        Y = self.UpperPanelHeight - 10
        #ButtonSprite = GenericImageSprite(FancyAssBoxedText("Key Items", FontSize = 18),X, Y)
        ButtonSprite = FancyAssBoxedSprite("Special Items", X, Y, HighlightIndex = 0)
        ButtonSprite.Slot = None
        #ButtonSprite.Text = "Key Items"
        self.ButtonSprites.add(ButtonSprite)
        self.AddBackgroundSprite(ButtonSprite)
        Y += 35
        ButtonSprite = FancyAssBoxedSprite("Optimize!", X, Y, HighlightIndex = 0)
        ButtonSprite.Slot = None
        #ButtonSprite = GenericImageSprite(FancyAssBoxedText("Optimize!", FontSize = 18),X, Y)
        #ButtonSprite.Text = "Optimize!"
        self.ButtonSprites.add(ButtonSprite)
        self.AddBackgroundSprite(ButtonSprite)
        Y += 45
        SlotX = [X, X+80, X, X+80, X, X+80, X]
        SlotY = [Y, Y, Y+30, Y+30, Y+60, Y+60, Y+90]

        Slots = list(EquipSlots.Slots)
        Slots.append("Supplies")
        SlotNames = list(EquipSlots.SlotNames)
        SlotNames.append("Supplies")
        
        for Index in range(len(Slots)):
            Slot = Slots[Index]
            SlotName = SlotNames[Index]
            #ButtonSprite = GenericTextSprite(EquipSlots.SlotNames[Slot], SlotX[Slot], SlotY[Slot], FontSize = 18)
            if self.FilterSlot == Slot:
                DrawBox = 1
            else:
                DrawBox = 0
            if SlotName == "Supplies":
                HI = 1
            else:
                HI = 0
            ButtonSprite = FancyAssBoxedSprite(SlotName,  SlotX[Index],  SlotY[Index],
                                               DrawBox = DrawBox, HighlightIndex = HI)
            ButtonSprite.Slot = Slot
            self.ButtonSprites.add(ButtonSprite)
            self.AddBackgroundSprite(ButtonSprite)
        Y += 115
        ButtonSprite = FancyAssBoxedSprite("Done", 740, Y, HighlightIndex = 0)
        #ButtonSprite = GenericTextSprite("Done", X, Y, FontSize = 18)
        ButtonSprite.Slot = None
        self.ButtonSprites.add(ButtonSprite)
        self.AddBackgroundSprite(ButtonSprite)
        # Player select button:
        Image = Resources.GetImage(os.path.join(Paths.Images,"ArrowLeft.png"))
        self.PrevPlayerButton = GenericImageSprite(Image, 20, 300)
        self.AddBackgroundSprite(self.PrevPlayerButton)
        self.ButtonSprites.add(self.PrevPlayerButton)
        Image = Resources.GetImage(os.path.join(Paths.Images,"ArrowRight.png"))
        self.NextPlayerButton = GenericImageSprite(Image, 70, 300)
        self.AddBackgroundSprite(self.NextPlayerButton)
        self.ButtonSprites.add(self.NextPlayerButton)
        
    def DrawEquip(self):
        for EquipSprite in self.EquipSprites.values():
            EquipSprite.kill()
        self.EquipSprites = {}
        # And, draw player equipment:
        for Slot in EquipSlots.Slots:
            Item = self.Player.GetEquip(Slot)
            EquipSprite = ItemPanel.ItemSpriteClass(self.SlotX[Slot], self.SlotY[Slot],
                                                    Item, 0, ItemPanel.Contexts.Equipped, self.Player, Slot)
            self.EquipSprites[Slot] = EquipSprite
            self.AddForegroundSprite(EquipSprite)
    def DrawPlayer(self):
        for Sprite in self.PlayerSprites:
            Sprite.kill()
        self.MouseOverEquipSprite = None
        self.PlayerSprites = []
        self.PlayerSprite = BattleSprites.CritterSpriteClass(self, self.Player, self.PlayerSpriteX, self.PlayerSpriteY)
        if self.Player.IsDead():
            self.PlayerSprite.PlayDead()
        self.AddForegroundSprite(self.PlayerSprite)
        self.PlayerSprites.append(self.PlayerSprite)
        # Name, level, class
        Y = self.PlayerSpriteY + 100
        Index = Global.Party.Players.index(self.Player)
        Label = PlayerIndexToPlayerLabel[Index]
        TextSprite = GenericTextSprite(PlayerLabelNames[Label], 10, Y)
        TextSprite.rect.left = 50 - TextSprite.rect.width / 2
        self.AddBackgroundSprite(TextSprite)
        self.PlayerSprites.append(TextSprite)        
        Y += 20
        TextSprite = GenericTextSprite(self.Player.Name, 10, Y)
        TextSprite.rect.left = 50 - TextSprite.rect.width / 2
        self.AddBackgroundSprite(TextSprite)
        self.PlayerSprites.append(TextSprite)
        Y += 20
        TextSprite = GenericTextSprite("Level %d"%self.Player.Level, 10, Y)
        TextSprite.rect.left = 50 - TextSprite.rect.width / 2
        self.AddBackgroundSprite(TextSprite)
        self.PlayerSprites.append(TextSprite)
        Y += 20
        TextSprite = GenericTextSprite("%s"%self.Player.Species.Name, 10, Y)
        TextSprite.rect.left = 50 - TextSprite.rect.width / 2
        self.AddBackgroundSprite(TextSprite)
        self.PlayerSprites.append(TextSprite)
        # Equipment
        self.DrawEquip()
    def HandleLoop(self):
        self.AnimationCycle+=1
        if (self.AnimationCycle>MaxAnimationCycle):
            self.AnimationCycle=0
        self.AnimationSprites.clear(self.Surface,self.BackgroundSurface) ###
        self.ForegroundSprites.clear(self.Surface,self.BackgroundSurface) ###
        self.HandleEvents() # pygame events
        for Sprite in self.AllSprites.sprites():
            Sprite.Update(self.AnimationCycle)
        for Pane in self.SubPanes:            
            Pane.HandleLoop()
        self.Update()
        self.HandleItemHighlight()
        DirtyRects = self.ForegroundSprites.draw(self.Surface) ###
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) ###
        Dirty(DirtyRects)
    def HandleItemHighlight(self):
        Sprite = self.ItemPanel.MouseOverItemSprite
        if Sprite:
            Item = Sprite.Item
        else:
            Item = None
        if Item != self.MouseOverItem:
            self.MouseOverItem = Item
            self.DrawStats(self.MouseOverItem)
    def AdvancePlayer(self, Dir):
        PlayerIndex = Global.Party.Players.index(self.Player)
        Label = PlayerIndexToPlayerLabel[PlayerIndex]
        NextLabel = Label + Dir
        if NextLabel<1:
            NextLabel = 4
        if NextLabel>4:
            NextLabel = 1
        OtherPlayer = Global.Party.Players[PlayerLabelToPlayerIndex[NextLabel]]
        self.Player = OtherPlayer
        self.ItemPanel.Player = OtherPlayer
        self.DrawPlayer()
        self.DrawStats()
        self.MouseOverItem = None
        self.ItemPanel.Redraw()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for equipment taking-off:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite and (Sprite in self.EquipSprites.values()):
            self.Player.Remove(Sprite.Item)
            self.MouseOverItem = None
            self.MouseOverEquipSprite = None
            if self.TooltipSprite:
                self.TooltipSprite.kill()
                self.TooltipSprite = None
            self.DrawEquip()
            self.DrawStats()
            self.ItemPanel.Redraw()
            Resources.PlayStandardSound("CursorMove.wav")
            return
        # Now, look for button clicks:        
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        if Sprite == self.NextPlayerButton:
            self.AdvancePlayer(1)
            return
        if Sprite == self.PrevPlayerButton:
            self.AdvancePlayer(-1)
            return
        if Sprite.Text == "Special Items":
            Global.App.DoSpecialItems()
            return
        if Sprite.Text == "Optimize!":
            Resources.PlayStandardSound("Bleep7.wav")
            self.OptimizePlayerEquipment()
            return
        if Sprite.Slot == None:
            # Done button
            self.App.PopScreen(self)
            return
        if self.FilterSlot == Sprite.Slot:
            self.FilterSlot = None
            self.ItemPanel.FilterSlots = list(EquipSlots.Slots)
            self.ItemPanel.FilterSlots.append(None)
        else:
            self.FilterSlot = Sprite.Slot
            if self.FilterSlot == "Supplies":
                self.ItemPanel.FilterSlots = [None]
            else:
                self.ItemPanel.FilterSlots = [self.FilterSlot]
        self.ItemPanel.ScrollRow = 0
        self.DrawButtons()
        self.Redraw()
    def OptimizePlayerEquipment(self):
        # Choose "best" equipment for the player.  ("Best" is a judgment call, so
        # this algorithm isn't intended to be perfect!)
        self.Player.OptimizeEquipment()
        self.DrawPlayer()
        self.DrawStats()
        self.MouseOverItem = None
        self.ItemPanel.Redraw()
    def HandleKeyPressed(self, Key):
        if Key == pygame.K_ESCAPE or Key == 100: # D for done
            self.App.PopScreen(self)
            return
        if Key == 111: #O for Optimize
            Resources.PlayStandardSound("Bleep7.wav")
            self.OptimizePlayerEquipment()
            if self.TooltipSprite:
                self.TooltipSprite.kill()
                self.TooltipSprite = None
            return
        if Key == ord("s"): #S for Special Items
            #self.ShowKeyItems()
            Global.App.DoSpecialItems()
            return
        if Key in (49,50,51,52):
            Label = Key - 48
            OtherPlayer = Global.Party.Players[PlayerLabelToPlayerIndex[Label]]
            if self.TooltipSprite and self.Player != OtherPlayer:
                self.TooltipSprite.kill()
                self.TooltipSprite = None
            self.Player = OtherPlayer
            self.ItemPanel.Player = OtherPlayer
            #self.DrawEquip()
            self.DrawPlayer()
            self.DrawStats()
            self.MouseOverItem = None
            self.MouseOverEquipSprite = None
            self.ItemPanel.MouseOverItemSprite = None
            self.ItemPanel.FindMouseOverSprites(self.ItemPanel.MousePosition)
            self.FindMouseOverSprites(self.MousePosition)
            self.ItemPanel.Redraw()
            return
        if Key in (281, 259): # pgDown - scroll
            self.ItemPanel.ScrollList(1)
        if Key in (280, 265): # pgUp - scroll
            self.ItemPanel.ScrollList(-1)
        Slot = self.KeysToFilterSlots.get(Key, None)
        
        if Slot!=None:
            if self.FilterSlot == Slot:
                self.FilterSlot = None
                self.ItemPanel.FilterSlots = list(EquipSlots.Slots)
                self.ItemPanel.FilterSlots.append(None)
            else:
                self.FilterSlot = Slot
                if Slot=="Supplies":
                    self.ItemPanel.FilterSlots = [None]
                else:
                    self.ItemPanel.FilterSlots = [self.FilterSlot]
            self.ItemPanel.ScrollRow = 0
            self.DrawButtons()
            self.Redraw()
