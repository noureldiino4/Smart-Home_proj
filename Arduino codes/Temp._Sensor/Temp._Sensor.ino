#include "DHT.h"

DHT dht(2,DHT11);
float temp;
float humidity;

void setup() {
 dht.begin();
 Serial.begin(9600);
}

void loop() {

  delay(2000);
  temp=dht.readTemperature();
  humidity=dht.readHumidity();
  Serial.print("Temperature:");
  Serial.print(temp);
  Serial.print("C m");
  Serial.print("Humidity ");
  Serial.print(humidity);
  Serial.println("%");
  
  
  

}
