import pyglet

wavefile_name = 'music/music.wav'
wavefile_name_reverse = 'music/music_reversed.wav'

window = pyglet.window.Window(800, 600)

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
    delta_time = (x - 400) / 400.0
    #player.pitch = delta_time + 1
    player.pitch = abs(delta_time) * 1.4
    #player_reverse.pitch = delta_time*-1 + 1
    player_reverse.pitch = abs(delta_time) * 1.4
    global reversed
    if reversed:
        if delta_time >= 0:
            player_reverse.pause()
            player.play()
            reversed = False
    else:
        if delta_time < 0:
            player.pause()
            player_reverse.play()
            reversed = True


pyglet.app.run()
