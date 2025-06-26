import RPi.GPIO as GPIO
from hx711 import HX711

try:
    GPIO.setmode(GPIO.BCM) 
    hx = HX711(dout_pin=3, pd_sck_pin=2, gain_channel_A=64, select_channel='A')

    err = hx.reset()
    if err:
        print('not ready')
    else:
        print('Ready to use')

    hx.set_gain_A(gain=64)
    hx.select_channel(channel='A')
    hx.set_offset(offset=-4143700, channel='A', gain_A=64)
    hx.set_scale_ratio(105.521408839779)

    data = hx.get_data_mean(readings=45)
   
    if data:
        print('Current weight on the scale in grams is: ')
        print(hx.get_weight_mean(45), 'g')    
    else:
        print('invalid data')

    #hx.power_down()
    #hx.power_up()          
    #hx.reset()
   
    print('\nThat is all. Cleaning up.')
except (KeyboardInterrupt, SystemExit):
    print('Bye :)')

finally:
    GPIO.cleanup()