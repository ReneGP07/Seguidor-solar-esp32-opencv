#include <Arduino.h>
#include <Servo.h>

#define PIN_DIR   26
#define PIN_STEP  27
#define PIN_EN    32    // A4988 Enable (LOW = habilitado)
#define SERVO_PIN 13

// Ajustes
const int STEPS_PER_TICK = 150;  // pasos por orden izquierda/derecha
const int STEP_DELAY_US  = 700;  // pulso (microsegundos) – ajusta según microstepping/velocidad
const int SERVO_DELTA    = 3;    // grados por orden arriba/abajo

Servo servoZ;
int servoPos = 90;               // posición inicial

void enableDriver(bool en) {
  digitalWrite(PIN_EN, en ? LOW : HIGH);
}

void stepperMove(int steps) {
  if (steps == 0) return;
  enableDriver(true);
  digitalWrite(PIN_DIR, (steps > 0) ? HIGH : LOW);
  int total = abs(steps);
  for (int i = 0; i < total; ++i) {
    digitalWrite(PIN_STEP, HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(PIN_STEP, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }
  enableDriver(false);
}

void servoUp() {
  servoPos = constrain(servoPos + SERVO_DELTA, 0, 180);
  servoZ.write(servoPos);
}

void servoDown() {
  servoPos = constrain(servoPos - SERVO_DELTA, 0, 180);
  servoZ.write(servoPos);
}

String readLine() {
  if (!Serial.available()) return "";
  String s = Serial.readStringUntil('\n');
  s.trim();
  return s;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_STEP, OUTPUT);
  pinMode(PIN_EN, OUTPUT);
  enableDriver(false);

  servoZ.attach(SERVO_PIN);
  servoZ.write(servoPos);

  Serial.println("ESP32 listo (A4988 + Servo).");
}

void loop() {
  String cmd = readLine();
  if (cmd.length() == 0) return;

  if (cmd == "MOTOR IZQUIERDA") {
    stepperMove(-STEPS_PER_TICK);
    Serial.println("OK IZQUIERDA");
  } else if (cmd == "MOTOR DERECHA") {
    stepperMove(STEPS_PER_TICK);
    Serial.println("OK DERECHA");
  } else if (cmd == "SERVO ARRIBA") {
    servoUp();  Serial.print("SERVO="); Serial.println(servoPos);
  } else if (cmd == "SERVO ABAJO") {
    servoDown(); Serial.print("SERVO="); Serial.println(servoPos);
  } else if (cmd == "SOL CENTRO") {
    // Sin acción: sistema estable
  } else {
    Serial.print("CMD desconocido: ");
    Serial.println(cmd);
  }
}
