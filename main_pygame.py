print("Importante, hacer pip install pygame antes...")
print("Parar cerrar, ESC y luego CTRL+c")
import sys
import threading
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame

from pygame.locals import *
import pyglet

WAVEFILE_NAME = "music/music.wav"
WAVEFILE_NAME_REVERSE = "music/music_reversed.wav"

class Player:

    def __init__(self):
        self.image = pygame.image.load('imagenes/player.png').convert()
        self.x = 0
        self.y = 0

    def update(self, dt):
        self.x += 100 * dt

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


def play_music():
    song = pyglet.media.load(WAVEFILE_NAME)
    reversed_song = pyglet.media.load(WAVEFILE_NAME_REVERSE)
    music_player.queue(song)
    music_player.loop = True
    player_reverse.queue(reversed_song)
    player_reverse.loop = True

music_player = pyglet.media.Player()
player_reverse = pyglet.media.Player()
window = None

def music_thread():
    global window
    window = pyglet.window.Window(100, 100, "Test")
    window.set_visible(False)
    pyglet.app.run()

def main():
    global window
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    player = Player() #£joystick=joystick, para_atras=para_atras, keys=keys)

    
    play_music()
    music_player.play()

    pygame.display.set_caption('Animation')

    clock = pygame.time.Clock()

    elapsed = 0

    t1 = threading.Thread(target=music_thread)
    t1.start()

    while True:
        dt = elapsed/1000.0
        player.update(dt)
        elapsed = clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                t1.join()
                sys.exit()
            else:
                music_player.pitch = 1

        player.draw(screen)
        pygame.display.update()

def update_player(seconds):
    player.position = (player.position[0] + int(player_speed[0]*seconds), 
                       player.position[1] + int(player_speed[1]*seconds))


if __name__ == "__main__":
    main()
