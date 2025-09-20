import asyncio
import struct
import csv
import os
from datetime import datetime
from bleak import BleakClient, BleakScanner

# ====== UUIDs (CC2650 SensorTag) ======
MOVEMENT_DATA_UUID   = "f000aa81-0451-4000-b000-000000000000"
MOVEMENT_CONFIG_UUID = "f000aa82-0451-4000-b000-000000000000"
MOVEMENT_PERIOD_UUID = "f000aa83-0451-4000-b000-000000000000"

MOVEMENT_CONFIG_BYTES = bytearray([0x7F, 0x02])
MOVEMENT_PERIOD_BYTE  = bytearray([0x0A])  # 100ms

# ====== Prepare folders ======
os.makedirs("SensorTag_Device1", exist_ok=True)
os.makedirs("SensorTag_Device2", exist_ok=True)

# ====== File setup ======
timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
csv_path_1 = os.path.join("SensorTag_Device1", f"device1_{timestamp}.csv")
csv_path_2 = os.path.join("SensorTag_Device2", f"device2_{timestamp}.csv")

csv_file_1 = open(csv_path_1, "w", newline="")
csv_file_2 = open(csv_path_2, "w", newline="")

writer1 = csv.writer(csv_file_1)
writer2 = csv.writer(csv_file_2)

writer1.writerow(["TimeStamp", "Gx", "Gy", "Gz", "Ax", "Ay", "Az", "Mx", "My", "Mz"])
writer2.writerow(["TimeStamp", "Gx", "Gy", "Gz", "Ax", "Ay", "Az", "Mx", "My", "Mz"])

# ====== Notification callback ======
def create_callback(writer, label):
    def movement_cb(_: int, data: bytearray):
        gx, gy, gz, ax, ay, az, mx, my, mz = struct.unpack("<hhhhhhhhh", data[:18])
        timestamp = datetime.now().strftime('%H:%M:%S')
        writer.writerow([timestamp, gx, gy, gz, ax, ay, az, mx, my, mz])
        if label == "Device 1":
            csv_file_1.flush()
        else:
            csv_file_2.flush()
        # No print statement
    return movement_cb

# ====== Connect and Stream ======
async def connect_and_stream(tag, name, writer, retries=3):
    for attempt in range(retries):
        try:
            print(f"Attempting connection to {name} ({tag.address})... Try {attempt + 1}")
            client = BleakClient(tag.address)
            await client.connect(timeout=10.0)

            if not client.is_connected:
                raise Exception(f"{name}: Could not connect.")

            print(f"{name}: Connected.")

            try:
                await client.exchange_mtu(247)
            except Exception:
                pass  # Some devices don't support MTU exchange

            await client.write_gatt_char(MOVEMENT_CONFIG_UUID, MOVEMENT_CONFIG_BYTES)
            await client.write_gatt_char(MOVEMENT_PERIOD_UUID,  MOVEMENT_PERIOD_BYTE)

            await client.start_notify(MOVEMENT_DATA_UUID, create_callback(writer, name))
            print(f"{name}: Streaming IMU data...")

            return client

        except Exception as e:
            print(f"{name}: Connection attempt {attempt + 1} failed - {e}")
            await asyncio.sleep(3)

    print(f"{name}: Failed to connect after {retries} attempts.")
    return None

# ====== Main ======
async def main():
    print("Scanning for SensorTags…")
    devices = await BleakScanner.discover(timeout=30.0)
    tags = [d for d in devices if d.name and ("CC2650" in d.name or "SensorTag" in d.name)]

    if len(tags) < 2:
        print(f"Only found {len(tags)} SensorTag(s). Need 2.")
        return

    tag1, tag2 = tags[:2]
    print(f"Found Device 1: {tag1.name} @ {tag1.address}")
    print(f"Found Device 2: {tag2.name} @ {tag2.address}")

    client1 = await connect_and_stream(tag1, "Device 1", writer1)
    await asyncio.sleep(2)
    client2 = await connect_and_stream(tag2, "Device 2", writer2)

    if not client1 or not client2:
        print("One or both devices failed to connect.")
        return

    try:
        await asyncio.Event().wait()  # Run until stopped manually
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Stopping notifications...")
    finally:
        if client1:
            await client1.stop_notify(MOVEMENT_DATA_UUID)
            await client1.disconnect()
        if client2:
            await client2.stop_notify(MOVEMENT_DATA_UUID)
            await client2.disconnect()

        print("Disconnected.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        csv_file_1.close()
        csv_file_2.close()
        print(f"Saved Device 1 data to: {csv_path_1}")
        print(f"Saved Device 2 data to: {csv_path_2}")
