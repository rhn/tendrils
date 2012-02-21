"""
StatusPanel - list of characters, displayed on the battle screen and on the
maze screen.  Shows character names, HP, MP, status, and current action.
Allows user to trigger spells and items, using keyboard or mouse.
"""
from Utils import *
from Constants import *
import Screen
import Resources
import time
import Critter
import Magic
import Global
import Maze

# Usable items are displayed in a consistently-labeled list, from A to whatever.  
UsableItemNames = ["Potion", "Hi-Potion", "X-Potion", "Antidote",
                   "Flute", "Black Coffee", "Medusa Scale", "Remedy",
                   "Phoenix Down", "Ether", "Elixir", "Escapipe", "Compass"]

class PanelStates:
    Status = "Status" # all players
    OnePlayer = "OnePlayer" # Player selected, menu shown
    Use = "Use"
    Cast = "Cast"
    SelectItemTarget = "SelectItemTarget"
    SelectTarget = "SelectTarget"
    Flee = "Flee"
    
class StatusPanel(Screen.TendrilsPane):
    BriefXCoords = [5, 320, 5, 320]
    BriefYCoords = [48, 48, 96, 96]
    StatusCycleTick = 70
    def __init__(self,OwningScreen,BlitX,BlitY,Width,Height):
        Screen.TendrilsPane.__init__(self,OwningScreen,BlitX,BlitY,Width,Height,"StatusPanel")
        self.Screen = OwningScreen
        # If IsBattle is true, we're on BattleScreen; otherwise, we're on MazeScreen.
        self.IsBattle = 1 # default
        self.State = PanelStates.Status
        self.Player = None # Active player
        self.ButtonSprites =  pygame.sprite.Group()
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.StatusSprites = pygame.sprite.Group()
        self.PlayerStatus = []
        for Player in Global.Party.Players:
            self.PlayerStatus.append(Player.GetStatus())
        self.CastingSpell = None
        self.UsingItem = None
        self.Tick = 0
        self.KeysToSpells = {}
        self.KeysToItems = {}
        self.ReRender()
    def Update(self):
        self.Tick += 1
        if self.Tick > self.StatusCycleTick:
            for Index in range(4):
                self.PlayerStatus[Index] = Global.Party.Players[Index].GetStatus(self.PlayerStatus[Index])
            for Sprite in self.StatusSprites.sprites():
                (StatusText, StatusColor) = self.PlayerStatus[Sprite.Index]
                if StatusColor:
                    Sprite.Color = StatusColor
                Sprite.ReplaceText(StatusText)
            self.Tick = 0
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.DeepSprites.draw(self.BackgroundSurface)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        

    def ReRender(self):
        # Slight hack: Make sure that out player is valid, in case we just returned from an inn screen:
        if self.Player not in Global.Party.Players:
            self.Player = Global.Party.Players[2]
        for Sprite in self.BackgroundSprites.sprites():
            Sprite.kill()
        for Sprite in self.DeepSprites.sprites():
            Sprite.kill()
        for Sprite in self.ForegroundSprites.sprites():
            Sprite.kill()
        self.PlayerStatus = []
        for Player in Global.Party.Players:
            self.PlayerStatus.append(Player.GetStatus())
            
        # %%%
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "StatusPanelBack.png"))
        self.DeepSprite = GenericImageSprite(Image, 0, 0)
        self.DeepSprites.add(self.DeepSprite)
        #self.AddBackgroundSprite(self.DeepSprite)
        ##self.BackgroundSurface.fill(Colors.Blue) #%%%
        # Move between states based on changes in conditions.  (E.g. if a player just
        # died, don't show the menu of spells!)
        if self.State in (PanelStates.SelectTarget, PanelStates.Cast) and not self.Player.CanCastSpells():
            self.State = PanelStates.OnePlayer
        if self.State in (PanelStates.SelectItemTarget, PanelStates.Use) and self.Player.IsIncapacitated():
            self.State = PanelStates.OnePlayer
        # Re-create sprites:
        if self.State == PanelStates.Status:
            self.PrintStatus()
        elif self.State == PanelStates.OnePlayer:
            self.PrintOnePlayer()
        elif self.State == PanelStates.Cast:
            self.PrintCast()
        elif self.State == PanelStates.Use:
            self.PrintUse()
        elif self.State == PanelStates.SelectTarget:
            self.PrintSelectTarget()
        elif self.State == PanelStates.SelectItemTarget:
            self.PrintSelectItemTarget()
        elif self.State == PanelStates.Flee:
            self.PrintFleeConfirm()
        # ...and refresh:
        self.Redraw()
    def PrintSelectTarget(self):
        Y = 3
        Label = PlayerIndexToPlayerLabel[self.Player.Index]
        self.ShowPlayerLine(self.Player, Label, 3)
        Y += 20
        Sprite = GenericTextSprite("Select a target for %s."%self.CastingSpell.Name, 10, Y, Colors.Green, 24)
        self.AddBackgroundSprite(Sprite)
        for Label in range(1,5):
            Player = Global.Party.Players[PlayerLabelToPlayerIndex[Label]]
            self.RenderPlayerBrief(Player, Label, self.BriefXCoords[Label-1], self.BriefYCoords[Label-1],
                               self.CastingSpell.IsValidTarget(Player))
    def PrintSelectItemTarget(self):
        Y = 3
        Label = PlayerIndexToPlayerLabel[self.Player.Index]
        self.ShowPlayerLine(self.Player, Label, 3)
        Y += 20
        Sprite = GenericTextSprite("Use %s on whom?"%self.UsingItem.Name, 10, Y, Colors.Green, 24)
        self.AddBackgroundSprite(Sprite)
        Y += 20
        for Label in range(1,5):
            Player = Global.Party.Players[PlayerLabelToPlayerIndex[Label]]
            self.RenderPlayerBrief(Player, Label, self.BriefXCoords[Label-1], self.BriefYCoords[Label-1], 1)

    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            if self.State == PanelStates.SelectItemTarget:
                # If they click on the line at the top:
                if hasattr(Sprite, "PlayerLine"):
                    self.State = PanelStates.OnePlayer
                    self.ReRender()
                else:                        
                    self.UseItem(self.Player, self.UsingItem, Sprite.Player)
                    self.State = PanelStates.Status
                    self.ReRender()                
                return
            if self.State == PanelStates.SelectTarget:
                if hasattr(Sprite, "PlayerLine"):
                    self.State = PanelStates.OnePlayer
                    self.ReRender()
                else:                                        
                    if self.IsBattle:
                        self.Screen.CommandCallback(("Spell", self.Player, self.CastingSpell, Sprite.Player))
                    else:
                        apply(self.CastingSpell.MazeEffectCode,(self.Screen, self.Player, Sprite.Player))
                    self.State = PanelStates.Status
                    self.ReRender()                
                return
            if self.State == PanelStates.Flee:
                if Sprite.Command == "Yes":
                    self.DoFlee()
                else:
                    self.State = PanelStates.Status
                    self.Player = None
                    self.ReRender()
                return                    
            if self.State in (PanelStates.Status, PanelStates.OnePlayer) and Sprite.Player:
                self.State = PanelStates.OnePlayer
                self.Player = Sprite.Player
                self.ReRender()
                return
            if self.State == PanelStates.Use:
                if Sprite.Item:
                    self.ItemClicked(Sprite.Item)
                    return
                self.State = PanelStates.OnePlayer
                self.ReRender()
                return
            if self.State == PanelStates.Cast:
                if Sprite.Spell:
                    if Sprite.Spell.Target == Magic.SpellTarget.OnePlayer:
                        self.CastingSpell = Sprite.Spell
                        self.State = PanelStates.SelectTarget
                        self.ReRender()
                        return
                    if self.IsBattle:
                        self.Screen.CommandCallback(("Spell", self.Player, Sprite.Spell,  None)) #no target selected
                    else:
                        apply(Sprite.Spell.MazeEffectCode,(self.Screen, self.Player, Sprite.Spell))
                    self.State = PanelStates.Status
                    self.ReRender()
                    return
                self.State = PanelStates.OnePlayer
                self.ReRender()
                return
            if self.State == PanelStates.OnePlayer:
                if Sprite.Command == "Back":
                    self.State = PanelStates.Status
                    self.ReRender()
                    return
                if Sprite.Command == "Turn":
                    if self.IsBattle and self.Player.CanTurn():
                        self.State = PanelStates.Status
                        self.ReRender()
                        self.Screen.CommandCallback(("Turn", self.Player))
                elif Sprite.Command == "Cast": # Cast Turn Flee Use Equip
                    if self.Player.CanCastSpells() and not self.Player.CurrentAction:
                        self.State = PanelStates.Cast
                        self.ReRender()
                        return
                elif Sprite.Command == "Flee":
                    if self.IsBattle and self.Screen.CanFlee:
                        # Confirm: Really try to run?
                        self.State = PanelStates.Flee
                        self.ReRender()
                elif Sprite.Command == "Use":
                    if not self.Player.IsIncapacitated() and not self.Player.CurrentAction:
                        self.State = PanelStates.Use
                        self.ReRender()
                        return
                elif Sprite.Command == "Equip":
                    if self.IsBattle:
                        return
                    Global.App.ShowEquipScreen(self.Player)
                    self.State = PanelStates.Status
                    self.ReRender()
                    return
            print "Don't know what I'm doing with this damn sprite:", Sprite
    def DoFlee(self):
        if self.Screen.CanFlee:
            for Player in Global.Party.Players:
                if Player.IsAlive() and not Player.CurrentAction:
                    Player.CurrentAction = "Fleeing..."
            self.Screen.QueueFleeEvent()
            self.State = PanelStates.Status
            self.Player = None
            self.ReRender()
            return
    def RenderPlayerBrief(self, Player, PlayerLabel, X, Y, IsValid):
        "Helper for choosing item and spell targets.  Build a single sprite that contains the player info."
        PlayerPanel = pygame.Surface((315, 55))
        pygame.draw.rect(PlayerPanel, Colors.White, (0, 0, 312, 41), 1)
        Sprite = GenericImageSprite(PlayerPanel, X, Y)
        Sprite.Player = Player
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        # Now, paint onto the sprite:
        FontSize = 24
        if IsValid:
            Color = Colors.White
        else:
            Color = Colors.Grey
        Image = TextImage("(%d) %s"%(PlayerLabel, Player.Name), Colors.Green, FontSize)
        Sprite.image.blit(Image, (0, 0))
        ##
        if IsValid:
            Color = self.GetPlayerColor(Player)
        else:
            Color = Colors.Grey
        Image = TextImage("%d/%d"%(max(0,Player.HP), Player.MaxHP), Color, FontSize)
        Sprite.image.blit(Image, (140, 0))
        ##
        if IsValid:
            Color = Colors.Blue
        else:
            Color = Colors.Grey        
        Image = TextImage("%d/%d"%(Player.MP, Player.MaxMP),Color, FontSize)
        Sprite.image.blit(Image, (240, 0))
        ##
        (StatusText, StatusColor) = self.PlayerStatus[Player.Index]
        StatusSprite = GenericTextSprite(StatusText, X+10, Y+20, StatusColor, FontSize)
        StatusSprite.Player = Player
        StatusSprite.Index = Player.Index
        self.AddForegroundSprite(StatusSprite)
        self.StatusSprites.add(StatusSprite)
        #Sprite.image.blit(Image, (10, 20))
        ##
        if IsValid:
            Color = Colors.White
        else:
            Color = Colors.Grey        
        Image = TextImage(Player.CurrentAction, Color, FontSize)
        Sprite.image.blit(Image, (100, 20))
    def PrintUse(self):
        Y = 3
        Label = PlayerIndexToPlayerLabel[self.Player.Index]
        self.ShowPlayerLine(self.Player, Label, 3)
        self.KeysToItems = {}
        Y += 20
        Sprite = GenericTextSprite("Select the item to use.", 10, Y, Colors.Green, 24)
        self.AddBackgroundSprite(Sprite)
        # Show the available items:
        X = 3
        Y = 46
        for Index in range(len(UsableItemNames)):
            Letter = ord("a")+Index
            Name = UsableItemNames[Index]
            Count = Global.Party.Items.get(Name.lower(), None)
            CanUse = (Count>0)
            if self.IsBattle and Name.lower() in ("escapipe", "compass"):
                CanUse = 0
            if CanUse:
                Color = Colors.White
                Str = "%s) %s (%d)"%(chr(Letter).upper(), Name, Count)
                self.KeysToItems[Letter] = Global.QuarterMaster.GetItem(Name)
            else:
                Color = Colors.Grey
                if Count:
                    Str = "%s) %s (%d)"%(chr(Letter).upper(), Name, Count)
                else:
                    Str = "--------"
                
            TheSprite = GenericTextSprite(Str, X, Y, Color, FontSize = 20)
            self.AddBackgroundSprite(TheSprite)            
            if CanUse:
                TheSprite.Player = None
                TheSprite.Spell = None
                self.ButtonSprites.add(TheSprite)
                TheSprite.Item = self.KeysToItems[Letter]
            Y += 23
            if Y>125:
                X += 158
                Y = 46
                
    def PrintCast(self):
        Y = 3
        Label = PlayerIndexToPlayerLabel[self.Player.Index]
        self.ShowPlayerLine(self.Player, Label, 3)
        self.KeysToSpells = {}
        Y += 20
        Sprite = GenericTextSprite("Select a spell to cast.", 10, Y, Colors.Green, 24)
        self.AddBackgroundSprite(Sprite)
        # Show the available spells:
        if self.Player.Species.Name == Critter.ClassNames.Cleric:
            Flags = Global.Party.FoundClericSpells
            Spellbook = Global.Spellbook.ClericSpells
        elif self.Player.Species.Name == Critter.ClassNames.Mage:
            Flags = Global.Party.FoundMageSpells
            Spellbook = Global.Spellbook.MageSpells
        else:
            Flags = Global.Party.FoundSummonerSpells
            Spellbook = Global.Spellbook.SummonerSpells
        # Find the highest spell index found by the party:
        MaxFoundIndex = 0
        for SpellIndex in range(len(Flags)):
            if Flags[SpellIndex]:
                MaxFoundIndex = SpellIndex
        MaxFoundIndex = min(SpellIndex, len(Spellbook)-1)
        X = 3
        Y = 46
        for SpellIndex in range(MaxFoundIndex+1):
            Letter = chr(ord("A") + SpellIndex)            
            Spell = Spellbook[SpellIndex]
            if Flags[SpellIndex]:
                Name = Spell.Name
                if (self.Player.Level >= Spell.Level) and (self.Player.MP >= Spell.Mana) and ((self.IsBattle and Spell.CombatUse) or (not self.IsBattle and Spell.MazeUse)):
                    self.KeysToSpells[ord(Letter.lower())] = Spell
                    Color = Colors.White
                else:
                    Color = Colors.Grey
                TheSprite = GenericTextSprite("(%s) %s (%s)"%(Letter, Name, Spell.Mana), X, Y, Color, FontSize = 20)                
            else:
                Name = "?" * len(Spellbook[SpellIndex].Name)
                Color = Colors.Grey
                TheSprite = GenericTextSprite("(%s) %s"%(Letter, Name), X, Y, Color, FontSize = 20)
            self.AddBackgroundSprite(TheSprite)
            if Color == Colors.White:
                TheSprite.Spell = Spell
                TheSprite.Player = None
                TheSprite.Item = None
                self.ButtonSprites.add(TheSprite)
            Y += 23
            if Y>125:
                X += 154
                Y = 46
    def PrintOnePlayer(self):
        Y = 3
        Label = PlayerIndexToPlayerLabel[self.Player.Index]
        self.ShowPlayerLine(self.Player, Label, 3)
        # Line 2: level 1 fighter
        Y += 20
        Str = "Level %d %s"%(self.Player.Level, self.Player.Species.Name)
        Sprite = GenericTextSprite(Str, 20, Y, FontSize = 24)
        self.AddBackgroundSprite(Sprite)
        # Line 3: stats
        Y += 20
        Str = "Str %d Dex %d Con %d Int %d Wis %d Cha %d"%(self.Player.STR, self.Player.DEX, self.Player.CON,
                                                           self.Player.INT,self.Player.WIS, self.Player.CHA)
        Sprite = GenericTextSprite(Str, 20, Y, FontSize = 20)
        self.AddBackgroundSprite(Sprite)
        # Line 4: perks
        Y += 20
        Str = ""
        for Perk in self.Player.SpellPerks.keys():
            if Str:
                Str+=", "
            else:
                Str="Spells: "
            Str += Perk
        Sprite = GenericTextSprite(Str, 20, Y, FontSize = 20)
        self.AddBackgroundSprite(Sprite)
        self.ShowPlayerActionButtons()
    def AddActionButton(self, Text, X, Y):
        Button = GenericImageSprite(FancyAssBoxedText(Text, HighlightIndex = 0), X, Y)
        self.AddBackgroundSprite(Button)
        self.ButtonSprites.add(Button)
        Button.Player = None
        Button.Command = Text
        return Button
    def ShowPlayerActionButtons(self):
        # Buttons:
        Y = 100
        X = 20
        Button = self.AddActionButton("Back", X, Y)
        X += Button.rect.width + 10
        if self.Player.IsIncapacitated():
            return # No other buttons for incapacitated players!
        # NO ACTION BUTTONS for players with a current action:        
        if not self.Player.CurrentAction:
            if self.Player.CanCastSpells():
                Button = self.AddActionButton("Cast", X, Y)
                X += Button.rect.width + 10
            if self.IsBattle and self.Player.CanTurn():
                Button = self.AddActionButton("Turn", X, Y)
                X += Button.rect.width + 10
            if self.IsBattle and self.Screen.CanFlee:
                Button = self.AddActionButton("Flee", X, Y)
                X += Button.rect.width + 10
            if not self.Player.IsIncapacitated():
                Button = self.AddActionButton("Use", X, Y)
                X += Button.rect.width + 10
            if not self.IsBattle:
                Button = self.AddActionButton("Equip", X, Y)
                X += Button.rect.width + 10
    def PrintFleeConfirm(self):
        #Sprite = GenericTextSprite("Really flee?  (Y/N)", self.Width / 2, 50, FontSize = 32, CenterFlag = 1)
        Sprite = GenericTextSprite("Really flee?", self.Width / 2, 50, FontSize = 32, CenterFlag = 1)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.AddActionButton("Yes", 200, 100)
        self.AddActionButton("No", 300, 100)
        
        #Sprite = GenericImageSprite(FancyAssBoxedText("Yes", HighlightIndex = 0), 300, 100)
        #Sprite.Command = "Yes"
        #self.AddBackgroundSprite(Sprite)
    def PrintStatus(self):
        Y = 3
        for PlayerLabel in range(1, 5):
            Player = Global.Party.GetLabel(PlayerLabel)
            self.ShowPlayerLine(Player, PlayerLabel, Y)
            Y += 35
    def GetPlayerColor(self, Player):
        if (Player.HP <= 0):
            PlayerColor = Colors.Red
        elif Player.HP < Player.MaxHP / 3:
            PlayerColor = Colors.Yellow
        else:
            PlayerColor = Colors.White        
        return PlayerColor
    def ShowPlayerLine(self, Player, PlayerLabel, Y):
        Image = pygame.Surface((650, 35))
        Sprite = GenericImageSprite(Image, 0, Y)
        Sprite.Item = None
        Sprite.Spell = None
        self.AddBackgroundSprite(Sprite)
        Sprite.Player = Player
        Sprite.PlayerLine = 1 # Flag!
        self.ButtonSprites.add(Sprite)
        PlayerColor = self.GetPlayerColor(Player)
        Image = TextImage("%d)"%PlayerLabel, Colors.Green, 24)
        Sprite.image.blit(Image, (10, 0))
        Image = TextImage(Player.Name, Colors.White, 24)
        Sprite.image.blit(Image, (40, 0))
        Image = TextImage("%d/%d"%(max(0,Player.HP), Player.MaxHP), PlayerColor, 24)
        Sprite.image.blit(Image, (150, 0))
        Image = TextImage("%d/%d"%(Player.MP, Player.MaxMP),Colors.Blue, 24)
        Sprite.image.blit(Image, (250, 0))
        (StatusText, StatusColor) = self.PlayerStatus[Player.Index]
        StatusSprite = GenericTextSprite(StatusText, 350, Y, StatusColor, 24)
        StatusSprite.Player = Player
        StatusSprite.Index = Player.Index
        self.AddForegroundSprite(StatusSprite)
        self.StatusSprites.add(StatusSprite)
        #Image = TextImage("%s"%(Player.GetStatus()),Colors.White, 24)
        #Sprite.image.blit(Image, (350, 0))
        Image = TextImage("%s"%(Player.CurrentAction), Colors.Red, 24)
        Sprite.image.blit(Image, (450, 0))
    def GetPlayerForKey(self, Key):
        if Key in [49,50,51,52]:
            return Global.Party.Players[PlayerLabelToPlayerIndex[Key - 48]]
    def UseEscapipe(self):
        Global.Party.DropItem("Escapipe")
        Resources.PlayStandardSound("MegamanNoise.wav")
        self.Screen.ShowGlowingText("Zoom!")
        Global.Party.X = Global.Party.InnX
        Global.Party.Y = Global.Party.InnY
        if Global.Maze.Level != Global.Party.InnZ:
            Maze.GoToMazeLevel(Global.Party.InnZ)
            #Global.Maze.Load()
        self.Screen.SignText = ""
        self.Screen.RenderLHS()
        self.Screen.RenderMaze()
        self.Screen.Redraw()            
    def UseItem(self, Player, Item, Target):
        if Player.IsIncapacitated():
            return
        Global.Party.DropItem(Item.Name)
        if self.IsBattle:
            Player.CurrentAction = "Use:%s"%Item.Name 
            self.Master.QueueItemEvent(self.Player, Item, Target)
            return
        self.UseItemEffect(Player, Item, Target)
    def UseItemEffect(self, Player, Item, Target):
        # In a maze, the "animation" and sfx happen here:
        if not self.IsBattle:
            Resources.PlayStandardSound("Heal.wav")
        # Item effects now:
        HealHP = None
        if Item.Name == "Potion":
            HealHP = 20
        elif Item.Name == "Hi-Potion":
            HealHP = 100
        elif Item.Name == "X-Potion":
            HealHP = 500
        if HealHP and Target.IsAlive():
            Amount = min(Target.HP + HealHP, Target.MaxHP) - Target.HP
            if self.IsBattle:
                self.Screen.QueueDamageEvent(Player, Target, -abs(Amount), 1, Colors.Green)
            else:
                Target.HP = min(Target.HP + HealHP, Target.MaxHP)                
        if Item.Name == "Antidote":
            Target.Perks["Poison"] = 0
        elif Item.Name == "Flute":
            Target.Perks["Silence"] = 0
        elif Item.Name == "Black Coffee":
            Target.Perks["Sleep"] = 0
            Target.Perks["Paralysis"] = 0
        elif Item.Name == "Medusa Scale":
            Target.Perks["Stone"] = 0
        elif Item.Name == "Remedy":
            Target.Perks["Poison"] = 0
            Target.Perks["Silence"] = 0
            Target.Perks["Sleep"] = 0
            Target.Perks["Paralysis"] = 0
            Target.Perks["Stone"] = 0
        elif Item.Name == "Ether":
            Target.MP = min(Target.MaxMP, Target.MP + 50)
        elif Item.Name == "Elixir":
            if Target.IsAlive:
                Target.Perks["Poison"] = 0
                Target.Perks["Silence"] = 0
                Target.Perks["Sleep"] = 0
                Target.Perks["Paralysis"] = 0
                Target.Perks["Stone"] = 0
                Target.HP = Target.MaxHP
                Target.MP = Target.MaxMP
        elif Item.Name == "Phoenix Down":
            HealedHP = max(Target.MaxHP / 4, 1)
            if Target.IsDead():
                Target.HP = HealedHP # Zing!
                
    def ItemClicked(self, Item):
        if (Item.Name == "Escapipe"):
            if self.IsBattle:
                return
            Str = "This pipe will warp you back to the last inn where you stayed (on level <CN:BRIGHTGREEN>%s</C>).\n\n<CENTER>Warp?"%Global.Party.InnZ
            Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = self.UseEscapipe)
            return
        if (Item.Name == "Compass"):
            Global.Party.DropItem("Compass")
            Magic.MazeSpellCompass(self.Master, None, None)
            self.State = PanelStates.Status
            self.ReRender()
            return
        self.UsingItem = Item
        self.State = PanelStates.SelectItemTarget
        self.ReRender()
        
    def HandleKeyPressed(self, Key):
        if Key == 96: # backtick: To normal state
            self.State = PanelStates.Status
            self.Player = None
            self.ReRender()
            return
        if Key == 110: # n: don't really flee!
            if self.State == PanelStates.Flee:
                self.State = PanelStates.Status
                self.Player = None
                self.ReRender()
                return
        if Key == 121: # y: really flee!
            if self.State == PanelStates.Flee:
                self.DoFlee()
        if Key in [49,50,51,52]:
            Player = self.GetPlayerForKey(Key)
            if self.State in (PanelStates.Status, PanelStates.OnePlayer):
                self.State = PanelStates.OnePlayer
                self.Player = Player
                self.ReRender()
                return
            if self.State == PanelStates.SelectItemTarget:
                self.UseItem(self.Player, self.UsingItem, Player)
                self.State = PanelStates.Status
                self.ReRender()                
                return
            if self.State == PanelStates.SelectTarget:
                if self.IsBattle:
                    self.Screen.CommandCallback(("Spell", self.Player, self.CastingSpell, Player))
                else:
                    apply(self.CastingSpell.MazeEffectCode,(self.Screen, self.Player, Player))
                self.State = PanelStates.Status
                self.ReRender()                
                return
        if Key == 53:
            self.State = PanelStates.Status
            self.ReRender()
            return
        if self.State == PanelStates.Use:
            Item = self.KeysToItems.get(Key, None)
            if Item:
                self.ItemClicked(Item)
                return
        if self.State == PanelStates.Cast:
            Spell = self.KeysToSpells.get(Key, None)
            if Spell:
                if Spell.Target == Magic.SpellTarget.OnePlayer:
                    self.CastingSpell = Spell
                    self.State = PanelStates.SelectTarget
                    self.ReRender()
                    return
                if self.IsBattle:
                    self.Screen.CommandCallback(("Spell", self.Player, Spell,  None)) #no target selected
                else:
                    apply(Spell.MazeEffectCode,(self.Screen, self.Player, Spell))
                self.State = PanelStates.Status
                self.ReRender()
                return
        if Key == 98: # B is for BACK:
            if self.State in (PanelStates.Use, PanelStates.Cast, PanelStates.SelectItemTarget, PanelStates.SelectTarget):
                self.State = PanelStates.OnePlayer
                self.ReRender()
                return
            if self.State == PanelStates.OnePlayer:
                self.State = PanelStates.Status
                self.ReRender()
                return
        if Key == 117: # U is for USE
            if self.State in (PanelStates.OnePlayer,) and not self.Player.IsIncapacitated() and not self.Player.CurrentAction:
                self.State = PanelStates.Use
                self.ReRender()
                return
        if Key == 116: # T is for TURN:
            if self.IsBattle and self.State == PanelStates.OnePlayer and self.Player.CanTurn():
                self.State = PanelStates.Status
                self.ReRender()
                self.Screen.CommandCallback(("Turn", self.Player))
        if Key == 99: # C is for CAST
            if self.State in (PanelStates.OnePlayer,) and self.Player.CanCastSpells() and not self.Player.CurrentAction:
                self.State = PanelStates.Cast
                self.ReRender()
                return
        if Key == 101: # E is for EQUIP:
            if self.IsBattle:
                return
            if self.State == PanelStates.OnePlayer:
                Global.App.ShowEquipScreen(self.Player)
                self.State = PanelStates.Status
                self.ReRender()
                return
        if Key == 102: # F is for Flee:
            if self.IsBattle and self.Screen.CanFlee and self.State in (PanelStates.Status, PanelStates.OnePlayer):
                # Confirm: Really try to run?
                self.State = PanelStates.Flee
                self.ReRender()
        if Key == 105: # I is for Inventory, if not in battle:
            if not self.IsBattle:
                Player = self.Player
                if not Player:
                    Player = Global.Party.Players[2]
                Global.App.ShowEquipScreen(Player)