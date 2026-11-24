#include <Servo.h>

// Arduino Uno/Nano: sensores e atuadores
const int ECHO_PIN = 13;
const int TRIG_PIN = 12;
const int BUZZER_PIN = 11;
const int SERVO_PIN = 10;
const int LED_B_PIN = 7;
const int LED_G_PIN = 6;
const int LED_R_PIN = 5;
const int WATER_ANALOG_PIN = A0;
const int WATER_DIGITAL_PIN = 9;

const float DISTANCE_DETECTION_CM = 20.0;
const float PERCEPTION_RANGE_CM = 30.0;
const int WATER_ANALOG_THRESHOLD = 800; // ajustar após teste do sensor real
const int MAX_SERVO_ATTEMPTS = 3;
const int SERVO_OPEN_ANGLE = 90;
const int SERVO_CLOSED_ANGLE = 0;

Servo mechanism;

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 25000UL);
  if (duration == 0) return -1.0;
  return (duration * 0.0343f) / 2.0f;
}

int readMoisturePercent() {
  int analogValue = analogRead(WATER_ANALOG_PIN);
  // Estimativa inicial; calibrar com leituras seco/molhado do sensor real.
  return constrain(map(analogValue, 1023, 0, 0, 100), 0, 100);
}

bool readWater() {
  int analogValue = analogRead(WATER_ANALOG_PIN);
  int digitalValue = digitalRead(WATER_DIGITAL_PIN);
  return digitalValue == LOW || analogValue < WATER_ANALOG_THRESHOLD;
}

void setIndicators(bool water, bool trash, bool failed) {
  digitalWrite(LED_R_PIN, water || failed ? HIGH : LOW);
  digitalWrite(LED_G_PIN, !water && !trash && !failed ? HIGH : LOW);
  digitalWrite(LED_B_PIN, trash && !failed ? HIGH : LOW);
  if (water || failed) tone(BUZZER_PIN, 1000, 400);
  else noTone(BUZZER_PIN);
}

bool rotateOnce() {
  mechanism.write(SERVO_OPEN_ANGLE);
  delay(600);
  mechanism.write(SERVO_CLOSED_ANGLE);
  delay(500);
  return true; // não há sensor de posição; sucesso é inferido pela leitura ultrassônica
}

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R_PIN, OUTPUT);
  pinMode(LED_G_PIN, OUTPUT);
  pinMode(LED_B_PIN, OUTPUT);
  pinMode(WATER_DIGITAL_PIN, INPUT_PULLUP);
  mechanism.attach(SERVO_PIN);
  mechanism.write(SERVO_CLOSED_ANGLE);
  delay(500);
}

void loop() {
  float distance = readDistanceCm();
  bool water = readWater();
  int humidityPercent = readMoisturePercent();
  int attempts = 0;
  bool rotationSuccess = false;
  const char* eventCode = "NONE";

  bool trash = distance >= 0 && distance <= DISTANCE_DETECTION_CM;
  if (trash) {
    for (int i = 0; i < MAX_SERVO_ATTEMPTS; i++) {
      attempts++;
      rotateOnce();
      distance = readDistanceCm();
      if (distance < 0 || distance > DISTANCE_DETECTION_CM) {
        rotationSuccess = true;
        break;
      }
    }
    if (!rotationSuccess) eventCode = "TRASH_REMOVAL_REQUIRED";
  }

  bool failure = trash && !rotationSuccess;
  setIndicators(water, trash, failure);

  // Linha JSON: uma medição por ciclo. Distância inválida = null.
  Serial.print("{\"distance_cm\":");
  if (distance < 0) Serial.print("null"); else Serial.print(distance, 2);
  Serial.print(",\"water_detected\":");
  Serial.print(water ? "true" : "false");
  Serial.print(",\"humidity_percent\":");
  Serial.print(humidityPercent);
  Serial.print(",\"rotation_attempts\":");
  Serial.print(attempts);
  Serial.print(",\"rotation_success\":");
  if (trash) Serial.print(rotationSuccess ? "true" : "false"); else Serial.print("null");
  Serial.print(",\"event_code\":\"");
  Serial.print(eventCode);
  Serial.println("\"}");
  delay(1500);
}
