#include <cooking-game_inferencing.h>
#include <Adafruit_BNO08x.h>
#include <Wire.h>

/* Constant defines */
#define BNO08X_RESET -1
#define I2C_SDA 5
#define I2C_SCL 6
#define MAX_ACCEPTED_RANGE 20.0f 

Adafruit_BNO08x bno08x(BNO08X_RESET);
sh2_SensorValue_t sensorValue;

// This is our "Moving Window" buffer
static float inference_buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];

// LPF Variables
float filteredX = 0.0, filteredY = 0.0, filteredZ = 0.0;
float alpha = 0.1; 

void setup() {
    Serial.begin(115200);
    while (!Serial); 

    Wire.begin(I2C_SDA, I2C_SCL);
    if (!bno08x.begin_I2C(0x4B, &Wire)) {
        Serial.println("Failed to find BNO08x chip");
        while (1) { delay(10); }
    }

    // Set BNO085 to 50Hz (20ms)
    if (!bno08x.enableReport(SH2_ACCELEROMETER, 20000)) {
        Serial.println("Could not enable accelerometer");
    }

    // Zero out the buffer
    memset(inference_buffer, 0, sizeof(inference_buffer));

    Serial.println("BNO085 Moving Window Inference Started...");
}

void loop() {
    // 1. Check for new sensor data
    if (bno08x.getSensorEvent(&sensorValue)) {
        if (sensorValue.sensorId == SH2_ACCELEROMETER) {
            
            // 2. Apply Low Pass Filter
            filteredX = (alpha * sensorValue.un.accelerometer.x) + ((1.0 - alpha) * filteredX);
            filteredY = (alpha * sensorValue.un.accelerometer.y) + ((1.0 - alpha) * filteredY);
            filteredZ = (alpha * sensorValue.un.accelerometer.z) + ((1.0 - alpha) * filteredZ);

            // 3. THE SLIDING WINDOW LOGIC
            // Shift all data in the buffer left by 3 (X, Y, Z)
            memmove(&inference_buffer[0], &inference_buffer[3], (EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE - 3) * sizeof(float));

            // Add the new filtered data at the very end of the buffer
            inference_buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE - 3] = filteredX;
            inference_buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE - 2] = filteredY;
            inference_buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE - 1] = filteredZ;

            // 4. Run Inference
            // Wrap the buffer in a signal_t object
            signal_t signal;
            int err = numpy::signal_from_buffer(inference_buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
            if (err != 0) {
                return;
            }

            ei_impulse_result_t result = { 0 };
            EI_IMPULSE_ERROR r = run_classifier(&signal, &result, false);

            if (r != EI_IMPULSE_OK) {
                return; 
            }

            // 5. Evaluate results with > 0.5 threshold
            int top_result_index = -1;
            float top_result_value = 0.0;

            for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
                if (result.classification[ix].value > top_result_value) {
                    top_result_value = result.classification[ix].value;
                    top_result_index = ix;
                }
            }

            // 6. Print to Serial if above threshold
            if (top_result_value > 0.5) {
                Serial.print("Gesture: ");
                Serial.print(result.classification[top_result_index].label);
                Serial.print(" (");
                Serial.print(top_result_value);
                Serial.println(")");
            }
        }
    }
}