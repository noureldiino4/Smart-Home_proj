#include <Servo.h>
Servo myServo;  // Create a servo object
bool doorOpened = false;  // State variable to track if the door is open

void setup() {
  Serial.begin(9600);  // Initialize serial communication at 9600 baud
  myServo.attach(9);   // Attach the servo to pin 9
  myServo.write(10);   // Ensure the door starts in the closed position
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');  // Read data sent from Python
    data.trim();  // Remove any extra whitespace or newline characters

    if (data == "MATCH" && !doorOpened) {
      Serial.println("MATCH received. Opening door...");
      myServo.write(110);  // Open the door
      delay(5000);         // Keep the door open for 5 seconds
      myServo.write(10);   // Close the door
      doorOpened = true;   // Set the state to indicate the door has been opened
    } else if (data == "NO_MATCH") {
      Serial.println("NO_MATCH received. Door remains closed.");
      myServo.write(10);   // Ensure the door remains closed
      doorOpened = false;  // Reset the state to allow future attempts
    }
  }
} 
