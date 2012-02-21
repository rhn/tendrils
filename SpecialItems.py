"""
Handle the use of SPECIAL ITEMS.  These are key items (denoted in the KeyItemFlags
dictionary on the Party object) which can be used - for instance, the Shovel can
be used to (try to) dig up the pirate treasure, the knight's maze map can be
called up at any time, et cetera.  In general, we want to get rid of key items after
they're no longer useful; we don't want the party to end up with loads of red herrings.
"""
from Utils import *
from Constants import *
import Screen
import MessagePanel
import Global
import string
import NewDialogScreen
import ChestScreen
import Instructions

UsableItems = {"Shovel":1,
               "STR seed":1,
               "DEX seed":1,
               "CON seed":1,
               "INT seed":1,
               "WIS seed":1,
               "CHA seed":1,
               "Knight Map":1,
               "Magic Map":1,
               "Red Puzzle Box":1, # Found on L1
               "Green Puzzle Box":1, # Found on L6
               "Blue Puzzle Box":1, # Found on L10
               "Letter":1,
               "Tendril 1":1,
               "Tendril 2":1,
               "Tendril 3":1,
               "Tendril 4":1,
               "Tendril 5":1,
               "Tendril 6":1,
               "Tendril 7":1,
               "Tendril 8":1,
               "Tendril 9":1,
               "Tendril 10":1,
               }

StatSeeds = {"STR seed":"STR",
             "DEX seed":"DEX",
             "CON seed":"CON",
             "INT seed":"INT",
             "WIS seed":"WIS",
             "CHA seed":"CHA",
             }

def GetUsableItemList():
    Sorting = []
    for Key in Global.Party.KeyItemFlags.keys():
        if Global.Party.KeyItemFlags[Key]:
            #List.append(Key)
            if UsableItems.has_key(Key):
                Sorting.append((Key, 1))
                #Flags.append(1)
            else:
                #Flags.append(0)
                Sorting.append((Key, 0))
    Sorting.sort()
    List = []
    Flags = []

    for (Key, Flag) in Sorting:
        List.append(Key)
        Flags.append(Flag)
    return (List, Flags)

def GetItemScreen():
    (NameList, Flags) = GetUsableItemList()
    if not NameList:
        Str = "You don't have any special items right now."
        return NewDialogScreen.DialogScreen(Global.App, Str)
    return ItemDialog(NameList, Flags)

class ItemDialog(Screen.TendrilsScreen):
    ItemHeight = 25
    ScrollArrowX = 520
    def __init__(self, List, Flags):
        Screen.TendrilsScreen.__init__(self,Global.App)
        self.Width = 300
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.BackgroundSurface.blit(self.App.BackgroundSurface,(0,0))
        self.BackgroundSurface.blit(self.App.Surface,(0,0))
        self.ItemList = List
        self.ItemSpriteList = []
        self.ScrollRow = 0
        self.UsableFlags = Flags
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))                        
        self.UpArrowSprite = None
        self.DownArrowSprite = None        
        self.Render()
    def Render(self):
        self.Height = 125
        self.RowsAtOnce = 0
        for Item in self.ItemList:
            self.RowsAtOnce += 1
            if (self.Height > 450): #580):
                break
            self.Height += self.ItemHeight
        print "Rows at once: %s of %s"%(self.RowsAtOnce, len(self.ItemList))
        self.DialogY = 300 - (self.Height / 2)
        Image = pygame.Surface((self.Width, self.Height))
        self.MasterSprite = GenericImageSprite(Image, 400 - (self.Width / 2), 300 - (self.Height / 2), 0)
        self.AddBackgroundSprite(self.MasterSprite)
        # Draw the colorful boxy thingy:
        self.MasterSprite.image.fill(Colors.Green)
        pygame.draw.rect(self.MasterSprite.image, Colors.White, (4, 4, self.Width - 8, self.Height - 8), 1)
        pygame.draw.rect(self.MasterSprite.image, Colors.Black, (10, 10, self.Width - 20, self.Height - 20), 0)
        # Add all the text images:
        self.ButtonSprites = pygame.sprite.Group()
        Y = self.DialogY + 10
        ###
        Sprite = GenericTextSprite("Use which key item?", 400, Y)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddForegroundSprite(Sprite)
        Y += Sprite.rect.height + 5
        ##
        Sprite = GenericTextSprite("(Usable item-names are green)", 400, Y)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddForegroundSprite(Sprite)
        Y += Sprite.rect.height + 5
        self.ItemTopY = Y
        ##
        for Index in range(len(self.ItemList)):
            String = self.ItemList[Index]
            Flag = self.UsableFlags[Index]
            if Flag:
                Sprite = GenericTextSprite(String, 400, 0, Colors.Green, FontSize = 24)
            else:
                Sprite = GenericTextSprite(String, 400, 0, Colors.Grey, FontSize = 24)
            Sprite.Text = String
            Sprite.rect.left -= Sprite.rect.width / 2
            self.ItemSpriteList.append(Sprite)
            if Index < self.RowsAtOnce:
                self.AddForegroundSprite(Sprite)
            if Flag:
                print "Usable:", String
                self.ButtonSprites.add(Sprite)
            ##Y += Sprite.rect.height + 5
        Sprite = GenericTextSprite("(Cancel)", 400, self.DialogY + self.Height - 35, Colors.Red)
        Sprite.Text = ""
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        self.ScrollList(-1)
    def ScrollList(self, Direction):
        self.ScrollRow += Direction*5
        self.ScrollRow = min(self.ScrollRow, len(self.ItemList) - self.RowsAtOnce)
        self.ScrollRow = max(0, self.ScrollRow)
        Y = self.ItemTopY
        for Index in range(len(self.ItemSpriteList)):
            Sprite = self.ItemSpriteList[Index]
            if Index < self.ScrollRow or Index >= self.ScrollRow + self.RowsAtOnce:
                Sprite.rect.top = -50
                try:
                    self.ForegroundSprites.remove(Sprite)
                except:
                    traceback.print_exc()
                    pass #%%
            else:
                self.AddForegroundSprite(Sprite)
                ##self.ButtonSprites.add(Sprite)
                Sprite.rect.top = Y
                Y += self.ItemHeight #Sprite.rect.height
        # UP arrow:
        if self.ScrollRow:
            if not self.UpArrowSprite:
                self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.DialogY + 20)
                self.AddForegroundSprite(self.UpArrowSprite)
                self.ButtonSprites.add(self.UpArrowSprite)
                self.UpArrowSprite.Text = "Up"
        else:
            if self.UpArrowSprite:
                self.UpArrowSprite.kill()
                self.UpArrowSprite = None
        if self.ScrollRow < len(self.ItemList) - self.RowsAtOnce:
            if not self.DownArrowSprite:
                self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DialogY + self.Height - 40)
                self.AddForegroundSprite(self.DownArrowSprite)
                self.ButtonSprites.add(self.DownArrowSprite)
                self.DownArrowSprite.Text = "Down"
        else:
            if self.DownArrowSprite:
                self.DownArrowSprite.kill()
                self.DownArrowSprite = None
            
    def RedrawBackground(self):
        self.BackgroundSprites.draw(self.BackgroundSurface)
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return        
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            print Sprite, Sprite.Text
            if Sprite.Text == "Up":
                self.ScrollList(-1)
                return
            if Sprite.Text == "Down":
                self.ScrollList(1)
                return
            Global.App.PopScreen(self)
            if Sprite.Text:
                UseKeyItem(Sprite.Text)
    def HandleKeyPressed(self, Key):
        if Key is pygame.K_ESCAPE:
            Global.App.PopScreen(self)
        if Key in (281, 259): # pgDown - scroll
            self.ScrollList(1)
        if Key in (280, 265): # pgUp - scroll
            self.ScrollList(-1)

def UseLetter():
    Str = """You examine the letter:\n\n<CN:BRIGHTBLUE>Hey!  Old Woman!


Help these nice kids out, or I'll tell everyone about how you and
you-know-who did you-know-what, you-know-when.

Your Pal,
  Old Man</C>

(Hmm...sounds almost like blackmail.  And why don't these old people have names?)

You fold the letter back up and carry onward."""
    Global.App.ShowNewDialog(Str)

def UseTendril(Index):
    Str = Instructions.TendrilsText[Index]
    if Index == 3:
        Global.App.ShowNewDialog(Str, Width = 750)
    elif Index == 8:
        Global.App.ShowNewDialog(Str, Width = 600)
    else:
        Global.App.ShowNewDialog(Str)

def UseKeyItem(Name):
    "Triage function - call the correct item-usage function"
    if Name == "Shovel":
        UseShovel()
    elif Name == "Red Puzzle Box":
        UsePuzzleBox("Red Puzzle Box", "Hughes")
    elif Name == "Green Puzzle Box":
        UsePuzzleBox("Green Puzzle Box", "Traffic Cop")
    elif Name == "Blue Puzzle Box":
        UsePuzzleBox("Blue Puzzle Box", "Blockado")
    elif Name in StatSeeds.keys():
        UseStatSeed(Name)
    elif Name == "Knight Map":
        UseKnightMap()
    elif Name == "Magic Map":
        UseSokobanMap()
    elif Name == "Letter":
        UseLetter()
    else:
        for Index in range(1, 11):
            if Name == "Tendril %d"%Index:
                UseTendril(Index)
                return
        else:
            Global.App.ShowNewDialog("Nothing happens.")
            print "** Unknown key item '%s'"%Name

def UsePuzzleBox(ItemName, PuzzleName):
    Callback = lambda Name=ItemName: GetPuzzleBoxTreasure(Name)
    Global.App.ShowBlockScreen(PuzzleName, Callback = Callback)

def GetPuzzleBoxTreasure(Name):
    # The box is gone now:
    try:
        del Global.Party.KeyItemFlags[Name]
    except:
        pass
    Str = "<CN:BRIGHTGREEN><CENTER>Aha!</C></CENTER>\n\nThe box tumbles open, and you collect the treasure within.\n"
    UnlockedFlag = Global.MemoryCard.Get("MiniGameSlidingBlock")
    if not UnlockedFlag:
        Str += "\n(You have unlocked the <CN:ORANGE>Sliding Block</C> mini-game!)\n\n"
        Global.MemoryCard.Set("MiniGameSlidingBlock")
    if Name == "Red Puzzle Box":
        Items = {"Ring of Haste": 1}
        Special = {"gold": 1000}
    elif Name == "Green Puzzle Box":
        Items = {}
        Special = {"STR seed":1,"DEX seed":1,"CON seed":1,
                   "INT seed":1, "WIS seed":1,"CHA seed":1,}
    elif Name == "Blue Puzzle Box":
        Items = {"Infinity Loop":1, "Elixir":3}
        Special = {"gold": 100000}
    ChestScreen.GetTreasureChestStuff(Items, Special, 2, Str)

def UseSokobanMap():
    if Global.Maze.Level != 5:
        Str = "The map is currently nothing but a confused swirl of colors.  Perhaps it's out of range of its territory..."
        Global.App.ShowNewDialog(Str)
        return
    Image = pygame.Surface((17*18 + 5, 9*18 + 5))
    Image.fill(Colors.Black)
    for X in range(3, 20):
        for Y in range(21, 30):
            # Circle for rock, X for floor:
            Top = (29 - Y) * 18 + 1
            Left = (X-3) * 18 + 1
            CenterX = Left + 9
            CenterY = Top + 9
            Right = Left + 18
            Bottom = Top + 18
            # Walls:
            WestWall = Global.Maze.Walls[2][(X,Y)]
            if WestWall:
                pygame.draw.line(Image, Colors.White, (Left, Top), (Left, Bottom))
            EastWall = Global.Maze.Walls[3][(X,Y)]
            if EastWall:
                pygame.draw.line(Image, Colors.White, (Right, Top), (Right, Bottom))
            NorthWall = Global.Maze.Walls[0][(X,Y)]
            if NorthWall:
                pygame.draw.line(Image, Colors.White, (Left, Top), (Right, Top))
            SouthWall = Global.Maze.Walls[1][(X,Y)]
            if SouthWall:
                pygame.draw.line(Image, Colors.White, (Left, Bottom), (Right, Bottom))
            Contents = Global.Maze.Rooms[(X,Y)]
            if Contents in (307, 306):
                pygame.draw.line(Image, Colors.Blue, (Left, Top), (Right, Bottom))
                pygame.draw.line(Image, Colors.Blue, (Right, Top), (Left, Bottom))
            if Contents in (308, 306):
                pygame.draw.circle(Image, Colors.Green, (CenterX, CenterY), 5, 2)
    Screen = NewDialogScreen.ImageDialogScreen(Image)
    Global.App.PushNewScreen(Screen)
    
def UseKnightMap():
    Str = "<CENTER><CN:BRIGHTRED>FIRE KNIGHT POSITIONS\n<IMG:KnightMap.png>"
    Global.App.ShowNewDialog(Str)
    
def UseStatSeed(Name):
    Callback = lambda P,N=Name: UseStatSeedCallback(N, P)
    Global.App.ShowNewDialog("Who will eat the <CN:RED>%s</C>?"%Name, ButtonGroup.PickPlayer, Callback = Callback)

def UseStatSeedCallback(Name, Player):
    if not Player:
        return
    StatAttName = StatSeeds[Name]
    OldStat = Player.GetNakedStat(StatAttName)
    if OldStat < MaxStat:
        Global.Party.KeyItemFlags[Name] -= 1
        if Global.Party.KeyItemFlags[Name]<=0:
            del Global.Party.KeyItemFlags[Name]        
        setattr(Player, StatAttName, getattr(Player, StatAttName) + 1)
        Global.App.ShowNewDialog("<CN:GREEN>%s</C> has gained a point of <CN:BLUE>%s</C>!"%(Player.Name, StatAttName))
    else:
        Global.App.ShowNewDialog("%s can not increase %s any further.\n<CN:GREY>(Item not used)</c>"%(Player.Name, StatAttName))
        
                                 
def UseShovel():
    # If it's not the right level:
    if Global.Maze.Level != 5:
        Global.App.ShowNewDialog("The ground here is not suitable for digging.")
        return
    Contents = Global.Maze.Rooms[(Global.Party.X, Global.Party.Y)]
    if Contents == 302:
        Global.App.ShowNewDialog("Grave-robbing ill becomes bold adventurers like you.")
        return
    if Contents != 303:
        Global.App.ShowNewDialog("You dig a bit, but find nothing.")
        return
    if Global.Party.EventFlags.get("L5BuriedTreasure", 0):
        # (shouldn't happen, since shovel disappears)
        Global.App.ShowNewDialog("You dig a bit, but find nothing.")
        return
    import ChestScreen
    Str = "You dig for a while, and hear a <CN:BRIGHTBLUE>KLANG!</C> as the shovel strikes something - a metal box!  You excavate and loot it.\n\n(The shovel has been blunted by all this digging, so you discard it)\n\n"
    ChestItems = {"Magic Shield":1, "Tiara":2, "Ninja Tabi":1}
    ChestSpecial = {"gold": 1000}
    ChestScreen.GetTreasureChestStuff(ChestItems, ChestSpecial, 2, Str)
    del Global.Party.KeyItemFlags["Shovel"]
    Global.Party.EventFlags["L5BuriedTreasure"]=1
    Resources.PlayStandardSound("MegaHappy.wav")

        