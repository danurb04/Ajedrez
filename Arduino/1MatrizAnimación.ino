#include <SPI.h>
#include <Adafruit_NeoPixel.h>

#define PIN 6
#define W 8
#define H 8
#define N 64

#define BRIGHTNESS 20   // mantener bajo para no acercarse a 500mA

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

// ===== Animación Game Over =====
bool gameOverAnim = false;
char gameOverTag[3] = {'J','M','\0'};  // "JM" o "SM"
unsigned long lastAnimMs = 0;
bool showLetters = false;
const unsigned long ANIM_PERIOD_MS = 600; // alterna cada 0.6s

// ===== ISR SPI =====
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

// ===== Paleta fuerte =====
uint32_t pieceToColor(const char* tok) {
  if (tok[0] == '-' && tok[1] == '-') return m.Color(0, 0, 0);

  char side = tok[0];
  char kind = tok[1];

  if (side == 'w') {
    switch (kind) {
      case 'P': return m.Color(255, 120, 180); // rosado
      case 'R': return m.Color( 80, 220, 255); // celeste
      case 'N': return m.Color(120, 255,   0); // lima
      case 'B': return m.Color(200,  80, 255); // lila
      case 'Q': return m.Color(255, 170,   0); // naranja
      case 'K': return m.Color(255, 255, 255); // blanco
      default:  return m.Color(255, 255, 255);
    }
  } else { // negras
    switch (kind) {
      case 'P': return m.Color(140,   0,  30); // vino
      case 'R': return m.Color(  0,  40, 120); // marino
      case 'N': return m.Color(  0, 100,   0); // verde oscuro
      case 'B': return m.Color( 80,   0, 140); // morado
      case 'Q': return m.Color(160,  70,   0); // ámbar oscuro
      case 'K': return m.Color(180, 180, 180); // gris
      default:  return m.Color(180, 180, 180);
    }
  }
}

// ===== Dibujar letras JM / SM en 8x8 =====
// Usa un solo color para letras
uint32_t lettersColor() {
  return m.Color(255, 0, 0); // rojo
}

void clearAll() {
  m.clear();
  m.show();
}

void drawLetters(const char* tag) {
  m.clear();
  uint32_t col = lettersColor();

  // Matriz (x=0..7, y=0..7) con y=0 arriba en tu lógica de juego.
  // Aquí dibujamos letras grandes simples en 8x8.
  // "JM" o "SM"
  if (tag[0] == 'J') {
    // J en la izquierda (aprox)
    for (int x=0; x<=2; x++) m.setPixelColor(xyToIndex(x+1, 1), col);
    for (int y=1; y<=5; y++) m.setPixelColor(xyToIndex(2, y), col);
    for (int x=0; x<=2; x++) m.setPixelColor(xyToIndex(x+1, 6), col);
    m.setPixelColor(xyToIndex(1,5), col);
  } else if (tag[0] == 'S') {
    // S en la izquierda
    for (int x=0; x<=2; x++) m.setPixelColor(xyToIndex(x+1, 2), col);
    m.setPixelColor(xyToIndex(1,3), col);
    for (int x=0; x<=2; x++) m.setPixelColor(xyToIndex(x+1, 4), col);
    m.setPixelColor(xyToIndex(3,5), col);
    for (int x=0; x<=2; x++) m.setPixelColor(xyToIndex(x+1, 6), col);
  }

  if (tag[1] == 'M') {
    // M a la derecha
    for (int y=2; y<=6; y++) m.setPixelColor(xyToIndex(5, y), col);
    for (int y=2; y<=6; y++) m.setPixelColor(xyToIndex(7, y), col);
    m.setPixelColor(xyToIndex(6,3), col);
    m.setPixelColor(xyToIndex(6,4), col);
  }

  m.show();
}

void startGameOverAnim(const char* tag) {
  gameOverAnim = true;
  gameOverTag[0] = tag[0];
  gameOverTag[1] = tag[1];
  gameOverTag[2] = '\0';
  showLetters = false;
  lastAnimMs = millis();
  // No tocamos el tablero: se queda como última imagen hasta el primer toggle
}

void stopGameOverAnim() {
  gameOverAnim = false;
}

// ===== Procesar mensaje B =====
void processBoardMessage(char* msg) {
  // msg viene con "B " al inicio
  char* p = msg + 2;
  int count = 0;

  m.clear();

  while (count < 64) {
    char* comma = strchr(p, ',');
    if (comma) *comma = '\0';

    int r = count / 8;
    int c = count % 8;

    int led = xyToIndex(c, r);
    m.setPixelColor(led, pieceToColor(p));

    count++;
    if (!comma) break;
    p = comma + 1;
  }

  if (count == 64) {
    m.setBrightness(BRIGHTNESS);
    m.show();
  }
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
  Serial.println("UNO listo: comandos 'B ...' y 'G JM/SM'");
}

void loop() {
  // 1) Animación (no bloquea recepción)
  if (gameOverAnim) {
    unsigned long now = millis();
    if (now - lastAnimMs >= ANIM_PERIOD_MS) {
      lastAnimMs = now;
      showLetters = !showLetters;
      if (showLetters) {
        drawLetters(gameOverTag);
      } else {
        // volver a mostrar el tablero actual (ya está en el buffer interno de NeoPixel)
        // Para garantizarlo, no hacemos clear; simplemente show con lo que ya esté seteado.
        m.show();
      }
    }
  }

  // 2) Procesar mensajes SPI cuando llegue una línea
  if (!lineReady) return;

  noInterrupts();
  char msg[256];
  strncpy(msg, (const char*)lineBuf, sizeof(msg));
  msg[sizeof(msg)-1] = '\0';
  lineReady = false;
  interrupts();

  // Comando tablero
  if (msg[0] == 'B' && msg[1] == ' ') {
    // Al recibir tablero nuevo, cancelar animación (si estaba)
    stopGameOverAnim();
    processBoardMessage(msg);
    return;
  }

  // Comando game over: "G JM" o "G SM"
  if (msg[0] == 'G' && msg[1] == ' ' && msg[2] && msg[3]) {
    char tag[3] = { msg[2], msg[3], '\0' };
    if ((tag[0]=='J' && tag[1]=='M') || (tag[0]=='S' && tag[1]=='M')) {
      startGameOverAnim(tag);
    }
    return;
  }

  // Comando clear opcional
  if (msg[0] == 'C') {
    stopGameOverAnim();
    clearAll();
    return;
  }
}
