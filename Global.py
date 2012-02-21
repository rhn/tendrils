# Various global variables, to make it easier for classes to talk to each other.
# Almost everybody talks to Global.Party to access the players and their inventory.
# Many screens talk to App.  The other variables are used less often.

Version = "20071125"

# The battle screen (as defined in BattleScreen.py), if it's up:
BattleScreen = None
QueueSong = None

# The bestiary (as defined in Critter.py), which can provide monster
# instances:
Bestiary = None

# The QuarterMaster (as defined in ItemPanel.py), which produces item
# instances:
QuarterMaster = None

# The application object (as defined in Tendrils.py); responsible for opening
# new screens.
App = None

# An empty image (instance of pygame.Surface).  Useful for sprites that turn invisible.
NullImage = None

# A spellbook (as defined in Magic.py), holding all spell definitions
Spellbook = None

# A maze (as defined in Maze.py); the current dungeon level
Maze = None

# The maze screen (as defined in MazeScreen.py), if it's up:
MazeScreen  = None

# The party object (as defined in Party.py)
Party = None

# The stats object (as defined in Party.py), for beta testing
BigBrother = None

# The MusicLibrary object (as defined in Music.py).  Lists all the songs we have.
MusicLibrary = None

# The MemoryCard object (as defined in MemoryCard.py).  Global, cross-party flags.
MemoryCard = None

# List indicating the buttons that are down now
JoyButtons = [0]*50

CurrentSong = None