import time
import board
import busio
import adafruit_scd4x

# Constants
CO2_SENSOR = "CO2"
TEMP_SENSOR = "Temperature"
HUM_SENSOR = "Humidity"


class SCD40:
    def __init__(self, fahrenheit=False):
        # Initialize I2C communication
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_scd4x.SCD4X(self.i2c)
        self.use_fahrenheit = fahrenheit

    def init(self):
        """Reinitialize the sensor."""
        self.stop_measurements()
        self.start_measurements()

    def start_measurements(self):
        """Start periodic measurement."""
        self.sensor.start_periodic_measurement()
        print("Started periodic measurements.")
        # Wait for some time to ensure the sensor has started measurements
        time.sleep(5)  # 5 seconds delay to allow the sensor to initialize

    def stop_measurements(self):
        """Stop periodic measurement."""
        self.sensor.stop_periodic_measurement()
        print("Stopped periodic measurements.")

    def read_measurement(self):
        """Read the sensor data."""
        try:
            # Wait until data is ready (check if data is available)
            if self.sensor.data_ready:
                co2, temp, humidity = self.sensor.read_measurement()
                print(f"CO2: {co2} ppm, Temperature: {temp} °C, Humidity: {humidity} %")
                
                # Convert temperature to Fahrenheit if needed
                if self.use_fahrenheit:
                    temp = self.celsius_to_fahrenheit(temp)
                
                return {CO2_SENSOR: co2, TEMP_SENSOR: temp, HUM_SENSOR: humidity}
            else:
                print("Data not ready yet. Waiting for data...")
                return None
        except Exception as e:
            print(f"Error reading measurement: {e}")
            return None

    def celsius_to_fahrenheit(self, celsius):
        """Convert temperature from Celsius to Fahrenheit."""
        return (celsius * 9 / 5) + 32

# Example usage:
if __name__ == "__main__":
    scd40 = SCD40(fahrenheit=False)  # Set to True for Fahrenheit
    scd40.init()  # Initialize the sensor

    try:
        while True:
            data = scd40.read_measurement()
            if data:
                print(f"CO2 Level: {data[CO2_SENSOR]} ppm")
                print(f"Temperature: {data[TEMP_SENSOR]} °C")
                print(f"Humidity: {data[HUM_SENSOR]} %")
            time.sleep(2)  # Delay for 2 seconds between readings
    except KeyboardInterrupt:
        print("Program interrupted. Stopping sensor.")
        scd40.stop_measurements()  # Stop the measurements on exit
