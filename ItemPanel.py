"""
ItemPanel - a scrollable list of items, used in the Equipment screen and in the
Shop screen.  
"""
from Utils import *
from Constants import *
import Screen
import Resources
import time
import Critter
import Global

class Contexts:
    # Equip: We're in the context of a PLAYER.  We show the number of items, and we indicate
    # items this player can't equip with RED FADE.
    Equip = "Equip" # Equip screen panel
    Equipped = "Equipped" # upper panel of equip screen
    ShopInventory = "ShopInventory"
    ShopOwned = "ShopOwned"

NonePic = None
GreyImage = None
def GetNonePic():
    global NonePic 
    if not NonePic:
        NonePic = TextImage("(Nothing)", Colors.LightGrey)
    return NonePic

def GetGreyImage():
    global GreyImage
    if not GreyImage:
        GreyImage = pygame.Surface((50, 50))
        GreyImage.set_alpha(100)
        ##GreyImage.set_colorkey(Colors.Black)
        GreyImage.fill(Colors.Red)
    return GreyImage    

class ItemSpriteClass(GenericImageSprite):
    Width = 100
    MidWidth = Width / 2
    Height = 90
    FontSize = 14
    def __init__(self, X, Y, Item, Count, Context, Player, Slot = None):
        self.image = pygame.Surface((100,100))
        self.Item = Item
        self.Slot = Slot
        self.Count = Count
        self.Context = Context
        self.Player = Player
        self.Redraw()
        GenericImageSprite.__init__(self, self.image, X, Y)
    def Redraw(self, Player = None):
        # Item picture:
        self.image = pygame.Surface((100,100))
        if self.Item:
            ItemPic = Resources.GetItemImage(self.Item)
        ####################################
        if self.Context == Contexts.Equipped:
            # If 'equipped': Show slot, then image, then name
            if self.Item:
                SlotPic = TextImage(EquipSlots.SlotNames[self.Item.Slot])
            else:
                SlotPic = TextImage(EquipSlots.SlotNames[self.Slot])
            self.image.blit(SlotPic, ((self.MidWidth - SlotPic.get_rect().width / 2), 0))
            if self.Item:
                self.image.blit(ItemPic, (25,20))
                NamePic = TextImage(self.Item.Name, FontSize = self.FontSize)
                self.image.blit(NamePic, ((self.MidWidth - NamePic.get_rect().width / 2), 70))
            else:
                NonePic = GetNonePic()
                self.image.blit(NonePic, ((self.MidWidth - NonePic.get_rect().width / 2),(55 - NonePic.get_rect().height / 2)))
        ####################################
        elif self.Context == Contexts.Equip:
            # If 'equip': Show image, then name+count, and possibly grey out
            self.image.blit(ItemPic, (25,0))
            if self.Count>1:
                NamePic = TextImage("%s (%s)"%(self.Item.Name, self.Count), FontSize = self.FontSize)
            else:
                NamePic = TextImage("%s"%(self.Item.Name), FontSize = self.FontSize)
            self.image.blit(NamePic, ((self.MidWidth - NamePic.get_rect().width / 2), 51))
            if not self.Player.CanEquip(self.Item):
                #print "GREYING:"
                self.image.blit(GetGreyImage(), (25,0))
        ####################################
        elif self.Context == Contexts.ShopInventory:
            # If 'shopinventory': Show image, then name (+count,maybe), then sell-price
            self.image.blit(ItemPic, (25,0))
            Count = Global.ShopScreen.ShopInventory.get(self.Item.Name.lower(), None)
            if Count!=None:
                NamePic = TextImage("%s (%s)"%(self.Item.Name, Count), FontSize = self.FontSize)
            else:
                NamePic = TextImage("%s"%(self.Item.Name), FontSize = self.FontSize)
            self.image.blit(NamePic, ((self.MidWidth - NamePic.get_rect().width / 2), 51))
            Cost = Global.Party.GetBuyCost(self.Item.Cost)
            CostPic = TextImage(Cost, FontSize = self.FontSize)
            self.image.blit(CostPic, ((self.MidWidth - CostPic.get_rect().width / 2), 71))
        ####################################
        elif self.Context == Contexts.ShopOwned:
            # If 'shopowned': Show image, then name+count, then sell-price
            self.image.blit(ItemPic, (25,0))
            if self.Count>1:
                NamePic = TextImage("%s (%s)"%(self.Item.Name, self.Count), FontSize = self.FontSize)
            else:
                NamePic = TextImage("%s"%(self.Item.Name), FontSize = self.FontSize)
            self.image.blit(NamePic, ((self.MidWidth - NamePic.get_rect().width / 2), 51))
            Cost = Global.Party.GetSellCost(self.Item.Cost)
            CostPic = TextImage(Cost, FontSize = self.FontSize)
            self.image.blit(CostPic, ((self.MidWidth - CostPic.get_rect().width / 2), 71))

class QuarterMaster:
    "Inventory isn't boring.  Inventory is LIFE!"
    BaseCosts = [10, 25, 50, 100, 250,
                 500, 1000, 2000, 3000, 4000,
                 5000, 7500, 10000, 12500, 15000,
                 20000, 30000, 40000, 50000, 75000,
                 100000, 150000, 200000, 250000, 500000,
                 10000000, 20000000, 30000000,40000000, 50000000,
                 50000000,50000000,50000000,50000000,50000000,
                 50000000,50000000,50000000,50000000,50000000,
                 50000000,50000000,50000000,50000000,50000000,
                 50000000,50000000,50000000,50000000,50000000,]
    def __init__(self):
        self.Items = {}
        self.HealingItems = []
        self.Load()
        Global.QuarterMaster = self
    def GetRandomBooty(self, Level):
        Items = {}
        ItemCount = random.choice([1,1,1,1,1,1,2,2,3])
        ItemKeys = self.Items.keys()
        for Index in range(ItemCount):
            MaxChecks = 50
            Counter = 0
            while (1):
                Counter += 1
                if Counter >= MaxChecks:
                    break
                Item = self.Items[random.choice(ItemKeys)]
                # Drop only items from the correct level that aren't unique:
                if (Level not in Item.Level) or Item.UniqueFlag:
                    continue
                Items[Item.Name] = 1
                break
        # Also, provide a healing item semi-often:
        if random.random()>0.3:
            if random.random() > 0.5:
                # A potion:
                if Level > 7:
                    Name = "x-potion"
                elif Level > 3:
                    Name = "hi-potion"
                else:
                    Name = "potion"
                #Item = self.Items[Name]
                Items[Name] = 1
            else:
                # A random healing thing:
                Counter = 0
                while (1):
                    Counter += 1
                    if Counter >= MaxChecks:
                        break
                    Item = random.choice(self.HealingItems)
                    if (Level not in Item.Level):
                        continue
                    Items[Item.Name] = 1
                    break
        return (Items, {}, 1)
    def Load(self):
        File = open("Items.txt","r")
        LineNumber = 0
        for FileLine in File.xreadlines():
            LineNumber += 1
            FileLine = FileLine.strip()
            if len(FileLine)==0 or FileLine[0]=="#":
                continue
            try:
                self.LoadItem(FileLine)
            except:
                print "** ERROR loading item!  Offending line number was %d"%LineNumber
                traceback.print_exc()
        print "TOTAL ITEMS:", len(self.Items.keys())
    def GetItemLevels(self, Item, Str):
        Str = Str.replace('"', "")
        Item.Level = []
        for Bit in Str.split(","):
            Bit = Bit.strip()
            if Bit!=None:
                Item.Level.append(int(Bit))
        
    def LoadItem(self, FileLine):
        Bits = FileLine.split("\t")
        if len(Bits)<2 or not Bits[0].strip():
            return
        while len(Bits)<21:
            Bits.append("")
        NewItem = Critter.Item()
        NewItem.Name = Bits[0]
        self.GetItemLevels(NewItem, Bits[2])
        self.Items[NewItem.Name.lower()] = NewItem        
        NewItem.Slot = self.GetInt(Bits[3], None)
        NewItem.Cost = self.GetInt(Bits[4], self.BaseCosts[NewItem.Level[0]])
        self.GetClasses(NewItem, Bits[5])
        NewItem.DamageDice = self.GetInt(Bits[6], 0)
        NewItem.DamageDie = self.GetInt(Bits[7], 0)
        # Default damage for weapons:
        if NewItem.Slot == EquipSlots.Weapon:
            if not NewItem.DamageDice:
                NewItem.DamageDice = 1
            if not NewItem.DamageDie:
                NewItem.DamageDie = 7
        else:
            if NewItem.DamageDice or NewItem.DamageDie:
                print "** WARNING: Damage attached to non-weapon is ignored!"
                print "Item:", NewItem.Name
                NewItem.DamageDice = 0
                NewItem.DamageDie = 0
        NewItem.DamgeBonus = self.GetInt(Bits[8])
        NewItem.ToHitBonus = self.GetInt(Bits[9])
        NewItem.AC = self.GetInt(Bits[10])
        NewItem.MaxHP = self.GetInt(Bits[11])
        NewItem.MaxMP = self.GetInt(Bits[12])
        NewItem.STR = self.GetInt(Bits[13])
        NewItem.DEX = self.GetInt(Bits[14])
        NewItem.CON = self.GetInt(Bits[15])
        NewItem.INT = self.GetInt(Bits[16])
        NewItem.WIS = self.GetInt(Bits[17])
        NewItem.CHA = self.GetInt(Bits[18])
        self.GetPerks(NewItem,Bits[19])
        NewItem.UniqueFlag = self.GetInt(Bits[20])
        if NewItem.UniqueFlag == 2:
            self.HealingItems.append(NewItem)
    def GetClasses(self, TheItem, Str):
        TheItem.Classes = Str.strip().upper()
    def GetPerks(self, TheItem, Str):
        Str = Str.strip()
        if not Str:
            return
        if Str[0]==Str[-1]=='"':
            Str = Str[1:-1]
        PerkBits = Str.split(",")
        for PerkBit in PerkBits:
            PerkBit = PerkBit.strip()
            if PerkBit:
                TheItem.Perks[PerkBit] = 1
    def GetInt(self, Str, Default = 0):
        ##print "Get int '%s' default %s"%(Str, Default)
        try:
            return int(Str)
        except:
            #traceback.print_exc()
            return Default
    def GetItem(self, Name):
        Item = self.Items.get(Name.lower(), None)
        if not Item:
            print "** ERROR: Unknown item '%s'"%Name
            ##traceback.print_stack()
            FakeItem = Critter.Item()
            FakeItem.Name = Name
            return FakeItem
            
        return Item
    def IntegrityCheck(self):
        for Item in self.Items.values():
            Item.Validate()
QuarterMaster()
        
class ItemPanel(Screen.TendrilsPane):
    ItemWidth = 103
    UpperItemY = 5
    LowerItemY = 105
    
    UpArrowY = 20
    DownArrowY = 165
    def __init__(self, OwningScreen, BlitX, BlitY, Width, Height, ItemList, ClickCallback = None, Context = Contexts.Equip, Player = None):
        self.Player = Player # if equipping (not shopping)
        Screen.TendrilsPane.__init__(self,OwningScreen,BlitX,BlitY,Width,Height,"StatusPanel")
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))
        self.ClickCallback = ClickCallback
        self.Screen = OwningScreen
        ##self.State = PanelStates.Status
        self.ItemList = ItemList
        self.MouseOverItemSprite = None
        self.Context = Context
        self.ScrollRow = 0
        self.MousePosition = (0,0)
        if self.Context == Contexts.Equip:
            self.ItemsPerRow = 6
            self.ScrollArrowX = 625
        else:
            self.ItemsPerRow = 5
            self.ScrollArrowX = 540
        self.FilterSlots = list(EquipSlots.Slots)
        self.FilterSlots.append(None)
        self.DrawBackground()
        self.Redraw()
    def DrawBackground(self):
        if self.Context == Contexts.Equip:
            TileNumber = Resources.Tiles.get("Equip2", 1)
            Path = os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber)
            print Path
            Image = Resources.GetImage(Path)
            Surface = GetTiledImage(800, 600, Image)
            self.DeepSprite = GenericImageSprite(Surface, 0, 0)
            self.BackgroundSprites.add(self.DeepSprite)
            
    def GetRowCount(self):
        TheCount = 0
        for ItemName  in self.ItemList.keys():
            Item = Global.QuarterMaster.GetItem(ItemName)
            if Item.Slot in self.FilterSlots:
                TheCount += 1
        return 1 + (TheCount - 1) / self.ItemsPerRow
    def DrawScrollArrows(self):
        TotalRows = self.GetRowCount()
        self.ScrollRow = max(0, min(self.ScrollRow, TotalRows - 1))
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        if self.ScrollRow > 0:
            self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.UpArrowY)
            self.AddForegroundSprite(self.UpArrowSprite)
        if self.ScrollRow < (TotalRows - 2):
            self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DownArrowY)
            self.AddForegroundSprite(self.DownArrowSprite)
            
    def Redraw(self):        
        for Sprite in self.ForegroundSprites.sprites():
            Sprite.kill()
        self.ItemSprites = []
        self.DrawScrollArrows()
        # ItemList is a dictionary whose keys are item names.
        # For party inventory, the values should be item counts
        # For shop inventory, values should be 1
        CurrentY = self.UpperItemY
        CurrentX = 3
        CurrentRow = 0
        Keys = self.ItemList.keys()
        Keys.sort()
        for ItemName in Keys:
            Count = self.ItemList[ItemName]
            Item = Global.QuarterMaster.GetItem(ItemName)
            if Item.Slot not in self.FilterSlots:
                continue
            if CurrentRow >= self.ScrollRow:
                ItemSprite = ItemSpriteClass(CurrentX, CurrentY, Item, Count, self.Context, self.Player)
                self.AddForegroundSprite(ItemSprite)
                self.ItemSprites.append(ItemSprite)
            CurrentX += self.ItemWidth
            if (CurrentX > self.Width - self.ItemWidth):
                CurrentRow += 1
                CurrentX = 3
                if CurrentRow > self.ScrollRow + 1:
                    break # No more will fit!
                if CurrentRow > self.ScrollRow:
                    CurrentY = self.LowerItemY
            
        # Sprites are now all in place.
        # ...and refresh:
        self.RedrawBackground()
        self.Surface.fill(Colors.Black)
        self.Surface.blit(self.BackgroundSurface,(0,0))
        self.ForegroundSprites.draw(self.Surface)
        self.AnimationSprites.draw(self.Surface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
    def HandleKeyPressed(self, Key):
        pass


    def FindMouseOverSprites(self,Position):
        self.MousePosition = Position
        self.MouseOverSprites.empty()
        self.MouseOverItemSprite = None
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite:
            self.MouseOverSprites.add(Sprite)
        if Sprite in self.ItemSprites:
            self.MouseOverItemSprite = Sprite
        return self.MouseOverItemSprite
    def HandleMouseClickedHere(self,Position,Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite and Sprite == self.UpArrowSprite:
            self.ScrollList(-1)
        if Sprite and Sprite == self.DownArrowSprite:
            self.ScrollList(1)
        if Sprite in self.ItemSprites:
            if self.ClickCallback:
                apply(self.ClickCallback, [Sprite])
    def ScrollList(self, Dir):
        self.ScrollRow += Dir
        self.ScrollRow = min(self.ScrollRow, self.GetRowCount() - 2)
        self.ScrollRow = max(self.ScrollRow, 0)
        self.Redraw()


def UnitTest():
    import pygame
    pygame.init()
    Surface = pygame.display.set_mode((800,600))
    print "--- Integrity check start ---"
    Global.QuarterMaster.IntegrityCheck()
    print "--- Integrity check complete ---"
    print "If there are errors, please do what you can to fix them."
    print "Let's love this tree."
    print "Total items:", len(Global.QuarterMaster.Items.values())

def BuildTooltipSprite(Item):
    if Item == None:
        return None # No tooltip for no-item
    Str = "Lvl%s"%Item.Level[0]
    if Item.UniqueFlag==1:
        Str += " (<CN:ORANGE>Unique</c>)"
    Str += "\n"
    Str += "<CN:BRIGHTGREEN>%s</C>\n"%Item.Classes
    if Item.Slot in EquipSlots.Slots:
        SlotName = EquipSlots.SlotNames[Item.Slot]
    else:
        SlotName = "Supplies"
    Str += "<CN:PURPLE>%s</C>\n"%SlotName
    if Item.AC:
        Str += "<CN:GREEN>AC%+d</C>\n"%Item.AC
    if Item.DamageDice:
        DamageStr = "<CN:BRIGHTRED>%d</c><CN:RED>D</C><CN:BRIGHTRED>%d</C>"%(Item.DamageDice, Item.DamageDie)
        if Item.DamageBonus:
            DamageStr += "<CN:WHITE>+</C><CN:BRIGHTRED>%d</C>"%Item.DamageBonus
        Str += DamageStr+"\n"
    # Stats and stuff:
    Stat = 0
    if Item.STR:
        Str += "STR%+d "%Item.STR
        Stat = 1
    if Item.DEX:
        Str += "DEX%+d "%Item.DEX
        Stat = 1
    if Item.CON:
        Str += "CON%+d "%Item.CON
        Stat = 1
    if Item.INT:
        Str += "INT%+d "%Item.INT
        Stat = 1
    if Item.WIS:
        Str += "WIS%+d "%Item.WIS
        Stat = 1
    if Item.CHA:
        Str += "CHA%+d "%Item.CHA
        Stat = 1
    if Stat:
        Str += "\n"
    for Perk in Item.Perks.keys():
        Str += "<CN:BRIGHTGREEN>%s</C> "%Perk
    Str = Str.strip()
    TextImage = TaggedRenderer.RenderToImage(Str, FontSize=16)
    TextImage.set_colorkey(Colors.Black)
    Image = pygame.Surface((TextImage.get_rect().width + 4, TextImage.get_rect().height + 4))
    
    Image.fill(Colors.AlmostBlack)
    Image.blit(TextImage, (2,2))
    pygame.draw.rect(Image, Colors.White, (0, 0, Image.get_rect().width, Image.get_rect().height), 1)
    Sprite = GenericImageSprite(Image, 0, 0)
    return Sprite


if __name__ == "__main__":
    # If run from the command-line, do unit testing / integrity checking
    UnitTest()