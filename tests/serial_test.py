"""
serial_text.py - A simple script to verify UART is working as expected.
Requires GPIO 14 % 15 to be bridged together with a resistor (560 ohms to 680 ohms).
Originally found at https://di-marco.net/blog/it/2020-06-06-raspberry_pi_3_4_and_0_w_serial_port_usage
"""

import serial

test_string = "Test serial port ...".encode('utf-8')
port_list = ["/dev/ttyAMA0", "/dev/ttyS0"]

for port in port_list:
    try:
        serial_port = serial.Serial(
            port = port,
            baudrate = 9600,
            timeout = 2,
            write_timeout = 2
        )
        print("Serial port", port, "ready for test:")
        bytes_sent = serial_port.write(test_string)
        print("Sent", bytes_sent, " byte")
        loopback = serial_port.read(bytes_sent)
        if loopback == test_string:
            print("Received ", len(loopback), "bytes.  Port", port, "is okay!\n")
        else:
            print("Received incorrect data:", loopback, "on serial port", port, "loopback\n")
        serial_port.close()

    except IOError:
        print("Error on", port, "\n")