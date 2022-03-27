import pyglet
import pyglet.window.key
from pyglet.window import mouse
from pyglet import shapes
import time

#global window
window = pyglet.window.Window(style = pyglet.window.Window.WINDOW_STYLE_DIALOG, resizable = True, caption = 'Salvando La Cena')
window.set_size(720, 560)

window_min = (720, 560)
window_max = (1280, 720)
default_ratio = (16, 9)


def update(dt):
	global x
	makeMenu(window_min[0], window_min[1])
	
pyglet.clock.schedule_interval(update, 1/120.0)

@window.event
def on_draw():
	global x
	
	
@window.event
def on_key_press(symbol, modifier):
	#Si se presiona la tecla ESCAPE:
	if symbol == pyglet.window.key.ESCAPE:
		window.close()
@window.event
def on_mouse_press(x, y, button, modifiers):
	if mouse.LEFT:
		window = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_DIALOG, resizable = True, caption = 'Salvando La Cena')

background = pyglet.resource.image("images/background.png")
batch = pyglet.graphics.Batch()

def makeMenu(length, height):
	
	horizontal_middle = length/2
	vertical_middle = height/2
	
	#Boton de Inicio
	button_1 = shapes.Rectangle(horizontal_middle - 100, vertical_middle + 50, 200, 40,color=(0, 0, 0), batch=batch)
	
	#Boton para Cerrar
	Button_2 = shapes.Rectangle(horizontal_middle - 120, vertical_middle - 10, 240, 40,color=(0, 0, 0) ,batch=batch)
	
	#Texto de boton 1
	label_1 = pyglet.text.Label('Iniciar',
								font_name='Calibri',
								font_size=20,
								x= horizontal_middle - 45,
								y= vertical_middle + 60)

	#Texto de boton 2
	label_2 = pyglet.text.Label('Cerrar = ESCAPE',
								font_name='Calibri',
								font_size=20,
								x= horizontal_middle - 115,
								y= vertical_middle)

	#Actually draw the stuff
	
	window.clear()
	background.blit(0, 0)
	batch.draw()
	label_1.draw()
	label_2.draw()
	

pyglet.app.run()
