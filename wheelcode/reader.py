import time
from machine import ADC


adc = ADC(0)

def get_adc_value():
    return adc.read()

while True:
    print(get_adc_value())
    time.sleep_ms(500)
