#loop de turnos (while)
# interactivo: pedimos un input 
# simulacion: esperamos un tiempo
# se gana cuando un jugador llega a la casilla 30 (sin rebote). La minima casilla es la 0
# Para ganar el jugador debe tener almenos una moneda
# Si llegas a 30 con 0 monedas perdes (gana el otro)
# hay que mostrar el juego en cada linea de comando
# jugador uno y dos deben estar con distintos colores

#Premios
# 3 casillas con premios de movimiento: una avanza 2 lugares, otra avanza 1 lugar y otra avanza 3.
# 2 casillas de castigo de movimiento, una que haga volver al principio y otra que lo haga retroceder 5 lugares.
# 3 casillas con premios económicos: 1 con +2 monedas, 1 con +1 moneda, 1 con +1 # moneda.
# 2 casillas de castigo económico, que hacen que el jugador devuelva 1 moneda, si tiene al menos 1. 
# las casillas de premios/castigos economicos y premios/castigos de movimiento pueden coincidir (son random)


import random
from typing import Dict, Iterator, Optional
from Entidades.jugador import Jugador

# Colores para la consola (ANSI)
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
    """
    Juego de tablero simplificado:
      - 30 casillas
      - 2 jugadores
      - Reglas aleatorias de movimiento y monedas
      - Modo simulación o interactivo
    """
    def __init__(self, j1: str, j2: str, interactive: bool, seed: Optional[int] = None):
        self.jugadores = [Jugador(j1), Jugador(j2)]
        self.interactive = interactive
        self.rng = random.Random(seed)
        self.rules = self._build_rules()
        self.turn_gen = self._turn_order()

    # ---------- Reglas aleatorias ----------
    def _build_rules(self) -> Dict[str, Dict[int, int]]:
        """
        Genera posiciones aleatorias para:
          mov: +2, +1, +3, -5, -999 (volver al inicio)
          mon: +2, +1, +1, -1, -1
        Las posiciones de 'mov' y 'mon' pueden coincidir.
        """
        cells = list(range(1, 30))   # casillas válidas para efectos (1..29)
        self.rng.shuffle(cells)
        mov_positions = cells[:5]
        self.rng.shuffle(cells)
        mon_positions = cells[:5]

        mov_values = [+2, +1, +3, -5, -999]  # -999 = volver al inicio
        mon_values = [+2, +1, +1, -1, -1]

        mov = {pos: delta for pos, delta in zip(mov_positions, mov_values)}
        mon = {pos: delta for pos, delta in zip(mon_positions, mon_values)}
        return {"mov": mov, "mon": mon}

    # ---------- Orden de turnos ----------
    def _turn_order(self) -> Iterator[int]:
        idx = 0
        while True:
            yield idx % 2
            idx += 1

    # ---------- Dado ----------
    def _roll_dice(self) -> int:
        return self.rng.randint(1, 6)

    # ---------- Tablero ----------
    def _render_board(self) -> str:
        def cell_str(i: int) -> str:
            tags = []
            if i in self.rules.get("mov", {}):
                tags.append("M")
            if i in self.rules.get("mon", {}):
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

        line = " ".join(cell_str(i) for i in range(1, 31))
        info = (
            f"{BOLD}P1{RESET}={self.jugadores[0]}  |  "
            f"{BOLD}P2{RESET}={self.jugadores[1]}"
        )
        legend = f"{DIM}Leyenda: (M)=movimiento ($)=monedas{RESET}"
        return f"\n{line}\n{info}\n{legend}\n"

    # ---------- Condiciones de fin ----------
    def _winner_condition(self, j: Jugador) -> bool:
        return j.posicion >= 30 and j.monedas > 0

    def _loser_condition(self, j: Jugador) -> bool:
        return j.monedas <= 0

    # ---------- API pública ----------
    def jugar(self) -> None:
        print(f"{BOLD}Reglas de movimiento:{RESET} {self.rules['mov']}")
        print(f"{BOLD}Reglas económicas:{RESET} {self.rules['mon']}")
        print(f"\n{BOLD}¡Comienza la partida!{RESET}")
        self._loop()

    # ---------- Bucle principal (recursivo para simplicidad) ----------
    def _loop(self) -> None:
        # Mostrar tablero
        print(self._render_board())

        # ¿Hay ganador?
        if any(self._winner_condition(j) for j in self.jugadores):
            ganador = next(j for j in self.jugadores if self._winner_condition(j))
            print(f"\n{GREEN}🏆 {ganador.nombre} gana la partida!{RESET}")
            return

        # ¿Alguien quedó sin monedas?
        perdedor = next((j for j in self.jugadores if self._loser_condition(j)), None)
        if perdedor:
            ganador = next(j for j in self.jugadores if j is not perdedor)
            print(f"\n{RED}💀 {perdedor.nombre} se quedó sin monedas.{RESET}")
            print(f"{GREEN}🏆 {ganador.nombre} gana por abandono.{RESET}")
            return

        # Turno
        idx = next(self.turn_gen)
        jugador = self.jugadores[idx]

        if self.interactive:
            input(f"{BOLD}Turno de {jugador.nombre}{RESET}. Presioná ENTER para tirar el dado… ")

        d = self._roll_dice()
        pos_antes = jugador.posicion
        mon_antes = jugador.monedas

        jugador.mover(d)

        # Efectos de casilla
        if jugador.posicion in self.rules["mov"]:
            jugador.aplicar_efecto_movimiento(self.rules["mov"][jugador.posicion])
        if jugador.posicion in self.rules["mon"]:
            jugador.aplicar_efecto_monedas(self.rules["mon"][jugador.posicion])

        print(
            f"{BOLD}Jugador:{RESET} {jugador.nombre}  "
            f"{BOLD}Dado:{RESET} {d}  "
            f"{BOLD}Pos:{RESET} {pos_antes}→{jugador.posicion}  "
            f"{BOLD}Mon:{RESET} {mon_antes}→{jugador.monedas}"
        )

        # Pausa corta en simulación para visualizar
        if not self.interactive:
            try:
                import time
                time.sleep(0.6)
            except Exception:
                pass

        # Siguiente paso (recursivo)
        self._loop()
