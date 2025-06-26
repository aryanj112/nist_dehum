import RPi.GPIO as GPIO
from hx711 import HX711
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_si7021
import modbus_tk.defines as flags
from modbus_tk import modbus_rtu
from serial import Serial
import RPi.GPIO as GPIO
from hx711 import HX711
import time

class DRIP:
    def __init__(self, drip_id, si7021_i2c_bus, pzem_interface_path = "/dev/ttyS0", hx711_pins = (3, 2), hx711_readings = 45, hx711_offset = -4143700, hx711_ratio = 105.521408839779):
        self.drip_id = drip_id
        self.si7021_i2c_bus = si7021_i2c_bus
        self.pzem_interface_path = pzem_interface_path
        self.hx711_out = hx711_pins[0]
        self.hx711_sck = hx711_pins[1]
        self.hx711_readings = hx711_readings
        self.hx711_offset = hx711_offset
        self.hx711_ratio = hx711_ratio
        
        # Sensor object initializations
        self.hx711_sensor = None
        self.si7021_sensor = None
        self.pzem_sensor = None

        print("Welcome!")
        print("Your D.R.I.P (Dehumidifier Response & Integration Package) unit is initialized")
        print(" - DRIP ID:", self.drip_id)
        print(" - Si7021 I2C bus number:", self.si7021_i2c_bus)
        print(" - PZEM-004T interface path:", self.pzem_interface_path)
        print(f" - HX711 data pin: {self.hx711_out}, HX711 sck pin: {self.hx711_sck}\n")
        print("-------- starting sensor initialization and resets -------- \n")
        self.init_hx711()
        self.init_si7021()
        self.init_pzem()
        print("---- all sensors have been initialized and all sensor objects have been created ---- \n")
       
        print("-------- running preliminary test on all sensors --------") 
        print("--- hx711 ---")
        self.run_hx711(print_out = True)
        print("\n\n--- si702 ---")
        self.run_si7021(print_out = True)
        print("\n--- pzem ---\n")
        self.run_pzem(print_out = True)
        print("\n---- all sensors have passed their initial test ---- \n")

    def init_hx711(self):
        print("--- Initializing HX711 ---")
        GPIO.setmode(GPIO.BCM) 
        self.hx711_sensor = HX711(dout_pin=self.hx711_out, pd_sck_pin=self.hx711_sck, gain_channel_A=64, select_channel='A')

        err = self.hx711_sensor.reset()
        while err:
            print('not ready')
            time.sleep(1)
        print('Ready to use')

        self.hx711_sensor.set_gain_A(gain=64)
        self.hx711_sensor.select_channel(channel='A')
        self.hx711_sensor.set_offset(offset=self.hx711_offset, channel='A', gain_A=64)
        self.hx711_sensor.set_scale_ratio(self.hx711_ratio)

        print(" - HX711 sensor has been initialized with OFFSETTT and RATIO")


    def init_si7021(self):
        print("--- Initializing Si7021 ---")
        self.si7021_sensor = adafruit_si7021.SI7021(I2C(self.si7021_i2c_bus))
        print(" - Si7021 sensor has been initialized with I2C bus", self.si7021_i2c_bus)

    def init_pzem(self, threshold = 50000):
        print("--- Initializing PZEM-004T ---")
        serial_int = Serial(
            port=self.pzem_interface_path,
            baudrate=9_600,
            bytesize=8,
            parity="N",
            stopbits=1,
            xonxoff=False,
            write_timeout=2
        )
        self.pzem_sensor = modbus_rtu.RtuMaster(serial_int)
        self.pzem_sensor.set_timeout(2.0)
        self.pzem_sensor.execute(1, flags.WRITE_SINGLE_REGISTER, 1, output_value=threshold)

    def run_hx711(self, print_out = False):
        data = self.hx711_sensor.get_weight_mean(self.hx711_readings)
        
        output = {"Grams": data}

        if print_out:
            print("\nGrams: %0.2f g" % data, end = "")
        return output
    
    def run_si7021(self, print_out = False,):

        output = {
            "Temperature": self.si7021_sensor.temperature,
            "Humidity": self.si7021_sensor.relative_humidity
        }
        
        if print_out:
            print("\nTemperature: %0.1f C" % self.si7021_sensor.temperature)
            print("Humidity: %0.1f %%" % self.si7021_sensor.relative_humidity)
        
        return output

    def run_pzem(self, print_out = False, threshold=50_000):

        raw_data = self.pzem_sensor.execute(1, flags.READ_INPUT_REGISTERS, 0, 10)

        clean_data = (
            raw_data[0] / 10,
            (raw_data[1] + (raw_data[2] << 16)) / 1_000,
            (raw_data[3] + (raw_data[4] << 16)) / 10,
            raw_data[5] + (raw_data[6] << 16),
            raw_data[7] / 10,
            raw_data[8] / 100,
            0 if raw_data[9] == 0 else 1
        )
        output = {
            "Voltage": clean_data[0],
            "Current": clean_data[1],
            "Power": clean_data[2],
            "Energy": clean_data[3],
            "Frequency": clean_data[4],
            "Power_Factor": clean_data[5],
            "Threshold": threshold,
            "Alarm_Status": clean_data[6]
        }

        if print_out:
            print("Voltage: %.1f V" % clean_data[0])
            print("Current: %.3f A" % clean_data[1])
            print("Power: %.1f W" % clean_data[2])
            print("Energy: %d Wh" % clean_data[3])
            print("Frequency: %.1f Hz" % clean_data[4])
            print("Power Factor: %.2f" % clean_data[5])
            print("Threshold: %d" % threshold)
            print("Alarm Status:", "ON" if clean_data[6] else "OFF")

        return output

    def run_all(self, iterations = 50, infinite = False, sleep = 2):
        iteration = 1
        if infinite:
            while infinite:
                start_time = time.time()
                print(f"\n--- Iteration {iteration} ---")
                self.run_hx711(print_out = True)
                self.run_si7021(print_out = True)
                self.run_pzem(print_out = True)
                end_time = time.time()
                print("\nTime elapsed: ", end_time-start_time)
                time.sleep(sleep)
                iteration += 1
        else:
            for i in range(1, iterations + 1, 1):
                start_time = time.time()
                print(f"\n--- Iteration {i} ---")
                self.run_hx711(print_out = True)
                self.run_si7021(print_out = True)
                self.run_pzem(print_out = True)
                end_time = time.time()
                print(f"\nTime elapsed: {end_time-start_time:.2f}")
                time.sleep(sleep)
                iteration = i

        output = f"\n----- Successfully ran {iteration} iterations -----"
        print(output)

        return output

    def close_sensors(self):
        self.pzem_sensor.close()
        self.hx711_sensor.GPIO.cleanup()
        print("\n----- closed all sensors -----")