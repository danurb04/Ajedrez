# mp_worker.py
from multiprocessing import Queue
import Engine

def _serialize_moves(moves):
    # Regresamos solo coordenadas para que sea fácil de enviar por Queue
    return [(m.startRow, m.startCol, m.endRow, m.endCol) for m in moves]

def worker_loop(req_q: Queue, resp_q: Queue):
    gs = Engine.GameState()

    while True:
        msg = req_q.get()
        if msg is None:
            break

        if len(msg) == 3: #mensaje simple
            position_id, board, white_to_move = msg
            en_passant = ()
            castle_tuple = None
        elif len(msg) == 5: #mensaje con información de en passant y enroque
            position_id, board, white_to_move, en_passant, castle_tuple = msg
        else:
            # si llega algo raro se ignora
            continue

        # Cargar snapshot del estado en el engine
        gs.load_position(board, white_to_move)

        #Aplicar las extras si vinieran
        gs.enPassantPossible = en_passant if en_passant is not None else ()

        if castle_tuple is not None:
            wks, wqs, bks, bqs = castle_tuple
            gs.currentCastlingRights.wks = bool(wks)
            gs.currentCastlingRights.wqs = bool(wqs)
            gs.currentCastlingRights.bks = bool(bks)
            gs.currentCastlingRights.bqs = bool(bqs)

        valid_moves = gs.getValidMoves()
        resp_q.put((position_id, _serialize_moves(valid_moves), gs.checkMate, gs.staleMate))