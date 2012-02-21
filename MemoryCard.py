"""
This module is the "memory card" for tendrils as a whole, tracking information that's not particular to a
particular game.  For instance: Number of victories, number of deaths, total play-time, and most importantly,
unlocked minigames.
To make life easy, we stuff everything into one DICTIONARY of strings/ints/floats.
"""

import cPickle
import Global
from Utils import *

class MemoryCardClass:
    def __init__(self):
        self.Dict = {}
    def Load(self):
        try:
            File = open(SharedDataFileName("MemoryCard.dat"),"rb")
            self.Dict = cPickle.load(File)
        except:
            pass # That's okay, we'll just start fresh!
        ##self.DebugPrint()
    def DebugPrint(self):
        print "-="*30
        print "MEMORII KAADO:"
        for Key in self.Dict.keys():
            print "   '%s' : '%s'"%(Key, self.Dict[Key])
        print "-="*30
    def Get(self, Name, Default = None):
        return self.Dict.get(Name, Default)
    def Set(self, Name, Value = 1):
        self.Dict[Name] = Value
        self.Save()
    def Save(self):
        try:
            File = open(SharedDataFileName("MemoryCard.dat"),"wb")
            cPickle.dump(self.Dict, File)
        except:
            print "** Warning: Unable to save memory card data."
            traceback.print_exc()

if not Global.MemoryCard:
    Global.MemoryCard = MemoryCardClass()
    Global.MemoryCard.Load()
    