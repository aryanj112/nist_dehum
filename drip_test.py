from drip import DRIP

# Initialize DRIP object with configuration parameters
DRIP_CONFIG = {
    'drip_id': 2,
    'si7021_i2c_bus': 10,
    'pzem_interface_path': '/dev/ttyS0',
    'hx711_pins': (3, 2),
    'hx711_readings': 45,
    'hx711_offset': -4143700,
    'hx711_ratio': 105.521408839779
}

drip = DRIP(**DRIP_CONFIG)

drip.run_all(iterations=2, infinite=False, sleep=0)
drip.close_sensors()