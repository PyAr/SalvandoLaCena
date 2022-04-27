import pyglet
from pyglet.window import key
pyglet.resource.path = ['..']

window = pyglet.window.Window(800, 600)

class Player(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        self.vy = -5
        image = pyglet.resource.image("imagenes/ball.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 2

        self.x = 200
        self.y = 600

        # TODO: intentar hacer que el movimiento se conecte
        #       o sea "tileable"

    def update(self, dt):
       self.y -= self.vy
       self.vy += 0.2
       self.x += 2
       if self.y < 0:
         self.y = 0
         self.vy *= -1
       if self.x > 800:
       	 self.x = 0
       self.rotation += 3.10

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
