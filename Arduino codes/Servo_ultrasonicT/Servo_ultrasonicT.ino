#include <Servo.h>

const int trigPin = 9;
const int echoPin = 10;
const int servoPin= 11;

long duration;
float distanceCm;

Servo myServo;  // Create a servo object

void setup() {
  myServo.attach(11);  // Attach servo to digital pin 
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}
  


void loop() {
  

   // Clear the trigger
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Trigger the sensor by setting the trigPin HIGH for 10µs
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the echoPin
  duration = pulseIn(echoPin, HIGH);

  // Calculate distance (in cm)
  distanceCm = duration * 0.034 / 2;

  // Print the distance
  Serial.print("Distance: ");
  Serial.print(distanceCm);
  Serial.println(" cm");

  if(distanceCm < 15)
  {
    myServo.write(17);
    //delay(5000);
    //myServo.write(180);

  }
  delay(5000);
  myServo.write(180);

  delay(500);
       

  
}
