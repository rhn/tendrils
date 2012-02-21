"""
Constants that are used all over Tendrils
"""
import os
import sys
Version = "20110130" #%%% Update this when you build a package!

LogFileName = "Tendrils.log"

# Take note: Psyco has some BAD BEHAVIOR in conjunction with Tendrils, at least on my WinXP box.
# If you do psyco.full(), you get good speed without having to pick and choose functions...HOWEVER!
# A segmentation fault occurs when cycling through sliding block puzzles.  Where?  Somewhere in a call
# to pygame.draw.rect()  Why?  I do not know.  After
# many hours spent building debug versions of pygame, and SDL, and all the sub-projects which are
# separate from SDL for no damn reason...I was never able to reproduce the error while stepping through
# the debugger.  (I could get the crash with debug CODE, but if I stepped through pygame.draw.rect(),
# there was no crash!)
#
# At any rate: I don't entirely trust psyco, but the speedup is nice, so for now, we default to using
# psyco on a collection of functions.  If that leads to crashes, at least the workaround is
# easy: set PSYCO_ON to 0.
#
# -- swt

PSYCO_ON = 0
if PSYCO_ON:
    try:
        import psyco
    except:
        print "*Note: Psyco optimization library NOT loaded.  (Please install psyco for improved speed)"
        PSYCO_ON = 0
        # But we can still run :)

KeyRepeatDelay = 28
MaxKeyRepeatTime = 10

# The event-ID that's raised when a song ends.  (We determine
# this, so we just picked an arbitrary unused ID)
SongOverEvent = 133

class ButtonGroup:
    Ok = "Ok"
    YesNo = "YesNo"
    PickPlayer = "PickPlayer"

class AnimationType:
    Stand = "Stand"
    Attack = "Attack"
    Ouch = "Ouch"
    Block = "Block"
    Death = "Death"
    AllTypes = [Stand, Attack, Ouch, Block, Death]

class HitQuality:
    "Constants: How good a 'hit' the user got on an arrow (which affects how well melee/magic works)"
    Miss = 0
    Poor = 1
    Good = 2
    Perfect = 3
    FreezeDenied = -1
    FreezeOk = 10
    # You can miss by pressing an arrow key when the arrow is this many ticks from impact:
    MaxMissableTicks = 400
    # Boundaries of hit quality levels, in ticks:
    MaxPoorTicks = 190
    MaxGoodTicks = 110
    MaxPerfectTicks = 50
    # If the user gets a Perfect on a defense arrow, the monster gets a Miss for its swing:
    ReversedQuality = {Miss: Perfect, Poor: Good, Good: Poor, Perfect: Miss}
    QualityNames = ["Miss", "Poor", "Good", "Perfect"]
    AllQualities = [Miss, Poor, Good, Perfect]

class EquipSlots:
    "Constants for equipment slots"
    Weapon = 0
    Body = 1
    Head = 2
    Arms = 3
    Feet = 4
    Relic = 5
    Slots = (Weapon, Body, Head, Arms, Feet, Relic)
    SlotNames = ["Weapon", "Body", "Head", "Arms", "Feet", "Relic"]

class Fonts:
    "Available font names"
    PressStart = "PrStart.ttf"
    Zelda = "RetGanon.ttf"
    Saturn = "saturno.ttf"

class Paths:
    "Relative paths to files"
    MusicBattle = os.path.join("Music","Battle")
    MusicBGM = os.path.join("Music","BGM")
    Images = "Images"
    ImagesTraps = os.path.join("Images","Traps")
    ImagesMisc = os.path.join("Images", "Misc")
    ImagesPlayer = os.path.join("Images", "Player")
    ImagesBackground = os.path.join("Images", "Background")
    ImagesMaze = os.path.join("Images","Maze")
    ImagesMagic = os.path.join("Images","Magic")
    ImagesCritter = os.path.join("Images","Critter")
    ImagesProjectile = os.path.join("Images","Projectile")
    ImagesItem = os.path.join("Images","Item")
    ImagesNPC = os.path.join("Images","NPC")
    ImagesWalls = os.path.join("Images","Walls")
    Fonts = "Fonts"

def IsEXE():
    if len(sys.argv)<1:
        return 1
    Extension = os.path.split(sys.argv[0])[1]
    Extension = os.path.splitext(Extension)[1].lower()
    if Extension.lower() not in (".py", ".pyc", ".pyo"):
        return 1
    return 0

class Keystrokes:
    Up = [264, 273]
    Down = [258, 274]
    Left = [260, 276]
    Right = [262, 275]
    ##Debug = 47
    Enter = 13

# The debug key isn't available from Tendrils.exe; only from the python code.
if IsEXE():
    Keystrokes.Debug = -1
else:
    Keystrokes.Debug = 47

class Directions:
    "Constants for the four directions"
    Up = 1
    Down = 2
    Left = 3
    Right = 4
    NW = 5
    NE = 6
    SW = 7
    SE = 8
    AllDirections = [Up,Down,Left,Right,NW,NE,SW,SE]

DirectionNames = {Directions.Up:"Up",
                  Directions.Down:"Down",
                  Directions.Left:"Left",
                  Directions.Right:"Right",
                  Directions.NW:"NW",
                  Directions.NE:"NE",
                  Directions.SW:"SW",
                  Directions.SE:"SE",
                  }
    
OppositeDirections = {Directions.Up:Directions.Down,
                      Directions.Down:Directions.Up,
                      Directions.Left:Directions.Right,
                      Directions.Right:Directions.Left,
                      Directions.NW:Directions.SE,
                      Directions.NE:Directions.SW,
                      Directions.SW:Directions.NE,
                      Directions.SE:Directions.NW,
                      }
SubDirections = {5:(1,3), 6:(1,4), 7:(2,3), 8:(2,4)}

class Colors:
    "Various handy colors.  TODO: Use aliases like 'mana' for colors, for easier color scheme harmony"
    White = (255,255,255)
    Black = (0,0,0)
    AlmostBlack = (11,11,11) # But NOT TRANSPARENT :)
    LightGrey = (200,200,200)
    MediumGrey = (100,100,100)
    Grey = (50,50,50)
    Red = (255,0,0)    
    Green = (0,255,0)
    DarkGreen = (0,125,0)
    Yellow = (255, 255, 0)
    Blue = (0,0,255)
    DarkBlue = (0, 0, 125)
    Purple = (160, 31, 231)
    Orange = (249, 159, 43)
    

# Keep a dictionary of perks handy, for validation:
AllPerks = {"Poison Immune":1, "Poison Strike":1,
            "Silence Immune":1, "Silence Strike":1,
            "Sleep Immune":1, "Sleep Strike":1,
            "Paralysis Immune":1, "Paralysis Strike":1,
            "Stoning Immune":1, "Stoning Strike":1,
            "Undead":1,
            "Regen":1, "Recovery":1, "Haste":1,
            "Resist Fire":1, "Resist Ice":1,
            "X-ray Vision":1,
            "Fire Strike":1, "Cold Strike":1, "Lightning Strike":1,
            "Resist Fire":1, "Resist Cold":1, "Resist Lightning":1,
            "Vulnerable Fire":1, "Vulnerable Cold":1, "Vulnerable Lightning":1,
            
            }
class SongType:
    Battle = "Battle"
    Sting = "Sting"
    Maze = "Maze"
    BGM = "Misc"
    Blocks = "Blocks"

