import sys
import time
import pygame

pygame.mixer.pre_init(44100, -16, 8, 1024)
pygame.init()
pygame.mixer.init()
Surface = pygame.display.set_mode((800,600))

##C:\Tendrils\Music\BGM\1\dkc-coral.it
##C:\Tendrils\Music\BGM\6\ff6-esper.it
##C:\Tendrils\Music\BGM\6\smw-ghosthouse.it

#pygame.mixer.music.load(r"C:\Tendrils\Music\BGM\WARRIOR.S3M")
##C:\Tendrils\Music\BGM\WARRIOR.S3M

#pygame.mixer.music.rewind()
#pygame.mixer.music.play(-1)
Sound = pygame.mixer.Sound(r"c:\tendrils\sounds\defeat.wav")
Sound.play()
print "Playing..."
while 1:
    time.sleep(0.5)
    print pygame.mixer.music.get_pos(), pygame.mixer.get_busy()
    