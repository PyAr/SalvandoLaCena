import random

import pyglet
from pyglet.window import key

from constants import FRAME_ESTADISTICAS


class Lluvia(pyglet.sprite.Sprite):
    def __init__(
        self, nombre_imagen="imagenes/lluvia-02.png", velocidad=200, *args, **kwargs
    ):
        self.velocidad = velocidad
        self.delta_time = kwargs['delta_time']
        del(kwargs['delta_time'])
        image = pyglet.resource.image(nombre_imagen)
        self.textura = pyglet.image.TileableTexture.create_for_image(image)
        super().__init__(img=image, *args, **kwargs)

    def draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.textura.blit_tiled(0, 0, 0, 800, 600)

    def update(self, dt):
        self.textura.anchor_y += dt * self.delta_time * self.velocidad


class Chispear(pyglet.sprite.Sprite):
    imagenes = [
        pyglet.resource.image("imagenes/chispear_0.png"),
        pyglet.resource.image("imagenes/chispear_1.png"),
        pyglet.resource.image("imagenes/chispear_2.png"),
        pyglet.resource.image("imagenes/chispear_3.png"),
    ]
    for i in imagenes:
        i.anchor_x = i.width / 2

    def __init__(self, seed, freq=10, desfase=0, get_current_frame=None, *args, **kwargs):
        self.get_current_frame = get_current_frame
        self.seed = seed
        self.freq = freq
        self.desfase = desfase
        super().__init__(img=self.imagenes[0], *args, **kwargs)
        self.last_frame = float("inf")
        self.rng = random.Random()
        self.opacity = 200
        self.scale = 0.6
        self.frames_repetidos = 2

    def punto_en_suelo(self):
        return (
            self.rng.randint(0, 800),
            self.rng.randint(0, 80),
        )

    def punto_en_techo(self):
        rx = self.rng.random()
        ry = self.rng.random() * rx
        return (
            600 + rx * 200,
            410 + ry * 100,
        )

    def update(self):
        current_frame = self.get_current_frame()
        frame = (current_frame + self.desfase) % self.freq
        if frame < len(self.imagenes) * self.frames_repetidos:
            if current_frame + self.desfase - frame != self.last_frame:
                self.last_frame = current_frame + self.desfase - frame
                self.rng.seed(current_frame + self.desfase - frame + self.seed)

                f = random.choice([self.punto_en_techo, self.punto_en_suelo])
                self.x, self.y = f()

            self.visible = True
            self.image = self.imagenes[int(frame / self.frames_repetidos)]
        else:
            self.visible = False


class Fondo(pyglet.sprite.Sprite):
    def __init__(self, imagen, *args, **kwargs):
        self.imagen = imagen
        image = pyglet.resource.image(self.imagen)
        super().__init__(img=image, *args, **kwargs)


class Title(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/title.png")
        super().__init__(img=image, *args, **kwargs)



class Estadisticas(pyglet.graphics.Batch):
    def __init__(self, window, objetos, get_current_frame):
        super().__init__()
        self.titulo = pyglet.text.Label(
            font_name="Sans Serif",
            font_size=30,
            color=(40, 40, 40, 255),
            bold=True,
            x=window.width / 2,
            y=window.height / 2 + 50,
            anchor_x="center",
            anchor_y="center",
            batch=self,
        )

        self.labels = []
        for i in range(7):
            self.labels.append(
                pyglet.text.Label(
                    font_name="Sans Serif",
                    font_size=20,
                    color=(40, 40, 40, 255),
                    bold=True,
                    x=window.width / 2,
                    y=window.height / 2 - 40 * i,
                    anchor_x="center",
                    anchor_y="center",
                    batch=self,
                )
            )
        self.objetos = objetos
        self.actualizado = False
        self.get_current_frame = get_current_frame

    def actualizar(self):
        todos_salvados = True
        objetos = self.objetos
        for o in objetos:
            if o.muerto:
                todos_salvados = False
                break

        if todos_salvados:
            self.titulo.text = "¡SALVASTE TODO!"
        else:
            self.titulo.text = "Lograste salvar…"

        """
        0: comida
        1: sombrero
        2: tech
        3: comida
        4: oveja
        5: logo
        6: bebida
        7: tech
        8: bebida
        9: leña
        """

        comidas = 0
        if not objetos[0].muerto:
            comidas += 1
        if not objetos[3].muerto:
            comidas += 1

        bebidas = 0
        if not objetos[6].muerto:
            bebidas += 1
        if not objetos[8].muerto:
            bebidas += 1

        tech = 0
        if not objetos[2].muerto:
            tech += 1
        if not objetos[7].muerto:
            tech += 1

        self.labels[0].text = f"{comidas} de 2 comidas"
        self.labels[1].text = f"{bebidas} de 2 bebidas"
        self.labels[2].text = f"{tech} de 2 artefactos tecnológicos"
        self.labels[3].text = ("ningún" if objetos[1].muerto else "un") + " sombrero"
        self.labels[4].text = ("ninguna" if objetos[4].muerto else "una") + " oveja"
        self.labels[5].text = ("ningún" if objetos[5].muerto else "un") + " logo"
        self.labels[6].text = ("no hay" if objetos[9].muerto else "habemus") + " leña"

    def update(self):
        if self.get_current_frame() < FRAME_ESTADISTICAS:
            if self.actualizado:
                self.actualizado = False
        else:
            if not self.actualizado:
                self.actualizar()
                self.actualizado = True



#class Label(pyglet.text.Label):
#    def __init__(self):
#        super().__init__(y=20, x=20, font_size=30)
#
#    def update(self, dt):
#        global delta_time
#        self.text = f"velocidad: {delta_time:.2f}, frame: {get_current_frame()}"
#

class Player(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        imagenes = [
            pyglet.resource.image("imagenes/player.png"),
            pyglet.resource.image("imagenes/player_1.png"),
            pyglet.resource.image("imagenes/player_2.png"),
        ]
        for image in imagenes:
            image.anchor_x = image.width / 2
            image.anchor_y = image.height / 2

        self.joystick = kwargs['joystick']
        del(kwargs['joystick'])
        self.para_atras = kwargs['para_atras']
        del(kwargs['para_atras'])
        self.keys = kwargs['keys']
        del(kwargs['keys'])


        super().__init__(img=imagenes[1], *args, **kwargs)

        self.idx_animacion = 0
        self.animacion = [
            imagenes[0],
            imagenes[1],
            imagenes[0],
            imagenes[2],
        ]
        self.dt_ani_accum = 0
        self.tiempo_animacion = 0.05

        self.scale = 0.8

        self.x = 100
        self.y = 80

    def update(self, dt):
        joystick = self.joystick
        para_atras = self.para_atras
        x_anterior = self.x
        keys = self.keys

        if joystick:
            if joystick.x < -0.2 or joystick.x > 0.2:
                self.x += joystick.x * 20

        if keys[key.RIGHT]:
            self.x += 10
        elif keys[key.LEFT]:
            self.x -= 10

        if self.x <= 80:
            self.x = 80

        if self.x > 800 - 80:
            self.x = 800 - 80

        # entre 0 y 20
        dx = abs(self.x - x_anterior)

        if dx == 0 and (self.idx_animacion != 0 or self.idx_animacion != 2):
            self.idx_animacion = 0
            self.image = self.animacion[0]
        else:
            if self.dt_ani_accum + dt < self.tiempo_animacion * 20 / dx:
                self.dt_ani_accum += dt
            else:
                self.dt_ani_accum = 0
                if self.idx_animacion + 1 < len(self.animacion):
                    self.idx_animacion += 1
                else:
                    self.idx_animacion = 0
                self.image = self.animacion[self.idx_animacion]


class Reloj(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        image = pyglet.resource.image("imagenes/reloj.png")
        super().__init__(img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2

        self.x = 50
        self.y = 545
        self.scale = 0.3
        self.opacity = 128

    def update(self, delta_time):
        self.rotation = delta_time * 90



