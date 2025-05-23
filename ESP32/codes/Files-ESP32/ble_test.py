import asyncio
import aioble
import bluetooth

SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHARACTERISTIC_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

async def main():
    # Create and register a service and characteristic explicitly
    service = aioble.Service(SERVICE_UUID)
    characteristic = aioble.Characteristic(service, CHARACTERISTIC_UUID, read=True, notify=True)
    aioble.register_services(service)  # explicitly register the service

    print("📡 Advertising BLE service as 'ESP32-BLE'...")

    while True:
        async with await aioble.advertise(
            interval_us=100_000,
            name="ESP32-BLE",
            services=[SERVICE_UUID]
        ) as connection:
            print("✅ Device connected:", connection.device)
            try:
                while connection.is_connected():
                    characteristic.write(b'Hello World')
                    await characteristic.notify(connection)
                    print("📤 Sent: Hello World")
                    await asyncio.sleep(2)
            except asyncio.CancelledError:
                print("⚠️ Connection cancelled.")
            finally:
                print("⚠️ Device disconnected, restarting advertising.")

asyncio.run(main())
