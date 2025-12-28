#Main driver (Recibir inputs del usuario y dar el display de salida)

import pygame as p
import Engine

WIDTH = HEIGHT = 600 #Tamaño de la ventana, se hizo más grande para que entre título
DIMENSION = 8  #Dimension del tablero de ajedrez
SQ_SIZE = HEIGHT // DIMENSION
Imagenes = {}

#Constantes de la ventana de inicio

STATE_MENU = "Menu" #ventana de selección de modo
STATE_SETUP = "Setup" #para cargar archivo de tablero de inicio diferente
STATE_GAME = "Game" #ya dentro de modo de juego 

MODE_ASSISTED = "Asistido" #modo asistente de juego (dos jugadores)
MODE_AUTO = "Automático" #modo automático 


#Funcion para cargar las imagenes de las piezas
def cargarImagenes():
    piezas = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for pieza in piezas:
        Imagenes[pieza] = p.transform.scale(
            p.image.load("Imagenes/" + pieza + ".png"),
            (SQ_SIZE, SQ_SIZE)
        )
#Ahora se puede acceder a una imagen usando Imagenes['wP'] por ejemplo


'''
Dibuja texto de ventana de inicio
'''
def draw_text(screen, text, center_pos, font, color=p.Color("black")):
    label = font.render(text, True, color)
    rect = label.get_rect(center=center_pos)
    screen.blit(label, rect)


'''
Dibuja botones de ventana de inicio definido por un diccionario:
button = {"rect": Rectangulo del boton, "text": string con lo que dice el boton, "action": string con funcionalidad}
'''
def draw_button(screen, button, font, mouse_pos):
    rect = button["rect"]

    # si el mouse está encima, cambia un toque el color para que se vea
    if rect.collidepoint(mouse_pos):
        color = p.Color(170, 170, 170)  # con el mouse encima (un poco más oscuro)
    else:
        color = p.Color(200, 200, 200)  # normal

    p.draw.rect(screen, color, rect, border_radius=10)
    p.draw.rect(screen, p.Color("gray"), rect, 2, border_radius=10)

    draw_text(screen, button["text"], rect.center, font, p.Color("black"))


"""
Define los botones del menu (solo datos)

"""

def build_menu_buttons():

    btn_w = 280
    btn_h = 60
    x = (WIDTH - btn_w) // 2
    y0 = 260   
    gap = 80

    return [
        {"rect": p.Rect(x, y0, btn_w, btn_h), "text": "Modo Asistido", "action": MODE_ASSISTED},
        {"rect": p.Rect(x, y0 + gap, btn_w, btn_h), "text": "Modo Automático", "action": MODE_AUTO}
    ]



"""
 Define los botones de SETUP (Nuevo/Cargar/Volver).
"""
def build_setup_buttons():

    btn_w = 280
    btn_h = 60
    x = (WIDTH - btn_w) // 2
    y0 = 220
    gap = 80

    return [
        {"rect": p.Rect(x, y0, btn_w, btn_h), "text": "Nuevo juego", "action": "NEW_GAME"},
        {"rect": p.Rect(x, y0 + gap, btn_w, btn_h), "text": "Cargar posición", "action": "LOAD_POS"},
        {"rect": p.Rect(x, y0 + 2 * gap, btn_w, btn_h), "text": "Volver", "action": "BACK"},
    ]


'''
Dibuja la ventana del menu de inicio
'''
def draw_menu(screen, buttons, mouse_pos, font_title, font_btn):
    screen.fill(p.Color("white"))

    draw_text(screen, "Microprocesadores y Microcontroladores", (WIDTH // 2, 70), font_title)
    draw_text(screen, "Proyecto Ajedrez", (WIDTH // 2, 130), font_title)
    draw_text(screen, "Seleccione el modo de juego", (WIDTH // 2, 180), font_btn)


    for b in buttons:
        draw_button(screen, b, font_btn, mouse_pos)

    draw_text(screen, "ESC para salir", (WIDTH // 2, HEIGHT - 30), font_btn)


'''
Dibuja la ventana de SETUP (Nuevo juego / Cargar posición / Volver)
'''
def draw_setup(screen, buttons, mouse_pos, font_title, font_btn, modo_seleccionado):
    screen.fill(p.Color("white"))

    draw_text(screen, "Setup de partida", (WIDTH // 2, 90), font_title)
    draw_text(screen, "Seleccione una opción", (WIDTH // 2, 140), font_btn)

    # Mostrar el modo seleccionado (solo texto informativo)
    draw_text(screen, "Modo seleccionado: " + str(modo_seleccionado), (WIDTH // 2, 175), font_btn)

    for b in buttons:
        draw_button(screen, b, font_btn, mouse_pos)

    draw_text(screen, "ESC para salir", (WIDTH // 2, HEIGHT - 30), font_btn)




"""
El main se encargará de manejar los inputs del usuario y la salida grafica
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    #Variables para pantallas de inicio
  
    state = STATE_MENU   # dice en qué “pantalla” está: Menu / Setup / Game
    mode = None # para saber si está en modo asistido o automático
    font_title = p.font.SysFont(None, 40) # fuentes para titulos 
    font_btn = p.font.SysFont(None, 28) # fuentes para texto de botones
    menu_buttons = build_menu_buttons() #datos botones del menu
    setup_buttons = build_setup_buttons() #datos botones del setup


    # Variables para modo de juego 

    gs = Engine.GameState() #Crear el estado inicial del juego por medio de Engine.py
    validMoves = gs.getValidMoves() #Obtener los movimientos validos
    moveMade = False #Variable para saber si se hizo un movimiento para asi solo verificar movimientos posibles y validos una vez se haga un movimiento
    cargarImagenes() #Cargar las imagenes de las piezas
    correr = True
    sqSelected = () #Tupla (fila, columna) de la casilla seleccionada, inicialmente vacia
    playerClicks = [] #Lista de tuplas [(fila1, columna1), (fila2, columna2)] para registrar los clicks del jugador para movimiento


    while correr:

        mouse_pos = p.mouse.get_pos()  # Para dibujar botones 

        for evento in p.event.get():
            if evento.type == p.QUIT:
                correr = False


            elif evento.type == p.KEYDOWN: 
                if evento.key == p.K_ESCAPE: 
                    if state == STATE_GAME: # si uno da escape estando en el tablero lo devuelve al setup del modo escogido 
                        state = STATE_SETUP
                    else:
                        correr = False # si uno da escape estando en el menu o setup cierra el programa


            
            # En estado menu (seleccionar modo)
          
            if state == STATE_MENU:

                if evento.type == p.MOUSEBUTTONDOWN:
                    for b in menu_buttons:
                        if b["rect"].collidepoint(mouse_pos): #si el mouse hace click encima de un boton

                            if b["action"] == MODE_ASSISTED: #se estripa boton de modo asistido 
                                mode = MODE_ASSISTED
                                state = STATE_SETUP

                            elif b["action"] == MODE_AUTO: #no hace nada de momento
                                mode = MODE_AUTO
                                state = STATE_SETUP #lo manda al mismo state_setup que mode assisted entonces abren el mismo juego, luego hay que cambiar eso 



            # En estado setup (nuevo juego / cargar posición / volver)

            elif state == STATE_SETUP:

                if evento.type == p.MOUSEBUTTONDOWN:
                    for b in setup_buttons:
                        if b["rect"].collidepoint(mouse_pos):

                            if b["action"] == "BACK":
                                state = STATE_MENU #se devuelve a la pantalla anterior

                            elif b["action"] == "NEW_GAME": #empieza un juego de cero como con el main de antes
                                gs = Engine.GameState()
                                validMoves = gs.getValidMoves()
                                moveMade = False
                                sqSelected = ()
                                playerClicks = []
                                state = STATE_GAME

                            elif b["action"] == "LOAD_POS": #no hace nada pero eventualmente se le pone una lista con el tablero inicial o algo 
                                pass



            # En estado juego (aplica para modo asistido o automatico, pero creo que hay que cambiar algo de salto de turnos para el automatico, se ve despues)

            elif state == STATE_GAME:
                        
                # Manejar clicks del mouse
                if evento.type == p.MOUSEBUTTONDOWN:
                    ubicacion = p.mouse.get_pos() #Posicion del mouse en (x,y)
                    columna = ubicacion[0] // SQ_SIZE
                    fila = ubicacion[1] // SQ_SIZE

                    if sqSelected == (fila, columna): #El usuario hizo click en la misma casilla dos veces
                        sqSelected = () #Deseleccionar
                        playerClicks = [] #Borrar los clicks previos
                    else:
                        sqSelected = (fila, columna)
                        playerClicks.append(sqSelected) #Agregar la casilla a la lista de clicks

                    if len(playerClicks) == 2: #Luego de dos clicks
                        move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        if move in validMoves: #Si el movimiento es valido
                            gs.makeMove(move)
                            moveMade = True #Se hizo un movimiento
                            sqSelected = () #Resetear seleccion
                            playerClicks = [] #Resetear lista de clicks
                        else:
                            playerClicks = [sqSelected] #Mantener solo el ultimo click


        # Dibuja en el GUI dependiendo del estado en el que esté 


        if state == STATE_MENU:
            draw_menu(screen, menu_buttons, mouse_pos, font_title, font_btn)

        elif state == STATE_SETUP:
            draw_setup(screen, setup_buttons, mouse_pos, font_title, font_btn, mode)

        elif state == STATE_GAME:

            if moveMade:
                validMoves = gs.getValidMoves() #Actualizar los movimientos validos
                moveMade = False

            # === Movimientos posibles de la pieza seleccionada (luces guia) ===
            movesFromSelected = []
            if sqSelected != ():
                r, c = sqSelected
                if gs.board[r][c] != "--":
                    color = gs.board[r][c][0]
                    if (color == 'w' and gs.whiteToMove) or (color == 'b' and not gs.whiteToMove):
                        movesFromSelected = [m for m in validMoves if m.startRow == r and m.startCol == c]

            dibujarGameState(screen, gs, sqSelected, movesFromSelected)

        p.display.flip()  #Actualizar la pantalla
        clock.tick(15) #15 fps


"""
dibujarGameState: Encargada de dibujar el estado actual del juego
"""
def dibujarGameState(screen, gs, sqSelected, movesFromSelected):
    dibujarTablero(screen) #Dibujar las casillas del tablero
    dibujarPiezas(screen, gs.board) #Dibujar las piezas sobre las casillas
    dibujarMovimientosPosibles(screen, movesFromSelected) #Luces guia


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


"""
Dibuja puntos verdes en las casillas a las que la pieza seleccionada puede moverse
"""

def dibujarMovimientosPosibles(screen, moves):
    color = p.Color("green")
    radio = SQ_SIZE // 6
    for move in moves:
        centro_x = move.endCol * SQ_SIZE + SQ_SIZE // 2
        centro_y = move.endRow * SQ_SIZE + SQ_SIZE // 2
        p.draw.circle(screen, color, (centro_x, centro_y), radio)


#Por recomendacion de Python para poder importar el main sin ejecutar este .py si fuera necesario
if __name__ == "__main__":
    main()