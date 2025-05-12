#include <Servo.h>
#include "DHT.h"
#include <Wire.h>

DHT dht(12, DHT11);
float temp;
float humidity;
unsigned long lastTempUpdate = 0;
const unsigned long tempUpdateInterval = 10000; // 10 seconds

const int Pfan = 4;
const int Pkitchen = A0;
const int Pbroom = A1;
const int Pgym = 8;
const int Pgarage = A2;
const int Plroom = A3;

const int Pecho = 11;
const int Ptrig = 13;
long duration;
float distanceCm;

const int Pbackdoor = 3;
const int Pgaragedoor = 5;
  const int Pmaindoor = 6;
const int Prightdoor = 9;
const int Pleftdoor = 10;

Servo backdoor;
Servo garagedoor;
Servo maindoor;
Servo rightdoor;
Servo leftdoor;

// Use bit fields for more memory-efficient state tracking
uint16_t deviceStates = 0;

// Define bit positions
#define MAIN_DOOR_BIT      0
#define BACK_DOOR_BIT      1
#define GARAGE_DOOR_BIT    2
#define GATE_BIT           3
#define FAN_BIT            4
#define LIVING_ROOM_BIT    5
#define KITCHEN_BIT        6
#define BEDROOM_BIT        7
#define GARAGE_LIGHT_BIT   8
#define GYM_BIT            9

// Timing variables for non-blocking operations
uint8_t gateOpenFlags = 0;
#define GATE_OPEN_IN_PROGRESS_BIT 0
#define GARAGE_OPEN_IN_PROGRESS_BIT 1

boolean garageflag = false;
unsigned long gateOpenTime = 0;
unsigned long garageOpenTime = 0;
const unsigned long gateOpenDuration = 5000;
const unsigned long garageOpenDuration = 5000;

// Ultrasonic sensor filtering and debounce
#define NUM_READINGS 5
float distanceReadings[NUM_READINGS];  // Array to store readings
int readingIndex = 0;
bool readingsInitialized = false;
unsigned long lastUltrasonicTrigger = 0;
const unsigned long ultrasonicDebounceTime = 1000;
unsigned long postCloseTimer = 0;
const unsigned long postCloseCooldown = 3000; // 10 second cooldown after closing
bool inPostCloseCooldown = false;

volatile bool openGateFlag = false; // I2C command flag

// Functions to work with bits
bool getState(uint8_t bit) {
  return (deviceStates & (1 << bit)) != 0;
}

void setState(uint8_t bit, bool value) {
  if (value)
    deviceStates |= (1 << bit);  // Set bit
  else
    deviceStates &= ~(1 << bit); // Clear bit
}

void sendAllStates() {
  Serial.println(F("STATE_BEGIN"));
  
  Serial.print(F("STATE:MAIN_DOOR:"));
  Serial.println(getState(MAIN_DOOR_BIT) ? F("OPEN") : F("CLOSED"));
  
  Serial.print(F("STATE:BACK_DOOR:"));
  Serial.println(getState(BACK_DOOR_BIT) ? F("OPEN") : F("CLOSED"));
  
  Serial.print(F("STATE:GARAGE_DOOR:"));
  Serial.println(getState(GARAGE_DOOR_BIT) ? F("OPEN") : F("CLOSED"));
  
  Serial.print(F("STATE:GATE:"));
  Serial.println(getState(GATE_BIT) ? F("OPEN") : F("CLOSED"));
  
  Serial.print(F("STATE:FAN:"));
  Serial.println(getState(FAN_BIT) ? F("ON") : F("OFF"));
  
  Serial.print(F("STATE:LIVING_ROOM_LIGHT:"));
  Serial.println(getState(LIVING_ROOM_BIT) ? F("ON") : F("OFF"));
  
  Serial.print(F("STATE:KITCHEN_LIGHT:"));
  Serial.println(getState(KITCHEN_BIT) ? F("ON") : F("OFF"));
  
  Serial.print(F("STATE:BEDROOM_LIGHT:"));
  Serial.println(getState(BEDROOM_BIT) ? F("ON") : F("OFF"));
  
  Serial.print(F("STATE:GARAGE_LIGHT:"));
  Serial.println(getState(GARAGE_LIGHT_BIT) ? F("ON") : F("OFF"));
  
  Serial.print(F("STATE:GYM_LIGHT:"));
  Serial.println(getState(GYM_BIT) ? F("ON") : F("OFF"));
  
  Serial.println(F("STATE_END"));
}

void receiveEvent(int bytes) {
  while (Wire.available()) {
    char cmd = Wire.read();
    if (cmd == 'O') {
      Serial.println(F("Received I2C Command: O"));
      openGateFlag = true;
    }
  }
}

void setup() {
  Serial.begin(9600);
  dht.begin();
  Wire.begin(8);
  Wire.onReceive(receiveEvent);

  pinMode(Pfan, OUTPUT);
  pinMode(Pecho, INPUT);
  pinMode(Ptrig, OUTPUT);
  
  // Optional bypass switch
  // pinMode(autoBypassPin, INPUT_PULLUP);

  backdoor.attach(Pbackdoor);
  backdoor.write(110);

  garagedoor.attach(Pgaragedoor);
  garagedoor.write(180);

  maindoor.attach(Pmaindoor);
  maindoor.write(0);

  rightdoor.attach(Prightdoor);
  rightdoor.write(10);

  leftdoor.attach(Pleftdoor);
  leftdoor.write(120);
  
  // Initialize distance readings
  for (int i = 0; i < NUM_READINGS; i++) {
    distanceReadings[i] = 400;  // Initialize with an "out of range" value
  }
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Handle I2C gate open request with non-blocking timing
  if (openGateFlag && !(gateOpenFlags & (1 << GATE_OPEN_IN_PROGRESS_BIT))) {
    // Start opening the gate
    Serial.println(F("Opening Gate via I2C..."));
    rightdoor.write(100);
    leftdoor.write(40);
    gateOpenTime = currentMillis;
    gateOpenFlags |= (1 << GATE_OPEN_IN_PROGRESS_BIT);
    setState(GATE_BIT, true);
    Serial.println(F("STATE:GATE:OPEN"));
  }
  
  // Check if it's time to close the gate
  if ((gateOpenFlags & (1 << GATE_OPEN_IN_PROGRESS_BIT)) && (currentMillis - gateOpenTime >= gateOpenDuration)) {
    // Time to close the gate
    rightdoor.write(10);
    leftdoor.write(120);
    gateOpenFlags &= ~(1 << GATE_OPEN_IN_PROGRESS_BIT);
    openGateFlag = false;
    setState(GATE_BIT, false);
    Serial.println(F("Gate closed after delay."));
    Serial.println(F("STATE:GATE:CLOSED"));
  }

  // Check for serial commands
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    handleSerialCommand(data);
  }

  updateTemperatureAndHumidity();
  handleUltrasonicSensor();
}

void handleSerialCommand(String data) {
  if (data == "MATCH_FOUND") {
    Serial.println(F("Match found. Opening Main Door..."));
    maindoor.write(110);
    setState(MAIN_DOOR_BIT, true);
    Serial.println(F("STATE:MAIN_DOOR:OPEN"));
  } 
  else if (data == "CLOSE_MAIN_DOOR") {
    Serial.println(F("Closing Main Door..."));
    maindoor.write(0);
    setState(MAIN_DOOR_BIT, false);
    Serial.println(F("STATE:MAIN_DOOR:CLOSED"));
  } 
  else if (data == "OPENGARAGEDOOR") {
    Serial.println(F("Opening Garage Door..."));
    garagedoor.write(12);
    setState(GARAGE_DOOR_BIT, true);
    Serial.println(F("STATE:GARAGE_DOOR:OPEN"));
    garageflag = true;
  } 
  else if (data == "CLOSEGARAGEDOOR") {
    Serial.println(F("Closing Garage Door..."));
    garagedoor.write(170);
    setState(GARAGE_DOOR_BIT, false);
    Serial.println(F("STATE:GARAGE_DOOR:CLOSED"));
    garageflag = false;
    
    // Set post-close cooldown
    inPostCloseCooldown = true;
    postCloseTimer = millis();
  } 
  else if (data == "OPEN_MAIN_GATE") {
    Serial.println(F("Opening Gate..."));
    leftdoor.write(40);
    rightdoor.write(100);
    setState(GATE_BIT, true);
    Serial.println(F("STATE:GATE:OPEN"));
  } 
  else if (data == "CLOSE_MAIN_GATE") {
    Serial.println(F("Closing Gate..."));
    leftdoor.write(125);
    rightdoor.write(10);
    setState(GATE_BIT, false);
    Serial.println(F("STATE:GATE:CLOSED"));
  } 
  else if (data == "OPEN_BACK_DOOR") {
    Serial.println(F("Opening Back Door..."));
    backdoor.write(0);
    setState(BACK_DOOR_BIT, true);
    Serial.println(F("STATE:BACK_DOOR:OPEN"));
  } 
  else if (data == "CLOSE_BACK_DOOR") {
    Serial.println(F("Closing Back Door..."));
    backdoor.write(110);
    setState(BACK_DOOR_BIT, false);
    Serial.println(F("STATE:BACK_DOOR:CLOSED"));
  } 
  else if (data == "AIRCON_ON") {
    Serial.println(F("AC is ON"));
    digitalWrite(Pfan, HIGH);
    setState(FAN_BIT, true);
    Serial.println(F("STATE:FAN:ON"));
  } 
  else if (data == "AIRCON_OFF") {
    Serial.println(F("AC is Off"));
    digitalWrite(Pfan, LOW);
    setState(FAN_BIT, false);
    Serial.println(F("STATE:FAN:OFF"));
  } 
  else if (data == "LIVING_ROOM_BULB_ON") {
    Serial.println(F("Living room Lights Are On."));
    digitalWrite(Plroom, HIGH);
    setState(LIVING_ROOM_BIT, true);
    Serial.println(F("STATE:LIVING_ROOM_LIGHT:ON"));
  } 
  else if (data == "LIVING_ROOM_BULB_OFF") {
    Serial.println(F("Living room Lights Are Off."));
    digitalWrite(Plroom, LOW);
    setState(LIVING_ROOM_BIT, false);
    Serial.println(F("STATE:LIVING_ROOM_LIGHT:OFF"));
  } 
  else if (data == "GYM_BULB_ON") {
    Serial.println(F("Gym room Lights Are On."));
    digitalWrite(Pgym, HIGH);
    setState(GYM_BIT, true);
    Serial.println(F("STATE:GYM_LIGHT:ON"));
  } 
  else if (data == "GYM_BULB_OFF") {
    Serial.println(F("Gym room Lights Are Off."));
    digitalWrite(Pgym, LOW);
    setState(GYM_BIT, false);
    Serial.println(F("STATE:GYM_LIGHT:OFF"));
  } 
  else if (data == "KITCHEN_BULB_ON") {
    Serial.println(F("Kitchen Lights Are On."));
    digitalWrite(Pkitchen, HIGH);
    setState(KITCHEN_BIT, true);
    Serial.println(F("STATE:KITCHEN_LIGHT:ON"));
  } 
  else if (data == "KITCHEN_BULB_OFF") {
    Serial.println(F("Kitchen Lights Are Off."));
    digitalWrite(Pkitchen, LOW);
    setState(KITCHEN_BIT, false);
    Serial.println(F("STATE:KITCHEN_LIGHT:OFF"));
  } 
  else if (data == "BEDROOM_BULB_ON") {
    Serial.println(F("Bedroom Lights Are On."));
    digitalWrite(Pbroom, HIGH);
    setState(BEDROOM_BIT, true);
    Serial.println(F("STATE:BEDROOM_LIGHT:ON"));
  } 
  else if (data == "BEDROOM_BULB_OFF") {
    Serial.println(F("Bedroom Lights Are Off."));
    digitalWrite(Pbroom, LOW);
    setState(BEDROOM_BIT, false);
    Serial.println(F("STATE:BEDROOM_LIGHT:OFF"));
  } 
  else if (data == "GARAGE_LIGHT_ON") {
    Serial.println(F("Garage Lights Are On."));
    digitalWrite(Pgarage, HIGH);
    setState(GARAGE_LIGHT_BIT, true);
    Serial.println(F("STATE:GARAGE_LIGHT:ON"));
  } 
  else if (data == "GARAGE_LIGHT_OFF") {
    Serial.println(F("Garage Lights Are Off."));
    digitalWrite(Pgarage, LOW);
    setState(GARAGE_LIGHT_BIT, false);
    Serial.println(F("STATE:GARAGE_LIGHT:OFF"));
  } 
  else if (data == "ALL_LIGHTS_ON") {
    digitalWrite(Pgarage, HIGH);
    digitalWrite(Pkitchen, HIGH);
    digitalWrite(Pbroom, HIGH);
    digitalWrite(Pgym, HIGH);
    digitalWrite(Plroom, HIGH);
    setState(GARAGE_LIGHT_BIT, true);
    setState(KITCHEN_BIT, true);
    setState(BEDROOM_BIT, true);
    setState(GYM_BIT, true);
    setState(LIVING_ROOM_BIT, true);
    Serial.println(F("STATE:GARAGE_LIGHT:ON"));
    Serial.println(F("STATE:KITCHEN_LIGHT:ON"));
    Serial.println(F("STATE:BEDROOM_LIGHT:ON"));
    Serial.println(F("STATE:GYM_LIGHT:ON"));
    Serial.println(F("STATE:LIVING_ROOM_LIGHT:ON"));
  } 
  else if (data == "ALL_LIGHTS_OFF") {
    digitalWrite(Pgarage, LOW);
    digitalWrite(Pkitchen, LOW);
    digitalWrite(Pbroom, LOW);
    digitalWrite(Pgym, LOW);
    digitalWrite(Plroom, LOW);
    setState(GARAGE_LIGHT_BIT, false);
    setState(KITCHEN_BIT, false);
    setState(BEDROOM_BIT, false);
    setState(GYM_BIT, false);
    setState(LIVING_ROOM_BIT, false);
    Serial.println(F("STATE:GARAGE_LIGHT:OFF"));
    Serial.println(F("STATE:KITCHEN_LIGHT:OFF"));
    Serial.println(F("STATE:BEDROOM_LIGHT:OFF"));
    Serial.println(F("STATE:GYM_LIGHT:OFF"));
    Serial.println(F("STATE:LIVING_ROOM_LIGHT:OFF"));
  }
  else if (data == "GET_ALL_STATES") {
    sendAllStates();
  } 
  else {
    Serial.println(F("Unknown command received."));
  }
}

void updateTemperatureAndHumidity() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastTempUpdate >= tempUpdateInterval) {
    lastTempUpdate = currentMillis;
    humidity = dht.readHumidity();
    temp = dht.readTemperature();
    if (!isnan(humidity) && !isnan(temp)) {
      Serial.print(F("Temperature:"));
      Serial.print(temp);
      Serial.print(F("C Humidity:"));
      Serial.print(humidity);
      Serial.println(F("%"));
    }
  }
}

void handleUltrasonicSensor() {
  // Check cooldown first
  unsigned long currentMillis = millis();
  
  if (inPostCloseCooldown) {
    if (currentMillis - postCloseTimer >= postCloseCooldown) {
      inPostCloseCooldown = false;
    }
    return; // Skip detection during cooldown
  }
  
  digitalWrite(Ptrig, LOW);
  delayMicroseconds(2);
  digitalWrite(Ptrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(Ptrig, LOW);
  
  // Get raw duration
  long rawDuration = pulseIn(Pecho, HIGH, 23200); // Timeout after ~4m distance
  
  // Handle sensor timeout or invalid reading
  if (rawDuration == 0) {
    return; // Skip this reading entirely
  }
  
  // Calculate the new distance
  float newDistance = rawDuration * 0.034 / 2;
  
  // Ignore clearly invalid readings
  if (newDistance > 400 || newDistance < 2) {
    return;
  }
  
  // Store this reading
  distanceReadings[readingIndex] = newDistance;
  readingIndex = (readingIndex + 1) % NUM_READINGS;
  
  // Wait until we have enough readings
  if (!readingsInitialized) {
    if (readingIndex == 0) {
      readingsInitialized = true;
    } else {
      return;
    }
  }
  
  // Calculate average distance
  float sum = 0;
  for (int i = 0; i < NUM_READINGS; i++) {
    sum += distanceReadings[i];
  }
  distanceCm = sum / NUM_READINGS;
 //Serial.print("outside");
 //Serial.println(distanceCm);
 //delay(1000);
  
  // Check if object is close enough and we haven't triggered recently
  if (distanceCm < 10 && !garageflag && !(gateOpenFlags & (1 << GARAGE_OPEN_IN_PROGRESS_BIT)) &&
      (currentMillis - lastUltrasonicTrigger > ultrasonicDebounceTime)) {
    
    // Start opening the garage door
    Serial.println(distanceCm);
    garagedoor.write(12);
    garageflag = true;
    gateOpenFlags |= (1 << GARAGE_OPEN_IN_PROGRESS_BIT);
    garageOpenTime = currentMillis;
    lastUltrasonicTrigger = currentMillis;
    setState(GARAGE_DOOR_BIT, true);
    
    Serial.println(F("Auto: Garage Door Opening"));
    Serial.println(F("STATE:GARAGE_DOOR:OPEN"));
  }
  
  // Check if it's time to close the garage door
  if ((gateOpenFlags & (1 << GARAGE_OPEN_IN_PROGRESS_BIT)) && (currentMillis - garageOpenTime >= garageOpenDuration)) {
    Serial.println(F("Auto: Garage Door Closing"));
    garagedoor.write(180);
    garageflag = false;
    gateOpenFlags &= ~(1 << GARAGE_OPEN_IN_PROGRESS_BIT);
    setState(GARAGE_DOOR_BIT, false);
    Serial.println(F("STATE:GARAGE_DOOR:CLOSED"));
    
    // Set post-close cooldown
    inPostCloseCooldown = true;
    postCloseTimer = currentMillis;
  }
}