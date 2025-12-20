#Main driver (Recibir inputs del usuario y dar el display de salida)

import pygame as p
import Engine

WIDTH = HEIGHT = 512 #Tamaño de la ventana
DIMENSION = 8  #Dimension del tablero de ajedrez
SQ_SIZE = HEIGHT // DIMENSION
Imagenes = {}

#Funcion para cargar las imagenes de las piezas
def cargarImagenes():
    piezas = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for pieza in piezas:
        Imagenes[pieza] = p.transform.scale(p.image.load("Imagenes/" + pieza + ".png"), (SQ_SIZE, SQ_SIZE))
#Ahora se puede acceder a una imagen usando Imagenes['wP'] por ejemplo


"""
El main se encargará de manejar los inputs del usuario y la salida grafica
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState() #Crear el estado inicial del juego por medio de Engine.py
    validMoves = gs.getValidMoves() #Obtener los movimientos validos
    moveMade = False #Variable para saber si se hizo un movimiento para asi solo verificar movimientos posibles y validos una vez se haga un movimiento
    cargarImagenes() #Cargar las imagenes de las piezas
    correr = True
    sqSelected = () #Tupla (fila, columna) de la casilla seleccionada, inicialmente vacia
    playerClicks = [] #Lista de tuplas [(fila1, columna1), (fila2, columna2)] para registrar los clicks del jugador para movimiento
    while correr:
        for evento in p.event.get():
            if evento.type == p.QUIT:
                correr = False
            # Manejar clicks del mouse
            elif evento.type == p.MOUSEBUTTONDOWN:
                ubicacion = p.mouse.get_pos() #Posicion del mouse en (x,y)
                columna = ubicacion[0] // SQ_SIZE
                fila = ubicacion[1] // SQ_SIZE 
                if sqSelected == (fila, columna): #El usuario hizo click en la misma casilla dos veces
                    sqSelected = () #Deseleccionar
                    playerClicks = [] #Borrar los clicks previos
                else:
                    sqSelected = (fila, columna)
                    playerClicks.append(sqSelected) #Agregar la casilla a la lista de clicks
                print(fila, columna) #Para probar que se obtienen bien las coordenadas
                if len(playerClicks) == 2: #Luego de dos clicks
                    move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves: #Si el movimiento es valido
                        gs.makeMove(move)
                        moveMade = True #Se hizo un movimiento
                        sqSelected = () #Resetear seleccion
                        playerClicks = [] #Resetear lista de clicks
                    else:
                        playerClicks = [sqSelected] #Mantener solo el ultimo click (si el primer click fue invalido) 
        if moveMade:
            validMoves = gs.getValidMoves() #Actualizar los movimientos validos
            moveMade = False
        dibujarGameState(screen, gs)
        p.display.flip()  #Actualizar la pantalla
        clock.tick(15) #15 fps  

"""
dibujarGameState: Encargada de dibujar el estado actual del juego
"""
def dibujarGameState(screen, gs):
    dibujarTablero(screen) #Dibujar las casillas del tablero
    dibujarPiezas(screen, gs.board) #Dibujar las piezas sobre las casillas

"""
Dibuja las casillas del tablero
"""
def dibujarTablero(screen):
    colores = [p.Color("white"), p.Color("light blue")]
    for r in range(DIMENSION): #Filas
        for c in range(DIMENSION): #Columnas
            color = colores[((r + c) % 2)] #Si la suma de fila y columna es par, casilla blanca, si es impar, negra
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) #Dibuja un rectangulo en la posicion dada

"""
Dibuja las piezas en el tablero usando el estado del juego
"""
def dibujarPiezas(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            pieza = board[r][c]
            if pieza != "--": #Si no es una casilla vacia
                screen.blit(Imagenes[pieza], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Por recomendacion de Python para poder importar el main sin ejecutar este .py si fuera necesario
if __name__ == "__main__":
    main()