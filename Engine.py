# Estado e informacion del juego, asi como reglas y logica de movimiento, ademas de un historial
class GameState():
    def __init__(self):
        #Tablero 8x8 representado como una lista de listas
        #Primer caracter representa el color (b o w)
        #Segundo caracter representa el tipo de pieza (Pawn(Peon), Rook(Torre), kNight(Caballo), Bishhop(Alfil), Queen, King)
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP" , "wP" , "wP" , "wP" , "wP" , "wP" , "wP" , "wP"],
            ["wR" , "wN" , "wB" , "wQ" , "wK" , "wB" , "wN" , "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []

        # Rastrear posición de los reyes, para verficar jaques
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.checkMate = False
        self.staleMate = False

    """
    Hacer un movimiento (no valida si es legal)
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" #Vaciar la casilla de inicio
        self.board[move.endRow][move.endCol] = move.pieceMoved #Colocar la pieza en la casilla destino
        self.moveLog.append(move) #Agregar el movimiento al historial
        self.whiteToMove = not self.whiteToMove #Cambiar el turno

        # Actualizar posición de los reyes:
        if move.pieceMoved == 'wK':
            self.whiteKingLocation= (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
         

    def undoMove(self):
        if len(self.moveLog) != 0:  
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Actualiza posición del rey
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
    """
    Obtener todos los movimientos validos considerando jaques:
    """
    def getValidMoves(self): # Devuelve solo los movimientos posibles (contemplando pins)
        moves = self.getAllPossibleMoves()

        for i in range(len(moves)-1, -1, -1): 
            self.makeMove(moves[i])
            # Por recomendación, se recorre la lista desde el final,
            # para evitar que al borrar elementos, el programa se brinque los repetidos

            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()  
        if len(moves) == 0: #no hay movimientos, es mate o empate
            if self.inCheck():
                self.checkMate = True
            else:
                self.checkMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves
    
    '''
    Revisa si el enemigo puede atacar ese espacio
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # Cambiar turno
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Cambiar turno de nuevo
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    Revisa si el jugador actual está en jaque
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Obtener todos los movimientos posibles sin considerar jaques
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #Recorrer filas
            for c in range(len(self.board[r])): #Recorrer columnas
                turno = self.board[r][c][0] #Primer caracter representa el color de la pieza
                if (turno == 'w' and self.whiteToMove) or (turno == 'b' and not self.whiteToMove): #Pieza del jugador actual
                    pieza = self.board[r][c][1]
                    if pieza == 'P':
                        self.getPawnMoves(r, c, moves)
                    elif pieza == 'R':
                        self.getRookMoves(r, c, moves)
                    elif pieza == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif pieza == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif pieza == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif pieza == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    """
    Obtener todos los movimientos de peon en la posicion (r, c)
    """
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #Movimiento de peon blanco
            if self.board[r-1][c] == "--": #Movimiento hacia adelante si la casilla esta vacia
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #Movimiento inicial de dos casillas si las casillas estan vacias
                    moves.append(Move((r, c), (r-2, c), self.board))
            #Capturas
            if c-1 >= 0: #Captura a la izquierda
                if self.board[r-1][c-1][0] == 'b': #Pieza negra para capturar
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <=7: #Captura a la derecha
                if self.board[r-1][c+1][0] == 'b': #Pieza negra para capturar
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: #Movimiento de peon negro
            if self.board[r+1][c] == "--": #Movimiento hacia adelante si la casilla esta vacia
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #Movimiento inicial de dos casillas si las casillas estan vacias
                    moves.append(Move((r, c), (r+2, c), self.board))
            #Capturas
            if c-1 >= 0: #Captura a la izquierda
                if self.board[r+1][c-1][0] == 'w': #Pieza blanca para capturar
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <=7: #Captura a la derecha
                if self.board[r+1][c+1][0] == 'w': #Pieza blanca para capturar
                    moves.append(Move((r, c), (r+1, c+1), self.board))
        return

    """
    Obtener todos los movimientos de torre en la posicion (r, c)
    """
    def getRookMoves(self, r, c, moves):
        direcciones = [(-1, 0), (0, -1), (1, 0), (0, 1)] #Arriba, Izquierda, Abajo, Derecha
        enemigoColor = "b" if self.whiteToMove else "w" #Color del enemigo
        for d in direcciones: #Iterar sobre todas las direcciones posibles
            for i in range(1,8): 
                filaDestino = r + d[0]*i
                colDestino = c + d[1]*i
                if 0 <= filaDestino < 8 and 0 <= colDestino <8: #Dentro del tablero
                    casillaDestino = self.board[filaDestino][colDestino] #Contenido de la casilla destino?
                    if casillaDestino == "--": #Casilla vacia
                        moves.append(Move((r, c), (filaDestino, colDestino), self.board))
                    elif casillaDestino[0] == enemigoColor: #Casilla con pieza enemiga
                        moves.append(Move((r, c), (filaDestino, colDestino), self.board))
                        break #No puede saltar sobre piezas
                    else: #Casilla con pieza propia
                        break
                else: #Fuera del tablero
                    break
        return

    """
    Obtener todos los movimientos de caballo en la posicion (r, c)
    """
    def getKnightMoves(self, r, c, moves):
        direcciones = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)] #Movimientos de caballo en L
        enemigoColor = "b" if self.whiteToMove else "w" #Color del enemigo
        for d in direcciones:
            filaDestino = r + d[0]
            colDestino = c + d[1]
            if 0 <= filaDestino < 8 and 0 <= colDestino <8:
                casillaDestino = self.board[filaDestino][colDestino]
                if casillaDestino == "--" or casillaDestino[0] == enemigoColor:
                    moves.append(Move((r, c), (filaDestino, colDestino), self.board))
        return

    """
    Obtener todos los movimientos de alfil en la posicion (r, c)
    """
    def getBishopMoves(self, r, c, moves):
        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)] #Diagonales
        enemigoColor = "b" if self.whiteToMove else "w"
        for d in direcciones:
            for i in range(1,8):
                filaDestino = r + d[0]*i
                colDestino = c + d[1]*i
                if 0 <= filaDestino < 8 and 0 <= colDestino <8:
                    casillaDestino = self.board[filaDestino][colDestino]
                    if casillaDestino == "--":
                        moves.append(Move((r, c), (filaDestino, colDestino), self.board))
                    elif casillaDestino[0] == enemigoColor:
                        moves.append(Move((r, c), (filaDestino, colDestino), self.board))
                        break
                    else:
                        break
                else:
                    break
        return

    """
    Obtener todos los movimientos de reina en la posicion (r, c)
    """
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
    Obtener todos los movimientos de rey en la posicion (r, c)
    """
    def getKingMoves(self, r, c, moves):
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        enemigoColor = "b" if self.whiteToMove else "w"
        for d in direcciones:
            filaDestino = r + d[0]
            colDestino = c + d[1]
            if 0 <= filaDestino < 8 and 0 <= colDestino <8:
                casillaDestino = self.board[filaDestino][colDestino]
                if casillaDestino == "--" or casillaDestino[0] == enemigoColor:
                    moves.append(Move((r, c), (filaDestino, colDestino), self.board))
        return


class Move():
    #Traduccion de filas y columnas a notacion de ajedrez para logica de juego
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol *100 + self.endRow *10 + self.endCol

    """
    Comparar movimientos para saber si son iguales y asi validar movimientos
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    """
    String con la notacion de ajedrez del movimiento
    """
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
