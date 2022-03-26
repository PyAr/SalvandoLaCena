import pyglet

window = pyglet.window.Window()
source = pyglet.media.load('music/music.wav')
player = pyglet.media.Player()
player.queue(source)
player.play()


@window.event
def on_draw():
    window.clear()

@window.event
def on_mouse_motion(x, y, dx, dy):
    player.pitch = x/200.0
    player.volume = y/100

pyglet.app.run()
