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
  // Velocidade do ar é 343 metros/s | 0,0343 cm/microssegundo
  return (duration * 0.0343) / 2.0;
}

bool run_servo_cycle(int max_attempts) {
  for (int attempt = 1; attempt <= max_attempts; attempt++) {
    myServo.write(SERVO_OPEN_ANGLE);
    delay(600);
    myServo.write(SERVO_CLOSED_ANGLE);
    delay(400);
  }
  return true;
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
  bool water_detected = (water_digital == LOW || water_analog < WATER_ANALOG_THRESHOLD);

  if (distance > 0 && distance <= DISTANCE_LIMIT) {
    run_servo_cycle(MAX_SERVO_ATTEMPTS);
    distance = read_distance();
  } else {
    myServo.write(SERVO_CLOSED_ANGLE);
  }
  set_alert(water_detected);

  Serial.print("DIST:");
  Serial.print(distance, 2);
  Serial.print("|WATER:");
  Serial.println(water_detected ? 1 : 0);

  delay(200);
}
