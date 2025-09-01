import random
from typing import Dict, Iterator, Optional
from Entidades.jugador import Jugador

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

class Juego:
   
    def __init__(self, j1: str, j2: str, interactivo: bool, semilla: Optional[int] = None):
        self.jugadores = [Jugador(j1), Jugador(j2)]
        self.interactivo = interactivo
        self.rng = random.Random(semilla)
        self.reglas = self.crear_reglas()
        self.turn_gen = self.CambioDeTurno()

    def crear_reglas(self) -> Dict[str, Dict[int, int]]:
        cells = list(range(1, 30))
        self.rng.shuffle(cells)
        mov_positions = cells[:5]
        self.rng.shuffle(cells)
        mon_positions = cells[:5]

        mov_values = [+2, +1, +3, -5, -999]
        mon_values = [+2, +1, +1, -1, -1]

        mov = {pos: delta for pos, delta in zip(mov_positions, mov_values)}
        mon = {pos: delta for pos, delta in zip(mon_positions, mon_values)}
        return {"mov": mov, "mon": mon}

    def crear_tablero(self) -> str:
        def cell_str(i: int) -> str:
            tags = []
            if i in self.reglas.get("mov", {}):
                tags.append("M")
            if i in self.reglas.get("mon", {}):
                tags.append("$")
            tag = "" if not tags else "(" + "".join(tags) + ")"
            if i == self.jugadores[0].posicion and i == self.jugadores[1].posicion:
                mark = MAGENTA + "P12" + RESET
            elif i == self.jugadores[0].posicion:
                mark = BLUE + "P1" + RESET
            elif i == self.jugadores[1].posicion:
                mark = CYAN + "P2" + RESET
            else:
                mark = f"{i:02d}"
            return f"{mark}{tag}"

        line = " ".join(map(cell_str, range(1, 31)))

        info = (
            f"{BOLD}P1{RESET}={self.jugadores[0]}  |  "
            f"{BOLD}P2{RESET}={self.jugadores[1]}"
        )
        legend = f"{DIM}M=movimiento $=monedas{RESET}"
        return f"\n{line}\n{info}\n{legend}\n"

    def TirarDado(self) -> int:
        return self.rng.randint(1, 6)

    def CambioDeTurno(self) -> Iterator[int]:
        idx = 0
        while True:
            yield idx % 2
            idx += 1


    def Condicion_para_ganar(self, j: Jugador) -> bool:
        return j.posicion >= 30 and j.monedas > 0

    def Condicion_para_perder(self, j: Jugador) -> bool:
        return j.monedas <= 0

    def loop(self) -> None:
        print(self.crear_tablero())

        if any(self.Condicion_para_ganar(j) for j in self.jugadores):
            ganador = next(filter(self.Condicion_para_ganar, self.jugadores))
            print(f"\n{GREEN} Ganó {ganador.nombre} !{RESET}")
            return
        perdedor = next(filter(self.Condicion_para_perder, self.jugadores), None)

        if perdedor:
            ganador = next(j for j in self.jugadores if j is not perdedor)
            print(f"\n{RED} {perdedor.nombre} se quedó sin monedas {RESET}")
            print(f"{GREEN} Gana {ganador.nombre} ! {RESET}")
            return

        idx = next(self.turn_gen)
        jugador = self.jugadores[idx]

        if self.interactivo:
            input(f"{BOLD}Turno de {jugador.nombre}{RESET}. Tocá ENTER para tirar el dado ")

        d = self.TirarDado()
        pos_antes = jugador.posicion
        mon_antes = jugador.monedas

        jugador.mover(d)

        if jugador.posicion in self.reglas["mov"]:
            jugador.aplicar_efecto_movimiento(self.reglas["mov"][jugador.posicion])
        if jugador.posicion in self.reglas["mon"]:
            jugador.aplicar_efecto_monedas(self.reglas["mon"][jugador.posicion])

        print(
            f"{BOLD}Jugador:{RESET} {jugador.nombre}  "
            f"{BOLD}Dado:{RESET} {d}  "
            f"{BOLD}Pos:{RESET} {pos_antes}→{jugador.posicion}  "
            f"{BOLD}Mon:{RESET} {mon_antes}→{jugador.monedas}"
        )

        if not self.interactivo:
            try:
                import time
                time.sleep(1)
            except Exception:
                pass

        self.loop()

    def jugar(self) -> None:
        print(f"{BOLD}Las reglas de movimiento son:{RESET} {self.reglas['mov']}")
        print(f"{BOLD}Las reglas para las monedas son:{RESET} {self.reglas['mon']}")
        print(f"\n{BOLD}¡Empieza el juegoooo!{RESET}")
        self.loop()