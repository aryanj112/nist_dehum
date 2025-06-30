from adafruit_extended_bus import ExtendedI2C as I2C
#from si7021 import Si7021
import time

import adafruit_si7021

sensor = adafruit_si7021.SI7021(I2C(10))


#i2c = I2C(10)  # This opens /dev/i2c-10
#sensor = Si7021(i2c)

while True:
        print("\nTemperature: %0.1f C" % sensor.temperature)
        print("Humidity: %0.1f %%" % sensor.relative_humidity)
        time.sleep(2)
