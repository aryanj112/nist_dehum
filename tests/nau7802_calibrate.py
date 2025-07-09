# SPDX-FileCopyrightText: 2023 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
nau7802_simpletest.py  2023-01-13 2.0.2  Cedar Grove Maker Studios

Instantiates two NAU7802 channels with default gain of 128 and sample
average count of 2.
"""

import time

import board

from cedargrove_nau7802 import NAU7802

# Instantiate 24-bit load sensor ADC; two channels, default gain of 128
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=2)


def zero_channel():
    """Initiate internal calibration for current channel.Use when scale is started,
    a new channel is selected, or to adjust for measurement drift. Remove weight
    and tare from load cell before executing."""
    print(
        "channel {0:1d} calibrate.INTERNAL: {1:5s}".format(
            nau7802.channel, str(nau7802.calibrate("INTERNAL"))
        )
    )
    print(
        "channel {0:1d} calibrate.OFFSET:   {1:5s}".format(
            nau7802.channel, str(nau7802.calibrate("OFFSET"))
        )
    )
    print(f"...channel {nau7802.channel:1d} zeroed")


def read_raw_value(samples=5):
    """Read and average consecutive raw sample values. Return average raw value."""
    sample_sum = 0
    sample_count = samples
    while sample_count > 0:
        while not nau7802.available():
            pass
        sample_sum = sample_sum + nau7802.read()
        sample_count -= 1
    return int(sample_sum / samples)


# Instantiate and calibrate load cell inputs
print("*** Instantiate and calibrate load cells")
# Enable NAU7802 digital and analog power
enabled = nau7802.enable(True)
print("Digital and analog power enabled:", enabled)

print("REMOVE WEIGHTS FROM LOAD CELLS")
time.sleep(3)

nau7802.channel = 1
zero_channel()  # Calibrate and zero channel
nau7802.channel = 2
zero_channel()  # Calibrate and zero channel

# Calibrate for grams
print("\n--- Calibration Step ---")
input("Make sure the scale is EMPTY and press Enter to tare...")

# Tare (zero)
nau7802.channel = 1
zero_channel()
zero_raw = read_raw_value()
print(f"Tare complete. Zero raw value: {zero_raw}")

input("Now place a known weight on the scale and press Enter...")

known_weight_grams = float(input("Enter the weight you placed (in grams): "))
known_raw = read_raw_value()
print(f"Raw value with known weight: {known_raw}")

scale_factor = known_weight_grams / (known_raw - zero_raw)
print(f"Calculated scale factor: {scale_factor} grams per raw unit")
print("--- Calibration Complete ---\n")

print(f"Offset (zero_raw): {zero_raw}")
print("READY")
print(f"Scale factor: {scale_factor} grams per raw unit")

### Main loop: Read load cells and display weight in grams
while True:
    print("=====")
    nau7802.channel = 1
    raw = read_raw_value()
    grams = (raw - zero_raw) * scale_factor
    print(f"channel {nau7802.channel:1.0f} weight: {grams:.2f} g")