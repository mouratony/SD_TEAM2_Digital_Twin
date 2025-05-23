import uasyncio as asyncio
import aioble
import bluetooth
from machine import I2C, Pin, reset
import mlx90640
import array, gc, time

SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHARACTERISTIC_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

# LED setup on GPIO 2
LED = Pin(2, Pin.OUT)
LED.off()

# I2C and MLX90640 setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400_000)
cam = mlx90640.MLX90640(i2c)
cam.refresh_rate = mlx90640.RefreshRate.REFRESH_4_HZ
frame = array.array('f', [0]*768)

CHUNK_SIZE = 200

def memory_error_blink():
    for _ in range(5):
        LED.on()
        time.sleep(0.1)
        LED.off()
        time.sleep(0.1)

async def main():
    service = aioble.Service(SERVICE_UUID)
    characteristic = aioble.Characteristic(
        service, CHARACTERISTIC_UUID, notify=True, read=True
    )
    aioble.register_services(service)

    while True:
        print("Advertising BLE thermal camera service as 'ESP32-BLE'...")
        connection = await aioble.advertise(
            interval_us=100_000,
            name="ESP32-BLE",
            services=[SERVICE_UUID]
        )

        print("Device connected:", connection.device)

        try:
            while connection.is_connected():
                # Capture frame with LED indication
                LED.on()
                cam.get_frame(frame)
                LED.off()

                # Prepare CSV data with a newline at the end
                csv_data = ','.join('{:.2f}'.format(val) for val in frame) + '\n'
                csv_bytes = csv_data.encode()

                # Send CSV data in chunks
                for start in range(0, len(csv_bytes), CHUNK_SIZE):
                    chunk = csv_bytes[start:start+CHUNK_SIZE]
                    characteristic.write(chunk)
                    characteristic.notify(connection, chunk)
                    await asyncio.sleep(0.05)

                print("Sent thermal frame via BLE")

                await asyncio.sleep(0.25)
                gc.collect()

        except (asyncio.CancelledError, aioble.DeviceDisconnectedError):
            print("Device disconnected, restarting advertising.")

        except MemoryError:
            print("Memory error encountered! Blinking LED and resetting ESP32...")
            memory_error_blink()
            time.sleep(1)
            reset()

asyncio.run(main())
