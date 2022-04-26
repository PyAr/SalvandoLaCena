import pyglet

from constants import COLCHON, FRAME_ESTADISTICAS, FRAME_TIME, SUBFRAMES, SUELO


class SpriteConHistoria(pyglet.sprite.Sprite):
    def __init__(self, espera, *args, **kwargs):
        self.espera = espera
        self.history = []
        super().__init__(*args, **kwargs)

    def serializar(self):
        raise NotImplementedError

    def restaurar(self, serializado):
        raise NotImplementedError

    def actualizar(self):
        raise NotImplementedError

    def update(self, avanzando, *args, **kwargs):
        if avanzando:
            self.update_avanza(*args, **kwargs)
        else:
            self.update_atras(*args, **kwargs)

    def update_atras(self, *args, **kwargs):
        if len(self.history):
            self.restaurar(self.history.pop())
        else:
            self.espera += FRAME_TIME / SUBFRAMES

    def update_avanza(self, *args, **kwargs):
        if len(self.history) == 0:
            self.history.append(self.serializar())

        if self.espera > 0:
            self.espera -= FRAME_TIME / SUBFRAMES
            self.history.append(self.serializar())
            return

        self.actualizar(*args, **kwargs)
        self.history.append(self.serializar())


class Final(SpriteConHistoria):
    def __init__(self, espera, *args, **kwargs):
        image = pyglet.resource.image("imagenes/final.png")
        super().__init__(espera=espera, img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height

        self.x = 400
        self.y = 0
        self.scale = 0.3

    def serializar(self):
        return (
            self.y,
            self.espera,
        )

    def restaurar(self, serializado):
        (
            self.y,
            self.espera,
        ) = serializado

    def actualizar(self):
        if self.y < 600:
            self.y = min(600, self.y + 40 / SUBFRAMES)


class Pelota(SpriteConHistoria):
    def __init__(self, espera, imagen, *args, **kwargs):
        image = pyglet.resource.image(imagen)
        super().__init__(espera=espera, img=image, *args, **kwargs)

        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        self.scale = 0.5

        self.x = -50
        self.y = 200

        self.vx = 2
        self.vy = 10
        self.vr = 5

        self.muerto = False

    def serializar(self):
        return (
            self.x,
            self.y,
            self.rotation,
            self.vx,
            self.vy,
            self.vr,
            self.muerto,
            self.espera,
        )

    def restaurar(self, serializado):
        (
            self.x,
            self.y,
            self.rotation,
            self.vx,
            self.vy,
            self.vr,
            self.muerto,
            self.espera,
        ) = serializado

    def update(self, direccion, player):
        self.muerto_anterior = self.muerto

        super().update(direccion, player)

        if self.muerto != self.muerto_anterior:
            if self.muerto:
                self.opacity = 80
            else:
                self.opacity = 255

    def actualizar(self, player):
        self.x += self.vx / SUBFRAMES
        self.y += self.vy / SUBFRAMES
        self.vy -= 0.2 / SUBFRAMES
        self.rotation += self.vr / SUBFRAMES

        # Si colisiona con la plataforma
        if self.y < COLCHON and self.y > SUELO:
            if abs(player.x - self.x) < 100:
                self.y = COLCHON
                self.vy = 13
        # Si cae al suelo
        elif self.y <= SUELO:
            self.y = SUELO - 1
            self.vx = 0
            self.vy = 0
            self.vr = 0
            self.muerto = True

        # El objeto llega a la derecha de la pantalla:
        if self.x > 800:
            self.x = 900
            self.vx = 0
            self.vy = 0
            self.vr = 0


class Sombra(SpriteConHistoria):
    def __init__(self, player, *args, **kwargs):
        self.player = player
        super().__init__(espera=0, img=self.player.image, *args, **kwargs)
        self.scale = self.player.scale
        self.x = self.player.x
        self.y = self.player.y
        self.opacity = 128
        self.visible = False

    def serializar(self):
        return (
            self.player.x,
            self.player.image,
        )

    def restaurar(self, serializado):
        (
            self.x,
            self.image,
        ) = serializado

    def update(self, avanzando):
        super().update(avanzando)
        if avanzando and self.visible:
            self.visible = False
        elif not avanzando and not self.visible:
            self.visible = True

    def actualizar(self):
        pass
