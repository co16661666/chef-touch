// Adapted BNO08x Accelerometer script with Low Pass Filter
#include <Adafruit_BNO08x.h>
#include <Wire.h>

#define BNO08X_RESET 4
Adafruit_BNO08x bno08x(BNO08X_RESET);
sh2_SensorValue_t sensorValue;

#define I2C_SDA 5
#define I2C_SCL 6

#define FREQUENCY_HZ 50
#define INTERVAL_MS (1000 / FREQUENCY_HZ)

static unsigned long last_interval_ms = 0;

// Variables to hold the raw and filtered sensor readings
float accelX = 0.0, accelY = 0.0, accelZ = 0.0;
float filteredX = 0.0, filteredY = 0.0, filteredZ = 0.0;

// --- LPF TWEAKING PARAMETER ---
// 1.0 = No filtering | 0.01 = Maximum filtering (heavy lag)
float alpha = 0.1; 

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10); 

  // Initialize I2C with custom pins for ESP32-S3
  Wire.begin(I2C_SDA, I2C_SCL);

  Serial.println("Initializing BNO08x...");
  if (!bno08x.begin_I2C(0x4B, &Wire)) {
    Serial.println("Failed to find BNO08x chip");
    while (1) { delay(10); }
  }
  Serial.println("Device OK!");

  if (!bno08x.enableReport(SH2_ACCELEROMETER, 20000)) {
    Serial.println("Could not enable accelerometer");
  }
}

void loop() {
  // 1. Check for incoming sensor events
  if (bno08x.getSensorEvent(&sensorValue)) {
    if (sensorValue.sensorId == SH2_ACCELEROMETER) {
      
      // Get raw values
      accelX = sensorValue.un.accelerometer.x;
      accelY = sensorValue.un.accelerometer.y;
      accelZ = sensorValue.un.accelerometer.z;

      // 2. Apply Low Pass Filter (Exponential Moving Average)
      filteredX = (alpha * accelX) + ((1.0 - alpha) * filteredX);
      filteredY = (alpha * accelY) + ((1.0 - alpha) * filteredY);
      filteredZ = (alpha * accelZ) + ((1.0 - alpha) * filteredZ);
    }
  }

  // 3. Output the FILTERED values at the designated frequency
  if (millis() - last_interval_ms >= INTERVAL_MS) {
    last_interval_ms = millis();

    Serial.print(filteredX, 4);
    Serial.print('\t');
    Serial.print(filteredY, 4);
    Serial.print('\t');
    Serial.println(filteredZ, 4);
  }
}