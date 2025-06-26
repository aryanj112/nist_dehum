# Reading PZEM-004t power sensor (new version v3.0) through Modbus-RTU protocol over TTL UART
# Run in python3

# To install library for PZEM:
# pip3 install modbus-tk
# pip3 install pyserial
# YouTube Video: https://www.youtube.com/watch?v=17xbPl7KpGo
#

import time

#library for PZEM-004T V3
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu



# Connect to the slave
serial = serial.Serial(
                       port='/dev/ttyS0',
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       xonxoff=0
                      )

master = modbus_rtu.RtuMaster(serial)
master.set_timeout(2.0)
master.set_verbose(True)
print("")
print("     CTRL-Z to STOP")
print("")
while True:
	data = master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)
	voltage = data[0] / 10.0 # [V]
	current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
	power = (data[3] + (data[4] << 16)) / 10.0 # [W]
	energy = data[5] + (data[6] << 16) # [Wh]
	frequency = data[7] / 10.0 # [Hz]
	powerFactor = data[8] / 100.0
	alarm = data[9] # 0 = no alarm

	print('Voltage [V]\t: ', voltage)
	print('Current [A]\t: ', current)
	print('Power [W]\t: ', power) # active power (V * I * power factor)
	print('Energy [Wh]\t: ', energy)
	print('Frequency [Hz]\t: ', frequency)
	print('Power factor []\t: ', powerFactor)
	#print('Alarm : ', alarm)
	print("--------------------")
	time.sleep(1)

# Changing power alarm value to 100 W
# master.execute(1, cst.WRITE_SINGLE_REGISTER, 1, output_value=100)

#try:
    #master.close()
    #if slave.is_open:
        #slave.close()
#except:
   # pass
