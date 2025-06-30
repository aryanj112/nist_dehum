# DRIP: Dehumidifier Response & Integration Package

## Overview
This project is part of a NIST research initiative to log the efficiency and operational metrics of portable dehumidifiers. It uses a Raspberry Pi (tested on Pi Zero, but compatible with all models) to interface with multiple sensors and log data for further analysis.

## Features
- Logs weight (HX711), temperature/humidity (Si7021), and power metrics (PZEM-004T)
- Outputs data to a CSV file for easy analysis
- Modular Python library (`drip.py`) for integration into your own scripts

## Hardware Setup
### Sensor Pinouts (Sensor -> Pi GPIO)
- **HX711**
  - VIN  -> 5V
  - GND  -> GND
  - SCK  -> GPIO2 (default, configurable)
  - DATA -> GPIO3 (default, configurable)
- **Si7021**
  - VIN  -> 3.3V
  - GND  -> GND
  - SDA  -> GPIO17 (default, configurable)
  - SCL  -> GPIO27 (default, configurable)
- **PZEM-004T**
  - 5V   -> 5V
  - GND  -> GND
  - RX   -> TX GPIO14 (default, configurable)
  - TX   -> RX GPIO15 (default, configurable)

> **Note:** You can change the pin mappings in your script by passing different values to the `DRIP` class. See the example below.

## Software Setup
1. **Clone the repository**
2. **Install dependencies** (using [uv](https://github.com/astral-sh/uv)):
   ```sh
   uv pip install -r requirements.txt
   ```
3. **Connect your sensors as described above.**

### Alternative: Install with pip and virtual environment

If you're not using `uv`, you can also install dependencies manually with `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This creates and activates a virtual environment in `.venv/` and installs the required packages.

To exit the virtual environment later:

```bash
deactivate
```

### SFTP Setup (for remote development)
To transfer files between your local machine and the Raspberry Pi, you can use the SFTP extension in VS Code:
- Install the [SFTP extension](https://marketplace.visualstudio.com/items?itemName=liximomo.sftp) from the Extensions Marketplace.
- Open the Command Palette (`CMD + SHIFT + P`), then search for and select `SFTP: Download Project` to download the entire project to your local machine.
- To upload files, just save them in the editor.
- To upload the entire project, use `SFTP: Upload Project` from the Command Palette.

## Usage
`drip.py` is a library. To log data, create a script (e.g., `drip_test.py`) like this:

```python
from drip import DRIP

DRIP_CONFIG = {
    'drip_id': 2,
    'si7021_i2c_bus': 10,  # Change if your I2C bus is different
    'pzem_interface_path': '/dev/ttyS0',
    'hx711_pins': (3, 2),  # (DATA, SCK) pins
    'hx711_readings': 45,
    'hx711_offset': -4143700,
    'hx711_ratio': 105.521408839779,
    'file_export': 'data_test.csv'
}

drip = DRIP(**DRIP_CONFIG)
drip.run_all(iterations=50, infinite=True, sleep=0)
drip.close_sensors()
```

- **Change pin numbers** in `DRIP_CONFIG` as needed for your setup.
- The main output is a CSV file (default: `data_test.csv`).

## Main Functions in `drip.py`
- `DRIP.__init__(...)`: Initializes the DRIP object and all sensors. You can configure pins and output file here.
- `run_all(iterations=50, infinite=False, sleep=2)`: Runs all sensors, logs data for a set number of iterations (or infinitely), and writes to CSV.
- `run_hx711(print_out=False)`: Reads and returns weight from the HX711 sensor.
- `run_si7021(print_out=False)`: Reads and returns temperature and humidity from the Si7021 sensor.
- `run_pzem(print_out=False)`: Reads and returns power metrics from the PZEM-004T sensor.
- `close_sensors()`: Safely closes all sensor connections and cleans up GPIO.

You can use these methods directly in your own scripts for custom workflows.

## Customization
- You can use any method from the `DRIP` class in your own scripts.
- The CSV output can be processed or visualized as needed.

## Requirements
- Raspberry Pi (any model)
- Python 3.7+
- All dependencies listed in `requirements.txt` (install with `uv`)

## Troubleshooting
- No common issues reported. If you encounter problems, check your wiring and ensure all dependencies are installed.

## Manually Syncing Files to the Raspberry Pi

If the SFTP extension does not fully remove outdated files on the Raspberry Pi, you can use `rsync` from your terminal for a full sync:

```bash
rsync -avz --delete ./ pi@<raspberry_pi_ip>:/home/pi/dehum/
```

- Replace `<raspberry_pi_ip>` with the actual IP address of your Raspberry Pi.
- This command ensures your Pi's `dehum` folder exactly mirrors your local folder.
- The `--delete` flag removes any files from the Pi that no longer exist locally.

This method is recommended for precise syncing in development or deployment setups.

## Syncing Files from the Raspberry Pi to Your Local Machine

To fully copy your entire project (including generated data and updated code) from the Raspberry Pi to your local computer, run the following from your local terminal:

```bash
rsync -avz pi@<raspberry_pi_ip>:/home/pi/dehum/ ./dehum_local/
```

- Replace `<raspberry_pi_ip>` with your Raspberry Pi’s IP address.
- This command will download the Pi’s `/home/pi/dehum` folder into a local directory called `dehum_local`.

If you want to ensure your local folder exactly matches what’s on the Pi (deleting extra local files):

```bash
rsync -avz --delete pi@<raspberry_pi_ip>:/home/pi/dehum/ ./dehum_local/
```

---

## License
This project is for research use under the NIST initiative.
