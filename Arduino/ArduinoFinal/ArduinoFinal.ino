#include <SPI.h>
#include <Adafruit_NeoPixel.h>

// =====================================================
// 4 matrices 8x8 encadenadas (DIN->DOUT), total 256 LEDs
// Panel lógico: 16x16
// Tablero 8x8 -> cada casilla es un bloque 2x2 en el panel 16x16
// DATA PIN MATRICES: 6
// Protocolo SPI: "B token,token,...(64)\n"
//
// + EXTRA: 12 LEDs fijos en OTRO PIN (otra tira)
// =====================================================

// ---------- Hardware (MATRICES) ----------
#define DATA_PIN 7
#define MATRIX_W 8
#define MATRIX_H 8
#define NUM_MATRICES 4
#define NUM_LEDS (MATRIX_W * MATRIX_H * NUM_MATRICES)

// Brillo bajo para pruebas (256 LEDs consumen mucho)
#define BRIGHTNESS 50

Adafruit_NeoPixel strip(NUM_LEDS, DATA_PIN, NEO_GRB + NEO_KHZ800);

// ---------- Hardware (LEDS FIJOS) ----------
#define FIXED_PIN   6
#define FIXED_COUNT 12
#define FIXED_BRIGHTNESS 125

Adafruit_NeoPixel fixedStrip(FIXED_COUNT, FIXED_PIN, NEO_GRB + NEO_KHZ800);

// === COLORES ===
// Formato original: (R, G, B) -> Formato corregido para tu tira: (G, R, B)

#define W_P fixedStrip.Color(120, 255, 180) // Era (255, 120, 180)
#define W_R fixedStrip.Color(220,  80, 255) // Era (80, 220, 255)
#define W_N fixedStrip.Color(255, 120,   0) // Era (120, 255, 0)
#define W_B fixedStrip.Color( 62, 255,  33) // Era (255, 62, 33)
#define W_Q fixedStrip.Color(255, 255,   0) // Era (255, 255, 0) - (R=G)
#define W_K fixedStrip.Color(217, 113,  65) // Era (113, 217, 65)

// Formato original: (R, G, B) -> Formato corregido para tu tira: (G, R, B)

#define B_P fixedStrip.Color(  0, 140,  30) // Era (140, 0, 30)
#define B_R fixedStrip.Color( 40,   0, 120) // Era (0, 40, 120)
#define B_N fixedStrip.Color(100,   0,   0) // Era (0, 100, 0)
#define B_B fixedStrip.Color(  0,  80, 140) // Era (80, 0, 140)
#define B_Q fixedStrip.Color( 70, 160,   0) // Era (160, 70, 0)
#define B_K fixedStrip.Color(180, 180, 180) // Se mantiene igual (R=G)
// ================================

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
const bool FLIP_X = true;
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
  1, // TL usa matriz física 0
  0, // TR usa matriz física 1
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
  ORI_ROT180, // TL
  ORI_ROT180, // TR
  ORI_ROT180, // BL
  ORI_ROT180  // BR
};

// --- 4) Paleta de colores por pieza (TABLERO) ---
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
      case 'B': return strip.Color(255,  62, 33);
      case 'Q': return strip.Color(255, 255,   0);
      case 'K': return strip.Color(113, 217, 65);
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
// LEDS FIJOS (NO SE TOCAN EN EL LOOP)
// =====================================================
void setupFixedLEDs() {
  fixedStrip.begin();
  fixedStrip.setBrightness(FIXED_BRIGHTNESS);

  fixedStrip.setPixelColor(0,  W_P);
  fixedStrip.setPixelColor(1,  W_R);
  fixedStrip.setPixelColor(2,  W_N);
  fixedStrip.setPixelColor(3,  W_B);
  fixedStrip.setPixelColor(4,  W_Q);
  fixedStrip.setPixelColor(5,  W_K);

  fixedStrip.setPixelColor(6,  B_P);
  fixedStrip.setPixelColor(7,  B_R);
  fixedStrip.setPixelColor(8,  B_N);
  fixedStrip.setPixelColor(9,  B_B);
  fixedStrip.setPixelColor(10, B_Q);
  fixedStrip.setPixelColor(11, B_K);

  fixedStrip.show(); // quedan fijos
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
  // --- MATRICES ---
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.clear();
  strip.show();

  // --- LEDS FIJOS (otra tira, otro pin) ---
  setupFixedLEDs();

  // --- SPI Slave (UNO) ---
  pinMode(MISO, OUTPUT);
  pinMode(SS, INPUT);
  SPCR |= _BV(SPE);
  SPCR |= _BV(SPIE);

  Serial.begin(115200);
  Serial.println("UNO listo: 4 matrices (16x16) + 12 LEDs fijos (otro pin), SPI 'B ...'");
}

void loop() {
  if (!lineReady) return;

  noInterrupts();
  char msg[512];
  strncpy(msg, (const char*)lineBuf, sizeof(msg));
  msg[sizeof(msg) - 1] = '\0';
  lineReady = false;
  interrupts();

  // Esperado: "B token,token,...(64)\n"
  if (!(msg[0] == 'B' && msg[1] == ' ')) return;

  // Actualiza SOLO el tablero
  strip.clear();

  char* p = msg + 2;
  int count = 0;

  while (count < 64 && p && *p) {
    // token = 2 chars tipo "wP" o "--"
    // se separa por comas
    char* comma = strchr(p, ',');
    if (comma) *comma = '\0';

    uint32_t col = pieceToColor(p);
    int r = count / 8;
    int c = count % 8;
    drawCell2x2(r, c, col);

    count++;
    if (!comma) break;
    p = comma + 1;
  }

  if (count == 64) strip.show();

  // Nota: NO tocamos fixedStrip aquí, quedan fijos siempre
}
