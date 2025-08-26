from typing import Optional, Tuple
from Entidades.juego import Juego, BOLD, RESET, RED
from Exceptions.exceptions import InvalidModeError

def pedir_modo() -> Tuple[bool, Optional[int]]:
    print(f"{BOLD}Modos disponibles:{RESET} [s] Simulación  |  [i] Interactivo")
    modo = input("Elegí modo (s/i): ").strip().lower() or "s"
    if modo not in ("s", "i"):
        raise InvalidModeError("Modo inválido. Usá 's' o 'i'.")
    interactivo = (modo == "i")

    semilla_raw = input("Semilla opcional (enter para aleatoria): ").strip()
    semilla: Optional[int] = None
    if semilla_raw:
        try:
            semilla = int(semilla_raw)
        except ValueError:
            print(f"{RED}Semilla inválida, se usará aleatoria.{RESET}")
            semilla = None
    return interactivo, semilla

def main() -> None:
    interactivo, semilla = pedir_modo()
    if interactivo:
        n1 = input("Nombre del Jugador 1: ").strip() or "J1"
        n2 = input("Nombre del Jugador 2: ").strip() or "J2"
    else:
        n1, n2 = "J1", "J2"

    juego = Juego(n1, n2, interactivo, semilla)
    juego.jugar()

if __name__ == "__main__":
    main()
