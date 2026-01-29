# IA.py
# IA simple Minimax + AlphaBeta 

import random

PIECE_VALUE = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "P": 1
}

CHECKMATE_SCORE = 10_000 # puntuación alta para mate
STALEMATE_SCORE = 0    # puntuación para empate


def _safe_valid_moves(gs):
    """
    Llama gs.getValidMoves() pero restaura checkMate/staleMate después.
    Esto para evitar contaminar el estado real del juego durante la búsqueda.
    """
    old_cm = gs.checkMate
    old_sm = gs.staleMate

    moves = gs.getValidMoves()

    # restaurar flags para no contaminar el estado real
    gs.checkMate = old_cm
    gs.staleMate = old_sm

    return moves


def _material_score(gs):
    """Evaluación básica por material (blancas positivo, negras negativo)."""
    score = 0
    for row in gs.board:
        for piece in row:
            if piece == "--":
                continue
            color = piece[0]
            kind  = piece[1]
            val = PIECE_VALUE.get(kind, 0)
            score += val if color == "w" else -val
    return score


def _terminal_score(gs, no_moves):
    """
    Calcula mate/empate para la posición ACTUAL sin usar gs.checkMate/staleMate.
    """
    if not no_moves:
        return None  # no es terminal

    # Si no hay movimientos legales:
    if gs.inCheck():
        # El que tiene el turno está en jaque y no tiene movimientos => mate.
        # Si es turno de blancas => blancas pierden => score muy negativo.
        return -CHECKMATE_SCORE if gs.whiteToMove else CHECKMATE_SCORE
    else:
        # Sin jaque y sin movimientos => stalemate
        return STALEMATE_SCORE

# Encuentra el mejor movimiento usando Minimax con poda Alpha-Beta
def find_best_move(gs, valid_moves, depth=2): 
    if not valid_moves:
        return None

    random.shuffle(valid_moves) # para variar entre movimientos iguales

    best_move = None 

    if gs.whiteToMove: 
        best_score = -float("inf") # puntuación inicial muy baja
        for mv in valid_moves: # iterar sobre movimientos
            gs.makeMove(mv) # hacer el movimiento
            score = _minimax(gs, depth - 1, -float("inf"), float("inf"), maximizing=False) # evaluar con minimax
            gs.undoMove() # deshacer el movimiento
            if score > best_score: # si la puntuación es mejor, actualizar
                best_score = score # mejor puntuación
                best_move = mv # mejor movimiento
    else: # turno de negras
        best_score = float("inf") # puntuación inicial muy alta
        for mv in valid_moves: # iterar sobre movimientos
            gs.makeMove(mv) # hacer el movimiento
            score = _minimax(gs, depth - 1, -float("inf"), float("inf"), maximizing=True) # evaluar con minimax
            gs.undoMove() # deshacer el movimiento
            if score < best_score: # si la puntuación es mejor, actualizar
                best_score = score # mejor puntuación
                best_move = mv # mejor movimiento

    return best_move  

# Minimax con poda Alpha-Beta
def _minimax(gs, depth, alpha, beta, maximizing):
    moves = _safe_valid_moves(gs) # obtener movimientos legales

    # terminal o profundidad 
    term = _terminal_score(gs, no_moves=(len(moves) == 0)) # verificar si es terminal
    if term is not None: 
        return term # retornar puntuación terminal
    if depth == 0: # profundidad alcanzada
        return _material_score(gs) # evaluar posición

    if maximizing: # turno de blancas
        best = -float("inf") # puntuación inicial muy baja
        for mv in moves: # iterar sobre movimientos
            gs.makeMove(mv) # hacer el movimiento
            score = _minimax(gs, depth - 1, alpha, beta, maximizing=False) # evaluar con minimax
            gs.undoMove() # deshacer el movimiento
            best = max(best, score) # actualizar mejor puntuación 
            alpha = max(alpha, best) # actualizar alpha
            if beta <= alpha: # poda beta
                break 
        return best
    else: # turno de negras
        best = float("inf") # puntuación inicial muy alta
        for mv in moves: # iterar sobre movimientos
            gs.makeMove(mv) # hacer el movimiento
            score = _minimax(gs, depth - 1, alpha, beta, maximizing=True) # evaluar con minimax
            gs.undoMove() # deshacer el movimiento
            best = min(best, score) # actualizar mejor puntuación
            beta = min(beta, best) # actualizar beta
            if beta <= alpha: # poda alpha
                break
        return best
