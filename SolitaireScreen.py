"""
Solitaire screen.
There are many flavors of solitaire; Tendrils includes just one (at least for now!)
"""
from Utils import *
from Constants import *
import Screen
import ItemPanel
import Global
import Resources
import Music
import os
import time
import math
import string
import Party
import random
HelpText = """<center><CN:ORANGE>Patience</C></center>

<CN:GREEN>Objective: </C> Move all the cards to the four <CN:BRIGHTGREEN>stacks</c> (one for each suit) \
at the upper right.  You place cards there in order from Ace to King.

Click on the <CN:BRIGHTGREEN>deck</C> at upper left to turn over a card.  Cards can be moved around in the \
<CN:BRIGHTGREEN>columns</C> along the bottom.  A card (or pile of cards) can be moved onto a column if the \
bottom card of the column has opposite rank and rank one higher.  For instance, the six of clubs can be \
placed on the seven of hearts.  Only a <CN:GREEN>king</c> can be moved into a blank column.

<CN:Yellow>Good luck!</C>
"""

SScreen = None

class Suits:
    Clubs = 0
    Hearts = 1
    Diamonds = 2
    Spades = 3
    AllSuits = (0,1,2,3)

SuitLetters = {Suits.Clubs:"c",
               Suits.Hearts:"h",
               Suits.Diamonds:"d",
               Suits.Spades:"s"}

OppositeColors = {Suits.Clubs:(Suits.Hearts, Suits.Diamonds),
                  Suits.Spades:(Suits.Hearts, Suits.Diamonds),
                  Suits.Hearts:(Suits.Clubs, Suits.Spades),
                  Suits.Diamonds:(Suits.Clubs, Suits.Spades)}

class Ranks:
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    AllRanks = (1,2,3,4,5,6,7,8,9,10,11,12,13)

CardBackImage = None

class CardSprite(GenericImageSprite):
    def __init__(self, Suit, Rank, X, Y, Z, FaceUp = 0):
        self.Suit = Suit
        self.Rank = Rank
        self.Z = Z
        self.FaceUp = FaceUp
        self.image = self.GetImage()
        GenericImageSprite.__init__(self, self.image, X, Y)
    def GetImage(self):
        if self.FaceUp:
            Path = os.path.join(Paths.ImagesMisc, "Cards", "%02d%s.png"%(self.Rank, SuitLetters[self.Suit]))
            return Resources.GetImage(Path)
        else:
            return CardBackImage
        
    def TurnFaceUp(self):
        if not self.FaceUp:
            self.FaceUp = 1
            self.UpdateImage()
    def TurnFaceDown(self):
        if self.FaceUp:
            self.FaceUp = 0
            self.UpdateImage()
            print "Turn face down!"
    def UpdateImage(self):
        OldCenter = self.rect.center
        self.image = self.GetImage()
        self.rect = self.image.get_rect()
        self.rect.center = OldCenter
    def __str__(self):
        return "<card %s%s>"%(self.Rank,SuitLetters[self.Suit])
class SolitaireScreen(Screen.TendrilsScreen):
    PileX = [20, 130, 240, 350, 460, 570, 680]
    DeckY = 40
    PileY = 150
    FaceDownY = 10
    FaceUpY = 20
    def __init__(self, App, FreePlay):
        global SScreen
        SScreen = self
        self.FreePlay = FreePlay
        self.MousePosition = (0,0)
        self.DraggingCards = []
        self.LastClickCard = None
        self.LastClickTime = 0
        Screen.TendrilsScreen.__init__(self,App)
        self.SummonSong("startout")
        self.DrawBackground()
        self.RedealSprite = None
        self.CardSprites = pygame.sprite.Group()
        self.BuildCards()
    def BuildCards(self):
        global CardBackImage
        Path = os.path.join(Paths.ImagesMisc, "Cards", "back.png")
        CardBackImage = Resources.GetImage(Path)
        # Cards live in the DECK, the PILE, the STACKS, or the TABLE.
        self.Deck = []
        for Suit in Suits.AllSuits:
            for Rank in Ranks.AllRanks:
                Sprite = CardSprite(Suit, Rank, self.PileX[0], self.DeckY, 0, FaceUp = 0)
                self.CardSprites.add(Sprite)
                Sprite.Z = len(self.Deck)
                self.Deck.append(Sprite)
        random.shuffle(self.Deck)
        self.Pile = []
        self.Stacks = [[],[],[],[]]
        self.Table = [[],[],[],[],[],[],[]]
        # Deal cards out:
        for Column in range(7):
            # Some cards are face-down:
            for FaceDownIndex in range(Column):
                Card = self.Deck[0]
                self.Deck = self.Deck[1:]
                Card.TurnFaceDown()
                self.MoveCardToColumn(Card, Column)
            # And one is face-up:
            Card = self.Deck[0]
            self.Deck = self.Deck[1:]
            Card.TurnFaceUp()
            self.MoveCardToColumn(Card, Column)
    def RedrawBackground(self):
        self.BackgroundSurface.fill(Colors.Black)
        self.BackgroundSprites.draw(self.BackgroundSurface)
        # Blit our cards:
        for Z in range(53):
            DrawFlag = 0
            for Sprite in self.CardSprites.sprites():
                if Sprite.Z == Z:
                    DrawFlag = 1
                    if Sprite not in self.ForegroundSprites.sprites():
                        self.BackgroundSurface.blit(Sprite.image, (Sprite.rect.left, Sprite.rect.top))
            if not DrawFlag:
                break # We're done!
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
    def MoveCardToColumn(self, Card, ColumnIndex):
        Card.Z = len(self.Table[ColumnIndex])
        Y = self.PileY
        for LowerCard in self.Table[ColumnIndex]:
            if LowerCard.FaceUp:
                Y += self.FaceUpY
            else:
                Y += self.FaceDownY        
        self.Table[ColumnIndex].append(Card)
        Card.rect.left = self.PileX[ColumnIndex]
        Card.rect.top = Y
    def MoveCardToPile(self, Card):
        Card.TurnFaceUp()
        Card.Z = len(self.Pile)
        Card.rect.left = self.PileX[1]
        Card.rect.top = self.DeckY
        self.Pile.append(Card)
    def DrawBackground(self):
        "Draw top label, buttons"
        Sprite = GenericTextSprite("Patience", 400, 10, Colors.Orange, CenterFlag = 1, FontSize = 32)
        self.AddBackgroundSprite(Sprite)
        # Buttons:
        self.ButtonSprites = pygame.sprite.Group()
        Sprite = FancyAssBoxedSprite("Help", 720, 510, HighlightIndex = 0)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        Sprite = FancyAssBoxedSprite("Give up", 720, 560)
        Sprite.rect.left -= Sprite.rect.width / 2
        self.AddBackgroundSprite(Sprite)
        self.ButtonSprites.add(Sprite)
        for Index in range(4):
            Name = ("Club","Heart","Diamond","Spade")[Index]
            Path = os.path.join(Paths.ImagesMisc, "Cards", "%s.png"%Name)
            Image = Resources.GetImage(Path)
            Sprite = GenericImageSprite(Image, self.PileX[3 + Index], self.DeckY + 20)
            self.AddBackgroundSprite(Sprite)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        if Key == ord("h"):
            self.ClickHelp()
        elif Key == Keystrokes.Debug:
            print "-"*70
            print "Deck len:", len(self.Deck)
            for Suit in Suits.AllSuits:
                print "Suitstack %d:"%Suit
                for Card in self.Stacks[Suit]:
                    print " - %s:%s:%s"%(Card, Card.FaceUp, Card.Z)
            for Index in range(7):
                print "Column %d:"%Index
                for Card in self.Table[Index]:
                    print " - %s:%s:%s"%(Card, Card.FaceUp, Card.Z)
                
    def ClickHelp(self):
        Global.App.ShowNewDialog(HelpText)
    def ClickQuit(self):
        Global.App.ShowNewDialog("Really give up?",ButtonGroup.YesNo, Callback = self.ClickQuitReally)
    def ClickQuitReally(self):
        Global.App.PopScreen(self)
    def Redeal(self):
        print "REDEAL!"
        for Index in range(len(self.Pile)-1, -1, -1):
            Card = self.Pile[Index]
            Card.Z = len(self.Deck)
            Card.TurnFaceDown()
            Card.rect.left = self.PileX[0]
            Card.rect.top = self.DeckY
            self.Deck.append(Card)
        self.Pile = []
        Resources.PlayStandardSound("Boop4.wav")
        self.UpdateRedealSprite()
        self.Redraw()
    def CheckVictory(self):
        if len(self.Deck):
            #print "(Deck nonzero, not done.)",
            return
        if len(self.Pile):
            #print "(Pile nonzero, not done.)",
            return
        for List in self.Table:
            if len(List):
                #print "(Table list nonempty, not done.)",
                return
        # We win!
        Music.FadeOut()
        Resources.PlayStandardSound("TodHappy.wav")
        Str = """<CENTER><CN:BRIGHTGREEN>Success!</C></CENTER>

With your excellent guidance, the armies of the Four Kingdoms gather into formation.  There is a sound of trumpets, \
and a mighty charge.  Your forces quickly rout the Goblin Army.  Soon, the dust clears, and the gory battlefield \
is shrouded in silence."""
        Global.App.ShowNewDialog(Str)
        Global.Party.EventFlags["L8Solitaire"] = 1
        Global.App.PopScreen(self)
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for button clicks:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            if Sprite.Text == "Help":
                self.ClickHelp()
            elif Sprite.Text == "Redeal":
                self.Redeal()
            else:
                self.ClickQuit()
            return
        # Now, handle clicked cards:
        TopZ = None
        CardsClicked = pygame.sprite.spritecollide(Dummy, self.CardSprites, 0)
        #print "Get by Z order.  %d cards hit.  %d cards in deck"%(len(CardsClicked), len(self.Deck))
        for Card in CardsClicked:
            #print "(Clicked %s at z %s...)"%(Card, Card.Z)
            if (TopZ == None) or (Card.Z > TopZ):
                TopZ = Card.Z
                ClickedCard = Card
        if TopZ!=None:
            self.ClickCard(ClickedCard, Position)
    def UpdateRedealSprite(self):
        if len(self.Deck)==0 and len(self.Pile) and not self.RedealSprite:
            self.RedealSprite = FancyAssBoxedSprite("Redeal", 720, 450)
            self.RedealSprite.rect.left -= self.RedealSprite.rect.width / 2
            self.RedealSprite.Text = "Redeal"
            self.ButtonSprites.add(self.RedealSprite)
            self.AddForegroundSprite(self.RedealSprite)
        if len(self.Deck)>0 and self.RedealSprite:
            self.RedealSprite.kill()
            self.RedealSprite = None
    def ClickCard(self, Card, Position):
        #print "Clicked card %s (Z %s)"%(Card, Card.Z)
        ClickTime = time.clock()
        #print (self.LastClickCard == Card), (ClickTime - self.LastClickTime)
        if self.LastClickCard == Card and (ClickTime - self.LastClickTime) < 0.4:
            # A double-click!  Try moving to stack:
            #print "Double click!"
            if self.CanDropOnStack(Card):
                CardList = None
                if Card in self.Pile:
                    CardList = self.Pile
                else:
                    for List in self.Table:
                        if Card in List:
                            CardList = List
                            break
                if CardList:
                    CardList.remove(Card)
                    self.MoveCardToStack(Card, self.Stacks[Card.Suit])
                    self.Redraw()
                    self.CheckVictory()
                    return
        self.LastClickCard = Card
        self.LastClickTime = ClickTime
        # Simple cases first.
        # Clicking the deck deals a card onto the pile:
        if Card in self.Deck:
            #DealCard = self.Deck[0]
            #self.Deck = self.Deck[1:]
            self.Deck.remove(Card)
            self.MoveCardToPile(Card)
            self.UpdateRedealSprite()
            self.Redraw()
            return
        # Clicking the bottom card on a column flips it over:
        for Index in range(7):
            if self.Table[Index] and self.Table[Index][-1]==Card and not Card.FaceUp:
                Card.TurnFaceUp()
                self.Redraw()
                return
        # Otherwise, clicking face-down cards does nothing:
        if not Card.FaceUp:
            print "Skip!  Not face up."
            return
        if pygame.mouse.get_pressed()[0]:
            # Face-up cards from the table or from the pile or from the stacks can be dragged.
            self.StartDragTime = time.time()
            self.DragPosition = Position
            # Get a list of dragging-cards:
            self.DraggingCards = []
            CardLists = self.Table[:]
            CardLists.append(self.Pile)
            CardLists.extend(self.Stacks)
            for CardList in CardLists:
                Found = 0
                for ListCard in CardList:
                    if ListCard == Card:
                        Found = 1
                        self.DraggingFromList = CardList
                    if Found:
                        ListCard.X = ListCard.rect.left
                        ListCard.Y = ListCard.rect.top
                        self.AddForegroundSprite(ListCard)
                        self.DraggingCards.append(ListCard)
                if Found:
                    break
            print "Dragging these cards now:", self.DraggingCards
            self.Redraw()
    def HandleMouseMoved(self,Position,Buttons,LongPause = 0):
        "Track mouse position, for summonings"
        self.MousePosition = Position            
    def Update(self):
        if self.DraggingCards:
            if pygame.mouse.get_pressed()[0]:
                # Move the dragging cards around:
                DeltaX = self.MousePosition[0] - self.DragPosition[0]
                DeltaY = self.MousePosition[1] - self.DragPosition[1]
                for Card in self.DraggingCards:
                    Card.rect.left = Card.X + DeltaX
                    Card.rect.top = Card.Y + DeltaY
            else:
                # Drop cards!
                self.DropCards()
    def DropCards(self):
        if not self.DraggingCards:
            return
##        # A fast drag, to the same pile, counts as a click:
##        if (time.clock() - self.StartDragTime) < 1.0:
##            pass
        (X, Y) = self.MousePosition
        for Card in self.DraggingCards:
            self.ForegroundSprites.remove(Card)
            Card.rect.left = Card.X
            Card.rect.top = Card.Y
        DraggingCards = self.DraggingCards
        self.DraggingCards = []
        # Where are we dropping?
        Dropping = None
        if Y < self.PileY:
##            if X > self.PileX[0] and X < self.PileX[1]:
##                Dropping = self.Deck
##            elif X >self.PlieX[1] and X < self.PileX[2]:
##                Dropping = self.Pile
##            else:
            for Suit in Suits.AllSuits:
                if X > self.PileX[Suit+3] and X < self.PileX[Suit+3] + 90:
                    #Dropping = self.Stacks[Suit]
                    if len(DraggingCards)==1 and DraggingCards[0].Suit == Suit:
                        if self.CanDropOnStack(DraggingCards[0]):
                            #self.RemoveCardFromList(self.DraggingFromList, DraggingCards[0])
                            self.DraggingFromList.remove(DraggingCards[0]) #
                            self.MoveCardToStack(DraggingCards[0], self.Stacks[Suit])
                            self.Redraw()
                            self.CheckVictory()
                            return
            # Denied!
            self.Redraw()
            return
        # Ok, trying to place on a stack:
        for Index in range(7):
            if X > self.PileX[Index] and X < self.PileX[Index] + 90:
                # Is it legal?
                if self.CanDropOnColumn(DraggingCards[0], self.Table[Index]):
                    self.DropOnColumn(DraggingCards, self.DraggingFromList, Index)
        # Denied!
        self.Redraw()
        return
    def MoveCardToStack(self, Card, Stack):
        Card.rect.left = self.PileX[Card.Suit + 3]
        Card.rect.top = self.DeckY
        Card.Z = len(Stack)
        Stack.append(Card)
    def CanDropOnStack(self, DragCard):
        Suit = DragCard.Suit
        if len(self.Stacks[Suit])==0:
            return (DragCard.Rank==Ranks.Ace)
        if self.Stacks[Suit][-1].Rank == DragCard.Rank - 1:
            return 1
        return 0
        
    def CanDropOnColumn(self, DragCard, ColumnCards):
        if len(ColumnCards) == 0:
            return (DragCard.Rank == Ranks.King)
        Suit = DragCard.Suit
        if ColumnCards[-1].Suit in OppositeColors[Suit]:
            if ColumnCards[-1].Rank == DragCard.Rank + 1:
                return 1
        return 0
    def DropOnColumn(self, DragCards, DragFromList, Index):
        for Card in DragCards:
            DragFromList.remove(Card)
            self.MoveCardToColumn(Card, Index)
