#include <Arduino.h>
#include <BleMouse.h>

BleMouse bleMouse;

unsigned long previousMicros = 0;
const unsigned long interval = 1000000; // 1`,000,000 us = 1000 ms

void setup() {
  Serial.begin(115200);
  bleMouse.begin();
  delay(2000); 
  previousMicros = micros();
  Serial.println("Setup complete! Waiting for Bluetooth connection...");
}

void loop() {
  unsigned long currentMicros = micros();
  
  if (currentMicros - previousMicros >= interval) {
    previousMicros += interval; 
    
    // Only click if a device is connected via Bluetooth`
    if(bleMouse.isConnected()) {
      Serial.println("Connected - Sending Forward Click!");
      bleMouse.click(MOUSE_FORWARD);
    } else {
      Serial.println("Waiting for Bluetooth pairing...");
    }
  }
}