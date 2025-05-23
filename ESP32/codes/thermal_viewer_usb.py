import serial, numpy as np, matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Serial connection setup
PORT = '/dev/cu.usbserial-0001'  # adjust if different
ser = serial.Serial(PORT, 115200, timeout=None)

# Custom colormap
colors = [
    (0.0, 'black'),
    (0.2, 'darkred'),
    (0.3, 'red'),
    (0.4, 'orange'),
    (1.0, 'yellow'),
]
cmap = mcolors.LinearSegmentedColormap.from_list('heat', colors)

# Plot setup
fig, ax = plt.subplots()
img = ax.imshow(np.zeros((24,32)), cmap=cmap, vmin=25, vmax=32)
plt.colorbar(img, ax=ax)
plt.title("Live MLX90640 frame")
plt.ion()
plt.show()

# Main loop with reset handling
while True:
    try:
        line = ser.readline().decode().strip()
        if not line:
            continue  # timeout or empty line
        values = np.fromstring(line, sep=',')
        if values.size != 768:
            print("⚠️ Bad frame, skipping")
            continue

        img.set_data(values.reshape(24,32))
        plt.pause(0.001)

    except (serial.SerialException, UnicodeDecodeError) as e:
        print(f"⚠️ Serial connection lost ({e}). Waiting for reconnection...")
        ser.close()
        connected = False
        # Try reconnecting until it succeeds
        while not connected:
            try:
                ser = serial.Serial(PORT, 115200, timeout=None)
                connected = True
                print("Serial connection restored!")
            except serial.SerialException:
                plt.pause(0.5)  # Wait a bit before retrying
