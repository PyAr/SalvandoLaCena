import pyglet

window = pyglet.window.Window(800, 600)
delta_time = 1

class Player(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/player.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2

        self.x = 100
        self.y = 100

    def update(self, dt):
        self.x += 20 * dt * delta_time
        self.y += 20 * dt * delta_time
        self.rotation += 30 * dt * delta_time


class Label(pyglet.text.Label):

    def __init__(self):
        super().__init__(text="test", y=10, x=10, font_size=20)

    def update(self, dt):
        global delta_time
        self.text = f"delta_time: {delta_time}"
        pass


player = Player()
label = Label()

def update(dt):
    player.update(dt)
    label.update(dt)

@window.event
def on_draw():
    window.clear()
    player.draw()
    label.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time
    delta_time = (x - 400 ) / 400.0


pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
