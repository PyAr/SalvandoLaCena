import math
import socket
import time
import pyglet
from pyglet.window import key
from itertools import cycle

wavefile_name = 'music/music.wav'
wavefile_name_reverse = 'music/music_reversed.wav'

window = pyglet.window.Window(800, 600)
last_delta_time = 1
delta_time = 1
freq = 0.05
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
music_player.play()

reversed = False

def update_direction(delta_time):
    #player.pitch = delta_time + 1
    music_player.pitch = abs(delta_time) * 1.4
    #player_reverse.pitch = delta_time*-1 + 1
    player_reverse.pitch = abs(delta_time) * 1.4
    global reversed
    if reversed:
        if delta_time >= 0:
            player_reverse.pause()
            music_player.play()
            reversed = False
    else:
        if delta_time < 0:
            music_player.pause()
            player_reverse.play()
            reversed = True



class Pelota(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        self.vy = -5
        self.vx = 2
        self.imagen = "imagenes/objeto_1.png"
        image = pyglet.resource.image(self.imagen)
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 2

        self.x = -50
        self.y = 200
        self.vr = 5
        self.history = []
        self.scale = 0.5
        self.muerto = False

    def serializar(self):
        return {
                "x": self.x,
                "y": self.y,
                "vy": self.vy,
                "vx": self.vx,
                "imagen": self.imagen,
                "rotation": self.rotation,
                "vr": self.vr,
                "muerto": self.muerto,
        }

    def restaurar(self, serializado):
        self.x = serializado["x"]
        self.y = serializado["y"]
        self.vy = serializado["vy"]
        self.vx = serializado["vx"]
        self.imagen = serializado["imagen"]
        self.rotation = serializado["rotation"]
        self.vr = serializado["vr"]
        self.muerto = serializado["muerto"]

    def update(self, dt, player):
        global last_delta_time, dt_accum

        if delta_time > 0 and last_delta_time < 0:
            dt_accum = 0
        elif delta_time < 0 and last_delta_time > 0:
            dt_accum = 0

        if delta_time > 0:
            self.update_avanza(dt, player)
        else:
            self.update_atras(dt)

        last_delta_time = delta_time

    def update_atras(self, dt):
        global delta_time, dt_accum

        dt_accum += dt * 30 * abs(delta_time)
        step = None

        while dt_accum > freq:
            dt_accum -= freq
            if self.history:
                step = self.history.pop()

        if step:
            self.restaurar(step)

    def update_avanza(self, dt, player):
        global delta_time, dt_accum
        dt_accum += 0.01 * delta_time * 15
        dt = dt * 20

        while dt_accum > freq:
            dt_accum -= freq

            self.y -= self.vy * dt
            self.vy += 0.2 * dt
            self.x += self.vx * dt

            if self.y < 100:

                # Si colisiona con la plataforma
                if not self.muerto and player.x - 100 < self.x < player.x + 100:
                    self.y = 100
                    self.vy = -13
                else:
                    # Si no colisiona con la plataforma
                    self.y = 99
                    self.vy = 0
                    self.vr = 0
                    self.vx = 0
                    self.muerto = True

            if self.x > 800:
                self.x = -50

            self.rotation += self.vr * dt

            self.history.append(self.serializar())

class Label(pyglet.text.Label):

    def __init__(self):
        super().__init__(text="test", y=10, x=10, font_size=20)

    def update(self, dt):
        global delta_time
        self.text = f"delta_time: {delta_time}"

class Player(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/player.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 2

        self.x = 100
        self.y = 100

        # TODO: intentar hacer que el movimiento se conecte
        #       o sea "tileable"

    def update(self, dt):

        if joystick:
            if joystick.x > 0.5:
                self.x += 10
            elif joystick.x < -0.5:
                self.x -= 10

        if keys[key.RIGHT]:
            self.x += 10
        elif keys[key.LEFT]:
            self.x -= 10

        if self.x <= 80:
            self.x = 80

        if self.x > 800 - 80:
            self.x = 800 - 80


player = Player()
pelota = Pelota()
label = Label()

def update(dt):
    global delta_time
    #print(joystick.x)
    pelota.update(dt, player)
    label.update(dt)
    player.update(dt)
    delta_time = next(FAKE_WHEEL)
    update_direction(delta_time)

@window.event
def on_draw():
    window.clear()
    player.draw()
    pelota.draw()
    label.draw()

# @window.event
# def on_mouse_motion(x, y, dx, dy):
    # global delta_time

    # # OJO, pusimos * 2 porque los límites
    # delta_time = 2 * ((x - 400 ) / 400.0)

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

def generate_wheel_fake():
    lista = []
    for row in open("wheelvalues.txt", "r"):
        converted_value = convert_speed_value(int(row))
        print(converted_value)
        lista.append(converted_value)
    return lista


FAKE_WHEEL = cycle(generate_wheel_fake())

pyglet.clock.schedule_interval(update, 1/100.0)
pyglet.app.run()
