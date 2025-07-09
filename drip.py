import RPi.GPIO as GPIO
from hx711 import HX711
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_si7021
import modbus_tk.defines as flags
from modbus_tk import modbus_rtu
from serial import Serial
import time
import csv
from datetime import datetime
from cedargrove_nau7802 import NAU7802
import board


class DRIP:
    def __init__(self, drip_id, si7021_i2c_bus, pzem_interface_path = "/dev/ttyS0", hx711_pins = (3, 2), hx711_readings = 45, hx711_offset = -4143700, hx711_ratio = 105.521408839779, nau7802_offset = "-309977", nau7802_ratio = "0.0039372056834247006", nau7802_readings = 15, nau7802_i2c_bus = "1", file_export = 'data.csv'):
        self.drip_id = drip_id
        self.si7021_i2c_bus = si7021_i2c_bus
        self.pzem_interface_path = pzem_interface_path
        self.hx711_out = hx711_pins[0]
        self.hx711_sck = hx711_pins[1]
        self.hx711_readings = hx711_readings
        self.hx711_offset = hx711_offset
        self.hx711_ratio = hx711_ratio
        self.nau7802_offset = nau7802_offset
        self.nau7802_ratio = nau7802_ratio
        self.nau7802_readings = nau7802_readings
        self.nau7802_i2c_bus = nau7802_i2c_bus
        self.file_export = file_export
        
        # Sensor object initializations
        self.hx711_sensor = None
        self.nau7802_sensor = None
        self.si7021_sensor = None
        self.pzem_sensor = None

        print("Welcome!")
        print("Your D.R.I.P (Dehumidifier Response & Integration Package) unit is initialized")
        print(" - DRIP ID:", self.drip_id)
        print(" - Si7021 I2C bus number:", self.si7021_i2c_bus)
        print(" - PZEM-004T interface path:", self.pzem_interface_path)
        # print(f" - HX711 data pin: {self.hx711_out}, HX711 sck pin: {self.hx711_sck}\n")
        print(f" - NAU7802 I2C: {self.nau7802_i2c_bus} \n")
        print("-------- starting sensor initialization and resets -------- \n")
        # self.init_hx711()
        self.init_nau7802()
        self.init_si7021()
        self.init_pzem()
        print("---- all sensors have been initialized and all sensor objects have been created ---- \n")
       
        print("-------- running preliminary test on all sensors --------") 
        # print("--- hx711 ---")
        # self.run_hx711(print_out = True)
        print("--- nau7802 ---")
        self.run_nau7802(print_out = True)
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
            err = self.hx711_sensor.reset()
        print('Ready to use')

        self.hx711_sensor.set_gain_A(gain=64)
        self.hx711_sensor.select_channel(channel='A')
        self.hx711_sensor.set_offset(offset=self.hx711_offset, channel='A', gain_A=64)
        self.hx711_sensor.set_scale_ratio(self.hx711_ratio)

        print(" - HX711 sensor has been initialized with OFFSETTT and RATIO")

    def init_nau7802(self):
        print("--- Initializing NAU7802 ---")
        # Instantiate 24-bit load sensor ADC; two channels, default gain of 128
        self.nau7802_sensor = NAU7802(board.I2C(), address=0x2A, active_channels=2)
        enabled = self.nau7802_sensor.enable(True)
        self.nau7802_sensor.channel = 1
        print(" - NAU7802 sensor has been initialized ")

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
        print(" - PZEM-004T sensor has been initialized")

    def run_nau7802(self, print_out = False):
        
        sample_sum = 0
        for _ in range(self.nau7802_readings):
            while not self.nau7802_sensor.available():
                pass
            sample_sum += self.nau7802_sensor.read()
        raw = int(sample_sum / self.nau7802_readings)

        grams = (raw - self.nau7802_offset) * self.nau7802_ratio

        output = {"Grams": grams}

        if print_out:
            print(f"\nGrams: {grams:.2f} g", end = "")
        return output

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
        i = 1
        records = []
        fields = ['Time', 'Grams', 'Temperature', 'Humidity', 'Voltage', 'Current', 'Power', 'Energy', 'Frequency', 'Power_Factor', 'Threshold', 'Alarm_Status']

        try:
            while i < (iterations + 1) or infinite:
                start_time = time.time()
                print(f"\n--- Iteration {iteration} ---")
                row = {'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                # row.update(self.run_hx711(print_out = True))
                row.update(self.run_nau7802(print_out = True))
                row.update(self.run_si7021(print_out = True))
                row.update(self.run_pzem(print_out = True))
                records.append(row)
                end_time = time.time()
                print("\nTime elapsed: ", end_time-start_time)
                time.sleep(sleep)
                iteration += 1
                if not infinite:
                    i += 1
        except KeyboardInterrupt:
            print("\n--- KeyboardInterrupt detected. Exiting gracefully ---")
        finally:
            print(f"\n----- Successfully ran {iteration - 1} iterations -----")
            with open(self.file_export, 'w', newline = '') as f:
                writer = csv.DictWriter(f, fieldnames = fields)
                writer.writeheader()
                for record in records:
                    writer.writerow(record)

            print(f'--- exported data to {self.file_export}')
            if infinite:
                self.close_sensors()
            return records   

    def close_sensors(self):
        self.pzem_sensor.close()
        GPIO.cleanup()
        print("\n----- Closed sensors -----")

if __name__ == '__main__':
    DRIP_CONFIG = {
        'drip_id': 2,
        'si7021_i2c_bus': 10,
        'pzem_interface_path': '/dev/ttyS0',
        'hx711_pins': (3, 2),
        'hx711_readings':5,
        'hx711_offset': -4143700,
        'hx711_ratio': 105.521408839779,
        'nau7802_offset': -309977,
        'nau7802_ratio': 0.0039372056834247006, 
        'nau7802_readings': 15,
        'nau7802_i2c_bus': 1,
        'file_export': "data_test.csv"
    }

    drip = DRIP(**DRIP_CONFIG)
    drip.run_all(iterations=50, infinite=True, sleep=0)
