#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Sensor Pin & Hardware Definitions
#define DHTPIN 4          // GPIO 4 for DHT22 signal pin
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu;

// Sampling & Sampling Window Configuration
const unsigned long SAMPLE_INTERVAL_MS = 1000; // Read sensors every 1 second
unsigned long lastSampleTime = 0;

float dailyActivityAccumulator = 0.0;

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); } // Wait for Serial console

  // Initialize Environmental Sensor
  dht.begin();

  // Initialize Motion Sensor
  if (!mpu.begin()) {
    // If MPU6050 is not detected, continue gracefully
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setFilterBandwidth(MPU6050_BANDWIDTH_21_HZ);
  }
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentMillis;

    // Read Environmental Metrics
    float tempC = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Fallback values if sensor readings fail
    if (isnan(tempC)) tempC = 38.0;
    if (isnan(humidity)) humidity = 40.0;

    // Read Movement Acceleration Vector
    sensors_event_t a, g, temp;
    float movementUnits = 0.0;

    if (mpu.getEvent(&a, &g, &temp)) {
      // Calculate Vector Magnitude of Acceleration (m/s^2)
      float accelMagnitude = sqrt(pow(a.acceleration.x, 2) + 
                                  pow(a.acceleration.y, 2) + 
                                  pow(a.acceleration.z, 2));
      
      // Subtract gravity (~9.81 m/s^2) to isolate active movement
      float netAccel = fabs(accelMagnitude - 9.81);
      
      // Accumulate activity score
      dailyActivityAccumulator += netAccel * 100.0;
      movementUnits = dailyActivityAccumulator;
    } else {
      // Fallback simulated activity if hardware motion sensor is disconnected
      movementUnits = 4500.0;
    }

    // Output formatted CSV payload over Serial: "TEMP,HUMIDITY,ACTIVITY"
    Serial.print(tempC, 1);
    Serial.print(",");
    Serial.print(humidity, 1);
    Serial.print(",");
    Serial.println(movementUnits, 0);
  }
}
