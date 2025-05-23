Run The following to see the output of my esp32:

```screen <usb_port_connected_to_esp32> 115200```

i.e.:

```screen /dev/cu.usbserial-0001 115200```

exit screen with:

```Control + A, then K```


## 🔷 Bluetooth (BLE) Library Setup for ESP32

To establish Bluetooth Low Energy (BLE) communication between your **ESP32** and your Mac, you'll need the `aioble` MicroPython library.

### 📌 Required Libraries

- **`aioble`**: Simplifies BLE communication for MicroPython.

> Note: `asyncio` is already included in recent versions of MicroPython.

### 📌 Installation Steps

#### 1\. Download the Library (`aioble`)  

Use your Mac terminal to quickly download all necessary files into a directory named `aioble`:

```bash
mkdir aioble
cd aioble

curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/__init__.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/central.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/client.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/core.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/device.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/l2cap.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/peripheral.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/security.py
curl -O https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/bluetooth/aioble/aioble/server.py
```

2. Upload to ESP32
Using PyMakr (VS Code) upload the downloaded aioble folder directly to your ESP32 filesystem. The resulting structure should look like this:

ESP32 filesystem:
├── aioble/
│   ├── __init__.py
│   ├── central.py
│   ├── client.py
│   ├── core.py
│   ├── device.py
│   ├── l2cap.py
│   ├── peripheral.py
│   ├── security.py
│   └── server.py

## ✅ BLE Communication Setup and Validation Test

This step ensures your ESP32 can communicate via Bluetooth Low Energy (BLE) clearly and reliably with your Mac. 

### 📌 Overview
The ESP32 uses MicroPython and the `aioble` BLE library to advertise itself as a BLE peripheral. A basic validation test is performed using the LightBlue app on your Mac.

### ⚙️ ESP32 Setup
The ESP32 uses the following simplified `ble_test.py` script to advertise a BLE service and send periodic notifications:

```python
import uasyncio as asyncio
import aioble
import bluetooth

SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHARACTERISTIC_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

async def main():
    service = aioble.Service(SERVICE_UUID)
    characteristic = aioble.Characteristic(
        service, CHARACTERISTIC_UUID, notify=True, read=True
    )
    aioble.register_services(service)

    while True:
        print("Advertising BLE service as 'ESP32-BLE'...")

        connection = await aioble.advertise(
            interval_us=100_000,
            name="ESP32-BLE",
            services=[SERVICE_UUID]
        )

        print("Device connected:", connection.device)

        try:
            while connection.is_connected():
                data = b'Hello World'
                characteristic.write(data)
                characteristic.notify(connection, data)
                print("Sent:", data.decode())
                await asyncio.sleep(2)

        except (asyncio.CancelledError, aioble.DeviceDisconnectedError):
            print("Device disconnected, restarting advertising.")

asyncio.run(main())
```

### Validation Test using LightBlue (Mac)

To verify successful BLE communication:

1. **Install the LightBlue app**:
   - Available on the [Mac App Store](https://apps.apple.com/us/app/lightblue/id557428110).

2. **BLE Device Scanning**:
   - Open LightBlue and scan for BLE devices.
   - The ESP32 device appears as `"ESP32-BLE"`.

3. **Connecting and Receiving Notifications**:
   - Click on `"ESP32-BLE"` to connect.
   - Locate the advertised service UUID (`12345678-1234-5678-1234-56789abcdef0`) and its characteristic UUID (`12345678-1234-5678-1234-56789abcdef1`).
   - Subscribe to notifications from this characteristic.

4. **Verification**:
   - You should clearly receive `"Hello World"` messages every 2 seconds, indicating successful BLE communication.

### 🎯 Expected Validation Outcome

- ESP32 REPL prints clearly:

```bash
Advertising BLE service as 'ESP32-BLE'...
Device connected: Device(...)
Sent: Hello World
Sent: Hello World
...
```