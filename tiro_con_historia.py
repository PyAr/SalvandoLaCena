import pyglet
from pyglet.window import key

window = pyglet.window.Window(800, 600)
last_delta_time = 1
delta_time = 1
freq = 0.05

keys = key.KeyStateHandler()
window.push_handlers(keys)
joysticks = pyglet.input.get_joysticks()
joystick = None

if joysticks:
    print("Hay un joystick")
    joystick = joysticks[0]

if joystick:
    joystick.open()


class Pelota(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        self.vy = -5
        self.vx = 2
        self.dt_accum = 0
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

    def serializar(self):
        return {
                "x": self.x,
                "y": self.y,
                "vy": self.vy,
                "vx": self.vx,
                "imagen": self.imagen,
                "rotation": self.rotation,
                "vr": self.vr,
        }

    def restaurar(self, serializado):
        self.x = serializado["x"]
        self.y = serializado["y"]
        self.vy = serializado["vy"]
        self.vx = serializado["vx"]
        self.imagen = serializado["imagen"]
        self.rotation = serializado["rotation"]
        self.vr = serializado["vr"]

    def update(self, dt, player):
        global last_delta_time

        if delta_time > 0 and last_delta_time < 0:
            self.dt_accum = 0
        elif delta_time < 0 and last_delta_time > 0:
            self.dt_accum = 0

        if delta_time > 0:
            self.update_avanza(dt, player)
        else:
            self.update_atras(dt)

        last_delta_time = delta_time

    def update_atras(self, dt):
        global delta_time

        self.dt_accum += dt * 30 * abs(delta_time)
        step = None

        while self.dt_accum > freq:
            self.dt_accum -= freq
            if self.history:
                step = self.history.pop()

        if step:
            self.restaurar(step)

    def update_avanza(self, dt, player):
        global delta_time
        self.dt_accum += 0.01 * delta_time * 15
        dt = dt * 20

        while self.dt_accum > freq:
            self.dt_accum -= freq

            self.y -= self.vy * dt
            self.vy += 0.2 * dt
            self.x += self.vx * dt

            if self.y < 100:

                # Si colisiona con la plataforma
                if (player.x - 100 < self.x < player.x + 100):
                    self.y = 100
                    self.vy = -13
                else:
                    # Si no colisiona con la plataforma
                    self.y = 99
                    self.vy = 0
                    self.vr = 0
                    self.vx = 0

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
    #print(joystick.x)
    pelota.update(dt, player)
    label.update(dt)
    player.update(dt)

@window.event
def on_draw():
    window.clear()
    pelota.draw()
    label.draw()
    player.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time

    # OJO, pusimos * 2 porque los límites
    delta_time = 2 * ((x - 400 ) / 400.0)


pyglet.clock.schedule_interval(update, 1/100.0)
pyglet.app.run()
