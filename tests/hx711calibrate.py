#!/usr/bin/env python3
import RPi.GPIO as GPIO
from hx711 import HX711

try:
    GPIO.setmode(GPIO.BCM) 
    hx = HX711(
        dout_pin=3, pd_sck_pin=2, gain_channel_A=64, select_channel='A')

    err = hx.reset()
    if err:
        print('not ready')
    else:
        print('Ready to use')

    hx.set_gain_A(gain=64)
    hx.select_channel(channel='A')

    data = hx.get_raw_data_mean(readings=30)

    if data:
        print('Raw data:', data)
    else:
        print('invalid data')

    result = hx.zero(readings=45)

    data = hx.get_data_mean(readings=45)

    if data:
        print('Data subtracted by offset but still not converted to any unit:', data)
    else:
        print('invalid data')

    input('Put known weight on the scale and then press Enter')
    data = hx.get_data_mean(readings=30)
    if data:
        print('Mean value from HX711 subtracted by offset:', data)
        known_weight_grams = input('Write how many grams it was and press Enter: ')
        try:
            value = float(known_weight_grams)
            print(value, 'grams')
        except ValueError:
            print('Expected integer or float and I have got:',known_weight_grams)

        ratio = data / value 
        hx.set_scale_ratio(ratio)
        print('Ratio is set.')
    else:
        raise ValueError('Cannot calculate mean value. Try debug mode.')

    print('Current weight on the scale in grams is: ')
    print(hx.get_weight_mean(45), 'g')

    offset = hx.get_current_offset(channel='A', gain_A=64)
    print('Current offset for channel A and gain 64:', offset)
    
    current_ratio = hx.get_current_scale_ratio()
    print('Current scale ratio is set to:', current_ratio)


    hx.set_offset(offset=-4143700, channel='A', gain_A=64)
    # hx.set_scale_ratio(scale_ratio = 15.350072761402876, channel='A', gain_A=64)

    # 5 + long hook
        # offset = -4143660
        # ratio = 15.350072761402876
    
    # solder + long hook 
        # offset = -4145949
        # ratio = 115.61125769569041

        # offset = -4143664
        # ratio = 105.52330694810905

    # solder + long hook + c hook
        # offset = -4143685
        # ratio = 105.4996214988645
    
    # bag + c hook
        # offset = -4143670
        # ratio = 105.50223546944858

    # bag + c hook + cyl
        # offset = -4143700
        # ratio = 105.521408839779

    #hx.power_down()
    #hx.power_up()          
    #hx.reset()
   
    print('\nThat is all. Cleaning up.')
except (KeyboardInterrupt, SystemExit):
    print('Bye :)')

finally:
    GPIO.cleanup()