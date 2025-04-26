const int rainSensorPin = A0; // Analog pin connected to AO
int sensorValue = 0;

void setup() {
  Serial.begin(9600);
}

void loop() { 
  sensorValue = analogRead(rainSensorPin);

  Serial.print("Rain Sensor Value: ");
  Serial.println(sensorValue);

  if(sensorValue < 500) {
    Serial.println("It's Raining!");
  } else {
    Serial.println("No Rain.");
  }

  delay(1000); // Read every second
}
