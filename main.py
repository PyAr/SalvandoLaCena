import math
import random
import socket
import sys
import threading
import time
from itertools import cycle

import pyglet
from pyglet.gl import *
from pyglet.window import key

from constants import COLCHON, FRAME_ESTADISTICAS, FRAME_TIME, SUBFRAMES, SUELO
from loggable_items import Final, Pelota, Sombra
from screen_items import (Chispear, Estadisticas, Fondo, Lluvia, Player,
                          Reloj, Title)

jugando = False

wavefile_name = "music/music.wav"
wavefile_name_reverse = "music/music_reversed.wav"

fullscreen = False
if len(sys.argv) > 1 and ("-f" in sys.argv or "--fullscreen" in sys.argv):
    fullscreen = True

window = pyglet.window.Window(800, 600, fullscreen=fullscreen, resizable=True)
delta_time = 1

current_subframe = 0

def get_current_frame():
    return int(current_subframe / SUBFRAMES)

dt_accum = 0

keys = key.KeyStateHandler()
window.push_handlers(keys)
joysticks = pyglet.input.get_joysticks()
joystick = None

if joysticks:
    print("Hay un joystick")
    joystick = joysticks[0]

if joystick:
    joystick.open()


## musica
song = pyglet.media.load(wavefile_name)
reversed_song = pyglet.media.load(wavefile_name_reverse)
music_player = pyglet.media.Player()
player_reverse = pyglet.media.Player()

music_player.queue(song)
music_player.loop = True
player_reverse.queue(reversed_song)
player_reverse.loop = True

para_atras = False


def update_direction(delta_time):
    # player.pitch = delta_time + 1
    music_player.pitch = abs(delta_time) * 1.4
    # player_reverse.pitch = delta_time*-1 + 1
    player_reverse.pitch = abs(delta_time) * 1.4
    global para_atras
    if para_atras:
        if delta_time >= 0:
            player_reverse.pause()
            music_player.play()
            para_atras = False
    else:
        if delta_time < 0:
            music_player.pause()
            player_reverse.play()
            para_atras = True

player = Player(joystick=joystick, para_atras=para_atras, keys=keys)
sombra = Sombra(player)
reloj = Reloj(delta_time=delta_time)

chispear = [
    Chispear(902, 8, get_current_frame=get_current_frame),
    Chispear(555, 8, 4, get_current_frame=get_current_frame),
    Chispear(112, 8, 6, get_current_frame=get_current_frame),
    Chispear(787, 20, get_current_frame=get_current_frame),
    Chispear(878, 20, 4, get_current_frame=get_current_frame),
]

esperas = [1, 10, 11, 20, 22, 25, 30, 31, 38, 39]
objetos = []

for numero, espera in enumerate(esperas):
    objeto = Pelota(espera=espera * 0.6, imagen=f"imagenes/objeto_{numero+1}.png")
    objetos.append(objeto)

final = Final(espera=50 * 0.6)
estadisticas = Estadisticas(window=window, objetos=objetos, get_current_frame=get_current_frame)

# label = Label()
lluvia_2 = Lluvia("imagenes/lluvia-02.png", velocidad=800, delta_time=delta_time)
lluvia_1 = Lluvia("imagenes/lluvia-01.png", velocidad=1200, delta_time=delta_time)
fondo = Fondo("imagenes/fondo_juego.png")
title = Title()

def get_current_frame():
    return int(current_subframe / SUBFRAMES)

def update_objetos(dt):
    global dt_accum
    global current_subframe

    if delta_time == 0:
        # en pausa, previene división por cero
        return

    delta_frame = FRAME_TIME / SUBFRAMES / abs(delta_time)
    if dt_accum + dt < delta_frame:
        dt_accum += dt
        return

    dt_accum = 0

    subframes = math.ceil(dt / delta_frame)
    for f in range(subframes):
        if delta_time > 0:
            current_subframe += 1
        else:
            current_subframe -= 1
        for x in objetos:
            x.update(delta_time > 0, player)
        for c in chispear:
            c.update()
        sombra.update(delta_time > 0)
        final.update(delta_time > 0)


def update(dt):
    global delta_time
    global jugando
    # print(joystick.x)

    if jugando:
        lluvia_1.update(dt)
        # label.update(dt)
        lluvia_2.update(dt)
        player.update(dt)
        reloj.update(dt)
        estadisticas.update()
        update_direction(delta_time)
        update_objetos(dt)
    else:
        if keys[key.SPACE]:
            if not jugando:
                music_player.play()
                jugando = True


@window.event
def on_draw():
    window.clear()
    glPushMatrix()
    x = int(window.width / 2)
    a = window.width / float(window.height)
    glTranslatef(-400, -600 / 2, -521)

    # el fondo se muestra en el menu y el juego
    fondo.draw()

    if jugando:
        lluvia_2.draw()

        for c in chispear:
            c.draw()

        sombra.draw()
        player.draw()

        for x in objetos:
            x.draw()

        # label.draw()
        lluvia_1.draw()
        final.draw()

        if get_current_frame() > FRAME_ESTADISTICAS:
            estadisticas.draw()

        reloj.draw()
    else:
        title.draw()

    glPopMatrix()


def convert_speed_value(value):
    converted_value = -1 * math.log10(-value + 947) + 2
    return converted_value


def read_wheel():
    global delta_time

    s = socket.socket()
    s.connect(("192.168.4.1", 80))

    while True:
        time.sleep(0.1)

        s.send(b"\xFF")
        raw = s.recv(10)
        raw_value = int(raw.decode("ascii"))
        delta_time = -convert_speed_value(raw_value)


# t1 = threading.Thread(target=read_wheel)
# t1.start()


@window.event
def on_close():
    # t1.join()
    print("cerrando")


@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time
    delta_time = (x - 400) / 200.0


@window.event
def on_resize(width, height):
    glViewport(0, 0, int(height / 0.75), height)
    return pyglet.event.EVENT_HANDLED


window.set_minimum_size(400, 300)
gluPerspective(60.0, window.width / float(window.height), 0.1, 1000.0)
pyglet.clock.schedule_interval(update, 1 / 100.0)
pyglet.app.run()
