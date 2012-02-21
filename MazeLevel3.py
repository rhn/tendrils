"""
Special maze locations for level 3.
"""
from Utils import *
from Constants import *
import Screen
import Tendrils
import Resources
import Global
import MazeRooms
import ChestScreen
import Music
import Maze

def L3DoCakeBeast(Screen, Maze, X, Y):
    # If he's already gone:
    if Global.Party.EventFlags.get("L2FedCakeBeast"):
        return 1
    MeetingString = "A misshapen greenish monster with arms as thick as tree-trunks is here.  <CN:BRIGHTRED>NO YOU PASS!</C> it booms, \
smiling a toothy grin.  A moment later, its stomach growls with alarming volume.  <CN:BRIGHTRED>SO...HUNGRY!  WANT...COOKIE!</C> the \
beast says, and slouches against the wall."    
    # If they can feed him already:
    if Global.Party.KeyItemFlags.get("Shortbread"):
        CookieString = "The beast catches a whiff of your shortbread, he begins sniffing \
eagerly at the musty dungeon air.  <CN:BRIGHTRED>COOKIE?</C> it asks.  You toss it the shortbread, which it swallows in one \
noisy gulp.  The green monster laughs, and dashes off down the corridor, knocking out chunks of wall with its unholy frolicking.\n\n\
It appears the way onward is clear now...\n\n<CN:GREY>(You have passed the dreaded <CN:PURPLE>Wumpus<CN:GREY>!)"
        if Global.Party.EventFlags.get("L2MetCakeBeast"):
            Str = CookieString
        else:
            Str = MeetingString+"\n\n"+CookieString
        Global.App.ShowNewDialog(Str)
        Global.Party.EventFlags["L2FedCakeBeast"] = 1
        Global.Party.KeyItemFlags["Shortbread"] = 0
        return 1
    Str = MeetingString+"\n\nHe's too big to fight, so you decide to leave him be."
    Global.App.ShowNewDialog(Str)
    return 0

def L3DoTetrisBattle(Screen, Maze, X, Y):
    "A random battle, with a chest, playing the Tetris music."
    Maze.Rooms[(X,Y)] = 0 # once only
    Global.Party.GetNextRandomBattle() # reset time-to-encounter
    Monsters = Global.Bestiary.GetRandomEncounter(Global.Maze.Level)
    Booty = Global.QuarterMaster.GetRandomBooty(Global.Maze.Level)
    Global.App.BeginBattle(Monsters, Booty, SongFileName = "Tetris.xm", CanFlee = 1)
    return 1
    
def DoElevator(Screen, Maze, X, Y):
    if Global.Party.KeyItemFlags.get("Blue Ribbon"):
        Global.Party.X = X
        Global.Party.Y = Y
        Screen.RenderMaze()
        Screen.Redraw()
        Str = "A sign on the wall reads:\n\n<CENTER><CN:ORANGE>Express Elevator</c>\n\nOn the wall a <CN:BRIGHTRED>big red button</c>.\n\nPush it?"
        Global.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback = lambda S=Screen:TakeElevator(S))
        return 1
    MazeRooms.DoSign(Screen, Maze, X, Y, "A sign on the wall reads:\n\n<CENTER><CN:ORANGE>Express Elevator</c>\n<CN:RED>Unauthorized operation prohibited</c></CENTER>\n\nThere is also a big <CN:BRIGHTRED>red</C> button here that doesn't do anything.")
    return 1

def TakeElevator(S):
  Resources.PlayStandardSound("MegamanNoise.wav")
  Maze.GoToMazeLevel(7)
  Global.Party.X = 21
  Global.Party.Y = 18
  S.RenderMaze(1)
  

def L3DoShortbreadShop(Screen, Maze, X, Y):
    Global.App.DoNPC("Pastry Chef")
    return 0

def DoBook(Screen, Maze, X, Y, BookName):
    Text = Books.get(BookName, None)
    if not Text:
        return 1
    Str = "You leaf through one of the books in this section:\n\n"+Text
    Global.App.ShowNewDialog(Str)
    return 1

def L3DoSilence(Screen, Maze, X, Y, Sign = ""):
    # The library "shushes" players:
    SilenceThese = []
    for Player in Global.Party.Players:
        # Find everyone who we can silence:
        if Player.IsAlive() and not Player.HasPerk("Silence Immune"):
            # If they're not silenced, add them to the list (for the dialog).  
            if not Player.HasPerk("Silence"):
                SilenceThese.append(Player)
            else:
                # They're silent already - "top off" the dosage
                Player.Perks["Silence"] = max(Player.Perks["Silence"], 500)
                
    for Player in SilenceThese: #Global.Party.Players:
        Player.Perks["Silence"] = 500
    if SilenceThese:
        Global.Party.X = X
        Global.Party.Y = Y
        Screen.Redraw()
        Str = "A ghostly voice whispers:\n<CN:GREY>Shush!  Please be quiet in the library!\n"
        for Player in SilenceThese:
            Str += "\n<CN:GREEN>%s</C> has been silenced."%Player.Name
        Global.App.ShowNewDialog(Str)
    if Sign:
        Sign = "<CN:GREY>Bookshelves stretch into the distance.\nA sign on the shelves reads:</C>\n\n<CENTER>"+Sign
        MazeRooms.DoSign(Screen, Maze, X, Y, Sign)
    return 1
    

def DoWarpToTown(S, M, X, Y):
    Global.Party.X = 9
    Global.Party.Y = 28
    #Global.Party.Z = 1
    Maze.GoToMazeLevel(1)
    Global.Party.Heading = Directions.Up
    #Global.Maze.Level = 1
    #Global.Maze.Load()
    S.RenderMaze(1)
    S.Redraw()
    Resources.PlayStandardSound("MegamanNoise.wav")

def DoL3QuadMiniBoss(S, M, X, Y):
    "The first room holds one monster, the next two, the next three, and the last four!"
    BattlesFought = Global.Party.EventFlags.get("L3QuadBoss", 0)
    if BattlesFought == 4:
      return 1 # all cleaned out
    # Dun-dun-dun!  It's the first boss battle!
    if BattlesFought == 3:
      # Good treasure!  Note: NOT in a chest.
      Booty = ({"Belmont's Cross":1}, {"Gold":1000}, 0)
    else:
      # Crummy treasure!
      Booty = ({}, {"Gold":(BattlesFought + 1)*100}, 1)
    MonsterRow = []
    for Index in range(BattlesFought + 1):
      MonsterRow.append(Global.Bestiary.GetCritter("Joust Knight"))
    Monsters = [MonsterRow]
    Global.Party.EventFlags["L3QuadBoss"] = BattlesFought + 1
    Global.App.BeginBattle(Monsters, Booty, CanFlee = 0)
    return 1
    
def DoL3Vault(S, M, X, Y):
    if Global.Party.EventFlags.get("L3Vault"):
      return 1
    if Global.Party.X == X:
      return 1
    # Display a dialog for entering a 5-digit combo:
    Str = "You come upon a sturdy, ominous door made of blackened iron.  There are five dials on its side, apparently forming a combination lock.\nHow will you set the dials?"
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    Global.App.ShowWordEntryDialog(Str, L3VaultEntry, 5, "0123456789")
    return 0

def L3VaultEntry(Text):
  if Text == "":
    return
  if Text != "84564":
    Global.App.ShowNewDialog("The vault door remains shut.")
    return
  Str = "The lock mechanism clicks loudly, and the door swings slowly open!"
  Music.PauseSong()
  Resources.PlayStandardSound("MegaHappy.wav")
  Global.Party.EventFlags["L3Vault"] = 1
  Global.App.ShowNewDialog(Str, Callback = L3VaultDone)
  

def L3VaultDone():
  Music.UnpauseSong()
  ChestItems = {"Regen Ring":1,"Pyros Cape":1,"Angel Ring":1}
  ChestSpecial  = {"gold":2000}
  Str = "You quickly liberate the vault's contents.\n\n"
  ChestScreen.GetTreasureChestStuff(ChestItems, ChestSpecial, 2, Str)

def DoTrapRoom(S,M,X,Y):
    # Note: Comes from 1st quest ending of Ghosts and Goblins for NES, a true bastard among games.
    MazeRooms.DoSign(S, M, X, Y, """<CENTER>THIS ROOM IS AN ILLUSION AND
IS A TRAP DEVISUT BY SATAN
GO AHEAD DAUNTLESSLY!
MAKE RAPID PROGRES!""")
    return 1
    

def DoL3Boss(S,M,X,Y):
    if Global.Party.KilledBosses.get((3, "Necromancers")):
        return 1
    Monsters = [[Global.Bestiary.GetCritter("Necromancer"),
                 Global.Bestiary.GetCritter("Necromancer"),
                 Global.Bestiary.GetCritter("Necromancer"),]] 
    Booty = ({"Potion":10, "Phoenix Down":5}, {}, 0)
    Global.App.BeginBattle(Monsters, Booty, BossBattleName = "Necromancers", SongFileName = "SOR.mp3", CanFlee = 0)
    Global.App.ScreenStack[-1].Redraw()
    Str = "<CENTER><CN:PURPLE>Necromancers!</C>\n\nThe wizards cast a spell of <CN:ORANGE>Confusion</C>!\n\n<CENTER><CN:BRIGHTRED>All arrows are reversed!</C>\n(Hit <CN:GREEN>LEFT</C> when arrows point <CN:GREEN>RIGHT</C>!)"
    Global.App.ShowNewDialog(Str)
    return 1
    

def DoGetShuriken(S,M,X,Y):
    if Global.Party.EventFlags.get("Lev3Shuriken"):
        return 1
    Global.Party.X = X
    Global.Party.Y = Y
    S.RenderMaze()
    S.Redraw()
    Item = Global.QuarterMaster.GetItem("shuriken")
    Global.Party.GetItem(Item)
    Global.Party.GetItem(Item)
    Global.Party.GetItem(Item)
    #Global.Party.Inventory["Shuriken"] = Global.Party.Inventory.get("Shuriken", 0) + 5
    Str = """Hooray!  A nice pile of ninja stars!  You remove them from the dead Samurai corpse they happen \
to be stuck in, and bring them along.

<CN:YELLOW>[You got: Shuriken]</CN>"""
    Global.App.ShowNewDialog(Str)
    Global.Party.EventFlags["Lev3Shuriken"] = 1
      
                     
EnterRoomRoutines = {201:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """There is a plaque set into the wall \
here:\n\n<CENTER>Our Dungeon Heritage\nThese three statues have guarded this level since time immemorial.  \
Of the three guardians, one always tells the truth, one always lies, and one sometimes lies and sometimes tells the truth.  \
At least one of the doors leads to a pit, so do be careful which door you choose.\n\n-----Tendrils Tourism Bureau"""),
                     202:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """A statue of a scowling centaur stands a silent \
vigil here.  At the base of the statue are carved these words:\n\n<CN:RED>AT LEAST ONE OF THE OTHER DOORS IS SAFE.</C>"""),
                     203:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """A statue of a catlike woman stands a silent \
vigil here.  At the base of the statue are carved these words:\n\n<CN:RED>THERE ARE AS MANY LIES AS THERE ARE PITS.</C>"""),
                     204:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, """A statue of a half-serpent is coiled here.  \
At the base of the statue are carved these words:\n\n<CN:RED>THERE IS ONLY ONE PIT.</C>"""),
                     205:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "Long march!"),
                     206:L3DoCakeBeast,
                     207:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "A dungeon's dark..."),
                     208:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "When it's not lit..."),
                     209:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "Watch out or you'll..."),
                     210:DoElevator,
                     211:lambda Screen,Maze,X,Y,I ={"Bombs":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     212:lambda Screen,Maze,X,Y,I ={"Pyros Cape":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     213:lambda Screen,Maze,X,Y,I ={"Angel Ring":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     214:lambda Screen,Maze,X,Y,I ={"King Tycoon's Helm":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     215:lambda Screen,Maze,X,Y,I ={"Speed Boots":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     216:L3DoTetrisBattle,
                     217:L3DoShortbreadShop,
                     218:L3DoSilence,
                     219:lambda Screen,Maze,X,Y,I ={"Regen Ring":1},S={}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     220:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"HISTORY"),
                     221:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"ASTRONOMY"),
                     222:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"LITERATURE A-N"),
                     223:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"LITERATURE O-Z"),
                     224:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"METEOROLOGY"),
                     225:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"LINGUISTICS"),
                     226:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"MUSIC"),
                     227:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"RELIGION"),
                     238:lambda S, M, X, Y:L3DoSilence(S,M,X,Y,"COOKING"),
                     # Religion section: A cleric spell
                     228:lambda Screen,Maze,X,Y,I ={},S={"Cleric:3":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     # Meteorology section: Blizzard spell
                     229:lambda Screen,Maze,X,Y,I ={},S={"Mage:3":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     230:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "Cathedral Library\n\n(Quiet Please!)"),                     
                     # History:
                     231:lambda S,M,X,Y:DoBook(S,M,X,Y,"History"),
                     232:lambda S,M,X,Y:DoBook(S,M,X,Y,"Astronomy"),
                     233:lambda S,M,X,Y:DoBook(S,M,X,Y,"LiteratureAN"),
                     234:lambda S,M,X,Y:DoBook(S,M,X,Y,"LiteratureOZ"),
                     235:lambda S,M,X,Y:DoBook(S,M,X,Y,"Linguistics"),
                     236:DoWarpToTown,
                     237:lambda S,M,X,Y:DoBook(S,M,X,Y,"Music"),
                     239:lambda Screen,Maze,X,Y,I ={},S={"Summoner:2":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     240:lambda Screen,Maze,X,Y: MazeRooms.DoSign(Screen, Maze, X, Y, "Shelving Area\n\nAuthorized Personnel Only"),
                     241:lambda S,M,X,Y:MazeRooms.DoSign(S, M, X, Y, """You find a desk overflowing with paperwork.  Among the clutter, you notice \
a sheet labeled <CN:BRIGHTRED>TRIBUTE COLLECTION</C>, and what looks like a sum:
<CENTER><IMG:TempleSum.png></CENTER>
...Hmm.  Looks like the necromancers write their digits differently."""),
                     242:DoL3Vault,
                     243:DoL3QuadMiniBoss,
                     244:lambda S,M,X,Y:MazeRooms.DoSign(S, M, X, Y, "A note is pinned to the wall here:\n\n\
<CN:red>Zoltan - \n\nI have changed the vault combination.  The new combination is \
the same as last year's total tribute."),
                     245:lambda Screen,Maze,X,Y,I ={},S={"Cleric:4":1}: MazeRooms.DoChest(Screen, Maze, X, Y, I, S),
                     246:DoTrapRoom,
                     247:DoL3Boss,
                     248:DoGetShuriken,
                    }

Books = {
    "History":"""<CENTER><CN:RED>Samurai Spirits</C>

Once there were a man
Who wanted to make his skill ultimate
Because of his dark past
It's no surprise
He was involved with the troubles.""",
    "Astronomy":"""From: Captain Avenger
      of the ISS Newhope
To:   All other Starship Captains

The way to stop the suns from flaring - killing all life in
the systems - is as follows:

<CN:RED>1</C>. You must use a black egg to destroy the Uhlek Brain World.
   If you do not, the Uhlek will not let you collect the
   Crystal Cone.  They will slaughter you and your crew with
   plasma bolts.  Do not feel guilty about destroying this
   planet.  The Uhlek are bloodthirsty killers.

<CN:RED>2</C>. You must collect the Crystal Orb to nullify the defenses
   of the Crystal Planet so you can land on it. The Crystal
   Orb is found at 132, 165.
   
<CN:RED>3</C>. You must collect the Crystal Cone to identify the control
   nexus of the planet. The Crystal Cone is found in the
   system at 20, 198 on the first planet.

<CN:YELLOW>(...The book continues in this vein for some time.)</C>
""",
    "LiteratureAN":"""<CENTER><CN:RED>[ <CN:BRIGHTRED>IN AD 2101, WAR WAS BEGINNING <CN:RED>]<CN:WHITE></CENTER>
    
<CN:GREEN>Captain</C>: What happen?
<CN:PURPLE>Mechanic</C>: Someone set up us the bomb
<CN:BLUE>Operator</C>: We get signal
<CN:GREEN>Captain</C>: What!
<CN:BLUE>Operator</C>: Main screen turn on.
 
<CN:GREEN>Captain</C>: It's you!!
<CN:ORANGE>Cats</C>: How are you gentlemen!!
<CN:ORANGE>Cats</C>: All your base are belong to us
<CN:ORANGE>Cats</C>: You are on the way to destruction
 
<CN:GREEN>Captain</C>: What you say?
<CN:ORANGE>Cats</C>: You have no chance to survive make your time
<CN:ORANGE>Cats</C>: Ha ha ha ....
<CN:BLUE>Operator</C>: Captain!!
 
<CN:GREEN>Captain</C>: Take off every 'ZIG'!!
<CN:GREEN>Captain</C>: Move 'ZIG'.
<CN:GREEN>Captain</C>: For great justice. 
""",
    "LiteratureOZ":"""<CN:YELLOW>>GNOME, BUILD A LADDER</C>
"I'd be glad to, but not for free!"

<CN:YELLOW>>GIVE THE JEWELED MONKEY WRENCH TO THE GNOME</C>
The gnome examines the jeweled monkey wrench carefully. "Thank you," he exclaims, adding it to his collection of tools.

<CN:YELLOW>>GNOME, BUILD A LADDER</C>
"Oh, yes, your ladder. Unfortunately, I have no lumber."

<CN:YELLOW>>GIVE THE LUMBER TO THE GNOME</C>
The gnome accepts the supply of lumber.

<CN:YELLOW>>GNOME, BUILD LADDER</C>
"Darn it! I'm fresh out of nails."

<CN:YELLOW>>GIVE NAILS</C>
(to the gnome)
The gnome accepts the bunch of nails.

<CN:YELLOW>>GIVE THE LAMP TO THE GNOME</C>
The gnome attempts to build a beautiful set of kitchen cabinets out of the lamp. Finally, he gives up and hands it back to you.

<CN:YELLOW>>GNOME, BUILD LADDER</C>
The gnome grumbles but constructs a handsome wodden ladder. He admires his handiwork and hands you the ladder.

<CN:YELLOW>>PUT THE LADER THROUGH THE HOLE</C>
I don't know the word "lader".

<CN:YELLOW>>OOPS LADDER</C>
The ladder is now resting against the rim of the hole.

<CN:YELLOW>>UP</C>
You're carrying too much to climb a ladder.
""",
    "Linguistics":"""(this book appears to be written in a strange tongue)

BMQI IMQBMI,
JWMIM HN Q NMZIMJ BEEI PMQIXA.  GE MQNJ JTHZM, PEIJW JTHZM, QPB TMNJ JWIHZM. \
JWM PEIJW TQDD THDD EYMP, IMCMQDHPG Q YEIJQD JE JWM NVIRQZM.  YDMQNM ZDENM \
JWM BEEI TWMP AEV GE JWIEVGW.  HR JWM WMQB QXXEJ BHNZECMIMB JWQJ WHN YIHMNJN \
TMIM NPMQOHPG ERR JE GMJ BIVPO, WM TEVDB XM CMIA QPGIA!
  --KASEL, BQIO YIHMNJ
""",
    }

##DEAR READER,
##THERE IS A SECRET DOOR NEARBY.  GO EAST TWICE, NORTH TWICE, AND WEST THRICE.
##THE NORTH WALL WILL OPEN, REVEALING A PORTAL TO THE SURFACE.  PLEASE CLOSE
##THE DOOR WHEN YOU GO THROUGH.  IF THE HEAD ABBOT DISCOVERED THAT HIS PRIESTS
##WERE SNEAKING OFF TO GET DRUNK, HE WOULD BE VERY ANGRY!
##  --ZYMOX, THE DARK PRIEST

if __name__=="__main__":
    import string

    Letters = "abcdefghijklmnopqrstuvwxyz"
    RandomLetters = list(Letters)
    random.shuffle(RandomLetters)
    RandomLetters = string.join(RandomLetters, "")
    Bob = string.maketrans(Letters, RandomLetters)
    print string.translate(Books["Linguistics"].lower(), Bob).upper()

