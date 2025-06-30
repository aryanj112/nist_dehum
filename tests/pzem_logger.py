"""
pilectric_cli.py - A Python script to read the signals from a Peacefair PZEM-004T V3.0 wattmeter
Version: 0.98.0
Requires: python3-serial (sudo apt install python3-serial)
Requires: modbus-tk      (pip3 install modbus-tk)
"""

import argparse
from datetime import datetime
import os
from pathlib import Path
import time

import modbus_tk.defines as flags
from modbus_tk import modbus_rtu
import modbus_tk.exceptions as error
import serial

"""Set up the optional arguments to customize the functions of the script"""
parser = argparse.ArgumentParser(description = "Reads from a PZEM-004T sensor and displays the results.")

parser.add_argument(
    "-p", "--port",
    help    = "Sets the port used, defaults to /dev/ttyS0",
    dest    = "port",
    action  = "store",
    type    = str,
    default = "/dev/ttyS0"
    )
parser.add_argument(
    "-nl", "--nolog", 
    help   = "Disables logging to a file",
    dest   = "logging",
    action = "store_false"
    )
parser.add_argument(
    "-i", "--interval",
    help    = "Sets the reading interval in seconds, defaults to 1 second",
    dest    = "interval",
    action  = "store",
    type    = float,
    default = 1
    )
parser.add_argument(
    "-a", "--alarm",
    help    = "Sets the alarm threshold in watts, defaults to 50000",
    dest    = "alarm",
    action  = "store",
    type    = int,
    default = 50000
    )

args = parser.parse_args()


class SerialConnection:
    """SerialConnection: Establishes a serial connection and opens a Modbus interface."""

    def __init__(self, interface = "/dev/ttyS0", timeout = 2.0):
        self.serial = serial.Serial(
            port          = interface,
            baudrate      = 9600,
            bytesize      = 8,
            parity        = "N",
            stopbits      = 1,
            xonxoff       = False,
            write_timeout = 2
        )
        self.modbus = modbus_rtu.RtuMaster(self.serial)
        self.modbus.set_timeout(timeout)

    def readRegisters(self):
        """"Read the electrical data from the sensor"""
        
        buffer = self.modbus.execute(1, flags.READ_INPUT_REGISTERS, 0, 10)
        return buffer

    def setAlarm(self, threshold):
        """Set the threshold (in watts) for the alarm to trip (max of 50000)"""
        
        self.modbus.execute(1, flags.WRITE_SINGLE_REGISTER, 1, output_value=threshold)

    def close(self):
        """Cleanly closes the Modbus and serial connections."""
        
        self.modbus.close()

class Logger:
    """Takes a set of data and outputs it to either the terminal or a log file."""
    
    def __init__(self):
        if args.logging == True:
            self.script_path = Path(".")
            self.date = str(datetime.now()).replace(' ', '_')
            self.log_path = self.script_path.cwd() / "logs"
            self.log_name = f"{self.log_path}/{self.date}_{args.port[5:]}.csv"
            if os.path.exists(self.log_path) == False:
                print(f"Creating {self.log_path}")
                os.makedirs(self.log_path)
            print(f"Logging to {self.log_name}")
            self.log_file = open(self.log_name, "a")
            self.log_file.write(f"Timestamp,Voltage,Current,Power,Energy,Frequency,Power Factor,Threshold,Alarm Status\n")

    def processData(self, data):
        """Takes the data from the sensor and processes it to standard units."""
        
        self.processed_data = (
        data[0] / 10,
        (data[1] + (data[2] << 16)) / 1000,
        (data[3] + (data[4] << 16)) / 10,
        data[5] + (data[6] << 16),
        data[7] / 10,
        data[8] / 100,
        0 if data[9] == 0 else 1
        )
        print(self.processed_data)
        
    def consoleLog(self):
        """Prints the processed data to the console."""

        buffer = self.processed_data
        output = (
        f"Voltage:      {buffer[0]: >6.1f}V\n"
        f"Current:      {buffer[1]: >6.1f}A\n"
        f"Power:        {buffer[2]: >6.1f}W\n"
        f"Energy:       {buffer[3]: >6.1f}Wh\n"
        f"Frequency:    {buffer[4]: >6.1f}Hz\n"
        f"Power Factor: {buffer[5]: >6}\n\n"
        f"Threshold:    {args.alarm:,}V\n"
        f"Alarm Status: {'Off' if buffer[6] == 0 else 'Active'}\n\n"
        f"Press \"Ctrl + C\" to exit."
        )
        print(output)

    def fileLog(self):
        """Prints the processed data to the log file (if enabled)."""

        buffer = self.processed_data
        self.log_file.write(f"{datetime.now()},{buffer[0]},{buffer[1]},{buffer[2]},{buffer[3]},{buffer[4]},{buffer[5]},{args.alarm},{buffer[6]}\n")

    def closeLog(self):
        """Closes the log file."""
        
        self.log_file.close()

def main():
    """The main loop of the program."""
    
    sensor = SerialConnection(interface = args.port)
    print("Estalished connection on " + sensor.serial.port)
    sensor.setAlarm(args.alarm)
    log = Logger()
    time.sleep(3)
    
    try:
        while True:
            data = sensor.readRegisters()
            log.processData(data)
            print("\033[2J\033[;H", end = "")
            log.consoleLog()
            if args.logging == True:
                log.fileLog()

            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print("Exiting script")
   
    finally:
        sensor.close()
        if args.logging == True:
            log.closeLog()

if __name__ == "__main__":
    main()
