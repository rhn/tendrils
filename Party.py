"""
"In America, you always find party!  In old country, party always finds you!"  -- Yakov Smirnov

The Party class keeps track of the player characters in the party (and the retinue back at the inn).  The party
object keeps track of which bosses have been killed, and which fixed-position chests looted.  Indeed, the Party
object keeps track of so much stuff that when you save and load the game, you're basically just pickling and
unpickling a Party object!

Equipment (like a shield) can be held by a party member; they are tracked in the Party's Items dictionary
(with LOWER-CASE keys) or in the character's Equipment dictionary.  Key items (like a Copper Key or WIS seed)
belong to the party as a whole and are stored in the KeyItemFlags dictionary (case-sensitively).  (See also
SpecialItems.py for code handling unique item usage)
"""
from Utils import *
import Critter
import Global
import types
import traceback
import sys
#import cPickle
import pickle
import cStringIO
import httplib, urllib

BetaStatsHost = "127.0.0.1:8080"
BetaStatsURL = "/Pharm201/BetaBlob.py"

def ReportBetaStats(Str):
    print "RBS:"
    params = urllib.urlencode({'Stats': Str, 'Version': Global.Version})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(BetaStatsHost)
    print "CONN:", conn
    conn.request("POST", BetaStatsURL, params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = str(response.read())
    print "\n\n\n"
    print "Data:", data
    conn.close()
    return data #[:200]
        

TheParty = None

class Party:
    def __init__(self):
        global TheParty
        self.Players = []
        self.Roster = [] # Players not currently in the party
        self.Items = {} # ItemName to count.  Keys are in lower-case.
        self.LootedChests = {} # Entries are tuples of the form (X, Y, Level)
        self.KilledBosses = {} # Entries of the form (Level, Name)
        self.KeyItemFlags = {} # 'key item' flags (non-equippable plot items like keys) 
        self.EventFlags = {} # General-purpose event flags
        self.ActiveSpells = {} # Map: Name to ticks-left
        self.FoundMageSpells = {} # Map: Index to true/false
        self.FoundClericSpells = {}
        self.FoundSummonerSpells = {}
        self.BigBrother = Global.BigBrother
        self.Options = {"SongDifficulty":1, "SFXVolume":50} # controlled on the Options screen
        self.Gold = 0 # Or "zenny", rather :)
        self.BlinkenCount = 0
        self.PawnedStuff = {} # Shop name -> Subdictionary mapping item names to counts
        self.BardPower = 0 # accumulates, then provides MP
        self.X = 0 # Maze position
        self.Y = 0
        self.Z = 1
        self.TotalPlayTime = 0
        self.KillCount = 0
        # For warping home:
        self.InnX = 4
        self.InnY = 2
        self.InnZ = 1
        self.GetNextRandomBattle()
        self.Heading = Directions.Up
        self.FindDefaultSpells()
        TheParty = self
    def LearnSpell(self, Class, Index):
        Class = Class.lower().strip()
        if Class == "mage":
            Spells = self.FoundMageSpells
            Book = Global.Spellbook.MageSpells
            ClassName = "Mages"
        elif Class == "cleric":
            Spells = self.FoundClericSpells
            Book = Global.Spellbook.ClericSpells
            ClassName = "Clerics"
        else:
            Spells = self.FoundSummonerSpells
            Book = Global.Spellbook.SummonerSpells
            ClassName = "Summoners"
        if not Spells[Index]:
            Spells[Index] = 1
            SpellName = Book[Index].Name
            return "<CN:YELLOW>[ %s can now cast the spell <CN:BRIGHTGREEN>%s<CN:YELLOW> ]\n"%(ClassName, SpellName)
        return ""
    def DecrementActiveSpells(self):
        RanOut = 0
        for Name in self.ActiveSpells.keys():
            self.ActiveSpells[Name] -= 1
            if self.ActiveSpells[Name] <= 0:
                del self.ActiveSpells[Name]
                RanOut = 1
        return RanOut
    def CanCalfo(self):
        if not self.FoundClericSpells[2]:
            return 0
        for Player in self.Players:
            if Player.Species.Name == Critter.ClassNames.Cleric and Player.IsAlive() and Player.MP >= 3:
                return 1
    def CastCalfo(self):
        for Player in self.Players:
            if Player.Species.Name == Critter.ClassNames.Cleric and Player.IsAlive() and Player.MP >= 3:
                Player.MP -= 3
                return
    def GetBuyCost(self, BaseCost):
        CHA = 0
        MaxCha = MaxStat * len(self.Players)
        for Player in self.Players:
            CHA += Player.CHA
        # Cost is 200% of raw price minus a discount of 0-100%
        Multiplier = 2.0 - (CHA / float(MaxCha))
        return int(Multiplier * BaseCost)
    def GetSellCost(self, BaseCost):
        CHA = 0
        MaxCha = MaxStat * len(self.Players)
        for Player in self.Players:
            CHA += Player.CHA
        # Cost is 50% of raw price plus a bonus of 0-50%
        Multiplier = 0.5 + 0.5*(CHA / float(MaxCha))
        return int(Multiplier * BaseCost)
    def CanSeeSecretDoors(self):
        for Player in self.Players:
            if Player.HasPerk("X-ray Vision"):
                return 1
        if self.ActiveSpells.get("Eye of Argon", 0):
            return 1
        return 0
    def FindBestEquipForSlot(self, Slot, Player):
        BestItem = None
        BestScore = 0
        for ItemName in self.Items.keys():
            if self.Items[ItemName]<=0:
                continue
            Item = Global.QuarterMaster.GetItem(ItemName)
            if not Player.CanEquip(Item):
                continue
            if Item.Slot != Slot:
                continue
            Score = 0
            if Slot == EquipSlots.Weapon:
                Player.Equip(Item)
                Score = 1000*float(Player.GetAverageDamage())
            Score += Item.AC * 5
            Score += Item.STR * 20
            Score += Item.DEX * 20
            Score += Item.CON * 20
            Score += Item.INT * 20
            Score += Item.WIS * 20
            Score += Item.CHA * 20
            Score += Item.MaxHP
            Score += Item.MaxMP
            Score += Item.ToHitBonus * 10
            Score += 10 * len(Item.Perks.keys())
            if (Score > BestScore):
                BestScore = Score
                BestItem = Item
        #print "Best item: %s score %s"%(BestItem, BestScore)
        return BestItem
    def GetNextRandomBattle(self):
        self.StepsUntilWanderingMonster = random.randrange(40, 200)
    def FindDefaultSpells(self):
        for X in range(15):
            self.FoundMageSpells[X] = 0
            self.FoundClericSpells[X] = 0
            self.FoundSummonerSpells[X] = 0
        if not IsEXE():
            MageFound = 1 #15 
            ClericFound = 2  #15
            SummonerFound = 1  # 15
        else:
            MageFound = 1 # FIRE
            ClericFound = 2 #CURE and ANTIDOTE
            SummonerFound = 1 # ZERGRUSH
        for X in range(MageFound): 
            self.FoundMageSpells[X] = 1
        for X in range(ClericFound):   
            self.FoundClericSpells[X] = 1
        for X in range(SummonerFound): 
            self.FoundSummonerSpells[X] = 1
    def GetDirection(self, Direction):
        if Direction<1 or Direction>4:
            print "* INVALID direction pased to Party.GetDirection(): %s"%Direction
            traceback.print_stack()
            Direction = 1
        return self.Players[Direction - 1]
    def GetLabel(self, Label):
        if Label<1 or Label>4:
            print "* INVALID label pased to Party.GetLabel(): %s"%Label
            traceback.print_stack()
            Direction = 1
        return self.Players[PlayerLabelToPlayerIndex[Label]]
    def GetItems(self):
        return self.Items
    def GetItem(self, Name):
        if type(Name)!=types.StringType:
            Name = Name.Name
        Name = Name.lower()
        if not self.Items.has_key(Name):
            self.Items[Name] = 0
        self.Items[Name] += 1
    def DropItem(self, Name):
        if type(Name)!=types.StringType:
            Name = Name.Name
        Name = Name.lower()
        if self.Items.has_key(Name):
            self.Items[Name] = max(self.Items[Name]-1, 0)
            if self.Items[Name]<= 0:
                del self.Items[Name]
    def AddPlayer(self, Player):
        Player.Index = len(self.Players)
        self.Players.append(Player)
        Player.Party = self
    def AddRosterPlayer(self, Player):
        Player.Index = None
        self.Roster.append(Player)
        Player.Party = self
    def HasNinja(self):
        for Player in self.Players:
            if Player.Species.Name == "Ninja" and Player.IsAlive():
                return 1
        if self.ActiveSpells.get("Thief", 0):
            return 1
        return 0
    def GetLiveMember(self):
        List = []
        for Member in self.Players:
            if Member.IsAlive():
                List.append(Member)
        if not List:
            return None
        return random.choice(List)
    def GetUnusedPlayer(self, ClassName):
        Names = {}
        Names[Critter.ClassNames.Fighter] = ["Toad", "Cloud", "Ruto", "Axl", "Dhalsim", "Fighter"]
        Names[Critter.ClassNames.Bard] = ["Link", "Iolo", "Parappa"]
        Names[Critter.ClassNames.Ninja] = ["Shinobi", "Haohmaru", "Donatello"]
        Names[Critter.ClassNames.Summoner] = ["Quistis", "Celes", "Justin Bailey"]
        Names[Critter.ClassNames.Cleric] = ["Tiala", "Lufia", "Nei"]
        Names[Critter.ClassNames.Mage] = ["Tellah", "MrWardner", "Red Elf"]
        NameChoices = Names[ClassName]
        SanityCount = 25
        Cycle = 0
        PlayerClass = Critter.ClassNameToClass[ClassName]
        while (1):
            Name = random.choice(NameChoices)
            Cycle += 1
            if Cycle > SanityCount:
                return ("Melvin", PlayerClass)
            UsedFlag = 0
            for Player in self.Players:
                print Player.Name
                if Player.Name.lower() == Name.lower():
                    UsedFlag = 1
                    break
            for Player in self.Roster:
                print Player.Name
                if Player.Name.lower() == Name.lower():
                    UsedFlag = 1
                    break
            if UsedFlag:
                continue
            print "OK:",Name
            return (Name, PlayerClass)

class BigBrother:
    """
    Keep track of various stats.  This is mostly for testing purposes, to figure out which songs and mini-games
    are too hard or too easy...but it also gives us some cute info to present on the victory screen.  
    """
    def __init__(self):
        self.SongStats = {}
        self.ChestStats = {}
        self.PlayerDeaths = []
        self.MonsterDeaths = {}
        print self.PlayerDeaths
    def UpdateSongPerformance(self, SongName, Performance):
        if not self.SongStats.has_key(SongName):
            self.SongStats[SongName] = {}
            for Quality in HitQuality.AllQualities:
                self.SongStats[SongName][Quality] = 0
        for Quality in HitQuality.AllQualities:
            self.SongStats[SongName][Quality] += Performance[Quality]
        self.Save()
    def UpdateTrapPerformance(self, TrapName, Success):
        if not self.ChestStats.has_key(TrapName):
            self.ChestStats[TrapName] = [0,0]
        if Success:
            self.ChestStats[TrapName][0] += 1
        else:
            self.ChestStats[TrapName][1] += 1
        self.Save()
    def LogPlayerDeath(self, Player, CauseOfDeath):
        self.PlayerDeaths.append((Player.Name, Player.Level, Player.Species.Name, str(CauseOfDeath)))
    def LogMonsterDeath(self, Monster):
        if not self.MonsterDeaths.has_key(Monster.Species.Name):
            self.MonsterDeaths[Monster.Species.Name] = 0
        self.MonsterDeaths[Monster.Species.Name] += 1
    def ReportBetaStats(self):
        MemFile = cStringIO.StringIO()
        self.DumpToFile(MemFile)
        Str = ReportBetaStats(MemFile.getvalue())
        MemFile.close()
        return Str
    def DumpToFile(self, File):
        File.write("##########################\n#Super-secret Spy Stuff\n")
        File.write("#Chests\tType\tSuccesses\tFailures\n")
        for Key in self.ChestStats.keys():
            Stats = self.ChestStats[Key]
            File.write("Trap\t%s\t%d\t%d\n"%(Key, Stats[0], Stats[1]))
        File.write("#Songs\tName\tMiss\tPoor\tGood\tPerfect\n")
        for Key in self.SongStats.keys():
            Stats = self.SongStats[Key]
            File.write("Song\t%s\t%d\t%d\t%d\t%d\t\n"%(Key, Stats[HitQuality.Miss],
                                                     Stats[HitQuality.Poor],
                                                     Stats[HitQuality.Good],
                                                     Stats[HitQuality.Perfect]))
        File.write("##########\n#Unfortunate PC Deaths\n")
        File.write("#Name\tLevel\tClass\tCause\n")
        for Death in self.PlayerDeaths:
            File.write("%s\t%s\t%s\t%s\n"%Death)
        File.write("##########\n#Glorious Victories over Monsters\n")
        for (Name, Count) in self.MonsterDeaths.items():
            File.write("%s\t%s\n"%(Name, Count))
        File.write("##########\n#Current Party Events\n")
        for Flag in Global.Party.EventFlags.keys():
            File.write("Event\t%s\t%s\n"%(Flag, Global.Party.EventFlags[Flag]))
        File.write("##########\n#Key items\n")
        for Name in Global.Party.KeyItemFlags.keys():
            File.write("KeyItem\t%s\t%s\n"%(Name, Global.Party.KeyItemFlags[Name]))
        File.write("##########\n#Characters\tName\tLevel\tSTR\tDEX\tCON\tINT\tWIS\tCHA\n")
        for Player in Global.Party.Players:
            File.write("Character\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"%\
                       (Player.Name, Player.Species.Name,Player.Level,
                        Player.STR, Player.DEX, Player.CON,
                        Player.INT, Player.WIS, Player.CHA))
            
    def DebugPrint(self):
        self.DumpToFile(sys.stdout)
    def Save(self):
        File = open(UserDataFileName("BigBrother.dat"),"w")
        #cPickle.dump(self,File)
        pickle.dump(self,File)
        File.close()

Global.BigBrother = BigBrother()
# Load any existing BigBrother:
try:
    File = open(UserDataFileName("BigBrother.dat"),"r")
    Global.BigBrother = pickle.load(File) #cPickle.load(File)
    File.close()
except:
    #traceback.print_exc()
    pass
        
def GetTestParty():
    TheParty = Party()
    TheParty.X = 5
    TheParty.Y = 0
    ### UP
    Player = Critter.Player("Shinobi", Critter.Ninja) #Critter.Ninja)
    Player.Equip(Global.QuarterMaster.GetItem("Bamboo Stick"))
    Player.Equip(Global.QuarterMaster.GetItem("Tunic"))
    TheParty.AddPlayer(Player)
    ### DOWN
    Player = Critter.Player("Pius", Critter.Cleric) #Critter.Cleric)
    Player.Equip(Global.QuarterMaster.GetItem("Bamboo Stick")) 
    Player.Equip(Global.QuarterMaster.GetItem("Tunic"))
    TheParty.AddPlayer(Player)
    ### LEFT
    Player = Critter.Player("Biff", Critter.Fighter) #Critter.Fighter)
    Player.Equip(Global.QuarterMaster.GetItem("Bamboo Stick"))
    Player.Equip(Global.QuarterMaster.GetItem("Tunic"))
    TheParty.AddPlayer(Player)
    ### RIGHT
    Player = Critter.Player("Schmendrick", Critter.Mage) #Critter.Mage)
    Player.Equip(Global.QuarterMaster.GetItem("Bamboo Stick"))
    Player.Equip(Global.QuarterMaster.GetItem("Tunic"))
    TheParty.AddPlayer(Player)
        
    TheParty.Gold = 100 # Poverty!  This should be enough to stay at the inn 1.5 times :)
    ##TheParty.Items["phoenix down"] = 3 # These sell for too much at the store :/

    PumpingDungeonLevel = 0 
    PumpingPlayerLevel = 1
    for (ItemName, Item) in Global.QuarterMaster.Items.items():
        Include = 0
        for Level in range(1, PumpingDungeonLevel):
            if Level in Item.Level:
                Include = 1
        if Include:
            TheParty.Items[ItemName] = 1

    TheParty.Items["potion"] = 5
    TheParty.Items["escapipe"] = 1
            
    for Player in TheParty.Players:
        for Level in range(2, PumpingPlayerLevel):
            Player.LevelUp()
            Player.STR += 1

    Global.Party = TheParty
    return TheParty

def GetNewParty():
    return GetTestParty()