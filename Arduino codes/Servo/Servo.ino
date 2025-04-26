#include <Servo.h>

Servo myServo;  // Create a servo object

void setup() {
  myServo.attach(9);  // Attach servo to digital pin 9
}

void loop() {
  myServo.write(10);   // Move to 0 degrees 85 eftah 180 e2fl
       

  
}
