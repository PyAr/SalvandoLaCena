import pyglet

window = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_DEFAULT)

titulo = pyglet.text.Label('Salvando La Cena',
                          font_name='Arial',
                          font_size=36,
                          x=window.width//2, 
                          y=window.height//1.2,
                          anchor_x='center', 
                          anchor_y='center')

empezar = pyglet.text.Label('Cualquier tecla\npara comenzar',
                          font_name='Arial',
                          multiline=True,
                          font_size=20,
                          x=window.width//1.9, 
                          y=window.height//2.5,
                          width=200,
                          anchor_x='center', 
                          anchor_y='center')

fondo = pyglet.resource.image("imagenes/fondo.png")
jugador_1 = pyglet.resource.image("imagenes/jugador1.png")
jugador_2 = pyglet.resource.image("imagenes/jugador2.png")

x = 0

def update(dt):
    global x


pyglet.clock.schedule_interval(update, 1/120.0)

@window.event
def on_draw():
    global x
    window.clear()
    fondo.blit(0, 0)
    jugador_1.blit(x, 75)
    jugador_2.blit(400, 75)
    titulo.draw()
    empezar.draw()

pyglet.app.run()
