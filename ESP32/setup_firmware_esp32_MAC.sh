#!/bin/bash
# setup_firmware_esp32_MAC.sh
# This script will erase and flash an ESP32 with MicroPython firmware on macOS.
# Usage: source setup_firmware_esp32_MAC.sh <firmware_file.bin>

# Check if the OS is macOS.
if [[ "$OSTYPE" != darwin* ]]; then
    echo "Error: This command only works on macOS. Exiting."
    return 1
fi

# Check if firmware file is provided as an argument.
if [ -z "$1" ]; then
    echo "Usage: source setup_firmware_esp32_MAC.sh <firmware_file.bin>"
    return 1
fi

FIRMWARE_FILE="$1"

# Verify the firmware file exists.
if [ ! -f "$FIRMWARE_FILE" ]; then
    echo "Error: Firmware file '$FIRMWARE_FILE' not found."
    return 1
fi

# Check if esptool.py is installed.
if ! command -v esptool.py &>/dev/null; then
    echo "Error: esptool.py not found. Please install it using 'pip3 install esptool'."
    return 1
fi

# Erase the flash.
echo "Erasing ESP32 flash..."
esptool.py erase_flash
if [ $? -ne 0 ]; then
    echo "Error during flash erase."
    return 1
fi

# Flash the firmware.
echo "Flashing firmware '$FIRMWARE_FILE' to ESP32..."
esptool.py --baud 460800 write_flash 0x1000 "$FIRMWARE_FILE"
if [ $? -ne 0 ]; then
    echo "Error during firmware flashing."
    return 1
fi

echo "Firmware successfully flashed to the ESP32!"
