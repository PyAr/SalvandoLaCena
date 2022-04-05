import sys
import math
import pyglet

delta_time = 1
FRAME_TIME = 1 / 60

# se puede jugar con esta resolución para que el
# slow-motion se vea más suave, pero mientras más
# resolución más estados se guardan, ocupando más
# memoria.
SUBFRAMES = 10

dt_accum = 0

window = pyglet.window.Window(800, 600)


class Label(pyglet.text.Label):
    def __init__(self):
        super().__init__(y=20, x=20, font_size=30)

    def update(self, dt):
        global objeto
        self.text = (
            f"velocidad: {delta_time:.2f} | bytes: {sys.getsizeof(objeto.history)}"
        )


class Pelota(pyglet.sprite.Sprite):
    def __init__(self, imagen, *args, **kwargs):
        image = pyglet.resource.image(imagen)
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 0.5

        self.x = 150
        self.y = 200

        self.vx = 1.8
        self.vy = 8

        self.history = []

    def serializar(self):
        return (
            self.x,
            self.y,
            self.rotation,
            self.vx,
            self.vy,
        )

    def restaurar(self, serializado):
        (
            self.x,
            self.y,
            self.rotation,
            self.vx,
            self.vy,
        ) = serializado

    def update(self, direccion):
        if direccion > 0:
            self.update_avanza()
        else:
            self.update_atras()

    def update_atras(self):
        if len(self.history):
            self.restaurar(self.history.pop())

    def update_avanza(self):
        if len(self.history) == 0:
            self.history.append(self.serializar())

        self.x += self.vx / SUBFRAMES
        self.y += self.vy / SUBFRAMES
        self.vy -= 0.15 / SUBFRAMES
        self.rotation += 5 / SUBFRAMES

        self.history.append(self.serializar())


label = Label()
objeto = Pelota(imagen=f"imagenes/objeto_1.png")


def update(dt):
    global dt_accum

    label.update(dt)

    if delta_time == 0:
        # en pausa, previene división por cero
        return

    delta_frame = FRAME_TIME / SUBFRAMES / abs(delta_time)
    if dt_accum + dt < delta_frame:
        dt_accum += dt
        # print('skip update')
        return

    dt_accum = 0

    frames = math.ceil(dt / delta_frame)
    # print(f'update {frames} frames')
    for f in range(frames):
        objeto.update(delta_time > 0)


@window.event
def on_draw():
    window.clear()
    objeto.draw()
    label.draw()


@window.event
def on_close():
    print("cerrando")


@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time
    delta_time = (x - 400) / 200.0


pyglet.clock.schedule_interval(update, 1 / 100.0)
pyglet.app.run()
