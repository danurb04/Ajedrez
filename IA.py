# IA.py
# IA simple Minimax + AlphaBeta SIN contaminar gs.checkMate/gs.staleMate

import random

PIECE_VALUE = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "P": 1
}

CHECKMATE_SCORE = 10_000
STALEMATE_SCORE = 0


def _safe_valid_moves(gs):
    """
    Llama gs.getValidMoves() PERO restaura checkMate/staleMate para que
    la IA no deje esos flags "pegados" en el estado real del juego.
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


def find_best_move(gs, valid_moves, depth=2):
    if not valid_moves:
        return None

    random.shuffle(valid_moves)

    best_move = None

    if gs.whiteToMove:
        best_score = -float("inf")
        for mv in valid_moves:
            gs.makeMove(mv)
            score = _minimax(gs, depth - 1, -float("inf"), float("inf"), maximizing=False)
            gs.undoMove()
            if score > best_score:
                best_score = score
                best_move = mv
    else:
        best_score = float("inf")
        for mv in valid_moves:
            gs.makeMove(mv)
            score = _minimax(gs, depth - 1, -float("inf"), float("inf"), maximizing=True)
            gs.undoMove()
            if score < best_score:
                best_score = score
                best_move = mv

    return best_move


def _minimax(gs, depth, alpha, beta, maximizing):
    moves = _safe_valid_moves(gs)

    # terminal o profundidad
    term = _terminal_score(gs, no_moves=(len(moves) == 0))
    if term is not None:
        return term
    if depth == 0:
        return _material_score(gs)

    if maximizing:
        best = -float("inf")
        for mv in moves:
            gs.makeMove(mv)
            score = _minimax(gs, depth - 1, alpha, beta, maximizing=False)
            gs.undoMove()
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float("inf")
        for mv in moves:
            gs.makeMove(mv)
            score = _minimax(gs, depth - 1, alpha, beta, maximizing=True)
            gs.undoMove()
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best
