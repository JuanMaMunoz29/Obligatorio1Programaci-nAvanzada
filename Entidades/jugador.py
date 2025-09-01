from functools import reduce

class Jugador:
    def __init__(self, nombre: str, posicion: int = 0, monedas: int = 2):
        self.nombre = nombre
        self.posicion = posicion
        self.monedas = monedas

    def mover(self, pasos: int) -> None:
        self.posicion = min(30, self.posicion + pasos)

    def aplicar_efecto_movimiento(self, delta: int) -> None:
        if delta == -999:
            self.posicion = 0
        else:
            self.posicion = reduce(
                lambda v, f: f(v),
                [
                    lambda v: v + delta,
                    lambda v: min(30, v),
                    lambda v: max(0, v),
                ],
                self.posicion
            )

    def aplicar_efecto_monedas(self, delta: int) -> None:
        if delta < 0:
            if self.monedas > 0:
                self.monedas -= 1
        else:
            self.monedas += delta

    def __str__(self) -> str:
        return f"{self.nombre} pos={self.posicion} mon={self.monedas}"




    