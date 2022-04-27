import math
import socket
import time

import pyglet
pyglet.resource.path = ['..']

wavefile_name = 'music/music.wav'
wavefile_name_reverse = 'music/music_reversed.wav'

window = pyglet.window.Window(800, 600)

song = pyglet.media.load(wavefile_name)
reversed_song = pyglet.media.load(wavefile_name_reverse)
player = pyglet.media.Player()
player_reverse = pyglet.media.Player()

player.queue(song)
player.loop = True
player_reverse.queue(reversed_song)
player_reverse.loop = True
player.play()

reversed = False


@window.event
def on_draw():
    window.clear()


def update_direction(delta_time):
    #player.pitch = delta_time + 1
    player.pitch = abs(delta_time) * 1.4
    #player_reverse.pitch = delta_time*-1 + 1
    player_reverse.pitch = abs(delta_time) * 1.4
    global reversed
    if reversed:
        if delta_time >= 0:
            player_reverse.pause()
            player.play()
            reversed = False
    else:
        if delta_time < 0:
            player.pause()
            player_reverse.play()
            reversed = True


@window.event
def on_mouse_motion(x, y, dx, dy):
    delta_time = (x - 400) / 400.0
    update_direction(delta_time)

def convert_speed_value(value):
    converted_value = -1*math.log10(-value+947) + 2
    print(converted_value)
    return converted_value

#s = socket.socket()
#s.connect(('192.168.4.1', 80))


def read_wheel():
    s.send(b"\xFF")
    raw = s.recv(10)
    raw_value = (int(raw.decode("ascii")))
    delta_time = convert_speed_value(raw_value)
    return delta_time


def read_wheel_fake():
    for row in open("wheelvalues.txt", "r"):
        converted_value = convert_speed_value(int(row))
        print(converted_value)
        yield converted_value

FAKE_WHEEL = read_wheel_fake()

def update(dt):
    print(dt)
    #delta_time = read_wheel()
    delta_time = next(FAKE_WHEEL)
    update_direction(delta_time)


pyglet.clock.schedule_interval(update, 1/20.0)
pyglet.app.run()
