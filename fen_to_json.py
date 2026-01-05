'''
Convierte notación de tableros FEN (Notación Forsyth-Edwards) a un archivo .json que el Engine puede leer como tablero inicial 
'''

import json
from pathlib import Path


#asigna el valor correspondiente a cada pieza de la notación FEN con la utilizada en Engine.
FEN_TO_PIECE = {
    "p": "bP", "r": "bR", "n": "bN", "b": "bB", "q": "bQ", "k": "bK",
    "P": "wP", "R": "wR", "N": "wN", "B": "wB", "Q": "wQ", "K": "wK",
}


'''
Convierte FEN a:
- board: lista 8x8
- whiteToMove: bool
Verifica errores de sintaxis en el FEN (número de filas, caracteres que no coinciden, no incluir turno, etc)
'''
def fen_to_board(fen: str):

    parts = fen.strip().split()
    if len(parts) < 2:
        raise ValueError("FEN inválido. Debe incluir tablero y turno (w o b).")

    board_part = parts[0]
    turn_part = parts[1]

    rows = board_part.split("/") #el separador de columan en FEN es "/"
    if len(rows) != 8:
        raise ValueError("FEN inválido: el tablero debe tener 8 filas.")

    board = []
    for row in rows:
        row_list = []
        for ch in row:
            if ch.isdigit():
                row_list.extend(["--"] * int(ch))
            else:
                if ch not in FEN_TO_PIECE:
                    raise ValueError(f"Carácter FEN desconocido: {ch}")
                row_list.append(FEN_TO_PIECE[ch])
        if len(row_list) != 8:
            raise ValueError("FEN inválido: una fila no tiene 8 columnas.")
        board.append(row_list)

    if turn_part not in ("w", "b"):
        raise ValueError("FEN inválido: el turno debe ser 'w' o 'b'.")

    whiteToMove = (turn_part == "w")
    return board, whiteToMove



'''
Verifica condiciones correctas en sintaxis pero sin sentido en ajedrez, para evitar problemas con el Engine
Más de dos reyes, más de 16 piezas por jugador, etc, peones en filas de promoción, etc.
'''

def validate_board_basic(board):


    # Contadores
    wK = bK = 0
    wP = bP = 0
    wPieces = 0
    bPieces = 0

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == "--":
                continue

            color = piece[0]
            kind = piece[1]

            if color == "w":
                wPieces += 1
            elif color == "b":
                bPieces += 1
            else:
                raise ValueError(f"Pieza inválida encontrada: {piece}")

            # Reyes
            if piece == "wK":
                wK += 1
            elif piece == "bK":
                bK += 1

            # Peones
            if piece == "wP":
                wP += 1
                # Peón blanco no puede estar en la fila 0 (rank 8)
                if r == 0:
                    raise ValueError("Peón blanco en la fila 8 (inválido).")
            elif piece == "bP":
                bP += 1
                # Peón negro no puede estar en la fila 7 (rank 1)
                if r == 7:
                    raise ValueError("Peón negro en la fila 1 (inválido).")

    # Validación de reyes: exactamente 1 de cada
    if wK != 1 or bK != 1:
        raise ValueError(f"Reyes inválidos: wK={wK}, bK={bK}. Debe haber exactamente 1 de cada.")

    # Máximo de piezas
    if wPieces > 16:
        raise ValueError(f"Demasiadas piezas blancas: {wPieces} (máximo 16).")
    if bPieces > 16:
        raise ValueError(f"Demasiadas piezas negras: {bPieces} (máximo 16).")

    # Máximo de peones
    if wP > 8:
        raise ValueError(f"Demasiados peones blancos: {wP} (máximo 8).")
    if bP > 8:
        raise ValueError(f"Demasiados peones negros: {bP} (máximo 8).")



'''
Se encarga de manejar los inputs del usuario y generar el archivo .json en el directorio "posiciones".
'''

def main():
    print("===================================")
    print(" Conversor FEN → JSON (Ajedrez)")
    print("===================================")
    print("Escriba el FEN del tablero.")
    print("Ejemplo:")
    print("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w")
    print("-----------------------------------")

    fen = input("FEN: ").strip()

    try:
        board, whiteToMove = fen_to_board(fen)
        validate_board_basic(board)
    except Exception as e:
        print(f"\n Error: {e}")
        input("Presione ENTER para salir...")
        return

    print("\nEscriba el nombre del archivo (sin .json):")
    filename = input("Nombre: ").strip()

    if filename == "":
        print("\n Nombre inválido.")
        input("Presione ENTER para salir...")
        return

    # Crear carpeta posiciones si no existe
    out_dir = Path("posiciones")
    out_dir.mkdir(exist_ok=True)

    out_path = out_dir / f"{filename}.json"

    data = {
        "whiteToMove": whiteToMove,
        "board": board
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("\n Archivo creado correctamente:")
    print(out_path.resolve())
    input("\nPresione ENTER para salir...")


if __name__ == "__main__":
    main()
