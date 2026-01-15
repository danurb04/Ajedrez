#include <SPI.h>
#include <Adafruit_NeoPixel.h>

// =====================================================
// 4 matrices 8x8 encadenadas (DIN->DOUT), total 256 LEDs
// Panel lógico: 16x16
// Tablero 8x8 -> cada casilla es un bloque 2x2 en el panel 16x16
// DATA PIN: 6
// Protocolo SPI: "B token,token,...(64)\n"
// =====================================================

// ---------- Hardware ----------
#define DATA_PIN 6
#define MATRIX_W 8
#define MATRIX_H 8
#define NUM_MATRICES 4
#define NUM_LEDS (MATRIX_W * MATRIX_H * NUM_MATRICES)

// Brillo bajo para pruebas (256 LEDs consumen mucho)
#define BRIGHTNESS 8

Adafruit_NeoPixel strip(NUM_LEDS, DATA_PIN, NEO_GRB + NEO_KHZ800);

// ---------- SPI buffer ----------
volatile char lineBuf[512];
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
    else idx = 0; // overflow reset
  }
}

// =====================================================
// CONFIGURACIÓN FÁCIL (AQUÍ CAMBIAS TODO)
// =====================================================

// --- 1) Flip global del tablero ---
// Si el tablero te queda espejado izquierda/derecha, pon FLIP_X = true.
// Si te queda arriba/abajo invertido, pon FLIP_Y = true.
const bool FLIP_X = false;
const bool FLIP_Y = true;

// --- 2) Orden de matrices en la cadena ---
// La cadena de LEDs es:
//   matriz física 0 = LED 0..63
//   matriz física 1 = LED 64..127
//   matriz física 2 = LED 128..191
//   matriz física 3 = LED 192..255
//
// Aquí defines cuál matriz física corresponde a cada cuadrante del panel 16x16:
//
//   TL = Top-Left (arriba-izquierda)
//   TR = Top-Right (arriba-derecha)
//   BL = Bottom-Left (abajo-izquierda)
//   BR = Bottom-Right (abajo-derecha)
//
// Cambia estos números (0..3) según cómo conectaste físicamente las matrices.
#define Q_TL 0
#define Q_TR 1
#define Q_BL 2
#define Q_BR 3

int MATRIX_AT[4] = {
  0, // TL usa matriz física 0
  1, // TR usa matriz física 1
  2, // BL usa matriz física 2
  3  // BR usa matriz física 3
};

// --- 3) Orientación por cuadrante ---
// 0 = NORMAL
// 1 = FLIP_X
// 2 = FLIP_Y
// 3 = ROT180 (flip X + flip Y)
//
// Ajusta estos 4 valores según cómo esté girada/espejada cada matriz físicamente.
#define ORI_NORMAL 0
#define ORI_FX     1
#define ORI_FY     2
#define ORI_ROT180 3

uint8_t ORI_AT[4] = {
  ORI_NORMAL, // TL
  ORI_NORMAL, // TR
  ORI_NORMAL, // BL
  ORI_NORMAL  // BR
};

// --- 4) Paleta de colores por pieza ---
// Aquí puedes cambiar colores sin tocar el resto del código.
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

// =====================================================
// MAPEO (no tocar salvo que tu matriz sea serpenteada)
// =====================================================

// Índices dentro de una matriz 8x8 (lineal por filas)
int idx8x8_xy(int x, int y) { return y * 8 + x; }
int idx8x8_fx(int x, int y) { return y * 8 + (7 - x); }
int idx8x8_fy(int x, int y) { return (7 - y) * 8 + x; }
int idx8x8_rot180(int x, int y) { return (7 - y) * 8 + (7 - x); }

// OJO: aquí usamos uint8_t para evitar el bug de prototipos del Arduino IDE
int orientIndex(uint8_t ori, int x, int y) {
  switch (ori) {
    case ORI_NORMAL: return idx8x8_xy(x, y);
    case ORI_FX:     return idx8x8_fx(x, y);
    case ORI_FY:     return idx8x8_fy(x, y);
    case ORI_ROT180: return idx8x8_rot180(x, y);
    default:         return idx8x8_xy(x, y);
  }
}

// Panel 16x16 -> índice global 0..255
int panel16x16_to_ledIndex(int x, int y) {
  if (x < 0 || x >= 16 || y < 0 || y >= 16) return -1;

  bool right = (x >= 8);
  bool bottom = (y >= 8);

  int q;
  if (!right && !bottom) q = Q_TL;
  else if (right && !bottom) q = Q_TR;
  else if (!right && bottom) q = Q_BL;
  else q = Q_BR;

  int localX = x % 8;
  int localY = y % 8;

  int matIndex = MATRIX_AT[q];        // 0..3
  int localIdx = orientIndex(ORI_AT[q], localX, localY);

  return matIndex * 64 + localIdx;
}

void setPanelPixel(int x, int y, uint32_t color) {
  int led = panel16x16_to_ledIndex(x, y);
  if (led >= 0) strip.setPixelColor(led, color);
}

// Casilla (r,c) -> bloque 2x2 en panel 16x16
void drawCell2x2(int r, int c, uint32_t color) {
  // Flip global (si activaste)
  int rr = FLIP_Y ? (7 - r) : r;
  int cc = FLIP_X ? (7 - c) : c;

  int x0 = cc * 2; // 0..14
  int y0 = rr * 2; // 0..14

  setPanelPixel(x0,     y0,     color);
  setPanelPixel(x0 + 1, y0,     color);
  setPanelPixel(x0,     y0 + 1, color);
  setPanelPixel(x0 + 1, y0 + 1, color);
}

// =====================================================
// SETUP / LOOP
// =====================================================

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
  Serial.println("UNO listo: 4 matrices (16x16), 2x2 por casilla, SPI 'B ...'");
}

void loop() {
  if (!lineReady) return;

  noInterrupts();
  char msg[512];
  strncpy(msg, (const char*)lineBuf, sizeof(msg));
  msg[sizeof(msg) - 1] = '\0';
  lineReady = false;
  interrupts();

  // Mensaje esperado: "B token,token,..."
  if (!(msg[0] == 'B' && msg[1] == ' ')) return;

  strip.clear();

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

  if (count == 64) strip.show();
}
