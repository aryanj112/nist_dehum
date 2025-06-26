"""
pilectric.py - Interfaces with Peacefair PZEM-004T V3.0 wattmeters.

SEE THIS LINK:  https://innovatorsguru.com/pzem-004t-v3/

Dependencies (from pip): modbus-tk, pyserial, trio
Dependents: supervisor.py
Version: 1.0.0
"""

import struct
from typing import List

import trio


def requirements() -> List[str]:
    return ["modbus-tk", "pyserial"]


def process_data(data):
    """Take the raw data from the wattmeter and converts into standard units."""

    processed_data = (
        data[0] / 10,
        (data[1] + (data[2] << 16)) / 1_000,
        (data[3] + (data[4] << 16)) / 10,
        data[5] + (data[6] << 16),
        data[7] / 10,
        data[8] / 100,
        0 if data[9] == 0 else 1
    )
    return processed_data


async def main(elec_queue=None,
               interface="/dev/ttyS0",
               threshold=50_000,
               reset=False):
    """The main function of the program."""
    import modbus_tk.defines as flags
    from modbus_tk import modbus_rtu
    from serial import Serial

    # Instantiating serial and modbus interfaces.
    serial_int = Serial(
        port=interface,
        baudrate=9_600,
        bytesize=8,
        parity="N",
        stopbits=1,
        xonxoff=False,
        write_timeout=2)
    wattmeter = modbus_rtu.RtuMaster(serial_int)
    wattmeter.set_timeout(2.0)

    # Set the alarm threshold.
    wattmeter.execute(1, flags.WRITE_SINGLE_REGISTER, 1, output_value=threshold)

    # Resets the energy counter.
    if reset:
        pdu = struct.pack(">B", 0x42)
        query = wattmeter._make_query()
        request = query.build_request(pdu, 1)
        wattmeter._send(request)

    # Read input from wattmeter and process it.
    raw_data = wattmeter.execute(1, flags.READ_INPUT_REGISTERS, 0, 10)
    clean_data = process_data(raw_data)

    output = {"Voltage": clean_data[0],
              "Current": clean_data[1],
              "Power": clean_data[2],
              "Energy": clean_data[3],
              "Frequency": clean_data[4],
              "Power_Factor": clean_data[5],
              "Threshold": threshold,
              "Alarm_Status": clean_data[6]}

    # Output to the queue or print if not available.
    if elec_queue is not None:
        elec_queue.put(output)
    else:
        print(output)

    wattmeter.close()


if __name__ == "__main__":
    trio.run(main)

