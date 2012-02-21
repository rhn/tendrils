"""
Special-purpose dialog to handle LEVELING UP.
Characters sometimes gain a random stat when they level up.  They always
get to choose one stat to raise.  Also, they get more HP and (if applicable) MP.
"""

from Utils import *
from Constants import *
import Screen
import MessagePanel
import Global
import NewDialogScreen

StatNames = ("STR", "DEX", "CON", "INT", "WIS", "CHA")

class LevelUpScreen(NewDialogScreen.DialogScreen):
    def __init__(self, Player, Callback):
        self.Player = Player
        self.TrueCallback = Callback
        Text = self.Player.LevelUp()
        CustomButtons = self.GetRaisableAttributes()
        if len(CustomButtons)==0:
            CustomButtons = ["Ok",]
        else:
            Text += "%s's attributes are:\n"%self.Player.Name
            for StatName in StatNames:
                Stat = self.Player.GetNakedStat(StatName)
                Text += "%s: %d\n"%(StatName, Stat)
            Text += "\nChoose an attribute to power up:"
        NewDialogScreen.DialogScreen.__init__(self, Global.App, Text, CustomButtons = CustomButtons, Callback = self.RaiseAttribute)
        Resources.PlayStandardSound("PowerUp.wav")
    def GetRaisableAttributes(self):
        List = []
        for StatName in StatNames:
            if self.Player.GetNakedStat(StatName) < MaxStat:
                List.append(StatName)
        return List
    def RaiseAttribute(self, Str):
        if Str=="Ok":
            return
        OldVal = getattr(self.Player, Str)
        setattr(self.Player, Str, OldVal + 1) # Gain a point of stat!
        # And, call the 'real' callback:
        apply(self.TrueCallback)