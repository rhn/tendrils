"""
The shopkeeper screen!
There's an upper itempanel for the shop inventory, and a lower itempanel for your inventory.
You can click on things in the top panel to buy them, in the bottom panel to sell them.
There are filter buttons to restrict the displayed items.
"""
from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import Instructions

AllSlots = list(EquipSlots.Slots)
AllSlots.append(None)

class ShopScreen(Screen.TendrilsScreen):
    StorePanelY = 80
    PartyPanelY = 330
    ItemPanelX = 10
    ItemListingWidth = 560
    ItemListingHeight = 195
    def __init__(self, App, ShopInventory, ShopName = "Welcome to my store.", ShopImageName = None):
        Screen.TendrilsScreen.__init__(self,App)
        Global.ShopScreen = self # Welcome to Hack City, population 0x29F
        self.ShopInventory = {}
        for Name in ShopInventory.keys():
            self.ShopInventory[Name.lower()] = None
        self.ShopName = ShopName
        # Get extra pawned items:
        PawnedStuff = Global.Party.PawnedStuff.get(ShopName, None)
        if PawnedStuff!=None:
            for Key in PawnedStuff.keys():
                if not self.ShopInventory.has_key(Key):
                    self.ShopInventory[Key] = PawnedStuff[Key]
        self.ShopName = ShopName
        self.KeyToSlot = {ord("w"): EquipSlots.Weapon,
                          ord("b"): EquipSlots.Body,
                          ord("h"): EquipSlots.Head,
                          ord("a"): EquipSlots.Arms,
                          ord("f"): EquipSlots.Feet,
                          ord("r"): EquipSlots.Relic,
                          ord("s"): "Supplies"
                          }
        if not ShopImageName:
            ShopImageName = "Shop"
        self.ShopImageName = ShopImageName
        self.MouseOverItemSprite = None
        self.TooltipSprite = None
        self.RenderInitialScreen()
        self.PlayShopMusic()
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        ShowedInnHelp = Global.MemoryCard.Get("Tutorial:Shop")
        if not ShowedInnHelp:
            Global.App.ShowNewDialog(Instructions.ShopInstructions)
            Global.MemoryCard.Set("Tutorial:Shop", 1)
        
    def PlayShopMusic(self):
        self.SummonSong("shopping")
        #Resources.PlayBGMSong("GoGetIt.xm")
    def DrawButtons(self):
        for ButtonSprite in self.ButtonSprites.sprites():
            ButtonSprite.kill()
        if self.HighlightSprite:
            self.HighlightSprite.kill()
        self.HighlightSprite = None
        #X = 750
        #Y = 350
        
        Slots = list(EquipSlots.Slots)
        Slots.append("Supplies")
        SlotNames = list(EquipSlots.SlotNames)[:]
        SlotNames.append("Supplies")
        Y = 380
        X = 610
        for Index in range(len(Slots)):
            if self.FilterSlot == Slots[Index]:
                DrawBox = 1
            else:
                DrawBox = 0
            ButtonSprite = FancyAssBoxedSprite(SlotNames[Index], X, Y, HighlightIndex = 0, DrawBox = DrawBox)
            #ButtonSprite = GenericTextSprite(SlotNames[Index], X, Y, FontSize = 18, CenterFlag = 1)
            ButtonSprite.Slot = Slots[Index]
            self.ButtonSprites.add(ButtonSprite)
            self.AddBackgroundSprite(ButtonSprite)
            if (X==610):
                X = 710
            else:
                Y += 35
                X = 610
        ButtonSprite = FancyAssBoxedSprite("Done", 680, 550, HighlightIndex = 0, BackColor = (11,11,11)) #GenericTextSprite("Done", X, self.Height - 30, FontSize = 18, CenterFlag = 1)
        ButtonSprite.Slot = None
        self.ButtonSprites.add(ButtonSprite)
        self.AddBackgroundSprite(ButtonSprite)        
    def GetHighlightImage(self, OtherSprite):
        Width = OtherSprite.rect.width + 8
        Height = OtherSprite.rect.height + 8
        Image = pygame.Surface((Width, Height))
        Image.fill(Colors.Black)
        pygame.draw.rect(Image,Colors.White,(1, 1, Width-1, Height-1),1)
        pygame.draw.rect(Image,Colors.White,(3, 3, Width-5, Height-5),1)
        return Image
    def DrawPlayerInfo(self):
        for Sprite in self.PlayerInfoSprites.sprites():
            Sprite.kill()
        Sprite = GenericTextSprite("Party Gold:", 600, 300)
        self.AddBackgroundSprite(Sprite)
        self.PlayerInfoSprites.add(Sprite)
        X = Sprite.rect.right + 20
        Sprite = GenericTextSprite(Global.Party.Gold, X, 300, Colors.Yellow, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        self.PlayerInfoSprites.add(Sprite)
    def RenderInitialScreen(self):
        self.DrawBackground()
        ##
        self.PlayerInfoSprites = pygame.sprite.Group()
        self.DrawPlayerInfo()
        ##
        self.ButtonSprites = pygame.sprite.Group()
        self.HighlightSprite = None
        self.FilterSlot = None
        self.DrawButtons()
        ##
        self.ShopPanel = ItemPanel.ItemPanel(self, self.ItemPanelX, self.StorePanelY, self.ItemListingWidth,
                                             self.ItemListingHeight, self.ShopInventory,
                                             self.ShopItemClicked, ItemPanel.Contexts.ShopInventory)
        self.SubPanes.append(self.ShopPanel)
        self.PartyPanel = ItemPanel.ItemPanel(self, self.ItemPanelX, self.PartyPanelY, self.ItemListingWidth,
                                             self.ItemListingHeight, Global.Party.GetItems(),
                                             self.PartyItemClicked, ItemPanel.Contexts.ShopOwned)
        self.SubPanes.append(self.PartyPanel)
    def ShopItemClicked(self, ItemSprite):
        Cost = Global.Party.GetBuyCost(ItemSprite.Item.Cost)
        if Cost > Global.Party.Gold:
            Resources.PlayStandardSound("Error.wav")
            return
        LowerName = ItemSprite.Item.Name.lower()
        Count = Global.Party.Items.get(LowerName, 0)
        if Count >= 99:
            Resources.PlayStandardSound("Full.wav")
            return
        Resources.PlayStandardSound("Shop.wav")
        Global.Party.Gold -= Cost
        Global.Party.GetItem(ItemSprite.Item.Name)
        if self.ShopInventory[LowerName]!=None:
            self.ShopInventory[LowerName] -= 1
            if self.ShopInventory[LowerName] <= 0:
                del self.ShopInventory[LowerName]
        self.DrawPlayerInfo()
        self.ShopPanel.Redraw()
        self.PartyPanel.Redraw()
        if self.TooltipSprite:
            self.TooltipSprite.kill()
            self.TooltipSprite = None
       
        self.Redraw()
    def PartyItemClicked(self, ItemSprite):
        Cost = Global.Party.GetSellCost(ItemSprite.Item.Cost)
        Global.Party.Gold += Cost / 2
        Global.Party.DropItem(ItemSprite.Item.Name)
        Resources.PlayStandardSound("Shop.wav")
        self.DrawPlayerInfo()
        LowerName = ItemSprite.Item.Name.lower()
        if not self.ShopInventory.has_key(LowerName):
            self.ShopInventory[LowerName] = 1
        else:
            if self.ShopInventory[LowerName] != None:
                self.ShopInventory[LowerName] += 1
        if self.TooltipSprite:
            self.TooltipSprite.kill()
            self.TooltipSprite = None
        self.ShopPanel.Redraw()
        self.PartyPanel.Redraw()
        self.Redraw()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        if Sprite.Slot == None:
            # Done button
            Global.ShopScreen = None
            self.RememberPawnedStuff()
            self.App.PopScreen(self)
            return
        if self.FilterSlot == Sprite.Slot:
            self.FilterSlot = None
            self.ShopPanel.FilterSlots = AllSlots
            self.PartyPanel.FilterSlots = AllSlots
        else:
            self.FilterSlot = Sprite.Slot
            TheSlot = self.FilterSlot
            if (self.FilterSlot == "Supplies"):
                TheSlot = None
            self.ShopPanel.FilterSlots = [TheSlot]
            self.PartyPanel.FilterSlots = [TheSlot]
        self.ShopPanel.ScrollRow = 0
        self.PartyPanel.ScrollRow = 0
        self.DrawButtons()
        self.Redraw()
    def GetPanelWrapImage(self, Color, Text):
        "Get wrapping image for shop/party panel"
        Width = self.ItemListingWidth + 20
        Height = self.ItemListingHeight + 40
        Image = pygame.Surface((Width, Height))
        pygame.draw.rect(Image, Color, (0, 0, Image.get_rect().width, Image.get_rect().height), 0)
        pygame.draw.line(Image, Colors.White, (50, 15), (4, 15))
        pygame.draw.line(Image, Colors.White, (4, 15), (4, Height - 5))
        pygame.draw.line(Image, Colors.White, (4, Height - 5), (Width-5, Height-5))
        pygame.draw.line(Image, Colors.White, (Width-5, Height-5), (Width-5, 15))
        pygame.draw.line(Image, Colors.White, (Width-5, 15), (200, 15))
        Text = TextImage(Text)
        Image.blit(Text, (55, 15 - Text.get_rect().height / 2))
        return Image        
    def DrawBackground(self):
        TileNumber = Resources.Tiles.get("Shop", 1)
        Image = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber))
        Surface = GetTiledImage(800, 600, Image)
        pygame.draw.rect(Surface, Colors.Black, (590, 295, 195, 240), 0)
        pygame.draw.rect(Surface, Colors.White, (590, 295, 195, 240), 1)
        BackSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(BackSprite)
        ##
        Sprite = GenericTextSprite(self.ShopName, 25, 5, FontSize = 36, Color = Colors.Yellow)
        self.AddBackgroundSprite(Sprite)
        Image = self.GetPanelWrapImage(Colors.DarkBlue, "Shop inventory:")
        Sprite = GenericImageSprite(Image, self.ItemPanelX - 10, self.StorePanelY - 30)
        self.AddBackgroundSprite(Sprite)
        Image = self.GetPanelWrapImage(Colors.DarkGreen, "Party items:")
        Sprite = GenericImageSprite(Image, self.ItemPanelX - 10, self.PartyPanelY - 30)
        self.AddBackgroundSprite(Sprite)
        ShopImage = Resources.GetImage(os.path.join(Paths.Images, "Background", "%s.png"%self.ShopImageName))
        Sprite = GenericImageSprite(ShopImage, 685, 5) #self.ItemPanelX + self.ItemListingWidth + 21, 5)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        ##
        LabelSprite = GenericTextSprite("Filter:", 700, 360, Colors.White, FontSize = 18, CenterFlag = 1)
        self.AddBackgroundSprite(LabelSprite)        
    def HandleKeyPressed(self, Key):
        if Key == pygame.K_ESCAPE or Key == ord("d"):
            Global.ShopScreen = None
            self.RememberPawnedStuff()
            self.App.PopScreen(self)
            return
        if Key in (281, 259): # pgDown - scroll
            self.PartyPanel.ScrollList(1)
        if Key in (280, 265): # pgUp - scroll
            self.PartyPanel.ScrollList(-1)
        Slot = self.KeyToSlot.get(Key, None)
        if Slot!=None:
            if self.FilterSlot == Slot:
                self.FilterSlot = None
                self.ShopPanel.FilterSlots = AllSlots
                self.PartyPanel.FilterSlots = AllSlots
            else:
                self.FilterSlot = Slot
                TheSlot = self.FilterSlot
                if (self.FilterSlot == "Supplies"):
                    TheSlot = None
                self.ShopPanel.FilterSlots = [TheSlot]
                self.PartyPanel.FilterSlots = [TheSlot]
            self.ShopPanel.ScrollRow = 0
            self.PartyPanel.ScrollRow = 0
            self.DrawButtons()
            self.Redraw()
    def HandleMouseMoved(self, Position, Buttons):
        MouseOverItemSprite = None
        for SubPane in self.SubPanes:
            SubPosition = SubPane.GetLocalPosition(Position)
            if SubPosition:
                MouseOverItemSprite = SubPane.FindMouseOverSprites(SubPosition)
        # If we're over the same sprite as before, do nothing:
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
        # If we're over a sprite, build a tooltip:
        if self.MouseOverItemSprite:
            self.TooltipSprite = ItemPanel.BuildTooltipSprite(self.MouseOverItemSprite.Item)
            self.TooltipSprite.rect.left = Position[0] + 10
            self.TooltipSprite.rect.top = min(600 - self.TooltipSprite.rect.height, Position[1])
            
            self.AddAnimationSprite(self.TooltipSprite)
    def RememberPawnedStuff(self):
        "MUST call this before dismissing screen!"
        Global.Party.PawnedStuff[self.ShopName] = {}
        for Key in self.ShopInventory:
            Count = self.ShopInventory[Key]
            if Count!=None:
                Global.Party.PawnedStuff[self.ShopName][Key] = Count



                
