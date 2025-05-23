import asyncio
from bleak import BleakClient, BleakScanner
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

DEVICE_NAME = "ESP32-BLE"
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"

# Custom colormap
colors = [
    (0.0, 'black'),
    (0.15, 'black'),
    (0.2, 'darkred'),
    (0.25, 'red'),
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

frame_buffer = bytearray()
save_frames = False
frames_to_save = 0
label = 0

# Helper to clear buffer
def clear_buffer():
    global frame_buffer
    frame_buffer = bytearray()

# Notification handler
async def notification_handler(sender, data):
    global frame_buffer, save_frames, frames_to_save, label

    frame_buffer.extend(data)

    if frame_buffer.count(b',') >= 767:
        try:
            frame_str = frame_buffer.decode()
            values = np.fromstring(frame_str, sep=',')

            if values.size == 768:
                reshaped_frame = values.reshape(24,32)
                img.set_data(reshaped_frame)
                plt.pause(0.001)

                if save_frames and frames_to_save > 0:
                    frame_id = random.randint(0, 10000)
                    filename = f"thermal_frame_label_{label}_ID{frame_id:05d}.npy"

                    np.save("dataset/"+filename, reshaped_frame)

                    print(f"Saved: {filename}")
                    frames_to_save -= 1

                    if frames_to_save == 0:
                        save_frames = False
                        print("Done saving frames.")

            else:
                print("⚠️ Incomplete frame received, skipping.")

        except UnicodeDecodeError:
            print("⚠️ Decode error, corrupted data. Skipping frame.")

        clear_buffer()

# Function to capture keypresses
def on_key(event):
    global save_frames, frames_to_save, label

    if event.key == 'p':
        try:
            frames_to_save = int(input("Enter number of frames to save: "))
            label = int(input("Enter label integer: "))
            save_frames = True
            print(f"Starting to save {frames_to_save} frames with label {label}.")
        except ValueError:
            print("Invalid input. Try again.")

fig.canvas.mpl_connect('key_press_event', on_key)

async def connect_and_receive():
    while True:
        print("Scanning for ESP32-BLE...")

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
