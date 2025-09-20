import asyncio
import csv
import time
import logging
import os
from datetime import datetime
from bleak import BleakClient, BleakScanner

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# UUIDs (matching Arduino code)
DEVICE_NAME = "nRF_IMU"
ACCEL_CHAR_UUID = "0000A001-0000-1000-8000-00805F9B34FB"
GYRO_CHAR_UUID  = "0000B001-0000-1000-8000-00805F9B34FB"
MAG_CHAR_UUID   = "0000C001-0000-1000-8000-00805F9B34FB"
HEART_CHAR_UUID = "0000D001-0000-1000-8000-00805F9B34FB"

# ---------- Folder and CSV setup ----------
FOLDER_NAME = "sensor_csv_data"
if not os.path.exists(FOLDER_NAME):
    os.makedirs(FOLDER_NAME)

CSV_PATH = os.path.join(FOLDER_NAME, f"sensor_data_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv")
csv_file = open(CSV_PATH, "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["TimeStamp", "Gx", "Gy", "Gz", "Ax", "Ay", "Az", "Mx", "My", "Mz", "BPM"])
csv_file.flush()  # Immediately write header

# Buffer to store latest sensor data
sensor_data = {
    "accel": None,
    "gyro": None,
    "mag": None,
    "heart": None
}

def write_csv_if_complete(timestamp):
    """Write to CSV if all sensor data (accel, gyro, mag, heart) is available."""
    if all(sensor_data.values()):
        writer.writerow([
            timestamp,
            *sensor_data["gyro"],
            *sensor_data["accel"],
            *sensor_data["mag"],
            sensor_data["heart"]
        ])
        csv_file.flush()
        print(f"Data written at {timestamp} Done")

        # Reset buffer after writing
        sensor_data["accel"] = None
        sensor_data["gyro"] = None
        sensor_data["mag"] = None
        sensor_data["heart"] = None
    else:
        print(f"Waiting for complete data set... Current buffer: {sensor_data}")

async def notification_handler(sender, data):
    """Handle incoming BLE notifications, print to console, and save to CSV."""
    logging.debug(f"Received data from {sender.uuid}: {data}")
    try:
        value = data.decode("utf-8")
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if sender.uuid.lower() == ACCEL_CHAR_UUID.lower():
            values = value.split(" ")[1].split(",")
            ax, ay, az = map(float, values)
            sensor_data["accel"] = [ax, ay, az]
            print(f"Accelerometer: x={ax:.2f}, y={ay:.2f}, z={az:.2f} m/s²")
            write_csv_if_complete(timestamp)
            
        elif sender.uuid.lower() == GYRO_CHAR_UUID.lower():
            values = value.split(" ")[1].split(",")
            gx, gy, gz = map(float, values)
            sensor_data["gyro"] = [gx, gy, gz]
            print(f"Gyroscope: x={gx:.2f}, y={gy:.2f}, z={gz:.2f} deg/s")
            write_csv_if_complete(timestamp)
            
        elif sender.uuid.lower() == MAG_CHAR_UUID.lower():
            values = value.split(" ")[1].split(",")
            mx, my, mz = map(float, values)
            sensor_data["mag"] = [mx, my, mz]
            print(f"Magnetometer: x={mx:.2f}, y={my:.2f}, z={mz:.2f} uT")
            write_csv_if_complete(timestamp)
            
        elif sender.uuid.lower() == HEART_CHAR_UUID.lower():
            bpm = int(value.split(" ")[1])
            sensor_data["heart"] = bpm
            print(f"Heart Rate: {bpm} bpm")
            write_csv_if_complete(timestamp)
            
    except (UnicodeDecodeError, ValueError, IndexError) as e:
        logging.error(f"Error processing data from {sender.uuid}: {e}, Raw data: {data}")

async def main():
    print("Scanning for nRF_IMU...")
    device = None
    devices = await BleakScanner.discover(timeout=15.0)
    for d in devices:
        if d.name == DEVICE_NAME:
            device = d
            break

    if not device:
        print("Device not found!")
        return

    print(f"Found device: {device.name} ({device.address})")

    async with BleakClient(device.address, timeout=30.0) as client:
        print(f"Connected to {device.name}")

        try:
            await client.start_notify(ACCEL_CHAR_UUID, notification_handler)
            await client.start_notify(GYRO_CHAR_UUID, notification_handler)
            await client.start_notify(MAG_CHAR_UUID, notification_handler)
            await client.start_notify(HEART_CHAR_UUID, notification_handler)
            print("Subscribed to all characteristics.")
        except Exception as e:
            logging.error(f"Failed to subscribe to notifications: {e}")
            return

        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("Disconnecting...")
            await client.stop_notify(ACCEL_CHAR_UUID)
            await client.stop_notify(GYRO_CHAR_UUID)
            await client.stop_notify(MAG_CHAR_UUID)
            await client.stop_notify(HEART_CHAR_UUID)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        csv_file.close()
        print(f"Saved to {CSV_PATH}")
