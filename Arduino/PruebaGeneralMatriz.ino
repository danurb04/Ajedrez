#include <SPI.h>
#include <Adafruit_NeoPixel.h>

#define PIN 6
#define W 8
#define H 8
#define N 64

#define BRIGHTNESS 20

Adafruit_NeoPixel m(N, PIN, NEO_GRB + NEO_KHZ800);

// ===== Mapeo: flip vertical + flip horizontal =====
int xyToIndex(int x, int y) {
  int yy = (H - 1) - y;
  int xx = (W - 1) - x;
  return yy * W + xx;
}

// ===== Buffer SPI =====
volatile char lineBuf[256];
volatile uint16_t idx = 0;
volatile bool lineReady = false;

ISR(SPI_STC_vect) {
  char c = (char)SPDR;
  if (c == '\n') {
    if (idx < sizeof(lineBuf)) lineBuf[idx] = '\0';
    lineReady = true;
    idx = 0;
  } else {
    if (idx < sizeof(lineBuf) - 1) lineBuf[idx++] = c;
    else idx = 0;
  }
}

// ===== Game Over latch + anim =====
bool gameOverLatched = false;
char gameOverTag[3] = {'J','M','\0'};

bool showLetters = false;
unsigned long nextSwitchMs = 0;

// Duraciones (ms)
const unsigned long START_BOARD_MS = 1000;  // al entrar: tablero 1s
const unsigned long LETTERS_MS     = 1000;  // letras 1s
const unsigned long BOARD_MS       = 2000;  // tablero 2s (repetición)


// Guardar último tablero (colores)
uint32_t boardColors[N];
bool boardValid = false;

// ===== Paleta fuerte =====
uint32_t pieceToColor(const char* tok) {
  if (tok[0] == '-' && tok[1] == '-') return m.Color(0, 0, 0);

  char side = tok[0];
  char kind = tok[1];

  if (side == 'w') {
    switch (kind) {
      case 'P': return m.Color(255, 120, 180);
      case 'R': return m.Color( 80, 220, 255);
      case 'N': return m.Color(120, 255,   0);
      case 'B': return m.Color(200,  80, 255);
      case 'Q': return m.Color(255, 170,   0);
      case 'K': return m.Color(255, 255, 255);
      default:  return m.Color(255, 255, 255);
    }
  } else {
    switch (kind) {
      case 'P': return m.Color(140,   0,  30);
      case 'R': return m.Color(  0,  40, 120);
      case 'N': return m.Color(  0, 100,   0);
      case 'B': return m.Color( 80,   0, 140);
      case 'Q': return m.Color(160,  70,   0);
      case 'K': return m.Color(180, 180, 180);
      default:  return m.Color(180, 180, 180);
    }
  }
}

void restoreBoard() {
  if (!boardValid) return;
  for (int i = 0; i < N; i++) m.setPixelColor(i, boardColors[i]);
  m.show();
}

void clearAll() {
  m.clear();
  m.show();
}

// ===== Letras =====
uint32_t lettersColor() {
  return m.Color(0, 90, 255); // rojo
}

void drawLetters(const char* tag) {
  m.clear();
  uint32_t col = lettersColor();

  // ---------- Letra izquierda: J o S ----------
  if (tag[0] == 'J') {
    // J (corrida 1 a la izquierda)
    // columna derecha en x=2, y=1..5
    for (int y = 1; y <= 5; y++) m.setPixelColor(xyToIndex(2, y), col);
    // base en y=6, x=0..2
    for (int x = 0; x <= 2; x++) m.setPixelColor(xyToIndex(x, 6), col);
    // gancho: (0,5)
    m.setPixelColor(xyToIndex(0, 5), col);

  } else if (tag[0] == 'S') {
    // S (corrida 1 a la izquierda)
    for (int x = 0; x <= 2; x++) m.setPixelColor(xyToIndex(x, 2), col);
    m.setPixelColor(xyToIndex(0, 3), col);
    for (int x = 0; x <= 2; x++) m.setPixelColor(xyToIndex(x, 4), col);
    m.setPixelColor(xyToIndex(2, 5), col);
    for (int x = 0; x <= 2; x++) m.setPixelColor(xyToIndex(x, 6), col);
  }

  // ---------- Letra derecha: M (4 de ancho) ----------
  if (tag[1] == 'M') {
    // M en columnas x=4..7
    // vertical izquierda x=4, y=2..6
    for (int y = 2; y <= 6; y++) m.setPixelColor(xyToIndex(4, y), col);
    // vertical derecha x=7, y=2..6
    for (int y = 2; y <= 6; y++) m.setPixelColor(xyToIndex(7, y), col);

    // dos leds una fila abajo del top (top=2 -> y=3): en x=5 y x=6
    m.setPixelColor(xyToIndex(5, 3), col);
    m.setPixelColor(xyToIndex(6, 3), col);
  }

  m.show();
}


void startGameOverLatch(const char* tag) {
  gameOverLatched = true;
  gameOverTag[0] = tag[0];
  gameOverTag[1] = tag[1];
  gameOverTag[2] = '\0';

  // Arranca mostrando TABLERO (ya está en LEDs)
  showLetters = false;

  // Primer cambio: después de 1s pasar a letras
  nextSwitchMs = millis() + START_BOARD_MS;
}


void stopGameOverLatch() {
  gameOverLatched = false;
  showLetters = false;
}

// ===== Procesar B (tablero) =====
bool processBoardMessage(char* msg) {
  // msg: "B token,token,..."
  char* p = msg + 2;
  int count = 0;
  bool allEmpty = true;

  // No hacemos clear hasta saber si viene vacío o no
  while (count < 64) {
    char* comma = strchr(p, ',');
    if (comma) *comma = '\0';

    int r = count / 8;
    int c = count % 8;
    int led = xyToIndex(c, r);

    bool isEmpty = (p[0] == '-' && p[1] == '-');
    if (!isEmpty) allEmpty = false;

    uint32_t col = pieceToColor(p);
    boardColors[led] = col;

    count++;
    if (!comma) break;
    p = comma + 1;
  }

  if (count != 64) return false;

  boardValid = true;
  m.setBrightness(BRIGHTNESS);

  // Render del tablero en LEDs
  restoreBoard();

  // Retornamos si es tablero vacío (para usarlo como “reset”)
  return allEmpty;
}

void setup() {
  m.begin();
  m.setBrightness(BRIGHTNESS);
  clearAll();

  pinMode(MISO, OUTPUT);
  pinMode(SS, INPUT);

  SPCR |= _BV(SPE);
  SPCR |= _BV(SPIE);

  Serial.begin(115200);
  Serial.println("UNO listo: B... y G JM/SM (latch hasta tablero vacío)");
}

void loop() {
  // Animación si estamos latched
if (gameOverLatched) {
  unsigned long now = millis();
  if ((long)(now - nextSwitchMs) >= 0) {

    if (!showLetters) {
      // Estábamos mostrando TABLERO -> ahora mostrar LETRAS por 1s
      showLetters = true;
      drawLetters(gameOverTag);
      nextSwitchMs = now + LETTERS_MS;

    } else {
      // Estábamos mostrando LETRAS -> ahora mostrar TABLERO por 2s
      showLetters = false;
      restoreBoard();
      nextSwitchMs = now + BOARD_MS;
    }
  }
}


  if (!lineReady) return;

  noInterrupts();
  char msg[256];
  strncpy(msg, (const char*)lineBuf, sizeof(msg));
  msg[sizeof(msg)-1] = '\0';
  lineReady = false;
  interrupts();

  // ---- B (tablero) ----
  if (msg[0] == 'B' && msg[1] == ' ') {
    bool isEmpty = processBoardMessage(msg);

    // Si llega tablero vacío, lo usamos como "reset" (salí al menú / nueva partida)
    if (isEmpty) {
      stopGameOverLatch();
      // ya está vacío en LEDs por restoreBoard()
    } else {
      // Si estamos en gameOverLatched, ignoramos el hecho de que llegó un tablero no-vacío:
      // dejamos que se guarde en boardColors (para futuro), pero seguimos animando letras/tablero.
      // (o si quieres, podrías ignorar por completo, pero esto te permite actualizar “final” si llega)
    }
    return;
  }

  // ---- G (game over) ----
  if (msg[0] == 'G' && msg[1] == ' ' && msg[2] && msg[3]) {
    char tag[3] = { msg[2], msg[3], '\0' };
    if ((tag[0]=='J' && tag[1]=='M') || (tag[0]=='S' && tag[1]=='M')) {
      startGameOverLatch(tag);
    }
    return;
  }

  // ---- C (clear opcional) ----
  if (msg[0] == 'C') {
    stopGameOverLatch();
    clearAll();
    return;
  }
}
