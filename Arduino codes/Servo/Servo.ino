#include <Servo.h>

Servo myServo;  // Create a servo object

void setup() {
  myServo.attach(9);  // Attach servo to digital pin 9
  myServo.write(10);  // Set initial position (closed)
  Serial.begin(9600); // Start serial communication
}

void loop() {
  if (Serial.available() > 0) {  // Check if data is available on the serial port
    String command = Serial.readStringUntil('\n');  // Read the incoming command

    if (command == "MATCH") {
      myServo.write(110);  // Open the servo
      delay(3000);        // Keep it open for 3 seconds
      myServo.write(10);  // Close the servo
    }
  }
}
