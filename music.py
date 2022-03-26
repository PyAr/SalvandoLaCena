import pyglet

wavefile_name = 'music/music.wav'
wavefile_name_reverse = 'music/music_reversed.wav'

window = pyglet.window.Window()

song = pyglet.media.load(wavefile_name)
reversed_song = pyglet.media.load(wavefile_name_reverse)
player = pyglet.media.Player()
player_reverse = pyglet.media.Player()

player.queue(song)
player.loop = True
player_reverse.queue(reversed_song)
player_reverse.loop = True
player.play()

reversed = False


@window.event
def on_draw():
    window.clear()


@window.event
def on_mouse_motion(x, y, dx, dy):
    player.pitch = x/200.0
    global reversed
    if reversed:
        if x > 400:
            player_reverse.pause()
            player.play()
            reversed = False
    else:
        if x < 400:
            player.pause()
            player_reverse.play()
            reversed = True


pyglet.app.run()
