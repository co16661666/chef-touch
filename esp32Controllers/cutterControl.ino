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

// REPLACE WITH THE RECEIVER'S MAC Address
uint8_t broadcastAddress[] = {0x58, 0x8c, 0x81, 0x3b, 0xcc, 0x78};

// Structure example to send data
// Must match the receiver structure
typedef struct struct_message {
    int id; // must be unique for each sender board
    int x;
} struct_message;

// Create a struct_message called numCutsMessage
struct_message numCutsMessage;

// Create peer interface
esp_now_peer_info_t peerInfo;

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

static unsigned long last_interval_ms = 0;
unsigned long lastTriggerTime = 0;
const int cooldownMs = 100;

// Send information
int numCuts = 0;
int id = 1

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

  // Init BNO08x
  Serial.println("Initializing BNO08x...");
  if (!bno08x.begin_I2C(0x4B, &Wire)) {
    Serial.println("Failed to find BNO08x chip");
    while (1) { delay(10); }
  }
  Serial.println("Device OK!");

  if (!bno08x.enableReport(SH2_ACCELEROMETER, 20000)) {
    Serial.println("Could not enable accelerometer");
  }

  // ESPNOW Init
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  esp_now_register_send_cb(esp_now_send_cb_t(OnDataSent));
  
  // Register peer
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Add peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
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

    // Calculate the magnitude (resultant vector)
    float magnitude = sqrt(filteredX * filteredX + filteredY * filteredY + filteredZ * filteredZ);

    if (magnitude <= 7.5) {
      if (millis() - lastTriggerTime >= cooldownMs) {
        Serial.println("cut");
        numCuts += 1;
        lastTriggerTime = millis(); // Reset the cooldown timer

        numCutsMessage.id = id;
        numCutsMessage.x = numCuts;

        esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &numCutsMessage, sizeof(numCutsMessage));
   
        if (result == ESP_OK) {
          Serial.println("Sent with success");
        }
        else
        {
          Serial.println("Error sending the data");
        }
      }
    }
  }
}