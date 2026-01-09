#include <SPI.h>
const uint8_t LED_PIN = 7;

// Buffer para recibir la línea completa
volatile char lineBuf[256];
volatile uint16_t idx = 0;
volatile bool lineReady = false;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  pinMode(53, OUTPUT);   // SS como OUTPUT

  // SPI Slave + interrupción
  SPCR |= _BV(SPE);
  SPCR |= _BV(SPIE);

  Serial.begin(115200);
  Serial.println("SPI Slave listo (imprime mensaje recibido, espera 'B ...')");
}

// Interrupción SPI: llega 1 byte por MOSI
ISR(SPI_STC_vect) {
  char c = (char)SPDR;

  if (c == '\n') {
    if (idx < sizeof(lineBuf)) {
      lineBuf[idx] = '\0';   // termina string
    }
    lineReady = true;
    idx = 0;
  } else {
    if (idx < sizeof(lineBuf) - 1) {
      lineBuf[idx++] = c;
    } else {
      
      idx = 0;
    }
  }
}

void blinkLed(uint8_t times = 1) {
  for (uint8_t i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(120);
    digitalWrite(LED_PIN, LOW);
    delay(120);
  }
}

void loop() {
  if (!lineReady) return;

  // Copiar a un buffer local 
  noInterrupts();
  char msg[256];
  strncpy(msg, (const char*)lineBuf, sizeof(msg));
  msg[sizeof(msg) - 1] = '\0';
  lineReady = false;
  interrupts();

  // Imprimir lo que llegó
  Serial.print("[RX] ");
  Serial.println(msg);

  // Si es tablero, contar casillas
  if (msg[0] == 'B' && msg[1] == ' ') {

    int count = 0;
    bool hasAny = false;

    // Contar tokens separados por coma a partir del índice 2
    // (si hay contenido, tokens = comas + 1)
    for (uint16_t i = 2; msg[i] != '\0'; i++) {
      hasAny = true;
      if (msg[i] == ',') count++;
    }

    if (hasAny) count = count + 1;  // comas + 1

    if (count == 64) {
      Serial.println("[OK] Tablero recibido (64 casillas)");
      blinkLed(1);   // OK
    } else {
      Serial.print("[ERR] Tablero incompleto: ");
      Serial.print(count);
      Serial.println(" casillas");
      blinkLed(3);   // error
    }

  } else {
    // Otros mensajes
    Serial.println("[INFO] Mensaje no es tablero (no empieza con 'B ')");
  }
}
