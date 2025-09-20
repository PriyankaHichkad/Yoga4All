import asyncio
import struct
import csv
from datetime import datetime
from bleak import BleakClient, BleakScanner

# ====== UUIDs (CC2650 SensorTag) ======
MOVEMENT_DATA_UUID   = "f000aa81-0451-4000-b000-000000000000"
MOVEMENT_CONFIG_UUID = "f000aa82-0451-4000-b000-000000000000"
MOVEMENT_PERIOD_UUID = "f000aa83-0451-4000-b000-000000000000"

# 0x7F enables gyro+accel+mag on all axes, 0x02 sets accel range (±8 g)
MOVEMENT_CONFIG_BYTES = bytearray([0x7F, 0x02])
# 0x0A => 100 ms (10 Hz). Smaller values are faster (0x01 ~10 ms), but may be unstable
MOVEMENT_PERIOD_BYTE  = bytearray([0x0A])

CSV_PATH = "imu_raw.csv"

# ---------- CSV setup ----------
csv_file = open(CSV_PATH, "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["timestamp_iso",
                 "gyro_x_raw","gyro_y_raw","gyro_z_raw",
                 "acc_x_raw","acc_y_raw","acc_z_raw",
                 "mag_x_raw","mag_y_raw","mag_z_raw"])

# ---------- Notification callback ----------
def movement_cb(_: int, data: bytearray):
    # Data layout: 9 x int16, little-endian: Gx,Gy,Gz, Ax,Ay,Az, Mx,My,Mz
    gx, gy, gz, ax, ay, az, mx, my, mz = struct.unpack("<hhhhhhhhh", data[:18])

    # Write raw values
    writer.writerow([datetime.now().isoformat(),
                     gx, gy, gz, ax, ay, az, mx, my, mz])

async def main():
    print("Scanning for SensorTag…")
    devices = await BleakScanner.discover(timeout=5.0)
    tags = [d for d in devices if d.name and ("CC2650" in d.name or "SensorTag" in d.name)]
    if not tags:
        print("No SensorTag found."); return
    dev = tags[0]
    print(f"Found {dev.name} @ {dev.address}")

    async with BleakClient(dev.address) as client:
        if not client.is_connected:
            print("Connection failed."); return
        print("Connected.")

        # Optional: increase MTU (Linux/macOS). Ignore exceptions on Windows.
        try:
            await client.exchange_mtu(247)
        except Exception:
            pass

        # Enable movement sensor & set period
        await client.write_gatt_char(MOVEMENT_CONFIG_UUID, MOVEMENT_CONFIG_BYTES)
        await client.write_gatt_char(MOVEMENT_PERIOD_UUID,  MOVEMENT_PERIOD_BYTE)

        # Subscribe to notifications
        await client.start_notify(MOVEMENT_DATA_UUID, movement_cb)
        print("Streaming raw IMU data… (Ctrl+C to stop)")

        # Keep running forever
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await client.stop_notify(MOVEMENT_DATA_UUID)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        csv_file.close()
        print(f"Saved to {CSV_PATH}")
