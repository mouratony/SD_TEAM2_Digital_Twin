# main.py – ESP32 + MLX90640 (Optimized for Memory & Stability)
# Streams CSV frames at ~4Hz; Visual LED feedback for memory errors.

import time, sys, gc, array
from machine import I2C, Pin
import mlx90640

# LED indicator setup (on GPIO 2)
LED = Pin(2, Pin.OUT)
LED.off()

# Optimized I2C frequency for MLX90640
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400_000)

# Use efficient memory structure
frame = array.array('f', [0]*768)

# Delayed camera initialization with memory-safe retries
cam = None
time.sleep(2)

while not cam:
    try:
        cam = mlx90640.MLX90640(i2c)
        cam.refresh_rate = mlx90640.RefreshRate.REFRESH_4_HZ
    except MemoryError:
        gc.collect()
        time.sleep(1)

# CSV streaming function
def send_csv(values):
    w = sys.stdout.write
    for i, v in enumerate(values):
        w("{:.2f}".format(v))
        w(',' if i < 767 else '\n')

# Main data capture loop
while True:
    try:
        LED.on()
        cam.get_frame(frame)
        send_csv(frame)
        gc.collect()
    except MemoryError:
        # Quickly blink LED to indicate memory error
        for _ in range(5):
            LED.on()
            time.sleep(0.1)
            LED.off()
            time.sleep(0.1)
        from machine import reset
        reset()
    except Exception:
        pass  # Quietly handle non-critical errors to maintain clean CSV output
    finally:
        LED.off()

    # Matches the 4 Hz refresh rate for smooth output
    time.sleep(0.25)
