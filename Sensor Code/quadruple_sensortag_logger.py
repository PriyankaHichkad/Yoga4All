import asyncio
import csv
import logging
import os
from datetime import datetime
from bleak import BleakClient, BleakScanner, BleakError

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# UUIDs (matching Arduino code)
DEVICE_NAME_1 = "nRF_IMU_1"
DEVICE_NAME_2 = "nRF_IMU_2"
DEVICE_NAME_3 = "nRF_IMU_3"
DEVICE_NAME_4 = "nRF_IMU"
ACCEL_CHAR_UUID = "0000A001-0000-1000-8000-00805F9B34FB"
GYRO_CHAR_UUID = "0000B001-0000-1000-8000-00805F9B34FB"
MAG_CHAR_UUID = "0000C001-0000-1000-8000-00805F9B34FB"

# Folder setup
BASE_FOLDER = "sensor_csv_data"
DEVICE_1_FOLDER = os.path.join(BASE_FOLDER, "device_1")
DEVICE_2_FOLDER = os.path.join(BASE_FOLDER, "device_2")
DEVICE_3_FOLDER = os.path.join(BASE_FOLDER, "device_3")
DEVICE_4_FOLDER = os.path.join(BASE_FOLDER, "device_4")

# Create folders if they don't exist
for folder in [DEVICE_1_FOLDER, DEVICE_2_FOLDER, DEVICE_3_FOLDER, DEVICE_4_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# CSV file setup
timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
CSV_PATH_1 = os.path.join(DEVICE_1_FOLDER, f"sensor_data_nRF_IMU_1_{timestamp}.csv")
CSV_PATH_2 = os.path.join(DEVICE_2_FOLDER, f"sensor_data_nRF_IMU_2_{timestamp}.csv")
CSV_PATH_3 = os.path.join(DEVICE_3_FOLDER, f"sensor_data_nRF_IMU_3_{timestamp}.csv")
CSV_PATH_4 = os.path.join(DEVICE_4_FOLDER, f"sensor_data_nRF_IMU_{timestamp}.csv")

# Initialize CSV files and writers
csv_files = {}
writers = {}
for path, label in [(CSV_PATH_1, "Device 1"), (CSV_PATH_2, "Device 2"), (CSV_PATH_3, "Device 3"), (CSV_PATH_4, "Device 4")]:
    csv_files[label] = open(path, "w", newline="")
    writers[label] = csv.writer(csv_files[label])
    writers[label].writerow(["TimeStamp", "Ax", "Ay", "Az", "Gx", "Gy", "Gz", "Mx", "My", "Mz"])
    csv_files[label].flush()

# Buffer to store latest sensor data for each device
sensor_data = {
    "Device 1": {"accel": None, "gyro": None, "mag": None},
    "Device 2": {"accel": None, "gyro": None, "mag": None},
    "Device 3": {"accel": None, "gyro": None, "mag": None},
    "Device 4": {"accel": None, "gyro": None, "mag": None}
}

async def write_csv(timestamp, sensor_data, writer, csv_file, device_label):
    """Write to CSV only if all sensor data is available."""
    if all(sensor_data.values()):
        writer.writerow([timestamp, *sensor_data["accel"], *sensor_data["gyro"], *sensor_data["mag"]])
        csv_file.flush()
        print(f"Data written for {device_label} at {timestamp}: A={sensor_data['accel']}, G={sensor_data['gyro']}, M={sensor_data['mag']}")
        # Reset buffer
        sensor_data["accel"] = None
        sensor_data["gyro"] = None
        sensor_data["mag"] = None
    else:
        logging.debug(f"Skipping CSV write for {device_label}, incomplete data: {sensor_data}")

def notification_handler(sender, data, device_label, sensor_data, writer, csv_file):
    """Handle incoming BLE notifications, print to console, and schedule CSV write."""
    logging.debug(f"Received data from {device_label} ({sender.uuid}): {data.hex()}")
    try:
        value = data.decode("utf-8")
        timestamp = datetime.now().strftime('%H:%M:%S')
        logging.info(f"{device_label} received: {value}")
        
        if sender.uuid.lower() == ACCEL_CHAR_UUID.lower():
            values = value.split(" ")[1].split(",")
            ax, ay, az = map(float, values)
            sensor_data["accel"] = [ax, ay, az]
            print(f"{device_label} Accelerometer: x={ax:.2f}, y={ay:.2f}, z={az:.2f} m/s²")
            asyncio.create_task(write_csv(timestamp, sensor_data, writer, csv_file, device_label))
            
        elif sender.uuid.lower() == GYRO_CHAR_UUID.lower():
            values = value.split(" ")[1].split(",")
            gx, gy, gz = map(float, values)
            sensor_data["gyro"] = [gx, gy, gz]
            print(f"{device_label} Gyroscope: x={gx:.2f}, y={gy:.2f}, z={gz:.2f} deg/s")
            asyncio.create_task(write_csv(timestamp, sensor_data, writer, csv_file, device_label))
            
        elif sender.uuid.lower() == MAG_CHAR_UUID.lower():
            values = value.split(" ")[1].split(",")
            mx, my, mz = map(float, values)
            sensor_data["mag"] = [mx, my, mz]
            print(f"{device_label} Magnetometer: x={mx:.2f}, y={my:.2f}, z={mz:.2f} uT")
            asyncio.create_task(write_csv(timestamp, sensor_data, writer, csv_file, device_label))
            
    except (UnicodeDecodeError, ValueError, IndexError) as e:
        logging.error(f"Error processing data from {device_label} ({sender.uuid}): {e}, Raw data: {data.hex()}")
        # Write placeholder data only if no valid data has been written recently
        timestamp = datetime.now().strftime('%H:%M:%S')
        if not any(sensor_data.values()):  # Only write if buffer is empty
            asyncio.create_task(write_csv(timestamp, sensor_data, writer, csv_file, device_label))

async def connect_and_subscribe(device, device_label, max_retries=3):
    """Attempt to connect to the device and subscribe to notifications with retries."""
    for attempt in range(1, max_retries + 1):
        try:
            async with BleakClient(device.address, timeout=30.0) as client:
                print(f"Connected to {device.name} ({device_label}, Attempt {attempt})")
                
                # Verify connection
                if not client.is_connected:
                    logging.error(f"Client not connected after initialization for {device_label}")
                    continue
                
                # Subscribe to notifications with delay
                subscribed_uuids = []
                for uuid in [ACCEL_CHAR_UUID, GYRO_CHAR_UUID, MAG_CHAR_UUID]:
                    try:
                        await client.start_notify(uuid, lambda sender, data: notification_handler(sender, data, device_label, sensor_data[device_label], writers[device_label], csv_files[device_label]))
                        logging.info(f"Successfully subscribed to {uuid} for {device_label}")
                        subscribed_uuids.append(uuid)
                        await asyncio.sleep(0.5)
                    except BleakError as e:
                        logging.warning(f"Failed to subscribe to {uuid} for {device_label}: {e}. Skipping...")
                
                if not subscribed_uuids:
                    logging.error(f"No characteristics subscribed for {device_label}. Terminating connection.")
                    return
                
                print(f"Subscribed to characteristics for {device_label}: {subscribed_uuids}")
                
                # Keep connection alive until interrupted
                try:
                    await asyncio.Event().wait()
                except KeyboardInterrupt:
                    print(f"Disconnecting from {device_label}...")
                    for uuid in subscribed_uuids:
                        try:
                            await client.stop_notify(uuid)
                            logging.info(f"Stopped notifications for {uuid} on {device_label}")
                        except Exception as e:
                            logging.error(f"Error stopping notifications for {uuid} on {device_label}: {e}")
                    return
                
        except BleakError as e:
            logging.error(f"Connection attempt {attempt} failed for {device_label}: {e}")
            if attempt < max_retries:
                print(f"Retrying connection for {device_label} ({attempt + 1}/{max_retries})...")
                await asyncio.sleep(2)
            else:
                logging.error(f"Max retries reached for {device_label}. Could not connect.")
                return
        except Exception as e:
            logging.error(f"Unexpected error during connection for {device_label}: {e}")
            return

async def main():
    print("Scanning for nRF_IMU_1, nRF_IMU_2, nRF_IMU_3, and nRF_IMU...")
    devices = {
        "Device 1": None,
        "Device 2": None,
        "Device 3": None,
        "Device 4": None
    }
    try:
        scanned_devices = await BleakScanner.discover(timeout=15.0)
        for d in scanned_devices:
            logging.debug(f"Found device: {d.name} ({d.address})")
            if d.name == DEVICE_NAME_1:
                devices["Device 1"] = d
            elif d.name == DEVICE_NAME_2:
                devices["Device 2"] = d
            elif d.name == DEVICE_NAME_3:
                devices["Device 3"] = d
            elif d.name == DEVICE_NAME_4:
                devices["Device 4"] = d

        # Check if any devices were found
        found_devices = {label: dev for label, dev in devices.items() if dev is not None}
        if not found_devices:
            print("No devices found! Need at least one of nRF_IMU_1, nRF_IMU_2, nRF_IMU_3, or nRF_IMU.")
            return

        # Log found devices
        print("Found devices:")
        for label, dev in found_devices.items():
            print(f"{dev.name} ({dev.address}) as {label}")

        # Create connection tasks for all found devices
        tasks = [connect_and_subscribe(dev, label) for label, dev in found_devices.items()]

        # Run connection tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
    finally:
        for label, csv_file in csv_files.items():
            csv_file.close()
            if label == "Device 1":
                print(f"Saved Device 1 data to {CSV_PATH_1}")
            elif label == "Device 2":
                print(f"Saved Device 2 data to {CSV_PATH_2}")
            elif label == "Device 3":
                print(f"Saved Device 3 data to {CSV_PATH_3}")
            elif label == "Device 4":
                print(f"Saved Device 4 data to {CSV_PATH_4}")

if __name__ == "__main__":
    asyncio.run(main())