import math
import time
import socket
import pyglet
from pyglet.window import key
from bisect import bisect
from itertools import cycle
import threading

#### inicio funciones tweening


def _chequear_rango(n):
    if n < 0 or n > 1:
        raise ValueError("tiene que ser entre 0 y 1")


def linear(n):
    _chequear_rango(n)
    return n


def easeInQuad(n):
    _chequear_rango(n)
    return n**2


def easeOutQuad(n):
    _chequear_rango(n)
    return -n * (n - 2)


def easeOutElastic(n, amplitude=1, period=0.3):
    _chequear_rango(n)

    if amplitude < 1:
        amplitude = 1
        s = period / 4
    else:
        s = period / (2 * math.pi) * math.asin(1 / amplitude)

    return amplitude * 2 ** (-10 * n) * math.sin((n - s) * (2 * math.pi / period)) + 1


class Tween:
    def __init__(self, obj, attr, f, v_ini, v_fin, t_ini, t_fin):
        self.obj = obj
        self.attr = attr
        self.f = f
        self.v_ini = v_ini
        self.v_fin = v_fin
        self.t_ini = t_ini
        self.t_fin = t_fin

    def asignar_valor(self, _T):
        # mapear el tiempo entre 0 y 1
        t = (_T - self.t_ini) / (self.t_fin - self.t_ini)
        if t < 0 or t > 1:
            # retornamos que no se hizo asignación
            return False
        # mapear f(t) que va de 0 a 1 entre ini y fin
        v = self.v_ini + self.f(t) * (self.v_fin - self.v_ini)
        # asignar v al atributo del objeto
        setattr(self.obj, self.attr, v)
        # retornamos que se hizo asignación
        return True

    def asignar_ini(self):
        return self.asignar_valor(self.t_ini)

    def asignar_fin(self):
        return self.asignar_valor(self.t_fin)

#### fin funciones tweening


jugando = False

wavefile_name = "music/music.wav"
wavefile_name_reverse = "music/music_reversed.wav"

T = 0  # El Tiempo
window = pyglet.window.Window(800, 600)
delta_time = 1
FACTOR_VELOCIDAD = 1.5
dt_accum = 0

AVANCE_X = 130
VUELTAS = 720
ALTURA_REBOTE = 540
ALTURA_COLCHON = 140
ALTURA_SUELO = 70

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
        self.history = [(espera, [
            Tween(self, "y", easeOutElastic, self.y, 0, espera, espera + 2),
        ])]

    def update(self, _dt):
        tiempos, tweens = zip(*self.history)
        i = bisect(tiempos, T)

        if i == 0:
            if self.y != -600:
                self.y = -600
            return

        for tween in tweens[i - 1]:
            tween.asignar_valor(T)


class Pelota(pyglet.sprite.Sprite):
    def __init__(self, espera, imagen, *args, **kwargs):
        self.imagen = imagen
        image = pyglet.resource.image(self.imagen)
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2

        self.x = -50
        self.y = 200

        self.scale = 0.5
        self.muerto = False

        # esto es solo para evitar que el squash-stretch no se rompa al rebobinar:
        self.ultimo_i = 0

        tweens = self._crear_tweens(espera, self.x, self.y, 0)
        self.history = [*tweens]

    def _crear_tweens(self, t_ini, x_ini, y_ini, r_ini):
        para_arriba = [
            Tween(self, "x", easeInQuad, x_ini, x_ini + AVANCE_X, t_ini, t_ini + 2),
            Tween(self, "y", easeOutQuad, y_ini, ALTURA_REBOTE, t_ini, t_ini + 2),
            Tween(self, "rotation", easeInQuad, r_ini, r_ini + VUELTAS, t_ini, t_ini + 2),
            # squash-stretch:
            Tween(self, "scale_x", easeOutElastic, 2, 1, t_ini, t_ini + 1),
            Tween(self, "scale_y", easeOutElastic, 0.5, 1, t_ini, t_ini + 1),
        ]
        para_abajo = [
            Tween(self, "x", easeOutQuad, x_ini + AVANCE_X, x_ini + AVANCE_X * 2, t_ini + 2, t_ini + 4),
            Tween(self, "y", easeInQuad, ALTURA_REBOTE, ALTURA_SUELO, t_ini + 2, t_ini + 4),
            Tween(self, "rotation", easeOutQuad, r_ini + VUELTAS, r_ini + VUELTAS * 2, t_ini + 2, t_ini + 4),
            Tween(self, "scale_x", linear, 1, 1, t_ini + 2, t_ini + 4),
            Tween(self, "scale_y", linear, 1, 1, t_ini + 2, t_ini + 4),
        ]
        return [
            (t_ini, para_arriba),
            (t_ini + 2, para_abajo),
        ]

    def update(self, _dt, player):
        tiempos, tweens = zip(*self.history)
        i = bisect(tiempos, T)
        if i == 0:
            # si bisect retorna 0 quiere decir que no hay tweens para este T
            return

        if self.ultimo_i != i - 1:
            if para_atras:
                # resetear valores
                for tween in tweens[self.ultimo_i]:
                    tween.asignar_ini()
            self.ultimo_i = i - 1

        actualizado = False
        for tween in tweens[i - 1]:
            actualizado = tween.asignar_valor(T) or actualizado

        if actualizado and para_atras and self.muerto:
            self.muerto = False
            self.opacity = 255
        elif not actualizado and not para_atras and not self.muerto:
            self.muerto = True
            self.opacity = 80

        if para_atras:
            # si el objeto está subiendo en reversa, borrar el futuro
            if tweens[i - 1][1].f == easeInQuad and len(self.history) > i:
                while len(self.history) > i:
                    self.history.pop()
        else:
            # si el objeto está bajando
            if tweens[i - 1][1].f == easeInQuad and not self.muerto:
                if ALTURA_SUELO < self.y <= ALTURA_COLCHON:
                    if abs(player.x - self.x) < 100:
                        # rebota
                        new_tweens = self._crear_tweens(
                            T, self.x, self.y, self.rotation
                        )
                        self.history.extend(new_tweens)


class Label(pyglet.text.Label):
    def __init__(self):
        super().__init__(color=(0, 0, 0, 255), y=10, x=550, font_size=30, bold=True, align="center", width=300)
        self.opacity = 128

    def update(self, dt):
        self.text = f"{T:.2f}"


class Player(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/player.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 0.8

        self.x = 100
        self.y = 80

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
    objeto = Pelota(espera, imagen=f"imagenes/objeto_{numero+1}.png")
    objetos.append(objeto)

final = Final(espera=52)

label = Label()
lluvia_2 = Lluvia("imagenes/lluvia-02.png", velocidad=800)
lluvia_1 = Lluvia("imagenes/lluvia-01.png", velocidad=1200)
fondo = Fondo("imagenes/fondo_juego.png")
title = Title()


def update(dt):
    global T
    # print(T)

    global delta_time
    global jugando
    global dt_accum

    if jugando:
        T += dt * delta_time * FACTOR_VELOCIDAD
        lluvia_1.update(dt)

        for x in objetos:
            x.update(dt, player)

        label.update(dt)
        final.update(dt)
        lluvia_2.update(dt)
        player.update(dt)
        reloj.update(dt)

        # delta_time = next(FAKE_WHEEL)
        update_direction(delta_time)
    else:
        if keys[key.SPACE]:
            if not jugando:
                music_player.play()
                jugando = True
                dt_accum = 0


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

        lluvia_1.draw()
        final.draw()
        label.draw()
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


# FAKE_WHEEL = cycle(generate_wheel_fake())

#t1 = threading.Thread(target=read_wheel)
#t1.start()


@window.event
def on_close():
    #t1.join()
    print("cerrando")


@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time
    delta_time = (x - 400) / 200.0


pyglet.clock.schedule_interval(update, 1 / 100.0)
pyglet.app.run()
