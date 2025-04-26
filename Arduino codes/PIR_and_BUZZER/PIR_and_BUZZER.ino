#define PIR_PIN 7
#define BUZZER_PIN 8

void setup() {
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int pirState = digitalRead(PIR_PIN);

  if (pirState == HIGH) {
    Serial.println("Motion detected!");
    //digitalWrite(BUZZER_PIN, HIGH);
    //delay(1000); // Beep for 1 second
    //digitalWrite(BUZZER_PIN, LOW);
  } else {
    //digitalWrite(BUZZER_PIN, LOW);
  }

  delay(100); // Optional: small delay to debounce sensor
}
