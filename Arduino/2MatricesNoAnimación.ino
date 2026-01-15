#include <SPI.h>
#include <Adafruit_NeoPixel.h>

// ===== Hardware =====
#define DATA_PIN 6

// 2 matrices 8x8 encadenadas => 128 LEDs
#define MATRIX_W 8
#define MATRIX_H 8
#define NUM_MATRICES 2
#define NUM_LEDS (MATRIX_W * MATRIX_H * NUM_MATRICES)

// Brillo muy bajo para evitar pasar 500mA con 128 LEDs
// 128 * 60mA = 7680mA worst-case white full
// Con BRIGHTNESS=8 => ~3.1% => ~240mA worst-case
#define BRIGHTNESS 8

Adafruit_NeoPixel strip(NUM_LEDS, DATA_PIN, NEO_GRB + NEO_KHZ800);

// ===== SPI buffer =====
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

// ===== Colores por pieza (como antes, pero puedes ajustar) =====
uint32_t pieceToColor(const char* tok) {
  if (tok[0] == '-' && tok[1] == '-') return strip.Color(0, 0, 0);

  char side = tok[0];
  char kind = tok[1];

  if (side == 'w') {
    switch (kind) {
      case 'P': return strip.Color(255, 120, 180);
      case 'R': return strip.Color( 80, 220, 255);
      case 'N': return strip.Color(120, 255,   0);
      case 'B': return strip.Color(200,  80, 255);
      case 'Q': return strip.Color(255, 170,   0);
      case 'K': return strip.Color(255, 255, 255);
      default:  return strip.Color(255, 255, 255);
    }
  } else {
    switch (kind) {
      case 'P': return strip.Color(140,   0,  30);
      case 'R': return strip.Color(  0,  40, 120);
      case 'N': return strip.Color(  0, 100,   0);
      case 'B': return strip.Color( 80,   0, 140);
      case 'Q': return strip.Color(160,  70,   0);
      case 'K': return strip.Color(180, 180, 180);
      default:  return strip.Color(180, 180, 180);
    }
  }
}

// ===== Mapeos =====
// Índice lineal dentro de una matriz 8x8 (asumiendo cableado lineal por filas)
// Si tu matriz es diferente (serpenteada), dímelo y lo ajustamos.
int idx8x8_xy(int x, int y) {            // normal
  return y * 8 + x;
}

int idx8x8_fx(int x, int y) {            // flip X
  return y * 8 + (7 - x);
}

int idx8x8_fy(int x, int y) {            // flip Y
  return (7 - y) * 8 + x;
}

int idx8x8_rot180(int x, int y) {        // flip X + flip Y
  return (7 - y) * 8 + (7 - x);
}


// Mapeo canvas 16x8 -> índice global 0..127 en el strip
// - Matriz derecha (la que recibe DIN): la ponemos como "matriz 0" (offset 0)
//   y ocupa canvas x=8..15 (lado derecho).
// - Matriz izquierda rotada 180°: "matriz 1" (offset 64)
//   y ocupa canvas x=0..7 (lado izquierdo).
int canvas16x8_to_ledIndex(int x, int y) {
  if (x < 0 || x >= 16 || y < 0 || y >= 8) return -1;

  if (x >= 8) {
    // Derecha: matriz 0, flip X
    int localX = x - 8;
    int localY = y;
    return 0 * 64 + idx8x8_fx(localX, localY);
  } else {
    // Izquierda: matriz 1, flip Y  (si aún se invierte en X, cámbialo a rot180)
    int localX = x;
    int localY = y;
    return 1 * 64 + idx8x8_fy(localX, localY);
  }
}


// Pinta un pixel del canvas 16x8
void setCanvasPixel(int x, int y, uint32_t color) {
  int led = canvas16x8_to_ledIndex(x, y);
  if (led >= 0) strip.setPixelColor(led, color);
}

// Pinta una casilla del tablero (r,c) solo si está en mitad baja r=4..7
// Cada casilla -> bloque 2x2 en canvas 16x8
void drawCell2x2(int r, int c, uint32_t color) {
  // Solo mitad baja:
  if (r < 4 || r > 7) return;

  // Convertir r=4..7 a fila local 0..3 dentro de la mitad baja
  int rLocal = r - 4; // 0..3

  // Posición en canvas (16x8)
  // Cada casilla es 2x2:
  int x0 = c * 2;        // 0..14
  int y0 = (3 - rLocal) * 2;   // invierte 0..3 -> 3..0


  setCanvasPixel(x0,     y0,     color);
  setCanvasPixel(x0 + 1, y0,     color);
  setCanvasPixel(x0,     y0 + 1, color);
  setCanvasPixel(x0 + 1, y0 + 1, color);
}

void setup() {
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.clear();
  strip.show();

  // SPI Slave (UNO)
  pinMode(MISO, OUTPUT);
  pinMode(SS, INPUT);
  SPCR |= _BV(SPE);
  SPCR |= _BV(SPIE);

  Serial.begin(115200);
  Serial.println("UNO listo: 2 matrices (16x8), mitad baja, 2x2 por casilla.");
}

void loop() {
  if (!lineReady) return;

  noInterrupts();
  char msg[256];
  strncpy(msg, (const char*)lineBuf, sizeof(msg));
  msg[sizeof(msg)-1] = '\0';
  lineReady = false;
  interrupts();

  // Espera: "B token,token,..."
  if (!(msg[0] == 'B' && msg[1] == ' ')) return;

  // Limpiar LEDs
  strip.clear();

  // Parse 64 tokens
  char* p = msg + 2;
  int count = 0;

  while (count < 64) {
    char* comma = strchr(p, ',');
    if (comma) *comma = '\0';

    int r = count / 8;
    int c = count % 8;

    uint32_t col = pieceToColor(p);
    drawCell2x2(r, c, col);

    count++;
    if (!comma) break;
    p = comma + 1;
  }

  if (count == 64) {
    strip.show();
  }
}
