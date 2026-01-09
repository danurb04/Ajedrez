#Main driver (Recibir inputs del usuario y dar el display de salida)

import pygame as p
import Engine
import json
import os
import random

#abrir json en Windows
import tkinter as tk
from tkinter import filedialog

#abrir json en Rasp
#import subprocess 

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
Esta función abre el explorador de archivos y devuelve el path del .json seleccionado.
Importante: para windows y para linux se trabaja diferente lo del explorador de archivos, por lo que se ponen ambas versiones
Quitar de comentarios uno u otro dependiendo de si se corre el código en la raspberry o de forma local en computadora windows
Recordar también quitar o poner en comentarios los imports correspondientes
 """


def pick_json_file():
    
    #Quitar de comentarios esta sección si se va a usar código en rasp

    '''
    start_dir = os.path.join(os.getcwd(),"posiciones") #carpeta donde están los .json
    
    try:  #datos que salen en la ventana del explorador 
        result = subprocess.run(
        [
            "zenity",
            "--file-selection",
            "--title=Seleccionar tablero (.json)",
            f"--filename={start_dir}/",
            "--file-filter=JSON files | *.json",
            
        ],
        capture_output = True,
        text = True
        )
        
        if result.returncode != 0:
            return None # cancelado
            
        file_path = result.stdout.strip()
        return file_path if file_path else None #si encuentra un archivo para abrir lo abre y si no tira error
        
    finally:
        #reenfocar eventos (mouse y teclado) en pygame
        p.event.pump()
    
    '''

    root = tk.Tk()
    root.withdraw()  # oculta la ventana principal de tkinter
    root.attributes("-topmost", True)  # trae el dialog al frente

    file_path = filedialog.askopenfilename(
        title="Seleccionar tablero (.json)", #mensaje de arriba
        filetypes=[("JSON files", "*.json")], #tipo de archivos que muestra
        initialdir=os.path.join(os.getcwd(), "posiciones") #carpeta en la que busca (carpeta donde fen_to_json manda los archivos)
    )

    root.destroy()
    return file_path if file_path else None #si encuentra archivo disponible seleccionado lo abre, si no da error


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
    errorMessage = "" #mensaje para cuando hay movimiento inválido
    errorFrames = 0 #cantidad de frames que sale el mensaje


    while correr:

        mouse_pos = p.mouse.get_pos()  # Para dibujar botones 

        for evento in p.event.get():
            if evento.type == p.QUIT:
                correr = False


            elif evento.type == p.KEYDOWN: 
                if evento.key == p.K_ESCAPE: 
                    if state == STATE_GAME: # si uno da escape estando en el tablero lo devuelve al menu 
                        state = STATE_MENU
                    else:
                        correr = False # si uno da escape estando en el menu o setup cierra el programa
                
                elif evento.key == p.K_SPACE: #Estripar la tecla de espacio hace cambio de turno
                    if state == STATE_GAME:
                        if gs.checkMate or gs.staleMate: #si hay jaque mate o stale mate no se puede usar el cambio de turno
                            continue

                        elif gs.inCheck(): #si el rey está en jaque no permite cambio de turno y obliga al jugador a hacer jugada para salvar el rey
                            errorMessage = ("Rey en jaque", "Cambio de turno inválido")
                            errorFrames = 15                           
                    

                        else:
                            gs.whiteToMove = not gs.whiteToMove 
                            despues = "W" if gs.whiteToMove else "B" #guarda quien es el siguiente en tener turno para poner en el mensaje

                            # Limpiar clicks previos al cambio de turno
                            sqSelected = ()
                            playerClicks = []

                            #Recalcular cuuales son los movimientos validos del nuevo turno
                            validMoves = gs.getValidMoves()
                            moveMade = False   

                            # Mensaje que anuncia el cambio de turno
                            linea1 = "Cambio de turno"
                            linea2 = f"Juega: {despues}"

                            errorMessage = (linea1, linea2)
                            errorFrames = 15  # 1 segundo a 15 fps                    

            
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

                            elif b["action"] == "LOAD_POS": #permite abrir el explorador de archivos y cargar un .json que incluye las variables iniciales de un tablero preestablecido
                                    file_path = pick_json_file() #llama a la función que abre el explorador de archivos y permite escoger el .json

                                    if file_path is None:
                                        # usuario canceló y no seleccionó nada
                                        errorMessage = "No se seleccionó archivo"
                                        errorFrames = 30
                                    else:
                                        try:
                                            with open(file_path, "r", encoding="utf-8") as f: #abre archivo
                                                data = json.load(f) 

                                            board = data["board"] #dato de posiciones de las piezas (lista de listas al inicio del Engine)
                                            whiteToMove = data.get("whiteToMove", True) #dato de quien sigue moviendo (blanco o negro)

                                            gs.load_position(board, whiteToMove) #carga la posicion actual con esos datos

                                            validMoves = gs.getValidMoves() #empieza la partida a partir de este punto
                                            moveMade = False
                                            sqSelected = ()
                                            playerClicks = []

                                            state = STATE_GAME

                                        except Exception:
                                            errorMessage = "Error cargando archivo"
                                            errorFrames = 30



            # En estado juego (aplica para modo asistido o automatico, pero creo que hay que cambiar algo de salto de turnos para el automatico, se ve despues) 
            elif state == STATE_GAME:

                # Manejar clicks del mouse
                if evento.type == p.MOUSEBUTTONDOWN:
                    ubicacion = p.mouse.get_pos() #Posicion del mouse en (x,y)
                    columna = ubicacion[0] // SQ_SIZE
                    fila = ubicacion[1] // SQ_SIZE

                    if gs.checkMate or gs.staleMate: # si hay jaquemate o stalemate no permite hacer clicks 
                        continue

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
                            if move in movesInvalidFromSelected: #si hubo jugada inválida poner el texto y el tiempo que va a estar el mensaje de error.
                                errorMessage = "Jugada inválida"
                                errorFrames = 22.5 # 1.5 segundos, porque se definio que el programa corre a 15 fps

                            playerClicks = [sqSelected] #Mantener solo el ultimo click


                # Si es modo automático y es turno de negras, ignorar clicks del usuario, debe cambiarse después si agregamos la posibilidad de que modo automaticvo juegue con blancas
                if mode == MODE_AUTO and (not gs.whiteToMove):
                    continue




        # Dibuja en el GUI dependiendo del estado en el que esté 


        if state == STATE_MENU:
            draw_menu(screen, menu_buttons, mouse_pos, font_title, font_btn)

        elif state == STATE_SETUP:
            draw_setup(screen, setup_buttons, mouse_pos, font_title, font_btn, mode)
            if errorFrames > 0: #si hay error cargando el .json, muestra el mensaje de error respectivo (el usuario no seleccionó nada, error al cargar, o cualquier otro.)
                p.draw.rect(screen, p.Color("white"), p.Rect(WIDTH//2 - 120, HEIGHT//2 - 40, 240, 80))
                p.draw.rect(screen, p.Color("gray"),  p.Rect(WIDTH//2 - 120, HEIGHT//2 - 40, 240, 80), 2)
                draw_text(screen, errorMessage, (WIDTH // 2, HEIGHT // 2), font_btn, p.Color("red"))
                errorFrames -= 1

        elif state == STATE_GAME:

            gameOver = gs.checkMate or gs.staleMate

            if moveMade:
                validMoves = gs.getValidMoves() #Actualizar los movimientos validos
                moveMade = False
            
           

            # === Movimientos posibles de la pieza seleccionada (luces guia) ===
            movesValidFromSelected = [] #lista con movimientos posibles (verdes+amarillos)
            movesInvalidFromSelected = [] #lista con movimientos ilegales (rojos)
            
            if sqSelected != ():
                r, c = sqSelected
                if gs.board[r][c] != "--":
                    color = gs.board[r][c][0]
                    if (color == 'w' and gs.whiteToMove) or (color == 'b' and not gs.whiteToMove):

                        movesValidFromSelected = [m for m in validMoves if m.startRow == r and m.startCol == c] #Movimientos válidos (lo que ya estaba antes: verdes+amarillos)

                        allMoves = gs.getAllPossibleMoves()
                        movesAllFromSelected = [m for m in allMoves if m.startRow == r and m.startCol == c] #todos los movimientos posibles de la pieza sin considerar jaque (para poder definir rojos)

                        movesInvalidFromSelected = [m for m in movesAllFromSelected if m not in movesValidFromSelected] #movimientos inválidos de pieza: todos movimientos válidos - movimientos válidos (rojo)

            dibujarGameState(screen, gs, sqSelected, movesValidFromSelected, movesInvalidFromSelected)


            if mode == MODE_AUTO: #si está en modo Auto, verifica si es el turno de las negras y hacer un movimiento aletorio de los válidos

                if not gs.whiteToMove:
                    autoMoves = gs.getValidMoves()

                    if len(autoMoves) > 0:
                        autoMove = random.choice(autoMoves)
                        gs.makeMove(autoMove)
                        moveMade = True

                        # limpiar si alguien hacía clicks en turno de negras (no debería de poder mover nada en turno de negras)
                        sqSelected = ()
                        playerClicks = []



            if gameOver: #dibuja un cuadro más grande si se da la condición de jaque mate o empate
                
                box_w, box_h = 420, 220
                x = WIDTH//2 - box_w//2
                y = HEIGHT//2 - box_h//2

                p.draw.rect(screen, p.Color("white"), p.Rect(x, y, box_w, box_h))
                p.draw.rect(screen, p.Color("gray"),  p.Rect(x, y, box_w, box_h), 3)

                if gs.checkMate: #si hay jaquemate verifica quien gana y lo pone en el mensaje
                    winner = "B" if gs.whiteToMove else "W"
                    draw_text(screen, "JAQUE MATE", (WIDTH//2, y + 55), font_title, p.Color("red"))
                    draw_text(screen, f"Gana: {winner}", (WIDTH//2, y + 105), font_title, p.Color("black"))
                else:
                    draw_text(screen, "EMPATE", (WIDTH//2, y + 70), font_title, p.Color("black"))
                    draw_text(screen, "Sin movimientos legales", (WIDTH//2, y + 115), font_btn, p.Color("black"))

                draw_text(screen, "Presione ESC para volver", (WIDTH//2, y + 175), font_btn, p.Color("gray"))

                        

            if errorFrames > 0: #si se generó jugada inválida, o hubo cambio de turno mostrar el mensaje 
                p.draw.rect(screen, p.Color("white"), p.Rect(WIDTH//2 - 120, HEIGHT//2 - 40, 240, 80))
                p.draw.rect(screen, p.Color("gray"),  p.Rect(WIDTH//2 - 120, HEIGHT//2 - 40, 240, 80), 2)

                if isinstance(errorMessage, tuple): #si el mensaje trae más de un renglón (como el de cambio de turno) usa el errorMessage en versión tupla (mensaje de cada renglon), si no en versión simple
                    draw_text(screen, errorMessage[0], (WIDTH // 2, HEIGHT // 2 - 10), font_btn, p.Color("red"))
                    draw_text(screen, errorMessage[1], (WIDTH // 2, HEIGHT // 2 + 15), font_btn, p.Color("red"))
                else:
                    draw_text(screen, errorMessage, (WIDTH // 2, HEIGHT // 2), font_btn, p.Color("red"))
                errorFrames -= 1

        p.display.flip()  #Actualizar la pantalla
        clock.tick(15) #15 fps


"""
dibujarGameState: Encargada de dibujar el estado actual del juego
"""
def dibujarGameState(screen, gs, sqSelected, movesValidFromSelected, movesInvalidFromSelected):
    dibujarTablero(screen) #Dibujar las casillas del tablero
    dibujarPiezas(screen, gs.board) #Dibujar las piezas sobre las casillas
    dibujarMovimientosPosibles(screen, movesValidFromSelected, movesInvalidFromSelected) #Luces guia


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
Dibuja puntos verdes en las casillas a las que la pieza seleccionada puede moverse y puntos verdes si puede comer alguna pieza
"""

def dibujarMovimientosPosibles(screen, movesValid, movesInvalid): #se agregó movesValid y movesInvalid en vez de solo moves
    radio = SQ_SIZE // 6

    # para dibujar los movimientos inválidos de las piezas (rojo)
    for move in movesInvalid:
        centro_x = move.endCol * SQ_SIZE + SQ_SIZE // 2
        centro_y = move.endRow * SQ_SIZE + SQ_SIZE // 2
        p.draw.circle(screen, p.Color("red"), (centro_x, centro_y), radio)

    for move in movesValid:
        if move.pieceCaptured != "--": 
            color = p.Color("yellow") #si el movimiento genera captura de pieza, color amarillo
        else:
            color = p.Color("green") #si el movimiento es en "--" color verde (movimiento posible)

        centro_x = move.endCol * SQ_SIZE + SQ_SIZE // 2
        centro_y = move.endRow * SQ_SIZE + SQ_SIZE // 2
        p.draw.circle(screen, color, (centro_x, centro_y), radio)


#Por recomendacion de Python para poder importar el main sin ejecutar este .py si fuera necesario
if __name__ == "__main__":
    main()