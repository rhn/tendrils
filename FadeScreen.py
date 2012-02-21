"""
Fade-to-black screen.  This is more of an effect than an actual screen, but it's useful
for when the player spends the night at the inn.  (Note to pygame novices: We don't update
our alpha on every tick, because that is VERY slow, ESPECIALLY on most laptops; we update
the alpha in a chunk every few ticks)
"""

from Utils import *
from Constants import *
import Screen
import MessagePanel

AlphaDownSize = 16
AlphaUpSize = 20

class FadeScreen(Screen.TendrilsScreen):
    MaxTick = 10
    def __init__(self, App, FadeOutScreen, FadeInScreen, DarkPause = 0):
        Screen.TendrilsScreen.__init__(self,App)
        # MINOR MAGIC to make the underlying stuff show:
        self.FadeOutScreen = FadeOutScreen
        self.FadeInScreen = FadeInScreen
        self.BackgroundSurface = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.BackgroundSurface.fill(Colors.Black)
        self.FadeInSurface = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.FadeInSurface.blit(FadeInScreen.Surface, (0,0))
        #self.BackgroundSurface.fill(Colors.Black)
        BigBiff = pygame.Surface((self.Surface.get_width(), self.Surface.get_height()))
        self.Alpha = 255
        self.Tick = self.MaxTick
        self.PauseTimer = DarkPause
        BigBiff.set_alpha(self.Alpha)
        self.AlphaDir = -AlphaDownSize
        BigBiff.blit(self.App.BackgroundSurface,(0,0))
        BigBiff.blit(self.App.Surface,(0,0))
        self.BigSprite = GenericImageSprite(BigBiff, 0, 0)
        self.AddBackgroundSprite(self.BigSprite)
    def RedrawBackground(self):
        "Redraw our background - note that we do NOT erase the blitted stuff (from the screen behind us)"
        self.BackgroundSurface.fill(Colors.Black)
        self.BackgroundSprites.draw(self.BackgroundSurface)
    def Update(self):
        self.Tick -= 1
        if self.Tick <= 0:
            self.Tick = self.MaxTick
            self.Alpha += self.AlphaDir
            self.BigSprite.image.set_alpha(self.Alpha)
            Dirty(self.BigSprite.rect)
            if (self.Alpha <= 0):
                self.PauseTimer -= 1
                ##print self.PauseTimer
                if self.PauseTimer <= 0:
                    self.BigSprite.image.fill(Colors.Green)
                    self.BigSprite.image.blit(self.FadeInSurface,(0,0))
                    #self.BigSprite.image.blit(self.FadeInScreen.Surface, (0,0))
                    self.Alpha = 1
                    self.AlphaDir = AlphaUpSize
            if (self.Alpha >= 255):
                self.App.PopScreen(self)
            self.Redraw()
            