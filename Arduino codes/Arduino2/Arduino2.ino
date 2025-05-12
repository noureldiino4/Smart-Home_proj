#include <Servo.h>




Servo myServo;

const int pirSensor = 3;
const int buzzer = 4;
const int rainSensorPin = A0;
const int gasSensorPin = A5;
const int flamePin = 5;

int umbrellasensorValue = 0;
int mask = 1;

const int gasThreshold = 350;

void setup() {

  
  pinMode(pirSensor, INPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(gasSensorPin, INPUT);
  pinMode(flamePin, INPUT);
  myServo.attach(6);
  myServo.write(7); // Initial servo position
}

void loop() {
  int motionDetected = digitalRead(pirSensor);
  int gasValue = analogRead(gasSensorPin);
  int flameState = digitalRead(flamePin);
  umbrellasensorValue = analogRead(rainSensorPin);

  bool dangerDetected = false;

  // 🔁 Motion detection
  if (motionDetected == HIGH) {
    if (mask == 1) {
      Serial.println("🚶 Motion Detected.");
      mask = 0;
    }
    dangerDetected = true;
  } else {
    mask = 1;
  }

  // 🔥 Gas detection
  if (gasValue > gasThreshold) {
    Serial.println("⚠️ Gas Detected!");
    dangerDetected = true;
  }

  // ☔ Rain detection
  if (umbrellasensorValue < 500) {
    myServo.write(110); // Open umbrella
  } else {
    myServo.write(7);   // Close umbrella
  }

  // Fire Detection
  if(flameState==LOW)
  {
    dangerDetected=true;
  }



  
 
  // 🔔 Buzzer control: turn on if either motion or gas detected
  digitalWrite(buzzer, dangerDetected ? HIGH : LOW);

  delay(500); // Stability
}
