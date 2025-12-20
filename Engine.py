#Estado e informacion del juego, asi como reglas y logica de movimiento, ademas de un historial
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
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" #Vaciar la casilla de inicio
        self.board[move.endRow][move.endCol] = move.pieceMoved #Colocar la pieza en la casilla destino
        self.moveLog.append(move) #Agregar el movimiento al historial
        self.whiteToMove = not self.whiteToMove #Cambiar el turno

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

    def getChessNotation(self):
        #Puede mejorarse para incluir capturas, jaques, etc.
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    