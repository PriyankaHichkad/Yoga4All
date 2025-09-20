
#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>
#include <Wire.h>

#define G_TO_MPS2 9.80665

// Accelerometer Service and Characteristic UUIDs
BLEService accelService("A000");
BLECharacteristic accelChar("A001", BLERead | BLENotify, 32); // String format for accel data

// Gyroscope Service and Characteristic UUIDs
BLEService gyroService("B000");
BLECharacteristic gyroChar("B001", BLERead | BLENotify, 32); // String format for gyro data

// Magnetometer Service and Characteristic UUIDs
BLEService magService("C000");
BLECharacteristic magChar("C001", BLERead | BLENotify, 32); // String format for mag data

// Heart Rate Service and Characteristic UUIDs
BLEService heartService("D000");
BLECharacteristic heartChar("D001", BLERead | BLENotify, 8); // String format for BPM

// Battery monitoring pin (adjust for your board)
#define VBAT_PIN A0 // Analog pin for battery voltage (e.g., A0 on Nano 33 BLE)

// Heart rate sensor I2C address (adjust if different)
#define HEART_SENSOR_ADDR 0x50

void setup() {
  // Initialize Serial (comment out for battery-powered operation)
  Serial.begin(9600);
  // while (!Serial); // Uncomment for debugging, remove for standalone

  // Initialize I2C
  Wire.begin();

  // Initialize IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }

  // Set BLE name and advertise service
  BLE.setLocalName("nRF_IMU");
  BLE.setAdvertisedService(accelService);

  // Add characteristics to services
  accelService.addCharacteristic(accelChar);
  gyroService.addCharacteristic(gyroChar);
  magService.addCharacteristic(magChar);
  heartService.addCharacteristic(heartChar);

  // Add services
  BLE.addService(accelService);
  BLE.addService(gyroService);
  BLE.addService(magService);
  BLE.addService(heartService);

  // Set initial values
  accelChar.writeValue("0.00,0.00,0.00");
  gyroChar.writeValue("0.00,0.00,0.00");
  magChar.writeValue("0.00,0.00,0.00");
  heartChar.writeValue("0");

  // Start advertising
  BLE.advertise();
  Serial.println("BLE Peripheral Advertising...");

  // Configure battery monitoring
  setupBatteryMonitor();
}

void setupBatteryMonitor() {
  analogReadResolution(10); // 10-bit ADC for Nano 33 BLE
  // Fixed 3.3V reference; no analogReference() needed
}

float readBatteryVoltage() {
  float measuredvbat = analogRead(VBAT_PIN);
  measuredvbat *= 2.0; // Adjust for voltage divider (e.g., 1:1, check schematic)
  measuredvbat *= 3.3; // Reference voltage for Nano 33 BLE
  measuredvbat /= 1024.0; // Convert to voltage (10-bit ADC)
  return measuredvbat;
}

int readHeartRateBPM() {
  // Request heart rate data from sensor (adjust I2C protocol as needed)
  Wire.beginTransmission(HEART_SENSOR_ADDR);
  Wire.write(0x00); // Register address (modify based on sensor datasheet)
  int error = Wire.endTransmission(false); // Keep connection open
  if (error != 0) {
    return -1; // I2C error
  }

  Wire.requestFrom(HEART_SENSOR_ADDR, 1); // Request 1 byte
  if (Wire.available()) {
    int bpm = Wire.read();
    if (bpm > 30 && bpm < 200) { // Basic range check for valid BPM
      return bpm;
    }
  }
  return -1; // No data or invalid
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      float ax, ay, az, gx, gy, gz, mx, my, mz;
      bool dataAvailable = IMU.accelerationAvailable() && 
                          IMU.gyroscopeAvailable() && 
                          IMU.magneticFieldAvailable();

      if (dataAvailable) {
        IMU.readAcceleration(ax, ay, az);
        IMU.readGyroscope(gx, gy, gz);
        IMU.readMagneticField(mx, my, mz);

        // Convert accel to m/s^2
        ax *= G_TO_MPS2;
        ay *= G_TO_MPS2;
        az *= G_TO_MPS2;

        // Format strings
        char accelBuf[32];
        snprintf(accelBuf, sizeof(accelBuf),"A " "%.2f,%.2f,%.2f", ax, ay, az);
        char gyroBuf[32];
        snprintf(gyroBuf, sizeof(gyroBuf),"G " "%.2f,%.2f,%.2f", gx, gy, gz);
        char magBuf[32];
        snprintf(magBuf, sizeof(magBuf),"M " "%.2f,%.2f,%.2f", mx, my, mz);

        // Write to BLE
        accelChar.writeValue(accelBuf);
        gyroChar.writeValue(gyroBuf);
        magChar.writeValue(magBuf);

        // Print for debugging (comment out for power saving)
        Serial.print("Accel: ");
        Serial.println(accelBuf);
        Serial.print("Gyro: ");
        Serial.println(gyroBuf);
        Serial.print("Mag: ");
        Serial.println(magBuf);
      }

      // Read and send heart rate
      int bpm = readHeartRateBPM();
      if (bpm > 0) {
        char bpmBuf[8];
        snprintf(bpmBuf, sizeof(bpmBuf),"HR " "%d", bpm);
        heartChar.writeValue(bpmBuf);
        Serial.print("Heart Rate: ");
        Serial.print(bpm);
        Serial.println(" bpm");
      } else {
        Serial.println("Heart Rate: Not available");
      }

      delay(100); // Adjust for desired update rate
    }

    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}