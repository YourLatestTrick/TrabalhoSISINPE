
#include <Servo.h>

const int ECHO_PIN   = 13;
const int TRIG_PIN   = 12;
const int BUZZER_PIN = 11;
const int SERVO_PIN  = 10;
const int LED_B_PIN  = 7;
const int LED_G_PIN  = 6;
const int LED_R_PIN  = 5;
const int WATER_ANALOG_PIN = A0;
const int WATER_DIGITAL_PIN = 9;

const float DISTANCE_LIMIT = 5.0;
const int WATER_ANALOG_THRESHOLD = 800;
const int MAX_SERVO_ATTEMPTS = 3;
const int SERVO_OPEN_ANGLE = 90;
const int SERVO_CLOSED_ANGLE = 0;

Servo myServo;

int rotation_attempts = 0;
bool rotation_success = false;
bool rotation_result_available = false;

void set_alert(bool water_detected) {
  if (water_detected) {
    digitalWrite(LED_R_PIN, HIGH);
    digitalWrite(LED_G_PIN, LOW);
    digitalWrite(LED_B_PIN, LOW);
    tone(BUZZER_PIN, 1000);
  } else {
    digitalWrite(LED_R_PIN, LOW);
    digitalWrite(LED_G_PIN, LOW);
    digitalWrite(LED_B_PIN, LOW);
    noTone(BUZZER_PIN);
  }
}

float read_distance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 25000);

  if (duration == 0) {
    return -1.0;
  }

  return (duration * 0.0343) / 2.0;
}

bool run_servo_cycle(int max_attempts) {
  rotation_attempts = 0;
  rotation_success = false;
  rotation_result_available = true;

  for (int attempt = 1; attempt <= max_attempts; attempt++) {
    rotation_attempts = attempt;

    myServo.write(SERVO_OPEN_ANGLE);
    delay(600);

    myServo.write(SERVO_CLOSED_ANGLE);
    delay(400);
  }

  // Nova leitura depois das tentativas.
  float distance_after_rotation = read_distance();

  rotation_success = (distance_after_rotation > DISTANCE_LIMIT);

  return rotation_success;
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

  myServo.attach(SERVO_PIN);
  myServo.write(SERVO_CLOSED_ANGLE);
}

void loop() {
  float distance = read_distance();

  int water_analog = analogRead(WATER_ANALOG_PIN);
  int water_digital = digitalRead(WATER_DIGITAL_PIN);

  bool water_detected = (
    water_digital == LOW ||
    water_analog < WATER_ANALOG_THRESHOLD
  );

  // Reinicia os resultados do ciclo anterior.
  rotation_attempts = 0;
  rotation_success = false;
  rotation_result_available = false;

  if (distance > 0 && distance <= DISTANCE_LIMIT) {
    run_servo_cycle(MAX_SERVO_ATTEMPTS);

    // Atualiza a distância após a movimentação.
    distance = read_distance();
  } else {
    myServo.write(SERVO_CLOSED_ANGLE);
  }

  set_alert(water_detected);

  // Envia a telemetria pela Serial.
  Serial.print("DIST:");
  Serial.print(distance, 2);

  Serial.print("|WATER:");
  Serial.print(water_detected ? 1 : 0);

  Serial.print("|ATTEMPTS:");
  Serial.print(rotation_attempts);

  Serial.print("|ROTATION:");

  if (!rotation_result_available) {
    Serial.println("NONE");
  } else if (rotation_success) {
    Serial.println("SUCCESS");
  } else {
    Serial.println("FAILED");
  }

  delay(200);
}
