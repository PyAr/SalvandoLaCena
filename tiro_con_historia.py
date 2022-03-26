import pyglet
from pyglet.window import key

window = pyglet.window.Window(800, 600)
last_delta_time = 1
delta_time = 1
freq = 0.05

class Player(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        self.vy = -5
        self.vx = 2
        self.dt_accum = 0
        self.imagen = "imagenes/ball.png"
        image = pyglet.resource.image(self.imagen)
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 2

        self.x = -50
        self.y = 200
        self.history = []

    def serializar(self):
        return {
                "x": self.x,
                "y": self.y,
                "vy": self.vy,
                "vx": self.vx,
                "imagen": self.imagen,
                "rotation": self.rotation,
        }

    def restaurar(self, serializado):
        self.x = serializado["x"]
        self.y = serializado["y"]
        self.vy = serializado["vy"]
        self.vx = serializado["vx"]
        self.imagen = serializado["imagen"]
        self.rotation = serializado["rotation"]

    def update(self, dt):
        global last_delta_time

        if delta_time > 0 and last_delta_time < 0:
            self.dt_accum = 0
        elif delta_time < 0 and last_delta_time > 0:
            self.dt_accum = 0

        if delta_time > 0:
            self.update_avanza(dt)
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

    def update_avanza(self, dt):
        global delta_time
        self.dt_accum += 0.01 * delta_time * 15
        dt = dt * 20

        while self.dt_accum > freq:
            self.dt_accum -= freq

            self.y -= self.vy * dt
            self.vy += 0.2 * dt
            self.x += self.vx * dt

            if self.y < 100:
                self.y = 100
                self.vy = -13

            if self.x > 800:
                self.x = -50

            self.rotation += 10 * dt

            self.history.append(self.serializar())

class Label(pyglet.text.Label):

    def __init__(self):
        super().__init__(text="test", y=10, x=10, font_size=20)

    def update(self, dt, dt_accum):
        global delta_time
        self.text = f"delta_time: {delta_time}, {dt_accum}"

player = Player()
label = Label()

def update(dt):
    #print(joystick.x)
    player.update(dt)
    label.update(dt, player.dt_accum)

@window.event
def on_draw():
    window.clear()
    player.draw()
    label.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time

    # OJO, pusimos * 2 porque los límites
    delta_time = 2 * ((x - 400 ) / 400.0)


pyglet.clock.schedule_interval(update, 1/100.0)
pyglet.app.run()
