"""
Some sort of playing-card puzzle...meh.  Not ready for broadcast yet.
Here's one idea: A 3x3 grid of cards.  You place cards from the deck onto
the grid.  If you form a run (horizontally, vertically, or diagonally) of cards
of the same suit, the same number, or a straight of 3 numbers, you remove those
three cards.  The idea is to clear out the whole grid.  (Along the way, you might
form stacks 2, 3, or higher on the grid points)
"""
from Utils import *
from Options import *
import Screen
#import TSS
import BattleSprites
import ItemPanel
import Global
import Resources
import string
import sys

class Suits:
    Heart="H"
    Club="C"
    Spade="S"
    Diamond="D"
    Suits = (Heart, Club, Spade, Diamond)
    
Pips = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "J", "Q", "K"]

class CardPuzzlePanel(Screen.TendrilsPane):
    "Card Lock"
    WireStartX = 100
    WireEndX = 700
    WireY = 100
    Instructions = """<CENTER><CN:BRIGHTBLUE>Wire Lock</C></CENTER>\n\nClick on one of the targets on the left to start the ball \
rolling.  The ball rolls to the right, following any shunts it encounters.  Try to hit the \
target on the far right."""
    def __init__(self, Master, BlitX, BlitY, Width, Height, DungeonLevel = 1, HasNinja = 0):
        Screen.TendrilsPane.__init__(self, Master, BlitX, BlitY, Width, Height, "Trap")
        self.DungeonLevel = DungeonLevel
        self.HasNinja = HasNinja
        self.TimeLimit = 600
        if HasNinja:
            self.TimeLimit *= 1.5
        self.Animating = 0
        self.Disarmed = 0
        self.Triggered = 0
    def GetCardImage(self, Pip, Suit):
        if Suit in (Suits.Heart, Suits.Diamond):
            Color = Colors.Red
        else:
            Color = Colors.Blue
        Image = TextImage("%s%s"%(Pip, Suit), Color, FontSize = 24)
        return Image
    def IsDisarmed(self):
        for X in range(3):
            for Y in range(3):
                if len(self.Field[X][Y]):
                    return 0
        return 1
    def GetPuzzle(self):
        self.Deck = []
        self.Discards = []
        for Suit in Suits.Suits:
            for Pip in Pips:
                self.Deck.append((Pip, Suit))
        random.shuffle(self.Deck)
        self.Field = []
        for Row in range(3):
            self.Field.append([None, None, None])
        while (1):
            for X in range(3):
                for Y in range(3):
                    if not self.Field[X][Y]:
                        self.Field[X][Y] = [self.Deck[0],]
                        self.Deck = self.Deck[1:]
            Clears = self.ClearRuns()
            if not Clears:
                break
    def IsFailed(self):
        return self.Triggered
    def RenderPuzzle(self):
        for Sprite in self.CardSprites.sprites():
            Sprite.kill()
        for X in range(3):
            for Y in range(3):
                Stack = self.Field[X][Y]
                if Stack:
                    Card = Stack[-1]
                    Image = self.GetCardImage(Card[0], Card[1])
                else:
                    Card = None
                    Image = TextImage("XX")
                Sprite = GenericImageSprite(Image, 100 + X*100, 100 + Y*100)
                Sprite.X = X
                Sprite.Y = Y
                Sprite.Card = Card
                self.AddBackgroundSprite(Sprite)
                self.CardSprites.add(Sprite)
        Y = 50
        for Card in self.Deck[:5]:
            Image = self.GetCardImage(Card[0],Card[1])
            Sprite = GenericImageSprite(Image, 600, Y)
            Sprite.X = None
            Sprite.Y = None
            self.AddBackgroundSprite(Sprite)
            self.CardSprites.add(Sprite)
            Y += 80
    def InitTrap(self):
        self.GetPuzzle()
        self.CardSprites = pygame.sprite.Group()
        self.RenderPuzzle()
        self.Redraw()
    def ShowInstructions(self):
        #Global.App.ShowNewDialog(self.Instructions, Callback = self.Start)
        self.Start()
        pass #%%%
    def Start(self):
        self.InitTrap()
        self.Redraw()
        self.Master.StartTimer()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.CardSprites)
        if Sprite:
            self.CardClick(Sprite)
    def CardClick(self, Sprite):
        if Sprite.X == None:
            return
        self.Field[Sprite.X][Sprite.Y].append(self.Deck[0])
        del self.Deck[0]
        if len(self.Deck) == 0:
            self.Deck = self.Discards
            self.Discards = []
            random.shuffle(self.Deck)
        self.ClearRuns()
        self.RenderPuzzle()
        self.Redraw()
    def HandleKeyPressed(self, Key):
        pass
    def ClearRuns(self):
        Runs = [((0,0),(1,0),(2,0)),
                ((0,1),(1,1),(2,1)),
                ((0,2),(1,2),(2,2)),
                #diagonal:
                ((0,0),(1,1),(2,2)),
                ((2,0),(1,1),(0,2)),
                ((0,0),(0,1),(0,2)),
                # vertical
                ((0,0),(0,1),(0,2)),
                ((1,0),(1,1),(1,2)),
                ((2,0),(2,1),(2,2)),
                ]
        Clears = []
        for Sequence in Runs:
            Cards = []
            for Coords in Sequence:
                Stack = self.Field[Coords[0]][Coords[1]]
                if not Stack:
                    break
                Cards.append(Stack[-1])
            if len(Cards)<3:
                continue
            ClearFlag = 0
            if Cards[0][0] == Cards[1][0] == Cards[2][0]:
                ClearFlag = 1
            if Cards[0][1] == Cards[1][1] == Cards[2][1]:
                ClearFlag = 1
            Numbers = [Cards[0][0], Cards[1][0], Cards[2][0]]
            for Index in range(len(Numbers)):
                Numbers[Index] = Pips.index(Numbers[Index])
            Numbers.sort()
            if Numbers[1] == Numbers[0]+1 and Numbers[2] == Numbers[1]+1:
                ClearFlag = 1
            elif Numbers[2] == len(Pips)-1 and Numbers[0]==0 and Numbers[1]==1:
                ClearFlag = 1
            elif Numbers[1] == len(Pips)-2 and Numbers[2]==len(Pips)-1 and Numbers[0]==0:
                ClearFlag = 1
            if ClearFlag:
                Clears.append(Sequence)
        # Set used flags:
        UsedFlags = [[0,0,0],[0,0,0],[0,0,0]]
        for Sequence in Clears:
            Cards = []
            for Coords in Sequence:
                if UsedFlags[Coords[0]][Coords[1]]:
                    continue
                UsedFlags[Coords[0]][Coords[1]] = 1
                Stack = self.Field[Coords[0]][Coords[1]]
                if not Stack:
                    break
                Cards.append(Stack[-1])
                del Stack[-1]
            self.Discards.extend(Cards)
        return len(Clears)
