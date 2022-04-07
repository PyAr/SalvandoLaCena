import sys
import math
import time
import socket
import pyglet
from pyglet.window import key
from itertools import cycle
import threading

jugando = False

wavefile_name = "music/music.wav"
wavefile_name_reverse = "music/music_reversed.wav"

fullscreen = False
if len(sys.argv) > 1 and ("-f" in sys.argv or "--fullscreen" in sys.argv):
    fullscreen = True

window = pyglet.window.Window(800, 600, fullscreen=fullscreen)
delta_time = 1
FRAME_TIME = 1 / 60

# se puede jugar con esta resolución para que el
# slow-motion se vea más suave, pero mientras más
# resolución más estados se guardan, ocupando más
# memoria.
SUBFRAMES = 10

dt_accum = 0

COLCHON = 140
SUELO = 70

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


class Lluvia(pyglet.sprite.Sprite):
    def __init__(
        self, nombre_imagen="imagenes/lluvia-02.png", velocidad=200, *args, **kwargs
    ):
        self.velocidad = velocidad
        image = pyglet.resource.image(nombre_imagen)
        self.textura = pyglet.image.TileableTexture.create_for_image(image)
        super().__init__(img=image, *args, **kwargs)

    def draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.textura.blit_tiled(0, 0, 0, 800, 600)

    def update(self, dt):
        self.textura.anchor_y += dt * delta_time * self.velocidad


class Fondo(pyglet.sprite.Sprite):
    def __init__(self, imagen, *args, **kwargs):
        self.imagen = imagen
        image = pyglet.resource.image(self.imagen)
        super().__init__(img=image, *args, **kwargs)


class Title(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/title.png")
        super().__init__(img=image, *args, **kwargs)


class Final(pyglet.sprite.Sprite):
    def __init__(self, espera, *args, **kwargs):
        image = pyglet.resource.image("imagenes/final.png")
        super().__init__(img=image, *args, **kwargs)
        self.espera = espera

        image.anchor_x = 0
        image.anchor_y = 0

        self.x = 0
        self.y = -600
        self.history = []

    def serializar(self):
        return (
            self.y,
            self.espera,
        )

    def restaurar(self, serializado):
        (
            self.y,
            self.espera,
        ) = serializado

    def update(self, direccion):
        if direccion > 0:
            self.update_avanza(player)
        else:
            self.update_atras()

    def update_atras(self):
        if len(self.history):
            self.restaurar(self.history.pop())

    def update_avanza(self, player):
        if len(self.history) == 0:
            self.history.append(self.serializar())

        if self.espera > 0:
            self.espera -= FRAME_TIME / SUBFRAMES
            self.history.append(self.serializar())
            return

        if self.y < 0:
            self.y = min(0, self.y + 10 / SUBFRAMES)

        self.history.append(self.serializar())


class Pelota(pyglet.sprite.Sprite):
    def __init__(self, espera, imagen, *args, **kwargs):
        self.espera = espera

        image = pyglet.resource.image(imagen)
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 0.5

        self.x = -50
        self.y = 200

        self.vx = 2
        self.vy = 10
        self.vr = 5

        self.muerto = False
        self.history = []

    def serializar(self):
        return (
            self.x,
            self.y,
            self.rotation,
            self.vx,
            self.vy,
            self.vr,
            self.muerto,
            self.espera,
        )

    def restaurar(self, serializado):
        (
            self.x,
            self.y,
            self.rotation,
            self.vx,
            self.vy,
            self.vr,
            self.muerto,
            self.espera,
        ) = serializado

    def update(self, direccion, player):
        self.muerto_anterior = self.muerto

        if direccion > 0:
            self.update_avanza(player)
        else:
            self.update_atras()

        if self.muerto != self.muerto_anterior:
            if self.muerto:
                self.opacity = 80
            else:
                self.opacity = 255

    def update_atras(self):
        if len(self.history):
            self.restaurar(self.history.pop())

    def update_avanza(self, player):
        if len(self.history) == 0:
            self.history.append(self.serializar())

        if self.espera > 0:
            self.espera -= FRAME_TIME / SUBFRAMES
            self.history.append(self.serializar())
            return

        self.x += self.vx / SUBFRAMES
        self.y += self.vy / SUBFRAMES
        self.vy -= 0.2 / SUBFRAMES
        self.rotation += self.vr / SUBFRAMES

        # Si colisiona con la plataforma
        if self.y < COLCHON and self.y > SUELO:
            if abs(player.x - self.x) < 100:
                self.y = COLCHON
                self.vy = 13
        # Si cae al suelo
        elif self.y <= SUELO:
            self.y = SUELO - 1
            self.vx = 0
            self.vy = 0
            self.vr = 0
            self.muerto = True

        # El objeto llega a la derecha de la pantalla:
        if self.x > 800:
            self.x = 900

        self.history.append(self.serializar())


class Label(pyglet.text.Label):
    def __init__(self):
        super().__init__(text="test", y=20, x=20, font_size=30)

    def update(self, dt):
        global delta_time
        self.text = f"velocidad: {delta_time:.2f}"


class Player(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/player.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 0.8

        self.x = 100
        self.y = 80

        # TODO: intentar hacer que el movimiento se conecte
        #       o sea "tileable"

    def update(self, dt):
        global joystick
        global para_atras

        if joystick:
            if joystick.x < -0.2 or joystick.x > 0.2:
                self.x += joystick.x * 20

        if keys[key.RIGHT]:
            self.x += 10
        elif keys[key.LEFT]:
            self.x -= 10

        if self.x <= 80:
            self.x = 80

        if self.x > 800 - 80:
            self.x = 800 - 80

        if para_atras:
            self.opacity = 80
        else:
            self.opacity = 255


class Reloj(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/reloj.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2

        self.x = 700
        self.y = 100
        self.scale = 0.5
        self.opacity = 128

    def update(self, dt):
        global delta_time
        self.rotation = delta_time * 90


player = Player()
reloj = Reloj()

esperas = [1, 10, 11, 20, 22, 25, 30, 31, 38, 39]
objetos = []

for numero, espera in enumerate(esperas):
    objeto = Pelota(espera=espera * 0.6, imagen=f"imagenes/objeto_{numero+1}.png")
    objetos.append(objeto)

final = Final(espera=52 * 0.6)


label = Label()
lluvia_2 = Lluvia("imagenes/lluvia-02.png", velocidad=800)
lluvia_1 = Lluvia("imagenes/lluvia-01.png", velocidad=1200)
fondo = Fondo("imagenes/fondo_juego.png")
title = Title()


def update_objetos(dt):
    global dt_accum

    if delta_time == 0:
        # en pausa, previene división por cero
        return

    delta_frame = FRAME_TIME / SUBFRAMES / abs(delta_time)
    if dt_accum + dt < delta_frame:
        dt_accum += dt
        return

    dt_accum = 0

    frames = math.ceil(dt / delta_frame)
    for f in range(frames):
        for x in objetos:
            x.update(delta_time > 0, player)
        final.update(delta_time > 0)


def update(dt):
    global delta_time
    global jugando
    # print(joystick.x)

    if jugando:
        lluvia_1.update(dt)
        update_objetos(dt)
        label.update(dt)
        lluvia_2.update(dt)
        player.update(dt)
        reloj.update(dt)
        update_direction(delta_time)
    else:
        if keys[key.SPACE]:
            if not jugando:
                music_player.play()
                jugando = True


@window.event
def on_draw():
    window.clear()

    # el fondo se muestra en el menu y el juego
    fondo.draw()

    if jugando:
        lluvia_2.draw()
        player.draw()

        for x in objetos:
            x.draw()

        # label.draw()
        lluvia_1.draw()
        final.draw()
        reloj.draw()
    else:
        title.draw()


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


def generate_wheel_fake():
    lista = []
    for row in open("wheelvalues.txt", "r"):
        converted_value = convert_speed_value(int(row))
        lista.append(converted_value)
    return lista


FAKE_WHEEL = cycle(generate_wheel_fake())

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


pyglet.clock.schedule_interval(update, 1 / 100.0)
pyglet.app.run()
