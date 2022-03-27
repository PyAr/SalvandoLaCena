import math
import time
import socket
import pyglet
from pyglet.window import key
from itertools import cycle
import threading

jugando = False

wavefile_name = 'music/music.wav'
wavefile_name_reverse = 'music/music_reversed.wav'

window = pyglet.window.Window(800, 600)
last_delta_time = 1
delta_time = 1
freq = 0.05
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


class Lluvia(pyglet.sprite.Sprite):

    def __init__(self, nombre_imagen="imagenes/lluvia-02.png", velocidad=200, *args, **kwargs):
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
        return {
                "x": self.x,
                "y": self.y,
                "espera": self.espera,
        }

    def restaurar(self, serializado):
        self.x = serializado["x"]
        self.y = serializado["y"]
        self.espera = serializado["espera"]

    def update(self, dt):
        global last_delta_time, dt_accum

        if delta_time > 0 and last_delta_time < 0:
            dt_accum = 0
        elif delta_time < 0 and last_delta_time > 0:
            dt_accum = 0

        if delta_time > 0:
            self.update_avanza(dt)
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

    def update_avanza(self, dt):
        global delta_time, dt_accum


        dt_accum += 0.01 * delta_time * 15
        dt = dt * 20

        while dt_accum > freq:
            dt_accum -= freq

            if self.espera > 0:
                self.espera -= dt
                if self.espera < 0:
                    self.espera = 0
                self.history.append(self.serializar())
                return

            self.y += 10 * dt

            if (self.y > 0):
                self.y = 0

            self.history.append(self.serializar())

class Pelota(pyglet.sprite.Sprite):

    def __init__(self, espera, imagen, *args, **kwargs):
        self.vy = -10
        self.vx = 2
        self.imagen = imagen
        image = pyglet.resource.image(self.imagen)
        super().__init__(img=image, *args, **kwargs)
        self.espera = espera

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 2.5

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
                "espera": self.espera,
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
        self.espera = serializado["espera"]

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

        if self.muerto:
            self.opacity = 80
        else:
            self.opacity = 255

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

            if self.espera > 0:
                self.espera -= dt
                if self.espera < 0:
                    self.espera = 0
                self.history.append(self.serializar())
                return

            self.y -= self.vy * dt
            self.vy += 0.2 * dt
            self.x += self.vx * dt

            if self.y < COLCHON:

                # Si colisiona con la plataforma
                if not self.muerto and player.x - 100 < self.x < player.x + 100 and self.y > SUELO:
                    self.y = COLCHON
                    self.vy = -13
                else:

                    if self.y < SUELO:
                        # Si no colisiona con la plataforma
                        self.y = SUELO - 1
                        self.vy = 0
                        self.vr = 0
                        self.vx = 0
                        self.muerto = True

            if self.x > 800:
                self.x = 900

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
        self.scale = 0.8

        self.x = 100
        self.y = 80

        # TODO: intentar hacer que el movimiento se conecte
        #       o sea "tileable"

    def update(self, dt):
        global joystick
        global reversed

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

        if reversed:
            self.opacity = 80
        else:
            self.opacity = 255


player = Player()
#          1   2    3    4    5    6    7    8    9    10
esperas = [0, 130, 150, 180, 400, 420, 440, 490, 550, 600]
objetos = []


for numero, espera in enumerate(esperas):
    objeto = Pelota(espera=espera, imagen=f"imagenes/objeto_{numero + 1}.png")
    objetos.append(objeto)

final = Final(espera=750)

label = Label()
lluvia_2 = Lluvia("imagenes/lluvia-02.png", velocidad=800)
lluvia_1 = Lluvia("imagenes/lluvia-01.png", velocidad=1200)
fondo = Fondo("imagenes/fondo_juego.png")
title = Title()

# contador = 60

def update(dt):
    global delta_time
    global jugando
    global dt_accum
    # global contador
    #print(joystick.x)

    if jugando:
        for x in objetos:
            x.update(dt, player)

        label.update(dt)
        lluvia_1.update(dt)
        final.update(dt)
        lluvia_2.update(dt)
        player.update(dt)
        # print(contador)

        # if contador == 0:
            # contador = 60
            # delta_time = -read_wheel()
        # else:
            # contador -= 1

        #delta_time = next(FAKE_WHEEL)
        update_direction(delta_time)
    else:
        if keys[key.SPACE]:
            if not jugando:
                music_player.play()
                jugando = True
                dt_accum = 0
            else:
                return True



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

        label.draw()
        lluvia_1.draw()
        final.draw()
    else:
        title.draw()


# @window.event
# def on_mouse_motion(x, y, dx, dy):
    # global delta_time

    # # OJO, pusimos * 2 porque los límites
    # delta_time = 2 * ((x - 400 ) / 400.0)

def convert_speed_value(value):
    converted_value = -1*math.log10(-value+947) + 2
    return converted_value


def read_wheel():
    global delta_time

    s = socket.socket()
    s.connect(('192.168.4.1', 80))

    while True:
        time.sleep(.1)

        s.send(b"\xFF")
        raw = s.recv(10)
        raw_value = (int(raw.decode("ascii")))
        delta_time = -convert_speed_value(raw_value)

def generate_wheel_fake():
    lista = []
    for row in open("wheelvalues.txt", "r"):
        converted_value = convert_speed_value(int(row))
        lista.append(converted_value)
    return lista


FAKE_WHEEL = cycle(generate_wheel_fake())

t1 = threading.Thread(target=read_wheel)
t1.start()



@window.event
def on_close():
    t1.join()
    print("cerrando")

pyglet.clock.schedule_interval(update, 1/100.0)
pyglet.app.run()
