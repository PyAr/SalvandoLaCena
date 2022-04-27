import pyglet
from pyglet.window import key
pyglet.resource.path = ['..']

window = pyglet.window.Window(800, 600)

keys = key.KeyStateHandler()
window.push_handlers(keys)
joysticks = pyglet.input.get_joysticks()
joystick = None

if joysticks:
    print("Hay un joystick")
    joystick = joysticks[0]

if joystick:
    joystick.open()

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

def update(dt):
    #print(joystick.x)
    player.update(dt)



    pass

@window.event
def on_draw():
    window.clear()
    player.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time
    delta_time = (x - 400 ) / 200.0


pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
