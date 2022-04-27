import math
import socket
import sys
import threading
import time

import pyglet
from pyglet.gl import (glPopMatrix, glPushMatrix, glTranslatef, gluPerspective,
                       glViewport)
from pyglet.window import key

from constants import (FIFO_WHEEL_FILE, FRAME_ESTADISTICAS, FRAME_TIME, SUBFRAMES,
                       WAVEFILE_NAME, WAVEFILE_NAME_REVERSE)
from connect_wheel import read_wheel
from loggable_items import Final, Pelota, Sombra
from screen_items import (Chispear, Estadisticas, Fondo, Lluvia, Player, Reloj,
                          Title)


fullscreen = False
use_wheel = False

if len(sys.argv) > 1:
    if ("-f" in sys.argv or "--fullscreen" in sys.argv):
        fullscreen = True

    if ("-w" in sys.argv or "--wheel" in sys.argv):
        use_wheel = True


def get_current_frame():
    return int(current_subframe / SUBFRAMES)

window = pyglet.window.Window(800, 600, fullscreen=fullscreen, resizable=True)
jugando = False
para_atras = False
delta_time = 1
current_subframe = 0
dt_accum = 0
keys = key.KeyStateHandler()
window.push_handlers(keys)
joysticks = pyglet.input.get_joysticks()
joystick = None
music_player = pyglet.media.Player()
player_reverse = pyglet.media.Player()

if joysticks:
    print("Hay un joystick")
    joystick = joysticks[0]

if joystick:
    joystick.open()

# Definición de objetos con historia y esperas
player = Player(joystick=joystick, para_atras=para_atras, keys=keys)
sombra = Sombra(player)
reloj = Reloj()
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

# Items en pantalla
lluvia_2 = Lluvia("imagenes/lluvia-02.png", velocidad=800, delta_time=delta_time)
lluvia_1 = Lluvia("imagenes/lluvia-01.png", velocidad=1200, delta_time=delta_time)
fondo = Fondo("imagenes/fondo_juego.png")
title = Title()
final = Final(espera=50 * 0.6)
estadisticas = Estadisticas(window=window, objetos=objetos, get_current_frame=get_current_frame)


def play_music():
    song = pyglet.media.load(WAVEFILE_NAME)
    reversed_song = pyglet.media.load(WAVEFILE_NAME_REVERSE)
    music_player.queue(song)
    music_player.loop = True
    player_reverse.queue(reversed_song)
    player_reverse.loop = True


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

    if jugando:
        lluvia_1.update(dt)
        # label.update(dt)
        lluvia_2.update(dt)
        player.update(dt)
        reloj.update(delta_time)
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
    # a = window.width / float(window.height)
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


def update_wheel_value():
    global delta_time

    for value in read_wheel():
        delta_time = value

if use_wheel:
    t1 = threading.Thread(target=update_wheel_value)
    t1.start()


@window.event
def on_close():
    if use_wheel:
        t1.join()
    print("cerrando")


@window.event
def on_mouse_motion(x, y, dx, dy):
    if not use_wheel:
        global delta_time
        delta_time = (x - 400) / 200.0


@window.event
def on_resize(width, height):
    glViewport(0, 0, int(height / 0.75), height)
    return pyglet.event.EVENT_HANDLED


window.set_minimum_size(400, 300)
gluPerspective(60.0, window.width / float(window.height), 0.1, 1000.0)
pyglet.clock.schedule_interval(update, 1 / 100.0)
play_music()
pyglet.app.run()
