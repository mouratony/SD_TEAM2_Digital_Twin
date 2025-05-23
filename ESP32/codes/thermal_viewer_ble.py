import asyncio
from bleak import BleakClient, BleakScanner
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

DEVICE_NAME = "ESP32-BLE"
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"

# Custom colormap
colors = [
    (0.0, 'black'),
    (0.2, 'black'),
    (0.275, 'darkred'),
    (0.3, 'red'),
    (0.5, 'orange'),
    (1.0, 'yellow'),
]
cmap = mcolors.LinearSegmentedColormap.from_list('heat', colors)

# Plot setup
fig, ax = plt.subplots()
img = ax.imshow(np.zeros((24,32)), cmap=cmap, vmin=25, vmax=32)
plt.colorbar(img, ax=ax)
plt.title("Live MLX90640 BLE frame")
plt.ion()
plt.show()

# Buffer to accumulate received data
frame_buffer = bytearray()

def clear_buffer():
    global frame_buffer
    frame_buffer = bytearray()

async def notification_handler(sender, data):
    global frame_buffer

    # Accumulate incoming chunks
    frame_buffer.extend(data)

    # Check if a complete frame is received (768 floats, 767 commas)
    if frame_buffer.count(b',') >= 767:
        try:
            # Convert buffer to numpy array
            frame_str = frame_buffer.decode()
            values = np.fromstring(frame_str, sep=',')

            if values.size == 768:
                # Successfully received full frame; visualize
                img.set_data(values.reshape(24,32))
                plt.pause(0.001)
            else:
                print("⚠️ Incomplete frame received, skipping.")

        except UnicodeDecodeError:
            print("⚠️ Decode error, corrupted data. Skipping frame.")

        # Always clear buffer after handling
        clear_buffer()

async def connect_and_receive():
    while True:
        print("Scanning for ESP32-BLE using Service UUID...")

        # Clearly filter device directly by Service UUID
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: SERVICE_UUID.lower() in [uuid.lower() for uuid in ad.service_uuids],
            timeout=10
        )

        if device is None:
            print("ESP32-BLE not found. Retrying in 2 seconds...")
            await asyncio.sleep(2)
            continue

        print(f"Connecting to {device.name} ({device.address})...")
        try:
            async with BleakClient(device.address) as client:
                print("Connected! Subscribing to notifications...")
                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

                while client.is_connected:
                    await asyncio.sleep(1)

                print("ESP32 disconnected, restarting scan...")

        except Exception as e:
            print(f"Error encountered: {e}. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(connect_and_receive())
