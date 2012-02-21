"""
Options for playing Tendrils - key settings, etc.
"""
from Utils import *
import pickle

# THE GAMEPAD KEYS!
KEY_DEBUG = 47
KEY_ATTACK = "Attack"
KEY_MOVE = "Move"
KEY_SPACE = 32
KEY_ENTER = 13
KEY_HELP = "Help" 
KEY_SAVE = "Quicksave" 
KEY_LOAD = "Quickload" 
KEY_INVENTORY = "Inventory"
KEY_RETINUE = "Status"
KEY_BASE = "Base command"
KEY_LEFT_SHIFT = 304
KEY_RIGHT_SHIFT = 303
KEY_AUTOFIGHT_ON = "Autofight on"
KEY_AUTOFIGHT_OFF = "Autofight off"
KEY_USE = "Use"


KEY_MAP_UP = "Scroll map up" 
KEY_MAP_DOWN = "Scroll map down" 
KEY_MAP_LEFT = "Scroll map left" 
KEY_MAP_RIGHT = "Scroll map right" 

KEY_UP = "Up"  # number-pad keys
KEY_DOWN = "Down" 
KEY_LEFT = "Left" 
KEY_RIGHT = "Right"

KEY_A_BUTTON = "Joypad A/Yes" #b - DO things
KEY_B_BUTTON = "Joypad B/No" #v - CANCEL things
KEY_X_BUTTON = "Joypad X" #g - Options A
KEY_Y_BUTTON = "Joypad Y" #f - Options B
KEY_L_BUTTON = "Joypad Left-index" #h - Scroll left/up
KEY_R_BUTTON = "Joypad Right-index" #n - Scroll right/down
KEY_START_BUTTON = "Joypad START" # enter
KEY_SELECT_BUTTON = "Joypad SELECT" # space
KEY_END_TURN = "End turn"

GamepadKeys = [KEY_UP,KEY_DOWN,KEY_LEFT,KEY_RIGHT,KEY_A_BUTTON,KEY_B_BUTTON,KEY_X_BUTTON,KEY_Y_BUTTON,
               KEY_L_BUTTON,KEY_R_BUTTON,KEY_START_BUTTON,KEY_SELECT_BUTTON]

StandardKeys = [KEY_ATTACK,KEY_MOVE,KEY_END_TURN,KEY_INVENTORY,KEY_USE,KEY_RETINUE,KEY_BASE,
                KEY_AUTOFIGHT_ON,KEY_AUTOFIGHT_OFF,
                KEY_HELP,KEY_SAVE,KEY_LOAD]
SpecialKeys = [KEY_MAP_UP,KEY_MAP_DOWN,KEY_MAP_LEFT,KEY_MAP_RIGHT]
KEY_DISPLAY_LISTING = [GamepadKeys,StandardKeys,SpecialKeys]

DEFAULT_KEY_DEFINITIONS ={KEY_ATTACK:97,KEY_MOVE:109,KEY_AUTOFIGHT_ON:114,KEY_AUTOFIGHT_OFF:116,
 KEY_HELP:272,KEY_SAVE:283,KEY_LOAD:284,KEY_INVENTORY:105,KEY_RETINUE:99,
 KEY_MAP_UP:273,KEY_MAP_DOWN:274,KEY_MAP_LEFT:276,KEY_MAP_RIGHT:275,
 KEY_UP:264,KEY_DOWN:258,KEY_LEFT:260,KEY_RIGHT:262,KEY_A_BUTTON:98,KEY_B_BUTTON:118,
 KEY_X_BUTTON:103,KEY_Y_BUTTON:102,KEY_L_BUTTON:104,KEY_R_BUTTON:110,
 KEY_START_BUTTON:13,KEY_SELECT_BUTTON:32,KEY_END_TURN:32,KEY_USE:117,
 KEY_BASE:98
}

def IsShiftPressed():
    KeysPressed = pygame.key.get_pressed()
    if KeysPressed[KEY_LEFT_SHIFT] or KeysPressed[KEY_RIGHT_SHIFT]:
        return 1
    return 0
    