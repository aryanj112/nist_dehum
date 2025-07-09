import time
import board
from cedargrove_nau7802 import NAU7802
import csv
import os

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

try:
    nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=1)
    nau7802.calibrate("INTERNAL")
    nau7802.channel = 1

    print("*** Instantiate and calibrate load cells")
    print("Digital and analog power enabled:", nau7802.enable(True))

    print("\n--- Calibration Step ---")
    print("REMOVE WEIGHTS FROM LOAD CELLS")
    input("Make sure the scale is EMPTY and press Enter to tare...")

    zero_raw = read_raw_value()
    print(f"Tare complete. Zero raw value: {zero_raw}")

    input("Now place a known weight on the scale and press Enter...")
    known_weight_grams = float(input("Enter the weight you placed (in grams): "))
    known_raw = read_raw_value()
    print(f"Raw value with known weight: {known_raw}")

    scale_factor = known_weight_grams / (known_raw - zero_raw)
    print(f"Calculated scale factor: {scale_factor} grams per raw unit")
    print(f"Offset (zero_raw): {zero_raw}")

    print("--- Calibration Complete ---\n")

    print("READY")

    for i in range(5):
        print("=====")
        nau7802.channel = 1
        raw = read_raw_value()
        grams = (raw - zero_raw) * scale_factor
        print(f"channel {nau7802.channel:1.0f} weight: {grams:.2f} g")

except KeyboardInterrupt:
            print("\n--- KeyboardInterrupt detected. Exiting gracefully ---")
finally:
    try:
        fields = ['Weight', 'Offset', 'Ratio']
        record = {
            'Weight': known_weight_grams,
            'Offset': zero_raw,
            'Ratio': scale_factor
        }

        file_path = "nau_calibrate.csv"
        write_header = not os.path.exists(file_path) or os.stat(file_path).st_size == 0

        # with open("nau_calibrate.csv", 'w', newline='') as f:
        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if write_header:
                writer.writeheader()
            writer.writerow(record)
            
        print("\n Saved calibration to nau_calibrate.csv")
    except Exception as e:
        print(f"Failed to write calibration file: {e}")
