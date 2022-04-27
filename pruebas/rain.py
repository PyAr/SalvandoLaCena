import pyglet
pyglet.resource.path = ['..']

window = pyglet.window.Window(800, 600)
delta_time = 1


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


class Label(pyglet.text.Label):

    def __init__(self):
        super().__init__(text="test", y=10, x=10, font_size=20)

    def update(self, dt):
        global delta_time
        self.text = f"delta_time: {delta_time}"
        pass


capas = [
    Lluvia("imagenes/lluvia-02.png", velocidad=800),
    Lluvia("imagenes/lluvia-01.png", velocidad=1200),
]

label = Label()

def update(dt):
    for capa in capas:
        capa.update(dt)
    label.update(dt)

@window.event
def on_draw():
    window.clear()
    for capa in capas:
        capa.draw()
    label.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global delta_time
    delta_time = (x - 400 ) / 200.0


pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
