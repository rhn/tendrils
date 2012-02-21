"""
The Inn is an important place - you can HEAL your party,
SWAP players between the party and the roster, and
RECRUIT new characters to the roster.

Is it necessary to swap players in and out?  Yes, sometimes, for puzzles.
"""

from Utils import *
from Constants import *
import Screen
import Music
import BattleSprites
import ItemPanel
import Global
import Resources
import Critter
import Instructions
import Maze

RecruitCost = 200

class InnScreen(Screen.TendrilsScreen):
    """
    Inn screen has an upper panel and a lower panel.  The upper panel shows the four
    party players, plus a detail panel for whoever the mouse is hanging over.  The
    lower panel has a list of retinue players, plus some buttons to "sleep", "recruit",
    et cetera.
    """
    UpperPanelHeight = 380
    UpperPanelY = 55
    RosterPanelY = UpperPanelHeight + UpperPanelY
    PartySpriteX = [125, 125, 10, 240]
    PartySpriteY = [5+UpperPanelY, 190+UpperPanelY, 97+UpperPanelY, 97+UpperPanelY]
    StatPlayerX = 410
    StatPlayerY = 129
    StatsX = 500
    PerksX = 630
    ButtonX = 700
    RosterWidth = 738
    GoldY = 365
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        self.MouseOverPlayerSprite = None
        self.MouseOverPlayer = None
        self.HighlightedPlayer = None
        self.GoldSprites = []
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.RenderInitialScreen()
        self.PlayInnMusic()
    def HandleMouseMoved(self,Position,Buttons):
        for SubPane in self.SubPanes:
            SubPosition = SubPane.GetLocalPosition(Position)
            if SubPosition:
                SubPane.FindMouseOverSprites(SubPosition)
            else:
                SubPane.FindMouseOverSprites((-1,-1))
        self.FindMouseOverSprites(Position)

    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.DeepSprites.draw(self.BackgroundSurface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
        
    def FindMouseOverSprites(self,Position):
        self.MouseOverSprites.empty()
        OldSprite = self.MouseOverPlayerSprite
        if OldSprite:
            OldPlayer = OldSprite.Critter
        else:
            OldPlayer = None
        self.MouseOverPlayerSprite = None
        self.MouseOverPlayer = None
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.PartySprites)
        if Sprite:
            self.MouseOverSprites.add(Sprite)
            self.MouseOverPlayerSprite = Sprite
            self.MouseOverPlayer = Sprite.Critter
        if self.MouseOverPlayer != OldPlayer:
            #if self.MouseOverPlayerSprite:
            #    print self.MouseOverPlayerSprite.rect.left, self.MouseOverPlayerSprite.rect.top
            self.DrawStats(self.MouseOverPlayer)
    def RenderInitialScreen(self):
        self.DrawBackground()
        #####
        self.HighlightSprite = None
        self.ButtonSprites = pygame.sprite.Group()
        self.DrawButtons()
        ###
        self.StatPlayerSprite = None
        self.PlayerSprites = pygame.sprite.Group() # Party players AND roster
        self.PartySprites = pygame.sprite.Group() # Party players only
        self.PartySupportSprites = [] # Party stuff, excluding the critter sprites
        self.DrawParty()
        ####
        self.StatSprites = []
        self.DrawStats()
        ####
        self.RosterPanel = RosterPanel(self, 0, self.RosterPanelY + 1,
            self.RosterWidth, self.Height - self.RosterPanelY - 1)
        self.SubPanes.append(self.RosterPanel)        
    def DrawStats(self, Player = None):
        for Sprite in self.StatSprites:
            Sprite.kill()
        self.StatSprites = []
        if not Player:
            self.Redraw()
            return
        self.StatPlayerSprite = BattleSprites.CritterSpriteClass(self, Player, self.StatPlayerX, self.StatPlayerY)
        self.StatSprites.append(self.StatPlayerSprite)
        self.AddForegroundSprite(self.StatPlayerSprite)
        if Player.IsAlive():
            self.StatPlayerSprite.AnimateAttack()
        else:
            self.StatPlayerSprite.PlayDead()
        ShowNameLevelClass(Player, self, self.StatSprites, self.StatPlayerX, self.StatPlayerY)
        Y = self.UpperPanelY + 10
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
                          ("ToHit","ToHitBonus"),
                          ("DamageDice","DamageDice"),
                          ("DamageDie","DamageDie"),
                          ("DamageBonus","DamageBonus"),
                          ("AvgDam",None, "GetAverageDamage"),
                          ("Level", "Level"),
                          ("XP", "EXP"),
                          ("To level", None, "GetEXPToLevel"),
                          ]:
            if len(StatTuple) == 3:
                self.DrawStat(Player, Y, StatTuple[0], StatFunctionName = StatTuple[2])
            else:
                self.DrawStat(Player, Y, StatTuple[0], StatTuple[1])
            Y += 18
        # Now draw perks:
        self.DrawPerks(Player)
        self.Redraw()
    def DrawPerks(self, Player):
        Y = self.UpperPanelY + 10
        CurrentPerks = Player.GetPerks()
        if len(CurrentPerks.keys()):
            Sprite = GenericTextSprite("-- Perks --", self.PerksX, Y, Colors.LightGrey)
            self.AddBackgroundSprite(Sprite)
            self.StatSprites.append(Sprite)
            Y += 20            
        for Perk in CurrentPerks.keys():
            Sprite = GenericTextSprite(Perk, self.PerksX, Y, Colors.White)
            self.AddBackgroundSprite(Sprite)
            self.StatSprites.append(Sprite)
            Y += 20
    def DrawStat(self, Player, Y, Label, StatAttributeName = None, StatFunctionName = None):
        if StatAttributeName:
            CurrentStat = getattr(Player, StatAttributeName)
        else:
            CurrentStatFcn = getattr(Player, StatFunctionName)
            CurrentStat = apply(CurrentStatFcn)
        StatSprite = GenericTextSprite("%s: %s"%(Label, CurrentStat), self.StatsX, Y)
        self.AddBackgroundSprite(StatSprite)
        self.StatSprites.append(StatSprite)
        return
    def PlayInnMusic(self):
        Music.PlaySongByName("innkeeper")
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        Music.PlaySongByName("innkeeper")
        ShowedInnHelp = Global.MemoryCard.Get("Tutorial:Inn")
        if not ShowedInnHelp:
            Global.App.ShowNewDialog(Instructions.InnInstructions)
            Global.MemoryCard.Set("Tutorial:Inn", 1)
    def DrawBackground(self):
        Image1 = Resources.GetImage(os.path.join(Paths.ImagesBackground, "BlueKnot.png"))
        Image2 = Resources.GetImage(os.path.join(Paths.ImagesBackground, "RedKnot.png"))
        TileImage = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile5.png"))
        Surface = pygame.Surface((800, 600))
        # Upper row:
        Y = -7
        X = -5
        while (X<800):
            Image = (Image1,Image2)[(X+Y)%2]
            Surface.blit(Image, (X,Y))
            X += Image1.get_rect().width
        # Center stuff:
        Y = self.UpperPanelY
        while (Y<432):
            X = -5
            while (X<800):
                Surface.blit(TileImage, (X,Y))
                X += TileImage.get_rect().width
            Y += TileImage.get_rect().height
        # Lower rows of knots:
        Y = 432
        while (Y<600):
            X = -5
            while (X<800):
                Image = (Image1,Image2)[(X+Y)%2]
                Surface.blit(Image, (X,Y))
                X += Image1.get_rect().width
            Y += Image1.get_rect().height
        ###
        
        self.BackSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(self.BackSprite)
        
        ###
        Sprite = GenericTextSprite("Welcome to the Adventurer's Inn!", self.Width / 2, 10, FontSize = 32, CenterFlag = 1)
        self.AddBackgroundSprite(Sprite)
        Border = LineSprite(0, self.RosterPanelY-2, 800, self.RosterPanelY-2, Colors.White, 3)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(self.PerksX - 5, self.GoldY, 800, self.GoldY, Colors.White, 3)
        self.AddBackgroundSprite(Border)
        
        Border = LineSprite(0, self.UpperPanelY, 800, self.UpperPanelY, Colors.White, 3)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(self.StatPlayerX - 35, self.UpperPanelY, self.StatPlayerX - 35, self.RosterPanelY, Colors.White, 3)
        self.AddBackgroundSprite(Border)
        Border = LineSprite(self.PerksX - 5, self.UpperPanelY, self.PerksX - 5, self.RosterPanelY, Colors.White, 3)
        self.AddBackgroundSprite(Border)
        self.GoldSprites = []
        self.DrawGold()
    def DrawGold(self, SkipRedraw = 0):
        for Sprite in self.GoldSprites:
            Sprite.kill()
        self.GoldSprites = []
        #
        Image = TaggedRenderer.RenderToImage("<CN:LIGHTGREY>Funds: <CN:YELLOW>z<CN:WHITE>%s"%Global.Party.Gold, FontSize = 18)
        Sprite = GenericImageSprite(Image, 630, self.GoldY + 4)
        self.AddBackgroundSprite(Sprite)
        self.GoldSprites.append(Sprite)        
        #
        GPCost = GetInnSleepCost()
        Image = TaggedRenderer.RenderToImage("<CN:LIGHTGREY>Sleep cost: <CN:YELLOW>z<CN:WHITE>%s"%GPCost, FontSize = 18)
        Sprite = GenericImageSprite(Image, 630, self.GoldY + 24)
        self.AddBackgroundSprite(Sprite)
        self.GoldSprites.append(Sprite)        
        #
        Image = TaggedRenderer.RenderToImage("<CN:LIGHTGREY>Recruit cost: <CN:YELLOW>z<CN:WHITE>%s"%RecruitCost, FontSize = 18)
        Sprite = GenericImageSprite(Image, 630, self.GoldY + 44)
        self.AddBackgroundSprite(Sprite)
        self.GoldSprites.append(Sprite)        
        if not SkipRedraw:
            self.Redraw()
        
        
    def AddButton(self, Y, Text, HighlightIndex = 0, Command = None):
        #Image = FancyAssBoxedText(Text, FontSize = 22)
        #ButtonSprite = GenericImageSprite(Image, self.ButtonX + 10, Y)
        ButtonSprite = FancyAssBoxedSprite(Text, self.ButtonX + 10, Y, HighlightIndex = HighlightIndex,
                                           BackColor = (11,11,11))
        
        self.AddForegroundSprite(ButtonSprite)
        if Command:
            ButtonSprite.Command = Command
        else:
            ButtonSprite.Command = Text
        self.ButtonSprites.add(ButtonSprite)
    def DrawButtons(self):
        for ButtonSprite in self.ButtonSprites.sprites():
            ButtonSprite.kill()
        Y = self.UpperPanelHeight + self.UpperPanelY + 5
        
        self.AddButton(Y, "Sleep")
        Y += 38
        self.AddButton(Y, "Recruit")
        Y += 38
        self.AddButton(Y, "Dismiss", HighlightIndex = 1)
        Y += 40
        self.AddButton(Y, "Done")
    def DrawParty(self):
        for Sprite in self.PartySprites.sprites():
            Sprite.kill()
        for Sprite in self.PartySupportSprites:
            Sprite.kill()
        self.PartySupportSprites = []
        for Index in range(len(Global.Party.Players)):
            Player = Global.Party.Players[Index]
            Sprite = BattleSprites.CritterSpriteClass(self, Player, self.PartySpriteX[Index], self.PartySpriteY[Index])
            if Player.IsDead():
                Sprite.PlayDead()
            self.PartySprites.add(Sprite)
            self.PlayerSprites.add(Sprite)
            self.AddForegroundSprite(Sprite)
            ####################################
            # Name, level, class
            ShowNameLevelClass(Player, self, self.PartySupportSprites, self.PartySpriteX[Index],self.PartySpriteY[Index])
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
        if self.StatPlayerSprite and self.StatPlayerSprite.CurrentAnimation and \
           self.StatPlayerSprite.CurrentAnimation.Type == AnimationType.Stand and self.AnimationCycle % 300 == 0:
            self.StatPlayerSprite.AnimateAttack()
        DirtyRects = self.ForegroundSprites.draw(self.Surface) ###
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) ###
        Dirty(DirtyRects)
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        # If there's not a highlight box yet, then highlight the clicked player:
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.PartySprites)
        if Sprite:
            self.ClickPlayer(Sprite)
            return
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        if Sprite.Command == "Done":
            self.App.PopScreen(self)
            return
        if Sprite.Command == "Sleep":
            self.DoSleepClick()
        if Sprite.Command == "Dismiss" and self.HighlightedPlayer:
            self.DoDismissClick()
        if Sprite.Command == "Recruit":
            self.DoRecruitClick()
    def RecruitPlayer(self, ClassName):
        if ClassName == "Cancel":
            return
        Global.Party.Gold -= RecruitCost
        self.DrawGold()
        (PlayerName, PlayerClass) = Global.Party.GetUnusedPlayer(ClassName)
        RecruitingPlayer = Critter.Player(PlayerName, PlayerClass)
        Str = "<CN:BRIGHTGREEN>%s</C> the level 1 <CN:BRIGHTBLUE>%s</C> has joined the retinue."%(RecruitingPlayer.Name, RecruitingPlayer.Species.Name)
        self.App.ShowNewDialog(Str)
        Global.Party.Roster.append(RecruitingPlayer)
        Resources.PlayStandardSound("Bleep7.wav")
    def DoSleepClick(self):
        GPCost = GetInnSleepCost()
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        self.Redraw()         
        if GPCost > Global.Party.Gold:
            Str = "You can't afford to stay at the inn!\n\nIt would cost <CN:YELLOW>%d</C> zenny, and you have only <CN:YELLOW>%d</C>."%(GPCost, Global.Party.Gold)
            self.App.ShowNewDialog(Str)
            return
        Str = "It will cost <CN:YELLOW>%d</C> zenny to stay at the inn.\n\n(All <CN:RED>HP</C> and <CN:BLUE>MP</C> will be refilled, dead players will be restored to life)\n\n<CENTER>Stay?"%GPCost
        self.App.ShowNewDialog(Str,ButtonGroup.YesNo, Callback = self.StayAtInn)
    def DoDismissClick(self):
        if not self.HighlightedPlayer:
            return
        if self.HighlightedPlayer in Global.Party.Players:
            Resources.PlayStandardSound("Heartbeat.wav")
            return
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        self.Redraw() 
        Str = "Are you <CN:BRIGHTRED>SURE</C> you want to permanently dismiss <CN:BRIGHTGREEN>%s</C>?"%self.HighlightedPlayer.Name
        self.App.ShowNewDialog(Str,ButtonGroup.YesNo, Callback = self.DismissPlayer)
        
    def DoRecruitClick(self):
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        self.Redraw()         
        if len(Global.Party.Roster) >= 19:
            self.App.ShowNewDialog("Your roster is already full.")
            return
        if Global.Party.Gold < RecruitCost:
            self.App.ShowNewDialog("You can't afford to recruit adventurers.\n\nIt would cost <CN:YELLOW>%d</C> zenny, and you have only <CN:YELLOW>%d</C>"%(RecruitCost, Global.Party.Gold))
            return
        Str = "It will cost <CN:YELLOW>%d</C> zenny to recruit an adventurer.\n\nWhich class will you recruit?"%RecruitCost
        Buttons = Critter.PlayerClassNames[:]
        Buttons.append("Cancel")
        print "These buttons:", Buttons
        self.App.ShowNewDialog(Str,CustomButtons = Buttons, Callback = self.RecruitPlayer)
        
    def HandleKeyPressed(self, Key):
        if Key in (pygame.K_ESCAPE, ord("d")):
            self.App.PopScreen(self)
            return
        if Key == ord("r"):
            self.DoRecruitClick()
            return
        if Key == ord("s"):
            self.DoSleepClick()
            return
        if Key == ord("i"):
            self.DoDismissClick()
            return
        if Key in (280, 265): # pgUp
            self.RosterPanel.ClickUpArrow()
            return
        if Key in (281, 259): # pgDown
            self.RosterPanel.ClickDownArrow()
            return
        
    def DismissPlayer(self):
        """Callback from the "are you sure?" dialog box - really do dismiss."""
        Resources.PlayStandardSound("Kill.wav")
        Global.Party.Roster.remove(self.HighlightedPlayer)
        self.HighlightedPlayer = None
        self.SetHighlightedSprite(None)
        self.RosterPanel.Redraw()
    def HighlightClickedPlayer(self, PlayerSprite):
        if PlayerSprite == None:
            self.HighlightedPlayer = None
            self.HighlightSprite.kill()
        else:
            self.HighlightedPlayer = PlayerSprite.Critter
            if PlayerSprite in self.PartySprites.sprites():
                self.SetHighlightedSprite(PlayerSprite, self)
            else:
                # Roster!
                self.SetHighlightedSprite(PlayerSprite, self.RosterPanel)
    def SwapPlayers(self, SecondPlayer):
        # Swap two players!
        if self.HighlightedPlayer != SecondPlayer:            
            Resources.PlayStandardSound("Bleep5.wav")
            if self.HighlightedPlayer in Global.Party.Players:
                PartyIndex = Global.Party.Players.index(self.HighlightedPlayer)
                RosterIndex = None
            else:
                RosterIndex = Global.Party.Roster.index(self.HighlightedPlayer)
                PartyIndex = None
            if SecondPlayer in Global.Party.Players:
                # The first player moves into the party:
                PartyIndex2 = Global.Party.Players.index(SecondPlayer)
                Global.Party.Players[PartyIndex2] = self.HighlightedPlayer
                self.HighlightedPlayer.Index = PartyIndex2
                self.HighlightedPlayer.Party = Global.Party
            else:
                # The first player moves into the roster:
                self.HighlightedPlayer.Strip()
                RosterIndex2 = Global.Party.Roster.index(SecondPlayer)
                Global.Party.Roster[RosterIndex2] = self.HighlightedPlayer
                self.HighlightedPlayer.Index = None
                self.HighlightedPlayer.Party = None
            if PartyIndex!=None:
                # Second player into party:
                Global.Party.Players[PartyIndex] = SecondPlayer
                SecondPlayer.Index = PartyIndex
                SecondPlayer.Party = Global.Party
            else:
                # Second player into roster:
                SecondPlayer.Strip()
                Global.Party.Roster[RosterIndex] = SecondPlayer
                SecondPlayer.Index = None
                SecondPlayer.Party = None
        self.SetHighlightedSprite(None)
        self.HighlightedPlayer = None
        self.DrawParty()
        self.DrawGold(1)
        self.RosterPanel.Redraw()
        self.RedrawBackground()
        self.Redraw()
    def ClickPlayer(self, PlayerSprite):
        if self.HighlightedPlayer:
            self.SwapPlayers(PlayerSprite.Critter)
        else:
            self.HighlightClickedPlayer(PlayerSprite)
        return
    def StayAtInn(self):
        GPCost = GetInnSleepCost()
        Global.Party.Gold -= GPCost
        self.DrawGold()
        DirtyRects = self.ForegroundSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        DirtyRects = self.AnimationSprites.draw(self.Surface) 
        Dirty(DirtyRects)
        self.Redraw()
        for Player in Global.Party.Players:
            Player.HP = Player.MaxHP
            Player.MP = Player.MaxMP
            Player.Perks["Poison"]=0
            Player.Perks["Sleep"]=0
            Player.Perks["Paralysis"]=0
            Player.Perks["Stone"]=0
            Player.Perks["Silence"]=0
            Player.CurrentAction = ""
            # status -> OK
        # Maze stuff (monsters) is reset:
        Maze.GoToMazeLevel(Global.Party.Z)
        #Global.Maze.Load()
        Music.PlaySongByName("sleeping")
        #Resources.PlaySting("sleeping")
        self.App.ShowFadeOutScreen(self, self, 4)
        # Start the new animation:
        for Sprite in self.PartySprites.sprites():
            Sprite.AnimateStand(1)
def GetInnSleepCost():
    #LevelCosts = {1:10, 2:50, 3:100}
    GP = 0
    for Player in Global.Party.Players:
        if Player.Level == 1:
            GP += 10
        elif Player.Level == 2:
            GP += 25
        else:
            GP += (Player.Level - 2) * 50
    return GP


def ShowNameLevelClass(Player, OwningPane, SpriteGroup, X, Y):
    X += 30
    Y += 100
    if Player.Index!=None:
        Label = PlayerIndexToPlayerLabel[Player.Index]
        TextSprite = GenericTextSprite(PlayerLabelNames[Label], X, Y, Colors.LightGrey)
        TextSprite.rect.left = X - TextSprite.rect.width / 2
        OwningPane.AddBackgroundSprite(TextSprite)
        if SpriteGroup!=None:
            SpriteGroup.append(TextSprite)        
        Y += 16
    TextSprite = GenericTextSprite(Player.Name, 10, Y, Colors.Yellow)
    TextSprite.rect.left = X - TextSprite.rect.width / 2
    OwningPane.AddBackgroundSprite(TextSprite)
    if SpriteGroup!=None:
        SpriteGroup.append(TextSprite)        
    Y += 16
    TextSprite = GenericTextSprite("Level %d"%Player.Level, 10, Y)
    TextSprite.rect.left = X - TextSprite.rect.width / 2
    OwningPane.AddBackgroundSprite(TextSprite)
    if SpriteGroup!=None:
        SpriteGroup.append(TextSprite)        
    Y += 16
    TextSprite = GenericTextSprite("%s"%Player.Species.Name, 10, Y)
    TextSprite.rect.left = X - TextSprite.rect.width / 2
    OwningPane.AddBackgroundSprite(TextSprite)
    if SpriteGroup!=None:
        SpriteGroup.append(TextSprite)        

class RosterPanel(Screen.TendrilsPane):
    PlayerWidth = 125
    PlayersPerRow = 5
    ScrollArrowX = 640
    UpArrowY = 20
    PlayerY = 5
    DownArrowY = 145
    def __init__(self, OwningScreen, BlitX, BlitY, Width, Height):
        Screen.TendrilsPane.__init__(self,OwningScreen,BlitX,BlitY,Width,Height,"RosterPanel")
        self.UpArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelUp.png"))
        self.DownArrowImage = Resources.GetImage(os.path.join(Paths.Images, "MessagePanelDown.png"))
        self.MouseOverPlayerSprite = None
        self.MouseOverPlayer = None 
        self.Screen = OwningScreen
        self.RosterPlayerSprites = pygame.sprite.Group()
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.ScrollRow = 0
        Image = pygame.Surface((self.Width, self.Height))
        Image.blit(OwningScreen.BackSprite.image, (-self.BlitX, -self.BlitY))
        self.DeepSprite = GenericImageSprite(Image, 0, 0)
        self.DeepSprites.add(self.DeepSprite)
        self.Redraw()
    def GetRowCount(self):        
        return 1 + (len(Global.Party.Roster) - 1) / self.PlayersPerRow
    def DrawScrollArrows(self):
        TotalRows = self.GetRowCount()
        self.ScrollRow = max(0, min(self.ScrollRow, TotalRows - 1))
        self.UpArrowSprite = None
        self.DownArrowSprite = None
        if self.ScrollRow > 0:
            self.UpArrowSprite = GenericImageSprite(self.UpArrowImage, self.ScrollArrowX, self.UpArrowY)
            self.AddForegroundSprite(self.UpArrowSprite)
        if self.ScrollRow < (TotalRows - 1):
            self.DownArrowSprite = GenericImageSprite(self.DownArrowImage, self.ScrollArrowX, self.DownArrowY)
            self.AddForegroundSprite(self.DownArrowSprite)
    def Redraw(self):        
        for Sprite in self.AllSprites.sprites():
            Sprite.kill()
        self.DrawScrollArrows()
        CurrentX = 5
        FirstPlayerIndex = self.ScrollRow*self.PlayersPerRow
        for Player in Global.Party.Roster[FirstPlayerIndex:FirstPlayerIndex + self.PlayersPerRow + 1]:
            PlayerSprite = BattleSprites.CritterSpriteClass(self, Player, CurrentX, self.PlayerY)
            # If they're dead, they should look dead:
            if Player.IsDead():
                PlayerSprite.PlayDead()
            self.AddForegroundSprite(PlayerSprite)
            self.RosterPlayerSprites.add(PlayerSprite)
            ShowNameLevelClass(Player, self, None, CurrentX, self.PlayerY)
            CurrentX += self.PlayerWidth
            if (CurrentX > self.Width - self.PlayerWidth):
                break
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
    def ClickUpArrow(self):
        self.ScrollRow = max(self.ScrollRow - 1, 0)
        if self.Master.HighlightedPlayer and not self.Master.HighlightedPlayer.Index:
            self.Master.HighlightClickedPlayer(None)
        self.Redraw()
    def ClickDownArrow(self):        
        self.ScrollRow = min(self.ScrollRow + 1, self.GetRowCount() - 1)
        self.ScrollRow = max(self.ScrollRow, 0)
        if self.Master.HighlightedPlayer and not self.Master.HighlightedPlayer.Index:
            self.Master.HighlightClickedPlayer(None)            
        self.Redraw()
    def HandleMouseClickedHere(self,Position,Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.RosterPlayerSprites)
        if Sprite:
            self.Master.ClickPlayer(Sprite)
            return
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ForegroundSprites)
        if Sprite and Sprite == self.UpArrowSprite:
            self.ClickUpArrow()            
        if Sprite and Sprite == self.DownArrowSprite:
            self.ClickDownArrow()
    def Update(self):
        for Sprite in self.RosterPlayerSprites.sprites():
            Sprite.Update(self.Master.AnimationCycle)
    def FindMouseOverSprites(self,Position):
        OldSprite = self.MouseOverPlayerSprite
        if OldSprite:
            OldPlayer = OldSprite.Critter
        else:
            OldPlayer = None
        self.MouseOverPlayerSprite = None
        self.MouseOverPlayer = None
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.RosterPlayerSprites)
        if Sprite:
            ##self.Master.MouseOverSprites.add(Sprite)
            self.MouseOverPlayerSprite = Sprite
            self.MouseOverPlayer = Sprite.Critter
        if self.MouseOverPlayer != OldPlayer:
            self.Master.DrawStats(self.MouseOverPlayer)
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.DeepSprites.draw(self.BackgroundSurface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
        

            