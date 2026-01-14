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

        position_id, board, white_to_move = msg

        # Cargar snapshot del estado en el engine
        gs.load_position(board, white_to_move)

        valid_moves = gs.getValidMoves()
        resp_q.put((position_id, _serialize_moves(valid_moves), gs.checkMate, gs.staleMate))