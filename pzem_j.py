import time

#library for PZEM-004T V3
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

# Connect to the slave
serial = serial.Serial(
                       port='/dev/serial0',
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       xonxoff=0
                      )

master = modbus_rtu.RtuMaster(serial)
master.set_timeout(2.0)
master.set_verbose(True)

while True:
	data = master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)
	voltage = data[0] / 10.0 # [V]
	# current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
	power = (data[3] + (data[4] << 16)) / 10.0 # [W]
	energy = data[5] + (data[6] << 16) # [Wh]
	frequency = data[7] / 10.0 # [Hz]
	powerFactor = data[8] / 100.0
	alarm = data[9] # 0 = no alarm

	print('Voltage [V]\t: ', voltage)
	# print('Current [A]\t: ', current)
	print('Power [W]\t: ', power) # active power (V * I * power factor)
	print('Energy [Wh]\t: ', energy)
	print('Frequency [Hz]\t: ', frequency)
	print('Power factor []\t: ', powerFactor)
	#print('Alarm : ', alarm)
	print("--------------------")
	time.sleep(1)
